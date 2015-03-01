# ##### BEGIN GPL LICENSE BLOCK #####
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
# ##### END GPL LICENSE BLOCK #####

# ----------------------------------------------------------
# File: silhouette.py
# Author: Antonio Vazquez (antonioya)
# PEP8 compliant (https://www.python.org/dev/peps/pep-0008)
# ----------------------------------------------------------

bl_info = {
    'name': 'Silhouette',
    'author': 'Antonio Vazquez (antonioya)',
    'version': (1, 0),
    "blender": (2, 7, 3),
    'location': 'View3D > Properties panel > Silhouette',
    'description': 'Simple silhouette for animators',
    'category': 'Animation'}

import bpy

# ------------------------------------------------------
# Button Action class
# Display silhouette
# ------------------------------------------------------


class RunActionSilhouetteOn(bpy.types.Operator):
    bl_idname = "animation.silhouette_on"
    bl_label = " Silhouette"
    bl_description = "Enable Silhouette view"

    # ------------------------------
    # Execute
    # ------------------------------
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def execute(self, context):
        # ----------------------------
        # Search lamps in scene
        # ----------------------------
        for l in bpy.data.scenes[bpy.context.scene.name].objects:
            if l.type == 'LAMP':
                l.hide_render = True

        # ---------------------------------------
        # Set render engine and shading mode
        # ---------------------------------------
        scn = bpy.context.scene
        # Set cycles render engine if not selected
        if not scn.render.engine == 'BLENDER_RENDER':
            scn.render.engine = 'BLENDER_RENDER'

        bpy.context.scene.game_settings.material_mode = 'GLSL'

        # ---------------------------------------
        # Loop areas to get VIEW_3D area
        # ---------------------------------------
        for e in bpy.data.screens[bpy.context.screen.name].areas:
            if e.type == 'VIEW_3D':
                e.spaces.active.show_only_render = True
                e.spaces.active.viewport_shade = 'TEXTURED'
                e.spaces.active.show_manipulator = False

        return {'FINISHED'}


# ------------------------------------------------------
# Button Action class
# Display figure only (render objects)
# ------------------------------------------------------


class RunActionSilhouetteHalf(bpy.types.Operator):
    bl_idname = "animation.silhouette_half"
    bl_label = "Render"
    bl_description = "Enable Figure view"

    # ------------------------------
    # Execute
    # ------------------------------
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def execute(self, context):
        # ----------------------------
        # Search lamps in scene
        # ----------------------------
        for l in bpy.data.scenes[bpy.context.scene.name].objects:
            if l.type == 'LAMP':
                l.hide_render = False

        # ---------------------------------------
        # Set render engine and shading mode
        # ---------------------------------------
        scn = bpy.context.scene
        # Set cycles render engine if not selected
        if not scn.render.engine == 'CYCLES':
            scn.render.engine = 'CYCLES'

        bpy.context.scene.game_settings.material_mode = 'MULTITEXTURE'
        # ---------------------------------------
        # Loop areas to get VIEW_3D area
        # ---------------------------------------
        for e in bpy.data.screens[bpy.context.screen.name].areas:
            if e.type == 'VIEW_3D':
                e.spaces.active.show_only_render = True
                e.spaces.active.viewport_shade = 'SOLID'
                e.spaces.active.show_manipulator = False

        return {'FINISHED'}


# ------------------------------------------------------
# Button Action class
# Display silhouette off (default mode)
# ------------------------------------------------------
class RunActionSilhouetteOff(bpy.types.Operator):
    bl_idname = "animation.silhouette_off"
    bl_label = "Default"
    bl_description = "Enable Solid view"

    # ------------------------------
    # Execute
    # ------------------------------
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def execute(self, context):
        # ----------------------------
        # Search lamps in scene
        # ----------------------------
        for l in bpy.data.scenes[bpy.context.scene.name].objects:
            if l.type == 'LAMP':
                l.hide_render = False

        # ---------------------------------------
        # Set render engine and shading mode
        # ---------------------------------------
        scn = bpy.context.scene
        # Set cycles render engine if not selected
        if not scn.render.engine == 'CYCLES':
            scn.render.engine = 'CYCLES'

        bpy.context.scene.game_settings.material_mode = 'MULTITEXTURE'

        # ---------------------------------------
        # Loop areas to get VIEW_3D area
        # ---------------------------------------
        for e in bpy.data.screens[bpy.context.screen.name].areas:
            if e.type == 'VIEW_3D':
                e.spaces.active.show_only_render = False
                e.spaces.active.viewport_shade = 'SOLID'
                e.spaces.active.show_manipulator = True

        return {'FINISHED'}


# ------------------------------------------------------
# Defines UI panel
# ------------------------------------------------------


class UISilhouettePanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Silhouette Tools"

    # noinspection PyUnusedLocal
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.operator("animation.silhouette_on", icon='GHOST_ENABLED')
        row.operator("animation.silhouette_half")
        row.operator("animation.silhouette_off")

# ------------------------------------------------------
# Registration
# ------------------------------------------------------


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
