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

# <pep8 compliant>

bl_info = {
    "name": "Vertex slide",
    "author": "Valter Battioli (ValterVB) and PKHG",
    "version": (1, 1, 0),
    "blender": (2, 5, 9),
    "api": 39094,
    "location": "View3D > Mesh > Vertices (CTRL V-key) or search for 'VB Vertex 2'",
    "description": "Slide a vertex along an edge",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Modeling/Vertex_Slide2",
    "tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=27561",
    "category": "Mesh"}

#***********************************************************************
#ver. 1.0.0: -First version
#ver. 1.0.1: -Now the mouse wheel select in continuos mode the next vertex
#            -Add a marker for the vertex to move
#ver. 1.0.2: -Add check for vertices not selected
#            -Some cleanup
#ver. 1.0.3: -Now the movement is proportional to the mouse movement
#             1/10 of the distance between 2 points for every pixel
#             mouse movement (1/100 with SHIFT)
#ver. 1.0.4: all coordinate as far as possible replaced by vectors
#            view3d_utils are used to define length of an edge on screen!
#            partial simplified logic by PKHG
#ver. 1.0.6: Restore continuous slide, code cleanup
#            Correct the crash with not linked vertex
#ver. 1.0.7: Restore shift, and some code cleanup
#ver. 1.0.8: Restore 2 type of sliding with 2 vertex selected
#ver. 1.0.9: Fix for reverse vector multiplication
#ver. 1.1.0: Delete debug info, some cleanup and add some comments
#***********************************************************************

import bpy
import bgl
import blf
from mathutils import Vector
from bpy_extras import view3d_utils

###global
direction = 1.0
mouseVec = None
ActiveVertex = None


#  This class store Vertex data
class Point():
    class Vertices():
        def __init__(self):
            self.co = Vector((0, 0, 0))
            self.idx = -1

    def __init__(self):
        self.original = self.Vertices()
        self.new = self.Vertices()
        self.t = 0
        self.selected = False


# Equation of the line
# Changing t, I have a new point coordinate on the line along v0 v1
# With t from 0 to 1  I move from v0 to v1
def NewCoordinate(v0, v1, t):
    return v0 + t * (v1 - v0)

# Draw an asterisk near the vertex that I move
def draw_callback_px(self, context):
    # Get screen information
    mid_x = context.region.width / 2.0
    mid_y = context.region.height / 2.0
    width = context.region.width
    height = context.region.height

    # Get matrices
    view_mat = context.space_data.region_3d.perspective_matrix
    ob_mat = context.active_object.matrix_world
    total_mat = view_mat * ob_mat

    Vertices = bpy.context.object.data.vertices
    temp = Vertices[ActiveVertex].co

    loc = Vertices[ActiveVertex].co.to_4d()  # Where I want draw the text

    vec = total_mat * loc
    if vec[3] != 0:
        vec = vec / vec[3]
    else:
        vec = vec
    x = int(mid_x + vec[0] * width / 2.0)
    y = int(mid_y + vec[1] * height / 2.0)

    # Draw an * at the active vertex
    blf.position(0, x, y, 0)
    blf.size(0, 26, 72)
    blf.draw(0, "*")


