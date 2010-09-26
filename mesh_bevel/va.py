# -*- coding: utf-8 -*-

# GPL LICENSE

import math
#import time

import bpy
import mathutils as Math
from mathutils import Euler, Matrix, Vector, Quaternion
import bgl


def the_other(ls, item):
    return ls[ls.index(item) - 1]


# pytohon cookbook
def list_or_tuple(x):
    return isinstance(x, (list, tuple))


def flatten(sequence, to_expand=list_or_tuple):
    for item in sequence:
        if to_expand(item):
            for subitem in flatten(item, to_expand):
                yield subitem
        else:
            yield item


class NullClass():
    def __init__(self):
        pass


### blender-2.5x, python-3.1 ##################################################
### Math Func #################################################################
def saacos(fac):
    if fac <= -1.0:
        return math.pi
    elif fac >= 1.0:
        return 0.0
    else:
        return math.acos(fac)


def saasin(fac):
    if fac <= -1.0:
        return -math.pi / 2.0
    elif fac >= 1.0:
        return math.pi / 2.0
    else:
        return math.asin(fac)


def cross2D(v1, v2):
    return v1.x * v2.y - v1.y * v2.x


def dot2D(v1, v2):
    return v1.x * v2.x + v1.y * v2.y


def triangle_normal(vec1, vec2, vec3):
    e1 = vec1 - vec2
    e2 = vec3 - vec2

    n = e2.cross(e1)
    vec = n.normalize()

    return vec


def axis_angle_to_quat(axis, angle, deg=False):
    if deg:
        # convert to radians
        ang = math.radians(angle)
    else:
        ang = angle
    q = Math.Quaternion([1.0, 0.0, 0.0, 0.0])
    if axis.length == 0.0:
        return None
    nor = axis.normalize()
    si = math.sin(ang / 2)
    q.w = math.cos(ang / 2)
    v = nor * si
    q.x = v.x
    q.y = v.y
    q.z = v.z

    return q


def rotation_between_vectors_to_quat(vec1, vec2):
    c = vec1.cross(vec2)
    axis = c if c.length > 0.0 else Math.Vector([1.0, 0.0, 0.0])
    #angle = NormalizedVecAngle2(vec1, vec2)
    angle = saacos(vec1.dot(vec2) / (vec1.length * vec2.length))
    quat = axis_angle_to_quat(axis, angle)

    return quat


def intersect(vec1, vec2, vec3, ray, orig, clip=1):
    v1 = vec1.copy()
    v2 = vec2.copy()
    v3 = vec3.copy()
    dir = ray.copy().normalize()
    orig = orig.copy()

    # find vectors for two edges sharing v1
    e1 = v2 - v1
    e2 = v3 - v1

    # begin calculating determinant - also used to calculated U parameter
    pvec = dir.cross(e2)

    # if determinant is near zero, ray lies in plane of triangle
    det = e1.dot(pvec)

    if (-1E-6 < det < 1E-6):
        return None

    inv_det = 1.0 / det

    # calculate distance from v1 to ray origin
    tvec = orig - v1

    # calculate U parameter and test bounds
    u = tvec.dot(pvec) * inv_det
    if (clip and (u < 0.0 or u > 1.0)):
        return None

    # prepare to test the V parameter
    qvec = tvec.cross(e1)

    # calculate V parameter and test bounds
    v = dir.dot(qvec) * inv_det

    if (clip and (v < 0.0 or u + v > 1.0)):
        return None

    # calculate t, ray intersects triangle
    t = e2.dot(qvec) * inv_det

    dir = dir * t
    pvec = orig + dir

    return pvec


def plane_intersect(loc, normalvec, seg1, seg2, returnstatus=0):
    zaxis = Vector([0.0, 0.0, 1.0])
    normal = normalvec.copy()
    normal.normalize()
    quat = rotation_between_vectors_to_quat(normal, zaxis)
    s1 = (seg1 - loc) * quat
    s2 = (seg2 - loc) * quat
    t = crossStatus = None
    if abs(s1[2] - s2[2]) < 1E-6:
        crossPoint = None
        if abs(s1[2]) < 1E-6:
            crossStatus = 3  # 面と重なる
        else:
            crossStatus = -1  # 面と平行
    elif s1[2] == 0.0:
        crossPoint = seg1
        t = 0
    elif s2[2] == 0.0:
        crossPoint = seg2
        t = 1
    else:
        t = -(s1[2] / (s2[2] - s1[2]))
        crossPoint = (seg2 - seg1) * t + seg1
    if t is not None:
        if 0 <= t <= 1:
            crossStatus = 2  # seg
        elif t > 0:
            crossStatus = 1  # ray
        else:
            crossStatus = 0  # line
    if returnstatus:
        return crossPoint, crossStatus
    else:
        return crossPoint


