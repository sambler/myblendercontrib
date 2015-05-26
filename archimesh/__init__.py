# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# PEP8 compliant (https://www.python.org/dev/peps/pep-0008)

# ----------------------------------------------------------
# File: __init__.py
# Author: Antonio Vazquez (antonioya)
# ----------------------------------------------------------
 
# ----------------------------------------------
# Define Addon info 
# ----------------------------------------------
bl_info = {
    "name": "Archimesh",
    "author": "Antonio Vazquez (antonioya)",
    "location": "View3D > Add > Mesh > Archimesh",
    "version": (1, 1, 0),
    "blender": (2, 6, 8),
    "description": "Generate rooms, doors, windows, kitchen cabinets, "
                   "shelves, roofs, stairs and other architecture stuff.",
    "category": "Add Mesh"}

import sys
import os

# ----------------------------------------------
# Add to Phyton path (once only)
# ----------------------------------------------
path = sys.path
flag = False
for item in path:
    if "archimesh" in item:
        flag = True
if flag is False:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'archimesh'))
    print("archimesh: added to phytonpath")

# ----------------------------------------------
# Import modules
# ----------------------------------------------
if "bpy" in locals():
    import imp
    imp.reload(room_maker)
    imp.reload(door_maker)
    imp.reload(window_maker)
    imp.reload(roof_maker)
    imp.reload(column_maker)
    imp.reload(stairs_maker)
    imp.reload(kitchen_maker)
    imp.reload(shelves_maker)
    imp.reload(books_maker)
    imp.reload(lamp_maker)
    imp.reload(curtain_maker)
    imp.reload(venetian_maker)
    imp.reload(main_panel)
    imp.reload(window_panel)
    print("archimesh: Reloaded multifiles")
else:
    import books_maker
    import column_maker
    import curtain_maker
    import venetian_maker
    import door_maker
    import kitchen_maker
    import lamp_maker
    import main_panel
    import roof_maker
    import room_maker
    import shelves_maker
    import stairs_maker
    import window_maker
    import window_panel

    print("archimesh: Imported multifiles")

# noinspection PyUnresolvedReferences
import bpy
# noinspection PyUnresolvedReferences
from bpy.props import *

# ----------------------------------------------------------
# Decoration assets
# ----------------------------------------------------------


class InfoMtMeshDecorationAdd(bpy.types.Menu):
    bl_idname = "INFO_MT_mesh_decoration_add"
    bl_label = "Decoration assets"

    # noinspection PyUnusedLocal
    def draw(self, context):
        self.layout.operator("mesh.archimesh_books", text="Add Books", icon="PLUGIN")
        self.layout.operator("mesh.archimesh_lamp", text="Add Lamp", icon="PLUGIN")
        self.layout.operator("mesh.archimesh_roller", text="Add Roller curtains", icon="PLUGIN")
        self.layout.operator("mesh.archimesh_venetian", text="Add Venetian blind", icon="PLUGIN")
        self.layout.operator("mesh.archimesh_japan", text="Add Japanese curtains", icon="PLUGIN")
    
# ----------------------------------------------------------
# Registration
# ----------------------------------------------------------


class InfoMtMeshCustomMenuAdd(bpy.types.Menu):
    bl_idname = "INFO_MT_mesh_custom_menu_add"
    bl_label = "Archimesh"

    # noinspection PyUnusedLocal
    def draw(self, context):
        self.layout.operator_context = 'INVOKE_REGION_WIN'
        self.layout.operator("mesh.archimesh_room", text="Add Room", icon="PLUGIN")
        self.layout.operator("mesh.archimesh_door", text="Add Door", icon="PLUGIN")
        self.layout.operator("mesh.archimesh_window", text="Add Rail Window", icon="PLUGIN")
        self.layout.operator("mesh.archimesh_winpanel", text="Add Panel Window", icon="PLUGIN")
        self.layout.operator("mesh.archimesh_kitchen", text="Add Cabinet", icon="PLUGIN")
        self.layout.operator("mesh.archimesh_shelves", text="Add Shelves", icon="PLUGIN")
        self.layout.operator("mesh.archimesh_column", text="Add Column", icon="PLUGIN")
        self.layout.operator("mesh.archimesh_stairs", text="Add Stairs", icon="PLUGIN")
        self.layout.operator("mesh.archimesh_roof", text="Add Roof", icon="PLUGIN")
        self.layout.menu("INFO_MT_mesh_decoration_add", text="Decoration props", icon="GROUP")

