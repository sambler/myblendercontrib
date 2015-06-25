# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# PEP8 compliant (https://www.python.org/dev/peps/pep-0008)

# ----------------------------------------------------------
# File: __init__.py
# Author: Antonio Vazquez (antonioya)
# ----------------------------------------------------------

# ----------------------------------------------
# Define Addon info 
# ----------------------------------------------
bl_info = {
    "name": "MeasureIt",
    "author": "Antonio Vazquez (antonioya)",
    "location": "View3D > Tools Panel /Properties panel",
    "version": (1, 4, 1),
    "blender": (2, 7, 4),
    "description": "Tools for measuring objects.",
    "category": "3D View"}

import sys
import os

# ----------------------------------------------
# Add to Phyton path (once only)
# ----------------------------------------------
path = sys.path
flag = False
for item in path:
    if "measureit" in item:
        flag = True
if flag is False:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'measureit'))
    print("measureit: added to phytonpath")

# ----------------------------------------------
# Import modules
# ----------------------------------------------
if "bpy" in locals():
    import imp

    imp.reload(measureit_main)
    print("measureit: Reloaded multifiles")
else:
    import measureit_main

    print("measureit: Imported multifiles")

# noinspection PyUnresolvedReferences
import bpy
# noinspection PyUnresolvedReferences
from bpy.props import *


# --------------------------------------------------------------
# Register all operators and panels
# --------------------------------------------------------------
def register():
    bpy.utils.register_class(measureit_main.RunHintDisplayButton)
    bpy.utils.register_class(measureit_main.AddSegmentButton)
    bpy.utils.register_class(measureit_main.AddAngleButton)
    bpy.utils.register_class(measureit_main.AddLabelButton)
    bpy.utils.register_class(measureit_main.AddLinkButton)
    bpy.utils.register_class(measureit_main.AddOriginButton)
    bpy.utils.register_class(measureit_main.DeleteSegmentButton)
    bpy.utils.register_class(measureit_main.DeleteAllSegmentButton)
    bpy.utils.register_class(measureit_main.MeasureitEditPanel)
    bpy.utils.register_class(measureit_main.MeasureitMainPanel)

    # Define properties
    bpy.types.Scene.measureit_default_color = bpy.props.FloatVectorProperty(
        name="Default color",
        description="Default Color",
        default=(0.173, 0.545, 1.0, 1.0),
        min=0.1,
        max=1,
        subtype='COLOR',
        size=4)
    bpy.types.Scene.measureit_font_size = bpy.props.IntProperty(name="Text Size",
                                                                description="Default text size",
                                                                default=14, min=10, max=150)
    bpy.types.Scene.measureit_hint_space = bpy.props.FloatProperty(name='Separation', min=0, max=5, default=0.1,
                                                                   precision=3,
                                                                   description="Default distance")
    bpy.types.Scene.measureit_gl_ghost = bpy.props.BoolProperty(name="All",
                                                                description="Display measures for all objects,"
                                                                            " not only selected",
                                                                default=True)
    bpy.types.Scene.measureit_gl_txt = bpy.props.StringProperty(name="Text", maxlen=48,
                                                                description="Short description")

    bpy.types.Scene.measureit_gl_precision = bpy.props.IntProperty(name='Precision', min=0, max=5, default=2,
                                                                   description="Number of decimal precision")
    bpy.types.Scene.measureit_gl_show_d = bpy.props.BoolProperty(name="ShowDist",
                                                                 description="Display measures",
                                                                 default=True)
    bpy.types.Scene.measureit_gl_show_n = bpy.props.BoolProperty(name="ShowName",
                                                                 description="Display text",
                                                                 default=False)
    bpy.types.Scene.measureit_scale = bpy.props.BoolProperty(name="Scale",
                                                             description="Use scale factor",
                                                             default=False)
    bpy.types.Scene.measureit_scale_factor = bpy.props.FloatProperty(name='Factor', min=0.001, max=9999999,
                                                                     default=1.0,
                                                                     precision=3,
                                                                     description="Scale factor 1:x")
    bpy.types.Scene.measureit_scale_color = bpy.props.FloatVectorProperty(name="Scale color",
                                                                          description="Scale Color",
                                                                          default=(1, 1, 0, 1.0),
                                                                          min=0.1,
                                                                          max=1,
                                                                          subtype='COLOR',
                                                                          size=4)
    bpy.types.Scene.measureit_scale_font = bpy.props.IntProperty(name="Font",
                                                                 description="Text size",
                                                                 default=14, min=10, max=150)
    bpy.types.Scene.measureit_scale_pos_x = bpy.props.IntProperty(name="Position X",
                                                                  description="Margin on the X axis",
                                                                  default=5,
                                                                  min=0,
                                                                  max=100)
    bpy.types.Scene.measureit_scale_pos_y = bpy.props.IntProperty(name="Position Y",
                                                                  description="Margin on the Y axis",
                                                                  default=5,
                                                                  min=0,
                                                                  max=100)
    bpy.types.Scene.measureit_gl_scaletxt = bpy.props.StringProperty(name="ScaleText", maxlen=48,
                                                                     description="Scale title",
                                                                     default="Scale:")
    bpy.types.Scene.measureit_scale_precision = bpy.props.IntProperty(name='Precision', min=0, max=5, default=0,
                                                                      description="Number of decimal precision")

    bpy.types.Scene.measureit_ovr = bpy.props.BoolProperty(name="Override",
                                                           description="Override colors and fonts",
                                                           default=False)
    bpy.types.Scene.measureit_ovr_font = bpy.props.IntProperty(name="Font",
                                                               description="Override text size",
                                                               default=14, min=10, max=150)
    bpy.types.Scene.measureit_ovr_color = bpy.props.FloatVectorProperty(name="Override color",
                                                                        description="Override Color",
                                                                        default=(1, 0, 0, 1.0),
                                                                        min=0.1,
                                                                        max=1,
                                                                        subtype='COLOR',
                                                                        size=4)
    bpy.types.Scene.measureit_ovr_width = bpy.props.IntProperty(name='Override width', min=1, max=10, default=1,
                                                                description='override line width')

    bpy.types.Scene.measureit_units = bpy.props.EnumProperty(items=(('1', "Automatic", "Use scene units"),
                                                                    ('2', "Meters", ""),
                                                                    ('3', "Centimeters", ""),
                                                                    ('4', "Milimiters", ""),
                                                                    ('5', "Feet", ""),
                                                                    ('6', "Inches", "")),
                                                             name="Units",
                                                             description="Units")

    # OpenGL flag
    wm = bpy.types.WindowManager
    # register internal property
    wm.measureit_run_opengl = bpy.props.BoolProperty(default=False)