def vedistance(vecp, vec1, vec2, segment=1, returnVerticalPoint=False):
    dist = None
    if segment:
        if DotVecs(vec2 - vec1, vecp - vec1) < 0.0:
            dist = (vecp - vec1).length
        elif DotVecs(vec1 - vec2, vecp - vec2) < 0.0:
            dist = (vecp - vec2).length
    vec = vec2 - vec1
    p = vecp - vec1
    zaxis = Vector([0.0, 0.0, 1.0])
    quat = rotation_between_vectors_to_quat(vec, zaxis)
    p2 = quat * p
    if dist is None:
        dist = math.sqrt(p2[0] ** 2 + p2[1] ** 2)
    t = p2[2] / (vec2 - vec1).length
    verticalPoint = vec1 + vec * t

    if returnVerticalPoint:
        return dist, verticalPoint
    else:
        return dist


### View3D ####################################################################
def check_view(quat, localgrid_quat=None):
    # 0:Right, 1:Front, 2:Top, 3:Left, 4:Back, 5:Bottom
    vs = ['right', 'front', 'top', 'left', 'back', 'bottom', 'user']
    thr = 1E-5
    si = math.sin(math.radians(45))
    quats = [(0.5, -0.5, -0.5, -0.5), (si, -si, 0., 0.), (1., 0., 0., 0.),
             (0.5, -0.5, 0.5, 0.5), (0., 0., si, si), (0., 1., 0., 0.)]
    if localgrid_quat:
        for i in range(6):
            quats[i] = Math.Quaternion(quats[i]).cross(localgrid_quat)
    for cnt in range(6):
        if not [1 for i, j in zip(quat, quats[cnt]) if abs(i - j) > thr]:
            return vs[cnt]
        if not [1 for i, j in zip(quat, quats[cnt]) if abs(i + j) > thr]:
            return vs[cnt]
    else:
        return vs[-1]


def check_view_context(context):
    space3dview = context.space_data
    enable_localgrid = space3dview.localgrid
    if enable_localgrid:
        localgrid_quat = space3dview.localgrid_quat
    else:
        localgrid_quat = None

    rv3d = context.space_data.region_3d
    if hasattr(rv3d, 'view'):
        view_upper_case = rv3d.view
        if view_upper_case in ('PERSPORTHO', 'CAMERA'):
            view = 'user'
        else:
            view = view_upper_case.lower()
    else:
        viewmat = rv3d.view_matrix
        quat = viewmat.rotation_part().to_quat()
        view = check_view(quat, localgrid_quat)
    return view


def get_view_vector(persmat):
    # persmat = context.space_data.region_3d.perspective_matrix
    invpersmat = persmat.copy().invert()
    v0 = invpersmat * Math.Vector([0, 0, 0])
    v1 = invpersmat * Math.Vector([0, 0, -1])
    return (v1 - v0).normalize()


def world_to_window_coordinate(vec, pmat, sx, sy):
    # return float list
    '''
    v = (pmat * vec + Math.Vector([1., 1., 0.])) / 2
    window_pi = [v[0] * sx, v[1] * sy, v[2]]
    return window_pi
    '''
    v = vec.copy().resize4D()
    v = pmat * v
    if v[3] != 0.0:
        v /= v[3]
    x = sx / 2 + v[0] * sx / 2
    y = sy / 2 + v[1] * sy / 2
    return [x, y, v[2]]


def window_to_world_coordinate(px, py, pmat, sx, sy, pz=0.):
    #return vector
    invpmat = pmat.copy()
    invpmat.invert()
    v = Math.Vector([float(px) * 2 / sx, float(py) * 2 / sy, pz])
    vec = v - Math.Vector([1., 1., 0.])
    vec.resize4D()
    vec2 = invpmat * vec
    if vec2[3] != 0.0:
        vec2 /= vec2[3]
    vec2.resize3D()
    return vec2


