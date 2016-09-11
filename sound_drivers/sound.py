import bpy
import time
from bpy.types import PropertyGroup, Panel, Operator, Menu
from bpy.props import *
from bpy.utils import register_class, unregister_class
from math import log, sqrt
from mathutils import Vector

from sound_drivers.Equalizer import showFilterBox, action_normalise_set
from sound_drivers import debug

from sound_drivers.utils import get_driver_settings,\
                icon_from_bpy_datapath, getSpeaker, getAction,\
                set_channel_idprop_rna, f, propfromtype,\
                get_channel_index, copy_sound_action, nla_drop,\
                validate_channel_name, unique_name, splittime,\
                get_context_area, replace_speaker_action

# validate_channel_name phase out
from sound_drivers.presets import notes_enum, note_from_freq,\
                freq_ranges, shownote

from sound_drivers.screen_panels import ScreenLayoutPanel

class Sound():
    def __init__(self, sound):
        pass


class BakeSoundGUIPanel():
    sd_operator = "wm.bake_sound_to_action"
    sd_operator_text = "BAKE"
    action = None
    baking = False
    status = []  # status of each fcurve
    bakeoptions = None
    current = 0
    report = ""
    wait = 0

    def draw_progress_slider(self, context):
        wm = context.window_manager
        layout = self.layout
        row = layout.row()
        row.scale_y = 0.4
        row.prop(wm, '["bake_progress"]', text="", slider=True, emboss=True)
        #WWWW

    def draw_fcurve_slider(self, context):
        layout = self.layout
        action = self.action
        channels = action["Channels"]
        row = layout.row()
        #row.scale_y = 0.5
        if action:
            cf = row.column_flow(columns=channels, align=True)
            cf.scale_y = 0.5
            for i in range(channels):
                fc = action.fcurves[i]
                if not fc.mute:
                    cf.prop(fc, "color", text="")

    def draw_current_fcurve_slider(self, context, i=0):
        channels = len(self.status)
        layout = self.layout
        action = self.action
        row = layout.row()
        if action:
            baked_channels = len([i for i in range(channels)
                                  if self.status[i]])
            pc = (baked_channels / channels)
            fc = action.fcurves[i]
            split = row.split(percentage=pc)
            split.prop(fc, "color", text="")
            split.scale_y = 0.5
            if self.wait:
                row = layout.row()
                tick = self.wait // 4
                if tick < 2:
                    row.label(str(pc), icon='INFO')
                else:
                    row.label(str(pc), icon='ERROR')


class SoundActionMethods:
    #icons = ['BLANK1', 'CHECKBOX_DEHLT', 'MESH_PLANE', 'ERROR']
    icons = ['BLANK1', 'CHECKBOX_DEHLT', 'MESH_PLANE', 'OUTLINER_OB_LATTICE']
    icontable = []
    vismode = 'NONE'

    @classmethod
    def poll(cls, context):

        if not hasattr(context, "speaker"):
            return False

        speaker = getSpeaker(context)
        action = getAction(speaker)

        return (context.speaker and speaker and action\
                and cls.vismode in speaker.vismode)

    def drawnormalise(self, context):
        layout = self.layout
        action = getAction(getSpeaker(context))
        row = layout.row(align=True)
        row.prop(action, "normalise", expand=True)
        row = layout.row()
        row.scale_y = row.scale_x = 0.5
        row.label("min: %6.2f" % action["min"])
        row.label("max: %6.2f" % action["max"])
        sub = layout.row()
        sub.enabled = action.normalise != 'NONE'
        sub.prop(action, "normalise_range", text="", expand=True)
        return

    def draw_tweaks(self, layout, context):

        scene = context.scene

        # Create a simple row.

        row = layout.row()
        '''
        row.context_pointer_set("scene", context.scene)
        row.context_pointer_set("area", context.screen.areas[0])
        row.context_pointer_set("window", context.window)
        row.context_pointer_set("screen", context.screen)
        row.context_pointer_set("region", context.screen.areas[0].regions[-1])
        op = row.operator("graph.clean")
        '''
        op = row.operator("soundaction.tweak", text="CLEAN")
        op.type = 'CLEAN'
        op = row.operator("soundaction.tweak", text="SMOOTH")
        op.type = 'SMOOTH'
        
        row = layout.row()
        #row.prop(op, "threshold")
        action = getAction(context.scene.speaker)
        for xx in action.tweaks:
            row = layout.row()
            row.label("[%s] %s " % (xx.channel_name, xx.type))

            #row.label("%.4f" % xx.threshold)
            row.label("%d" % xx.fcurve_count)
            row.label("%d" % xx.samples_count)
            row.label("%d" % xx.keyframe_count)
                    
    def nla_tracks(self, context):
        layout = self.layout
        speaker = getSpeaker(context)

        row = layout.row()
        if not getattr(speaker, "animation_data", None):
            row.label("NO ANITION DATA", icon='ERROR')
            return None
        row.prop(speaker.animation_data, "use_nla", toggle=True)
        if not speaker.animation_data.use_nla:
            return None
        l = len(speaker.animation_data.nla_tracks) - 1
        for i in range(l):
            nla_track = speaker.animation_data.nla_tracks[l - i]
            # need to fix for only strips with soundactions.. for R'ON
            row = layout.row()
            row = layout.row(align=True)
            for strip in nla_track.strips:
                action = strip.action
                ch = action.get("channel_name")
                if ch is None:
                    continue
                sub = row.row()
                sub.alignment = 'LEFT'
                op = sub.operator("soundaction.change", text=ch)
                op.action = strip.action.name
                sub.enabled = action != speaker.animation_data.action

                #sub.label(strip.action["channel_name"])
                if not nla_track.mute:
                    icon = "MUTE_IPO_OFF"
                else:
                    icon = "MUTE_IPO_ON"
                row.prop(action, "normalise_range", text="", expand=True)
                row.prop(nla_track, "mute",  icon=icon,
                         text="", icon_only=True)

    def copy_action(self, context):
        speaker = getSpeaker(context)
        sound = speaker.sound
        bakeoptions = sound.bakeoptions
        scene = context.scene
        layout = self.layout
        row = layout.row(align=True)
        sub = row.row()
        sub.scale_x = 2

        channels = [c for sp in scene.objects if sp.type == 'SPEAKER' for c in sp.data.channels]
        new_channel_name = unique_name(channels, bakeoptions.channel_name)
        op = sub.operator("soundaction.copy", text="Copy to Channel %s" % new_channel_name)
        op.new_channel_name = new_channel_name
        '''
        row = layout.row()
        op = row.operator("sound.bake_animation")
        row = layout.column()
        row.prop(scene, "sync_mode", expand=True)
        '''
        return

    def FCurveSliders(self, context):
        layout = self.layout
        speaker = getSpeaker(context)
        action = getAction(speaker)
        if not (action and speaker):
            return None

        channel_name = action["channel_name"]

        start = action["start"]
        end = action["end"]
        box = layout.box()
        #row  = box.row()
        #box.scale_y = 0.4
        cf = box.column_flow(columns=1)
        #cf.scale_y = action["row_height"]
        fcurves = action.fcurves
        for i in range(start, end + 1):
            channel = "%s%d" % (channel_name, i)
            v = speaker[channel]
            MIN = speaker["_RNA_UI"][channel]['min']
            MAX = speaker["_RNA_UI"][channel]['max']
            diff = MAX - MIN
            pc = 0.0
            if diff > 0.0000001:
                pc = (v - MIN) / diff
            #row = cf.row()
            #row.scale_y = action["row_height"]
            if pc < 0.00001:
                split = cf.split(percentage=0.0001)
                split.scale_y = action["row_height"]
                split.label("")
                continue
            split = cf.split(percentage=pc)
            split.scale_y = action["row_height"]
            split.prop(fcurves[i], "color", text="")
        row = box.row()
        row.scale_y = 0.2
        row.label(icon='BLANK1')

    def ColSliders(self, context):
        layout = self.layout
        speaker = getSpeaker(context)
        action = getAction(speaker)
        if not (action and speaker):
            return None

        channel_name = action["channel_name"]
        start = action["start"]
        end = action["end"]
        box = layout.box()
        #row  = box.row()
        #box.scale_y = 0.4
        cf = box.column()
        cf.scale_y = action["row_height"]
        for i in range(start, end + 1):
            channel = "%s%d" % (channel_name, i)
            cf.prop(speaker, '["%s"]' % channel, slider=True,
                       emboss=True, text="")

    def Sliders(self, context):
        layout = self.layout
        speaker = getSpeaker(context)
        action = getAction(speaker)
        if not (action and speaker):
            return None

        channel_name = action["channel_name"]
        start = action["start"]
        end = action["end"]
        box = layout.box()
        #row  = box.row()
        #box.scale_y = 0.4
        cf = box.column_flow(columns=1)
        cf.scale_y = action["row_height"]
        for i in range(start, end + 1):
            channel = "%s%d" % (channel_name, i)
            # TODO ADDED with MIDI
            if channel not in speaker.keys():
                continue
            cf.prop(speaker, '["%s"]' % channel, slider=True,
                       emboss=True, text="")


    def EBT(self, context):
        layout = self.layout
        speaker = getSpeaker(context)
        action = getAction(speaker)
        # max and min of whole action

        def icon(ch, pc):
            cn = action["channel_name"]
            chi = "%s%d" % (cn, ch)
            mn = speaker['_RNA_UI'][chi]["min"]
            mx = speaker['_RNA_UI'][chi]["max"]
            vol_range = Vector((mx, mn)).magnitude
            mx = max(mn, mx)
            b = speaker['_RNA_UI'][chi]["b"]
            a = speaker['_RNA_UI'][chi]["a"]
            map_range = Vector((a, b)).magnitude
            v = map_range * abs(speaker[chi]) / vol_range

            o = 0  # no output
            if v >= vol_range * pc:
                o = 3
            elif  pc * vol_range < (abs(map_range)):
                o = 1
                #return 'CHECKBOX_DEHLT'
            return o

        # create a list channels x 10
        channels = action["Channels"]
        #row = layout.row()

        self.icontable = [[icon(j, (i + 1) / 20.0)
                           for i in range(20)]
                          for j in range(channels)]
        for l in self.icontable:
            i = l.count(3)
            if i:
                l[i - 1] = 2
        '''
        # horizontal
        cf = self.column_flow(columns=10, align=True)
        cf.scale_y = 0.4
        for i in range(10):
            for j in range(channels):
                cf.label(text='', icon=icontable[j][i])
        '''
        row = layout.box()
        row.scale_x = 0.5

        #row = row.row()
        cf = row.column_flow(columns=channels + 1)
        cf.scale_y = action["row_height"]
        cf.scale_x = action["row_height"]

        for j in range(channels + 1):
            if j == channels:
                for i in range(19, -1, -1):
                    cf.label("")
                continue
            for i in range(19, -1, -1):
                #col.label(text='', icon=self.icons[self.icontable[j][i]])
                cf.label(text='', icon=self.icons[self.icontable[j][i]])


