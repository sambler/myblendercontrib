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

bl_info = {
    "name": "Cutout Animation Tools",
    "description": "This Addon provides a Toolset for a 2D Animation Workflow.",
    "author": "Andreas Esau",
    "version": (0, 1, 0, "Alpha"),
    "blender": (2, 75, 0),
    "location": "View 3D > Tools > Cutout Animation Tools",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Ndee Tools" }
    
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

class AddAnimationCollection(bpy.types.Operator):
    bl_idname = "my_operator.add_animation_collection"
    bl_label = "Add Animation Collection"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True
    
    sprite_object = None
    
    def create_actions_collection(self,context):
        if self.sprite_object != None:
            if len(self.sprite_object.coa_anim_collections) == 0:
                item = self.sprite_object.coa_anim_collections.add()
                item.name = "NO ACTION"
                
                item = self.sprite_object.coa_anim_collections.add()
                item.name = "Restpose"
                item.frame_start = 0
                item.frame_end = 1
                
            item = self.sprite_object.coa_anim_collections.add()
            item.name = check_name(self.sprite_object.coa_anim_collections,"NewCollection")
            item.name_old = item.name
            item.action_collection = True
            
            self.sprite_object.coa_anim_collections_index = len(self.sprite_object.coa_anim_collections)-1
        else:
            return{'FINISHED'}    
    
    def create_actions(self,context):
        item = self.sprite_object.coa_anim_collections[self.sprite_object.coa_anim_collections_index]
        
        for child in get_children(context,self.sprite_object,ob_list=[]):
            if child.type == "ARMATURE":
                action_name = item.name + "_" + child.name
                
                action = None
                if action_name not in bpy.data.actions:
                    action = bpy.data.actions.new(action_name)
                else:
                    action = bpy.data.actions[action_name]
                action.use_fake_user = True    
                if child.animation_data == None:
                    child.animation_data_create()
                child.animation_data.action = action

    def execute(self, context):
        self.sprite_object = get_sprite_object(context.active_object)
        
        self.create_actions_collection(context)
        self.create_actions(context)
        
        
        return {"FINISHED"}
        
class RemoveAnimationCollection(bpy.types.Operator):
    bl_idname = "my_operator.remove_animation_collection"
    bl_label = "Remove Animation Collection"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True
    
    sprite_object = None
    
    def remove_actions_collection(self,context):
        if self.sprite_object != None:
            if self.sprite_object.coa_anim_collections[self.sprite_object.coa_anim_collections_index].name != "NO ACTION" and self.sprite_object.coa_anim_collections[self.sprite_object.coa_anim_collections_index].name != "Restpose":
                self.sprite_object.coa_anim_collections.remove(self.sprite_object.coa_anim_collections_index)
            if self.sprite_object.coa_anim_collections_index > 2:
                self.sprite_object.coa_anim_collections_index = self.sprite_object.coa_anim_collections_index - 1
            
            if len(self.sprite_object.coa_anim_collections) < 3:
                self.sprite_object.coa_anim_collections.remove(0)
                self.sprite_object.coa_anim_collections.remove(0)
            
    def remove_actions(self,context):
        item = self.sprite_object.coa_anim_collections[self.sprite_object.coa_anim_collections_index]
        
        for child in get_children(context,self.sprite_object,ob_list=[]):
            action_name = item.name + "_" + child.name
            
            if action_name in bpy.data.actions:
                if child.animation_data != None and child.animation_data.action == bpy.data.actions[action_name]:
                    child.animation_data_clear()
                bpy.data.actions[action_name].use_fake_user = False
                bpy.data.actions[action_name].user_clear()    
                #bpy.data.actions.remove(bpy.data.actions[action_name])
            
                    
    def execute(self, context):
        self.sprite_object = get_sprite_object(context.active_object)
        if len(self.sprite_object.coa_anim_collections) > 0:
            
            self.remove_actions(context)
            self.remove_actions_collection(context)
            
        return {"FINISHED"}
                