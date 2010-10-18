# coding: utf-8

import math
from functools import reduce

import bpy
from bpy.props import *
import mathutils as Math
from mathutils import Matrix, Vector, Quaternion
import geometry as Geo
from mesh_vertex_align_25.va import *
from mesh_vertex_align_25.va_ex import *

P = type('',(),{'__or__':(lambda s,o:print(o))})()

Normal = Vector([0.0, 0.0, 1.0])
Loc = Vector([0.0, 0.0, 0.0])
Axis = Vector([0.0, 0.0, 1.0])

SMALL_NUMBER = 1E-8

"""
scn = context.scene
cursor = scn.cursor_location

verts = me.vertices
vecs = [0 for i in range(len(verts) * 3)]
verts.foreach_get('co', vecs)

me.vertices.add(v)
me.edges.add(e)
me.faces.add(f)
me.vertices.foreach_set('co', verts_loc)
me.from_pydata(verts, edges, faces)
me.update()
scene.update()
scene.objects.active = ob
"""

class Config():
    def __init__(self):
        # unbend
        self.unbend_equaldist = False
        self.unbend_lock = [False, False, False]

        # edeg_slide
        self.edge_slide2_center_mode = True
        self.edge_slide2_consider_angle = False
        self.edge_slide2_auto = True
        self.edge_slide2_limit_max = True
        self.edge_slide2_limit_min = True

config = Config()

def cmp(a, b):
    return (a > b) -  (a < b)

def remove_double(veclist, dist):
    if len(veclist) == 0:
        return []
    newvecs = []
    while(len(veclist) >= 2):
        v0 = veclist[0]
        veclist = veclist[1:]
        copy = 1
        for v in veclist:
            d = (v0 - v).length
            if d < dist:
                copy = 0
                break
        if copy:
            newvecs.append(v0)
    newvecs.append(veclist[-1])
    return newvecs

def curved_edges_to_straight_edges(ob, fac=1.0, equaldist=0, lock=[False, False, False]):
    if ob.type != 'MESH':
        return
    nolock = [float(i is False) for i in lock]
    me = ob.data
    vvdict = vert_vert_dict(me, sel=2)
    masses = connected_verts(me, sel=1)
    masslist = []
    for mass in masses:
        if len(mass) >= 2:
            corners = []
            appendedcorners = []
            for i in mass:
                if len(vvdict[i]) != 2:
                    corners.append(i)
            for i in corners:
                if i in appendedcorners:
                    continue
                cnt = 0
                edges = []
                cindex = i
                while True:
                    if cnt == 0:
                        cindex = i
                        nindex = vvdict[cindex][0]
                        edges.append(cindex)
                        appendedcorners.append(cindex)
                        cnt += 1
                        continue
                    else:
                        bindex = cindex
                        cindex = nindex
                    if len(vvdict[cindex]) == 1:
                        edges.append(cindex)
                        masslist.append(edges)
                        appendedcorners.append(cindex)
                        break
                    elif len(vvdict[cindex]) == 2:
                        nindex = vvdict[cindex][vvdict[cindex].index(bindex) - 1]
                        edges.append(cindex)
                    elif len(vvdict[cindex]) >= 3:
                        edges.append(cindex)
                        masslist.append(edges)
                        appendedcorners.append(cindex)
                        break
                    cnt += 1
    for mass in masslist:
        if len(mass) <= 2:
            continue
        vec1 = me.vertices[mass[0]].co
        vec2 = me.vertices[mass[-1]].co
        verts = [me.vertices[i] for i in mass]
        normal = vec2 - vec1
        nnormal = normal.copy()
        nnormal.normalize()
        vec1_vertical_len = [0.0 for i in range(len(mass))]
        equaldist = len(verts) > 2 and equaldist
        for cnt, vert in enumerate(verts):
            vec = vert.co
            dist, vertical_point = vedistance(vec, vec1, vec2, 0, True)
            if equaldist:
                v = vec1 + nnormal * (normal.length / (len(verts) - 1)) * cnt
                v = (v - vec) * fac
                mvvec = Vector([v[i] * nolock[i] for i in range(3)])
                vert.co = vec + mvvec
            else:
                v = (vertical_point - vec) * fac
                mvvec = Vector([v[i] * nolock[i] for i in range(3)])
                vert.co = vec + mvvec