def snap_to_grid(vec, grid_distance, localgrid_orig=None, localgrid_quat=None):
    if localgrid_quat and localgrid_orig:
        quat = localgrid_quat.copy().inverse()
        mat = quat.to_matrix().to_4x4()
        for i in range(3):
            mat[3][i] = localgrid_orig[i]
        imat = mat.copy().invert()
        vec = imat * vec
    for i in range(3):
        vec[i] = grid_distance * math.floor(0.5 + vec[i] / grid_distance)
    if localgrid_quat and localgrid_orig:
        vec = mat * vec
    return vec


### Utils #####################################################################

def vert_vert_dict(me, sel=0):
    # -1 <= sel <= 2
    if sel == -1:  # all vertices
        vert_verts = {v.index: [] for v in me.vertices}
    elif sel:
        vert_verts = {v.index: [] for v in me.vertices if \
                      v.select and not v.hide}
    else:
        vert_verts = {v.index: [] for v in me.vertices if not v.hide}
    if sel == -1:
        for ed in me.edges:
            v1 = ed.key[0]
            v2 = ed.key[1]
            vert_verts[v1].append(v2)
            vert_verts[v2].append(v1)
    else:
        for ed in me.edges:
            if not ed.hide:
                for cnt, v in enumerate(ed.key):
                    if sel == 0:
                        vert_verts[v].append(ed.key[cnt - 1])
                    elif sel == 1:
                        if v in vert_verts:
                            vert_verts[v].append(ed.key[cnt - 1])
                    else:  # sel == 2
                        if ed.select:
                            vert_verts[v].append(ed.key[cnt - 1])
    return vert_verts


def vert_edge_dict(me, sel=0, key=True):
    # -1 <= sel <= 2
    if sel == -1:
        vert_edges = {v.index: [] for v in me.vertices}
    elif sel:
        vert_edges = {v.index: [] for v in me.vertices if \
                      v.select and not v.hide}
    else:
        vert_edges = {v.index: [] for v in me.vertices if not v.hide}
    if sel == -1:
        for ed in me.edges:
            edkey = ed.key
            ei = ed.index
            vert_edges[edkey[0]].append(edkey if key else ei)
            vert_edges[edkey[1]].append(edkey if key else ei)
    else:
        for ed in me.edges:
            if not ed.hide:
                ei = ed.index
                for v in ed.key:
                    if sel == 0:
                        vert_edges[v].append(ed.key if key else ei)
                    elif sel == 1:
                        if v in vert_edges:
                            vert_edges[v].append(ed.key if key else ei)
                    else:  # sel == 2
                        if ed.select:
                            vert_edges[v].append(ed.key if key else ei)
    return vert_edges


def vert_face_dict(me, sel=0):
    # -1 <= sel <= 2
    if sel == -1:
        vert_faces = {v.index: [] for v in me.vertices}
    elif sel:
        vert_faces = {v.index: [] for v in me.vertices if \
                      v.select and not v.hide}
    else:
        vert_faces = {v.index: [] for v in me.vertices if not v.hide}

    if sel == -1:
        for f in me.faces:
            for v in f.vertices:
                vert_faces[v].append(f.index)
    else:
        for f in me.faces:
            if not f.hide:
                for v in f.vertices:
                    if sel == 0:
                        vert_faces[v].append(f.index)
                    elif sel == 1:
                        if v in vert_faces:
                            vert_faces[v].append(f.index)
                    else:  # sel == 2
                        if f.select:
                            vert_faces[v].append(f.index)

    return vert_faces


def edge_face_dict(me, sel=0, key=True):
    # sel==0:all, sel==1:edge.select, sel==2:face&edge.select
    if sel == -1:
        edge_faces = {ed.key: [] for ed in me.edges}
    elif sel:
        edge_faces = {ed.key: [] for ed in me.edges if \
                        ed.select and not ed.hide}
    else:
        edge_faces = {ed.key: [] for ed in me.edges if \
                        not ed.hide}
    if sel == -1:
        for f in me.faces:
            for edkey in f.edge_keys:
                edge_faces[edkey].append(f.index)
    else:
        for f in me.faces:
            if not f.hide:
                for edkey in f.edge_keys:
                    if sel == 0:
                        edge_faces[edkey].append(f.index)
                    elif sel == 1:
                        if edkey in edge_faces:
                            edge_faces[edkey].append(f.index)
                    else:
                        if f.select:
                            edge_faces[edkey].append(f.index)
    if key:
        return edge_faces
    else:
        kedict = key_edge_dict(me, sel=-1)
        edge_faces_i = {}
        for k, i in edge_faces.items():
            edge_faces_i[kedict[k]] = i
        return edge_faces_i


