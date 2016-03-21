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


######################################################################################################################################### Cutout Animatin Tools Modal Operator    
class COAModal(bpy.types.Operator):
    bl_idname = "wm.coa_modal"
    bl_label = "Cutout Animation Tools Modal"
    bl_options = {"REGISTER","INTERNAL"}
    
    
    def __init__(self):
        self.sprite_object = None
        self.value = ""
        self.value_hist = ""
        self.type_hist = ""
        self.value_pressed = False
        self.scaling = False
        
    def set_frame_bounds_and_actions(self,context):
        scene = context.scene
        if len(self.sprite_object.coa_anim_collections) > 2:
            scene.frame_start = self.sprite_object.coa_anim_collections[self.sprite_object.coa_anim_collections_index].frame_start
            scene.frame_end = self.sprite_object.coa_anim_collections[self.sprite_object.coa_anim_collections_index].frame_end
        #set_action(context)
    
    
    def check_event_value(self,event):
        if event.value == "PRESS" and self.value_hist in ["RELEASE","NOTHING"]:
            self.value_pressed = True
            return "JUST_PRESSED"
        elif event.value != "RELEASE" and self.value_pressed:
            return "PRESSED"
        elif event.value == "RELEASE" and self.value_hist == "PRESS":
            self.value_pressed = False
            return "JUST_RELEASED"
        else:
            return "RELEASED"
    
    def set_scaling(self,obj,event):
        if obj != None and obj.mode == "EDIT":
            if event.type == "S":
                self.scaling = True
    def check_scaling(self,obj,event):
        if self.scaling:
            if event.value == "RELEASE":
                if event.type == "LEFTMOUSE":
                    self.scaling = False
                    return "SCALE_APPLIED"
                elif event.type in ["RIGHTMOUSE","ESC"]:
                    self.scaling = False
                    return "SCALE_CANCELLED"
    
    def modal(self,context,event):
        ### execute only if an event pressed is triggered
        active_object = context.active_object
        if self.check_event_value(event) == "JUST_PRESSED":
            wm = context.window_manager
            self.sprite_object = get_sprite_object(context.active_object)
            
            self.set_scaling(active_object,event)
            if self.sprite_object != None:
                self.set_frame_bounds_and_actions(context)
            
            screen = context.screen    
            if screen.coa_view == "2D":
                set_middle_mouse_move(True)
            elif screen.coa_view == "3D":
                set_middle_mouse_move(False)
                
        elif self.check_event_value(event) == "JUST_RELEASED":
            screen = context.screen
            if screen.coa_view == "2D":
                set_middle_mouse_move(True)
            elif screen.coa_view == "3D":
                set_middle_mouse_move(False)
                
            if active_object != None and "sprite" in active_object and active_object.mode == "OBJECT":    
                set_alpha(active_object,bpy.context,active_object.coa_alpha)
                set_z_value(context,active_object,active_object.coa_z_value)
                set_modulate_color(active_object,context,active_object.coa_modulate_color)
                
                
        
        ### Store sprite dimension in coa_sprite_dimension when mesh is rescaled
            for obj in context.selected_objects:
                if obj != None and "sprite" in obj and len(obj.data.vertices) == 4:
                    obj.coa_sprite_dimension = Vector((get_local_dimension(obj)[0],0,get_local_dimension(obj)[1]))
        if self.check_scaling(active_object,event) == "SCALE_APPLIED":
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.mode_set(mode="EDIT")
            active_object.coa_sprite_dimension = Vector((get_local_dimension(active_object)[0],0,get_local_dimension(active_object)[1]))
        ###
        
        self.value_hist = str(event.value)
        self.type_hist = str(event.type)
        return{'PASS_THROUGH'}
        
    def execute(self,context):
        wm = context.window_manager
        if not context.window_manager.coa_running_modal:
            context.window_manager.coa_running_modal = True
            wm.modal_handler_add(self)
        return{'RUNNING_MODAL'} 


