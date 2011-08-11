# -*- coding: utf-8 -*-

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Updates by AlexV #
# Updates by Meta-Androcto #

bl_info = {
    "name": "Fake Knife",
    "author": "Chromoly",
    "version": (0, 4),
    "blender": (2, 5, 9),
    "api": 39104,
    "location": "Editmode specials menu",
    "description": "Interactive Knife Tool.",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/Modeling/Fake_Knife",
    "tracker_url": "http://projects.blender.org/tracker/index.php?"\
        "func=detail&aid=28209",
    "category": "Mesh"}
'''
'snap_cursor_to_element.patch'?????????????????
'''


import time
import math
import bpy
from bpy.props import *
from mathutils import Vector
import bgl

'''from va.math import is_nan
from va.view import convert_window_to_world, convert_world_to_window, \
                    snap_to_grid, get_DPBU_dx_unit_pow, \
                    find_nearest_element_from_mouse
from va.gl import draw_box, draw_circle
'''


### Redraw Rate ####
redraw_rate = 0.01
####################

color_cross = [1.0, 1.0, 1.0, 0.7]
color_line = [1.0, 1.0, 0.0, 1.0]
color_snap_vert = [1.0, 1.0, 1.0, 1.0]
cross_size = 20
cross_ofs = 30


### copy from va ##############################################################
GRID_MIN_PX = 6.0

def is_nan(f):
    return not f == f


def convert_world_to_window(vec, persmat, sx, sy):
    '''
    vec: sequence
    return Vector
    '''
    #v = vec.to_4d()
    v = Vector([vec[0], vec[1], vec[2], 1.0])
    v = persmat * v
    if v[3] != 0.0:
        v /= v[3]
    x = sx / 2 + v[0] * sx / 2
    y = sy / 2 + v[1] * sy / 2
    return Vector([x, y, v[2]])


def convert_window_to_world(vec, persmat, sx, sy):
    '''
    vec: sequence
    return Vector
    '''
    invpmat = persmat.copy()
    invpmat.invert()
    v1 = Vector([float(vec[0]) * 2 / sx, float(vec[1]) * 2 / sy, vec[2]])
    v2 = v1 - Vector([1., 1., 0.])
    v2.resize_4d()
    v3 = invpmat * v2
    if v3[3] != 0.0:
        v3 /= v3[3]
    v3.resize_3d()
    return v3

def get_DPBU_dx_unit_pow(region):
    '''????p??????BlenderUnit?????????????q?
    ????window?????(p,q???world??)
    '''
    sx = region.width
    sy = region.height
    rv3d = region.region_data
    persmat = rv3d.perspective_matrix
    viewmat = rv3d.view_matrix
    viewinvmat = viewmat.inverted()
    viewloc = rv3d.view_location

    p = viewloc
    if sx >= sy:
        q = viewloc + Vector(viewinvmat[0][:3])
    else:
        q = viewloc + Vector(viewinvmat[1][:3])
    dp = convert_world_to_window(p, persmat, sx, sy)
    dq = convert_world_to_window(q, persmat, sx, sy)
    l = math.sqrt((dp[0] - dq[0]) ** 2 + (dp[1] - dq[1]) ** 2)
    dot_per_blender_unit = dx = l

    #unit = 1.0
    unit_pow = 0
    if dx < GRID_MIN_PX:
        while dx < GRID_MIN_PX:
            dx *= 10
            unit_pow += 1
    else:
        while dx > GRID_MIN_PX * 10:
            dx /= 10
            unit_pow -= 1
    return dot_per_blender_unit, dx, unit_pow


def snap_to_grid(vec, grid_distance,
                 local_grid_origin=None, local_grid_rotation=None):
    local_grid = True if local_grid_rotation and local_grid_origin else False
    if local_grid:
        mat = local_grid_rotation.to_matrix().to_4x4()
        for i in range(3):
            mat[3][i] = local_grid_origin[i]
        imat = mat.inverted()
        vec = vec * imat
    else:
        vec = vec.copy()
    for i in range(3):
        vec[i] = grid_distance * math.floor(0.5 + vec[i] / grid_distance)
    if local_grid:
        vec = vec * mat
    return vec


