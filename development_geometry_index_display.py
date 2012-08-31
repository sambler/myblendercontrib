#Simplified BSD License
#
#Copyright (c) 2012, Florian Meyer
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met: 
#
#1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer. 
#2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution. 
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#################################################################
bl_info = {
    "name": "Geometry Index Display",
    "author": "tstscr",
    "version": (1, 0),
    "blender": (2, 6, 3),
    "location": "View3D > Properties Panel",
    "description": "Display of mesh indicies (Verts, Edges, Faces)",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Development/Geometry_Index_Display",
    "tracker_url": "http://projects.blender.org/tracker/?func=detail&aid=32425",
    "category": "Development"}
###########################################################################
import bpy, bgl, blf, bmesh
from bpy.types import Operator, Menu, Panel, PropertyGroup, PointerProperty
from bpy_extras.view3d_utils import location_3d_to_region_2d
from bpy.props import *#BoolProperty, IntProperty
###########################################################################
def get_edge_coordinate(self, context, obj, edge):
    v0 = edge.link_loops[0].vert
    v1 = edge.link_loops[0].link_loop_next.vert
    center= (v0.co + v1.co) * 0.5
    co = location_3d_to_region_2d(context.region,
                                  context.space_data.region_3d,
                                  obj.matrix_world * center)
    return co

def get_data(self, context, options):
    vert_data = []
    edge_data = []
    face_data = []
    
    if context.mode != 'EDIT_MESH':
        return 
    obj = context.active_object
    me = obj.data
    mesh = bmesh.from_edit_mesh(me)

    #Vertex Indicies
    if options.show_vertex_indicies:
        vertices = mesh.verts
        for vert in vertices:
            if options.show_selected and not vert.select:
                continue
            co = location_3d_to_region_2d(context.region,
                                          context.space_data.region_3d,
                                          obj.matrix_world * vert.co)
            idx = vert.index
            vert_data.append((idx, co))
    
    #Edge Indicies
    if options.show_edge_indicies:
        edges = mesh.edges
        for edge in edges:
            if options.show_selected and not edge.select:
                continue
            co = get_edge_coordinate(self, context, obj, edge)
            idx = edge.index
            edge_data.append((idx, co))

    #Face Indicies
    if options.show_face_indicies:
        faces = mesh.faces
        for face in faces:
            if options.show_selected and not face.select:
                continue
            co = location_3d_to_region_2d(context.region,
                                          context.space_data.region_3d,
                                          obj.matrix_world * face.calc_center_median())
            idx = face.index
            face_data.append((idx, co))

    return vert_data, edge_data, face_data

def draw_callback_indicies(self, context):
    if context.mode != 'EDIT_MESH':
        return
    font_id = 0
    options = context.scene.mesh_indicies_display_options
    font_size = options.font_size
    verts = []
    edges = []
    faces = []

    ### Indicies
    verts, edges, faces = get_data(self, context, options)

    ### Vertex Indicies
    bgl.glColor4f(1, 0, 0, 1)
    if verts:
        for vert in verts:
            blf.position(font_id, vert[1][0], vert[1][1], 0)
            blf.size(font_id, font_size, 72)
            blf.draw(font_id, str(vert[0]))

    ### Edge Indicies
    bgl.glColor4f(0, 1, 0, 1)
    if edges:
        for edge in edges:
            blf.position(font_id, edge[1][0], edge[1][1], 0)
            blf.size(font_id, font_size, 72)
            blf.draw(font_id, str(edge[0]))
    
    ### Face Indicies
    bgl.glColor4f(0, 0, 1, 1)
    if faces:
        for face in faces:
            blf.position(font_id, face[1][0], face[1][1], 0)
            blf.size(font_id, font_size, 72)
            blf.draw(font_id, str(face[0]))
    
    ### LinkLoop Drawing ## does nothing useful
    #if options.loop_drawing:
    #    draw_loops(context, font_id, font_size)

    ### End
    bgl.glEnd()
    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


class Mesh_Index_Display(Operator):
    '''Draw mesh indicies'''
    bl_idname = "view3d.mesh_indicies_display"
    bl_label = "Mesh index display"
    bl_description='Start Display / ESC to Cancel'

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'ESC'}:
            context.region.callback_remove(self._handle)
            return {'CANCELLED'}

        return {'PASS_THROUGH'} #{'RUNNING_MODAL'}

    def invoke(self, context, event):
        try:
            if self._handle:
                context.region.callback_remove(self._handle)
                return {'CANCELLED'}
        except: pass
        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)

            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle = context.region.callback_add(draw_callback_indicies, (self, context), 'POST_PIXEL')

            self.mouse_path = []

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

#############################################################
class VIEW3D_PT_mesh_index_display_options(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Mesh Index Display Options"
    
    @classmethod
    def poll(cls, context):
        view = context.space_data
        return (view)

    def draw(self, context):
        geo = context.scene.mesh_indicies_display_options
        layout = self.layout
        col = layout.column()
        col.operator('view3d.mesh_indicies_display', text='Start Display',)
        row = layout.row()
        row = row.split(1/3, align = True)
        row.label(text='Indicies:')
        row.prop(geo, 'show_vertex_indicies', toggle=True)
        row.prop(geo, 'show_edge_indicies', toggle=True)
        row.prop(geo, 'show_face_indicies', toggle=True)
        col = layout.column(align=True)
        col.separator()
        col.prop(geo, 'show_selected', toggle=True)
        col.prop(geo, 'font_size')
        #col.prop(geo, 'loop_drawing')

#############################################################
# PropertyCollections
class MeshIndexDisplayOptions(PropertyGroup):
    show_vertex_indicies = BoolProperty(name='Vertex',
                                   default=True)
    show_edge_indicies = BoolProperty(name='Edge',
                                   default=False)
    show_face_indicies = BoolProperty(name='Face',
                                   default=False)
    font_size = IntProperty(name='Font Size',
                            default=16,
                            min=0, soft_min=0)
    show_selected = BoolProperty(name='Show only selected',
                                default=True)


#############################################################
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.mesh_indicies_display_options = PointerProperty(
                                               type=MeshIndexDisplayOptions,
                                               name='MeshIndexDisplayOptions')

def unregister():
    bpy.utils.unregister_module(__name__)
    del(bpy.types.Scene.geometry_display_options)

if __name__ == "__main__":
    register()