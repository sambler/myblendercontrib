# <pep8-80 compliant>
import bpy
from bpy.app.handlers import persistent
from bpy.props import *
from bpy.utils import preset_find, preset_paths
from bpy.types import PropertyGroup

from math import log, sqrt
from mathutils import Vector, Color
from sound_drivers.NLALipsync import SoundTools_LipSync_PT
from sound_drivers.presets import AddPresetSoundToolOperator
from bl_ui.properties_data_speaker  import DATA_PT_context_speaker, \
                DATA_PT_speaker, DATA_PT_cone, DATA_PT_distance, \
                DATA_PT_custom_props_speaker

from sound_drivers.utils import get_driver_settings,\
                icon_from_bpy_datapath, getSpeaker, getAction,\
                set_channel_idprop_rna, f, get_channel_index

from sound_drivers.filter_playback import setup_buffer, play_buffer,\
                mix_buffer
# add drivers to the namespace


@persistent
def InitSoundTools(dummy):
    dns = bpy.app.driver_namespace
    if "SoundDrive" not in dns:
        print("SoundDrive Added to drivers namespace")
        bpy.app.driver_namespace["SoundDrive"] = SoundDrive
    if "GetLocals" not in dns:
        dns["GetLocals"] = local_grabber
    handler = bpy.app.handlers.frame_change_pre
    handlers = [f for f in handler if f.__name__ == "live_speaker_view"]
    for f in handlers:
        handler.remove(f)
    handler.append(live_speaker_view)
    if dummy is not None:
        for speaker in bpy.data.speakers:
            speaker.filter_sound = False


def live_speaker_view(scene):
    '''
    Update the visualiser in the PROPERTIES Panel

    this can be very heavy when animating so check if needed

    '''

    if len(scene.soundspeakers) == 0:
        return None
    if scene is None:
        return None

    if scene.speaker is None:
        return None

    if 'VISUAL' not in scene.speaker.vismode:
        return None

    for area in bpy.context.screen.areas:
        if area.type == 'PROPERTIES':
            if not (area.spaces.active.pin_id is not None and area.spaces.active.pin_id == scene.speaker):
                if scene.objects.active is not None:
                    if scene.objects.active.type != 'SPEAKER':
                        return None
            if area.spaces.active.context == 'DATA':
                area.tag_redraw()

    return None

# DRIVER methods


def local_grabber(index, locs, dm):
    '''
    dns = bpy.app.driver_namespace
    dm = dns.get("DriverManager")
    '''
    #print("localgrabber")
    if dm is None:
        return 0.0
    ed = dm.find(index)

    if ed is not None:
        setattr(ed, "locs", locs)
        #print(ed.driven_object)
    return 0.0


def SoundDrive(channels, **kwargs):
    #print("SDLOCS:",locals())
    if isinstance(channels, float):
        channel = channels
    elif isinstance(channels, list):
        op = kwargs.get('op', 'avg')
        if op == 'avg':
            if len(channels) > 0:
                channel = sum(channels) / len(channels)
            else:
                channel = 0.0
        elif op in ['sum', 'min', 'max']:
            channel = eval("%s(channels)" % op)
    else:
        print("SoundDrive %f" % channel)
        return 0.0  # somethings gone wrong
    del(channels)

    value = kwargs.get('amplify', 1.0) * kwargs.get('norm', 1.0) * channel
    if 'threshold' not in kwargs.keys():
        return(value)
    if value > kwargs.get('threshold', 0.00):
        return(value)
    else:
        return(0.0)


def getrange(fcurve, tolerance):
    '''
    #get the minimum and maximum points from an fcurve

    REJECT = tolerance  # reject frequencty
    #print(len(fcurve.sampled_points))
    points = [0.0]
    for point in fcurve.sampled_points:
        # bake sound to fcurve returns some rubbish when the frequency
        # is out of range
        # often the only usable point is in the first
        if point.co[1] > -REJECT and point.co[1] < REJECT:
            points.append(point.co[1])
    #print(points)
    #print("GETRANGE",min(points),max(points))
    '''
    (minv, maxv), (min_pos, max_pos) = fcurve.minmax

    hasrange = abs(maxv - minv) > 0.01

    return hasrange, round(minv, 4), round(maxv, 4)