class SoundPanel(Panel):
    bl_label = "Sound"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    #Open this one to see the big OPEN SOUND button
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        speaker = getSpeaker(context)

        return (speaker and 'SOUND' in speaker.vismode)

    def draw_header(self, context):
        layout = self.layout
        layout.label("", icon='SOUND')

    def draw(self, context):
        layout = self.layout
        layout.enabled = not BakeSoundPanel.baking
        # get speaker returns the PROPERTIES PANEL speaker
        speaker = getSpeaker(context)
        # refactored code
        box = layout
        has_sound = (speaker.sound is not None)
        if not has_sound:
            row = box.row()
            row.template_ID(speaker, "sound", open="sound.open_mono")
            return

        row = box.row(align=True)

        if 'SOUND' in speaker.vismode:
            soundbox = box.box()
            row = soundbox.row(align=True)
            row.template_ID(speaker, "sound", open="sound.open_mono")
            sub = row.row()
            sub.alignment = 'RIGHT'
            sub.prop(speaker, "muted", text="")
            row = soundbox.row()
            row.prop(speaker, "volume")
            row.prop(speaker, "pitch")

            box.label("Distance", icon='ARROW_LEFTRIGHT')
            distancebox = box.box()
            split = distancebox.split()

            col = split.column()
            col.label("Volume:")
            col.prop(speaker, "volume_min", text="Minimum")
            col.prop(speaker, "volume_max", text="Maximum")
            col.prop(speaker, "attenuation")

            col = split.column()
            col.label("Distance:")
            col.prop(speaker, "distance_max", text="Maximum")
            col.prop(speaker, "distance_reference", text="Reference")

            box.label("Cone", icon='MESH_CONE')
            conebox = box.box()
            split = conebox.split()
            col = split.column()

            col.label("Angle:")
            col.prop(speaker, "cone_angle_outer", text="Outer")
            col.prop(speaker, "cone_angle_inner", text="Inner")

            col = split.column()

            col.label("Volume:")
            col.prop(speaker, "cone_volume_outer", text="Outer")


class SoundVisualiserPanel(SoundActionMethods, Panel):
    bl_label = "Visualiser"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    vismode = 'VISUAL'
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        speaker = getSpeaker(context)
        if speaker is None:
            return False

        if context.space_data.pin_id is not None:
            if context.space_data.pin_id == speaker:
                return cls.vismode in speaker.vismode

        return (context.object.data == speaker and cls.vismode
                in speaker.vismode)

    def draw_header(self, context):
        layout = self.layout
        speaker = getSpeaker(context)
        action = getAction(speaker)
        if not action:
            layout.label("", icon='SEQ_HISTOGRAM')
            return

        op = layout.operator("action.visualiser", icon='SEQ_HISTOGRAM',
                             emboss=False, text="")
        op.action_name = action.name

    def draw(self, context):
        layout = self.layout
        layout.enabled = not BakeSoundPanel.baking
        speaker = getSpeaker(context)
        action = getAction(speaker)

        #checks
        if speaker.sound is None:
            layout.label("Speaker has No Sound", icon='INFO')
            return
        if action is None:
            layout.label("No Action Baked", icon='INFO')
            return
        elif action is None:
            layout.label("No Action Baked", icon='INFO')
            return
        elif action['wavfile'] != speaker.sound.name:
            layout.label("No Action Baked", icon='INFO')
            layout.label("for %s" % speaker.sound.name)
            return
        '''
        layout.label(repr(action))
        if action:
            layout.label(action['wavfile'])

        '''
        if not BakeSoundPanel.baking:
            if action.vismode == 'SLIDER':
                self.Sliders(context)
            elif action.vismode == 'FCURVE':
                self.FCurveSliders(context)
            elif action.vismode == 'VERTICAL':
                self.EBT(context)
            elif action.vismode == 'TABSTER':
                self.EBT(context)

            #self.ColSliders(context)


