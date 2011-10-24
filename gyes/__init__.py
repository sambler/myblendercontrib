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


""" Copyright  Kilon 2011 GPL licence applies"""

bl_info = {
    "name": "Gyes (A Blender MultiTool)",
    "description": "Gyes is a collection of scripts, named <tools> that simplify , automate and extend blender",
    "author": "Kilon",
    "version": (0,0,7),
    "blender": (2, 5, 9),
    "api": 40500,
    "location": "View3D > Left panel ",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/System/Gyes",
    "tracker_url": "https://github.com/kilon/Gyes",
    "category": "System"}
    
if "bpy" in locals():
    import imp
    imp.reload(random_material_generator)
    imp.reload(random_texture_generator)
    #imp.reload(random_landscape_generator)
else:
    from gyes import random_material_generator
    from gyes import random_texture_generator
    #from gyes import random_landscape_generator
    
import bpy
from bpy.props import *


# Choose the tool you want to use
bpy.types.Scene.tool = EnumProperty(attr='tool', name='Tool', items=(
('RMG', 'RMG', 'Random Material Generator'),
('RTG', 'RTG', 'Random Texture Generator'),
('RLG', 'RLG' , 'Random Landscape Generator'),
('TARTARA', 'TARTARA', 'An online Library for any kind of blender asset')),default='RMG')


rm = random_material_generator.rm
rt = random_texture_generator.rt                 
# this the main panel
class gyes_panel(bpy.types.Panel):
    bl_label = "Gyes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    
    """@classmethod    
    def poll(self, context):
        if context.object and context.object.type == 'MESH':                    
            return len(context.object.data.materials)"""
        
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene , "tool" )
        
        # check which tool the user has selected (RGM is the default one) and display the appropriate gui
        
        if context.scene.tool == 'RMG' :
            rm.draw_gui(context,self)
        
        if context.scene.tool == 'RTG' :
            rt.draw_gui(context,self,rm)
 
        r = layout.row()
        if context.scene.tool == 'RLG' :
            r.label(text="WIP not finished yet")
        if context.scene.tool == 'TARTARA' :
            r.label(text="WIP not finished yet")


        
def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

 
if __name__ == "__main__":
    register()
