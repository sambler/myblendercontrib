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
        self.use_unified_strength = False
        self.non_deform_bones = []
        self.deform_bones = []
    
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
        tool_settings = context.scene.tool_settings
        tool_settings.unified_paint_settings.use_unified_strength = self.use_unified_strength
        set_local_view(False)
        armature = get_armature(get_sprite_object(context.active_object))
        bpy.ops.object.mode_set(mode="OBJECT")
        for i,bone_layer in enumerate(bone_layers):
            armature.data.layers[i] = bone_layer
        
        for obj in context.scene.objects:
            obj.select = False
        for obj in self.selected_objects:
            obj.select = True            
        context.scene.objects.active = self.active_object
        self.unhide_non_deform_bones(context)
        self.hide_deform_bones(context)
            
    def modal(self, context, event):
    
        if get_local_view(context) == None or (context.active_object != None and context.active_object.mode != "WEIGHT_PAINT") or context.active_object == None:
            self.exit_edit_weights(context)
            self.sprite_object.coa_edit_weights = False
            bpy.ops.ed.undo_push(message="Exit Edit Weights")
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
    
    def unhide_deform_bones(self,context):
        for bone in self.armature.data.bones:
            if bone.hide and bone.use_deform:
                self.deform_bones.append(bone)
                bone.hide = False
    
    def hide_deform_bones(self,context):
        for bone in self.deform_bones:
            bone.hide = True
            
    def hide_non_deform_bones(self,context):
        for bone in self.armature.data.bones:
            if not bone.hide and not bone.use_deform:
                self.non_deform_bones.append(bone)
                bone.hide = True
    
    def unhide_non_deform_bones(self,context):
        for bone in self.non_deform_bones:
            bone.hide = False
    
                                    
    def invoke(self, context, event):
        self.obj = context.active_object
        self.sprite_object = get_sprite_object(self.obj)
        self.armature = get_armature(self.sprite_object)
        
        if self.armature == None or not self.armature in context.visible_objects:
            self.report({'WARNING'},'No Armature Available or Visible')
            return{"CANCELLED"}
        
        scene = context.scene
        tool_settings = scene.tool_settings
        self.use_unified_strength = tool_settings.unified_paint_settings.use_unified_strength
        tool_settings.unified_paint_settings.use_unified_strength = True
        
        self.disable_object_color(True)
        context.window_manager.modal_handler_add(self)
        
        self.active_object = context.active_object
        self.selected_objects = context.selected_objects
        
        self.sprite_object.coa_edit_weights = True
        
        
        self.hide_non_deform_bones(context)
        self.unhide_deform_bones(context)
            
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
        
        bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
        return {"RUNNING_MODAL"}
            