class SoundActionPanel(SoundActionMethods, Panel):
    bl_label = "Sound Action"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    vismode = 'ACTION'
    #bl_options = {'DEFAULT_CLOSED'}

    def SoundActionMenu(self, context, speaker=None,
                        action=None, has_sound=True):
        speaker = getSpeaker(context)
        action = getAction(speaker)
        layout = self.layout
        if action is None:
            layout.label("NO ACTION", icon='INFO')
            return
        channel_name = action.get("channel_name")
        if channel_name is None:
            return
        row = layout.row(align=True)
        if has_sound:
            sub = row.row()
            sub.alignment = 'LEFT'
            #col.alignment = 'LEFT'
            sub.menu("soundtest.menu", text=channel_name)
            #sub = row.row()
            row.prop(action, "name", text="")
            sub = row.row()
            sub.alignment = 'RIGHT'
            sub.prop(action, "use_fake_user",
                       toggle=True, text="F")

    def draw_header(self, context):
        layout = self.layout
        layout.label("", icon='ACTION')

    def draw(self, context):
        layout = self.layout
        layout.enabled = not BakeSoundPanel.baking
        speaker = getSpeaker(context)
        action = getAction(speaker)
        self.SoundActionMenu(context)

        row = layout.row(align=True)
        self.drawnormalise(context)
        self.copy_action(context)
        row = layout.row()
        enabled = getattr(context.active_object, "data", None) == speaker
        if enabled:
            row=layout.row()
            op = row.operator("soundaction.unbake")
            if bpy.ops.soundaction.rebake.poll() :
                col = layout.column()
                self.draw_tweaks(col, context)
            row=layout.row()
            row.operator("soundaction.rebake")
        else:
            row = layout.row()
            row.label("Select Speaker to (un)(re)bake", icon='INFO')


class SoundNLAPanel(SoundActionMethods, Panel):
    bl_label = "NLA Mixer Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        speaker = getSpeaker(context)

        return (speaker
                and hasattr(speaker, "animation_data")
                and 'NLA' in speaker.vismode)

    def draw_header(self, context):
        layout = self.layout
        layout.label("", icon='NLA')

    def draw(self, context):
        layout = self.layout
        layout.enabled = not BakeSoundPanel.baking
        self.nla_tracks(context)


class FilterSoundPanel(Panel):
    bl_label = "Filter Sound"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        speaker = getSpeaker(context)

        return (speaker and 'OUT' in speaker.vismode)

    def draw_header(self, context):
        layout = self.layout
        layout.label("", icon='FILTER')

    def draw(self, context):
        layout = self.layout
        layout.enabled = not BakeSoundPanel.baking
        speaker = getSpeaker(context)
        action = getAction(speaker)
        showFilterBox(layout, context, speaker, action)


class BakeSoundPanel(ScreenLayoutPanel, BakeSoundGUIPanel, Panel):
    bl_label = "Bake Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    sd_operator = "wm.bake_sound_to_action"
    sd_operator_text = "BAKE"
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        speaker = getSpeaker(context)
        if speaker is not None and 'BAKE' in speaker.vismode:
            return True

        return False

    def draw_area_operator(self, context, layout, index):
        speaker = getSpeaker(context)
        sound = speaker.sound
        op = layout.operator("wm.bake_sound_to_action", text="BAKE",
                             icon='FCURVE')
        op.sound_name = sound.name
        op.speaker_name = speaker.name
        op.area_index = index
        

    def draw_freqs(self, layout, bakeoptions):
        if bakeoptions.sound_type == 'MUSIC':
            layout.label('Note Range (From-To)', icon='SOUND')
            box = layout.box()
            row = box.row()
            row.prop(bakeoptions, "music_start_note", text="")
            row.prop(bakeoptions, "music_end_note", text="")
        else:
            layout.label("Frequencies")
            row = layout.row()
            cbox = row.box()
            crow = cbox.row(align=True)
            sub = crow.row()
            sub.alignment = 'LEFT'
            sub.prop(bakeoptions, "auto_adjust", text="", icon='AUTO')
            crow.prop(bakeoptions, "minf", text="")
            crow.prop(bakeoptions, "maxf", text="")
            sub = crow.row()
            sub.alignment = 'RIGHT'
            sub.scale_x = 0.5
            sub.prop(bakeoptions, "use_log", toggle=True, text="LOG")

    def draw_header(self, context):
        layout = self.layout
        layout.label("", icon='FCURVE')

    def draw(self, context):
        space = context.space_data
        layout = self.layout

        if self.baking:
            action = self.action
            #self.draw_progress_slider(context)

            row = layout.row()
            row.label("[%s] %s" % (action["channel_name"], action.name), icon='ACTION')
            self.draw_progress_slider(context)
            '''
            if channels > 24:
                i = getattr(self, "channel", 0)
                self.draw_current_fcurve_slider(context, i=i)
            else:
                self.draw_fcurve_slider(context)
            '''
            box = layout.box()
            if len(action.fcurves):
                row = box.row(align=False)
                i = getattr(self, "channel", 0)
                fc = action.fcurves[i]
                sub = row.row()
                sub.alignment = 'LEFT'
                sub.label(fc.data_path.strip('["]'))
                color = [c for c in fc.color]
                color.append(1.0)
                row.label("Baking...")
                sub = row.row()
                sub.alignment = 'RIGHT'
                sub.template_node_socket(color=color)

            box = layout.box()

            if len(self.bake_times):
                row = box.row(align=False)
                i = getattr(self, "channel", 0)
                fc = action.fcurves[i]
                sub = row.row()
                sub.alignment = 'LEFT'
                sub.label(fc.data_path.strip('["]'))
                color = [c for c in fc.color]
                color.append(1.0)
                row.label("Baked")
                sub = row.row()
                sub.alignment = 'RIGHT'
                sub.template_node_socket(color=color)
                row = box.row(align=False)
                row.label(BakeSoundPanel.report)
                row = box.row()
                row.label("Baked in: %02d:%02d.%02d" % splittime(self.bake_times[-1]))
                row = box.row()
                te = sum(self.bake_times)
                abt = te / len(self.bake_times)
                channels = self.action.get("Channels", 0)
                tr = (channels - len(self.bake_times)) * abt

                row.label("Elapsed: %02d:%02d.%02d" % splittime(te))
                row.label("Remaining: %02d:%02d.%02d" % splittime(tr))
            #row.column_flow(columns=10, align=True)

            return None


        speaker = getSpeaker(context)
        sound = speaker.sound

        if sound is None:
            row = layout.row()
            row.label("No Sound to Bake", icon='INFO')
            return None

        scene = context.scene

        bakeoptions = sound.bakeoptions
        bake_operator = bakeoptions.bake_operator

        # Settings for bake sound to fcurve Operator
        if not self.baking:
            areas = [a.type for a in context.screen.areas]
            if 'GRAPH_EDITOR' in areas:
                area_index = areas.index('GRAPH_EDITOR')
                op = layout.operator("wm.bake_sound_to_action", text="BAKE",
                                icon='FCURVE')
                op.area_index = area_index
                op.sound_name = sound.name
                op.speaker_name = speaker.name
    
            elif len(areas) > 1:
                self.draw_area_buttons(context)
            else:
                op = layout.operator("wm.bake_sound_to_action", text="BAKE",
                                icon='FCURVE')
    
                op.sound_name = sound.name
                op.speaker_name = speaker.name

        ### TEST FOR SQUIZ
        action = None
        channels = 0
        if speaker.animation_data:
            action = speaker.animation_data.action
            if action is not None:
                channels = action["Channels"]


        #row.operator(self.bl_idname).preset = "FOOBAR"
        row = layout.row()
        
        col = layout.column_flow(align=True)
        col.label("Bake Options")
        row = col.row(align=True)
        row.menu("speaker.preset_menu",
                 text=getattr(bpy.types, "speaker.preset_menu").bl_label)
        row.operator("wm.soundtool_operator_preset_add", text="", icon='ZOOMIN')
        row.operator("wm.soundtool_operator_preset_add", text="", icon='ZOOMOUT').remove_active = True
        
        
        #row.prop(bakeoptions, "show_graph_editor", toggle=True, emboss=True)
        '''
        preset_box = row.box()
        row = preset_box.row()
        if len(bakeoptions.preset) == 0:
            txt = "Select Preset"
        else:
            txt = bakeoptions.preset
        row.menu("speaker.preset_menu", text=txt)
        row = preset_box.row()
        #row.prop(bakeoptions, "save_preset")
        preset_row = preset_box.row()
        preset_row.prop(bakeoptions, "preset")
        row = layout.row()
        row.menu("sound.music_notes")
        '''
        channels = [c for sp in context.scene.objects if sp.type == 'SPEAKER' for c in sp.data.channels]
        channel_name = unique_name(channels, "AA")
        row = layout.row()
        row.label("%s_%s_%s" % (bakeoptions.sound_type, channel_name, sound.name), icon='ACTION')
        abox = layout.box()
        arow = abox.row(align=True)
        arow.prop(bakeoptions, "sound_type", text="")

        arow.label(channel_name)
        #arow.prop(bakeoptions, "channel_name", text="")
        arow.label(sound.name)
        #arow.prop(bakeoptions, "action_name", text="") # REFACTO OUT

        row = layout.row()
        '''
        if not validate_channel_name(context):
            row.label("Channel in USE or INVALID", icon='ERROR')
            row.alert = True
            row = layout.row()

        '''
        #col.scale_x = row.scale_y = 2

        row.label("Channel")
        row = layout.row()
        box = row.box()
        #col.scale_x = row.scale_y = 2
        brow = box.row(align=True)
        #brow.prop(bakeoptions, "channel_name", text="Name")
        sub = brow.row()
        sub.prop(bakeoptions, "channels", text="")
        sub.enabled = bakeoptions.sound_type != 'MUSIC'
        row = layout.row()

        self.draw_freqs(layout, bakeoptions)
        row = layout.row()

        row.label("Bake Sound to F-Curves", icon='IPO')
        box = layout.box()
        #box.operator("graph.sound_bake", icon='IPO')
        box.prop(bake_operator, "threshold")
        box.prop(bake_operator, "release")
        box.prop(bake_operator, 'attack')
        box.prop(bake_operator, "use_additive", icon="PLUS")
        box.prop(bake_operator, "use_accumulate", icon="PLUS")

        row = box.row()

        split = row.split(percentage=0.20)
        split.prop(bake_operator, "use_square")
        split.prop(bake_operator, "sthreshold")
        #layout.prop(self, "TOL")


