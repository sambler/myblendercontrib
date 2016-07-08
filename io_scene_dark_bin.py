bl_info = {
    "name": "Dark Engine Static Model",
    "author": "nemyax",
    "version": (0, 3, 20160511),
    "blender": (2, 7, 4),
    "location": "File > Import-Export",
    "description": "Import and export Dark Engine static model .bin",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}

import bpy
import bmesh
import mathutils as mu
import math
import re
import struct
import os
import glob
from struct import pack, unpack
from bpy.props import (
    StringProperty,
    BoolProperty)
from bpy_extras.io_utils import (
    ExportHelper,
    ImportHelper,
    path_reference_mode)

###
### Import
###

class FaceImported:
    binVerts   = []
    binUVs     = []
    binMat     = None
    bmeshVerts = []

def aka(key, l):
    result = None
    for i in range(len(l)):
        if key == l[i][0]:
            result = (i,l[i])
            break
    return result

def get_uints(bs):
    spec = '<' + str(len(bs) // 4) + 'I'
    return list(unpack(spec, bs))

def get_ushorts(bs):
    spec = '<' + str(len(bs) // 2) + 'H'
    return list(unpack(spec, bs))

def get_floats(bs):
    spec = '<' + str(len(bs) // 4) + 'f'
    return list(unpack(spec, bs))

def get_string(bs):
    s = ""
    for b in bs:
        s += chr(b)
    result = ""
    for c in filter(lambda x: x!='\x00', s):
        result += c
    return result

class SubobjectImported(object):
    def __init__(self, bs, faceRefs, faces, materials, vhots):
        self.name   = get_string(bs[:8])
        self.motion, self.parm, self.min, self.max = unpack('<Biff', bs[8:21])
        self.child, self.next  = unpack('<hh', bs[69:73])
        self.xform = get_floats(bs[21:69])
        curVhotsStart, numCurVhots = get_ushorts(bs[73:77])
        self.vhots = vhots[curVhotsStart:curVhotsStart+numCurVhots]
        facesHere = [faces[addr] for addr in faceRefs]
        matsUsed = {}
        for f in facesHere:
            m = f.binMat
            if m != None:
                matsUsed[m] = materials[m]
        self.faces = facesHere
        self.matsUsed = matsUsed
    def matSlotIndexFor(self, matIndex):
        if matIndex != None:
            return list(self.matsUsed.values()).index(self.matsUsed[matIndex])
    def localMatrix(self):
        if all(map(lambda x: x == 0.0, self.xform)):
            return mu.Matrix.Identity(4)
        else:
            matrix = mu.Matrix()
            matrix[0][0], matrix[1][0], matrix[2][0] = self.xform[:3]
            matrix[0][1], matrix[1][1], matrix[2][1] = self.xform[3:6]
            matrix[0][2], matrix[1][2], matrix[2][2] = self.xform[6:9]
            matrix[0][3] = self.xform[9]
            matrix[1][3] = self.xform[10]
            matrix[2][3] = self.xform[11]
            return matrix

def prep_materials(matBytes, numMats, file_path):
    materials = {}
    stage1 = []
    stage2 = []
    for _ in range(numMats):
        matName = get_string(matBytes[:16])
        matSlot = matBytes[17]
        stage1.append((matSlot,matName))
        matBytes = matBytes[26:]
    if matBytes: # if there's aux data
        auxChunkSize = len(matBytes) // numMats
        for _ in range(numMats):
            clear, bright = get_floats(matBytes[:8])
            stage2.append((clear,bright))
            matBytes = matBytes[auxChunkSize:]
    else:
        for _ in range(numMats):
            stage2.append((0.0,0.0))
    for i in range(numMats):
        s, n = stage1[i]
        c, b = stage2[i]
        materials[s] = (n,c,b)
    return materials

def prep_vhots(vhotBytes):
    result = []
    while len(vhotBytes):
        result.append((
            unpack('<I', vhotBytes[:4])[0],
            list(get_floats(vhotBytes[4:16]))))
        vhotBytes = vhotBytes[16:]
    return result

def prep_verts(vertBytes):
    floats = list(get_floats(vertBytes))
    verts = []
    i = -1
    while floats:
        i += 1
        x = floats.pop(0)
        y = floats.pop(0)
        z = floats.pop(0)
        verts.append((i,(x,y,z)))
    return verts

def prep_uvs(uvBytes):
    floats = list(get_floats(uvBytes))
    uvs = []
    i = -1
    while floats:
        i += 1
        u = floats.pop(0)
        v = floats.pop(0)
        uvs.append(mu.Vector((u,v)))
    return uvs

def prep_faces0(faceBytes, version):
    garbage = 9 + version # magic 12 or 13: v4 has an extra byte at the end
    faces = {}
    faceAddr = 0
    faceIndex = 0
    while len(faceBytes):
        matIndex = unpack('<H', faceBytes[2:4])[0]
        type = faceBytes[4]
        numVerts = faceBytes[5]
        verts = get_ushorts(faceBytes[12:12+numVerts*2])
        if type == 89:
            faceEnd = garbage + numVerts * 4
            uvs = []
        else:
            faceEnd = garbage + numVerts * 6
            uvs = get_ushorts(faceBytes[12+numVerts*4:12+numVerts*6])
        face = FaceImported()
        face.binVerts = verts
        face.binUVs = uvs
        face.binMat = matIndex
        faces[faceAddr] = face
        faceAddr += faceEnd
        faceIndex += 1
        faceBytes = faceBytes[faceEnd:]
    return faces

def prep_faces(faceBytes, version):
    garbage = 9 + version # magic 12 or 13: v4 has an extra byte at the end
    faces = {}
    faceAddr = 0
    faceIndex = 0
    while len(faceBytes):
        matIndex = unpack('<H', faceBytes[2:4])[0]
        type = faceBytes[4] & 3
        numVerts = faceBytes[5]
        verts = get_ushorts(faceBytes[12:12+numVerts*2])
        uvs = []
        if type == 3:
            faceEnd = garbage + numVerts * 6
            uvs.extend(get_ushorts(faceBytes[12+numVerts*4:12+numVerts*6]))
        else:
            faceEnd = garbage + numVerts * 4
            matIndex = None
        face = FaceImported()
        face.binVerts = verts
        face.binUVs = uvs
        face.binMat = matIndex
        faces[faceAddr] = face
        faceAddr += faceEnd
        faceIndex += 1
        faceBytes = faceBytes[faceEnd:]
    return faces

def node_subobject(bs):
    return ([],bs[3:])

def node_vcall(bs):
    return ([],bs[19:])

def node_call(bs):
    facesStart = 23
    numFaces1 = unpack('<H', bs[17:19])[0]
    numFaces2 = unpack('<H', bs[21:facesStart])[0]
    facesEnd = facesStart + (numFaces1 + numFaces2) * 2
    faces = get_ushorts(bs[facesStart:facesEnd])
    return (faces,bs[facesEnd:])

def node_split(bs):
    facesStart = 31
    numFaces1 = unpack('<H', bs[17:19])[0]
    numFaces2 = unpack('<H', bs[29:facesStart])[0]
    facesEnd = facesStart + (numFaces1 + numFaces2) * 2
    faces = get_ushorts(bs[facesStart:facesEnd])
    return (faces,bs[facesEnd:])

def node_raw(bs):
    facesStart = 19
    numFaces = unpack('<H', bs[17:facesStart])[0]
    facesEnd = facesStart + numFaces * 2
    faces = get_ushorts(bs[facesStart:facesEnd])
    return (faces,bs[facesEnd:])

def prep_face_refs(nodeBytes):
    faceRefs = []
    while len(nodeBytes):
        nodeType = nodeBytes[0]
        if nodeType == 4:
            faceRefs.append([])
            process = node_subobject
        elif nodeType == 3:
            process = node_vcall
        elif nodeType == 2:
            process = node_call
        elif nodeType == 1:
            process = node_split
        elif nodeType == 0:
            process = node_raw
        else:
            return
        faces, newNodeBytes = process(nodeBytes)
        nodeBytes = newNodeBytes
        faceRefs[-1].extend(faces)
    return faceRefs

def prep_subobjects(subBytes, faceRefs, faces, materials, vhots):
    subs = []
    index = 0
    while len(subBytes):
        sub = SubobjectImported(
            subBytes[:93],
            faceRefs[index],
            faces,
            materials,
            vhots)
        subs.append(sub)
        index += 1
        subBytes = subBytes[93:]
    return subs

def parse_bin(binBytes, file_path):
    version = unpack('<I', binBytes[4:8])[0]
    bbox = get_floats(binBytes[24:48])
    numMats = binBytes[66]
    subobjOffset,\
    matOffset,\
    uvOffset,\
    vhotOffset,\
    vertOffset,\
    lightOffset,\
    normOffset,\
    faceOffset,\
    nodeOffset = get_uints(binBytes[70:106])
    materials  = prep_materials(binBytes[matOffset:uvOffset], numMats, file_path)
    uvs        = prep_uvs(binBytes[uvOffset:vhotOffset])
    vhots      = prep_vhots(binBytes[vhotOffset:vertOffset])
    verts      = prep_verts(binBytes[vertOffset:lightOffset])
    faces      = prep_faces(binBytes[faceOffset:nodeOffset], version)
    faceRefs   = prep_face_refs(binBytes[nodeOffset:])
    subobjects = prep_subobjects(
        binBytes[subobjOffset:matOffset],
        faceRefs,
        faces,
        materials,
        vhots)
    return (bbox,subobjects,verts,uvs,materials)

def build_bmesh(bm, sub, verts):
    faces = sub.faces
    for v in verts:
        bm.verts.new(v[1])
        bm.verts.index_update()
    for f in faces:
        bmVerts = []
        for oldIndex in f.binVerts:
            newIndex = aka(oldIndex, verts)[0]
            bm.verts.ensure_lookup_table()
            bmVerts.append(bm.verts[newIndex])
        bmVerts.reverse() # flip normal
        try:
            bm.faces.new(bmVerts)
            f.bmeshVerts = bmVerts
        except ValueError:
            extraVerts = []
            for oldIndex in reversed(f.binVerts):
                sameCoords = aka(oldIndex, verts)[1][1]
                ev = bm.verts.new(sameCoords)
                bm.verts.index_update()
                extraVerts.append(ev)
            bm.faces.new(extraVerts)
            f.bmeshVerts = extraVerts
        bm.faces.index_update()
    bm.faces.ensure_lookup_table()
    for i in range(len(faces)):
        bmFace = bm.faces[i]
        binFace = faces[i]
        mi = sub.matSlotIndexFor(binFace.binMat)
        if mi != None:
            bmFace.material_index = sub.matSlotIndexFor(binFace.binMat)
    bm.edges.index_update()
    return

def assign_uvs(bm, faces, uvs):
    bm.loops.layers.uv.new()
    uvData = bm.loops.layers.uv.active
    for x in range(len(bm.faces)):
        bmFace = bm.faces[x]
        binFace = faces[x]
        loops = bmFace.loops
        binUVs = binFace.binUVs
        binUVs.reverse() # to match the face's vert direction
        for i in range(len(binUVs)):
            loop = loops[i]
            u, v = uvs[binUVs[i]]
            loop[uvData].uv = (u,1-v)
    return

def make_mesh(subobject, verts, uvs):
    faces = subobject.faces
    vertsSubset = []
    for f in faces:
        vertsSubset.extend([aka(v, verts)[1] for v in f.binVerts])
    vertsSubset = list(set(vertsSubset))
    bm = bmesh.new()
    build_bmesh(bm, subobject, vertsSubset)
    assign_uvs(bm, faces, uvs)
    mesh = bpy.data.meshes.new(subobject.name)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def parent_index(index, subobjects):
    for i in range(len(subobjects)):
        if subobjects[i].next == index:
            return parent_index(i, subobjects)
        elif subobjects[i].child == index:
            return i
    return -1

def make_bbox(coords):
    bm = bmesh.new()
    v1 = bm.verts.new(coords[:3])
    v2 = bm.verts.new(coords[3:])
    e = bm.edges.new((v1, v2))
    mesh = bpy.data.meshes.new("bbox")
    bm.to_mesh(mesh)
    bm.free()
    bbox = bpy.data.objects.new(name="bbox", object_data=mesh)
    bbox.draw_type = 'BOUNDS'
    bpy.context.scene.objects.link(bbox)
    return bbox

def load_img(file_path, img_name):
    dir_path = os.path.dirname(file_path)
    ps       = os.sep
    files    = []
    for n in (glob.glob(dir_path + ps + "*")):
        nl = os.path.split(n)[-1].lower()
        if ((nl == "txt") or (nl == "txt16")) and os.path.isdir(n):
            files.extend(glob.glob(n + ps + "*.???"))
    if not files:
        return
    img_file = None
    for f in files:
        fbase = os.path.splitext(os.path.split(f)[-1])[0]
        if img_name.lower() == fbase.lower():
            img_file = f
            break
    if not img_file:
        return
    for t in bpy.data.textures:
        if t.type == 'IMAGE' and t.image.filepath == img_file:
            return t
    img = None
    for i in bpy.data.images:
        if i.filepath == img_file:
            img = i
            break
    if not img:
        img = bpy.data.images.load(img_file)
    img.mapping = 'UV'
    tex = bpy.data.textures.new(name=img_file, type='IMAGE')
    tex.image = img
    return tex

def apply_tex(mat, tex):
    for ts in mat.texture_slots:
        if ts and ts.texture == tex:
            return
    mat.active_texture = tex

def make_objects(object_data, file_path):
    bbox, subobjects, verts, uvs, mats = object_data
    objs = []
    for s in subobjects:
        mesh = make_mesh(s, verts, uvs)
        obj = bpy.data.objects.new(name=mesh.name, object_data=mesh)
        obj.matrix_local = s.localMatrix()
        bpy.context.scene.objects.link(obj)
        if s.motion == 1:
            limits = obj.constraints.new(type='LIMIT_ROTATION')
            limits.owner_space = 'LOCAL'
            limits.min_x = s.min
            limits.max_x = s.max
        elif s.motion == 2:
            limits = obj.constraints.new(type='LIMIT_LOCATION')
            limits.owner_space = 'LOCAL'
            limits.min_x = s.min
            limits.max_x = s.max
        for v in s.vhots:
            vhot_name = s.name + "-vhot-" + str(v[0])
            vhot = bpy.data.objects.new(vhot_name, None)
            bpy.context.scene.objects.link(vhot)
            vhot.parent = obj
            vhot.location = v[1]
        bpy.context.scene.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT') # initialises UVmap correctly
        mesh.uv_textures.new()
        for m in s.matsUsed.values():
            bpy.ops.object.material_slot_add()
            mat = None
            mat_name = m[0]
            for a in bpy.data.materials:
                if a.name == mat_name:
                    mat = a
                    break
            if not mat:
                mat = bpy.data.materials.new(mat_name)
            mat.translucency = m[1]
            mat.emit = m[2]
            tex = load_img(file_path, mat_name)
            if tex:
                apply_tex(mat, tex)
            obj.material_slots[-1].material = mat
        objs.append(obj)
    for i in range(len(subobjects)):
        mum = parent_index(i, subobjects)
        if mum >= 0:
            objs[i].parent = objs[mum]
    make_bbox(bbox)
    return {'FINISHED'}

def do_import(file_path):
    binData = open(file_path, 'r+b')
    binBytes = binData.read(-1)
    typeID = binBytes[:4]
    if typeID == b'LGMD':
        object_data = parse_bin(binBytes, file_path)
        msg = "File \"" + file_path + "\" loaded successfully."
        result = make_objects(object_data, file_path)
    elif typeID == b'LGMM':
        msg = "The Dark Engine AI mesh format is not supported."
        result = {'CANCELLED'}
    else:
        msg = "Cannot understand the file format."
        result = {'CANCELLED'}
    return (msg,result)

###
### Export
###

# Classes

class Kinematics(object):
    def __init__(self, parm, matrix, mot_type,
        min, max, rel):
        self.parm     = parm
        self.matrix   = matrix
        self.mot_type = mot_type
        self.min      = min
        self.max      = max
        self.child    = rel['child']
        self.sibling  = rel['next']
        self.call     = rel['call']
        self.splits   = rel['splits']

class Model(object):
    def __init__(self,
        kinem, meshes, names, materials, vhots, bbox,
        clear, bright):
        num_vs = num_uvs = num_lts = num_fs = num_ns = 0
        for bm in meshes:
            bm.edges.ensure_lookup_table()
            ext_e = bm.edges.layers.string.active
            num_vs0, num_uvs0, num_lts0, num_ns0, num_fs0 = \
                unpack('<5H', bm.edges[0][ext_e])
            num_vs  += num_vs0
            num_uvs += num_uvs0
            num_lts += num_lts0
            num_ns  += num_ns0
            num_fs  += num_fs0
        self.meshes        = meshes
        self.kinem         = kinem
        self.names         = encode_names(names, 8)
        self.materials     = materials
        self.numVhots      = deep_count(vhots)
        self.vhots         = vhots
        self.numFaces      = num_fs
        self.numVerts      = num_vs
        self.numNormals    = num_ns
        self.numUVs        = num_uvs
        self.numLights     = num_lts
        self.numMeshes     = len(meshes)
        self.bbox          = bbox
        self.maxPolyRadius = max([max_poly_radius(m) for m in meshes])
        matFlags = 0
        if clear:
            matFlags += 1
        if bright:
            matFlags += 2
        self.matFlags = matFlags
    def encodeVerts(self):
        result = b''
        for bm in self.meshes:
            ext_v = bm.verts.layers.string.active
            result += concat_bytes([o[2:] for o
                in sorted(set([v[ext_v] for v in bm.verts]))])
        return result
    def encodeUVs(self):
        result = b''
        for bm in self.meshes:
            ext_l = bm.loops.layers.string.active
            uv_set = set()
            for f in bm.faces:
                for l in f.loops:
                    uv_set.add(l[ext_l][:10])
            result += concat_bytes([o[2:] for o in sorted(uv_set)])
        return result 
    def encodeLights(self):
        result = b''
        for bm in self.meshes:
            ext_l = bm.loops.layers.string.active
            lt_set = set()
            for f in bm.faces:
                for l in f.loops:
                    lt_set.add(l[ext_l][10:])
            result += concat_bytes([o[2:] for o in sorted(lt_set)])
        return result 
    def encodeVhots(self):
        chunks = []
        for mi in range(len(self.vhots)):
            currentVhots = self.vhots[mi]
            offset = deep_count(self.vhots[:mi])
            for ai in range(len(currentVhots)):
                id, coords = currentVhots[ai]
                chunks.append(concat_bytes([
                    pack('<I', id),
                    encode_floats(coords[:])]))
        return concat_bytes(chunks)
    def encodeNormals(self):
        result = b''
        for bm in self.meshes:
            ext_f = bm.faces.layers.string.active
            result += concat_bytes([o[2:] for o
                in sorted(set([f[ext_f][:14] for f in bm.faces]))])
        return result
    def encodeFaces(self):
        result = []
        for bm in self.meshes:
            ext_f = bm.faces.layers.string.active
            result.append([f[ext_f][14:] for f in bm.faces])
        return result
    def encodeMaterials(self):
        names = []
        if self.materials:
            for m in self.materials:
                names.append(m.name)
        else:
            names.append("oh_bugger")
        finalNames = encode_names(names, 16)
        return concat_bytes(
            [encode_material(finalNames[i], i) for i in range(len(names))])
    def encodeMatAuxData(self):
        if self.materials:
            result = b''
            for m in self.materials:
                result += encode_floats([
                    m.translucency,
                    min([1.0,m.emit])])
            return result
        else:
            return bytes(8)

# Utilities

def strip_wires(bm):
    [bm.verts.remove(v) for v in bm.verts if v.is_wire or not v.link_faces]
    [bm.edges.remove(e) for e in bm.edges if not e.link_faces[:]]
    [bm.faces.remove(f) for f in bm.faces if len(f.edges) < 3]
    for seq in [bm.verts, bm.faces, bm.edges]: seq.index_update()
    for seq in [bm.verts, bm.faces, bm.edges]: seq.ensure_lookup_table()
    return bm

def concat_bytes(bs_list):
    return b"".join(bs_list)

def deep_count(deepList):
    return sum([len(i) for i in deepList])

def encode(fmt, what):
    return concat_bytes([pack(fmt, i) for i in what])

def encode_floats(floats):
    return encode('<f', floats)

def encode_uints(uints):
    return encode('<I', uints)

def encode_ints(ints):
    return encode('<i', ints)

def encode_shorts(shorts):
    return encode('<h', shorts)

def encode_ushorts(ushorts):
    return encode('<H', ushorts)

def encode_ubytes(ubytes):
    return encode('B', ubytes)

def encode_misc(items):
    return concat_bytes([pack(fmt, i) for (fmt, i) in items])

def find_common_bbox(ms, bms):
    xs = set()
    ys = set()
    zs = set()
    for pair in zip(ms, bms):
        matrix, bm = pair
        coords = [matrix * v.co for v in bm.verts]
        [xs.add(c[0]) for c in coords]
        [ys.add(c[1]) for c in coords]
        [zs.add(c[2]) for c in coords]
    return {min:(min(xs),min(ys),min(zs)),max:(max(xs),max(ys),max(zs))}

def find_d(n, vs):
    nx, ny, nz = n
    count = len(vs)
    vx = sum([v[0] for v in vs]) / count
    vy = sum([v[1] for v in vs]) / count
    vz = sum([v[2] for v in vs]) / count
    return -(nx*vx+ny*vy+nz*vz)

def max_poly_radius(bm):
    diam = 0.0
    for f in bm.faces:
        dists = set()
        vs = f.verts
        for v in vs:
            for x in vs:
                dists.add((v.co-x.co).magnitude)
        diam = max([diam,max(list(dists))])
    return diam * 0.5
        
def calc_center(pts):
    n = len(pts)
    x = sum([pt[0] for pt in pts]) / n
    y = sum([pt[1] for pt in pts]) / n
    z = sum([pt[2] for pt in pts]) / n
    return mu.Vector((x,y,z))

# Other functions

def encode_nodes(ext_face_lists, model):
    addr        = 0
    node_sizes  = []
    addr_chunks = []
    num_subs    = len(ext_face_lists)
    for bfli in range(num_subs):
        bfl = ext_face_lists[bfli]
        node_sizes.append(precalc_node_size(model.kinem[bfli], bfl))
        ext_face_addrs = b''
        for bf in bfl:
            ext_face_addrs += pack('<H', addr)
            addr += len(bf)
        addr_chunks.append(ext_face_addrs)
    result = b''
    for bfli in range(num_subs):
        result += encode_sub_node(bfli)
        k         = model.kinem[bfli]
        sphere_bs = encode_sphere(get_local_bbox_data(model.meshes[bfli]))
        call      = k.call
        splits    = k.splits
        nbf       = len(ext_face_lists[bfli])
        if call >= 0:
            result += encode_call_node(
                nbf,
                sum(node_sizes[:call]),
                sphere_bs,
                addr_chunks[bfli])
        elif splits:
            ns = len(splits)
            split_offs1, split_offs2 = \
                calc_split_offsets(splits, nbf, node_sizes, bfli)
            ac_list  = [addr_chunks[bfli]] + [b''] * (ns - 1)
            f_counts = [nbf] + [0] * (ns - 1)
            for n_back, n_front, nf, addr_chunk in zip(
                split_offs1, split_offs2, f_counts, ac_list):
                result += encode_split_node(
                    nf, sphere_bs, n_back, n_front, addr_chunk)
        else:
            result += encode_raw_node(nbf, sphere_bs, addr_chunks[bfli])
    node_offs = [sum(node_sizes[:i+1]) for i in range(len(node_sizes))]
    node_offs.insert(0, 0)
    return node_offs, result

def calc_split_offsets(splits, nf, node_sizes, idx):
    offs = [sum(node_sizes[:a]) for a in splits]
    res1 = []
    res2 = []
    pos = offs[idx] + 34 + nf * 2
    while offs:
        o = offs.pop()
        if len(offs) == 1:
            res1.append(o)
            res2.append(offs.pop())
        else:
            res1.append(pos)
            pos += 31
            res2.append(o)
    return res1, res2

def precalc_node_size(k, fl):
    size_fs = len(fl) * 2
    if k.call >= 0:
        return 26 + size_fs
    splits = k.splits
    if splits:
        return 3 + size_fs + 31 * (len(splits) - 1)
    return 22 + size_fs

def encode_sub_node(index):
    return pack('<BH', 4, index)

def encode_call_node(nf, off, sphere_bs, addr_chunk):
    return pack('<B16s3H', 2, sphere_bs, nf, off, 0) + addr_chunk

def encode_raw_node(nf, sphere_bs, addr_chunk):
    return pack('<B16sH', 0, sphere_bs, nf) + addr_chunk

def encode_split_node(nf, sphere_bs, n_back, n_front, addr_chunk):
    return pack('<B16sHHf3H',
        1, sphere_bs, nf, 0, 0, n_back, n_front, 0) + addr_chunk

def pack_light(xyz):
    result = 0
    shift = 22
    for f in xyz:
        val = round(f * 256)
        sign = int(val < 0) * 1024
        result |= (sign + val) << shift
        shift -= 10
    return pack('<I', result)

def encode_subobject(model, index, node_off):
    name = model.names[index]
    vhot_off   = deep_count(model.vhots[:index])
    num_vhots   = len(model.vhots[index])
    bm = model.meshes[index]
    bm.edges.ensure_lookup_table()
    ext_e = bm.edges.layers.string.active
    num_vs, num_lts, num_ns = \
        unpack('<HxxHHxx', bm.edges[0][ext_e])
    v_off, lt_off, n_off = \
        unpack('<3H', bm.edges[1][ext_e])
    kinem   = model.kinem[index]
    xform   = kinem.matrix
    splits  = kinem.splits
    if splits:
        num_nodes = len(splits) - 1
    else:
        num_nodes = 1
    return concat_bytes([
        name,
        pack('b', kinem.mot_type),
        pack('<i', kinem.parm),
        encode_floats([
            kinem.min,
            kinem.max,
            xform[0][0],
            xform[1][0],
            xform[2][0],
            xform[0][1],
            xform[1][1],
            xform[2][1],
            xform[0][2],
            xform[1][2],
            xform[2][2],
            xform[0][3],
            xform[1][3],
            xform[2][3]]),
        encode_shorts([kinem.child, kinem.sibling]),
        encode_ushorts([
            vhot_off,
            num_vhots,
            v_off,
            num_vs,
            lt_off,
            num_lts,
            n_off,
            num_ns,
            node_off,
            num_nodes])])

def encode_header(model, offsets):
    radius = (
        mu.Vector(model.bbox[max]) -\
        mu.Vector(model.bbox[min])).magnitude * 0.5
    return concat_bytes([
        b'LGMD\x04\x00\x00\x00',
        model.names[0],
        pack('<f', radius),
        pack('<f', model.maxPolyRadius),
        encode_floats(model.bbox[max]),
        encode_floats(model.bbox[min]),
        bytes(12), # relative centre
        encode_ushorts([
            model.numFaces,
            model.numVerts,
            max(0, model.numMeshes - 1)]), # parms
        encode_ubytes([
            max(1, len(model.materials)), # can't be 0
            0, # vcalls
            model.numVhots,
            model.numMeshes]),
        encode_uints([
            offsets['subs'],
            offsets['mats'],
            offsets['uvs'],
            offsets['vhots'],
            offsets['verts'],
            offsets['lights'],
            offsets['normals'],
            offsets['faces'],
            offsets['nodes'],
            offsets['end'],
            model.matFlags, # material flags
            offsets['matsAux'],
            8, # bytes per aux material data chunk
            offsets['end'], # ??? mesh_off
            0]), # ??? submesh_list_off
        b'\x00\x00']) # ??? number of meshes

def encode_sphere(bbox): # (min,max), both tuples
    xyz1 = mu.Vector(bbox[0])
    xyz2 = mu.Vector(bbox[1])
    halfDiag = (xyz2 - xyz1) * 0.5
    cx, cy, cz = xyz1 + halfDiag
    radius = halfDiag.magnitude
    return encode_floats([cx,cy,cz,radius])

def encode_names(names, length):
    newNames = []
    for n in names:
        trail = 0
        newName = ascii(n)[1:-1][:length]
        while newName in newNames:
            trail += 1
            trailStr = str(trail)
            newName = newName[:(length - len(trailStr))] + trailStr
        newNames.append(newName)
    binNames = []
    for nn in newNames:
        binName = bytes([ord(c) for c in nn])
        while len(binName) < length:
            binName += b'\x00'
        binNames.append(binName)
    return binNames

def encode_material(binName, index):
    return concat_bytes([
        binName,
        b'\x00', # material type = texture
        pack('B', index),
        bytes(4), # ??? "texture handle or argb"
        bytes(4)]) # ??? "uv/ipal"

def build_bin(model):
    binFaceLists = model.encodeFaces()
    matsChunk    = model.encodeMaterials()
    matsAuxChunk = model.encodeMatAuxData()
    uvChunk      = model.encodeUVs()
    vhotChunk    = model.encodeVhots()
    vertChunk    = model.encodeVerts()
    lightChunk   = model.encodeLights()
    normalChunk  = model.encodeNormals()
    nodeOffsets, nodeChunk = encode_nodes(binFaceLists, model)
    faceChunk    = concat_bytes(
        [concat_bytes(l) for l in binFaceLists])
    subsChunk    = concat_bytes(
        [encode_subobject(model, i, nodeOffsets[i])
            for i in range(model.numMeshes)])
    offsets = {}
    def offs(cs):
        return [sum([len(c) for c in cs[:i+1]]) for i in range(len(cs))]
    offsets['subs'],\
    offsets['mats'],\
    offsets['matsAux'],\
    offsets['uvs'],\
    offsets['vhots'],\
    offsets['verts'],\
    offsets['lights'],\
    offsets['normals'],\
    offsets['faces'],\
    offsets['nodes'],\
    offsets['end'] = offs([
        bytes(132),
        subsChunk,
        matsChunk,
        matsAuxChunk,
        uvChunk,
        vhotChunk,
        vertChunk,
        lightChunk,
        normalChunk,
        faceChunk,
        nodeChunk])
    header = encode_header(model, offsets)
    return concat_bytes([
        header,
        subsChunk,
        matsChunk,
        matsAuxChunk,
        uvChunk,
        vhotChunk,
        vertChunk,
        lightChunk,
        normalChunk,
        faceChunk,
        nodeChunk])

def get_local_bbox_data(mesh):
    xs = [v.co[0] for v in mesh.verts]
    ys = [v.co[1] for v in mesh.verts]
    zs = [v.co[2] for v in mesh.verts]
    return (
        (min(xs),min(ys),min(zs)),
        (max(xs),max(ys),max(zs)))

def get_mesh(obj, materials): # and tweak materials
    mat_slot_lookup = {}
    for i in range(len(obj.material_slots)):
        maybe_mat = obj.material_slots[i].material
        if maybe_mat and (maybe_mat in materials):
            mat_slot_lookup[i] = materials.index(maybe_mat)
    bm = bmesh.new()
    bm.from_object(obj, bpy.context.scene)
    strip_wires(bm) # goodbye, box tweak hack
    uvs = bm.loops.layers.uv.verify()
    for f in bm.faces:
        orig_mat = f.material_index
        if orig_mat in mat_slot_lookup.keys():
            f.material_index = mat_slot_lookup[orig_mat]
            for c in f.loops:
                c[uvs].uv[1] = 1.0 - c[uvs].uv[1]
    return bm

def append_bmesh(bm1, bm2, matrix):
    bm2.transform(matrix)
    uvs = bm1.loops.layers.uv.verify()
    uvs_orig = bm2.loops.layers.uv.verify()
    vs_so_far = len(bm1.verts)
    for v in bm2.verts:
        bm1.verts.new(v.co)
        bm1.verts.index_update()
    for f in bm2.faces:
        try:
            bm1.verts.ensure_lookup_table()
            bm1.faces.ensure_lookup_table()
            nf = bm1.faces.new(
                [bm1.verts[vs_so_far+v.index] for v in f.verts])
        except ValueError:
            continue
        for i in range(len(f.loops)):
            nf.loops[i][uvs].uv = f.loops[i][uvs_orig].uv
            nf.material_index = f.material_index
        bm1.faces.index_update()
    bm2.free()
    bm1.normal_update()
    return bm1

def combine_meshes(bms, matrices):
    result = bmesh.new()
    for bmi in range(len(bms)):
        bm = bms[bmi]
        matrix = matrices[bmi]
        result = append_bmesh(result, bm, matrix)
    return result
    
def build_rels(root, branches):
    nb = len(branches)
    hier = [[] for _ in range(nb + 1)]
    for i in range(nb):
        m = branches[i]
        final_idx = i + 1
        if m.parent in branches:
            hier[branches.index(m.parent)+1].append(final_idx)
        else:
            hier[0].append(final_idx)
    [l.append(-1) for l in hier]
    ns = len(hier)
    rels = [{'child':-1,'next':-1,'call':-1,'splits':[]}
        for _ in range(ns)]
    for i, r, ks in zip(range(ns), rels, hier):
        n = len(ks)
        for x in hier:
            if i in x:
                r['next'] = x[(x.index(i)+1)]
                break
        if n == 2:
            r['call']   = ks[0]
            r['child']  = ks[0]
        elif n > 2:
            r['splits'] = ks[:-1]
            r['child']  = ks[0]
    return rels

def get_motion(obj):
    if not obj:
        mot_type = 0
        min = max = 0.0
    else:
        types = ('LIMIT_ROTATION','LIMIT_LOCATION')
        limits = [c for c in obj.constraints if
            c.type in types]
        if limits:
            c = limits.pop()
            mot_type = types.index(c.type) + 1
            min = c.min_x
            max = c.max_x
        else:
            mot_type = 1
            min = max = 0.0
    return (mot_type,min,max)

def init_kinematics(objs, rels, matrices):
    kinem = []
    for i in range(len(objs)):
        motion_type, min, max = get_motion(objs[i])
        kinem.append(Kinematics(
            i - 1,
            matrices[i],
            motion_type,
            min,
            max,
            rels[i]))
    return kinem

def categorize_objs(objs):
    custom_bboxes = [o for o in objs if o.name.lower().startswith("bbox")]
    bbox = None
    if custom_bboxes:
        bo = custom_bboxes[0]
        bm = bo.matrix_world
        bmin = bm * mu.Vector(bo.bound_box[0])
        bmax = bm * mu.Vector(bo.bound_box[6])
        bbox = {min:tuple(bmin),max:tuple(bmax)}
    for b in custom_bboxes:
        objs.remove(b)
    root = [o for o in objs if o.data.polygons and not (o.parent in objs)]
    gen2 = [o for o in objs if o.data.polygons and o.parent in root]
    gen3_plus = [o for o in objs if
        o.data.polygons and
        o.parent in objs and
        not (o.parent in root)]
    return (bbox,root,gen2,gen3_plus)

def shift_box(box_data, matrix):
    return {
        min:tuple(matrix * mu.Vector(box_data[min])),
        max:tuple(matrix * mu.Vector(box_data[max]))}

def tag_vhots(dl):
    ids = {}
    idx = 0
    for l in dl:
        for vhn, _ in l:
            id_s = "".join(re.findall("\d", vhn))
            if id_s:
                id = int(id_s) % (2**32-1)
                ids[vhn] = idx if id in ids.values() else id
            else:
                ids[vhn] = idx
            while idx in ids.values():
                idx += 1
    for l in dl:
        for i in range(len(l)):
            name, pos = l[i]
            l[i] = (ids[name], pos)
    return dl

def prep_meshes(all_objs, materials, world_origin, bsp):
    bbox, root, gen2, gen3_plus = categorize_objs(all_objs)
    gen2_meshes = [get_mesh(o, materials) for o in gen2]
    gen3_plus_meshes = [get_mesh(o, materials) for o in gen3_plus]
    branches = gen2 + gen3_plus
    branch_meshes = gen2_meshes + gen3_plus_meshes
    root_mesh = combine_meshes(
        [get_mesh(o, materials) for o in root],
        [o.matrix_world for o in root])
    real_bbox = find_common_bbox(
        [mu.Matrix.Identity(4)] + [o.matrix_world for o in branches],
        [root_mesh] + branch_meshes)
    if not bbox:
        bbox = real_bbox
    if world_origin:
        origin_shift = mu.Matrix.Identity(4)
    else:
        origin_shift = mu.Matrix.Translation(
            (mu.Vector(real_bbox[max]) + mu.Vector(real_bbox[min])) * -0.5)
    names = [root[0].name]
    names.extend([o.name for o in gen2])
    names.extend([o.name for o in gen3_plus])
    matrices = [mu.Matrix([[0]*4] * 4)]
    root_mesh.transform(origin_shift)
    for i in range(len(gen2)):
        o = gen2[i]
        matrices.append(origin_shift * o.matrix_world)
    for j in range(len(gen3_plus)):
        o = gen3_plus[j]
        matrices.append(o.matrix_local)
    vhots = [[]]
    for o in root:
        for vhot in [e for e in o.children if e.type == 'EMPTY']:
            mtx = origin_shift * vhot.matrix_world.translation
            vhots[-1].append((vhot.name,mtx))
    for o in branches:
        vhots.append([])
        for vhot in [e for e in o.children if e.type == 'EMPTY']:
            vhots[-1].append((vhot.name,vhot.matrix_local.translation))
    vhots = tag_vhots(vhots)
    if bsp:
        gen2_meshes = [do_bsp(m) for m in gen2_meshes]
        gen3_plus_meshes = [do_bsp(m) for m in gen3_plus_meshes]
        root_mesh = do_bsp(root_mesh)
    rels = build_rels(root, branches)
    kinem = init_kinematics([None] + branches, rels, matrices)
    meshes = [root_mesh]+branch_meshes
    return (names,meshes,vhots,kinem,shift_box(bbox, origin_shift))

# Each bmesh is extended with custom bytestring data used by the exporter.
# Edges #0 and #1 carry custom mesh-level attributes.
#     Custom vertex data layout:
# v[ext_v][0:2]   : bin vert index as '>H' (BE for sorting)
# v[ext_v][2:14]  : vert coords as '<3f'
#     Custom loop data layout:
# l[ext_l][0:2]   : bin UV index as '>H' (BE for sorting)
# l[ext_l][2:10]  : UV coords as '<ff'
# l[ext_l][10:12] : bin light index as '>H' (BE for sorting)
# l[ext_l][12:14] : bin light mat index as '<H'
# l[ext_l][14:16] : bin light vert index as '<H'
# l[ext_l][16:20] : bin light normal as '<I'
#     Custom face data layout:
# f[ext_f][0:2]  : normal index as '>H' (BE for sorting)
# f[ext_f][2:14] : normal as '<3f'
# f[ext_f][14:]  : ready-made mds_pgon struct
#     Custom edge data layout:
#   Edge #0:
# e0[ext_e][0:2]   : number of bin verts as '<H'
# e0[ext_e][2:4]   : number of bin UVs as '<H'
# e0[ext_e][4:6]   : number of bin lights as '<H'
# e0[ext_e][6:8]   : number of normals as '<H'
# e0[ext_e][8:10]  : number of faces as '<H'
#   Edge #1:
# e1[ext_e][0:2]   : vert offset as '<H'
# e1[ext_e][2:4]   : light offset as '<H'
# e1[ext_e][4:6]   : normal offset as '<H'

def extend_verts(off, bm):
    ext_v = bm.verts.layers.string.verify()
    ext_e = bm.edges.layers.string.verify()
    v_set = set()
    for v in bm.verts:
        xyz = v.co
        xyz_bs = pack('<3f', xyz.x, xyz.y, xyz.z)
        v_set.add(xyz_bs)
        v[ext_v] = xyz_bs
    num_vs = len(v_set)
    v_dict = dict(zip(v_set, range(num_vs)))
    for v in bm.verts:
        xyz_bs = v[ext_v]
        v_idx = pack('>H', off + v_dict[xyz_bs])
        v[ext_v] = v_idx + xyz_bs
    bm.edges.ensure_lookup_table()
    bm.edges[0][ext_e] = pack('<H', num_vs)
    bm.edges[1][ext_e] = pack('<H', off)
    return num_vs + off, bm

def extend_loops(uv_off, lt_off, bm):
    ext_l = bm.loops.layers.string.verify()
    ext_v = bm.verts.layers.string.active
    ext_e = bm.edges.layers.string.verify()
    uv = bm.loops.layers.uv.active
    lt_set = set()
    uv_set = set()
    for f in bm.faces:
        mat = pack('<H', f.material_index)
        for l in f.loops:
            v = l.vert[ext_v][-13:-15:-1] # BE to LE
            n = pack_light(l.vert.normal)
            lt = mat + v + n
            lt_set.add(lt)
            l[ext_l] = lt
            uv_set.add(l[uv].uv[:])
    num_lts = len(lt_set)
    num_uvs = len(uv_set)
    lt_dict = dict(zip(lt_set, range(num_lts)))
    uv_dict = dict(zip(uv_set, range(num_uvs)))
    for f in bm.faces:
        for l in f.loops:
            lt = l[ext_l]
            lt_idx = pack('>H', lt_off + lt_dict[lt])
            uv_co = l[uv].uv[:]
            uv_co_bs = pack('<ff', uv_co[0], uv_co[1])
            uv_idx = pack('>H', uv_off + uv_dict[uv_co])
            l[ext_l] = uv_idx + uv_co_bs + lt_idx + lt
    bm.edges.ensure_lookup_table()
    bm.edges[0][ext_e] += pack('<HH', num_uvs, num_lts)
    bm.edges[1][ext_e] += pack('<H', lt_off)
    return num_uvs + uv_off, num_lts + lt_off, bm

def extend_faces(n_off, f_off, bm):
    ext_f = bm.faces.layers.string.verify()
    ext_v = bm.verts.layers.string.active
    ext_l = bm.loops.layers.string.active
    ext_e = bm.edges.layers.string.active
    n_set = set()
    for f in bm.faces:
        n = f.normal
        n_bs = pack('<3f', n.x, n.y, n.z)
        n_set.add(n_bs)
        f[ext_f] = n_bs
    num_ns = len(n_set)
    n_dict = dict(zip(n_set, range(num_ns)))
    for f in bm.faces:
        f_idx = f_off + f.index
        tx = f.material_index
        num_vs = len(f.verts)
        n_bs = f[ext_f]
        n_idx = n_off + n_dict[n_bs]
        d = find_d(f.normal, [v.co[:] for v in f.verts])
        corners = list(reversed(f.loops)) # flip normal
        vs  = concat_bytes([l.vert[ext_v][-13:-15:-1] for l in corners])
        lts = concat_bytes([l[ext_l][-9:-11:-1] for l in corners])
        uvs = concat_bytes([l[ext_l][-19:-21:-1] for l in corners])
        f[ext_f] = pack('>H', n_idx) + n_bs + \
            pack('<HHBBHf', f_idx, tx, 27, num_vs, n_idx, d) + \
            vs + lts + uvs + pack('B', tx)
    num_fs = len(bm.faces)
    bm.edges.ensure_lookup_table()
    bm.edges[0][ext_e] += pack('<HH', num_ns, num_fs)
    bm.edges[1][ext_e] += pack('<H', n_off)
    return n_off + num_ns, f_off + num_fs, bm

def gather_materials(objs):
    ms = set()
    for o in objs:
        mat_indexes = set()
        for f in o.data.polygons:
            mat_indexes.add(f.material_index)
        slots = o.material_slots
        for mi in mat_indexes:
            try:
                ms.add(slots[mi].material)
            except:
                pass
    return list(ms)

def do_export(file_path, clear, bright, world_origin, bsp):
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and not o.hide]
    if not objs:
        return ("Nothing to export.",{'CANCELLED'})
    materials = gather_materials(objs)
    names, meshes, vhots, kinem, bbox = prep_meshes(
        objs,
        materials,
        world_origin,
        bsp)
    v_off = uv_off = lt_off = n_off = f_off = 0
    for i in range(len(meshes)):
        bm = meshes[i]
        v_off, bm = extend_verts(v_off, bm)
        uv_off, lt_off, bm = extend_loops(uv_off, lt_off, bm)
        n_off, f_off, bm = extend_faces(n_off, f_off, bm)
        meshes[i] = bm
    model = Model(
        kinem,
        meshes,
        names,
        materials,
        vhots,
        bbox,
        clear,
        bright)
    try:
        binBytes = build_bin(model)
        f = open(file_path, 'w+b')
        f.write(binBytes)
        msg = "File \"" + file_path + "\" written successfully."
        result = {'FINISHED'}
    except struct.error:
        msg = "The model has too many polygons. Export cancelled.\n"
        result = {'CANCELLED'}
    return (msg,result)

###
### Sorting: common
###

def reorder_faces(bm, order):
    bm0 = bm.copy()
    bm.clear()
    uvs = bm.loops.layers.uv.verify()
    uvs_orig = bm0.loops.layers.uv.verify()
    for v in bm0.verts:
        bm.verts.new(v.co)
        bm.verts.index_update()
    bm0.faces.ensure_lookup_table()
    bm0.verts.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    for fi in order:
        f = bm0.faces[fi]
        nf = bm.faces.new(
            [bm.verts[v.index] for v in f.verts])
        for i in range(len(f.loops)):
            nf.loops[i][uvs].uv = f.loops[i][uvs_orig].uv
            nf.material_index = f.material_index
        bm.faces.index_update()
    bm.normal_update()
    bm0.free()
    return bm

###
### Sorting: BSP
###

def walk(paths): # incremented indexes in keys, regular in values
    path = (0,) # 0 is used for root (index 0 doesn't occur)
    ps = []
    ns = []
    while paths:
        v = paths[path] + 1
        neg = path + (-v,) # negative for "is behind"
        pos = path + (v,)  # positive for "is in front"
        if neg in paths:
            path = neg
        elif pos in paths:
            path = pos
        else:
            if path[-1] >= 0:
                ps.append(paths.pop(path))
            else:
                ns.append(paths.pop(path))
            path = path[:-1]
    ps.reverse()
    ns.reverse()
    return ps + ns

def do_bsp(bm):
    all_fs = bm.faces[:]
    todo = [set(all_fs)]
    paths = dict(zip([f.index for f in all_fs], [(0,)] * len(all_fs)))
    while todo:
        fs = todo.pop(0)
        f, plane_n, plane_xyz = split_plane(fs, bm)
        idx = f.index + 1 # regular indexes in keys, incremented in values
        fs_inner, fs_outer = slash(bm, fs, plane_xyz, plane_n, f, idx, paths)
        if fs_inner:
            todo.append(fs_inner)
        if fs_outer:
            todo.append(fs_outer)
    paths_swapped = dict([(paths[i],i) for i in paths])
    ordered = walk(paths_swapped)
    return reorder_faces(bm, ordered)

def slash(bm, fs, plane_xyz, plane_n, ref_f, idx, paths):
    g = set()
    par = paths[ref_f.index]
    fs.remove(ref_f)
    g |= fs
    for f in fs:
        for e in f.edges:
            g.add(e)
        for v in f.verts:
            g.add(v)
    fs_orig = set(bm.faces)
    bmesh.ops.bisect_plane(
        bm, geom=list(g), dist=0.05, plane_co=plane_xyz, plane_no=plane_n)
    fs_new = set(bm.faces)
    fs_new -= fs_orig
    fs |= fs_new
    for f in fs:
        paths[f.index] = par
    fs_inner = set()
    fs_outer = set()
    for f in fs:
        fi = f.index
        a = plane_n.dot(f.calc_center_median() - plane_xyz)
        if a >= 0: # play with equation
            paths[fi] = paths[fi] + (idx,)
            fs_outer.add(f)
        else:
            paths[fi] = paths[fi] + (-idx,)
            fs_inner.add(f)
    return fs_inner, fs_outer

def split_plane(fs, bm):
    rated = list(fs)
    c = calc_center([f.calc_center_median() for f in fs])
    rated.sort(key=lambda a: rate(a, c))
    best_f = rated[0]
    new_plane_n = best_f.normal
    new_plane_d = find_d(new_plane_n, [v.co for v in best_f.verts])
    plane_xyz = new_plane_n * -new_plane_d
    return best_f, new_plane_n, plane_xyz

def rate(f, c):
    # return -find_d(f.normal, [(v.co - c) for v in f.verts])
    return (-find_d(f.normal, [(v.co - c) for v in f.verts]),-f.calc_area())

###
### UI
###

class ImportDarkBin(bpy.types.Operator, ImportHelper):
    '''Load a Dark Engine Static Model File'''
    bl_idname = "import_scene.dark_bin"
    bl_label = 'Import BIN'
    bl_options = {'PRESET'}
    filename_ext = ".bin"
    filter_glob = StringProperty(
        default="*.bin",
        options={'HIDDEN'},
        )
    path_mode = path_reference_mode
    check_extension = True
    path_mode = path_reference_mode
    def execute(self, context):
        msg, result = do_import(self.filepath)
        print(msg)
        return result

class ExportDarkBin(bpy.types.Operator, ExportHelper):
    '''Save a Dark Engine Static Model File'''
    bl_idname = "export_scene.dark_bin"
    bl_label = 'Export BIN'
    bl_options = {'PRESET'}
    filename_ext = ".bin"
    filter_glob = StringProperty(
        default="*.bin",
        options={'HIDDEN'})
    clear = BoolProperty(
        name="Use Translucency",
        default=True,
        description="Use the Translucency values set on materials")
    bright = BoolProperty(
        name="Use Emission",
        default=True,
        description="Use the Emit values set on materials")
    world_origin = BoolProperty(
        name="Model origin is at world origin",
        default=True,
        description="Otherwise, it is in the center of the geometry")
    bsp = BoolProperty(
        name="Use BSP sorting for polygons",
        default=False,
        description="May increase the polygon count unpredictably; use only if you need transparency support")
    path_mode = path_reference_mode
    check_extension = True
    path_mode = path_reference_mode
    def execute(self, context):
        msg, result = do_export(
            self.filepath,
            self.clear,
            self.bright,
            self.world_origin,
            self.bsp)
        if result == {'CANCELLED'}:
            self.report({'ERROR'}, msg)
        print(msg)
        return result

def menu_func_import_bin(self, context):
    self.layout.operator(
        ImportDarkBin.bl_idname, text="Dark Engine Static Model (.bin)")

def menu_func_export_bin(self, context):
    self.layout.operator(
        ExportDarkBin.bl_idname, text="Dark Engine Static Model (.bin)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import_bin)
    bpy.types.INFO_MT_file_export.append(menu_func_export_bin)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_bin)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_bin)
