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

# <pep8 compliant>

import bpy


class RENDER_PT_copy_settings(bpy.types.Panel):
    bl_label = "Copy Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER'}

    def draw(self, context):
        layout = self.layout
        cp_sett = context.scene.render_copy_settings

        layout.operator("scene.render_copy_settings", text="Copy Render Settings")

        # This will update affected_settings/allowed_scenes (as this seems to be impossible
        # to do it from here…).
        if bpy.ops.scene.render_copy_settings_prepare.poll():
            bpy.ops.scene.render_copy_settings_prepare()

        split = layout.split(0.75)
        split.template_list(cp_sett, "affected_settings", cp_sett, "aff_sett_idx",
                            enum_ctrls_name="template_list_controls", rows=6)
        col = split.column()
        label = ""
        if (cp_sett.affected_settings["resolution_x"].copy and
            cp_sett.affected_settings["resolution_y"].copy and
            cp_sett.affected_settings["pixel_aspect_x"].copy and
            cp_sett.affected_settings["pixel_aspect_y"].copy):
            label = "Clear Resolution"
        else:
            label = "Set Resolution"
        col.operator("scene.render_copy_settings_preset", text=label, ).presets = {"resolution"}
        if cp_sett.affected_settings["resolution_percentage"].copy:
            label = "Clear Scale"
        else:
            label = "Set Scale"
        col.operator("scene.render_copy_settings_preset", text=label).presets = {"scale"}
        if (cp_sett.affected_settings["use_antialiasing"].copy and
            cp_sett.affected_settings["antialiasing_samples"].copy):
            label = "Clear OSA"
        else:
            label = "Set OSA"
        col.operator("scene.render_copy_settings_preset", text=label).presets = {"osa"}
        if (cp_sett.affected_settings["threads_mode"].copy and
            cp_sett.affected_settings["threads"].copy):
            label = "Clear Threads"
        else:
            label = "Set Threads"
        col.operator("scene.render_copy_settings_preset", text=label).presets = {"threads"}
        if (cp_sett.affected_settings["use_fields"].copy and
            cp_sett.affected_settings["field_order"].copy and
            cp_sett.affected_settings["use_fields_still"].copy):
            label = "Clear Fields"
        else:
            label = "Set Fields"
        col.operator("scene.render_copy_settings_preset", text=label).presets = {"fields"}
        if cp_sett.affected_settings["use_stamp"].copy:
            label = "Clear Stamp"
        else:
            label = "Set Stamp"
        col.operator("scene.render_copy_settings_preset", text=label).presets = {"stamp"}

        layout.prop(cp_sett, "filter_scene")
        if len(cp_sett.allowed_scenes):
            layout.label("Affected Scenes:")
            # XXX Unfortunately, there can only be one template_list per panel…
#            layout.template_list(cp_sett, "allowed_scenes", cp_sett, "allw_scenes_idx", rows=5)
            col = layout.column_flow(columns=0)
            for i, prop in enumerate(cp_sett.allowed_scenes):
                col.prop(prop, "allowed", toggle=True, text=prop.name)
        else:
            layout.label(text="No Affectable Scenes!", icon="ERROR")