class SoundVisMenu(Menu):
    bl_idname = "soundtest.menu"
    bl_label = "Select a Sound"
    vismode = 'VISUAL'

    def draw(self, context):
        layout = self.layout
        speaker = getSpeaker(context)
        #speaker = context.scene.speaker
        #if SoundVisMenu.vismode in ["VISUAL", "SOUND", "DRIVERS"]:
        if True:
            actions = [action for action in bpy.data.actions
                       if "wavfile" in action
                       and action["wavfile"] == speaker.sound.name]

            
            for action in actions:
                if "channels" in action.keys(): # midi atm TODO
                    channels = action["channels"]
                    channels.sort()
                    layout.label("MIDI %s" %  action["wavfile"])
                    layout.separator()
                    groups = [g.name for g in action.groups]
                    groups.sort()
                    for channel in channels:
                        cn = groups[channels.index(channel)]
                        op = layout.operator("soundaction.change",
                             text="%s" % (cn))
                        op.action = action.name
                        op.channel = channel
                else:
                    layout.label("MUSIC %s" % action.name)
                    layout.separator()
                    channel = action["channel_name"]
                    op = layout.operator("soundaction.change",
                         text="%s" % (channel))
                    op.action = action.name


class SoundActionBaseOperator:
    sd_tweak_type = 'BAKED'

    def count_keyframes(self, action):
        keyframes = [len(fc.keyframe_points) for fc in action.fcurves]
        samples = [len(fc.sampled_points) for fc in action.fcurves]
        return sum(samples), sum(keyframes)

    def add_to_tweaks(self, action):
        tw = action.tweaks.add()  
        #tw.type = "COPIED FROM %s" % original_action.name
        tw.type = self.sd_tweak_type
        tw.samples_count, tw.keyframe_count = self.count_keyframes(action)
        tw.fcurve_count = len(action.fcurves)
        tw.channel_name = action.get("channel_name", "AA")
        

class VisualiserOptions(Operator):
    """Visualiser Options"""
    bl_idname = "action.visualiser"
    bl_label = "Visualiser Options"
    action_name = StringProperty(default="", options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=200)

    def execute(self, context):
        return {'FINISHED'}
        pass

    def draw(self, context):
        action = bpy.data.actions.get(self.action_name)
        layout = self.layout
        layout.label("Visualiser Settings", icon='SEQ_HISTOGRAM')
        col = layout.column()
        col.prop(action, "vismode", expand=True)
        row = layout.row(align=True)
        sub = row.row()
        sub.alignment = 'LEFT'
        sub.label("", icon='NLA')
        col = row.row()
        col.prop(action, '["row_height"]', text="h", slider=True)
        col = layout.row()
        col.prop(action, '["start"]', text="Start", slider=True)
        col.prop(action, '["end"]', text="  End", slider=True)