def SoundActionMenuRow(row, speaker, action, has_sound):
    if has_sound:
        col = row.column()
        col.alignment = 'LEFT'
        col.menu("soundtest.menu", text="", icon='SOUND')
    #col.alignment="LEFT"
    if action:
        col = row.column()
        col.prop(action, "name", emboss=True, text="")
    else:
        col = row.column()
        #col.label("NO SOUND BAKED")
        col.operator("speaker.visualise",
                     text="Bake %s" % speaker.sound.name)
    col = row.column()
    col.alignment = 'RIGHT'
    split = col.split()
    split.alignment = 'RIGHT'
    if not has_sound:
        return
    if action:
        split.prop(action, "use_fake_user",
                   toggle=True, text="F", emboss=True)
    op = split.operator("speaker.visualise", text="", icon='ZOOMIN')
    return(op)


class DataButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return getattr(context, "speaker", None) is not None\
               and getSpeaker(context) is not None


class OLDSoundVisualiserPanel(DataButtonsPanel, bpy.types.Panel):
    bl_label = " "
    bl_options = {'HIDE_HEADER'}
    #bl_space_type = "GRAPH_EDITOR"
    #bl_region_type = "UI"
    driver_index = 0

    def draw_header(self, context):
        layout = self.layout
        row = layout.row()
        layout.menu("soundtest.menu", text="Select Sound Action", icon='SOUND')

    def drawvisenum(self, context):
        speaker = getSpeaker(context)
        layout = self.layout
        row = layout.row()
        row.prop(speaker, 'vismode', expand=True, icon_only=True)

    def drawcontextspeaker(self, context):
        layout = self.layout
        ob = context.active_object
        speaker = getSpeaker(context)

        space = context.space_data
        row = layout.row(align=True)

        if not space.pin_id:
            row.template_ID(ob, "data")
        else:
            row.template_ID(space, "pin_id")

        if speaker.sound is not None:
            row = layout.row(align=True)
            sub = row.row()
            sub.alignment = 'LEFT'
            #use solo icon to show speaker has context
            if speaker.is_context_speaker:
                sub.prop(speaker, "is_context_speaker",
                         icon='SOLO_ON', text="", emboss=False)
            else:
                sub.prop(speaker, "is_context_speaker",
                         icon='SOLO_OFF', text="", emboss=False)

            row.label(speaker.sound.name)

    def draw(self, context):
        layout = self.layout
        sce = context.scene
        space = context.space_data
        speaker = getSpeaker(context)
        '''
        # Call menu executes the operator...
        row = layout.row()
        row.operator("wm.call_menu").name="speaker.preset_menu"
        row = layout.row()
        row.menu("speaker.preset_menu")

        '''
        nla = False
        action = None
        frame = sce.frame_current
        self.drawvisenum(context)
        '''
        if speaker.vismode == 'BAKE':
            return None
        '''
        self.drawcontextspeaker(context)

        return
        '''

            elif speaker.vismode == 'LIPSYNC':
                bpy.types.SoundTools_LipSync_PT.draw(self, context)
            #print("ACTION",action)
            #timemarkers = ['rest']

        '''


def test(self, context):
    if self.save_preset:
        if len(self.preset) == 0:
            self.save_preset = False
    return None


class DriverMenu(bpy.types.Menu):
    bl_idname = "sound_drivers.driver_menu"
    bl_label = "Select a Driver"

    def draw(self, context):
        print("draw")


def showFilterBox(layout, context, speaker, action):
    dns = bpy.app.driver_namespace
    if action:
        scene = context.scene
        minf = -1
        maxf = -1
        if "row_height" not in action.keys():
            return
        scale = action["row_height"]
        name = "Channel"
        if "Channels" in action:
            channels = action["Channels"]
            name = channel_name = action["channel_name"]
            minf = action["minf"]
            maxf = action["maxf"]
            MIN = action["min"]
            MAX = action["max"]
            start = action["start"]
            end = action["end"]
        else:
            channels = len(action.fcurves)
            minf = 0.0
            MIN = 0.0
            maxf = 0.0
            MAX = 0.0
            start = 0
            end = channels

        if start >= end:
            end = start + 1
        i = start
        box = layout
        row = box.row()
        row.prop(speaker, "filter_sound", toggle=True)
        #row = box.row()
        #row.prop(scene, "sync_play", toggle=True, text="PLAY", icon="PLAY")
        b = dns.get("ST_buffer")
        h = dns.get("ST_handle")
        if b and not h:
            row = layout.row()
            row.label("BUFFERING %s" % b, icon='INFO')
        if b:
            row = layout.row()
            row.label("BUFFERED %s" % b, icon='INFO')
        if h:
            row = layout.row()
            if not h.status:
                row.label("Handle %s" % h.status, icon='INFO')
            else:
                row.label("Handle.position %d %0.2fs" % (h.status, h.position),
                          icon='INFO')

        row = box.row()
        COLS = int(sqrt(channels))

        sound_channel_id = "%s__@__%s" % (speaker.name, action.name)
        sound_item = None
        from sound_drivers.filter_playback import  sound_buffer
        if sound_buffer:
            sound_item = sound_buffer.get(sound_channel_id)
        filter_item = scene.sound_channels.get(sound_channel_id)
        if filter_item is not None:
            '''
            row = box.row()
            row.prop(filter_item, "buffered")
            row = box.row()
            row.prop(filter_item, "valid_handle")
            '''
            for i in range(start, end + 1):
                cn = "channel%02d" % i
                #box.split(percentage=0.50)
                if not i % COLS:
                    row = box.row()
                col = row.column()
                #BUGGY on speaker object
                icon = 'OUTLINER_DATA_SPEAKER'
                if sound_item and sound_item.get(cn):
                    icon = 'OUTLINER_OB_SPEAKER'
                col.prop(filter_item,
                         cn,
                         text="%s" % i,
                         icon=icon,
                         toggle=True)


