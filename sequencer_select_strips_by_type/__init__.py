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

# ##### CHANGELOG #####
#
#  0.0.1
#      * Initial release.
#
#  0.0.2
#      * Updates to follow Blender API:
#        ** bl_addon_info renamed in bl_info!
#        ** adding bpy.utils.(un)register_module calls.
#      * Also, in standard import, using “from . import …” now.
#
#  0.0.3
#      * Now using an EnumProperty to set which types to (de)select. A little bit more verbose,
#        but much less hackish than the previous string technique…
#      * As requested by mindrones, renamed in “Sequencer Select Strips By Type”.
#
# ##### END OF CHANGELOG #####

bl_info = {
    "name": "Sequencer Select Strips By Type",
    "author": "Bastien Montagne",
    "version": (0, 0, 3),
    "blender": (2, 5, 6),
    "api": 35433,
    "location": "Video Sequence Editor header (Select menu)",
    "description": "Allows to select strips by their type (image, video, audio, etc.).",
    "warning": "beta",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
                "Scripts/Sequencer/Select Strips By Type",
    "tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=25833",
    "category": "Sequencer"}


if "bpy" in locals():
    import imp
    imp.reload(operator)
    imp.reload(menu)

else:
    import bpy
    from . import operator
    from . import menu

def register():
    bpy.utils.register_module(__name__)

    # Append the relevant menu entries.
    bpy.types.SEQUENCER_MT_select.append(menu.menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)

    # Remove the relevant menu entries.
    bpy.types.SEQUENCER_MT_select.remove(menu.menu_func)

if __name__ == "__main__":
    register()