class MESH_OT_unbend_edges(bpy.types.Operator):
    global config
    bl_idname = 'mesh.unbend_edges'
    bl_label = 'Unbend Edges'
    bl_options = {'REGISTER', 'UNDO'}

    fac = FloatProperty(name='Fac',
        description = 'tool tip ?',
        default = 1.0,
        min = 0.0,
        max = 1.0,
        soft_min = 0.0,
        soft_max = 1.0,
        step = 1,
        precision = 3)

    equaldist = BoolProperty(name = 'Equal distance',
                             description = 'tip',
                             default=False)

    lock = BoolVectorProperty(name = 'Lock',
        description = 'Lock axis',
        default=[False, False, False],
        subtype='XYZ')

    force_invoke = BoolProperty(name = 'Call Invoke Force',
                                description = '',
                                default=False,
                                options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        if self.force_invoke:
            ## view3d.circle_menu
            self.invoke(context, None)
            self.force_invoke = False

        bpy.ops.object.mode_set(mode='OBJECT')
        ob = context.active_object
        fac = self.fac
        equaldist = self.equaldist
        lock = self.lock
        curved_edges_to_straight_edges(ob, fac, equaldist, lock)
        bpy.ops.object.mode_set(mode='EDIT')
        config.unbend_equaldist = equaldist
        config.unbend_lock = lock
        return {'FINISHED'}

    def invoke(self, context, event):
        self.equaldist = config.unbend_equaldist
        self.lock = config.unbend_lock
        context.area.tag_redraw()
        if not self.force_invoke:
            self.execute(context)
        return {'FINISHED'}

def align_edges_to_plane(ob, fac, mode, planenormal, planeloc):
    # mode = 'single', 'double', 'add'
    if ob.type != 'MESH':
        return
    obmat = ob.matrix_world
    obinvmat = obmat.copy().invert()
    obrotmat = obmat.to_3x3()
    obinvrotmat = obrotmat.copy().invert()
    me = ob.data

    vvdict = vert_vert_dict(me, sel=1)
    masses = connected_verts(me, sel=1)

    nums = [len(me.vertices), len(me.edges), len(me.faces)]
    geometry = [[], []] # verts, edges

    for mass in masses:
        if len(mass) == 1:
            vecindexes = vvdict[mass[0]]
            if len(vecindexes) == 0:
                continue
            elif len(vecindexes) == 1:
                v1 = me.vertices[mass[0]]
                v2 = me.vertices[vecindexes[0]]
            else:
                v1 = me.vertices[mass[0]]
                selvec = None
                selcnt = 0
                for i in vecindexes:
                    if me.vertices[i].select:
                        selvec = me.vertices[i]
                        selcnt += 1
                if selcnt == 1:
                    v2 = selvec
                else:
                    continue
        elif len(mass) == 2:
            v1 = me.vertices[mass[0]]
            v2 = me.vertices[mass[1]]
        else:
            continue

        if v1.select and (not v2.select):
            cpoint = plane_intersect(obinvmat * planeloc, obinvrotmat * planenormal, v1.co, v2.co)
            if cpoint is not None:
                if mode == 'add':
                    geometry[0].append(v1.co + (cpoint - v1.co) * fac)
                    nums[0] += 1
                    geometry[1].append([v1.index, nums[0] - 1])
                elif mode == 'single':
                    v1.co = v1.co + (cpoint - v1.co) * fac
                else:
                    v2.co = v2.co + (cpoint - v1.co) * fac
                    v1.co = v1.co + (cpoint - v1.co) * fac


        elif v1.select and v2.select:
            cpoint = plane_intersect(obinvmat * planeloc, obinvrotmat * planenormal, v1.co, v2.co)
            if cpoint is not None:
                if (cpoint - v1.co).length < (cpoint - v2.co).length:
                    near = v1
                    far = v2
                else:
                    near = v2
                    far = v1
                if mode == 'add':
                    geometry[0].append(near.co + (cpoint - near.co) * fac)
                    nums[0] += 1
                    geometry[1].append([near.index, nums[0] - 1])
                elif mode == 'single':
                    near.co = near.co + (cpoint - near.co) * fac
                else:
                    far.co = far.co + (cpoint - near.co) * fac
                    near.co = near.co + (cpoint - near.co) * fac

    vnum = len(me.vertices)
    enum = len(me.edges)
    me.vertices.add(len(geometry[0]))
    me.edges.add(len(geometry[1]))
    me.faces.add(0)
    # BUG!! me.vertices[vnum:]
    for cnt, v in enumerate(me.vertices):
        if cnt < vnum:
            continue
        v.co = geometry[0][cnt-vnum]
        v.select = 1

    for cnt, e in enumerate(me.edges[enum:]):
        e.vertices = geometry[1][cnt]
        e.select = 1
    me.update()

class MESH_OT_align_edges_to_plane(bpy.types.Operator):
    bl_idname = 'mesh.align_edges_to_plane'
    bl_label = 'Align Edges'
    bl_options = {'REGISTER', 'UNDO'}

    fac = FloatProperty(name='Fac',
        description = 'tool tip ?',
        default = 1.0,
        min = 0.0,
        max = 1.0,
        soft_min = 0.0,
        soft_max = 1.0,
        step = 1,
        precision = 3)

    mode = EnumProperty(items = (('single', 'Move one side', ''),
                                 ('double', 'Move edges', ''),
                                 ('add', 'Add edges', '')),
                                 name="Mode",
                                 description="mode",
                                 default='single',
                                 options={'ANIMATABLE'})
    normal = FloatVectorProperty(name='Normal',
                                 description = 'plane normal',
                                 default = (0.0, 0.0, 1.0),
                                 step = 10,
                                 precision = 3,
                                 subtype = 'XYZ')
    loc = FloatVectorProperty(name='Location',
                              description = 'plane location',
                              default = (0.0, 0.0, 0.0),
                              step = 10,
                              precision = 3,
                              subtype = 'XYZ')

    force_invoke = BoolProperty(name = 'Call Invoke Force',
                                description = '',
                                default=False,
                                options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        if self.force_invoke:
            ## view3d.circle_menu
            self.invoke(context, None)
            self.force_invoke = False
        bpy.ops.object.mode_set(mode='OBJECT')
        ob = context.active_object
        fac = self.fac
        mode = self.mode
        normal = self.normal
        loc = self.loc

        if fac != 0.0:
            align_edges_to_plane(ob, fac, mode, normal, loc)

        Normal[:] = self.normal[:]
        Loc[:] = self.loc[:]
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

    def invoke(self, context, event):
        self.normal[:] = Normal[:]
        self.loc[:] = Loc[:]
        context.area.tag_redraw()
        if not self.force_invoke:
            self.execute(context)
        return {'FINISHED'}

class MESH_MT_align_edges_to_plane(bpy.types.Menu):
    bl_idname = 'mesh.align_edges_to_plane_menu'
    bl_label = "Align Edges to Plane"

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.mode == 'EDIT'
        else:
            return False

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.operator('mesh.align_edges_to_plane', text='Move one side').mode = 'single'
        layout.operator('mesh.align_edges_to_plane', text='Move edges').mode = 'double'
        layout.operator('mesh.align_edges_to_plane', text= 'Add edges').mode = 'add'

'''
# old 2.4x
def select_distance(x, y, z, local, doubleside, select):
    ob = Scene.GetCurrent().objects.active
    obmat = ob.mat
    obrotmat = obmat.rotationPart()
    obinvmat = obmat.copy()
    obinvmat.invert()
    me = ob.getData(mesh=True)
    if not isinstance(me, Types.MeshType):
        return
    select = 1 if select else 0

    vals = [x, y, z]

    vcoarray = [v.co for v in me.vertices if v.sel and v.hide != 1]
    if len(vcoarray) == 0:
        return
    if not local:
        vcoarray = [v * obmat for v in vcoarray]
    minv = [0., 0., 0.]
    maxv = [0., 0., 0.]
    for v in vcoarray:
        for i in range(3):
            if v[i] < minv[i]:
                minv[i] = v[i]
            if v[i] > maxv[i]:
                maxv[i] = v[i]
    if not doubleside:
        minv = [min(minv[i], minv[i] + vals[i]) for i in range(3)]
        maxv = [max(maxv[i], maxv[i] + vals[i]) for i in range(3)]
    else:
        minv = [min(minv[i], minv[i] + vals[i], minv[i] - vals[i]) for i in range(3)]
        maxv = [max(maxv[i], maxv[i] + vals[i], maxv[i] - vals[i]) for i in range(3)]

    #if cmode & modes[0]:
    for v in [v for v in me.vertices if v.sel == 1-select and v.hide != 1]:
        if local:
            vco = v.co
        else:
            vco = v.co * obmat
        if vals[0] == 0.0 or minv[0] <= vco[0] <= maxv[0]:
            if vals[1] == 0.0 or minv[1] <= vco[1] <= maxv[1]:
                if vals[2] == 0.0 or minv[2] <= vco[2] <= maxv[2]:
                    if minv[0] == maxv[0] and minv[1] == maxv[1] and minv[2] == maxv[2]:
                        if vco[0] == minv[0] and vco[1] == minv[1] and vco[2] == minv[2]:
                            v.sel = select
                    else:
                        v.sel = select
    update_mesh_selected(me)
'''


##########################
### object.matrix2.4x ###
##########################

class MESH_OT_align_verts_to_plane(bpy.types.Operator):
    bl_idname = "mesh.align_verts_to_plane"
    bl_label = "Align to Plane"
    bl_options = {'REGISTER', 'UNDO'}

    mitems = (('x', 'X', 'Global X'),
              ('y', 'Y', 'Global Y'),
              ('z', 'Z', 'Global Z'),
              ('lx', 'Local X', 'Local X'),
              ('ly', 'Local Y', 'Local Y'),
              ('lz', 'Local Z', 'Local Z'),
              ('vx', 'View X', 'View X'),
              ('vy', 'View Y', 'View Y'),
              ('ax', 'Custom Axis', 'Custom Axis'),
              ('nor', 'Plane Normal', 'normal'))

    mode = EnumProperty(items = mitems,
                        name="Move Axis",
                        description="Move Axis",
                        default='x',
                        options={'ANIMATABLE'})

    fac = FloatProperty(
        name='Fac',
        description = 'Factor',
        default = 1.0,
        min = 0.0,
        max = 1.0,
        soft_min = 0.0,
        soft_max = 1.0,
        step = 1,
        precision = 3)

    transofs = FloatProperty(
        name='TransOfs',
        description = 'Trans axis offset',
        default = 0.0,
        min = -10.0,
        max = 10.0,
        soft_min = -10.0,
        soft_max = 10.0,
        step = 1,
        precision = 3)

    normalofs = FloatProperty(
        name='NormalOfs',
        description = 'Plane normal offset',
        default = 0.0,
        min = -10.0,
        max = 10.0,
        soft_min = -10.0,
        soft_max = 10.0,
        step = 1,
        precision = 3)

    normal = FloatVectorProperty(name='Normal',
                                 description = 'plane normal',
                                 default = (0.0, 0.0, 1.0),
                                 step = 10,
                                 precision = 3,
                                 subtype = 'XYZ')

    loc = FloatVectorProperty(name='Location',
                              description = 'plane location',
                              default = (0.0, 0.0, 0.0),
                              step = 10,
                              precision = 3,
                              subtype = 'XYZ')

    axis = FloatVectorProperty(name='Custom trans axis',
                           description = 'transform axis',
                           default = (0.0, 0.0, 1.0),
                           step = 10,
                           precision = 3,
                           subtype = 'XYZ')

    force_invoke = BoolProperty(name = 'Call Invoke Force',
                                description = '',
                                default=False,
                                options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        if self.force_invoke:
            ## view3d.circle_menu
            self.invoke(context, None)
            self.force_invoke = False
        bpy.ops.object.mode_set(mode='OBJECT')
        threthold = 1E-5
        mode = self.mode
        ob = context.active_object
        me = ob.data
        obmat = ob.matrix_world
        obinvmat = obmat.copy().invert()
        obrotmat = obmat.to_3x3()
        rv3d = context.space_data.region_3d
        pmat = rv3d.perspective_matrix
        pimat = pmat.copy().invert()
        vmat = rv3d.view_matrix
        vimat = vmat.to_3x3().invert()


        mode = self.mode
        fac = self.fac
        transofs = self.transofs
        normalofs = self.normalofs
        normal = self.normal
        loc = self.loc
        axis = self.axis


        if mode == 'x': # Global
            ray = Vector([1.0, 0.0, 0.0])
        elif mode == 'y':
            ray = Vector([0.0, 1.0, 0.0])
        elif mode == 'z':
            ray = Vector([0.0, 0.0, 1.0])
        elif mode == 'lx': # Local
            ray = obrotmat * Vector([1.0, 0.0, 0.0])
        elif mode == 'ly':
            ray = obrotmat * Vector([0.0, 1.0, 0.0])
        elif mode == 'lz':
            ray = obrotmat * Vector([0.0, 0.0, 1.0])
        elif mode == 'vx':
            ray = vimat * Vector([1.0, 0.0, 0.0])
        elif mode == 'vy':
            ray = vimat * Vector([0.0, 1.0, 0.0])
        elif mode == 'ax':
            ray = axis
        elif mode == 'nor':
            ray = normal

        loc_cp = loc.copy()
        if transofs:
            loc_cp += ray.normalize() * transofs
        if normalofs:
            loc_cp += normal.normalize() * normalofs

        if abs(normal.dot(ray)) > threthold:
            verts = [v for v in me.vertices if v.select and not v.hide]
            for vert in verts:
                vec = obmat * vert.co
                crosspoint = plane_intersect(loc_cp, normal, vec, vec + ray)
                crosspoint = obinvmat * crosspoint
                vert.co = vert.co + (crosspoint - vert.co) * fac

        Normal[:] = self.normal[:]
        Loc[:] = self.loc[:]
        Axis[:] = self.axis[:]
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

    def invoke(self, context, event):
        self.normal[:] = Normal[:]
        self.loc[:] = Loc[:]
        self.axis[:] = Axis[:]
        context.area.tag_redraw()
        if not self.force_invoke:
            self.execute(context)
        return {'FINISHED'}

def mark(context):
    # Global coordinate
    threshold = 1E-5

    ob = context.active_object
    if ob.type != 'MESH':
        return
    obmat = ob.matrix_world
    obrotmat = obmat.to_3x3()
    obinvmat = obmat.copy().invert()
    obinvrotmat = obrotmat.copy().invert()
    me = ob.data
    rv3d = context.space_data.region_3d
    persmat = rv3d.perspective_matrix

    planenormal = None
    planeloc = None

    markedvecs = [obmat * v.co for v in me.vertices if v.select and not v.hide]
    '''if len(markedvecs):
        markedvecs = remove_double(markedvecs, threshold)
    oneline = False
    if len(markedvecs) >= 3:
        oneline = True
        for vec in markedvecs[2:]:
            dist = vedistance(vec, markedvecs[0], markedvecs[1], segment=0)
            if dist > threshold:
                oneline = False
                break
    '''
    #if len(markedvecs) == 2 or oneline:
    if len(markedvecs) == 2:
        # different view vector
        winvec = get_view_vector(persmat)
        quat = rotation_between_vectors_to_quat(winvec, Vector([0.0, 0.0, 1.0]))
        v1 = markedvecs[0] * quat
        v2 = markedvecs[1] * quat
        if math.sqrt((v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2) < threshold: # XY
            planenormal = None
            planeloc = None
        else:
            v1 = markedvecs[0]
            v2 = markedvecs[1]
            v3 = markedvecs[0] + winvec
            planenormal = Geo.TriangleNormal(v1, v2, v3)
            planeloc = markedvecs[0]
    elif 3 <= len(markedvecs) <= 4:
        if len(markedvecs) == 3:
            planenormal = Geo.TriangleNormal(*markedvecs)
        else:
            pn1 = Geo.TriangleNormal(*(markedvecs[:3]))
            pn2 = Geo.TriangleNormal(*(markedvecs[1:]))
            if pn1.dot(pn2) < 0:
                pn2 = -pn2
            planenormal = (pn1 + pn2).normalize()
        planeloc = markedvecs[0]

    return planenormal, planeloc

class MESH_OT_mark_plane(bpy.types.Operator):
    bl_idname = 'mesh.mark_plane'
    bl_label = 'Mark Verts'
    bl_options = {'REGISTER', 'UNDO'}

    normal = FloatVectorProperty(name='Normal',
                                 description = 'plane normal',
                                 default = (0.0, 0.0, 1.0),
                                 step = 10,
                                 precision = 3,
                                 subtype = 'XYZ')
    loc = FloatVectorProperty(name='Location',\
                              description = 'plane location',
                              default = (0.0, 0.0, 0.0),
                              step = 10,
                              precision = 3,
                              subtype = 'XYZ')
    lock = BoolProperty(name = 'Lock',
                        description = 'lock',
                        default=True)

    force_invoke = BoolProperty(name = 'Call Invoke Force',
                                description = '',
                                default=False,
                                options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        if self.force_invoke:
            ## view3d.circle_menu
            self.invoke(context, None)
            self.force_invoke = False

        bpy.ops.object.mode_set(mode='OBJECT')
        lock = self.lock
        if lock:
            n, l = mark(context)
            if n:
                self.normal[:] = Normal[:] = n[:]
            if l:
                self.loc[:] = Loc[:] = l[:]
        else:
            Normal[:] = self.normal[:]
            Loc[:] = self.loc[:]
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

    def invoke(self, context, event):
        self.normal[:] = Normal[:]
        self.loc[:] = Loc[:]
        context.area.tag_redraw()
        if not self.force_invoke:
            self.execute(context)
        return {'FINISHED'}

class MESH_OT_mark_axis(bpy.types.Operator):
    bl_idname = 'mesh.mark_axis'
    bl_label = 'Mark Trans Axis'
    bl_options = {'REGISTER', 'UNDO'}

    axis = FloatVectorProperty(name='Custom trans axis',\
                               description = 'transform axis',
                               default = (0.0, 0.0, 1.0),
                               step = 10,
                               precision = 3,
                               subtype = 'XYZ')

    lock = BoolProperty(name = 'Lock',
                        description = 'tip',
                        default=True)

    force_invoke = BoolProperty(name = 'Call Invoke Force',
                                description = '',
                                default=False,
                                options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        if self.force_invoke:
            ## view3d.circle_menu
            self.invoke(context, None)
            self.force_invoke = False

        threthold = 1E-5
        bpy.ops.object.mode_set(mode='OBJECT')
        lock = self.lock
        if lock:
            ob = context.active_object
            me = ob.data
            obmat = ob.matrix_world
            markedvecs = [obmat * v.co for v in me.vertices \
                          if v.select and not v.hide]
            if len(markedvecs) == 2:
                vec = markedvecs[0] - markedvecs[1]
                if vec.length > threthold:
                    self.axis[:] = Axis[:] = vec
        else:
            Axis[:] = self.axis[:]
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

    def invoke(self, context, event):
        self.axis[:] = Axis[:]
        context.area.tag_redraw()
        if not self.force_invoke:
            self.execute(context)
        return {'FINISHED'}

def shift_outline(scene, ob, dist, type, normal, mod):
    mesh = ob.data
    if mod:
        dm, medmdict, dmmedict = get_mirrored_mesh(scene, ob)
        me = dm
    else:
        me = mesh

    faces = [f for f in me.faces if f.select and not f.hide]
    edges = [e for e in me.edges if e.select and not e.hide]
    verts = [v for v in me.vertices if v.select and not v.hide]

    if not edges:
        return

    ### for Edge ###
    if mod:
        me = dm
    else:
        me = mesh

    masses = connected_verts(me) ###
    vvdict = vert_vert_dict(me, sel=2)
    vfdict = vert_face_dict(me, sel=2)
    if normal is None:
        auto_plane = 1
    else:
        auto_plane = 0
    masscount = 0

    ret_vecs = {} # return dict

    for mass in masses:
        masscount += 1
        if len(mass) == 1:
            continue
        if len(mass) == 2 and normal is None:
            continue
        selfaces = False
        oneline = True
        edge_end = []
        for i in mass:
            if vfdict[i]:
                selfaces = True
                break
            if len(vvdict[i]) > 2:
                oneline = False
                break
            if len(vvdict[i]) == 1:
                edge_end.append(i)
        if selfaces or (not oneline):
            continue

        ### calc ###
        vecsindex = []
        for i in range(len(mass)):
            if i == 0:
                if edge_end:
                    v0 = edge_end[0]
                else:
                    v0 = mass[0]
                vn = vvdict[v0][0]
                vecsindex.append(v0)
            elif i == len(mass) - 1 and edge_end:
                vecsindex.append(edge_end[1])
            else:
                v0 = vn
                vn = the_other(vvdict[v0], vecsindex[-1])
                vecsindex.append(v0)
        if len(vecsindex) == 0:
            continue
        if auto_plane:
            if mod:
                # raw Mesh data
                verts = [mesh.vertices[dmmedict[i]] for i in vecsindex if dmmedict[i] is not None]
                vecs = [v.co for v in verts]
            else:
                verts = [me.vertices[i] for i in vecsindex]
                vecs = [v.co for v in verts]
            if len(vecs) == 0:
                continue
            #distvecs = (vecs - vecs[0])
            #dists = numpy.apply_along_axis(linalg.norm, 1, distvecs)
            #maxindex = numpy.argmax(dists)
            dists = [(v - vecs[0]).length for v in vecs]
            maxindex = dists.index(max(dists))
            vec1 = vecs[0]
            vec2 = vecs[maxindex]
            #dists = zeros(len(vecs))
            dists = []
            for cnt, vecp in enumerate(vecs):
                projvec = (vecp - vec1).project(vec2 - vec1)
                verticalvec = (vecp - vec1) - projvec
                dists.append(verticalvec.length)
            #maxindex = numpy.argmax(dists)
            maxindex = dists.index(max(dists))
            vec3 = vecs[maxindex]
            normal = triangle_normal(vec1, vec2, vec3)
        else:
            normal = normal.normalize()

        # derived mesh
        if mod:
            verts = [dm.vertices[i] for i in vecsindex]
        else:
            verts = [mesh.vertices[i] for i in vecsindex]
        vecs = [v.co for v in verts]
        vecs_orig = vecs
        if len(vecs) == 0:
            continue

        rotmat = ob.matrix_world.to_3x3()

        q = rotation_between_vectors_to_quat(normal, Math.Vector([0.0, 0.0, 1.0]))
        invq = q.copy().inverse()
        #normal_rotmat = quat_to_mat(q, 3) ###
        #normal_rotmat = q.to_matrix(other) ###
        vecs = [v * q for v in vecs]
        vecs2d = [Math.Vector([v.x, v.y]) for v in vecs]

        newvecs2d = []
        rotsum = 0.0
        for i in range(len(mass)):
            if i == 0 and edge_end:
                r = math.pi / 2
                mat = Math.Matrix([math.cos(r), math.sin(r)], \
                                  [-math.sin(r), math.cos(r)])
                vec = mat * (vecs2d[i] - vecs2d[i + 1])
                #newvecs2d.append(vec.normalize() * dist)
                newvecs2d.append(vec.normalize())
            elif i == len(mass) - 1 and edge_end:
                r = math.pi / 2
                mat = Math.Matrix([math.cos(r), math.sin(r)],\
                                  [-math.sin(r), math.cos(r)])
                vec = mat * (vecs2d[i - 1] - vecs2d[i])
                #newvecs2d.append(vec.normalize() * dist)
                newvecs2d.append(vec.normalize())
            else:
                vec1 = vecs2d[i-1] - vecs2d[i]
                if i == len(mass) -1:
                    vec2 = vecs2d[0] - vecs2d[i]
                else:
                    vec2 = vecs2d[i+1] - vecs2d[i]
                projvec = vec2.project(vec1)
                verticalvec = vec2 - projvec
                if vec1.dot(projvec) < 0:
                    x = -projvec.length
                else:
                    x = projvec.length
                if cross2D(vec1, verticalvec) < 0:
                    y = -verticalvec.length
                else:
                    y = verticalvec.length
                r = math.atan2(y, x)
                if r < 0:
                    r += 2 * math.pi
                mat = Math.Matrix([math.cos(r/2), math.sin(r/2)],\
                                  [-math.sin(r/2), math.cos(r/2)])
                vec = mat * vec1
                if math.sin(r/2) == 0.0:
                    d = 0.0
                else:
                    #d = dist / math.sin(r/2)
                    d = 1.0 / math.sin(r/2)
                newvecs2d.append(vec.normalize() * d)
                # for rotsum
                r = math.atan2(y, -x)
                rotsum += r
        if rotsum >= 0:
            newvecs2d = [v.negate() for v in newvecs2d]

        newvecs2d = [newvecs2d[i] + vecs2d[i] for i in range(len(newvecs2d))]
        mvvecs = []
        for i in range(len(newvecs2d)):
            v = vecs[i].copy()
            v.x = newvecs2d[i].x
            v.y = newvecs2d[i].y
            v = v * invq
            mvvecs.append(v - vecs_orig[i])


        for cnt, vert in enumerate(verts):
            if mod:
                index = dmmedict[vert.index]
                if not index:
                    continue
            else:
                index = vert.index
            if type == 'dist':
                ret_vecs[index] = mvvecs[cnt].normalize()
            else:
                ret_vecs[index] = mvvecs[cnt]
    return ret_vecs



def shift_faces_outline(scene, ob, dist, follow, type='min', mod=1, \
                        threthold=math.radians(5.0)):
    #threthold = math.radians(5.0)
    me_raw = ob.data
    if mod:
        dm, medmdict, dmmedict = get_mirrored_mesh(scene, ob)
        me = dm
    else:
        me = me_raw
    vertsco = [v.co for v in me.vertices]

    # make outside verts-verts list
    efdict = edge_face_dict(me, sel=2)
    outside_vv_list = [[] for i in range(len(me.vertices))]
    verts = [v for v in me.vertices if v.select and not v.hide]
    for key, faces in efdict.items():
        if len(faces) != 1:
            continue
        v1, v2 = key
        outside_vv_list[v1].append(v2)
        outside_vv_list[v2].append(v1)

    vfdict = vert_face_dict(me, sel=2)
    vedict = vert_edge_dict(me, sel=2)
    vert_vecs = [[] for i in range(len(me.vertices))] #  x outsideVec
    #vert_accum = [0.0 for i in range(len(me.vertices))]

    #  va2     /    vac(f.cent)
    #     \   /     |               /
    #      \ /______|______________/
    #     va0      vap   ->vr01    va1
    for vi0, findices in vfdict.items():
        if len(outside_vv_list[vi0]) != 2:
            continue
        # calc normal
        vi1, vi2 = outside_vv_list[vi0]
        va0 = vertsco[vi0]
        va1 = vertsco[vi1]
        va2 = vertsco[vi2]
        vr01 = (va1 - va0).normalize()
        vr02 = (va2 - va0).normalize()
        if follow and len(vedict[vi0]) > 2:
            angles = []
            #normals = []
            vindices = []
            for key in vedict[vi0]:
                if vi1 in key or vi2 in key:
                    continue
                vi3 = the_other(key, vi0)
                va3 = vertsco[vi3]
                vr03 = (va3 - va0).normalize()
                filist = efdict[key]
                if len(filist) != 2:
                    continue
                f1 = me.faces[filist[0]]
                f2 = me.faces[filist[1]]
                angle = f1.normal.angle(f2.normal)
                vr0c1 = f1.center - va0
                vr0p1 = vr0c1.project(vr03) # on vr03
                vrpc1 = (vr0c1 - vr0p1).normalize()
                vr0c2 = f2.center - va0
                vr0p2 = vr0c2.project(vr03) # on vr03
                vrpc2 = (vr0c2 - vr0p2).normalize()
                normal = (-vrpc1 + vrpc2) / 2
                angles.append(angle)
                vindices.append(vi3)

            angle_max = max(angles)
            if angle_max >= threthold and (follow == 1 or follow == 3) or \
               angle_max < threthold and (follow == 2 or follow == 3) and len(vedict[vi0]) == 3:
                # 1:3D, 2:2D, 3:2D&3D
                angle_max_index = angles.index(angle_max)
                mvvec = (vertsco[vindices[angle_max_index]] - va0).normalize()
                normal = None
            else:
                normal = (-vr01 + vr02) / 2
        else:
            normal = (-vr01 + vr02) / 2


        for fi in findices:
            # calc faces include outside edge
            f = me.faces[fi]
            if vi1 in f.vertices:
                va1 = vertsco[vi1]
            elif vi2 in f.vertices:
                va1 = vertsco[vi2]
            else:
                continue
            vr01 = (va1 - va0).normalize()

            vr0c = f.center - va0
            vr0p = vr0c.project(vr01)
            vrpc = vr0c - vr0p
            if normal:
                vaq, status = plane_intersect(va0, normal, f.center, f.center - vr01, 1)
                if not vaq or (len(vedict[vi0]) > 2 and status == 0):
                    continue
                vr0q = (vaq - va0).normalize()
                if vrpc.length and vr0q.length:
                    angle = vrpc.angle(vr0q)
                    vr0q *= shell_angle_to_dist(angle)
                    vert_vecs[vi0].append(vr0q)
                else:
                    vert_vecs[vi0].append(Vector())
            else:
                # along mvvec
                if vrpc.dot(mvvec) < SMALL_NUMBER:
                    continue
                angle = vr01.angle(mvvec)
                newvec = mvvec * shell_angle_to_dist_sin(angle)
                vert_vecs[vi0].append(newvec)

    me = me_raw
    #ret_vecs = [None for i in range(len(me.vertices))]
    ret_vecs = {}
    for index in range(len(me.vertices)):
        if mod:
            '''
            if index in dmmedict:
                i = dmmedict[index]
            else:
                continue
            if not i:
                continue
            '''
            i = medmdict[index]
        else:
            i = index
        if not vert_vecs[i]:
            continue

        if type == 'min':
            ret_vecs[index] = -min(vert_vecs[i], key=lambda x : x.length)
        elif type == 'max':
            ret_vecs[index] = -max(vert_vecs[i], key=lambda x : x.length)
        else:
            vec = Vector()
            for v in vert_vecs[i]:
                vec += v
            vec /= len(vert_vecs[i])

            if type == 'average':
                ret_vecs[index] = -vec
            else:
                ret_vecs[index] = -vec.normalize()

    return ret_vecs


class MESH_OT_shift_outline(bpy.types.Operator):
    bl_idname = 'mesh.shift_outline'
    bl_label = 'Shift Outline'
    bl_options = {'REGISTER', 'UNDO'}

    #bpy.data.window_managers['WinMan'].operators['Test'].v2

    dist = FloatProperty(name='Dist',
        description = 'tool tip ?',
        default = 0.00,
        min = -10.0,
        max = 10.0,
        soft_min = -10.0,
        soft_max = 10.0,
        step = 1,
        precision = 3,
        subtype = 'DISTANCE',
        unit = 'LENGTH')
    follow3d = BoolProperty(name = 'Follow edge 3D',
        description = 'tip',
        default=True)
    follow2d = BoolProperty(name = 'Follow edge 2D',
        description = 'tip',
        default=False)
    type = EnumProperty(items = (('average', 'Average', ''),
                                 ('min', 'Min', ''),
                                 ('max', 'Max', ''),
                                 ('dist', 'Dist', '')),
                        name="type",
                        description="",
                        default='min')
    mod = BoolProperty(name = 'Apply mirror modifier',
        description = 'tip',
        default=True)
    '''
    auto = BoolProperty(name = 'Auto calc plane',
        description = 'when edges selected only ...',
        default=True)
    '''
    mode = EnumProperty(items = (('auto', 'Auto', 'Auto calc plane normal'),
                                 ('right', 'Right', 'Right view'),
                                 ('front', 'Front', 'Front view'),
                                 ('top', 'Top', 'Top view'),
                                 ('normal', 'Plane normal', 'Plane normal')),
                        name="Edges normal",
                        description="",
                        default='auto')
    normal = FloatVectorProperty(name='Plane normal',
                                 description = 'plane normal',
                                 default = (0.0, 0.0, 1.0),
                                 step = 10,
                                 precision = 3,
                                 subtype = 'XYZ')

    threthold = FloatProperty(name='Threthold',
        description = 'tool tip ?',
        default = math.radians(5.0),
        min = 0.0,
        max = math.radians(45.0),
        soft_min = 0.0,
        soft_max = math.radians(45.0),
        step = 10,
        precision = 1,
        subtype = 'ANGLE',
        unit = 'ROTATION')

    '''v2 = EnumProperty(items = (('a','menu 1', 'tip1'),('b', 'menu 2', 'tip2')),
        name="Menu",
        description="menu?",
        default='a',
        options={'ANIMATABLE'})
    '''
    force_invoke = BoolProperty(name = 'Call Invoke Force',
                                description = '',
                                default=False,
                                options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if self.force_invoke:
            ## view3d.circle_menu
            self.invoke(context, None)
            self.force_invoke = False

        bpy.ops.object.mode_set(mode='OBJECT')

        dist = self.dist
        follow = self.follow3d + self.follow2d * 2
        type = self.type
        mod = self.mod
        mode = self.mode
        pnormal = self.normal
        threthold = self.threthold

        scene = context.scene
        ob = context.active_object

        p = self.p
        if follow != p.follow or type != p.type or mod != p.mod or \
           mode != p.mode or pnormal != p.pnormal or \
           threthold != p.threthold:
            # faces

            if self.f:
                vecs = shift_faces_outline(scene, ob, dist, follow, type, mod, threthold)
                p.vecs = vecs
            # edges
            if self.e:
                obmat = ob.matrix_world
                obinvmat = obmat.copy().invert()
                vec0 = obinvmat * Vector([0,0,0])
                if mode == 'auto':
                    normal = None
                elif mode == 'right':
                    normal = (obinvmat * Vector([1,0,0]) - vec0).normalize()
                elif mode == 'front':
                    normal = (obinvmat * Vector([0,1,0]) - vec0).normalize()
                elif mode == 'top':
                    normal = (obinvmat * Vector([0,0,1]) - vec0).normalize()
                else:
                    normal = (obinvmat * pnormal - vec0).normalize()
                vecs_e = shift_outline(scene, ob, dist, type, normal, mod)
                p.vecs_e = vecs_e

            if Normal != pnormal:
                Normal[:] = pnormal[:]
            p.follow = int(follow)
            p.type = type
            p.mod = mod
            p.mode = mode
            p.pnormal = pnormal.copy()
            p.threthold = threthold


        if dist != 0.0:
            if self.f:
                verts = ob.data.vertices
                vecs = self.p.vecs
                for i, vec in vecs.items():
                    verts[i].co += vec * dist # negative
            if self.e:
                verts = ob.data.vertices
                vecs_e = self.p.vecs_e
                for i, vec in vecs_e.items():
                    verts[i].co += vec * dist


        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}

    def invoke(self, context, event):
        self.normal[:] = Normal[:]
        context.area.tag_redraw()

        self.p = p = NullClass()
        p.follow = p.type = p.mod = p.mode = p.pnormal = None
        p.threthold = p.vecs = p.vecs_e = None

        bpy.ops.object.mode_set(mode='OBJECT')
        me = context.active_object.data
        efdict = edge_face_dict(me, sel=2)
        e = 0
        f = 0
        for key, faces in efdict.items():
            if faces:
                f += len(faces)
            else:
                e += 1
        self.e = e
        self.f = f
        bpy.ops.object.mode_set(mode='EDIT')
        if not self.force_invoke:
            self.execute(context)

        return {'FINISHED'}

def em_make_hq_normals(scene, ob, mechanical, selected, local, mod, threthold=math.radians(1.0)):
    if mod:
        #me = ob.data
        me, medmdict, dmmedict = get_mirrored_mesh(scene, ob)
    else:
        me = ob.data
    if not local:
        mesh = me.copy()
        mesh.transform(ob.matrix_world)
        me = mesh

    normals = [Vector() for i in range(len(me.vertices))]

    if mechanical:
        pass
        '''
        # new code
        if selected:
            vedict = vert_edge_dict(me, sel=1, key=False)
            vfdict = vert_face_dict(me, sel=2)
            efdict = edge_face_dict(me, sel=2, key=False)
            kedict = key_edge_dict(me, sel=2)
        else:
            vedict = vert_edge_dict(me, sel=-1, key=False)
            vfdict = vert_face_dict(me, sel=-1)
            efdict = edge_face_dict(me, sel=-1, key=False)
            kedict = key_edge_dict(me, sel=-1)

        for vi, faces in vfdict.items():
            if not faces:
                continue
            if len(faces) == 1:
                fi = faces[0]
                normals[vi] = me.faces[fi].normal.copy()
            elif len(faces) == 2:
                f1no, f2no = [me.faces[fi].normal for fi in faces]
                normals[vi] = (f1no + f2no).normalize()
            else:
                outside = []
                for ei in vedict[vi]:
                    efs = efdict[ei]
                    if len(efs) == 0:
                        continue
                    elif len(efs) == 1:
                        outside.append(efs[0])
                if len(outside) == 0:
                    # closed
                    next = False
                    for ei in vedict[vi]:
                        if len(efdict[ei]) > 2:
                            next = True
                            break
                    if next:
                        normals[vi] = Vector()
                        continue

                    fi = faces[0]
                    face_list = [fi]
                    face = me.faces[fi]
                    key, key2 = [key for key in face.edge_keys if vi in key]
                    for i in range(len(faces) - 1):
                        finext = [f for f in efdict[kedict[key]] \
                                  if f != face_list[-1]][0]
                        facenext = me.faces[finext]
                        keynext = [k for k in facenext.edge_keys \
                                   if k != key and vi in k][0]

                        face_list.append(finext)
                        face = facenext
                        key = keynext

                    angle_list = []
                    for i in range(len(faces)):
                        f1no = me.faces[face_list[i]].normal
                        if i == len(faces) - 1:
                            f2no = me.faces[face_list[0]].normal
                        else:
                            f2no = me.faces[face_list[i + 1]].normal
                        angle_list.append(f1no.angle(f2no))

                    for i, angle in enumerate(angle_list):
                        if angle > threthold:
                            break
                    else:
                        vec = Vector()
                        for fi in faces:
                            vec += me.faces[fi].normal
                        normals[vi] = vec.normalize()
                        continue
                    # i+1
                    i += 1
                    if i == len(face_list):
                        i = 0
                    # [f[0] - a[0] - f[1] - a[1] - ...]
                    angle_list = angle_list[i:] + angle_list[:i]
                    face_list = face_list[i:] + face_list[:i]
                    vec = Vector()
                    tmp_vec = Vector()
                    for i in range(len(face_list)):
                        fi = face_list[i]
                        tmp_vec += me.faces[fi].normal
                        angle = angle_list[i]
                        if angle > threthold:
                            vec += tmp_vec.normalize()
                            tmp_vec = Vector()
                    normals[vi] = vec.normalize()

                elif len(outside) == 2:
                    # 'open'
                    f1nor, f2nor = [me.faces[fi].normal for fi in outside]
                    normals[vi] = (f1nor + f2nor).normalize()
                else:
                    # normal
                    v = Vector()
                    for fi in faces:
                        v += me.faces[fi].normal
                    v /= len(faces)
                    normals[vi] = v.normalize()
        '''
    else:
        # built-in

        if selected:
            vedict = vert_edge_dict(me, sel=1, key=True)
            efdict = edge_face_dict(me, sel=2, key=True)
            calcverts = set()
            for f in [f for f in me.faces if f.select and not f.hide]:
                for v in f.vertices:
                    calcverts.add(v)
        else:
            vedict = vert_edge_dict(me, sel=-1, key=True)
            efdict = edge_face_dict(me, sel=-1, key=True)
            calcverts = [i for i in range(len(me.vertices))]

        vf = [None for i in range(len(me.vertices))]
        for key, faces in efdict.items():
            v1, v2 = key
            if not faces:
                continue
            if len(faces) == 2:
                f1 = me.faces[faces[0]]
                f2 = me.faces[faces[1]]
                angle = angle_normalized_v3v3(f1.normal, f2.normal)
                if angle > 0.0:
                    edge_normal = (f1.normal + f2.normal).normalize()
                    edge_normal *= angle
                else:
                    vf[v1] = vf[v2] = faces[0]
                    continue
            else:
                f1 = me.faces[faces[0]]
                edge_normal = f1.normal
                edge_normal *= math.pi / 2
            normals[v1] += edge_normal
            normals[v2] += edge_normal
        for i in calcverts:
            if normals[i].length > 0.0:
                normals[i] = normals[i].normalize()
            elif vf[i] is not None:
                f = me.faces[vf[i]]
                normals[i] = f.normal.copy()


    if mod:
        mesh = ob.data
        new_normals = [Vector() for i in range(len(mesh.vertices))]
        for i, vec in enumerate(normals):
            if dmmedict[i] is not None:
                new_normals[dmmedict[i]] = vec
        normals = new_normals

    return normals

def solidify(me, dist, vertsnormal_in, lock, keepdist, matrix=None):
    threthold = 1e-6

    coval = [1 - val for val in lock]

    vertsnormal = vertsnormal_in

    vert_angles = [0.0 for i in range(len(me.vertices))]
    vert_accum = [0.0 for i in range(len(me.vertices))]

    if matrix: # global coordinate
        mat = matrix
        #imat = matrix.copy().invert()
        rmat = matrix.to_3x3()
        rimat = rmat.copy().invert()

        vertsco = [mat * v.co for v in me.vertices]
        fsnormal = [None for f in me.faces]
        for f in me.faces:
            vecs = [vertsco[vi] for vi in f.vertices]
            if len(f.vertices) == 4:
                fnormal = Geo.QuadNormal(*vecs)
            else:
                fnormal = Geo.TriangleNormal(*vecs)
            if fnormal.dot(rmat * f.normal) < 0.0:
                fnormal.negate()
            fsnormal[f.index] = fnormal

        for i, f in enumerate(me.faces):
            if not f.select:
                continue

            vecs = [vertsco[vi] for vi in f.vertices]

            if len(f.vertices) == 4:
                face_angles = angle_quad_v3(*vecs)
            else:
                face_angles = angle_tri_v3(*vecs)
            for j, vindex in enumerate(f.vertices):
                vert_accum[vindex] += face_angles[j]
                angle = angle_normalized_v3v3(vertsnormal[vindex], fsnormal[i])
                vert_angles[vindex] += shell_angle_to_dist(angle) * face_angles[j]

        for i, vert in enumerate(me.vertices):
            if vert_accum[i]:
                v = vertsnormal[i] * (dist * vert_angles[i] / vert_accum[i])
                if sum(lock):
                    vec = Vector([v[i] * coval[i] for i in range(3)])
                    if keepdist:
                        if v.dot(vec) > threthold:
                            vec = vec.normalize() * v.length
                        else:
                            vec = Vector()
                    vert.co += rimat * vec
                else:
                    vert.co += rimat * v

    else:
        for i, f in enumerate(me.faces):
            if not f.select:
                continue

            if len(f.vertices) == 4:
                face_angles = angle_quad_v3(*[me.vertices[vi].co for vi in f.vertices])
            else:
                face_angles = angle_tri_v3(*[me.vertices[vi].co for vi in f.vertices])
            for j, vindex in enumerate(f.vertices):
                vert_accum[vindex] += face_angles[j]
                angle = angle_normalized_v3v3(vertsnormal[vindex], f.normal)
                vert_angles[vindex] += shell_angle_to_dist(angle) * face_angles[j]

        for i, vert in enumerate(me.vertices):
            if vert_accum[i]: # zero if unselected
                v = vertsnormal[i] * (dist * vert_angles[i] / vert_accum[i])
                if sum(lock):
                    vec = Vector([v[i] * coval[i] for i in range(3)])
                    if keepdist:
                        if v.dot(vec) > threthold:
                            vec = vec.normalize() * v.length
                        else:
                            vec = Vector()
                    vert.co += vec
                else:
                    vert.co += v

class MESH_OT_solidify2(bpy.types.Operator):
    bl_idname = 'mesh.solidify2'
    bl_label = 'Solidify2'
    bl_options = {'REGISTER', 'UNDO'}

    #bpy.data.window_managers['WinMan'].operators['Test'].v2

    dist = FloatProperty(name='Dist',
        description = 'distance',
        default = 0.0,
        min = -10.0,
        max = 10.0,
        soft_min = -10.0,
        soft_max = 10.0,
        step = 1,
        precision = 3,
        subtype = 'DISTANCE',
        unit = 'LENGTH')

    select = BoolProperty(name = 'Calc Sel & not Hide',
        description = 'Calculate verts normal',
        default = True)

    local = BoolProperty(name = 'Local coordinate',
        description = 'Use local coordinate',
        default = True)

    lock = BoolVectorProperty(name = 'Lock',
        description = 'Lock axis',
        default=[False, False, False],
        subtype='XYZ')

    keepdist = BoolProperty(name = 'Keep dist',
        description = 'Keep dist when locked',
        default = False)

    mod = BoolProperty(name = 'Apply mirror modifier',
        description = '',
        default=True)

    mechanical = BoolProperty(name = 'Mechanical',
        description = 'on: original, off: built-in solidify',
        default = False,
        options = {'HIDDEN'})

    force_invoke = BoolProperty(name = 'Call Invoke Force',
                               description = '',
                               default=False,
                               options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if self.force_invoke:
            ## view3d.circle_menu
            self.invoke(context, None)
            self.force_invoke = False

        bpy.ops.object.mode_set(mode='OBJECT')

        scene = context.scene
        ob = context.active_object
        me = ob.data

        dist = self.dist

        mechanical = int(self.mechanical)
        selected = int(self.select)
        local = int(self.local)
        lock = [int(l) for l in self.lock]
        keepdist = int(self.keepdist)
        mod = int(self.mod)
        mechanical_bak, selected_bak, local_bak, lock_bak, keepdist_bak, mod_bak = self.bak
        if mechanical != mechanical_bak or \
          selected != selected_bak or local != local_bak or \
          lock[0] != lock_bak[0] or lock[1] != lock_bak[1] or lock[2] != lock_bak[2] or\
          keepdist != keepdist_bak or mod != mod_bak:
            self.verticesnormal = em_make_hq_normals(scene, ob, mechanical, selected, local, mod)
            self.bak = [mechanical, selected, local, lock, keepdist, mod]

        if dist != 0.0 and not (lock[0] and lock[1] and lock[2]):
            if local:
                solidify(me, dist, self.verticesnormal, lock, keepdist, None)
            else:
                solidify(me, dist, self.verticesnormal, lock, keepdist, ob.matrix_world)

        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='OBJECT')
        scene = context.scene
        ob = context.active_object
        me = ob.data
        mechanical = self.mechanical
        dist = self.dist
        selected = self.select
        local = self.local
        lock = self.lock
        keepdist = self.keepdist
        mod = self.mod

        self.verticesnormal = em_make_hq_normals(scene, ob, mechanical, selected, local, mod)
        self.bak = [int(mechanical), int(selected), int(local), [int(l) for l in lock], keepdist, mod]

        bpy.ops.object.mode_set(mode='EDIT')

        context.area.tag_redraw()
        if not self.force_invoke:
            self.execute(context)
        return {'FINISHED'}

class MESH_OT_select_verts(bpy.types.Operator):
    bl_idname = 'mesh.select_verts'
    bl_label = 'Select Verts'
    bl_options = {'REGISTER', 'UNDO'}

    type = EnumProperty(items = (('rerative', 'Rerative', ''),
                                 ('absolute', 'Absolute', '')),
                        name="Coordinate type",
                        description="",
                        default='rerative')

    select = BoolProperty(name = 'Select',
        description = 'Select or deselect',
        default = True)

    infinite = BoolVectorProperty(name = 'Select Infinite',
                          description = '',
                          default=(False, False, False),
                          subtype='XYZ')

    samedist = BoolProperty(name = 'Copy Max -> Min',
                          description = 'Max Dist == Min Dist',
                          default=True)

    dist_max = FloatVectorProperty(name='Max Dist',
        description = 'distance',
        default = (0.0, 0.0, 0.0),
        min = -100.0,
        max = 100.0,
        soft_min = -100.0,
        soft_max = 100.0,
        step = 1,
        precision = 3,
        subtype = 'XYZ')

    dist_min = FloatVectorProperty(name='Min Dist',
        description = 'distance',
        default = (0.0, 0.0, 0.0),
        min = -100.0,
        max = 100.0,
        soft_min = -100.0,
        soft_max = 100.0,
        step = 1,
        precision = 3,
        subtype = 'XYZ')

    threthold = FloatProperty(name='Threthold',
                         description = 'min, max +- val * 1E-3',
                         default = 0.01,
                         min = 0.0,
                         max = 100.0,
                         soft_min = 0.0,
                         soft_max = 100.0,
                         step = 0.1,
                         precision = 4)

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == 'MESH' and \
                    context.active_object.mode == 'EDIT'
        else:
            return False

    def execute(self, context):
        type = self.type
        select = self.select
        infinite = self.infinite
        samedist = self.samedist
        dist_max = self.dist_max
        dist_min = self.dist_min
        threthold = self.threthold * 1E-3

        # copy dist
        if samedist:
            self.dist_min[:] = dist_max.copy().negate()[:]

        if infinite[0] and infinite[1] and infinite[2]:
            bpy.ops.object.mode_set(mode='EDIT')
            return

        # change vertex select mode
        ob = context.active_object
        me = ob.data
        mesh_mode = list(bpy.context.tool_settings.mesh_select_mode)
        if not mesh_mode[0]:
            bpy.context.tool_settings.mesh_select_mode[0] = True

        # main
        bpy.ops.object.mode_set(mode='OBJECT')
        if type == 'rerative':
            # select only
            selvecs = [v.co for v in me.vertices if v.select and not v.hide]
            if not selvecs:
                bpy.ops.object.mode_set(mode='EDIT')
                return {'FINISHED'}
            minvec = selvecs[0].copy()
            maxvec = selvecs[0].copy()
            for v in selvecs[1:]:
                for i in range(3):
                    if v[i] < minvec[i]:
                        minvec[i] = v[i]
                    if v[i] > maxvec[i]:
                        maxvec[i] = v[i]
            minvec += dist_min - Vector([threthold, threthold, threthold])
            maxvec += dist_max + Vector([threthold, threthold, threthold])

            for v in [v for v in me.vertices if not v.hide]:
                sel = True
                for i in range(3):
                    if infinite[i]:
                        continue
                    else:
                        if minvec[i] <= v.co[i] <= maxvec[i]:
                            pass
                        else:
                            sel = False
                            break
                if sel:
                    v.select = True
        elif type == 'absolute':
            minvec = Vector([0, 0, 0]) - Vector([threthold, threthold, threthold])
            minvec[:] = dist_min[:]
            maxvec = Vector([0, 0, 0]) + Vector([threthold, threthold, threthold])
            maxvec[:] = dist_max[:]
            for v in [v for v in me.vertices if not v.hide]:
                sel = True
                for i in range(3):
                    if infinite[i]:
                        continue
                    else:
                        if minvec[i] <= v.co[i] <= maxvec[i]:
                            pass
                        else:
                            sel = False
                            break
                if sel:
                    v.select = select is True

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.tool_settings.mesh_select_mode[:] = mesh_mode
        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

class MESH_OT_edge_intersect(bpy.types.Operator):
    bl_idname = 'mesh.edge_intersect'
    bl_label = 'Edge Intersect'
    bl_options = {'REGISTER', 'UNDO'}

    mode = EnumProperty(items = (('move', 'Move', ''),
                                 ('vert', 'Add vert', ''),
                                 ('edge', 'Add edges', '')),
                                 name="Mode",
                                 description="mode",
                                 default='move')

    fac = FloatProperty(name = 'Fac',
                         description = 'Threthold',
                         default = 1.0, step = 1,
                         min = 0.0, max = 1.0,
                         soft_min = 0.0, soft_max = 1.0)

    rmdoubles = BoolProperty(name = 'Remove Doubles',
                             description = '',
                             default=False)
    limit = FloatProperty(name = 'Limit',
                         description = 'Remove Doubles Limit',
                         default = 0.0001, step = 00.1, precision = 4,
                         min = 1E-6, max = 50,
                         soft_min = 1E-6, soft_max = 1.0)

    force_invoke = BoolProperty(name = 'Call Invoke Force',
                                description = '',
                                default=False,
                                options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object

    def init(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')

        ob = context.active_object
        me = ob.data
        vvdict = vert_vert_dict(me, sel=0)
        vedict = vert_edge_dict(me, sel=0, key=False)
        seledges = [e for e in me.edges if e.select and not e.hide]
        selverts = [v for v in me.vertices if v.select and not v.hide]

        e1 = e2 = v1 = v2 = v3 = v4 = None # v1, v2 = active
        if len(seledges) == 2 and len(selverts) == 4:
            e1, e2 = seledges
        elif len(seledges) == 1 and len(selverts) == 3:
            e1 = seledges[0]
            v3 = [v.index for v in selverts if v.index not in e1.key][0]
            if len(vedict[v3]) == 1:
               e2 = me.edges[vedict[v3][0]]
        elif len(seledges) == 0 and len(selverts) == 2:
            v1, v3 = [v.index for v in selverts]
            if len(vedict[v1]) == 1 and len(vedict[v3]) == 1:
                e1 = me.edges[vedict[v1][0]]
                e2 = me.edges[vedict[v3][0]]
        if e1 is None or  e2 is None:
            return

        e1v1, e1v2 = [me.vertices[i].co for i in e1.key]
        e2v1, e2v2 = [me.vertices[i].co for i in e2.key]
        intersect = Geo.LineIntersect(e1v1, e1v2, e2v1, e2v2)
        if not intersect:
            return

        vecs = {}
        for i, v, e in [[0, v1, e1], [1, v3, e2]]:
            if v is None:
                l1 = (me.vertices[e.key[0]].co - intersect[i]).length
                l2 = (me.vertices[e.key[1]].co - intersect[i]).length
                vi = e.key[0] if l1 < l2 else e.key[1]
                vecs[vi] = intersect[i] - me.vertices[vi].co
            else:
                vecs[v] = intersect[0] - me.vertices[v].co

        self.p.vecs = vecs
        self.p.vnum = len(me.vertices)
        self.p.enum = len(me.edges)

        bpy.ops.object.mode_set(mode='EDIT')

    def execute(self, context):
        if self.force_invoke:
            ## view3d.circle_menu
            self.invoke(context, None)
            self.force_invoke = False

        vecs = self.p.vecs
        vnum = self.p.vnum
        enum = self.p.enum
        mode = self.mode
        fac = self.fac
        rmdoubles = self.rmdoubles
        limit = self.limit

        ob = context.active_object
        me = ob.data

        if vecs is None:
            return {'FINISHED'}

        bpy.ops.object.mode_set(mode='OBJECT')
        if mode == 'move':
            for i, vec in vecs.items():
                co = me.vertices[i].co
                me.vertices[i].co = co + vec * fac
        elif mode == 'vert':
            me.vertices.add(2)
            me.edges.add(0)
            me.faces.add(0)
            cnt = 0
            for i, vec in vecs.items():
                co = me.vertices[i].co + vec * fac
                me.vertices[vnum + cnt].co = co
                cnt += 1

        elif mode == 'edge':
            me.vertices.add(2)
            me.edges.add(2)
            me.faces.add(0)
            cnt = 0
            for i, vec in vecs.items():
                co = me.vertices[i].co + vec * fac
                me.vertices[vnum + cnt].co = co
                me.edges[enum + cnt].vertices = [vnum + cnt, i]
                cnt += 1

        bpy.ops.object.mode_set(mode='EDIT')

        if rmdoubles:
            bpy.ops.mesh.remove_doubles(limit)

        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='OBJECT')

        self.p = p = NullClass()
        p.vnum = p.enum = p.vecs = None

        self.init(context)
        if not self.force_invoke:
            self.execute(context)

        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

class MESH_OT_edge_slide2(bpy.types.Operator):
    global config
    bl_idname = 'mesh.edge_slide2'
    bl_label = 'Edge Slide'
    bl_options = {'REGISTER', 'UNDO'}

    center_mode = BoolProperty(name = 'center mode', description = '', default=True)
    dist = FloatProperty(name = 'Dist',
                         description = 'Threthold',
                         default = 0.0, step = 1,
                         precision = 3,
                         subtype = 'DISTANCE',
                         unit = 'LENGTH')
    consider_angle = BoolProperty(name = 'consider angle', description = '', default=False)
    auto = BoolProperty(name = 'auto select vec', description = 'if center mode is False', default=True)
    second_vec = BoolProperty(name = 'vec1 -> vec2', description = '', default=False)
    limit_max = BoolProperty(name = 'limit max', description = '', default=True)
    limit_min = BoolProperty(name = 'limit min', description = '', default=True)

    force_invoke = BoolProperty(name = 'Call Invoke Force',
                                description = '',
                                default=False,
                                options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object

    def init(self, context):
        pymesh = self.p.pymesh

        '''
        ## 
        for v in pymesh.vertices:
            v.f1 = v.f2 = 0 # f1: , f2: if e.f1 >= 1: verts = e.vertices; if not v.sel(): v.f2 = 1
        for e in pymesh.edges:
            e.f1 = 0 # f1:-1:, 0:, 1:V, 2:-V
        for f in pymesh.faces:
            f.f1 = 0 # f1:
        '''

        ## edgeface1~2
        s = 0
        for e in pymesh.edges:
            if e.sel():
                i = 0
                for f in e.faces:
                    if f.h == 0:
                        i += 1
                if not 1 <= i <= 2:
                    calc = False
                    break
                s += 1
        else:
            calc = True
        if not calc or s == 0:
            return None, 0

        ## 1~2flag
        for v in pymesh.vertices:
            if v.sel():
                i = 0
                for e in v.edges:
                    if e.sel():
                        i += 1
                if i == 1:
                    v.f1 = 1 # 
                elif not 1 <= i <= 2:
                    calc = False
                    break
        else:
            calc = True

        ## 
        pass_ends = []
        for v in pymesh.vertices:
            if v.f1:
                pass_ends.append(v)
        if len(pass_ends) not in [0, 2]:
            calc = False

        if not calc:
            return None, 1

        '''
        ## faceedge
        for f in pymesh.faces:
            if not f.h:
                i = 0
                for e in f.edges:
                    if e.sel():
                        i += 1
                if i > 1:
                    calc = False
                    break
        else:
            calc = True
        if not calc:
            return None, 2
        '''

        ##  -1
        for e in pymesh.edges:
            if e.s or e.h:
                continue
            v1, v2 = e.vertices
            if v1.s or v2.s:
                e.f1 = -1


        ## facef2
        for f in pymesh.faces:
            i = 0
            for e in f.edges:
                if e.sel():
                    i += 1
            f.f1 = i

        ## pass_endse.f1
        if pass_ends:
            for v in pass_ends:
                for e in v.edges:
                    if e.h:
                        continue
                    if sum([f.f1 for f in e.faces]) == 0:
                        e.f1 = 0

        ## e.f1 face3
        for e in pymesh.edges:
            if e.f1:
                if len([f for f in e.faces if f.h == 0]) > 2:
                    return None, 3

        ## 
        if pass_ends:
            v_start, v_end = pass_ends
        else:
            for v in pymesh.vertices:
                if v.sel():
                    v_start = v_end = v
                    break

        e_starts = []
        for e in v_start.edges:
            if e.h == 0 and e.f1 == -1:
                for f in e.faces:
                    if f.h == 0:
                        if f.f1 >= 1:
                            e_starts.append(e)
                            break

        ## 
        stage = 1
        for e_start in e_starts:
            e = e_start
            if e.f1 != -1:
                continue
            init = False
            cnt = -1
            while True:
                cnt += 1
                if cnt == 0:
                    e.f1 = stage
                    f = [f for f in e.faces if f.h == 0 and f.f1 >= 1][0]
                    for e in f.edges:
                        if e.f1 == -1:
                            break
                    continue

                faces = [f for f in e.faces if f.h == 0]
                if pass_ends:
                    if e.vertices[0] == v_end or e.vertices[1] == v_end:
                        e.f1 = stage
                        break
                    elif len(faces) == 1:
                        # v_end
                        init = True
                        break
                else:
                    if e.f1 == stage:
                        break
                    elif len(faces) == 1:
                        init = True
                        break
                e.f1 = stage
                f = faces[0] if faces[0] != f else faces[1]
                for e in f.edges:
                    if e.f1 == -1:
                        break
                else:
                    # not pass_ends, while-loop end
                    break
            if init:
                #e.f1 == stage-1
                for e in pymesh.edges:
                    if e.f1 == stage:
                        e.f1 = -1
            else:
                stage += 1

        #print([(e.i, e.f1) for e in pymesh.edges if e.f1])

        #*** Trans Vector ***#
        ## add vec to class
        for v in pymesh.vertices:
            v.vec1 = None
            v.vec2 = None
            v.vec1len_center_and_next_path = [0.0, 0.0]
            v.vec2len_center_and_next_path = [0.0, 0.0]

        for v in pymesh.vertices:
            if v.sel():
                vecs1 = []
                vecs2 = []
                for e in v.edges:
                    v2 = e.vert_another(v)
                    #v2 = e.vertices[0] if e.vertices[0] != v else e.vertices[1]
                    vec3 = v2.co - v.co
                    if e.f1 == 1:
                        vecs1.append(vec3)
                        v2.f2 = 1 # execute()
                    elif e.f1 == 2:
                        vecs2.append(vec3)
                        v2.f2 = 2
                if vecs1:
                    v.vec1 = reduce(lambda a,b: a+b/len(vecs1), vecs1, Vector())
                if vecs2:
                    v.vec2 = reduce(lambda a,b: a+b/len(vecs2), vecs2, Vector())

        ## f.f2 = stage; if f.f2 and e.f1 == 0: e.f2 = stage
        for f in pymesh.faces:
            if f.h:
                continue
            f2 = 0
            for e in f.edges:
                if e.f1 >= 1:
                   f2 = e.f1
            f.f2 = f2
            if f2:
                for e in f.edges:
                    if e.h == 0 and e.s == 0 and e.f1 == 0:
                        e.f2 = f2


        for v in pymesh.vertices:
            if not v.sel():
                continue
            for stage in (1, 2):
                if stage == 1:
                    vec = v.vec1
                    veclen_center_and_next_path = v.vec1len_center_and_next_path
                else:
                    vec = v.vec2
                    veclen_center_and_next_path = v.vec2len_center_and_next_path
                edges = [e for e in v.edges if e.f1 == stage]
                if len(edges) == 0:
                    continue
                ## veclen_next_path
                if len(edges) == 1:
                    #   -e2--v2--e2- next_path
                    #        |e
                    #     ---v---- path(selected edges)
                    e = edges[0]
                    v2 = e.vert_another(v)
                    vec_v_v2 = v2.co - v.co
                    edges_in_next_path = [e for e in v2.edges if e.vert_another(v2).f2 == stage]
                    if edges_in_next_path:
                        veclen_next_path = 0.0
                        for e2 in edges_in_next_path:
                            v3 = e2.vert_another(v2)
                            vec_v2_v3 = v3.co - v2.co
                            if vec.length > 0.0 and vec_v2_v3.length > 0.0:
                                veclen_next_path += 1.0 / abs(math.sin(vec_v2_v3.angle(-vec_v_v2)))
                            else:
                                veclen_next_path += 1.0
                        veclen_next_path /= len(edges_in_next_path)
                    else:
                        # ____
                        # |\/|
                        # |/\|
                        # 
                        veclen_next_path = 1.0
                else:
                    edges2 = []
                    for e in edges:
                        for f in e.faces: # len(e.faces) == 2
                            if len([e for e in f.edges if e in edges]) == 1:
                                edges2.append(e)
                                break
                    v2 = edges2[0].vert_another(v)
                    v3 = edges2[1].vert_another(v)
                    vec_v3_v2 = v2.co - v3.co
                    if vec.length > 0.0 and vec2.length > 0.0:
                        veclen_next_path = 1.0 / abs(math.sin(vec.angle(vec_v3_v2)))
                    else:
                        veclen_next_path = 1.0

                veclen_center_and_next_path[1] = veclen_next_path

                ## veclen_center
                edges_sel = [e for e in v.edges if e.sel()]
                veclen_center = 0.0
                for e in edges_sel:
                    v2 = e.vert_another(v)
                    vec_v_v2 = v2.co - v.co
                    if vec.length > 0.0 and vec_v_v2.length > 0.0:
                        veclen_center += 1.0 / abs(math.sin(vec.angle(vec_v_v2)))
                    else:
                        veclen_center += 1.0
                veclen_center /= len(edges_sel)
                veclen_center_and_next_path[0] = veclen_center

        return True, 99


    def execute(self, context):
        if self.force_invoke:
            ## view3d.circle_menu
            self.invoke(context, None)
            self.force_invoke = False

        bpy.ops.object.mode_set(mode='OBJECT')
        pymesh = self.p.pymesh
        status = self.p.status
        center_mode = self.center_mode
        dist = self.dist
        consider_angle = self.consider_angle
        auto = self.auto
        second_vec = self.second_vec
        limit_max = self.limit_max
        limit_min = self.limit_min

        if status[0] is None:
            bpy.ops.object.mode_set(mode='EDIT')
            return {'FINISHED'}

        me = context.active_object.data
        max_dist = 0.0
        for v in pymesh.vertices:
            if second_vec == False or (center_mode and auto): # default
                vec = v.vec1
                if vec is None:
                    continue
                vec_sub = v.vec2 if v.vec2 else None
                veclen_center_and_next_path = v.vec1len_center_and_next_path
                veclen_center_and_next_path_sub = v.vec2len_center_and_next_path
            else:
                vec = v.vec2
                if vec is None:
                    continue
                vec_sub = v.vec1 if v.vec1 else None
                veclen_center_and_next_path = v.vec2len_center_and_next_path
                veclen_center_and_next_path_sub = v.vec1len_center_and_next_path

            if center_mode == True:
                if auto:
                    if dist < 0.0:
                        vec = vec_sub
                        if vec is None:
                            continue
                        veclen_center_and_next_path = veclen_center_and_next_path_sub
                    if consider_angle:
                       d = abs(dist * veclen_center_and_next_path[0])
                    else:
                        d = abs(dist)
                    if limit_max:
                        d = min(d, vec.length)
                else:
                    if consider_angle:
                       d = dist * veclen_center_and_next_path[0]
                    else:
                        d = dist
                    if limit_min:
                        d = max(0.0, d)
                    if limit_max:
                        d = min(d, vec.length)
                co = v.co + vec.copy().normalize() * d
            else:
                # auto
                if consider_angle:
                    d = dist * veclen_center_and_next_path[1]
                else:
                    d = dist
                if limit_min:
                    d = max(0.0, d)
                if limit_max:
                    d = min(d, vec.length)
                co = v.co + vec
                co -= vec.copy().normalize() * d
            if limit_max:
                max_dist = max(max_dist, vec.length)

            me.vertices[v.i].co = co


        if limit_max:
            if abs(dist) > abs(max_dist):
                self.dist = cmp(dist, 0.0) * max_dist
        if limit_min and center_mode and not auto:
            if dist < 0.0:
                dist = self.dist = 0.0
        elif limit_min and not center_mode:
            if dist < 0.0:
                dist = self.dist = 0.0

        bpy.ops.object.mode_set(mode='EDIT')

        # update config
        config.edge_slide2_center_mode = self.center_mode
        config.edge_slide2_consider_angle = self.consider_angle
        config.edge_slide2_auto = self.auto
        config.edge_slide2_limit_max = self.limit_max
        config.edge_slide2_limit_min = self.limit_min

        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='OBJECT')
        me = context.active_object.data
        pymesh = PyMesh(me)

        self.p = p = NullClass()
        p.pymesh = pymesh
        p.status = None

        # read config
        self.center_mode = config.edge_slide2_center_mode
        self.consider_angle = config.edge_slide2_consider_angle
        self.auto = config.edge_slide2_auto
        self.limit_max = config.edge_slide2_limit_max
        self.limit_min = config.edge_slide2_limit_min

        context.area.tag_redraw()
        status = self.init(context)
        self.p.status = status
        #print(status)
        if not self.force_invoke:
            self.execute(context)

        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

class MESH_MT_align_verts_to_plane(bpy.types.Menu):
    bl_idname = 'mesh.align_verts_to_plane_menu'
    bl_label = "Align Verts to Plane"

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.mode == 'EDIT'
        else:
            return False

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'
        '''
        layout.operator('mesh.align_edges_to_plane', text='Move one side').mode = 'single'
        layout.operator('mesh.align_edges_to_plane', text='Move edges').mode = 'double'
        layout.operator('mesh.align_edges_to_plane', text= 'Add edges').mode = 'add'
        '''
        layout.operator('mesh.align_verts_to_plane', text='X').mode = 'x'
        layout.operator('mesh.align_verts_to_plane', text='Y').mode = 'y'
        layout.operator('mesh.align_verts_to_plane', text='Z').mode = 'z'
        layout.operator('mesh.align_verts_to_plane', text='X (local)').mode = 'lx'
        layout.operator('mesh.align_verts_to_plane', text='Y (local)').mode = 'ly'
        layout.operator('mesh.align_verts_to_plane', text='Z (local)').mode = 'lz'
        layout.operator('mesh.align_verts_to_plane', text='X (View)').mode = 'vx'
        layout.operator('mesh.align_verts_to_plane', text='Y (View)').mode = 'vy'
        layout.operator('mesh.align_verts_to_plane', text='Custom Axis').mode = 'ax'
        layout.operator('mesh.align_verts_to_plane', text='Plane Normal').mode = 'nor'

class MESH_MT_vertex_align(bpy.types.Menu):
    bl_idname = 'mesh.vertex_align'
    bl_label = "Vertex Align"

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.mode == 'EDIT'
        else:
            return False

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.operator('mesh.mark_plane', text='Mark Target Plane')
        layout.operator('mesh.mark_axis', text='Mark Custom Axis')
        layout.separator()
        '''layout.operator('mesh.align_verts_to_plane', text='Move X').mode = 'x'
        layout.operator('mesh.align_verts_to_plane', text='Move Y').mode = 'y'
        layout.operator('mesh.align_verts_to_plane', text='Move Z').mode = 'z'
        layout.operator('mesh.align_verts_to_plane', text='Move Local X').mode = 'lx'
        layout.operator('mesh.align_verts_to_plane', text='Move Local Y').mode = 'ly'
        layout.operator('mesh.align_verts_to_plane', text='Move Local Z').mode = 'lz'
        layout.operator('mesh.align_verts_to_plane', text='Move Custom Axis').mode = 'ax'
        layout.operator('mesh.align_verts_to_plane', text='Move Plane Normal').mode = 'nor'
        '''
        layout.menu('mesh.align_verts_to_plane_menu', text='Align Verts', icon='VERTEXSEL')
        layout.menu('mesh.align_edges_to_plane_menu', text='Align Edges', icon='EDGESEL')
        layout.separator()
        layout.operator('mesh.unbend_edges', text='Edge Unbend', icon='EDGESEL')
        layout.operator('mesh.edge_intersect', text='Edge Intersect', icon='EDGESEL')
        layout.operator('mesh.edge_slide2', text='Edge Slide', icon='EDGESEL')
        layout.separator()
        layout.operator('mesh.solidify2', text='Solidify', icon='FACESEL')
        layout.operator('mesh.shift_outline', text='Shift faces outline', icon='FACESEL')
        layout.separator()
        layout.operator('mesh.select_verts', text='Select Verts', icon='VERTEXSEL')


classes = [MESH_OT_mark_plane,
           MESH_OT_mark_axis,
           MESH_OT_align_verts_to_plane,
           MESH_OT_align_edges_to_plane,
           #AlignToPlane,
           #AlignEdgesToPlane,
           MESH_OT_unbend_edges,
           MESH_OT_shift_outline,
           MESH_OT_solidify2,
           MESH_MT_align_verts_to_plane,
           MESH_MT_align_edges_to_plane,
           MESH_MT_vertex_align,
           MESH_OT_select_verts,
           MESH_OT_edge_intersect,
           MESH_OT_edge_slide2]