def key_edge_dict(me, sel=0):
    # sel==-1:all, sel==0:notHidden, sel==1or2:edge.select
    if sel == -1:
        key_edges = {ed.key: ed.index for ed in me.edges}
    elif sel == 0:
        key_edges = {ed.key: ed.index for ed in me.edges if not ed.hide}
    elif sel:
        key_edges = {ed.key: ed.index for ed in me.edges if \
                     ed.select and not ed.hide}
    return key_edges


def connected_verts(me, sel=1):
    '''
    from source, 'void selectconnected_mesh(void)'
    sel 0: not hide, 1: sel & not hide, else: all
    '''
    if sel == 0:
        edges = [ed for ed in me.edges if not ed.hide]
        flagdict = dict.fromkeys([v.index for v in me.vertices if not v.hide], 0)
    elif sel == 1:
        edges = [ed for ed in me.edges if ed.select and not ed.hide]
        flagdict = dict.fromkeys([v.index for v in me.vertices if \
                                  v.select and not v.hide], 0)
    else:
        edges = me.edges
        flagdict = dict.fromkeys([v.index for v in me.vertices], 0)

    masseslist = []
    while flagdict:
        flagdict[list(flagdict.keys())[0]] = 1
        if edges:
            done = 1
            toggle = 0
            while done == 1:
                done = 0
                toggle += 1

                if toggle & 1:
                    index = 0
                else:
                    index = len(edges) - 1
                ed = edges[index]
                while ed:
                    v1i, v2i = ed.vertices
                    if flagdict[v1i] == 1 and flagdict[v2i] == 0:
                        flagdict[v2i] = 1
                        done = 1
                    elif flagdict[v1i] == 0 and flagdict[v2i] == 1:
                        flagdict[v1i] = 1
                        done = 1
                    if toggle & 1:
                        index += 1
                    else:
                        index -= 1
                    if index >= len(edges) or index < 0:
                        break
                    ed = edges[index]
            indexes = [key for key, val in flagdict.items() if val == 1]
            masseslist.append(sorted(indexes))
            # 'edges' for next loop
            edges = [ed for ed in edges if \
                     flagdict[ed.vertices[0]] == 0 and flagdict[ed.vertices[1]] == 0]
        else:
            indexes = [key for key, val in flagdict.items() if val == 1]
            masseslist.append(sorted(indexes))

        for i in indexes:
            del flagdict[i]
    return masseslist


def split_faces_re(me, edkey, efdict, fdict):
    for findex in efdict[edkey]:
        if findex in fdict:
            continue
        fdict[findex] = None
        keys = me.faces[findex].edge_keys
        for key in keys:
            split_faces_re(me, key, efdict, fdict)


def split_faces(me, indexlist=None):
    if indexlist:
        efdict = edge_face_dict(me, sel=0)
        for key in efdict.keys():
            if len(efdict[key]) == 0:
                del efdict[key]
        indexdict = dict.fromkeys(indexlist)  # for performance
        for f in me.faces:
            if not f.hide and f.index not in indexdict:  # dell
                for key in f.edge_keys:
                    if f.index in efdict[key]:
                        edfict[key].remove[f.index]
    else:
        efdict = edge_face_dict(me, sel=2)
        for key in efdict.keys():
            if len(efdict[key]) == 0:
                del efdict[key]
        indexdict = dict([[f.index, None] for f in me.faces if \
                          f.select and not f.hide])

    returnlist = []
    while indexdict:
        fdict = {}
        split_faces_re(me, me.faces[list(indexdict.keys())[0]].edge_keys[0], \
                       efdict, fdict)
        returnlist.append(fdict.keys())
        for findex in fdict.keys():
            del indexdict[findex]

    return returnlist


