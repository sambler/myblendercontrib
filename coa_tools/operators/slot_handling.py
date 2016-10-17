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


class CreateSlotObject(bpy.types.Operator):
    bl_idname = "coa_tools.create_slot_object"
    bl_label = "Create Slot Object"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True
    
    slot_name = StringProperty(name="Slot Name")
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        #obj = bpy.data.objects[context.active_object.name]
        init_obj = bpy.data.objects[context.active_object.name] 
        obj = context.active_object.copy()
        context.scene.objects.link(obj)
        context.scene.objects.active = obj
        obj.name = self.slot_name
        
        objs = context.selected_objects
        obj.coa_type = "SLOT"
        for sprite in context.selected_objects:
            if sprite != obj:
                if sprite.type == "MESH":
                    #sprite.data.use_fake_user = True
                    #print(sprite.name,"-----",sprite.data)
                    
                    if sprite.data.name not in obj.coa_slot:
                        item = obj.coa_slot.add()
                    else:
                        item = obj.coa_slot[sprite.data.name]
                    item.name = sprite.data.name
                    item.index = len(obj.coa_slot)-1
                    if sprite == init_obj:
                        obj.coa_slot_index =  item.index
                        obj.coa_slot_reset_index =  item.index
                        
                    
                    item["active"] = False
        for sprite in objs:        
            if sprite != obj:
                sprite.parent = None
                sprite.location = [0,0,0]
                sprite.layers[19] = True
                for i,layer in enumerate(sprite.layers):
                    if i < 19:
                        sprite.layers[i] = False
                #bpy.context.scene.objects.unlink(sprite)
                #bpy.data.objects.remove(sprite)
        return {"FINISHED"}