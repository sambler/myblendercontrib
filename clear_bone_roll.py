#
#    Copyright (c) 2016 Shane Ambler
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

# made in response to
# http://blender.stackexchange.com/q/48125/935
# this re-creates an operator added to blender on 3/3
# which may be too late to be included in the 2.77 release
# so may not be available until the next release.
# this addon fills the gap until then.

import bpy, math

bl_info = {
    "name": "Clear bone roll",
    "author": "sambler",
    "version": (1,0),
    "blender": (2, 62, 0),
    "location": "Alt-R while editing an armature",
    "description": "Clear the roll of selected bones",
    "warning": "",
    "wiki_url": "https://github.com/sambler/addonsByMe/blob/master/clear_bone_roll.py",
    "tracker_url": "https://github.com/sambler/addonsByMe/issues",
    "category": "Rigging",
}

class ClearBoneRoll(bpy.types.Operator):
    """Clear Roll of selected bones"""
    bl_idname = 'armature.clear_roll'
    bl_label = 'Clear Roll'
    bl_options = {'REGISTER', 'UNDO'}

    roll = bpy.props.FloatProperty(name='Roll', default=0.0,
                subtype='ANGLE', unit='ROTATION',
                min=math.radians(-360), max=math.radians(360))

    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'ARMATURE' \
                and context.active_object.mode == 'EDIT'

    def execute(self, context):
        for b in context.selected_bones:
            b.roll = self.roll
        return {'FINISHED'}


def menu_item(self, context):
    self.layout.operator(ClearBoneRoll.bl_idname)

addon_keymaps = []

def register():
    bpy.utils.register_class(ClearBoneRoll)

    if bpy.app.background: return

    bpy.types.VIEW3D_MT_edit_armature_roll.append(menu_item)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new('Armature', space_type='EMPTY')
        kmi = km.keymap_items.new('armature.clear_roll',
                    'R', 'PRESS', alt=True)
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.types.VIEW3D_MT_edit_armature_roll.remove(menu_item)
    bpy.utils.unregister_class(ClearBoneRoll)

if __name__ == "__main__":
    register()