# --------------------------------------------------------------
# Register all operators and panels
# --------------------------------------------------------------
# Define menu


# noinspection PyUnusedLocal
def menu_func(self, context):
    self.layout.menu("INFO_MT_mesh_custom_menu_add", icon="PLUGIN")


def register():
    bpy.utils.register_class(InfoMtMeshCustomMenuAdd)
    bpy.utils.register_class(InfoMtMeshDecorationAdd)
    bpy.utils.register_class(room_maker.ROOM)
    bpy.utils.register_class(room_maker.RoomGeneratorPanel)
    bpy.utils.register_class(room_maker.ExportRoom)
    bpy.utils.register_class(room_maker.ImportRoom)
    bpy.utils.register_class(door_maker.DOOR)
    bpy.utils.register_class(door_maker.DoorObjectgeneratorpanel)
    bpy.utils.register_class(window_maker.WINDOWS)
    bpy.utils.register_class(window_maker.WindowObjectgeneratorpanel)
    bpy.utils.register_class(roof_maker.ROOF)
    bpy.utils.register_class(column_maker.COLUMN)
    bpy.utils.register_class(stairs_maker.STAIRS)
    bpy.utils.register_class(kitchen_maker.KITCHEN)
    bpy.utils.register_class(kitchen_maker.ExportInventory)
    bpy.utils.register_class(shelves_maker.SHELVES)
    bpy.utils.register_class(books_maker.BOOKS)
    bpy.utils.register_class(lamp_maker.LAMP)
    bpy.utils.register_class(curtain_maker.ROLLER)
    bpy.utils.register_class(curtain_maker.JAPAN)
    bpy.utils.register_class(window_panel.WindowEditPanel)
    bpy.utils.register_class(venetian_maker.VENETIAN)
    bpy.utils.register_class(venetian_maker.VenetianObjectgeneratorpanel)
    bpy.utils.register_class(main_panel.ArchimeshMainPanel)
    bpy.utils.register_class(main_panel.HoleAction)
    bpy.utils.register_class(main_panel.PencilAction)
    bpy.utils.register_class(main_panel.RunHintDisplayButton)
    bpy.utils.register_class(window_panel.WINPANEL)
    bpy.types.INFO_MT_mesh_add.append(menu_func)
    
    # Define properties
    bpy.types.Scene.archimesh_select_only = bpy.props.BoolProperty(name="Only selected",
                                                                   description="Apply auto holes only to"
                                                                               " selected objects",
                                                                   default=False)
    bpy.types.Scene.archimesh_ceiling = bpy.props.BoolProperty(name="Ceiling",
                                                               description="Create a ceiling.",
                                                               default=False)
    bpy.types.Scene.archimesh_floor = bpy.props.BoolProperty(name="Floor",
                                                             description="Create a floor automatically.",
                                                             default=False)

    bpy.types.Scene.archimesh_merge = bpy.props.BoolProperty(name="Close walls",
                                                             description="Close walls to create a full closed room.",
                                                             default=False)

    bpy.types.Scene.archimesh_text_color = bpy.props.FloatVectorProperty(
        name="Hint color",
        description="Color for the text and lines",
        default=(0.173, 0.545, 1.0, 1.0),
        min=0.1,
        max=1,
        subtype='COLOR',
        size=4)
    bpy.types.Scene.archimesh_walltext_color = bpy.props.FloatVectorProperty(
        name="Hint color",
        description="Color for the wall label",
        default=(1, 0.8, 0.1, 1.0),
        min=0.1,
        max=1,
        subtype='COLOR',
        size=4)
    bpy.types.Scene.archimesh_font_size = bpy.props.IntProperty(
        name="Text Size",
        description="Text size for hints",
        default=14, min=10, max=150)
    bpy.types.Scene.archimesh_wfont_size = bpy.props.IntProperty(
        name="Text Size",
        description="Text size for wall labels",
        default=16, min=10, max=150)
    bpy.types.Scene.archimesh_hint_space = bpy.props.FloatProperty(name='Separation', min=0, max=5, default=0.1,
                                                                   precision=2,
                                                                   description='Distance from object to display hint')
    bpy.types.Scene.archimesh_gl_measure = bpy.props.BoolProperty(name="Measures",
                                                                  description="Display measures",
                                                                  default=True)
    bpy.types.Scene.archimesh_gl_name = bpy.props.BoolProperty(name="Names",
                                                               description="Display names",
                                                               default=True)
    bpy.types.Scene.archimesh_gl_ghost = bpy.props.BoolProperty(name="All",
                                                                description="Display measures for all objects,"
                                                                            " not only selected",
                                                                default=True)

    # OpenGL flag
    wm = bpy.types.WindowManager
    # register internal property
    wm.archimesh_run_opengl = bpy.props.BoolProperty(default=False)


