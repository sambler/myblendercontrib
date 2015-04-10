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
    'version': (1, 2),
    "blender": (2, 7, 3),
    'location': 'View3D > Properties panel > Silhouette',
    'description': 'Simple silhouette for animators and backups',
    'category': 'Animation'}

import bpy
import os
import datetime
import time
import sys
# noinspection PyUnresolvedReferences
from bpy.app.handlers import persistent

# noinspection PyUnusedLocal
# -------------------------------------
# Handler init render
# -------------------------------------


@persistent
def render_start_handler(dummy):
    myscene = bpy.data.scenes[bpy.context.scene.name]
    if myscene.render.use_stamp_note is True:
        # Saves formula
        scene = bpy.context.scene
        scene.silhoutte_formula = myscene.render.stamp_note_text
        # Set replacement text
        txt = myscene.render.stamp_note_text
        myscene.render.stamp_note_text = split_formula(txt)

# noinspection PyUnusedLocal
# -------------------------------------
# Handler end render
# -------------------------------------


@persistent
def render_end_handler(dummy):
    myscene = bpy.data.scenes[bpy.context.scene.name]
    if myscene.render.use_stamp_note is True:
        myscene.render.stamp_note_text = bpy.context.scene.silhoutte_formula

bpy.app.handlers.render_init.append(render_start_handler)
bpy.app.handlers.render_post.append(render_end_handler)
# -------------------------------------
# Replace formulas of stamp notes
# -------------------------------------


def split_formula(txt):
    # for example:
    # Resolution #bpy.data.scenes[bpy.context.scene.name].render.resolution_x#
    #  by #bpy.data.scenes[bpy.context.scene.name].render.resolution_y#
    while txt.find("#") > -1:
        idx = txt.index("#")
        initial = txt[0:idx]
        idx += 1
        idx2 = txt.index("#", idx)
        formula = txt[idx:idx2]
        pending = txt[idx2 + 1:]

        txt = initial + run_formula(formula) + pending

    return txt

# -------------------------------------
# Execute formula parameter
# -------------------------------------


def run_formula(runcmd):
    # noinspection PyBroadException
    try:
        cmd = "global buf; buf = " + runcmd
        exec(cmd)
        # noinspection PyUnresolvedReferences
        res = buf

        return str(res)
    except:
        return "*ERROR"

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
# Button: Save a backup with time
# ------------------------------------------------------


class BackupAction(bpy.types.Operator):
    bl_idname = "antonio_animation.backupfile"
    bl_label = "Backup"
    bl_description = "Create a backup copy of the file appending datetime to the name"

    # ------------------------------
    # Execute
    # ------------------------------
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def execute(self, context):
        (filepath, filename) = os.path.split(bpy.data.filepath)
        blendfile = os.path.splitext(filename)[0]

        st = "_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')

        outfile = os.path.join(filepath, blendfile + st + ".blend")
        # noinspection PyBroadException
        try:
            bpy.ops.wm.save_as_mainfile(filepath=outfile, copy=True)
            self.report({'INFO'}, outfile + " successfully saved")
            return {'FINISHED'}
        except:
            print("Unexpected error:" + str(sys.exc_info()))
            self.report({'ERROR'}, "Unable to save")
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

        row = box.row(align=True)
        row.operator("antonio_animation.backupfile", icon='SAVE_COPY')

# ------------------------------------------------------
# Registration
# ------------------------------------------------------


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.silhoutte_formula = bpy.props.StringProperty(name="Formula", maxlen=512)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.silhoutte_formula