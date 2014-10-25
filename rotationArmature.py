#
#    Copyright (c) 2014 Shane Ambler
#
#    All rights reserved.
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are met:
#
#    1.  Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#    2.  Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
#    OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#    PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#    LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# made in response to --
# http://blender.stackexchange.com/q/18027
#
# Given an armature used for bvh import that contains only movement bones
# from a facial motion capture, this script will replace each of the moving bones
# with a new bone that only rotates and scales.
# This is to facilitate exporting to an app that doesn't support bone translations

## WARNING
# This is made to work with a particular rig, adjustments may need to be made
# to work with other rigs.
# Most likely change will be setting the name of parent_bone

bl_info = {
    "name": "Rotation Armature",
    "author": "sambler",
    "version": (1,0),
    "blender": (2, 68, 0),
    "location": "View3D > Toolbar > Tools tab",
    "description": "Turn a movement based armature into rotation based",
    "warning": "May need to be adjusted for rig",
    "wiki_url": "https://github.com/sambler/addonsByMe/blob/master/rotationArmature.py",
    "tracker_url": "https://github.com/sambler/addonsByMe/issues",
    "category": "Rigging",
}

import bpy

class createRotationBones(bpy.types.Operator):
    """Create bones that follow existing moving bones but don't move"""
    bl_idname = "object.create_rotational_bones"
    bl_label = "Create rotational bones"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        # ********* ADJUST this as needed
        parent_bone = 'Markers'
        # *********
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bnames = [b.name for b in context.active_object.data.edit_bones if b.name != parent_bone]
        ebones = context.active_object.data.edit_bones
        basebone = ebones[parent_bone]

        # create new bones
        for bn in bnames:
            nb = ebones.new(name=bn+'.new')
            nb.head = basebone.tail
            nb.tail = ebones[bn].head
            nb.parent = basebone

        # add constraints
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        pbones = context.active_object.pose.bones

        for bn in bnames:
            nc = pbones[bn+'.new'].constraints.new(type='STRETCH_TO')
            nc.target = context.active_object
            nc.subtarget = bn
            nc.head_tail = 0.0

        # bake animation
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.nla.bake(frame_start=bpy.context.scene.frame_start,
            frame_end=bpy.context.scene.frame_end,
            only_selected=True,
            visual_keying=True,
            clear_constraints=True,
            bake_types={'POSE'})

        # remove old bones
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.object.select_pattern(pattern="*.new", extend=False)
        bpy.ops.object.select_pattern(pattern=parent_bone, extend=True)
        bpy.ops.armature.select_all(action='INVERT')
        bpy.ops.armature.delete()

        for bn in bnames:
            ebones[bn+'.new'].name = bn

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}


class rotationBonesPanel(bpy.types.Panel):
    """Provide steps to convert an armature"""
    bl_label = "Rotation Armature"
    bl_idname = "SCENE_PT_RotationArmature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator(createRotationBones.bl_idname, text=createRotationBones.bl_label)


def register():
    bpy.utils.register_class(createRotationBones)
    bpy.utils.register_class(rotationBonesPanel)

def unregister():
    bpy.utils.unregister_class(createRotationBones)
    bpy.utils.unregister_class(rotationBonesPanel)

if __name__ == "__main__":
    register()
