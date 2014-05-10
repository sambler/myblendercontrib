## by Aldrik
## from http://blender.stackexchange.com/questions/1993/snap-a-bunch-of-keyframes-to-the-cursor/

# align keyframes to current frame without scaling all of them to the frame.
# eg. an action over 5 frames can be moved to the current frame - still taking 5 frames.

import bpy

class ANIM_OT_Align_frames(bpy.types.Operator):
    bl_idname = "action.align_frames"
    bl_label = "Align selected keys around current frame"
    bl_options = {"REGISTER", "UNDO",}

    align_end = bpy.props.BoolProperty(name="Align End")

    def execute(self, context):
        if context.space_data.type in ("DOPESHEET_EDITOR", "GRAPH_EDITOR",):
            points = []
            if context.space_data.dopesheet.show_only_selected:
                objects = context.selected_objects
            else:
                objects = context.scene.objects
            for obj in objects:
                if hasattr(obj.animation_data, "action"):
                    for fcurve in obj.animation_data.action.fcurves:
                        if fcurve.lock or (fcurve.hide and context.space_data.type == "GRAPH_EDITOR"):
                            continue
                        for keyframe_point in fcurve.keyframe_points:
                            if keyframe_point.select_control_point:
                                points.append(keyframe_point)

            if points:
                current_frame = context.scene.frame_current
                x_positions = (p.co[0] for p in points)
                offset = max(x_positions) if self.align_end else min(x_positions)
                for point in points:
                    point.co[0] += current_frame - offset
                return {"FINISHED"}
        return {"CANCELLED"}

class ANIM_MT_Align(bpy.types.Menu):
    bl_label = "Align"
    bl_idname = "action.align_frames"

    def draw(self, context):
        layout = self.layout
        layout.operator("action.align_frames", text="Selection start to current frame").align_end=False
        layout.operator("action.align_frames", text="Selection end to current frame").align_end=True

def menu(self, context):
    self.layout.menu("action.align_frames") #, icon="ALIGN")

bpy.utils.register_class(ANIM_OT_Align_frames)
bpy.utils.register_class(ANIM_MT_Align)
bpy.types.DOPESHEET_MT_key.prepend(menu)
bpy.types.GRAPH_MT_key.prepend(menu)
