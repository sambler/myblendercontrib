#view3d_multiselect_menu.py (c) 2010 Sean Olson (liquidApe)
#Original Script by: Mariano Hidalgo (uselessdreamer)
#contributed to by: Crouch, sim88, sam, meta-androcto, and Michael W
#
#Tested with r28146
#
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
    'name': '3D View: Multiselect Menu',
    'author': 'Sean Olson (liquidApe)',
    'version': '1.0',
    'blender': (2, 5, 3),
    'location': 'View3D > Mouse > Menu ',
    'description': 'Added options for multiselect to the ctrl-tab menu',
    'url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/' \
        'Scripts/3D_interaction/multiselect_Menu',
    'category': '3D View'}
"Add multiselect options to ctrl-tab menu"

"""
Name: 'Multiselect Menu'
Blender: 253
"""

__author__ = ["Sean Olson (liquidape)"]
__version__ = '1.0'
__url__ = [""]
__bpydoc__ = """
Multiselect Menu
This adds a the multiselect Menu in the EditMode 3d view.

Usage:
*  This script gives adds the multiselect options to the ctrl-tab menu


Version history:
v0.1 -first working version
v1.0 -first uploaded version
"""
import bpy
from bpy import *

# multiselect menu
class VIEW3D_MT_Multiselect_Menu(bpy.types.Menu):
    bl_label = "MultiSelect Menu"

    def draw(self, context):
        layout = self.layout
        settings = context.tool_settings
        layout.operator_context = 'INVOKE_REGION_WIN'

        ob = context
        if ob.mode == 'EDIT_MESH':

            layout = self.layout
            row = layout.row()

            layout.operator_context = 'INVOKE_REGION_WIN'

            prop = layout.operator("wm.context_set_value", text="Vertex", icon='VERTEXSEL')
            prop.value = "(True, False, False)"
            prop.data_path = "tool_settings.mesh_selection_mode"

            prop = layout.operator("wm.context_set_value", text="Edge", icon='EDGESEL')
            prop.value = "(False, True, False)"
            prop.data_path = "tool_settings.mesh_selection_mode"

            prop = layout.operator("wm.context_set_value", text="Face", icon='FACESEL')
            prop.value = "(False, False, True)"
            prop.data_path = "tool_settings.mesh_selection_mode"
            layout.separator()

            prop = layout.operator("wm.context_set_value", text="Vertex & Edge", icon='ORTHO_OFF')
            prop.value = "(True, True, False)"
            prop.data_path = "tool_settings.mesh_selection_mode"

            prop = layout.operator("wm.context_set_value", text="Vertex & Face", icon='ORTHO')
            prop.value = "(True, False, True)"
            prop.data_path = "tool_settings.mesh_selection_mode"

            prop = layout.operator("wm.context_set_value", text="Edge & Face", icon='SNAP_FACE')
            prop.value = "(False, True, True)"
            prop.data_path = "tool_settings.mesh_selection_mode"
            layout.separator()

            prop = layout.operator("wm.context_set_value", text="Vertex & Edge & Face", icon='SNAP_VOLUME')
            prop.value = "(True, True, True)"
            prop.data_path = "tool_settings.mesh_selection_mode"                        



def register():
    
    km = bpy.context.manager.active_keyconfig.keymaps['Mesh']
    for kmi in km.items:
        if kmi.idname == 'wm.call_menu':
            if kmi.ctrl and not kmi.shift and not kmi.alt and kmi.value =="PRESS":
                if kmi.type =="TAB":
                   km.remove_item(kmi)
                   break
    kmi = km.items.add('wm.call_menu', 'TAB', 'PRESS', ctrl=True)
    kmi.properties.name = "VIEW3D_MT_Multiselect_Menu"

def unregister():

    km = bpy.context.manager.active_keyconfig.keymaps['Mesh']
    for kmi in km.items:
        if kmi.idname == 'wm.call_menu':
            if kmi.properties.name == "VIEW3D_MT_Multiselect_Menu":
                km.remove_item(kmi)
                break

if __name__ == "__main__":
    register()