class SD_ReBakeTweak(SoundActionBaseOperator, Operator):
    bl_idname = "soundaction.tweak"
    bl_label = "Tweak"
    bl_options = {'REGISTER', 'UNDO'}
    ''' Pre Bake Clean / Smooth '''
    type=EnumProperty(items = (('CLEAN', 'CLEAN', 'CLEAN'),
                               ('SMOOTH', 'SMOOTH', 'SMOOTH')),
                      default = 'CLEAN',
                      )
    threshold = FloatProperty(default=0.0001, min=0.0001 , max=0.1, step=0.001) 
    def draw(self, context):
        layout = self.layout
        box = layout
        row = box.row()

        row = box.row()
        row.label(self.type)
        #box.seperate()
        if self.type == 'CLEAN':
            box.prop(self, "threshold", slider=True)
            
        #layout.operator("ed.undo_history")
        layout.operator(self.bl_idname, text="Done")

    def invoke(self, context, event):
        wm = context.window_manager
        if self.type in ['CLEAN']:
            return  wm.invoke_props_popup(self, event)
        else:
            return self.execute(context)
        #return  wm.invoke_popup(self)

    def execute(self, context): 
        action = getAction(context.scene.speaker)
        c = {}
        graph = get_context_area(context, c, 'GRAPH_EDITOR')
        '''
        c["area"] = graph
        c["screen"] = context.screen
        c["region"] = graph.regions[-1]
        c["window"] = context.window
        c["scene"] = context.scene
        '''
        #hs = action.tweaks.add()
        #hs.type = self.type
        
        if self.type == 'CLEAN':
            bpy.ops.graph.clean(c, threshold=self.threshold)
            print("clean")
            
            
            #hs.threshold = self.threshold
            
             
        elif self.type == 'SMOOTH':
            bpy.ops.graph.smooth(c)
            print("smooth")

            #hs.type = self.type       
        
        #hs.fcurve_count = len(action.fcurves)
        #hs.keyframe_count = count_keyframes(action)   
        self.sd_tweak_type = self.type
        self.add_to_tweaks(action)        
        return {'FINISHED'} 


class ChangeSoundAction(Operator):
    """Make Action Active"""
    bl_idname = "soundaction.change"
    bl_label = "Load Action"
    action = StringProperty(default="", options={'SKIP_SAVE'})
    channel = StringProperty(default="", options={'SKIP_SAVE'})

    def execute(self, context):
        #speaker = context.scene.speaker
        speaker = getSpeaker(context)
        if not speaker:
            return {'CANCELLED'}
        soundaction = bpy.data.actions.get(self.action)
        if soundaction is not None:
            SoundVisMenu.bl_label = soundaction["channel_name"]
            speaker.animation_data.action = soundaction
            if self.channel:
                # set channel for now TODO
                soundaction["channel_name"] = self.channel
            action_normalise_set(soundaction, context)

        dm = bpy.app.driver_namespace.get('DriverManager')
        if dm is not None:
            dm.set_edit_driver_gui(context)
        return {'FINISHED'}


class CopySoundAction(SoundActionBaseOperator, Operator):
    """Copy Action with new channel name"""
    bl_idname = "soundaction.copy"
    bl_label = "Action Copy"
    new_channel_name = StringProperty(default="AA")
    nla_drop = BoolProperty(default=True)
    sd_tweak_type = 'COPIED'

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None)

    def execute(self, context):
        speaker = getSpeaker(context)
        original_action = speaker.animation_data.action
        newaction = copy_sound_action(speaker, self.new_channel_name)
        channels = [c for sp in context.scene.objects if sp.type == 'SPEAKER' for c in sp.data.channels]

        if newaction is not None:
            speaker.animation_data.action = newaction
            speaker.sound.bakeoptions.channel_name =\
                    unique_name(channels, "AA")
                    #unique_name(channels, self.new_channel_name)

            if self.nla_drop:
                # need to override context to use.. cbf'd
                nla_drop(speaker, newaction, 1, self.new_channel_name)

            self.add_to_tweaks(newaction)
            #tw.type = "COPIED FROM %s" % original_action.name
            return {'FINISHED'}


        return {'CANCELLED'}



class UnbakeSoundAction(SoundActionBaseOperator, Operator):
    '''Unbake'''
    bl_idname = 'soundaction.unbake'
    bl_label = 'unBake to Key-frames'
    bl_description = 'Unbake to keyframes'
    bl_options = {'UNDO'}
    sd_tweak_type = 'UNBAKE'
    bake_all = BoolProperty(default=True, options={'SKIP_SAVE'})


    @classmethod

    def poll(cls, context):

        sp = getSpeaker(context)
        a = getAction(sp)
        samples = [1 for fc in a.fcurves if len(fc.sampled_points)]

        return len(samples)


    def execute(self, context):
        #unbake action
        speaker = getSpeaker(context)
        action = getAction(speaker)
        name = action.name
        print("-" * 72)
        print("Unbake action %s to keyframe points" % name)
        print("-" * 72)
        rna = speaker["_RNA_UI"]
        
        save_fcurve_select = [0] * len(action.fcurves)
        action.fcurves.foreach_get("select", save_fcurve_select)
        #action["max"] = -float("inf")
        #action["min"] = float("inf")
        channel_prefix = action["channel_name"]
        #keys.normalise = 'NONE'
        fcurves = [fc for fc in action.fcurves if len(fc.sampled_points)]
        sp_rna = speaker.get("_RNA_UI").to_dict()
        
        pts = [(fc, [(sp.co[0], fc.evaluate(sp.co[0])) for sp in fc.sampled_points]) for fc in fcurves if fc.select or self.bake_all]
        

        for fcu, fd in pts:
            dp = fcu.data_path
            i = fcu.array_index
            action.fcurves.remove(fcu)
            fc = action.fcurves.new(dp, index=i, action_group=channel_prefix)
            channel_name = dp.strip('["]')
            #fc.keyframe_points.foreach_set("co", [v for c in fd for v in c])
            for p in fd:
                w = fc.keyframe_points.insert(*p)

            
            is_music = False
            channel_rna = rna[channel_name]
            fc_range, points = fc.minmax
            low = channel_rna['low']
            high = channel_rna['high']
            (_min, _max) = fc_range
            if _min < action["min"]:
                action["min"] = _min
            if _max > action["max"]:
                action["max"] = _max

            set_channel_idprop_rna(channel_name,
                                   rna,
                                   low,
                                   high,
                                   fc_range,
                                   fc_range,
                                   is_music=is_music)

            sp_rna[channel_name] = channel_rna.to_dict()
            print("%4s %8s %8s %10.4f %10.4f" %\
                      (channel_name,\
                       f(low),\
                       f(high),\
                       fc_range[0],\
                       fc_range[1]))
        
        

        action['rna'] = str(sp_rna)
        action.normalise = 'NONE'
        action.fcurves.foreach_set("select", save_fcurve_select)
            
            
        #replace_speaker_action(speaker, action, keys)
        self.add_to_tweaks(speaker.animation_data.action)
        return{'FINISHED'}