def unregister():
    bpy.utils.unregister_class(measureit_main.RunHintDisplayButton)
    bpy.utils.unregister_class(measureit_main.AddSegmentButton)
    bpy.utils.unregister_class(measureit_main.AddAngleButton)
    bpy.utils.unregister_class(measureit_main.AddLabelButton)
    bpy.utils.unregister_class(measureit_main.AddLinkButton)
    bpy.utils.unregister_class(measureit_main.AddOriginButton)
    bpy.utils.unregister_class(measureit_main.DeleteSegmentButton)
    bpy.utils.unregister_class(measureit_main.DeleteAllSegmentButton)
    bpy.utils.unregister_class(measureit_main.MeasureitEditPanel)
    bpy.utils.unregister_class(measureit_main.MeasureitMainPanel)

    # Remove properties
    del bpy.types.Scene.measureit_default_color
    del bpy.types.Scene.measureit_font_size
    del bpy.types.Scene.measureit_hint_space
    del bpy.types.Scene.measureit_gl_ghost
    del bpy.types.Scene.measureit_gl_txt
    del bpy.types.Scene.measureit_gl_precision
    del bpy.types.Scene.measureit_gl_show_d
    del bpy.types.Scene.measureit_gl_show_n
    del bpy.types.Scene.measureit_scale
    del bpy.types.Scene.measureit_scale_factor
    del bpy.types.Scene.measureit_scale_color
    del bpy.types.Scene.measureit_scale_font
    del bpy.types.Scene.measureit_scale_pos_x
    del bpy.types.Scene.measureit_scale_pos_y
    del bpy.types.Scene.measureit_gl_scaletxt
    del bpy.types.Scene.measureit_scale_precision
    del bpy.types.Scene.measureit_ovr
    del bpy.types.Scene.measureit_ovr_font
    del bpy.types.Scene.measureit_ovr_color
    del bpy.types.Scene.measureit_ovr_width
    del bpy.types.Scene.measureit_units

    # remove OpenGL data
    measureit_main.RunHintDisplayButton.handle_remove(measureit_main.RunHintDisplayButton, bpy.context)
    wm = bpy.context.window_manager
    p = 'measureit_run_opengl'
    if p in wm:
        del wm[p]


if __name__ == '__main__':
    register()
