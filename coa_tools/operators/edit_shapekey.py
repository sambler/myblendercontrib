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
from mathutils import Vector, Matrix, Quaternion, geometry
import math
import bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty
from .. functions import *
from .. functions_draw import *
import bgl, blf
import traceback

class LeaveSculptmode(bpy.types.Operator):
    bl_idname = "coa_tools.leave_sculptmode"
    bl_label = "Leave Sculptmode"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = context.active_object
        if obj != None and obj.type == "MESH":
            bpy.ops.object.mode_set(mode="OBJECT")
        return {"FINISHED"}
        

class ShapekeyAdd(bpy.types.Operator):
    bl_idname = "coa_tools.shapekey_add"
    bl_label = "Shapekey Add"
    bl_description = ""
    bl_options = {"REGISTER"}

    name = StringProperty(name="Name")

    @classmethod
    def poll(cls, context):
        return True
        
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
    def execute(self, context):
        obj = context.active_object
        if obj.data.shape_keys == None:
            obj.shape_key_add(name="Basis",from_mix=False)
            
        
        shape = obj.shape_key_add(name=self.name,from_mix=False)
        shape_name = shape.name
        
        for i,shape in enumerate(obj.data.shape_keys.key_blocks):
            if shape.name == shape_name:
                obj.active_shape_key_index = i
                break
            
        return {"FINISHED"}
        

class EditShapekeyMode(bpy.types.Operator):
    bl_idname = "coa_tools.edit_shapekey"
    bl_label = "Edit Shapekey"
    bl_description = ""
    bl_options = {"REGISTER","UNDO"}

    def get_shapekeys(self,context):
        SHAPEKEYS = []
        SHAPEKEYS.append(("NEW_KEY","New Shapekey","New Shapekey","NEW",0))
        obj = context.active_object
        if obj.type == "MESH" and obj.data.shape_keys != None:
            i = 0
            for i,shape in enumerate(obj.data.shape_keys.key_blocks):
                if i > 0:
                    SHAPEKEYS.append((shape.name,shape.name,shape.name,"SHAPEKEY_DATA",i+1))
                
        
        return SHAPEKEYS

    shapekeys = EnumProperty(name="Shapekey",items=get_shapekeys)
    shapekey_name = StringProperty(name="Name",default="New Shape")
    mode_init = StringProperty()
    obj_init = None
    armature = None
    sprite_object = None
    shape = None
    create_shapekey = BoolProperty(default=False)
    objs = []
    
    @classmethod
    def poll(cls, context):
        return True
    
    def check(self,context):
        return True
    
    def draw(self,context):
        layout = self.layout
        col = layout.column()
        col.prop(self,"shapekeys")
        if self.shapekeys == "NEW_KEY":
            col.prop(self,"shapekey_name")
        
    
    def invoke(self,context,event):
        obj = context.active_object
        
        if event.ctrl:# or obj.data.shape_keys == None:
            wm = context.window_manager
            self.create_shapekey = True
            return wm.invoke_props_dialog(self)
        else:
            return self.execute(context)
            
    
    def execute(self, context):
        if context.active_object == None:
            self.report({"ERROR"},"Armature is hidden or not selected. Cannot go in Edit Mode.")
            return{"CANCELLED"}
        obj = context.active_object
        self.sprite_object = get_sprite_object(obj)
        self.armature = get_armature(self.sprite_object)
        self.obj_init = context.active_object
        
        self.mode_init = obj.mode if obj.mode != "SCULPT" else "OBJECT"
        
        shape_name = self.shapekeys
        
        if self.shapekeys == "NEW_KEY" and self.create_shapekey:
            if obj.data.shape_keys == None:
                obj.shape_key_add(name="Basis", from_mix=False)
            shape = obj.shape_key_add(name=self.shapekey_name, from_mix=False)    
            shape_name = shape.name
            
        self.sprite_object.coa_edit_shapekey = True
        self.sprite_object.coa_edit_mode = "SHAPEKEY"
        bpy.ops.object.mode_set(mode="SCULPT")
        
        for brush in bpy.data.brushes:
            if brush.sculpt_tool == "GRAB":
                context.scene.tool_settings.sculpt.brush = brush
                break
        
        ### run modal operator and draw handler
        args = ()
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
    
    def exit_edit_mode(self,context,event,obj):
        for obj in context.selected_objects:
            obj.select = False
        self.sprite_object.coa_edit_shapekey = False
        self.sprite_object.coa_edit_mode = "OBJECT"
        
        for obj in self.objs:
            obj.hide = False
            if obj.type == "MESH" and obj != None:
                context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode="OBJECT")
                obj.show_only_shape_key = False
        
        context.scene.objects.active = obj
        obj.select = True
        if self.armature != None:
            self.armature.data.pose_position = "POSE"
            
        ### remove draw handler on exiting modal mode    
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")    
        return {"FINISHED"}
    
    def modal(self, context, event):
        obj = context.active_object
        try:
            if obj != None:
                if obj not in self.objs and obj.type == "MESH":
                    self.objs.append(obj)
                if obj.type == "MESH" and obj.mode in ["OBJECT","WEIGHT_PAINT"]:
                    bpy.ops.object.mode_set(mode="SCULPT")    
                
                if obj.type == "MESH" and obj.data.shape_keys != None:
                    if obj.coa_selected_shapekey != obj.active_shape_key.name:
                        obj.coa_selected_shapekey = str(obj.active_shape_key_index) #obj.active_shape_key.name
            
            if self.sprite_object.coa_edit_shapekey == False:
                return self.exit_edit_mode(context,event,obj)
            
        except Exception as e:
            traceback.print_exc()
            self.report({"ERROR"},"An Error occured, please check console for more Information.")
            self.exit_edit_mode(context,event,obj) 
        return {"PASS_THROUGH"}
    
    def draw_callback_px(self):
        draw_edit_mode(self,bpy.context,offset=2)
           