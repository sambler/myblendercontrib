#
#    Copyright (c) 2017 Shane Ambler
#
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

# made in response to -
# https://blender.stackexchange.com/q/89821/935

bl_info = {
    "name": "Image zoom",
    "author": "sambler",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "UV/Image Editor",
    "description": "Display the current zoom used in the image editor.",
    "warning": "",
    "wiki_url": "https://github.com/sambler/addonsByMe/blob/master/image_zoom_display.py",
    "tracker_url": "https://github.com/sambler/addonsByMe/issues",
    "category": "UV",
    }

# while the UV category is misleading, it is the one already in use
# for the UV\Image Editor

import bpy
import math

class Image_PT_zoom(bpy.types.Panel):
    bl_idname = "Image_PT_zoom"
    bl_label = "Image Zoom"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        zoom = context.space_data.zoom[0]*100
        zoom_h = context.space_data.zoom[1]*100
        if math.isclose(zoom,zoom_h,rel_tol=0.001):
            self.layout.label(text="{:.1f}%".format(zoom))
        else:
            self.layout.label(text="Width:  {:.1f}%".format(zoom))
            self.layout.label(text="Height: {:.1f}%".format(zoom_h))

def scale_header(self, context):
    zoom = context.space_data.zoom[0]*100
    self.layout.label(text="{:.1f}%".format(zoom))

def register():
    bpy.utils.register_class(Image_PT_zoom)
    # adding this will display the scale in the header
    # also uncomment the remove in unregister
    # having this in place fails to update automatically,
    # you need to move the mouse over the header to update it
    #bpy.types.IMAGE_HT_header.prepend(scale_header)
    # prepend puts it at the left, change to append to have it on the right

def unregister():
    bpy.utils.unregister_class(Image_PT_zoom)
    #bpy.types.IMAGE_HT_header.remove(scale_header)

if __name__ == "__main__":
    register()