def unregister():
    bpy.utils.unregister_class(InfoMtMeshCustomMenuAdd)
    bpy.utils.unregister_class(InfoMtMeshDecorationAdd)
    bpy.utils.unregister_class(room_maker.ROOM)
    bpy.utils.unregister_class(room_maker.RoomGeneratorPanel)
    bpy.utils.unregister_class(room_maker.ExportRoom)
    bpy.utils.unregister_class(room_maker.ImportRoom)
    bpy.utils.unregister_class(door_maker.DOOR)
    bpy.utils.unregister_class(door_maker.DoorObjectgeneratorpanel)
    bpy.utils.unregister_class(window_maker.WINDOWS)
    bpy.utils.unregister_class(window_maker.WindowObjectgeneratorpanel)
    bpy.utils.unregister_class(roof_maker.ROOF)
    bpy.utils.unregister_class(column_maker.COLUMN)
    bpy.utils.unregister_class(stairs_maker.STAIRS)
    bpy.utils.unregister_class(kitchen_maker.KITCHEN)
    bpy.utils.unregister_class(kitchen_maker.ExportInventory)
    bpy.utils.unregister_class(shelves_maker.SHELVES)
    bpy.utils.unregister_class(books_maker.BOOKS)
    bpy.utils.unregister_class(lamp_maker.LAMP)
    bpy.utils.unregister_class(curtain_maker.ROLLER)
    bpy.utils.unregister_class(curtain_maker.JAPAN)
    bpy.utils.unregister_class(venetian_maker.VENETIAN)
    bpy.utils.unregister_class(venetian_maker.VenetianObjectgeneratorpanel)
    bpy.utils.unregister_class(main_panel.ArchimeshMainPanel)
    bpy.utils.unregister_class(main_panel.HoleAction)
    bpy.utils.unregister_class(main_panel.PencilAction)
    bpy.utils.unregister_class(main_panel.RunHintDisplayButton)
    bpy.utils.unregister_class(window_panel.WINPANEL)
    bpy.utils.unregister_class(window_panel.WindowEditPanel)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
    
    # Remove properties
    del bpy.types.Scene.archimesh_select_only
    del bpy.types.Scene.archimesh_ceiling
    del bpy.types.Scene.archimesh_floor
    del bpy.types.Scene.archimesh_merge
    del bpy.types.Scene.archimesh_text_color
    del bpy.types.Scene.archimesh_walltext_color
    del bpy.types.Scene.archimesh_font_size
    del bpy.types.Scene.archimesh_wfont_size
    del bpy.types.Scene.archimesh_hint_space
    del bpy.types.Scene.archimesh_gl_measure
    del bpy.types.Scene.archimesh_gl_name
    del bpy.types.Scene.archimesh_gl_ghost
    # remove OpenGL data
    main_panel.RunHintDisplayButton.handle_remove(main_panel.RunHintDisplayButton, bpy.context)
    wm = bpy.context.window_manager
    p = 'archimesh_run_opengl'
    if p in wm:
        del wm[p]


if __name__ == '__main__':
    register()