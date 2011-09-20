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

# These operators are only defined because it seems impossible to directly edit properties from
# UI code…


# A sorting func for collections (working in-place).
# XXX Not optimized at all…
# XXX If some items in the collection do not have the sortkey property, they are just ignored…
def collection_property_sort(collection, sortkey, start_idx=0):
    while start_idx + 1 < len(collection):
        while not hasattr(collection[start_idx], sortkey):
            start_idx += 1
            if start_idx + 1 >= len(collection):
                return collection
        min_idx = start_idx
        min_prop = collection[start_idx]
        for i, prop in enumerate(collection[start_idx + 1:]):
            if not hasattr(prop, sortkey):
                continue
            if getattr(prop, sortkey) < getattr(min_prop, sortkey):
                min_prop = prop
                min_idx = i + start_idx + 1
        collection.move(min_idx, start_idx)
        start_idx += 1
    return collection


class RenderCopySettingsPrepare(bpy.types.Operator):
    '''
    Prepare internal data for render_copy_settings (gathering all existing render settings,
    and scenes).
    '''
    bl_idname = "scene.render_copy_settings_prepare"
    bl_label = "Render: Copy Settings Prepare"
    bl_option = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.scene != None

    def execute(self, context):
        cp_sett = context.scene.render_copy_settings

        # Get all available render settings, and update accordingly affected_settings…
        props = set()
        for prop in context.scene.render.bl_rna.properties:
            if prop.identifier in {'rna_type'}:
                continue
            if prop.is_readonly:
                continue
            props.add(prop.identifier)
        for i, sett in enumerate(cp_sett.affected_settings):
            if sett.name not in props:
                cp_sett.affected_settings.remove(i)
            else:
                props.remove(sett.name)
        for prop in props:
            sett = cp_sett.affected_settings.add()
            sett.name = prop
#            sett.init_TemplateListControls()
        collection_property_sort(cp_sett.affected_settings, "name")

        # Get all available scenes, and update accordingly allowed_scenes…
        regex = None
        if cp_sett.filter_scene:
            try:
                import re
                try:
                    regex = re.compile(cp_sett.filter_scene)
                except Exception as e:
                    self.report('ERROR_INVALID_INPUT', "The filter-scene regex " \
                                "did not compile:\n    (%s)." % str(e))
                    return {'CANCELLED'}
            except:
                regex = None
                self.report('WARNING', "Unable to import the re module. Regex " \
                            "scene filtering will be disabled!")
        scenes = set()
        for scene in bpy.data.scenes:
            if scene == bpy.context.scene:  # Exclude current scene!
                continue
            if regex:  # If a valid filtering regex, only keep scenes matching it.
                if regex.match(scene.name):
                    scenes.add(scene.name)
            else:
                scenes.add(scene.name)
        for i, scene in enumerate(cp_sett.allowed_scenes):
            if scene.name not in scenes:
                cp_sett.allowed_scenes.remove(i)
            else:
                scenes.remove(scene.name)
        for scene in scenes:
            sett = cp_sett.allowed_scenes.add()
            sett.name = scene
#            sett.init_TemplateListControls()
        collection_property_sort(cp_sett.allowed_scenes, "name")

        return {'FINISHED'}


from bpy.props import EnumProperty


class RenderCopySettingsPreset(bpy.types.Operator):
    '''
    Apply some presets of render settings to copy to other scenes.
    '''
    bl_idname = "scene.render_copy_settings_preset"
    bl_label = "Render: Copy Settings Preset"
    bl_description = "Apply or clear this preset of render settings."
    # Enable undo…
    bl_option = {'REGISTER', 'UNDO'}

    presets = EnumProperty(items=(("resolution", "Render Resolution", "Render resolution and aspect ratio settings"),
                                  ("scale", "Render Scale", "The “Render Scale” setting."),
                                  ("osa", "Render OSA", "The OSA toggle and sample settings."),
                                  ("threads", "Render Threads", "The thread mode and number settings."),
                                  ("fields", "Render Fields", "The Fields settings."),
                                  ("stamp", "Render Stamp", "The Stamp toggle."),
                                 ),
                           default=set(),
                           options={"ENUM_FLAG"})

    @classmethod
    def poll(cls, context):
        return context.scene != None

    def execute(self, context):
        cp_sett = context.scene.render_copy_settings
        if "resolution" in self.presets:
            res_x = cp_sett.affected_settings["resolution_x"]
            res_y = cp_sett.affected_settings["resolution_y"]
            asp_x = cp_sett.affected_settings["pixel_aspect_x"]
            asp_y = cp_sett.affected_settings["pixel_aspect_y"]
            if res_x.copy and res_y.copy and asp_x.copy and asp_y.copy:
                res_x.copy = res_y.copy = asp_x.copy = asp_y.copy = False
            else:
                res_x.copy = res_y.copy = asp_x.copy = asp_y.copy = True
        if "scale" in self.presets:
            scale = cp_sett.affected_settings["resolution_percentage"]
            if scale.copy:
                scale.copy = False
            else:
                scale.copy = True
        if "osa" in self.presets:
            osa = cp_sett.affected_settings["use_antialiasing"]
            osa_lvl = cp_sett.affected_settings["antialiasing_samples"]
            if osa.copy and osa_lvl.copy:
                osa.copy = osa_lvl.copy = False
            else:
                osa.copy = osa_lvl.copy = True
        if "threads" in self.presets:
            thrd_mode = cp_sett.affected_settings["threads_mode"]
            threads = cp_sett.affected_settings["threads"]
            if thrd_mode.copy and threads.copy:
                thrd_mode.copy = threads.copy = False
            else:
                thrd_mode.copy = threads.copy = True
        if "fields" in self.presets:
            fields = cp_sett.affected_settings["use_fields"]
            field_ord = cp_sett.affected_settings["field_order"]
            fields_still = cp_sett.affected_settings["use_fields_still"]
            if fields.copy and field_ord.copy and fields_still.copy:
                fields.copy = field_ord.copy = fields_still.copy = False
            else:
                fields.copy = field_ord.copy = fields_still.copy = True
        if "stamp" in self.presets:
            stamp = cp_sett.affected_settings["use_stamp"]
            if stamp.copy:
                stamp.copy = False
            else:
                stamp.copy = True
        return {'FINISHED'}


# Real interesting stuff…

def do_copy(context, affected_settings, allowed_scenes):
    # Stores render settings from current scene.
    p = dict((n, None) for n in affected_settings)
    # put it in all other (valid) scenes’ render settings!
    for scene in bpy.data.scenes:
        # If scene not in allowed scenes, skip.
        if scene.name not in allowed_scenes:
            continue
        # Propagate all affected settings.
        for sett in affected_settings:
            if p[sett] is None:
                p[sett] = getattr(context.scene.render, sett)
            setattr(scene.render, sett, p[sett])


class RenderCopySettings(bpy.types.Operator):
    '''
    Copy render settings from current scene to others.
    '''
    bl_idname = "scene.render_copy_settings"
    bl_label = "Render: Copy Settings"
    # Enable undo…
    bl_option = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene != None

    def execute(self, context):
        regex = None
        cp_sett = context.scene.render_copy_settings
        affected_settings = set([sett.name for sett in cp_sett.affected_settings if sett.copy])
        allowed_scenes = set([sce.name for sce in cp_sett.allowed_scenes if sce.allowed])
        do_copy(context, affected_settings=affected_settings, allowed_scenes=allowed_scenes)
        return {'FINISHED'}


if __name__ == "__main__":
    bpy.ops.scene.render_copy_settings()