def action_normalise_set(self, context):
    # add normal envelope
    '''
    NONE : No normalisation  # all modifiers off
    ACTION: Normalised to ACTION  always modifier 0
    CHANNEL: Normalised to CHANNEL  always modifier 1
             (Note could make this
             one use previous, and factor or TOGGLE)
    '''
    scene = context.scene
    speaker = getSpeaker(context, action=self)
    # boo (bakeoptions) change. Add if doesn't exist.
    if "boo" not in self.keys():
        # set to default.
        self["boo"] = 'SOUND'
    if speaker is None:
        print("SPEAKER IS NONE")
        return None
    speaker_rna = self.get('rna')
    speaker_rna = eval(speaker_rna)

    def add_normal_envelope(fcurve, type):
        #print("RNA", self.speaker_rna)
        '''
        mods = [m for m in fcurve.modifiers if m.type == 'ENVELOPE']
        # remove mods (shouldn't be any)
        for m in mods:
            fcurve.modifiers.remove(m)
        '''
        m = fcurve.modifiers.new(type='ENVELOPE')
        # add a control point at start end
        for f in self.frame_range:
            cp = m.control_points.add(f)
            cp.min = self.normalise_range[0]
            cp.max = self.normalise_range[1]
        m.mute = True
        m.show_expanded = False
        return m

    def set_modifiers(type='ENVELOPE'):
        scene = context.scene
        #speaker = getSpeaker(context)
        for f in self.fcurves:
            channel = f.data_path.strip('[""]')
            touched = False
            while len(f.modifiers) < 2:
            # add muted envelope modifiers
                add_normal_envelope(f, type='ENVELOPE')
                touched = True
            for i, m in enumerate(f.modifiers):
                m.mute = True
                if self.normalise == 'NONE':
                    continue
                m.reference_value = 0.0
                m.default_min = self["min"]\
                                if i == 0 else speaker_rna[channel]["min"]
                m.default_max = self["max"]\
                                if i == 0 else speaker_rna[channel]["max"]

            low = speaker_rna[channel]["low"]
            high = speaker_rna[channel]["high"]
            sp_rna = speaker['_RNA_UI']

            map_range = Vector((self['min'], self['max']))
            if self.normalise == 'NONE':
                fc_range = Vector((speaker_rna[channel]['a'],
                                  speaker_rna[channel]['b']))
                '''
                speaker['_RNA_UI'][channel] = speaker_rna[channel]
                speaker['_RNA_UI']['a'] = self['min']
                speaker['_RNA_UI']['b'] = self['max']
                '''
                pass
            else:
                # could use the mods ID prop to get indexes
                if self.normalise == 'ACTION':
                    m = f.modifiers[0]
                    b = Vector(self.normalise_range).magnitude
                    fc_range = Vector((speaker_rna[channel]['a'],
                                      speaker_rna[channel]['b']))
                    a = map_range.magnitude
                    fc_range *= b / a
                    map_range = Vector(self.normalise_range)
                if self.normalise == 'CHANNEL':
                    m = f.modifiers[1]
                    fc_range = map_range = self.normalise_range
                for cp in m.control_points:
                    cp.min = self.normalise_range[0]
                    cp.max = self.normalise_range[1]

                m.mute = False

            set_channel_idprop_rna(channel,
                                   sp_rna,
                                   low,
                                   high,
                                   fc_range,
                                   map_range,
                                   is_music=(self["boo"] == 'MUSIC'))

        # flag the mods are added
        self["mods"] = True

    def change_range(self):
        pass

    def check_range(self):
        '''
        Check Envelope Modifier Range
        '''
        # check range
        if self.normalise_range[0] == self.normalise_range[1]:
            self.normalise_range[1] += 0.0000001
            return None
        if self.normalise_range[0] > self.normalise_range[1]:
            self.normalise_range[0] = self.normalise_range[1]
            return None

        elif self.normalise_range[1] < self.normalise_range[0]:
            self.normalise_range[1] = self.normalise_range[0]
            return None

    if True or not self.get('mods', False):
        set_modifiers(type='EVELOPE')

    #check_range(self)
    #normalise_action(speaker)
    bpy.ops.graph.view_all_with_bgl_graph()
    return None


