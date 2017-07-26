#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# made for https://blender.stackexchange.com/q/85049/935

bl_info = {
    "name": "Set Smooth",
    "author": "sambler",
    "version": (1, 0),
    "blender": (2, 75, 0),
    "location": "Render panel",
    "description": "Easily set smooth/flat shading to all objects.",
    "wiki_url": "https://github.com/sambler/addonsByMe/blob/master/set_smooth.py",
    "tracker_url": "https://github.com/sambler/addonsByMe/issues",
    "category": "Render",
    }

import bpy

class SetShading(bpy.types.Operator):
    bl_idname = 'object.set_shading'
    bl_label = 'Set shading of all objects'

    smooth = bpy.props.BoolProperty()

    def execute(self, context):
        cur_selected = context.selected_objects.copy()
        bpy.ops.object.select_all(action='SELECT')
        if self.smooth:
            bpy.ops.object.shade_smooth()
        else:
            bpy.ops.object.shade_flat()
        bpy.ops.object.select_all(action='DESELECT')
        for o in cur_selected:
            o.select = True
        return {'FINISHED'}

def add_change_shading(self, context):
    self.layout.operator(SetShading.bl_idname, text='All smooth').smooth = True
    self.layout.operator(SetShading.bl_idname, text='All flat').smooth = False

def register():
    bpy.utils.register_class(SetShading)
    bpy.types.RENDER_PT_render.prepend(add_change_shading)

def unregister():
    bpy.types.RENDER_PT_render.remove(add_change_shading)
    bpy.utils.unregister_class(SetShading)

if __name__ == "__main__":
    register()