class ReBakeSoundAction(SoundActionBaseOperator, Operator):
    bl_idname = 'soundaction.rebake'
    bl_label = 'ReBake to Samples'
    bl_description = 'Resample baked f-curve to a new Action / f-curve'
    bl_options = {'UNDO'}
    sd_tweak_type = 'REBAKE'
    bake_all = BoolProperty(default=True, options={'SKIP_SAVE'})


    @classmethod

    def poll(cls, context):

        sp = getSpeaker(context)
        a = getAction(sp)
        kfps = [1 for fc in a.fcurves if len(fc.keyframe_points)]

        return len(kfps)


    def finished(self, context):
        return {'FINISHED'}

    def execute(self, context):
        # rebake action using modifiers
        scene = context.scene
        speaker = getSpeaker(context)
        action = getAction(speaker)
        name = action.name
        print("-" * 72)
        print("Rebake  action %s to sampled points" % name)
        print("-" * 72)
        rna = speaker["_RNA_UI"]
        sp_rna = {}
        pts = [(c, [(sp.co[0], c.evaluate(sp.co[0])) for sp in c.keyframe_points]) for c in action.fcurves if c.select or self.bake_all]
        action.normalise = 'NONE'
        action["max"] = -float("inf")
        action["min"] = float("inf")

        start, end = action.frame_range[0], action.frame_range[1]

        for fc, sam in pts:
            
            #if self.RGB: fcu.color_mode = 'AUTO_RGB'
            
            for i, p in enumerate(sam):
                frame, v = p
                fc.keyframe_points[i].co.y = v
            
            fc.keyframe_points.update()

            channel_name = fc.data_path.strip('["]')
            
            is_music = False
            fc_range, points = fc.minmax
            low = rna[channel_name]['low']
            high = rna[channel_name]['high']
            (_min, _max) = fc_range
            if _min < action["min"]:
                action["min"] = _min
            if _max > action["max"]:
                action["max"] = _max

            set_channel_idprop_rna(channel_name,
                                   rna,
                                   low,
                                   high,
                                   fc_range,
                                   fc_range,
                                   is_music=is_music)
            sp_rna[channel_name] = rna[channel_name].to_dict()
            print("%4s %8s %8s %10.4f %10.4f" % (channel_name, f(low), f(high), fc_range[0], fc_range[1]))

        
            # ok now bake
            fc.convert_to_samples(start, end)
        
        self.add_to_tweaks(action)

        return{'FINISHED'}


class SD_ContinueBakeOperator(Operator):
    """Continue Baking"""
    bl_idname = "sounddrivers.continue_baking"
    bl_label = "Continue"


    def execute(self, context):
        BakeSoundPanel.wait = 2
        BakeSoundPanel.cancel_baking = False
        return {'FINISHED'}

class SD_CancelBakeOperator(Operator):
    """Cancel Baking"""
    bl_idname = "sounddrivers.cancel_baking"
    bl_label = "Cancel"


    def execute(self, context):
        BakeSoundPanel.cancel_baking = True
        return {'FINISHED'}

