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
    'name': 'Vertex align',
    'author': 'chromoly',
    'version': (0, 3),
    'blender': (2, 5, 3),
    'api': 31847,
    'location': 'View3D > EditMode > Ctrl + A',
    'wiki_url': '',
    'category': 'Mesh'}


if "bpy" in locals():
    import imp
    imp.reload(vertex_align_25)
else:
    from . import vertex_align_25

import bpy


def register():
    km = bpy.context.window_manager.keyconfigs.default.keymaps['Mesh']
    kmi = km.items.new('wm.call_menu', 'A', 'PRESS', ctrl=True)
    kmi.properties.name = 'mesh.vertex_align'

def unregister():
    km = bpy.context.window_manager.keyconfigs.default.keymaps['Mesh']
    for kmi in km.items:
        if kmi.idname == 'wm.call_menu':
            if kmi.properties.name == 'mesh.vertex_align':
                km.items.remove(kmi)
                break

if __name__ == '__main__':
    register()
