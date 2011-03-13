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

import bpy

# Selection.
class SEQUENCER_MT_select_by_type(bpy.types.Menu):
    """
    Sub-menu to select strips by types.
    """
    bl_label = "Select by Type"

    def draw(self, context):
        layout = self.layout

        layout.column()
        layout.operator("sequencer.select_by_type", text="All Graphical Strips").select_types = {
                "CROSS", "ADD", "SUBTRACT", "ALPHA_OVER", "ALPHA_UNDER", "GAMMA_CROSS", "MULTIPLY",
                "OVER_DROP", "PLUGIN", "WIPE", "GLOW", "TRANSFORM", "COLOR", "SPEED", "IMAGE",
                "MOVIE", "SCENE", "META"} # META might be graphical…
        layout.operator("sequencer.select_by_type", text="All Effect Strips").select_types = {
                "CROSS", "ADD", "SUBTRACT", "ALPHA_OVER", "ALPHA_UNDER", "GAMMA_CROSS", "MULTIPLY",
                "OVER_DROP", "PLUGIN", "WIPE", "GLOW", "TRANSFORM", "COLOR", "SPEED"}
        layout.separator()
        layout.operator("sequencer.select_by_type", text="Video Strips").select_types = {"MOVIE"}
        layout.operator("sequencer.select_by_type", text="Image Strips").select_types = {"IMAGE"}
        layout.operator("sequencer.select_by_type", text="Scene Strips").select_types = {"SCENE"}
        layout.operator("sequencer.select_by_type", text="Sound Strips").select_types = {"SOUND"}
        layout.operator("sequencer.select_by_type", text="Meta Strips").select_types  = {"META"}

        layout.separator()
        layout.menu("SEQUENCER_MT_select_by_type_effects")

class SEQUENCER_MT_select_by_type_effects(bpy.types.Menu):
    """
    Sub-menu to select effect strips by types.
    """
    bl_label = "Effects"

    def draw(self, context):
        layout = self.layout

        layout.column()
        layout.operator("sequencer.select_by_type", text="Add").select_types         = {"ADD"}
        layout.operator("sequencer.select_by_type", text="Subtract").select_types    = {"SUBTRACT"}
        layout.operator("sequencer.select_by_type", text="Multiply").select_types    = {"MULTIPLY"}
        layout.operator("sequencer.select_by_type", text="Alpha Over").select_types  = {"ALPHA_OVER"}
        layout.operator("sequencer.select_by_type", text="Alpha Under").select_types = {"ALPHA_UNDER"}
        layout.operator("sequencer.select_by_type", text="Over Drop").select_types   = {"OVER_DROP"}
        layout.operator("sequencer.select_by_type", text="Cross").select_types       = {"CROSS"}
        layout.operator("sequencer.select_by_type", text="Gamma Cross").select_types = {"GAMMA_CROSS"}
        layout.operator("sequencer.select_by_type", text="Wipe").select_types        = {"WIPE"}
        layout.operator("sequencer.select_by_type", text="Glow").select_types        = {"GLOW"}
        layout.operator("sequencer.select_by_type", text="Transform").select_types   = {"TRANSFORM"}
        layout.operator("sequencer.select_by_type", text="Color").select_types       = {"COLOR"}
        layout.operator("sequencer.select_by_type", text="Speed").select_types       = {"SPEED"}
        layout.operator("sequencer.select_by_type", text="Plugin").select_types      = {"PLUGIN"}

# Deselection
class SEQUENCER_MT_deselect_by_type(bpy.types.Menu):
    """
    Sub-menu to deselect strips by types.
    """
    bl_label = "Deselect by Type"

    def draw(self, context):
        layout = self.layout

        layout.column()
        me = layout.operator("sequencer.select_by_type", text="All Graphical Strips")
        me.select_types = {"CROSS", "ADD", "SUBTRACT", "ALPHA_OVER", "ALPHA_UNDER", "GAMMA_CROSS",
                "MULTIPLY", "OVER_DROP", "PLUGIN", "WIPE", "GLOW", "TRANSFORM", "COLOR", "SPEED",
                "IMAGE", "MOVIE", "SCENE", "META"} # META might be graphical…
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="All Effect Strips")
        me.select_types = {"CROSS", "ADD", "SUBTRACT", "ALPHA_OVER", "ALPHA_UNDER", "GAMMA_CROSS",
                "MULTIPLY", "OVER_DROP", "PLUGIN", "WIPE", "GLOW", "TRANSFORM", "COLOR", "SPEED"}
        me.deselect = True
        me = layout.separator()
        me = layout.operator("sequencer.select_by_type", text="Video Strips")
        me.select_types = {"MOVIE"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Image Strips")
        me.select_types = {"IMAGE"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Scene Strips")
        me.select_types = {"SCENE"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Sound Strips")
        me.select_types = {"SOUND"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Meta Strips")
        me.select_types  = {"META"}
        me.deselect = True

        layout.separator()
        layout.menu("SEQUENCER_MT_deselect_by_type_effects")

class SEQUENCER_MT_deselect_by_type_effects(bpy.types.Menu):
    """
    Sub-menu to deselect effect strips by types.
    """
    bl_label = "Effects"

    def draw(self, context):
        layout = self.layout

        layout.column()
        me = layout.operator("sequencer.select_by_type", text="Add")
        me.select_types = {"ADD"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Subtract")
        me.select_types = {"SUBTRACT"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Multiply")
        me.select_types = {"MULTIPLY"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Alpha Over")
        me.select_types = {"ALPHA_OVER"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Alpha Under")
        me.select_types = {"ALPHA_UNDER"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Over Drop")
        me.select_types = {"OVER_DROP"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Cross")
        me.select_types = {"CROSS"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Gamma Cross")
        me.select_types = {"GAMMA_CROSS"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Wipe")
        me.select_types = {"WIPE"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Glow")
        me.select_types = {"GLOW"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Transform")
        me.select_types = {"TRANSFORM"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Color")
        me.select_types = {"COLOR"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Speed")
        me.select_types = {"SPEED"}
        me.deselect = True
        me = layout.operator("sequencer.select_by_type", text="Plugin")
        me.select_types = {"PLUGIN"}
        me.deselect = True

def menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("SEQUENCER_MT_select_by_type")
    layout.menu("SEQUENCER_MT_deselect_by_type")

