# -*- coding: utf-8 -*-

# GPL LICENSE

import math

import bpy
from bpy.props import *
import mathutils as Math
from mathutils import Matrix, Vector, Quaternion
import geometry as Geo

import mesh_vertex_align_25.va
from mesh_vertex_align_25.va import *

LOOSE = 1
SEAM  = 1 << 1
SHARP = 1 << 2

class Vert():
    def __init__(self):
        self.i = 0  # index
        self.s = 0  # selecte
        self.h = 0  # hide
        self.n = Vector()  # normal
        self.co = Vector()
        self.vertices = []
        self.edges = []
        self.faces = []
        self.f1 = 0
        self.f2 = 0

    def sel(self):
        return self.s and not self.h

class Edge():
    def __init__(self):
        self.i = 0
        self.s = 0
        self.h = 0
        # self.l = 0 # loose
        # self.seam = 0 # seam
        # self.sharp = 0 # sharp
        self.f = 0  # LOOSE, SEAM, SHARP
        self.key = []  # [int, int]
        self.vertices = []
        self.faces = []
        self.f1 = 0
        self.f2 = 0

    def sel(self):
        return self.s and not self.h

    def vert_another(self, v):
        if v in self.vertices:
            return self.vertices[self.vertices.index(v) - 1]
        else:
            return None

class Face():
    def __init__(self):
        self.i = 0
        self.s = 0
        self.h = 0
        self.m = 0  # material_index
        self.a = 0.0  # area
        self.n = Vector()  # normal
        self.c = Vector()  # center
        self.keys = []  # edge_keys (int)
        self.vertices = []
        self.edges = []
        self.f1 = 0
        self.f2 = 0

    def sel(self):
        return self.s and not self.h

    def vertices_other(self, vertices, force=False):
        ret_vertices = self.vertices[:]
        if force:
            for v in vertices:
                try:
                    ret_vertices.remove(v)
                except:
                    pass
        else:
            for v in vertices:
                try:
                    ret_vertices.remove(v)
                except:
                    return None
        return ret_vertices


class PyMesh():
    def __init__(self, me, ob=False):
        kedict = key_edge_dict(me, sel=-1)

        vertices = [Vert() for i in range(len(me.vertices))]
        for i, v in enumerate(me.vertices):
            vert = vertices[i]
            vert.i = v.index
            vert.s = int(v.select)
            vert.h = int(v.hide)
            vert.n = v.normal.copy()
            vert.co = v.co.copy()
            # vert.edges = []
            # vert.faces = []

            vert.f1 = vert.f2 = 0

        edges = [Edge() for i in range(len(me.edges))]
        for i, e in enumerate(me.edges):
            edge = edges[i]
            edge.i = e.index
            edge.s = int(e.select)
            edge.h = int(e.hide)
            edge.f = int(e.is_loose) * LOOSE | int(e.use_seam) * SEAM | \
                     int(e.use_edge_sharp) * SHARP
            edge.key = list(e.key)
            edge.vertices = [vertices[i] for i in e.vertices]
            # edge.faces = []

            edge.f1 = edge.f2 = 0


        faces = [Face() for i in range(len(me.faces))]
        for i, f in enumerate(me.faces):
            face = faces[i]
            face.i = f.index
            face.s = int(f.select)
            face.h = int(f.hide)
            face.m = f.material_index
            face.a = f.area
            face.n = f.normal.copy()
            face.c = f.center.copy()
            face.keys = list(f.edge_keys)
            face.vertices = [vertices[i] for i in f.vertices]
            face.edges = [edges[kedict[key]] for key in f.edge_keys]

            face.f1 = face.f2 = 0

        for f in faces:
            for v in f.vertices:
                v.faces.append(f)
            for key in f.keys:
                edges[kedict[key]].faces.append(f)
        for e in edges:
            for v in e.vertices:
                v.edges.append(e)

        for v in vertices:
            for e in v.edges:
                v.vertices.append(e.vert_another(v))

        self.vertices = vertices
        self.edges = edges
        self.faces = faces


        for key in kedict.keys():
            kedict[key] = edges[kedict[key]]
        self.key_edge = kedict

# ******************************************************************************
# *** View ****
# ******************************************************************************
def check_view(quat, localgrid_quat):
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

def get_viewmat_and_viewname(context):
    # viewmat not has location

    '''
    viewmat <- invert() -> emptymat
    1.world-coordinate: me.transform(ob.matrix)
    2a.empty-base-coordinate: me.transform(viewmat)
    2b.empty-base-coordinate: me.transform(emptymat.invert())
    2Dvecs = [v.co.copy().resize2D() for v in me.vertices]
    '''

    '''
    # 蛇使い
    view_mat = context.space_data.region_3d.perspective_matrix # view matrix
    ob_mat = context.active_object.matrix # object world space matrix
    total_mat = view_mat*ob_mat # combination of both matrices

    loc = v.co.copy().resize4D() # location vector resized to 4 dimensions
    vec = total_mat*loc # multiply vector with matrix
    vec = mathutils.Vector((vec[0]/vec[3],vec[1]/vec[3],vec[2]/vec[3])) # dehomogenise vector

    # result (after scaling to viewport)
    x = int(mid_x + vec[0]*width/2.0)
    y = int(mid_y + vec[1]*height/2.0)
    #mid_x and mid_y are the center points of the viewport, width and height are the sizes of the viewport.
    '''

    scn = context.scene
    ob = context.active_object
    ob_selected = ob.select

    # add empty object
    l = [True for i in range(32)]
    bpy.ops.object.add(type='EMPTY', view_align=True,
                       location = (0,0,0), layer=l)  # 原点
    ob_empty = context.active_object

    # check localgrid
    space3dview = context.space_data  # Space3DView
    try:
        localgrid = space3dview.localgrid
    except:
        localgrid = False
    if localgrid:
        localgrid_quat = space3dview.localgrid_quat
        localgrid_orig = space3dview.localgrid_orig
    else:
        localgrid_quat = localgrid_orig = None

    # check view
    mat = ob_empty.matrix_world.rotation_part().transpose()
    quat = mat.to_quat()
    view = check_view(quat, localgrid_quat)

    # cleanup
    scn.objects.unlink(ob_empty)
    scn.objects.active = ob
    ob.select = ob_selected
    scn.update()

    return mat, view

# ******************************************************************************
# *** Print ****
# ******************************************************************************
def print_mat(label, matrix, column=8):
    print(label)
    if len(matrix) == 2:
        txt = 'row{0} [{1:>{5}.{6}f}, {2:>{5}.{6}f}]'
        for cnt, row in enumerate(matrix):
            print(txt.format(cnt, row[0], row[1], 0, 0, column + 3, column))
    elif len(matrix) == 3:
        txt = 'row{0} [{1:>{5}.{6}f}, {2:>{5}.{6}f}, {3:>{5}.{6}f}]'
        for cnt, row in enumerate(matrix):
            print(txt.format(cnt, row[0], row[1], row[2], 0, column + 3, column))
    elif len(matrix) == 4:
        txt = 'row{0} [{1:>{5}.{6}f}, {2:>{5}.{6}f}, {3:>{5}.{6}f}, {4:>{5}.{6}f}]'
        for cnt, row in enumerate(matrix):
            print(txt.format(cnt, row[0], row[1], row[2], row[3], column + 3, column))
