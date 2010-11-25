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

bl_addon_info = {
    'name': 'AniMesh',
    'author': 'Daniel Salazar <zanqdo@gmail.com>',
    'version': (0, 2),
    'blender': (2, 5, 5),
    'api': 33232,
    'location': 'Select a Mesh: Toolbar > AniMesh panel',
    'description': 'Allows animation of mesh data (Verts, VCols, VGroups, UVs)',
    'warning': 'Blender API has some bugs around this still',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Animation/AniMesh',
    'tracker_url': 'http://projects.blender.org/tracker/index.php?'\
        'func=detail&aid=24839&group_id=153&atid=469',
    'category': 'Animation'}

'''-------------------------------------------------------------------------
Thanks to Campbell Barton for hes API additions and fixes
Daniel Salazar - ZanQdo

Rev 0.1 initial release
Rev 0.2 added support for animating UVs, VCols, VGroups
-------------------------------------------------------------------------'''

import bpy
from bpy.props import *


#
# Property Definitions
#
bpy.types.WindowManager.key_points = BoolProperty(
    name="Points",
    description="Insert keyframes on point locations",
    default=True)

bpy.types.WindowManager.key_uvs = BoolProperty(
    name="UVs",
    description="Insert keyframes on active UV coordinates",
    default=False)

bpy.types.WindowManager.key_vcols = BoolProperty(
    name="VCols",
    description="Insert keyframes on active Vertex Color values",
    default=False)

bpy.types.WindowManager.key_vgroups = BoolProperty(
    name="VGroups",
    description="Insert keyframes on active Vertex Group values",
    default=False)


#
# GUI (Panel)
#
class VIEW3D_PT_animesh(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'AniMesh'

    # show this add-on only in the Camera-Data-Panel
    @classmethod
    def poll(self, context):
        if context.active_object:
            return context.active_object.type  == 'MESH'
    
    # draw the gui
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        
        #col.label(text="Keyframing:")
        row = col.row()
        row.prop(context.window_manager, "key_points")
        row.prop(context.window_manager, "key_uvs")
        row = col.row()
        row.prop(context.window_manager, "key_vcols")
        row.prop(context.window_manager, "key_vgroups")
        
        row = col.row()
        row.operator('mesh.insert_keyframe_animesh')
        row.operator('mesh.delete_keyframe_animesh')
        row = layout.row()
        row.operator('mesh.clear_animation_animesh')


class MESH_OT_insert_keyframe_animesh(bpy.types.Operator):
    bl_label = 'Insert'
    bl_idname = 'mesh.insert_keyframe_animesh'
    bl_description = 'Insert an Animesh Keyframe'
    bl_options = {'REGISTER', 'UNDO'}
    
    
    # on mouse up:
    def invoke(self, context, event):

        self.execute(context)

        return {'FINISHED'}


    def execute(op, context):
        
        Obj = context.active_object
        
        if Obj.type == 'MESH':
            Mode = False
            if context.mode == 'EDIT_MESH':
                Mode = not Mode
                bpy.ops.object.editmode_toggle()
            
            Data = Obj.data
            
            if context.window_manager.key_points or context.window_manager.key_vgroups:
                for Vert in Data.vertices:
                    if context.window_manager.key_points:
                        Vert.keyframe_insert('co')
                    if context.window_manager.key_vgroups:
                        for Group in Vert.groups:
                            Group.keyframe_insert('weight')
                    
            if context.window_manager.key_uvs:
                for UVLayer in Data.uv_textures:
                    if UVLayer.active: # only insert in active UV layer
                        for Data in UVLayer.data:
                            Data.keyframe_insert('uv')

            if context.window_manager.key_vcols:
                for VColLayer in Data.vertex_colors:
                    if VColLayer.active: # only insert in active VCol layer
                        for Data in VColLayer.data:
                            Data.keyframe_insert('color1')
                            Data.keyframe_insert('color2')
                            Data.keyframe_insert('color3')
                            Data.keyframe_insert('color4')
            
            
            if Mode:
                bpy.ops.object.editmode_toggle()


        return {'FINISHED'}


class MESH_OT_delete_keyframe_animesh(bpy.types.Operator):
    bl_label = 'Delete'
    bl_idname = 'mesh.delete_keyframe_animesh'
    bl_description = 'Delete an Animesh Keyframe'
    bl_options = {'REGISTER', 'UNDO'}
    
    
    # on mouse up:
    def invoke(self, context, event):

        self.execute(context)

        return {'FINISHED'}


    def execute(op, context):
        
        Obj = context.active_object
        
        if Obj.type == 'MESH':
            Mode = False
            if context.mode == 'EDIT_MESH':
                Mode = not Mode
                bpy.ops.object.editmode_toggle()
            
            Data = Obj.data
            
            if context.window_manager.key_points or context.window_manager.key_vgroups:
                for Vert in Data.vertices:
                    if context.window_manager.key_points:
                        Vert.keyframe_delete('co')
                    if context.window_manager.key_vgroups:
                        for Group in Vert.groups:
                            Group.keyframe_delete('weight')
                    
            if context.window_manager.key_uvs:
                for UVLayer in Data.uv_textures:
                    if UVLayer.active: # only delete in active UV layer
                        for Data in UVLayer.data:
                            Data.keyframe_delete('uv')

            if context.window_manager.key_vcols:
                for VColLayer in Data.vertex_colors:
                    if VColLayer.active: # only delete in active VCol layer
                        for Data in VColLayer.data:
                            Data.keyframe_delete('color1')
                            Data.keyframe_delete('color2')
                            Data.keyframe_delete('color3')
                            Data.keyframe_delete('color4')
            
            
            if Mode:
                bpy.ops.object.editmode_toggle()


        return {'FINISHED'}


class MESH_OT_clear_animation_animesh(bpy.types.Operator):
    bl_label = 'Clear Animation'
    bl_idname = 'mesh.clear_animation_animesh'
    bl_description = 'Clear all animation from the mesh'
    bl_options = {'REGISTER', 'UNDO'}

    # on mouse up:
    def invoke(self, context, event):
        
        wm = context.window_manager
        return wm.invoke_confirm(self, event)
    
    
    def execute(op, context):
        
        Data = context.active_object.data
        Data.animation_data_clear()
        
        return {'FINISHED'}


def register():
    pass
    
def unregister():
    pass
    
if __name__ == "__main__":
    register()
