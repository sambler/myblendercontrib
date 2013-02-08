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

# <pep8-80 compliant>

# Export wrappers and integration with external tools.

import bpy
import os


def write_mesh(context, info, report_cb):
    scene = context.scene
    print_3d = scene.print_3d

    obj_base = scene.object_bases.active
    obj = obj_base.object

    context_override = context.copy()
    context_override["selected_bases"] = [obj_base]
    context_override["selected_objects"] = [obj]

    export_format = print_3d.export_format

    export_path = bpy.path.abspath(print_3d.export_path)

    # Create name 'export_path/blendname-objname'
    # add the filename component
    if bpy.data.is_saved:
        name = os.path.basename(bpy.data.filepath)
        name = os.path.splitext(name)[0]
    else:
        name = "untitled"
    # add object name
    name += "-%s" % bpy.path.clean_name(obj.name)

    # first ensure the path is created
    os.makedirs(export_path, exist_ok=True)

    filepath = os.path.join(export_path, name)

    # ensure addon is enabled
    import addon_utils

    def addon_ensure(addon_id):
        # Enable the addon, dont change preferences.
        default_state, loaded_state = addon_utils.check(addon_id)
        if not loaded_state:
            addon_utils.enable(addon_id, default_set=False)

    if export_format == 'STL':
        addon_ensure("io_mesh_stl")
        filepath = bpy.path.ensure_ext(filepath, ".stl")
        ret = bpy.ops.export_mesh.stl(
                context_override,
                filepath=filepath,
                ascii=False,
                use_mesh_modifiers=True,
                )
    elif export_format == 'PLY':
        addon_ensure("io_mesh_ply")
        filepath = bpy.path.ensure_ext(filepath, ".ply")
        ret = bpy.ops.export_mesh.ply(
                context_override,
                filepath=filepath,
                use_mesh_modifiers=True,
                )
    elif export_format == 'X3D':
        addon_ensure("io_scene_x3d")
        filepath = bpy.path.ensure_ext(filepath, ".x3d")
        ret = bpy.ops.export_scene.x3d(
                context_override,
                filepath=filepath, use_mesh_modifiers=True,
                use_selection=True,
                )
    elif export_format == 'OBJ':
        addon_ensure("io_scene_obj")
        filepath = bpy.path.ensure_ext(filepath, ".obj")
        ret = bpy.ops.export_scene.obj(
                context_override,
                filepath=filepath,
                use_mesh_modifiers=True,
                use_selection=True,
                )
    else:
        assert(0)

    if 'FINISHED' in ret:
        info.append(("%r ok" % os.path.basename(filepath), None))

        if report_cb is not None:
            report_cb({'INFO'}, "Exported: %r" % filepath)
        return True
    else:
        info.append(("%r fail" % os.path.basename(filepath), None))
        return False