def get_mirrored_mesh(scene, ob):
    # apply MirrorModifier only
    mods = ob.modifiers
    mods_realtime = [mod.show_viewport for mod in mods]
    for mod in mods:
        if mod.type != 'MIRROR':
            mod.show_viewport = False

    me = ob.data
    selbuf = [v.select for v in me.vertices]
    for i in range(len(me.vertices)):
        me.vertices[i].select = i % 2
    dm = ob.create_mesh(scene, 1, 'PREVIEW')  # applied modifiers

    medmdict = {}
    already = 0
    index = 0
    for i in range(len(dm.vertices)):
        if dm.vertices[i].select == me.vertices[index].select:
            if already == 0:
                medmdict[index] = i
                already = 1
            else:
                continue
        else:
            index += 1
            medmdict[index] = i
            already = 1

    dmmedict = dict.fromkeys(range(len(dm.vertices)), None)
    for key, val in medmdict.items():
        dmmedict[val] = key

    for i in range(len(me.vertices)):
        me.vertices[i].select = selbuf[i]
    dm = ob.create_mesh(scene, 1, 'PREVIEW')

    for i in range(len(mods)):
        mods[i].show_viewport = mods_realtime[i]

    return dm, medmdict, dmmedict


def keypath(edge_keys):
    vkdict = {}
    tip = -1
    tip_sub = edge_keys[0][0]
    tipnum = 0
    verts = []
    closed = 1

    for k in edge_keys:
        for v in k:
            if v not in vkdict:
                vkdict[v] = [k]
            else:
                vkdict[v].append(k)

    for v, keys in vkdict.items():
        if len(keys) == 1:
            closed = 0
            tipnum += 1
            for k in keys:
                if k.index(v) == 0:
                    tip = v
                else:
                    tip_sub = v
    if tipnum >= 3:
        return []

    if tip == -1:
        tip = tip_sub

    verts.append(tip)

    while True:
        v = verts[-1]
        keys = vkdict[v]
        for k in keys:
            v2 = the_other(k, v)
            if v2 not in verts:
                verts.append(v2)
                break
        if not closed:
            if len(verts) >= len(edge_keys) + 1:
                break
        else:
            if len(verts) >= len(edge_keys):
                break

    return verts


def fill(verts):
    faces = []
    if len(verts) <= 2:
        pass
    elif 3 <= len(verts) <= 4:
        faces.append(verts)
    else:
        i = 0
        j = len(verts) - 1
        end = 0
        while True:
            if j - i == 2:
                # Triangle
                f = verts[i:i + 3]
                end = 1
            elif j - i == 3:
                # Quad
                f = verts[i:i + 4]
                end = 1
            else:
                f = [verts[i], verts[i + 1], verts[j - 1], verts[j]]
            faces.append(f)
            if end:
                break
            i += 1
            j -= 1

    return faces


def same_all(ls):
    if len(ls) <= 1:
        return True
    val = ls[0]
    for i in ls[1:]:
        if i != val:
            return False
    return True


def exclude_continuance(ls):
    '''連続した同じ値を複数返さない'''
    if len(ls) == 0:
        raise StopIteration
    tmp = None if ls[0] != None else False
    for i in ls:
        if i == tmp:
            continue
        yield i
        tmp = i


def exclude_duplicate(ls):
    '''重複した値を複数返さない'''
    if len(ls) == 0:
        raise StopIteration
    s = set()
    tmp = None if ls[0] != None else False
    for i in ls:
        if i in s:
            continue
        yield i
        s.add(i)


