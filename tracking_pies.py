bl_info = {
"name": "Tracking Pies",
"author": "Sebastian Koenig",
"version": (1, 0),
"blender": (2, 7, 2),
"location": "Clip Editor > Masking Pies",
"description": "Pie Controls for Tracking",
"warning": "",
"wiki_url": "",
"tracker_url": "",
"category": "Movie Tracking"}

'''
This script adds tracking pies to the clip editor.
Hotkeys:
Q:      Marker Setup
W:      Setup Clip and Display options
E:      Tracking commands
Shift+S: Solving  
Shift+W: Scene Reconstruction
OSkey+A: Playback and frame jumping commands
'''


import bpy
from bpy.types import Menu



class CLIP_marker_pie(Menu):
    # Settings for the individual markers
    bl_label = "Marker Settings"
    bl_idname = "clip.marker_pie"

    def draw(self, context):

        layout = self.layout
        clip = context.space_data.clip
        settings = clip.tracking.settings
        active = clip.tracking.tracks.active

        pie = layout.menu_pie()

        op = pie.operator("wm.context_set_enum", text="Loc", icon="OUTLINER_DATA_EMPTY")
        op.data_path="space_data.clip.tracking.tracks.active.motion_model"
        op.value="Loc"
        op = pie.operator("wm.context_set_enum", text="Affine", icon="OUTLINER_DATA_LATTICE")
        op.data_path="space_data.clip.tracking.tracks.active.motion_model"
        op.value="Affine"

        if clip.tracking.tracks.active.use_blue_channel:
            pie.prop(active, "use_blue_channel", text="Blue Channel (ON)", icon="FILTER")
        else:
            pie.prop(active, "use_blue_channel", text="Blue Channel (OFF)", icon="FILTER")
        pie.operator("clip.track_settings_as_default", icon="SETTINGS")

        if clip.tracking.tracks.active.use_normalization:
            pie.prop(active, "use_normalization", text="Normalization (ON)", icon="IMAGE_ALPHA")
        else:
            pie.prop(active, "use_normalization", text="Normalization (OFF", icon="IMAGE_ALPHA")
        if clip.tracking.tracks.active.use_brute:
            pie.prop(active, "use_brute", text="Prepass (ON)", icon="FILTER")
        else:
            pie.prop(active, "use_brute", text="Prepass (OFF)", icon="FILTER")

        op = pie.operator("wm.context_set_enum", text="Match Previous", icon="KEY_HLT")
        op.data_path="space_data.clip.tracking.tracks.active.pattern_match"
        op.value="PREV_FRAME"
        op = pie.operator("wm.context_set_enum", text="Match Keyframe", icon="KEY_HLT")
        op.data_path="space_data.clip.tracking.tracks.active.pattern_match"
        op.value="KEYFRAME"
        
       
        


class CLIP_tracking_pie(Menu):
    # Tracking Operators
    bl_label = "Tracking"
    bl_idname = "clip.tracking_pie"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        
        prop = pie.operator("clip.track_markers", icon="PLAY_REVERSE")
        prop.backwards = True
        prop.sequence = True
        prop = pie.operator("clip.track_markers", icon="PLAY")
        prop.backwards = False
        prop.sequence = True
        
        pie.operator("clip.detect_features", icon="ZOOM_SELECTED")
        pie.operator("clip.disable_markers", icon="RESTRICT_VIEW_ON")

        pie.operator("clip.clear_track_path", icon="BACK").action="UPTO"
        pie.operator("clip.clear_track_path", icon="FORWARD").action="REMAINED"

        pie.operator("clip.refine_markers", icon="LOOP_BACK").backwards=True
        pie.operator("clip.refine_markers", icon="LOOP_FORWARDS").backwards=False



class CLIP_clipsetup_pie(Menu):
    # Setup the clip display options
    bl_label = "Clip and Display Setup"
    bl_idname = "clip.clipsetup_pie"

    def draw(self, context):
        layout = self.layout
        clip = context.space_data.clip
        sc = context.space_data

        pie = layout.menu_pie()

        pie.operator("clip.reload", text="Reload Footage", icon="FILE_REFRESH")
        pie.operator("clip.prefetch", text="Prefetch Footage", icon="LOOP_FORWARDS")
        
        pie.prop(sc, "use_mute_footage", text="Mute Footage", icon="MUTE_IPO_ON")
        if sc.clip_user.use_render_undistorted:
            pie.prop(sc.clip_user, "use_render_undistorted", text="Render Undistorted (ON)", icon="MESH_GRID")
        else:
            pie.prop(sc.clip_user, "use_render_undistorted", text="Render Undistorted (OFF)", icon="MESH_GRID")

        pie.prop(sc, "show_names", text="Show Track Info", icon="WORDWRAP_ON")
        pie.prop(sc, "lock_selection", text="Lock", icon="LOCKED")
        
        pie.prop(sc, "show_disabled", text="Show Disabled Tracks", icon="VISIBLE_IPO_ON")
        pie.prop(sc, "show_marker_search", text="Display Search Area", icon="EDIT_VEC")




