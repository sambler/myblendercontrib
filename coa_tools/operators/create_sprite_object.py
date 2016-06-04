'''
Copyright (C) 2015 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
    
import bpy
import bpy_extras
import bpy_extras.view3d_utils
from math import radians
import mathutils
from mathutils import Vector, Matrix, Quaternion
import math
import bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty
import os
from bpy_extras.io_utils import ExportHelper, ImportHelper
import json
from bpy.app.handlers import persistent
from .. functions import *

######################################################################################################################################### Create Sprite Object
class CreateSpriteObject(bpy.types.Operator):
    bl_idname = "wm.coa_create_sprite_object"
    bl_label = "Create Sprite Object"
    bl_options = {"REGISTER","UNDO"}
    
    def execute(self, context):
        obj = context.active_object
        
        if context.active_object != None and obj.type == "ARMATURE" and obj.mode == "POSE":
            context.scene.objects.active = None
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=False, location=context.scene.cursor_location)
        empty = bpy.context.active_object
        empty.name = "SpriteObject"
        empty.show_name = True
        empty.show_x_ray = True
        empty["sprite_object"] = True
        bpy.ops.ed.undo_push(message="Create Sprite Object")
        return{"FINISHED"}