def defaultPanels(regflag):
    if regflag:
        bpy.utils.register_class(DATA_PT_speaker)
        bpy.utils.register_class(DATA_PT_context_speaker)
        bpy.utils.register_class(DATA_PT_cone)
        bpy.utils.register_class(DATA_PT_distance)
        bpy.utils.register_class(DATA_PT_custom_props_speaker)
    else:
        bpy.utils.unregister_class(DATA_PT_speaker)
        bpy.utils.unregister_class(DATA_PT_context_speaker)
        bpy.utils.unregister_class(DATA_PT_cone)
        bpy.utils.unregister_class(DATA_PT_distance)
        bpy.utils.unregister_class(DATA_PT_custom_props_speaker)


def play_live(self, context):
    speakers = ModalTimerOperator.speakers
    if self.play:
        if self not in speakers:
            speakers.append(self)
    return None


class ModalTimerOperator(bpy.types.Operator):
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None
    speakers = []

    def modal(self, context, event):
        if event.type == 'ESC':
            return self.cancel(context)

        if event.type == 'TIMER':
            for speaker in ModalTimerOperator.speakers:
                speaker.vismode = speaker.vismode
        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        wm.modal_handler_add(self)
        ModalTimerOperator.speakers = [speaker
                                       for speaker in bpy.data.speakers
                                       if speaker.play == True]

        self._timer = wm.event_timer_add(0.1, context.window)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}


class SoundToolSettings(PropertyGroup):
    show_vis = BoolProperty(default=True, description="Show Visualiser")
    use_filter = BoolProperty(default=False,
                                 description="Filter Drivers")
    filter_object = BoolProperty(default=True,
                                 description="Filter Drivers by Objects")
    filter_context = BoolProperty(default=True,
                                  description="Filter Drivers by Context")
    filter_material = BoolProperty(default=True,
                                   description="Filter Drivers by Material")
    filter_monkey = BoolProperty(default=True,
                                 description="Filter Drivers by New (Monkeys)")
    filter_texture = BoolProperty(default=True,
                                  description="Filter Drivers by Texture")
    filter_world = BoolProperty(default=True,
                                description="Filter Drivers by World")
    filter_speaker = BoolProperty(default=True,
                                description="Filter Drivers by Speaker")
    context_speaker = StringProperty(default="None")


def speaker_channel_buffer(self, context):
    dns = bpy.app.driver_namespace

    #b = dns.get("ST_buffer")
    h = dns.get("ST_handle")
    b = dns["ST_buffer"] = mix_buffer(context)
    if h:
        h.stop()
    return None


class SoundChannels(PropertyGroup):
    name = StringProperty(default="SoundChannels")
    buffered = BoolProperty(default=False, description="Buffered")
    valid_handle = BoolProperty(default=False, description="Has Valid Handle")
    action_name = StringProperty(default="SoundChannels")
    pass

for i in range(96):
    setattr(SoundChannels,
            "channel%02d" % i,
            BoolProperty(default=(i == 0),
                         description="Channel %02d" % i,
                         update=speaker_channel_buffer))


def dummy(self, context):
    return None

    # check for modifiers
    mods = [mod for mod in self.modifiers if not mod.mute and mod.is_valid]
    if len(mods):
        #evaluate at frame
        v = [self.evaluate(p.co[0]) for p in col]
    else:
        #use the value at frame
        v = [p.co[1] for p in col]

    #print(v)
    _min = min(v)
    _max = max(v)
    return ((_min, _max), (v.index(_min), v.index(_max)))