class CLIP_solver_pie(Menu):
    # Operators to solve the scene
    bl_label = "Solving"
    bl_idname = "clip.solver_pie"

    def draw(self, context):
        layout = self.layout
        sc = context.space_data
        clip = context.space_data.clip
        settings = clip.tracking.settings

        pie = layout.menu_pie()

        pie.operator("clip.create_plane_track", icon="MESH_PLANE")
        pie.operator("clip.solve_camera", text="Solve Camera", icon="OUTLINER_OB_CAMERA")

        op= pie.operator("clip.clean_tracks", icon="STICKY_UVS_DISABLE")
        op.frames=15
        op.error=2
        if settings.use_tripod_solver:
            pie.prop(settings, "use_tripod_solver", text="Tripod Solver (ON)", icon="RESTRICT_RENDER_OFF")
        else:
            pie.prop(settings, "use_tripod_solver", text="Tripod Solver (OFF)", icon="RESTRICT_RENDER_ON")


        pie.operator("clip.set_solver_keyframe", text="Set Keyframe A", icon="KEY_HLT").keyframe='KEYFRAME_A'
        pie.operator("clip.set_solver_keyframe", text="Set Keyframe B", icon="KEY_HLT").keyframe='KEYFRAME_B'

        op = pie.operator("wm.context_set_enum", text="No refinement", icon="CAMERA_DATA")
        op.data_path="space_data.clip.tracking.settings.refine_intrinsics"
        op.value="NONE"
        op = pie.operator("wm.context_set_enum", text="Refine Focal Length", icon="CAMERA_DATA")
        op.data_path="space_data.clip.tracking.settings.refine_intrinsics"
        op.value="FOCAL_LENGTH"




class CLIP_reconstruction_pie(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Reconstruction"
    bl_idname = "clip.reconstruction_pie"


    def draw(self, context):

        clip = context.space_data.clip
        settings = clip.tracking.settings
        layout = self.layout

        pie = layout.menu_pie()
  
        pie.operator("clip.set_scale", text="Set Scale", icon="ARROW_LEFTRIGHT")
        pie.operator("clip.setup_tracking_scene", text="Setup Tracking Scene", icon="SCENE_DATA")
  
        pie.operator("clip.set_plane", text="Setup Floor", icon="MESH_PLANE")
        pie.operator("clip.set_origin", text="Set Origin", icon="MANIPUL")
  
        pie.operator("clip.set_axis", text="Set X Axis", icon="AXIS_FRONT").axis="X"
        pie.operator("clip.set_axis", text="Set Y Axis", icon="AXIS_SIDE").axis="Y"



class CLIP_timecontrol_pie(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Time Control"
    bl_idname = "clip.timecontrol_pie"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
      
        pie.operator("screen.frame_jump", text="Jump to Startframe", icon="TRIA_LEFT").end=False
        pie.operator("screen.frame_jump", text="Jump to Endframe", icon="TRIA_RIGHT").end=True
      
        pie.operator("clip.frame_jump", text="Start of Track", icon="REW").position="PATHSTART"
        pie.operator("clip.frame_jump", text="End of Track", icon="FF").position="PATHEND"
      
        pie.operator("screen.animation_play", text="Playback Backwards", icon="PLAY_REVERSE").reverse=True
        pie.operator("screen.animation_play", text="Playback Forwards", icon="PLAY").reverse=False
      
        pie.operator("screen.frame_offset", text="Previous Frame", icon="TRIA_LEFT").delta=-1
        pie.operator("screen.frame_offset", text="Next Frame", icon="TRIA_RIGHT").delta=1






########## register ############


def register():
    bpy.utils.register_class(CLIP_tracking_pie)
    bpy.utils.register_class(CLIP_marker_pie)
    bpy.utils.register_class(CLIP_solver_pie)
    bpy.utils.register_class(CLIP_reconstruction_pie)
    bpy.utils.register_class(CLIP_clipsetup_pie)
    bpy.utils.register_class(CLIP_timecontrol_pie)


    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Clip', space_type='CLIP_EDITOR')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'Q', 'PRESS').properties.name = "clip.marker_pie"
    kmi = km.keymap_items.new('wm.call_menu_pie', 'W', 'PRESS').properties.name = "clip.clipsetup_pie"
    kmi = km.keymap_items.new('wm.call_menu_pie', 'E', 'PRESS').properties.name = "clip.tracking_pie"
    kmi = km.keymap_items.new('wm.call_menu_pie', 'S', 'PRESS', shift=True).properties.name = "clip.solver_pie"
    kmi = km.keymap_items.new('wm.call_menu_pie', 'W', 'PRESS', shift=True).properties.name = "clip.reconstruction_pie"

    km = wm.keyconfigs.addon.keymaps.new(name='Frames')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'A', 'PRESS', oskey=True).properties.name = "clip.timecontrol_pie"




def unregister():
    bpy.utils.unregister_class(CLIP_tracking_pie)
    bpy.utils.unregister_class(CLIP_marker_pie)
    bpy.utils.unregister_class(CLIP_clipsetup_pie)
    bpy.utils.unregister_class(CLIP_solver_pie)
    bpy.utils.unregister_class(CLIP_reconstruction_pie)
    bpy.utils.unregister_class(CLIP_timecontrol_pie)



    

if __name__ == "__main__":
    register()


