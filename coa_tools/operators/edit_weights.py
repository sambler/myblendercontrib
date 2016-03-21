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
    
class EditWeights(bpy.types.Operator):
    bl_idname = "object.coa_edit_weights"
    bl_label = "Select Child"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def __init__(self):
        self.sprite_object = None
        self.obj = None
        self.armature = None
        self.active_object = None
        self.selected_objects = []
        self.object_color_settings = {}
    
    def armature_set_mode(self,context,mode,select):
        global armature_select
        armature_select = self.armature.select
        self.armature.select = select
        active_object = context.scene.objects.active
        global armature_mode
        armature_mode = self.armature.mode
        context.scene.objects.active = self.armature
        bpy.ops.object.mode_set(mode=mode)

        context.scene.objects.active = active_object
    
    def select_bone(self):
        for bone in self.armature.data.bones:
            bone.select = False
        self.armature.data.bones.active = None
        
        for i,vertex_group in enumerate(self.obj.vertex_groups):
            if vertex_group.name in self.armature.data.bones:
                self.obj.vertex_groups.active_index = i
                bone = self.armature.data.bones[vertex_group.name]
                self.armature.data.bones.active = bone
                break
     
    def exit_edit_weights(self,context):
        armature = get_armature(get_sprite_object(context.active_object))
        bpy.ops.object.mode_set(mode="OBJECT")
        set_local_view(False)
        for i,bone_layer in enumerate(bone_layers):
            armature.data.layers[i] = bone_layer
        
        for obj in context.scene.objects:
            obj.select = False
        for obj in self.selected_objects:
            obj.select = True        
        context.scene.objects.active = self.active_object
                
            
            
    def modal(self, context, event):
    
        if self.sprite_object.coa_edit_weights == False or get_local_view(context) == None or context.active_object.mode != "WEIGHT_PAINT":
            self.exit_edit_weights(context)
            self.sprite_object.coa_edit_weights = False
            bpy.ops.ed.undo_push(message="Enter Edit Weights")
            self.disable_object_color(False)
            return {"FINISHED"}
            
        return {"PASS_THROUGH"}
    
    def disable_object_color(self,disable):
        sprite_object = get_sprite_object(bpy.context.active_object)
        children = get_children(bpy.context,sprite_object,ob_list=[])
        for obj in children:
            if obj.type == "MESH":
                if len(obj.material_slots) > 0:
                    if disable:
                        self.object_color_settings[obj.name] = obj.material_slots[0].material.use_object_color
                        obj.material_slots[0].material.use_object_color = not disable
                    else:
                        obj.material_slots[0].material.use_object_color = self.object_color_settings[obj.name]
                            
    
    def invoke(self, context, event):
        self.disable_object_color(True)
        context.window_manager.modal_handler_add(self)
        
        self.active_object = context.active_object
        self.selected_objects = context.selected_objects
        
        self.obj = context.active_object
        self.sprite_object = get_sprite_object(self.obj)
        self.sprite_object.coa_edit_weights = True
        self.armature = get_armature(self.sprite_object)
        bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
            
        if self.armature != None:
            self.armature_set_mode(context,"POSE",True)
            global bone_layers
            bone_layers = []
            for i,bone_layer in enumerate(self.armature.data.layers):
                bone_layers.append(bone_layer)
                self.armature.data.layers[i] = True
            self.select_bone()
            
        sprite = context.active_object
        if sprite.parent != get_armature(self.sprite_object):
            create_armature_parent(context)

        set_local_view(True)
        context.scene.tool_settings.use_auto_normalize = True
        #bpy.ops.ed.undo_push(message="Enter Edit Weights")
        return {"RUNNING_MODAL"}
            