### Snap ######################################################################
#def make_snap_matrix(region, obs=None, subdivide=100, snap_to_visible=0, \
#                          snap_to_dm=0, all_origins=0):
def make_snap_matrix(sx, sy, persmat, snap_to='selected', \
                     snap_to_origin='selected', apply_modifiers=True, \
                     objects=None, subdivide=100):
    '''
    snap_to: ('active', 'selected', 'visible') # snap to mesh & bone
    snap_to_origin: (None, 'none', 'active', 'selected', 'visible', 'objects')\
                                                         #snap to object origin
    apply_modifiers: (True, False)
    '''
    scn = bpy.context.scene
    actob = bpy.context.active_object
    if objects is None:
        if snap_to == 'active':
            obs = [actob]
        elif snap_to == 'selected':
            obs = [ob for ob in bpy.context.selected_objects]
            if actob.mode == 'EDIT' and actob not in obs:
                obs.append(actob)
        else:
            obs = [ob for ob in scn.objects if ob.is_visible(scn)]
    else:
        obs = objects
    # window座標(ドット)に変換したベクトルの二次元配列
    #vmat = [[[] for j in range(subdivide)] for i in range(subdivide)]
    colcnt = int(math.ceil(subdivide * sx / max(sx, sy)))
    rowcnt = int(math.ceil(subdivide * sy / max(sx, sy)))
    vmat = [[[] for c in range(colcnt)] for r in range(rowcnt)]

    for ob in obs:
        obmode = ob.mode
        if obmode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        if ob.type == 'MESH':
            if ob == actob:
                if obmode == 'EDIT' and apply_modifiers and ob.modifiers:
                    me = ob.create_mesh(bpy.context.scene, 1, 'PREVIEW')
                    meshes = [ob.data, me]
                elif obmode == 'EDIT':
                    meshes = [ob.data]
                else:
                    meshes = [ob.create_mesh(bpy.context.scene, 1, 'PREVIEW')]
            else:
                meshes = [ob.create_mesh(bpy.context.scene, 1, 'PREVIEW')]
            # ※meshes == local座標
            #me.transform(ob.matrix_world)
            for me in meshes:
                for v in me.vertices:
                    if obmode == 'EDIT' and v.hide:
                        continue
                    vec = Vector(world_to_window_coordinate( \
                                      ob.matrix_world * v.co, persmat, sx, sy))
                    if 0 <= vec[0] < sx and 0 <= vec[1] < sy:
                        #row = int(vec[1] / sy * subdivide)
                        #col = int(vec[0] / sx * subdivide)
                        row = int(vec[1] / max(sx, sy) * subdivide)
                        col = int(vec[0] / max(sx, sy) * subdivide)
                        #if 0 <= row < subdivide and 0 <= col < subdivide:
                        vmat[row][col].append(vec)

        elif ob.type == 'ARMATURE':
            if obmode == 'EDIT':
                bones = ob.data.bones
            else:
                bones = ob.pose.bones
            for bone in bones:
                if obmode == 'EDIT':
                    head = bone.head_local
                    tail = bone.tail_local
                else:
                    head = bone.head
                    tail = bone.tail
                for v in (head, tail):
                    vec = Vector(world_to_window_coordinate( \
                                         ob.matrix_world * v, persmat, sx, sy))
                    if 0 <= vec[0] < sx and 0 <= vec[1] < sy:
                        #row = int(vec[1] / sy * subdivide)
                        #col = int(vec[0] / sx * subdivide)
                        row = int(vec[1] / max(sx, sy) * subdivide)
                        col = int(vec[0] / max(sx, sy) * subdivide)
                        #if 0 <= row < subdivide and 0 <= col < subdivide:
                        vmat[row][col].append(vec)

        if obmode == 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

    # object origins
    if snap_to_origin in (None, 'none'):
        obs_snap_origin = []  # 無し
    elif snap_to_origin == 'active':
        obs_snap_origin = [actob]
    elif snap_to_origin == 'selected':
        obs_snap_origin = [ob for ob in bpy.context.selected_objects]
        if actob.mode == 'EDIT' and actob not in obs:
            obs.append(actob)
    elif snap_to_origin == 'visible':
        obs_snap_origin = [ob for ob in scn.objects if ob.is_visible(scn)]
    else:  # snap_to_origin == 'objects'
        obs_snap_origin = objects
    for ob in obs_snap_origin:
        origin = Vector(ob.matrix_world[3][:3])
        vec = Vector(world_to_window_coordinate(origin, persmat, sx, sy))
        if 0 <= vec[0] < sx and 0 <= vec[1] < sy:
            #row = int(vec[1] / sy * subdivide)
            #col = int(vec[0] / sx * subdivide)
            row = int(vec[1] / max(sx, sy) * subdivide)
            col = int(vec[0] / max(sx, sy) * subdivide)
            #if 0 <= row < subdivide and 0 <= col < subdivide:
            vmat[row][col].append(vec)

    return vmat


def get_matrix_element_square(mat, center, r):
    '''
    # centerの周り、r距離分の要素を左上から順に返す。
    mat = [[ 0, 1, 2, 3],
           [ 4, 5, 6, 7],
           [ 8, 9,10,11],
           [12,13,14,15]]
    print([i for i in get_matrix_fuga(mat, (1,2), 1)]) #center==6
    > [1, 2, 3, 7, 11, 10, 9, 5]
    print([i for i in get_matrix_fuga(mat, (0,2), 2)]) #center==2
    > [11, 10, 9, 8, 4, 0]
    '''
    i = [center[0] - r, center[1] - r]
    cnt = 0
    while True:
        if cnt != 0 and cnt >= 8 * r:
            raise StopIteration
        if 0 <= i[0] < len(mat) and 0 <= i[1] < len(mat[0]):
            yield mat[i[0]][i[1]]
        if cnt < 2 * r:
            i[1] += 1
        elif cnt < 4 * r:
            i[0] += 1
        elif cnt < 6 * r:
            i[1] -= 1
        elif cnt < 8 * r:
            i[0] -= 1
        cnt += 1


