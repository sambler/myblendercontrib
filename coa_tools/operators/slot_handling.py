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
        if context.active_object.coa_type != "SLOT":
            return wm.invoke_props_dialog(self)
        else:
            self.execute(context)
            return{"FINISHED"}
    
    def execute(self, context):
        #obj = bpy.data.objects[context.active_object.name]
        init_obj = bpy.data.objects[context.active_object.name] 
        obj = context.active_object.copy()
        context.scene.objects.link(obj)
        context.scene.objects.active = obj
        if obj.coa_type == "MESH":
            obj.name = self.slot_name    
        
        objs = context.selected_objects
        obj.coa_type = "SLOT"
        for sprite in context.selected_objects:
            if sprite != obj:
                if sprite.type == "MESH":
                    if sprite.coa_type == "MESH":
                        if sprite.data.name not in obj.coa_slot:
                            item = obj.coa_slot.add()
                        else:
                            item = obj.coa_slot[sprite.data.name]
                        item.name = sprite.data.name
                        item.index = len(obj.coa_slot)-1
                        if sprite == init_obj:
                            obj.coa_slot_index =  item.index
                            obj.coa_slot_reset_index =  item.index
                    elif sprite.coa_type == "SLOT" and sprite != init_obj:
                        for slot in sprite.coa_slot:
                            item = obj.coa_slot.add()
                            item.name = slot.name
                                    
                        
                    
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
        for i,s in enumerate(obj.coa_slot):
            s.index = i
        return {"FINISHED"}
    

class MoveSlotItem(bpy.types.Operator):
    bl_idname = "coa_tools.move_slot_item"
    bl_label = "Move Slot Item"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    idx = IntProperty()
    ob_name = StringProperty()
    mode = StringProperty()
        
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = bpy.data.objects[self.ob_name]
        
        if self.mode == "UP":
            new_idx = max(self.idx-1,0)
            obj.coa_slot.move(self.idx,new_idx)
        elif self.mode == "DOWN":
            new_idx = min(self.idx+1,len(obj.coa_slot)-1)
            obj.coa_slot.move(self.idx,new_idx)
        
        for i,s in enumerate(obj.coa_slot):
            s.index = i
        
        return {"FINISHED"}
        
    
class RemoveFromSlot(bpy.types.Operator):
    bl_idname = "coa_tools.remove_from_slot"
    bl_label = "Remove From Slot"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    idx = IntProperty()
    ob_name = StringProperty()
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        print(self.idx)
        obj = bpy.data.objects[self.ob_name]
        slot = obj.coa_slot[self.idx]
        active_idx = 0
        for i,s in enumerate(obj.coa_slot):
            if s.active:
                active_idx = i
                break
        obj.coa_slot.remove(self.idx)
        
        active_idx = max(0,(active_idx - 1))
        
        for i,s in enumerate(obj.coa_slot):
            s["index"] = i    
        if len(obj.coa_slot) > 0:
            obj.coa_slot[active_idx].active = True
        else:
            context.scene.objects.unlink(obj)
            bpy.data.objects.remove(obj)    
        
#        for s in obj.coa_slot:
#            if s.index > self.idx:
#                s["index"] -= 1
        
        
        
        
        return {"FINISHED"}
            