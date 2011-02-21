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

bl_info = {
    'name': 'Bevel',
    'author': 'chromoly',
    'version': (0, 2),
    'blender': (2, 5, 6),
    'api': 34530,
    'location': 'View3D > EditMode > Specials',
    'wiki_url': '',
    'category': 'Mesh'}

if "bpy" in locals():
    import imp
    imp.reload(bevel)
else:
    from . import bevel

import bpy

def menu_func(self, context): 
    self.layout.operator(bevel.Bevel.bl_idname, text="Bevel")

def register():
    bpy.utils.register_class(bevel.Bevel)
    bpy.types.VIEW3D_MT_edit_mesh_specials.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)
    bpy.utils.register_class(bevel.Bevel)

if __name__ == '__main__':
    register()