def get_vector_from_snap_maxrix(mouseco, max_size, subdivide, snap_vmat, \
                                snap_range):
    # max_size: max(sx, sy)
    snap_vec = snap_vec_len = None
    center = (int(mouseco[1] / max_size * subdivide), \
              int(mouseco[0] / max_size * subdivide))
    #find_before_loop = 0
    r = 0
    find = 0
    #while i <= math.ceil(snap_range / max_size * subdivide)
    #for r in range(int(math.ceil(snap_range / subdivide)) + 1):
    while True:
        for l in get_matrix_element_square(snap_vmat, center, r):
            if not l:
                continue
            for v in l:
                vec = Vector([v[0] - mouseco[0], v[1] - mouseco[1]])
                vec_len = vec.length
                if vec_len <= snap_range:
                    if snap_vec_len is None:
                        snap_vec_len = vec_len
                        snap_vec = v
                        #break
                        find = max(find, 1)
                    elif vec_len < snap_vec_len:
                        snap_vec_len = vec_len
                        snap_vec = v
                        find = max(find, 1)
            #if snap_vec:
            #    break
        if r > snap_range / max_size * subdivide:
            break
        if find == 1:
            find = 2
        elif find == 2:
            break
        r += 1
    return snap_vec

### source ####################################################################
SMALL_NUMBER = 1E-8


def shell_angle_to_dist(angle):
    return 1.0 if angle < SMALL_NUMBER else abs(1.0 / math.cos(angle))


def shell_angle_to_dist_sin(angle):
    return 1.0 if angle < SMALL_NUMBER else abs(1.0 / math.sin(angle))


def angle_normalized_v3v3(v1, v2):
    # this is the same as acos(dot_v3v3(v1, v2)), but more accurate
    if v1.dot(v2) < 0.0:
        vec = v2.copy().negate()
        return math.pi - 2.0 * saasin((vec - v1).length / 2.0)

    else:
        return 2.0 * saasin((v2 - v1).length / 2.0)


def angle_tri_v3(v1, v2, v3):
    angles = [0.0, 0.0, 0.0]
    ed1 = (v3 - v1).normalize()
    ed2 = (v1 - v2).normalize()
    ed3 = (v2 - v3).normalize()

    angles[0] = math.pi - angle_normalized_v3v3(ed1, ed2)
    angles[1] = math.pi - angle_normalized_v3v3(ed2, ed3)
    angles[2] = math.pi - (angles[0] + angles[1])
    return angles


def angle_quad_v3(v1, v2, v3, v4):
    ed1 = (v4 - v1).normalize()
    ed2 = (v1 - v2).normalize()
    ed3 = (v2 - v3).normalize()
    ed4 = (v3 - v4).normalize()

    angles = [math.pi - angle_normalized_v3v3(ed1, ed2),
              math.pi - angle_normalized_v3v3(ed2, ed3),
              math.pi - angle_normalized_v3v3(ed3, ed4),
              math.pi - angle_normalized_v3v3(ed4, ed1)]
    return angles


### bgl ###
def draw_circle(x, y, radius, subdivide):
    '''e = Euler([0, 0, math.radians(360 / subdivide)])
    m = e.to_matrix()
    v = Vector([0, radius, 0])
    bgl.glBegin(bgl.GL_LINE_LOOP)
    for i in range(subdivide):
        bgl.glVertex2f(x + v[0], y + v[1])
        v = m * v
    bgl.glEnd()
    '''
    bgl.glBegin(bgl.GL_LINE_LOOP)
    r = 0.0
    dr = math.pi * 2 / subdivide
    for i in range(subdivide):
        bgl.glVertex2f(x + radius * math.cos(r), y + radius * math.sin(r))
        r += dr
    bgl.glEnd()


def draw_box(xmin, ymin, w, h):
    bgl.glBegin(bgl.GL_LINE_LOOP)
    bgl.glVertex2f(xmin, ymin)
    bgl.glVertex2f(xmin + w, ymin)
    bgl.glVertex2f(xmin + w, ymin + h)
    bgl.glVertex2f(xmin, ymin + h)
    bgl.glEnd()