def find_nearest_element_from_mouse(context, type='VERTEX', mode='ALL_EMALL'):
    v3d = context.space_data
    cursor = v3d.cursor_location.copy()
    v3d.cursor_location = [float('nan') for i in range(3)]
    bpy.ops.view3d.snap_cursor_to_element('INVOKE_REGION_WIN',
        type=type, use_mouse_cursor=True, mode=mode, redraw=False)
    if not is_nan(v3d.cursor_location[0]):
        vec = v3d.cursor_location.copy()
    else:
        vec = None
    v3d.cursor_location = cursor
    return vec


def draw_box(xmin, ymin, w, h, poly=False):
    bgl.glBegin(bgl.GL_QUADS if poly else bgl.GL_LINE_LOOP)
    bgl.glVertex2f(xmin, ymin)
    bgl.glVertex2f(xmin + w, ymin)
    bgl.glVertex2f(xmin + w, ymin + h)
    bgl.glVertex2f(xmin, ymin + h)
    bgl.glEnd()


def draw_circle(x, y, radius, subdivide, poly=False):
    r = 0.0
    dr = math.pi * 2 / subdivide
    if poly:
        subdivide += 1
        bgl.glBegin(bgl.GL_TRIANGLE_FAN)
        bgl.glVertex2f(x, y)
    else:
        bgl.glBegin(bgl.GL_LINE_LOOP)
    for i in range(subdivide):
        bgl.glVertex2f(x + radius * math.cos(r), y + radius * math.sin(r))
        r += dr
    bgl.glEnd()
### copy end ##################################################################
# ??????????(???)????!


def draw_lines(self, context):
    region = bpy.context.region
    sx, sy = region.width, region.height
    persmat = context.region_data.perspective_matrix

    vertices = self.vertices
    mouseco = self.mouseco
    current_vec = self.current_vec  # ????
    vec_snap_vert = self.vec_snap_vert  # ?????

    bgl.glLineWidth(1)
    bgl.glEnable(bgl.GL_BLEND)

    # cursor cross
    bgl.glColor4f(*color_cross)
    bgl.glBegin(bgl.GL_LINES)
    bgl.glVertex2f(mouseco[0] + cross_ofs, mouseco[1])  # right
    bgl.glVertex2f(mouseco[0] + cross_ofs + cross_size, mouseco[1])
    bgl.glVertex2f(mouseco[0] - cross_ofs, mouseco[1])  # left
    bgl.glVertex2f(mouseco[0] - cross_ofs - cross_size, mouseco[1])
    bgl.glVertex2f(mouseco[0], mouseco[1] + cross_ofs)  # top
    bgl.glVertex2f(mouseco[0], mouseco[1] + cross_ofs + cross_size)
    bgl.glVertex2f(mouseco[0], mouseco[1] - cross_ofs)  # bottom
    bgl.glVertex2f(mouseco[0], mouseco[1] - cross_ofs - cross_size)
    bgl.glEnd()

    vec = convert_world_to_window(current_vec, persmat, sx, sy)
    # snap circle
    if self.snap_type:
        if self.snap_type == 'grid':
            bgl.glColor4f(*color_snap_vert)
            draw_box(vec[0] - 5, vec[1] - 5, 10, 10)
        else:
            bgl.glColor4f(*color_snap_vert)
            v2d = convert_world_to_window(vec_snap_vert, persmat, sx, sy)
            draw_circle(v2d[0], v2d[1], 6, 16)

    if vertices:
        # split line
        bgl.glColor4f(*color_line)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for v in vertices:
            v2d = convert_world_to_window(v, persmat, sx, sy)
            bgl.glVertex2f(v2d[0], v2d[1])
        bgl.glVertex2f(vec[0], vec[1])
        bgl.glEnd()

    ## restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


