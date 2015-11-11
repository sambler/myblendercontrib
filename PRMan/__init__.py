# ##### BEGIN MIT LICENSE BLOCK #####
#
# Copyright (c) 2011 Matt Ebb
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#
# ##### END MIT LICENSE BLOCK #####
import bpy
import sys

bl_info = {
    "name": "PRMan Render Engine",
    "author": "Brian Savery",
    "version": (0, 7, 0),
    "blender": (2, 74, 0),
    "location": "Info Header, render engine menu",
    "description": "RenderMan 20.0 integration",
    "warning": "",
    "category": "Render"}

from . import engine


class PRManRender(bpy.types.RenderEngine):
    bl_idname = 'PRMAN_RENDER'
    bl_label = "PRMan Render"
    bl_use_preview = True
    bl_use_save_buffers = True

    def __init__(self):
        self.render_pass = None

    def __del__(self):
        if hasattr(self, "render_pass"):
            if self.render_pass is not None:
                engine.free(self)

    # main scene render
    def update(self, data, scene):
        if(engine.ipr):
            return
        if self.is_preview:
            if not self.render_pass:
                engine.create(self, data, scene)
        else:
            if not self.render_pass:
                engine.create(self, data, scene)
            else:
                engine.reset(self, data, scene)

        engine.update(self, data, scene)

        # add in the update_handler
        if engine.update_timestamp not in bpy.app.handlers.scene_update_pre:
            bpy.app.handlers.scene_update_pre.append(engine.update_timestamp)

    def render(self, scene):
        if self.render_pass is not None:
            engine.render(self)


def register():
    from . import ui
    from . import preferences
    from . import properties
    from . import operators
    from . import nodes
    preferences.register()
    properties.register()
    operators.register()
    ui.register()
    nodes.register()
    bpy.utils.register_module(__name__)


def unregister():
    if engine.update_timestamp in bpy.app.handlers.scene_update_pre:
        bpy.app.handlers.scene_update_pre.remove(engine.update_timestamp)

    from . import ui
    from . import preferences
    from . import properties
    from . import operators
    from . import nodes

    preferences.unregister()
    properties.unregister()
    operators.unregister()
    ui.unregister()
    nodes.unregister()
    bpy.utils.unregister_module(__name__)
