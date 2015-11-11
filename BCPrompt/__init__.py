# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you may redistribute it, and/or
# modify it, under the terms of the GNU General Public License
# as published by the Free Software Foundation - either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, write to:
#
#   the Free Software Foundation Inc.
#   51 Franklin Street, Fifth Floor
#   Boston, MA 02110-1301, USA
#
# or go online at: http://www.gnu.org/licenses/ to view license options.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Console Prompt",
    "author": "Dealga McArdle",
    "version": (0, 1, 3),
    "blender": (2, 7, 4),
    "location": "Console - keystrokes",
    "description": "Adds feature to intercept console input and parse accordingly.",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Console"}

if 'bpy' in globals():
    print('{0}: detected reload event! cool.'.format(__package__))

    if 'bc_operators' in globals():
        import imp
        imp.reload(bc_operators)
        imp.reload(bc_panels)
        imp.reload(bc_utils)
        imp.reload(bc_search_utils)
        imp.reload(bc_gist_utils)
        imp.reload(bc_scene_utils)
        imp.reload(bc_update_utils)
        imp.reload(bc_CAD_utils)
        imp.reload(bc_TEXT_utils)
        imp.reload(bc_text_repr_utils)
        imp.reload(bc_package_manager)
        imp.reload(bc_command_dispatch)
        imp.reload(sub_util)
        imp.reload(fast_ops.curve_handle_equalizer)
        imp.reload(fast_ops.curve_nurbs_to_polyline)
        imp.reload(keymaps.console_keymaps)
        print('{0}: reloaded.'.format(__package__))

else:
    from . import bc_operators
    from . import bc_panels
    from . import bc_TEXT_utils
    from .fast_ops import curve_handle_equalizer
    from .fast_ops import curve_nurbs_to_polyline
    from .keymaps import console_keymaps

import bpy


def menu_func(self, context):
    self.layout.operator("curve.curve_handle_eq")
    self.layout.operator("curve.nurbs_to_polyline")


def register():
    bpy.utils.register_module(__name__)
    console_keymaps.add(__package__)
    bpy.types.VIEW3D_MT_edit_curve_specials.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_edit_curve_specials.remove(menu_func)
