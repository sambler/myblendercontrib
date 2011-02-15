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
    'name': 'Light Field Tools',
    'author': 'Aurel Wildfellner',
    'description': 'Tools to create a light field camera and projector',
    'version': (0, 2, 1),
    'blender': (2, 5, 6),
    'api': 34843,
    'location': 'View3D > Tool Shelf > Light Field Tools',
    'url': 'http://www.jku.at/cg/',
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Render/Light_Field_Tools",
    "tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=25719",
    'category': 'Render'
}


if "bpy" in locals():
    import imp
    imp.reload(light_field_tools)
else:
    from . import light_field_tools

import bpy


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