class BakeSoundAction(SoundActionBaseOperator, Operator):
    """Bake Multiple Sound Frequencies to Action"""
    bl_idname = "wm.bake_sound_to_action"
    bl_label = "Bake Sound"
    bl_options = {'INTERNAL'}
    sd_tweak_type = 'BAKE'

    _timer = None
    speaker_name = StringProperty(name="Speaker", default="Speaker")
    sound_name = StringProperty(name="Speaker", default="Sound")
    area_index = IntProperty(default=-1, options={'SKIP_SAVE'})
    count = 0
    channels = 0
    fp = None
    c = {}
    context_override = False
    baking = False
    baked = False
    sound = None
    speaker = None
    graph = None
    view3d = None
    _view3d = "VIEW_3D"
    change_last = False
    bakeorder = []
    #bake_times = []
    retries = []  # add channel here if it has no range.
    cancel_baking = False

    @classmethod
    def poll(cls, context):
        
        if getattr(context.space_data, "pin_id", None) is not None and context.space_data.pin_id != context.scene.objects.active.data:
            return False
        return True

    def channel_range(self):
        bakeoptions = self.sound.bakeoptions

        # get the channel
        channel = self.bakeorder[self.count]
        channels = bakeoptions.channels
        if bakeoptions.sound_type == 'MUSIC':
            return freq_ranges(bakeoptions.music_start_note,\
                               bakeoptions.music_end_note)[channel]

        if bakeoptions.use_log:
            # 0Hz is silence? shouldn't get thru trap anyway
            if bakeoptions.minf == 0:
                bakeoptions.minf = 1
            LOW = log(bakeoptions.minf, bakeoptions.log_base)
            HIGH = log(bakeoptions.maxf, bakeoptions.log_base)
            RANGE = HIGH - LOW
            low = LOW + (channel) * RANGE / channels
            high = LOW + (channel + 1) * RANGE / channels
            low = bakeoptions.log_base ** low
            high = bakeoptions.log_base ** high

        else:
            LOW = bakeoptions.minf
            HIGH = bakeoptions.maxf
            RANGE = HIGH - LOW
            low = LOW + (channel) * RANGE / channels
            high = LOW + (channel + 1) * RANGE / channels

        return (low, high)


    def modal(self, context, event):
        context.area.tag_redraw()
        wm = context.window_manager

        '''
        if BakeSoundPanel.wait > 0:
            debug.print("waiting", BakeSoundPanel.wait)
        '''

        def confirm_cancel(self, context):
            layout = self.layout
            layout.operator("sounddrivers.cancel_baking")
            layout.operator("sounddrivers.continue_baking")
        
        if BakeSoundPanel.cancel_baking:
            self.clean()
            return self.cancel(context)

        BakeSoundPanel.baking = True

        bakeoptions = self.sound.bakeoptions
        channels = bakeoptions.channels
        bake_operator = bakeoptions.bake_operator
        sound = self.sound
        speaker = self.speaker
        action = speaker.animation_data.action
        
        if event.type == 'ESC' or not BakeSoundPanel.baking:
            context.window_manager.popup_menu(confirm_cancel, title="Baking", icon='SOUND')
            BakeSoundPanel.wait = 1000000
            return {'PASS_THROUGH'}
            self.clean()
            return self.cancel(context)

        if BakeSoundPanel.wait > 0:
            BakeSoundPanel.wait -= 1
            return {'PASS_THROUGH'}

        if  self.count >= bakeoptions.channels:
            # Success do PostPro
            # return {'PASS_THROUGH'}
            return self.finished(context)

        if self.baking:
            return {'PASS_THROUGH'}

        if event.type == 'TIMER':
            if self.baking:
                return {'PASS_THROUGH'}
            #context.scene.frame_set(1)
            self.baking = True
            fc = action.fcurves[self.bakeorder[self.count]]

            channel = self.bakeorder[self.count]
            wm["bake_progress"] = 100 * self.count / channels
            setattr(BakeSoundPanel, "channel", channel)
            BakeSoundPanel.report = "[%s%d]" % (bakeoptions.channel_name,
                                                      channel)

            fc.select = True
            #FIXME FIXME FIXME
            fp = bpy.path.abspath(sound.filepath)
            low, high = self.channel_range()
            if not self.context_override or not self.graph:
                context.area.type = 'GRAPH_EDITOR'
                context.area.spaces.active.mode = 'FCURVES'
                self.c = context.copy()

            context.scene.frame_set(1)
            #context.area.type = 'GRAPH_EDITOR'

            t0 = time.clock()
            try:
                #x = bpy.ops.graph.sound_bake(

                x = bpy.ops.graph.sound_bake(self.c,
                             filepath=fp,
                             low=low,
                             high=high,
                             attack=bake_operator.attack,
                             release=bake_operator.release,
                             threshold=bake_operator.threshold,
                             use_accumulate=bake_operator.use_accumulate,
                             use_additive=bake_operator.use_additive,
                             use_square=bake_operator.use_square,
                             sthreshold=bake_operator.sthreshold)
            except:
                print("ERROR IN BAKE OP")
                '''
                for k in self.c.keys():
                    print(k, ":", self.c[k])

                '''
                return self.cancel(context)

            '''
            if self.graph:
                #bpy.ops.graph.view_all(self.c)
                bpy.ops.graph.view_all_with_bgl_graph()
            '''

            context.area.type = 'PROPERTIES'
            t1 = time.clock()
            BakeSoundPanel.bake_times.append(t1 - t0)

            fc_range, points = fc.minmax
            vol_range = abs(fc_range[1] - fc_range[0])
            # FIXME make retry count an addon var.
            if self.retries.count(channel) > channels // 5:
                print("TOO MANY RETRIES")
                self.clean()
                return self.cancel(context)
            if bakeoptions.auto_adjust\
                and (vol_range < 0.0001 or vol_range > 1e10):
                print("NO RANGE", vol_range)
                self.retries.append(channel)
                BakeSoundPanel.status[channel] = 99
                if channel == 0:
                    BakeSoundPanel.report = "[%s%d] NO Lo RANGE.. adjusting" \
                    % (bakeoptions.channel_name, channel)
                    bakeoptions.minf = high
                elif channel == (bakeoptions.channels - 1):
                    BakeSoundPanel.report = "[%s%d] NO Hi RANGE .. adjusting" \
                                       % (bakeoptions.channel_name, channel)
                    self.change_last == True
                    bakeoptions.maxf = low
                else:
                    BakeSoundPanel.wait = 20  # wait 2 seconds to continue
                    BakeSoundPanel.report = "[%s%d] NO Mid RANGE\
                            .. continuing" % (bakeoptions.channel_name,\
                                                      channel)
                    self.count += 1
                    bpy.ops.graph.view_all_with_bgl_graph()
                #need to set count down one
            else:
                BakeSoundPanel.status[channel] = 1
                # set up the rna
                rna = speaker["_RNA_UI"]
                channel_name = "%s%d" % (bakeoptions.channel_name, channel)

                is_music = bakeoptions.sound_type == 'MUSIC'
                set_channel_idprop_rna(channel_name,
                                       rna,
                                       low,
                                       high,
                                       fc_range,
                                       fc_range,
                                       is_music=is_music)

                print("%4s %8s %8s %10.4f %10.4f" %\
                          (channel_name,\
                           f(low),\
                           f(high),\
                           fc_range[0],\
                           fc_range[1]),\
                           end="")
                print(" %02d:%02d:%02d" % (splittime(t1 - t0)))
                BakeSoundPanel.report = rna[channel_name]["description"]\
                        .replace("Frequency", "")
                if channel == (bakeoptions.channels - 1)\
                        and self.change_last:
                    self.change_last = False
                    action.fcurves[0].mute = True
                    bakeorder[0], bakeorder[channels - 1] =\
                            bakeorder[channels - 1], bakeorder[0]
                    # need to swap n clear first fcurve
                    # mute the first fcurve
                _min, _max = fc_range
                if _min < action["min"]:
                    action["min"] = _min
                if _max > action["max"]:
                    action["max"] = _max
                self.count += 1

            fc.mute = not bool(BakeSoundPanel.status[channel])
            fc.select = False
            self.baking = False
            self.baked = True

        return {'PASS_THROUGH'}

    def execute(self, context):
        
        BakeSoundPanel.bake_times = []
        wm = context.window_manager
        wm_rnaui = wm.get("_RNA_UI")
        if wm_rnaui is None:
            wm_rnaui = wm["_RNA_UI"] = {}
            wm["_RNA_UI"]["bake_progress"] = {
                                              "min": 0.0,
                                              "soft_min":0.0,
                                              "hard_min":0.0,
                                              "soft_max":100.0,
                                              "hard_max":100.0,
                                              "max":100.0,
                                              "description": "Baking....",
                                              }
        wm["bake_progress"] = 0.0
        BakeSoundPanel.cancel_baking = False
        self.speaker = bpy.data.speakers.get(self.speaker_name)
        self.c = context.copy()
        self.first_baked = False
        self.last_baked = False
        self.sound = bpy.data.sounds.get(self.sound_name)
        if not (self.sound and self.speaker):
            return {'CANCELLED'}
        bakeoptions = self.sound.bakeoptions
        channels = [c for sp in context.scene.objects if sp.type == 'SPEAKER' for c in sp.data.channels]
        bakeoptions.channel_name = unique_name(channels, "AA") # AAAA
        self.retries = []

        if self.area_index > -1:
            '''
            self.view3d = get_context_area(context, {}, 'VIEW_3D',
                                  context_screen=True)
            '''
            self.view3d = context.screen.areas[self.area_index]
            self._view3d = self.view3d.type
            if self.view3d is not None:
                self.view3d.type = 'GRAPH_EDITOR'

        # NEEDS REFACTO to get BGL Graph Area if there is one
        self.graph = get_context_area(context,
                              self.c,
                              'GRAPH_EDITOR',
                              context_screen=(self.area_index != -1))

        self.context_override = self.graph is not None\
                and self.graph.spaces.active.mode != 'DRIVERS'

        if "_RNA_UI" not in self.speaker.keys():
            self.speaker["_RNA_UI"] = dict()

        context.scene.frame_set(1)
        channels = bakeoptions.channels

        # Create the action # might move this to see if one channel baked
        current_action = None
        if not self.speaker.animation_data:
            self.speaker.animation_data_create()
        elif self.speaker.animation_data.action:
            current_action = self.speaker.animation_data.action

        name = "%s_%s_%s" % (bakeoptions.sound_type, bakeoptions.channel_name, self.sound.name)

        action = bpy.data.actions.new(name)

        if current_action:
            #take some settings from last baked
            action.vismode = current_action.vismode

        action["Channels"] = channels
        action["channel_name"] = bakeoptions.channel_name
        action["minf"] = bakeoptions.minf
        action["maxf"] = bakeoptions.maxf
        action["use_log"] = bakeoptions.use_log
        action["wavfile"] = self.sound.name
        action["min"] = 1000000
        action["max"] = -1000000
        action["start"] = 0
        action["end"] = channels - 1

        #keep some UI stuff here too like the row height of each channel

        # use 0.4 as a default value
        action["row_height"] = 0.4
        action_rna = {}
        action_rna["row_height"] = {"min": 0.001,
                                    "max": 1.0,
                                    "description": "Alter the row height",
                                    "soft_min": 0.0,
                                    "soft_max": 1.0}
        action_rna["start"] = {"min": 0,
                               "max": 1.0,
                               "description": "Clip Start",
                               "soft_min": 0,
                               "soft_max": channels - 1}
        action_rna["end"] = {"min": 1,
                             "max": channels - 1,
                             "description": "Clip End",
                             "soft_min": 1,
                             "soft_max": channels - 1}

        action["_RNA_UI"] = action_rna
        #action["rna"] = str(action_rna)
        # set up the fcurves
        BakeSoundPanel.action = action
        BakeSoundPanel.wait = 0
        BakeSoundPanel.status = [0 for i in range(channels)]
        for i in range(channels):
            p = "%s%d" % (bakeoptions.channel_name, i)
            self.speaker[p] = 0.0
            fc = action.fcurves.new('["%s"]' % p, action_group=bakeoptions.channel_name)
            fc.select = False
            fc.mute = True

        bakeorder = [i for i in range(channels)]
        if channels > 1:
            bakeorder[1], bakeorder[channels - 1] = bakeorder[channels - 1],\
                                                    bakeorder[1]
        self.bakeorder = bakeorder

        self.speaker.animation_data.action = action
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        context.window_manager.modal_handler_add(self)
        self.wait = 30
        print("-" * 80)
        print("BAKING %s to action %s" % (self.sound.name, action.name))
        print("-" * 80)

        return {'RUNNING_MODAL'}

    def finished(self, context):
        # return to view3d

        if self.view3d is not None:
            self.view3d.type = self._view3d
        print("TOTAL BAKE TIME: %02d:%02d:%02d" %
                  splittime(sum(BakeSoundPanel.bake_times)))
        BakeSoundPanel.report = "Finished Baking"
        #context.area.header_text_set()
        # set up the rnas
        sp = self.speaker
        sound = self.sound
        action = sp.animation_data.action
        bakeoptions = sound.bakeoptions
        boo = bakeoptions.bake_operator
        # save non defaults to an ID prop.

        action['boo'] = bakeoptions.sound_type

        action['_RNA_UI']['boo'] = dict(boo.items())

        channel_name = action['channel_name']
        vcns = ["%s%d" % (channel_name, i) for i in
                range(bakeoptions.channels)]

        sp_rna = {k: sp['_RNA_UI'][k].to_dict()
                  for k in sp['_RNA_UI'].keys()
                  if k in vcns}

        action['rna'] = str(sp_rna)

        BakeSoundPanel.baking = False
        # drop the action into the NLA
        nla_drop(sp, action, 1, "%s %s" %(channel_name, channel_name))
        # normalise to action. This will set the
        action.normalise = 'ACTION'

        if context.scene.speaker is None:
            sp.is_context_speaker = True

        context.window_manager.event_timer_remove(self._timer)
        bpy.ops.graph.view_all_with_bgl_graph()
        self.add_to_tweaks(action)
        return {'FINISHED'}

    def clean(self):
        speaker = self.speaker
        action = speaker.animation_data.action
        if action:
            speaker.animation_data.action = None
            del(action["wavfile"])
            del(action["channel_name"])
            del(action["Channels"])
            for t in speaker.animation_data.nla_tracks:
                for s in t.strips:
                    if s.action == action:
                        #remove track
                        speaker.animation_data.nla_tracks.remove(t)
                        break
            if not action.users:
                bpy.data.actions.remove(action)

    def cancel(self, context):
        if self.view3d is not None:
            #self._view3d = self.view3d.type
            self.view3d.type = self._view3d

        BakeSoundPanel.report = "User Cancelled Cleaning..."
        BakeSoundPanel.baking = False
        
        #context.area.header_text_set()
        context.window_manager.event_timer_remove(self._timer)
        print("BAKING CANCELLED.")
        return None
        return {'CANCELLED'}