class VertexSlideOperator(bpy.types.Operator):
    bl_idname = "vertex.slide"
    bl_label = "VB Vertex Slide 2"  # PKHG easy to searc for ;-)

    Vert1 = Point()  # Original selected vertex data
    Vert2 = Point()  # Second selected vertex data
    LinkedVerts = []  # List of linked vertex to Vert1
    VertLinkedIdx = 0  # Index of the linked vertex selected
    temp_mouse_x = 0
    tmpMouse = Vector((0, 0))

    first_vertex_move = True
    left_alt_press = False
    left_shift_press = False

    #Compute the screendistance of two vertices PKHG
    def denominator(self, vertex_zero_co, vertex_one_co):
        global denom
        matw = bpy.context.active_object.matrix_world
        V0 = matw * vertex_zero_co
        res0 = view3d_utils.location_3d_to_region_2d(bpy.context.region, bpy.context.space_data.region_3d, V0)
        V1 = matw * vertex_one_co
        res1 = view3d_utils.location_3d_to_region_2d(bpy.context.region, bpy.context.space_data.region_3d, V1)
        result = (res0 - res1).length
        denom = result
        return result

    def modal(self, context, event):
        global ActiveVertex, mouseVec, direction
        context.area.tag_redraw()
        if event.type == 'MOUSEMOVE':
            Vertices = bpy.context.object.data.vertices
            bpy.ops.object.mode_set(mode='OBJECT')
            if self.Vert2.original.idx != -1:  # Starting with 2 vertex selected
                denom = self.denominator(self.Vert1.original.co, self.Vert2.original.co)
                tmpMouse = Vector((event.mouse_x, event.mouse_y))
                t_diff = (tmpMouse - self.tmpMouse).length
                self.tmpMouse = tmpMouse
                td = t_diff * direction / denom
                mouseDir = "right"
                if event.mouse_x < self.temp_mouse_x:
                    mouseDir = "left"
                    td = -td
                if self.first_vertex_move:
                    self.Vert1.t = self.Vert1.t + td
                    Vertices[self.Vert1.original.idx].co = NewCoordinate(self.Vert1.original.co, self.Vert2.original.co, self.Vert1.t)
                    Vertices[self.Vert2.original.idx].co = NewCoordinate(self.Vert2.original.co, self.Vert1.original.co, self.Vert2.t)
                else:
                    self.Vert2.t = self.Vert2.t + td
                    Vertices[self.Vert1.original.idx].co = NewCoordinate(self.Vert1.original.co, self.Vert2.original.co, self.Vert1.t)
                    Vertices[self.Vert2.original.idx].co = NewCoordinate(self.Vert2.original.co, self.Vert1.original.co, self.Vert2.t)
            else:  # Starting with 1 vertex selected
                denom = self.denominator(self.Vert1.original.co, self.LinkedVerts[self.VertLinkedIdx].original.co)
                tmpMouse = Vector((event.mouse_x, event.mouse_y))
                t_diff = (tmpMouse - self.tmpMouse).length
                self.tmpMouse = tmpMouse
                td = t_diff * direction / denom
                mouseDir = "right"
                if event.mouse_x < self.temp_mouse_x:
                    mouseDir = "left"
                    td = -td
                if self.left_alt_press:  # Continuous slide (Starting from last position, not from original position)
                    self.Vert2.t = self.Vert2.t + td
                    Vertices[self.Vert1.original.idx].co = NewCoordinate(self.Vert2.original.co, self.LinkedVerts[self.VertLinkedIdx].original.co, self.Vert2.t)
                    ActiveVertex = self.Vert1.original.idx
                else:
                    self.LinkedVerts[self.VertLinkedIdx].t = self.LinkedVerts[self.VertLinkedIdx].t + td
                    Vertices[self.Vert1.original.idx].co = NewCoordinate(self.Vert1.original.co, self.LinkedVerts[self.VertLinkedIdx].original.co, self.LinkedVerts[self.VertLinkedIdx].t)
                    ActiveVertex = self.Vert1.original.idx
            self.temp_mouse_x = event.mouse_x
            bpy.ops.object.mode_set(mode='EDIT')

        elif event.type == 'LEFT_ALT':  # Hold ALT to use continuous slide
            self.left_alt_press = not self.left_alt_press
            if self.left_alt_press and self.Vert2.original.idx == -1:
                vert = bpy.context.object.data.vertices[self.Vert1.original.idx]
                self.Vert2.original.co = Vector((vert.co.x, vert.co.y, vert.co.z))
                self.Vert2.t = 0

        elif event.type == 'LEFT_SHIFT':  # Hold left SHIFT to slide lower
            self.left_shift_press = not self.left_shift_press
            if self.left_shift_press:
                direction *= 0.1
            else:
                if direction < 0:
                    direction = -1
                else:
                    direction = 1

        elif event.type == 'WHEELDOWNMOUSE':  # Change the vertex to be moved
            if self.Vert2.original.idx == -1:
                if self.left_alt_press:
                    vert = bpy.context.object.data.vertices[self.Vert1.original.idx]
                    self.Vert2.original.co = Vector((vert.co.x, vert.co.y, vert.co.z))
                    self.Vert2.t = 0
                self.VertLinkedIdx = self.VertLinkedIdx + 1
                if self.VertLinkedIdx > len(self.LinkedVerts) - 1:
                    self.VertLinkedIdx = 0
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.context.object.data.vertices[self.Vert1.original.idx].select = True
                bpy.context.object.data.vertices[self.LinkedVerts[self.VertLinkedIdx].original.idx].select = True
                bpy.ops.object.mode_set(mode='EDIT')
            else:
                self.first_vertex_move = not self.first_vertex_move
                if self.left_alt_press == False:
                    self.Vert1.t = 0
                    self.Vert2.t = 0
                    if self.first_vertex_move:
                        ActiveVertex = self.Vert1.original.idx
                    else:
                        ActiveVertex = self.Vert2.original.idx
                else:
                    if self.first_vertex_move:
                        ActiveVertex = self.Vert1.original.idx
                    else:
                        ActiveVertex = self.Vert2.original.idx

        elif event.type == 'WHEELUPMOUSE':  # Change the vertex to be moved
            if self.Vert2.original.idx == -1:
                if self.left_alt_press:
                    vert = bpy.context.object.data.vertices[self.Vert1.original.idx]
                    self.Vert2.original.co = Vector((vert.co.x, vert.co.y, vert.co.z))
                    self.Vert2.t = 0
                self.VertLinkedIdx = self.VertLinkedIdx - 1
                if self.VertLinkedIdx < 0:
                    self.VertLinkedIdx = len(self.LinkedVerts) - 1
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.context.object.data.vertices[self.Vert1.original.idx].select = True
                bpy.context.object.data.vertices[self.LinkedVerts[self.VertLinkedIdx].original.idx].select = True
                bpy.ops.object.mode_set(mode='EDIT')
            else:
                self.first_vertex_move = not self.first_vertex_move
                if self.left_alt_press == False:
                    self.Vert1.t = 0
                    self.Vert2.t = 0
                    if self.first_vertex_move:
                        ActiveVertex = self.Vert1.original.idx
                    else:
                        ActiveVertex = self.Vert2.original.idx
                else:
                    if self.first_vertex_move:
                        ActiveVertex = self.Vert1.original.idx
                    else:
                        ActiveVertex = self.Vert2.original.idx

        elif event.type == 'NUMPAD_PLUS':  # Change direction
            if direction < 0.0:
                direction = - direction

        elif event.type == 'NUMPAD_MINUS':  # Change direction
            if direction > 0.0:
                direction = - direction

        elif event.type == 'LEFTMOUSE':  #Confirm and exit
            Vertices = bpy.context.object.data.vertices
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            Vertices[self.Vert1.original.idx].select = True
            bpy.ops.object.mode_set(mode='EDIT')
            context.region.callback_remove(self._handle)
            return {'FINISHED'}

        elif event.type in ('RIGHTMOUSE', 'ESC'):  # Exit without change
            Vertices = bpy.context.object.data.vertices
            bpy.ops.object.mode_set(mode='OBJECT')
            Vertices[self.Vert1.original.idx].co = self.Vert1.original.co
            if self.Vert2.original.idx != -1:
                Vertices[self.Vert2.original.idx].co = self.Vert2.original.co
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                Vertices[self.Vert1.original.idx].select = True
                Vertices[self.Vert2.original.idx].select = True
                bpy.ops.object.mode_set(mode='EDIT')
            else:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                Vertices[self.Vert1.original.idx].select = True
                bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.mode_set(mode='EDIT')
            context.region.callback_remove(self._handle)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        global mouseVec, direction
        direction = 1.0
        if context.active_object == None or context.active_object.type != "MESH":
            print("Not any active object or not an mesh object:")
            self.report({'WARNING'}, "Not any active object or not an mesh object:")
            return {'CANCELLED'}
        else:
            mouse_start_x = event.mouse_x
            mouse_start_y = event.mouse_y
            mouseVec = Vector((mouse_start_x, mouse_start_y))

            obj = bpy.context.object
            Selected = False
            bpy.ops.object.mode_set(mode='OBJECT')
            count = 0
            selected_vertices = []
            for vert in obj.data.vertices:
                if vert.select:
                    Selected = True
                    selected_vertices.append(vert.index)
                    count += 1
                    if (count > 2):  # more than 2 vertex selected
                        Selected = False
                        break

            if Selected == False:
                self.report({'WARNING'}, "0 or more then 2 vertices selected, could not start")
                bpy.ops.object.mode_set(mode='EDIT')
                return {'CANCELLED'}
            else:
                bpy.ops.object.mode_set(mode='EDIT')
                global ActiveVertex
                self.Vert1 = Point()
                self.Vert2 = Point()
                self.LinkedVerts = []
                obj = bpy.context.object
                bpy.ops.object.mode_set(mode='OBJECT')
                self.Vert1.original.idx = selected_vertices[0]
                self.Vert1.original.co = obj.data.vertices[selected_vertices[0]].co.copy()
                self.Vert1.new = self.Vert1.original
                if len(selected_vertices) == 2:
                    self.Vert2.original.idx = selected_vertices[1]
                    self.Vert2.original.co = obj.data.vertices[selected_vertices[1]].co.copy()
                    self.Vert2.new = self.Vert2.original
                ActiveVertex = self.Vert1.original.idx
                bpy.ops.object.mode_set(mode='EDIT')
                if self.Vert2.original.idx == -1:
                    self.Vert = []
                    bpy.ops.mesh.select_more()  # Select the linked vertices; PKHG: fine knoff hoff used!
                    bpy.ops.object.mode_set(mode='OBJECT')
                    for vert in obj.data.vertices:
                        if vert.select:
                            if vert.index != self.Vert1.original.idx:
                                self.LinkedVerts.append(Point())
                                self.LinkedVerts[-1].original.idx = vert.index
                                self.LinkedVerts[-1].original.co = vert.co.copy()
                                self.LinkedVerts[-1].new = self.LinkedVerts[-1].original
                    if len(self.LinkedVerts) > 0:  # Check for isolated vertex
                        self.VertLinkedIdx = 0
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_all(action='DESELECT')
                        bpy.ops.object.mode_set(mode='OBJECT')
                        obj.data.vertices[self.Vert1.original.idx].select = True  # Select the original vertex
                        obj.data.vertices[self.LinkedVerts[0].original.idx].select = True  # Select the first linked vertex
                        bpy.ops.object.mode_set(mode='EDIT')
                    else:
                        bpy.ops.object.mode_set(mode='EDIT')
                        self.report({'WARNING'}, "Isolated vertex or wrong Select Mode!")
                        return {'CANCELLED'}
                context.window_manager.modal_handler_add(self)
                # Add the region OpenGL drawing callback
                # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
                self._handle = context.region.callback_add(draw_callback_px, (self, context), 'POST_PIXEL')
                self.temp_mouse_x = event.mouse_x
                self.tmpMouse[0], self.tmpMouse[1] = (event.mouse_x, event.mouse_y)
                return {'RUNNING_MODAL'}


def menu_func(self, context):
    self.layout.operator_context = "INVOKE_DEFAULT"
    self.layout.operator(VertexSlideOperator.bl_idname, text="Vertex Slide")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.prepend(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(menu_func)


if __name__ == "__main__":
    register()