# *** Main Operator *** #
class MESH_OT_fake_knife(bpy.types.Operator):
    bl_label = 'Fake Knife'
    bl_idname = 'mesh.fake_knife'
    bl_description = 'Line knife'
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}

    type = EnumProperty(items=(('EXACT', 'Exact', ''),
                               ('MIDPOINTS', 'Midpoints', ''),
                               ('MULTICUT', 'Multicut', '')),
                        name='type',
                        default='EXACT')
    num_cuts = IntProperty(name='Number of Cuts',
                           description='Only for Multi-Cut',
                           default=1)
    cursor = IntProperty(name='Cursor', default=9)

    count = IntProperty(name='Path Count', default=0, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return {context.active_object.mode == 'EDIT'}
        else:
            return {False}

    def execute(self, context):
        region = bpy.context.region
        sx, sy = region.width, region.height
        persmat = context.region_data.perspective_matrix
        vertices = self.vertices

        if len(vertices) <= 1:
            return {'FINISHED'}

        cutpath = []
        for i, v in enumerate(vertices):
            v2d = convert_world_to_window(v, persmat, sx, sy)
            loc = (v2d[0], v2d[1])
            cutpath.append({'name': 'tmp', 'time': i / 10, 'loc': loc})
        bpy.ops.mesh.knife_cut(type=self.type, path=cutpath, \
                               num_cuts=self.num_cuts, \
                               cursor=self.cursor)  # , num_lines=0)
        return {'FINISHED'}

    def copy_persp_vec_value(self, context, v1, v2, index):
        # copy vector value by window coordinate
        # v1_winco[index] = v2_winco[index]
        region = context.region
        sx, sy = region.width, region.height
        rv3d = context.region_data
        persmat = rv3d.perspective_matrix
        v1_winco = convert_world_to_window(v1, persmat, sx, sy)
        v2_winco = convert_world_to_window(v2, persmat, sx, sy)
        v1_winco[index] = v2_winco[index]
        v = convert_window_to_world(v1_winco, persmat, sx, sy)
        return v

    def calc_align_to_axis(self, context, current_vec):
        if self.along == 0:  # lock Y
            current_vec = self.copy_persp_vec_value(context,
                               current_vec, self.vertices[-1], 1)
        elif self.along == 1:  # lock X
            current_vec = self.copy_persp_vec_value(context,
                               current_vec, self.vertices[-1], 0)
        return current_vec

    def calc_basic(self, context, rv3d, sx, sy, persmat, mouseco):
        current_vec = convert_window_to_world(mouseco, persmat, sx, sy)
        if self.vertices:
            current_vec = self.copy_persp_vec_value(context, current_vec,
                                                    self.vertices[-1], 2)
        else:
            current_vec = self.copy_persp_vec_value(context, current_vec,
                                                    rv3d.view_location, 2)
        # Align Axis
        self.current_vec = self.calc_align_to_axis(context, current_vec)

    def calc_snap_to_grid(self, context, event):
        # Snap to Grid
        # /10???snap_cursor_to_grid??????
        v3d = context.space_data
        current_vec = self.current_vec
        if hasattr(v3d, 'use_local_grid') and v3d.use_local_grid:
            orig = v3d.local_grid_origin
            quat = v3d.local_grid_rotation
        else:
            orig = quat = None
        dpbu, dx, unit_pow = get_DPBU_dx_unit_pow(context.region)
        grid_distance = 10 ** unit_pow
        if event.shift and event.alt:
            grid_distance = grid_distance / 10
        snap_vec = snap_to_grid(current_vec, grid_distance,
                                orig, quat)
        if self.along == 0:
            current_vec = self.copy_persp_vec_value(context,
                               current_vec, snap_vec, 0)
        elif self.along == 1:
            current_vec = self.copy_persp_vec_value(context,
                               current_vec, snap_vec, 1)
        else:
            current_vec = snap_vec
        self.snap_type = 'grid'
        self.current_vec = current_vec
        return current_vec

    def calc_snap_to_vert(self, context):
        # Snap to Vertex
        snap_vec = find_nearest_element_from_mouse(context, type='VERTEX')
        if snap_vec:
            if self.along == 0:  # copy Y
                current_vec = self.copy_persp_vec_value(context,
                               snap_vec, self.vertices[-1], 1)
            elif self.along == 1:
                current_vec = self.copy_persp_vec_value(context,
                               snap_vec, self.vertices[-1], 0)
            else:
                current_vec = snap_vec.copy()
            self.vec_snap_vert = snap_vec.copy()
            self.snap_type = 'vertex'
            self.current_vec = current_vec
        else:
            self.snap_type = ''

    def modal(self, context, event):
        region = bpy.context.region
        sx, sy = region.width, region.height
        v3d = context.space_data
        rv3d = context.region_data
        persmat = rv3d.perspective_matrix
        mouseco = Vector((event.mouse_region_x, event.mouse_region_y, 0))
        self.mouseco = mouseco.copy()
        vertices = self.vertices

        do_redraw = False

        if time.time() - self.time >= redraw_rate:
            self.time = time.time()
            if event.type == 'MOUSEMOVE':
                ### ????????
                self.calc_basic(context, rv3d, sx, sy, persmat, mouseco)
                if event.ctrl:
                    if event.shift or event.alt:
                        ### Snap Grid
                        self.calc_snap_to_grid(context, event)
                    else:
                        ### Snap Vert
                        pass #self.calc_snap_to_vert(context)
                else:
                    self.snap_type = ''
                do_redraw = True
        else:
            # calc_snap_to_vert???????????????
            if not (event.ctrl and not (event.shift or event.alt)):
                self.calc_basic(context, rv3d, sx, sy, persmat, mouseco)
                if event.ctrl:
                    self.calc_snap_to_grid(context, event)
                do_redraw = True

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.time = time.time()
            self.calc_basic(context, rv3d, sx, sy, persmat, mouseco)
            if event.ctrl:
                if event.shift or event.alt:
                    self.calc_snap_to_grid(context, event)
                else:
                    pass #self.calc_snap_to_vert(context)
            do_redraw = True
            vertices.append(self.current_vec)
            self.along = -1
        elif event.type == 'MIDDLEMOUSE' and event.value == 'PRESS':
            if event.shift:
                return {'PASS_THROUGH'}
            else:
                if self.along == -1 and vertices:
                    v = convert_world_to_window(vertices[-1], persmat, sx, sy)
                    relative = mouseco - v
                    if abs(relative[0]) >= abs(relative[1]):
                        self.along = 0
                    else:
                        self.along = 1
                else:
                    self.along = -1
                do_redraw = True
        elif event.type in ('WHEELUPMOUSE', 'WHEELDOWNMOUSE'):
            return {'PASS_THROUGH'}
        elif event.type in ('ENTER', 'RET', 'SPACE'):
            context.region.callback_remove(self._handle)
            context.area.tag_redraw()
            self.execute(context)
            return {'FINISHED'}
        elif event.type in ('RIGHTMOUSE', 'ESC'):
            context.region.callback_remove(self._handle)
            context.area.tag_redraw()
            return {'CANCELLED'}

        if do_redraw:
            context.area.tag_redraw()

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        active_space = context.space_data
        if active_space.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            self._handle = context.region.callback_add(draw_lines,\
                                                 (self, context), 'POST_PIXEL')
            self.vertices = []
            mouseco = Vector((event.mouse_region_x, event.mouse_region_y, 0))
            self.mouseco = mouseco
            self.current_vec = mouseco.copy()
            self.along = -1
            self.snap_type = ''
            self.vec_snap_vert = None
            context.area.tag_redraw()
            self.time = time.time()
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}


def menu_func(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator(MESH_OT_fake_knife.bl_idname, text="Fake Knife")

# Register
def register():
    bpy.utils.register_module(__name__)

    bpy.types.VIEW3D_MT_edit_mesh_specials.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)


if __name__ == '__main__':
    register()