def panel_items(self, context):
    # if is_baking then only show bake panel
    #print("PANEL ITEMS", self, context.scene)
    if bpy.types.BakeSoundPanel.baking:
        return [("BAKE", "BAKE", "Bake Sound to FCurves", 'FCURVE', 64)]
    
    pv = [("SPEAKER", "SPEAKER", "Edit Speaker properties", 'SPEAKER', 1),
          ("SOUND", "SOUND", "Edit sound properties", 'SOUND', 2)]
    if self.sound is not None:
        pv.extend([("BAKE", "BAKE", "Bake Sound to FCurves", 'FCURVE', 64)])
    if not getattr(self, "animation_data", None):
        pass
    else:
        if self.animation_data.action is not None:
            pv.extend([("VISUAL",
                        "VISUAL",
                        "Show sound visualiser",
                        'SEQ_HISTOGRAM', 16),
              ("ACTION", "ACTION", "Sound Action Properties", 'ACTION', 4),
              ("OUT", "OUT", "Filter Output", 'FILTER', 32)])

        if len(self.animation_data.nla_tracks) > 1:
            pv.extend([("NLA", "NLA", "NLA SoundTracks", 'NLA', 8)])
        '''
        pv = [("SPEAKER", "SPEAKER", "Edit Speaker properties",'SPEAKER',1),
              ("SOUND", "SOUND", "Edit sound properties",'SOUND',2),
              ("ACTION", "ACTION", "Sound Action Properties",'ACTION',4),
              ("NLA", "NLA", "NLA SoundTracks",'NLA',8),
              ("VISUAL", "VISUAL", "Show sound visualiser",'SEQ_HISTOGRAM',16),
              ("OUT", "OUT", "Filter Output",'FILTER',32),
              ("BAKE", "BAKE", "Bake Sound to FCurves",'FCURVE',64),]
        '''
    return pv


def register():
    defaultPanels(False)
    bpy.types.Scene.SoundToolsGUISettings =\
                BoolVectorProperty(name="GUI_Booleans",
                                   size=32,
                                   default=(False for i in range(0, 32)))

    bpy.types.Action.normalise = EnumProperty(items=(
                ('NONE', "None", "No Normalisation (As Baked)", 'BLANK', 0),
                ('CHANNEL', "Channel", "Normalise each CHANNEL", 'BLANK', 1),
                ('ACTION', "Action",
                 "Normalise to Maximumum Channel Value in ACTION", 'ACTION', 2)
                ),
                name="Normalise",
                default="NONE",
                description="Normalise to MIN MAX of Channel or Action",
                update=action_normalise_set,
                options={'HIDDEN'},
                )

    bpy.types.Action.normalise_range = FloatVectorProperty(default=(0, 1),
                                 size=2,
                                 description="Remap Action RANGE",
                                 update=action_normalise_set)

    bpy.types.Speaker.vismode = EnumProperty(items=panel_items,
                                name="SoundDriver",
                                description="Panel Filters",
                                options={'HIDDEN', 'ENUM_FLAG'})


    bpy.types.Action.vismode = EnumProperty(items=(
                ("SLIDER", "Sliders", "Display as Property Sliders"),
                ("VERTICAL", "Whitey",\
                 "Horizontal Icons (Vanishes on high channel count"),
                ("FCURVE", "Fcurve Colors",
                 "Horizontal Display of Fcurve colors")
                ),
                name="Visual Type",
                default="SLIDER",
                description="Visualisation Type",
                options={'HIDDEN'},
                )

    bpy.utils.register_class(SoundChannels)
    #BUGGY on SPEAKER object
    bpy.types.Scene.sound_channels = CollectionProperty(type=SoundChannels)

    bpy.types.Scene.play = BoolProperty("Play",
                default=True,
                description="Play Live")
                #update=dummy)

    bpy.utils.register_class(SoundToolSettings)
    bpy.types.Scene.speaker_tool_settings = \
            PointerProperty(type=SoundToolSettings)

    bpy.types.Action.show_freq = BoolProperty(default=True)
    #bpy.utils.register_class(ModalTimerOperator)
    bpy.utils.register_class(OLDSoundVisualiserPanel)
    bpy.app.handlers.load_post.append(InitSoundTools)
    if ("GetLocals" not in bpy.app.driver_namespace 
            or "SoundDrive" not in bpy.app.driver_namespace):
        InitSoundTools(None)


def unregister():
    #del(bpy.types.FCurve.minmax)
    defaultPanels(True)
    bpy.utils.unregister_class(SoundChannels)
    bpy.utils.unregister_class(OLDSoundVisualiserPanel)
    #bpy.utils.unregister_class(ModalTimerOperator)
    bpy.utils.unregister_class(SoundToolSettings)

    bpy.app.handlers.load_post.remove(InitSoundTools)
    dns = bpy.app.driver_namespace
    drivers = ["SoundDrive", "GetLocals", "DriverManager"]
    for d in drivers:
        if d in dns:
            dns.pop(d)