def get_dm():
    dns = bpy.app.driver_namespace
    dm = dns.get("DriverManager")
    return dm


def register():
    bakeop = bpy.types.GRAPH_OT_sound_bake
    propdic = {}
    propfromtype(propdic, bakeop)
    bakeprops = type("BakeFCProperties", (PropertyGroup,), propdic)

    register_class(bakeprops)
    propdic = {}
    sound_type = EnumProperty(items=(
                ("SOUND", "SOUND", "Basic Sound"),
                ("SFX", "SFX", "Sound Effects"),
                ("MUSIC", "MUSIC", "Music"),
                ("VOICE", "VOICE", "Voice"),
                #("MIDI", "MIDI", "Midi"),
                ),
                name="type",
                default="SOUND",
                description="Input Type",
                update=shownote
                )
    propdic["sound_type"] = sound_type

    propdic["preset"] = StringProperty(name="Preset",
                            default="",
                            #update=test,
                            options={'SKIP_SAVE'},
                            description="Save Preset")

    propdic["action_name"] = StringProperty(name="Action Name",
                                            default="SoundAction")

    propdic["channel_name"] = StringProperty(name="Channel Name",
                                             default="AA",
                              description="Limit Name to two Uppercase chars")

    propdic["channels"] = IntProperty(name="Channels",
                           default=16,
                           description="Number of frequencies to split",
                           min=1,
                           max=1000)
    propdic["minf"] = FloatProperty(name="Min Freq",
                         default=4.0,
                         description="Minimum Freq",
                         min=0,
                         max=10000.0)
    propdic["maxf"] = FloatProperty(name="Max Freq",
                         default=10000.0,
                         description="Maximum Freq",
                         min=100.0,
                         max=1000000.0)

    propdic["use_log"] = BoolProperty(name="Log Scale",
                           default=True,
                           description="Use Log scale for channels")

    '''
    # REFACTO................ OUT!!!!!!!!!!!!!!!!!
    propdic["show_graph_editor"] = BoolProperty(name="3DView to Graph",
           description="Change 3D view to Graph Editor to visualise bake",\
           default=True)
    '''
    propdic["music_start_note"] = notes_enum
    propdic["music_end_note"] = notes_enum

    # doh.. this is useless.
    propdic["log_base"] = IntProperty(name="log_base",
                           default=2,
                           description="log base to use",
                           min=2,
                           soft_min=2,
                           soft_max=32,
                           max=64)
    txt = "Automatically adjust end ranges for nill bake data"
    propdic["auto_adjust"] = BoolProperty(default=True, description=txt)

    propdic["bake_operator"] = PointerProperty(type=bakeprops)

    BakeOptions = type("BakeOptions", (PropertyGroup,), propdic)
    register_class(BakeOptions)


    dic = {"type": StringProperty(),
           "threshold": FloatProperty(default=0.0001, max=0.01),
           "keyframe_count": IntProperty(default=0),
           "fcurve_count": IntProperty(default=0),
           "samples_count": IntProperty(default=0),
           "channel_name": StringProperty(default='AA'),
           }

    SD_ActionPostPro = type("SD_ActionPostPro", (PropertyGroup,), dic)

    bpy.utils.register_class(SD_ActionPostPro)

    bpy.types.Action.tweaks = CollectionProperty(type=SD_ActionPostPro)    
    #Menus
    register_class(SoundVisMenu)

    # Operators
    register_class(ChangeSoundAction)
    register_class(CopySoundAction)
    register_class(BakeSoundAction)
    register_class(UnbakeSoundAction)
    register_class(ReBakeSoundAction)
    register_class(VisualiserOptions)

    bpy.types.Sound.bakeoptions = PointerProperty(type=BakeOptions)
    # Panels
    register_class(SoundPanel)
    register_class(SoundVisualiserPanel)
    register_class(SoundActionPanel)
    register_class(SoundNLAPanel)
    register_class(FilterSoundPanel)
    register_class(SD_CancelBakeOperator)
    register_class(SD_ContinueBakeOperator)
    register_class(BakeSoundPanel)
    register_class(SD_ReBakeTweak)

def unregister():
    unregister_class(SoundVisMenu)
    unregister_class(ChangeSoundAction)
    unregister_class(BakeSoundAction)
    unregister_class(UnbakeSoundAction)
    unregister_class(ReBakeSoundAction)
    unregister_class(SoundPanel)
    unregister_class(SoundVisualiserPanel)
    unregister_class(VisualiserOptions)
    unregister_class(SoundActionPanel)
    unregister_class(SoundNLAPanel)
    unregister_class(FilterSoundPanel)
    unregister_class(BakeSoundPanel)
    unregister_class(SD_CancelBakeOperator)
    unregister_class(SD_ContinueBakeOperator)
    unregister_class(CopySoundAction)
    unregister_class(SD_ReBakeTweak)
