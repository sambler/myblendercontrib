# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_addon_info = {
    "name": "M3",
    "author": "Cory Perry (muraj)",
    "version": (0, 0, 2),
    "blender": (2, 5, 4),
    "api": 31878,
    "location": "File > Import-Export > M3 Import ",
    "description": "Import Blizzard M3 models (.m3 format)",
    "warning": "Alpha version",
    "wiki_url": "http://github.com/muraj/m3_import/wiki",
    "tracker_url": "http://github.com/muraj/m3_import/issues",
    "category": "Import-Export"}

if "bpy" in locals():
    import imp
    imp.reload(import_m3)
    #imp.reload(export_m3)
else:
    from . import import_m3
    #from . import export_m3

import bpy

def menu_import(self, context): 
    from io_scene_pmd import import_pmd
    self.layout.operator(
            import_m3.M3Importer.bl_idname, 
            text="Blizzard M3 (.m3)",
            icon='PLUGIN'
            )


#def menu_export(self, context):
# from io_mesh_raw import export_raw
# import os
# default_path = os.path.splitext(bpy.data.filepath)[0] + ".raw"
# self.layout.operator(export_raw.RawExporter.bl_idname, text="Raw Faces (.raw)").filepath = default_path


def register():
    bpy.types.INFO_MT_file_import.append(menu_import)
# bpy.types.INFO_MT_file_export.append(menu_export)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_import)
# bpy.types.INFO_MT_file_export.remove(menu_export)

if __name__ == "__main__":
    register()