def draw_triangles(verts):
    bgl.glBegin(bgl.GL_TRIANGLES)
    for v in verts:
        bgl.glVertex2f(v[0], v[1])
    bgl.glEnd()


def triangle_relative_to_verts(top, base_relative, base_length):
    v1 = Vector(top)
    v = Vector([-base_relative[1] / 2, base_relative[0] / 2])
    v.normalize()
    v *= base_length / 2
    vb = Vector(base_relative)
    v2 = v1 + vb + v
    v3 = v1 + vb - v
    return v1, v2, v3


def draw_triangle_polygon_relative(top, base_relative, base_length):
    v1, v2, v3 = triangle_relative_to_verts(top, base_relative, base_length)
    bgl.glBegin(bgl.GL_TRIANGLES)
    bgl.glVertex2f(*v1)
    bgl.glVertex2f(*v2)
    bgl.glVertex2f(*v3)
    bgl.glEnd()


def draw_triangle_line_relative(top, base_relative, base_length):
    v1, v2, v3 = triangle_relative_to_verts(top, base_relative, base_length)
    bgl.glBegin(bgl.GL_LINE_LOOP)
    bgl.glVertex2f(*v1)
    bgl.glVertex2f(*v2)
    bgl.glVertex2f(*v3)
    bgl.glEnd()


def draw_quad_fan(x, y, inner_radius, outer_radius, start_angle, end_angle, \
                  subdivide):
    # 十二時から時計回りに描画
    v = Vector([0, 1, 0])
    e = Euler((0, 0, -start_angle))
    m = e.to_matrix()
    v = m * v
    a = (end_angle - start_angle) / (subdivide + 1)
    e = Euler((0, 0, -a))  # 時計回り
    m = e.to_matrix()

    bgl.glBegin(bgl.GL_QUAD_STRIP)
    for i in range(subdivide + 2):
        v1 = v * inner_radius
        v2 = v * outer_radius
        bgl.glVertex2f(x + v1[0], y + v1[1])
        bgl.glVertex2f(x + v2[0], y + v2[1])
        v = m * v
    bgl.glEnd()


def draw_arc(x, y, radius, start_angle, end_angle, subdivide):
    # 十二時から時計回りに描画
    v = Vector([0, 1, 0])
    e = Euler((0, 0, -start_angle))
    m = e.to_matrix()
    v = m * v
    if end_angle >= start_angle:
        a = (end_angle - start_angle) / (subdivide + 1)
    else:
        a = (end_angle + math.pi * 2 - start_angle) / (subdivide + 1)
    e = Euler((0, 0, -a))
    m = e.to_matrix()

    bgl.glBegin(bgl.GL_LINE_STRIP)
    for i in range(subdivide + 2):
        v1 = v * radius
        bgl.glVertex2f(x + v1[0], y + v1[1])
        v = m * v
    bgl.glEnd()


def normalize_angle(angle):
    while angle < 0.0:
        angle += math.pi * 2
    while angle > math.pi * 2:
        angle -= math.pi * 2
    return angle


def draw_quad_fan2(x, y, inner_radius, outer_radius,
                  start_angle, end_angle, edgenum):
    # 三時から反時計回りに描画 angle:radians
    startangle = normalize_angle(start_angle)
    endangle = normalize_angle(end_angle)
    if endangle < startangle:
        endangle += math.pi * 2
    diffangle = (endangle - startangle) / edgenum
    bgl.glBegin(bgl.GL_QUAD_STRIP)
    r = startangle
    for i in range(edgenum + 1):
        bgl.glVertex2f(x + inner_radius * math.cos(r),
                       y + inner_radius * math.sin(r))
        bgl.glVertex2f(x + outer_radius * math.cos(r),
                       y + outer_radius * math.sin(r))
        r += diffangle
    bgl.glEnd()


def draw_arc2(x, y, radius, start_angle, end_angle, edgenum):
    # 三時から反時計回りに描画 angle:radians
    startangle = normalize_angle(start_angle)
    endangle = normalize_angle(end_angle)
    if endangle < startangle:
        endangle += math.pi * 2
    diffangle = (endangle - start_angle) / edgenum

    bgl.glBegin(bgl.GL_LINE_STRIP)
    r = startangle
    for i in range(edgenum + 1):
        bgl.glVertex2f(x + radius * math.cos(r), y + radius * math.sin(r))
        r += diffangle
    bgl.glEnd()
