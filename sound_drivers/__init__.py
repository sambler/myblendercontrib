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


bl_info = {
    "name": "Sound Drivers",
    "author": "batFINGER",
    "location": "Properties > Speaker > Toolshelf",
    "description": "Drive Animations with baked sound files",
    "warning": "Still in Testing",
    "wiki_url": "http://wiki.blender.org/index.php/\
                User:BatFINGER/Addons/Sound_Drivers",
    "version": (3, 0),
    "blender": (2, 7, 6),
    "tracker_url": "",
    "support": 'TESTING',
    "category": "Animation"}

mods = ("screen_panels",
        "sounddriver",
        "driver_panels",
        "driver_manager",
        "speaker",
        "sound",
        "midi",
        "visualiser",
        "Equalizer",
        "EqMenu",
        "NLALipsync",
        "filter_playback",
        "utils",
        "graph",
        "BGL_draw_visualiser",
        "presets")

if "bpy" in locals():
    import imp
    for mod in mods:
        exec("imp.reload(%s)" % mod)


else:
    for mod in mods:
        exec("from . import %s" % mod)


import bpy
from bpy.types import  AddonPreferences
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.utils import register_class, unregister_class


class SpeakerToolsAddonPreferences(AddonPreferences):
    ''' Speaker Tools User Prefs '''
    bl_idname = "sound_drivers"

    temp_folder = StringProperty(
            name="Example File Path",
            subtype='DIR_PATH',
            )

    midi_support = BoolProperty(
            name = "Midi Support",
            description = "Enable Midi Support",
            default = False,
            )
    smf_dir = StringProperty(
            name="smf (midi) python path",
            description="folder where smf is installed",
            subtype='DIR_PATH',
            )
    audio_dir = StringProperty(
            name="Audio Files Folder",
            description="folder where audio files are",
            subtype='DIR_PATH',
            )
    driver_manager_update_speed = IntProperty(
                                  name="Driver Manager Update Speed",
                                  min=1,
                                  max=100,
                                  description="Update timer, lower value = faster updates, higher value slow self update use refresh",
                                  default=10)

    def draw(self, context):
        def icon(test):
            if test:
                icon = 'FILE_TICK'
            else:
                icon = 'ERROR'
            return icon

        layout = self.layout
        # check that automatic scripts are enabled
        UserPrefs = context.user_preferences
        paths = UserPrefs.filepaths
        dns = bpy.app.driver_namespace
        row = layout.row()
        row.prop(UserPrefs.system, "use_scripts_auto_execute")

        if not UserPrefs.system.use_scripts_auto_execute:
            row = layout.row()
            row.label("Warning Will not work unless Auto Scripts Enabled",
                      icon='ERROR')
            return
        row = layout.row()
        row.label("SoundDrive in Driver Namespace", icon=icon("SoundDrive" in
                                                              dns))
        row = layout.row()
        row.label("GetLocals in Driver Namespace", icon=icon("GetLocals" in
                                                              dns))
        test = "DriverManager" in dns
        row = layout.row()
        row.label("DriverManager Started", icon=icon(test))
        row = layout.row()
        if not test:
            row.operator("drivermanager.update")
        else:
            row.prop(self, "driver_manager_update_speed", slider=True)
        row = layout.row()
        row = layout.prop(self, "midi_support")
        # midi support
        if self.midi_support:
            row = layout.row()
            row.prop(self, "smf_dir")
            row = layout.row()
            op = row.operator("wm.url_open", icon='INFO', text="GitHub PySMF Project (Cython)")
            op.url="https://github.com/dsacre/pysmf"
            row = layout.row()
            if "smf" in locals():
                row.label("SMF IMPORTED OK...", icon='FILE_TICK')

            else:
                try:
                    import sys
                    sys.path.append(self.smf_dir)
                    import smf
                    row.label("SMF IMPORTED OK", icon='FILE_TICK')
                except:
                    row.label("SMF FAILED", icon ='ERROR')

        # end midi support
        row = layout.row()
        row.prop(self, "audio_dir", icon='SOUND')
        row = layout.row()
        row.prop(paths, "sound_directory", icon='SOUND')


def register():
    register_class(SpeakerToolsAddonPreferences)
    sounddriver.register()
    driver_panels.register()
    speaker.register()
    sound.register()
    midi.register()
    visualiser.register()
    Equalizer.register()
    EqMenu.register()
    NLALipsync.register()
    presets.register()
    graph.register()
    BGL_draw_visualiser.register()
    filter_playback.register()


def unregister():
    unregister_class(SpeakerToolsAddonPreferences)
    sounddriver.unregister()
    speaker.unregister()
    sound.unregister()
    midi.unregister()
    visualiser.unregister()
    driver_panels.unregister()
    Equalizer.unregister()
    EqMenu.unregister()
    NLALipsync.unregister()
    presets.unregister()
    graph.unregister()
    BGL_draw_visualiser.unregister()
    filter_playback.unregister()
