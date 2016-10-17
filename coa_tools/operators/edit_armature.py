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

######################################################################################################################################### Quick Armature        
class QuickArmature(bpy.types.Operator):
    bl_idname = "scene.coa_quick_armature" 
    bl_label = "Quick Armature"
    
    def __init__(self):
        self.distance = .1
        self.cur_distance = 0
        self.old_coord = Vector((0,0,0))
        self.mouse_press = False
        self.mouse_press_hist = False
        self.inside_area = False
        self.show_manipulator = False
        self.current_bone = None
        self.object_hover = None
        self.object_hover_hist = None
        self.in_view_3d = False
        self.armature_mode = None
        self.set_waits = False
        self.mouse_click_vec = Vector((0,0,0))
        self.shift = False
        self.shift_hist = False
        self.sprite_object = None
        self.alt = False
        self.alt_hist = False
        self.selected_objects = []
        self.active_object = None
        self.armature = None
        
        self.created_bones = []
        
    def project_cursor(self, event):
        coord = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))
        transform = bpy_extras.view3d_utils.region_2d_to_location_3d
        region = bpy.context.region
        rv3d = bpy.context.space_data.region_3d
        #### cursor used for the depth location of the mouse
        depth_location = bpy.context.scene.cursor_location
        #depth_location = bpy.context.active_object.location
        ### creating 3d vector from the cursor
        end = transform(region, rv3d, coord, depth_location)
        #end = transform(region, rv3d, coord, bpy.context.space_data.region_3d.view_location)
        ### Viewport origin
        start = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        
        ### Cast ray from view to mouselocation
        if b_version_bigger_than((2,76,0)):
            ray = bpy.context.scene.ray_cast(start, (start+(end-start)*2000)-start )
        else:    
            ray = bpy.context.scene.ray_cast(start, start+(end-start)*2000)
            
        ### ray_cast return values have changed after blender 2.67.0 
        if b_version_bigger_than((2,76,0)):
            ray = [ray[0],ray[4],ray[5],ray[1],ray[2]]
        
        return start, end, ray
    
    def create_armature(self,context):
        obj = bpy.context.active_object
        sprite_object = get_sprite_object(obj)
        armature = get_armature(sprite_object)
        
        for obj2 in context.selected_objects:
            obj2.select = False
        
        if armature != None:
            context.scene.objects.active = armature
            armature.select = True
            return armature
        else:
            amt = bpy.data.armatures.new("Armature")
            armature = bpy.data.objects.new("Armature",amt)
            armature.parent = sprite_object
            context.scene.objects.link(armature)
            context.scene.objects.active = armature
            armature.select = True
            armature.show_x_ray = True
            #amt.draw_type = "BBONE"
            return armature
        
    def create_default_bone_group(self,armature):
        default_bone_group = None
        if "default_bones" not in armature.pose.bone_groups:
            default_bone_group = armature.pose.bone_groups.new("default_bones")
            default_bone_group.color_set = "THEME08"
        else:
            default_bone_group = armature.pose.bone_groups["default_bones"]
        return default_bone_group   
                            
    def create_bones(self,context,armature):
        if armature != None:
            
            bpy.ops.object.mode_set(mode='EDIT')
            bone = armature.data.edit_bones.new("Bone")
            
            ### store newly created editbone names -> for locking z scale for posebones later. Posebones are not available at this point yet
            if bone.name not in self.created_bones:
                self.created_bones.append(bone.name)
            
            bone.head = self.armature.matrix_world.inverted() * context.scene.cursor_location
            bone.hide = True
            bone.bbone_x = .05
            bone.bbone_z = .05
            
            for bone2 in armature.data.edit_bones:
                bone2.select_head = False
                bone2.select_tail = False
                if bone2 != armature.data.edit_bones.active:
                    bone2.select = False        
            if armature.data.edit_bones.active != None and armature.data.edit_bones.active.select == True:
                active_bone = armature.data.edit_bones.active
                bone.parent = active_bone
                bone.name = active_bone.name
                distance = Vector(active_bone.tail.xyz - bone.head.xyz).magnitude / bpy.context.space_data.region_3d.view_distance
                if distance < .02:
                    bone.use_connect = True
                    active_bone.select_tail = True
                active_bone.select = False
            
                
            bone.select = True
            bone.select_head = True
            bone.select_tail = True
            armature.data.edit_bones.active = bone
            self.current_bone = bone
            self.create_default_bone_group(armature)    
    
    def drag_bone(self,context, event ,bone=None):
        ### math.atan2(0.5, 0.5)*180/math.pi
        if bone != None:
            
            bone.hide = False
            mouse_vec_norm = (context.scene.cursor_location - self.mouse_click_vec).normalized()
            mouse_vec = (context.scene.cursor_location - self.mouse_click_vec)
            angle = (math.atan2(mouse_vec_norm[0], mouse_vec_norm[2])*180/math.pi)
            cursor_local = self.armature.matrix_world.inverted() * context.scene.cursor_location   
            if event.shift:
                if angle > -22.5 and angle < 22.5:
                    ### up
                    bone.tail =  Vector((bone.head[0],0,cursor_local[2]))
                elif angle > 22.5 and angle < 67.5:
                    ### up right
                    bone.tail = (bone.head +  Vector((mouse_vec[0],0,mouse_vec[0])))
                elif angle > 67.5 and angle < 112.5:
                    ### right
                    bone.tail = Vector((cursor_local[0],0,bone.head[2]))
                elif angle > 112.5 and angle < 157.5:
                    ### down right
                    bone.tail = (bone.head +  Vector((mouse_vec[0],0,-mouse_vec[0])))
                elif angle > 157.5 or angle < -157.5:   
                    ### down
                    bone.tail = Vector((bone.head[0],0,cursor_local[2]))
                elif angle > -157.5 and angle < -112.5:
                    ### down left
                        bone.tail = (bone.head +  Vector((mouse_vec[0],0,mouse_vec[0])))
                elif angle > -112.5 and angle < -67.5:
                    ### left
                    bone.tail = Vector((cursor_local[0],0,bone.head[2]))
                elif angle > -67.5 and angle < -22.5:       
                    ### left up
                    bone.tail = (bone.head +  Vector((mouse_vec[0],0,-mouse_vec[0])))
            else:
                bone.tail = self.armature.matrix_world.inverted() * context.scene.cursor_location
                 
    def set_parent(self,context,obj):
        obj.select = True
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.object.parent_set(type='BONE')
        bpy.ops.object.mode_set(mode='EDIT')
        obj.select = False
        bpy.ops.ed.undo_push(message="Sprite "+obj.name+ " set parent")
    
    def set_weights(self,context,obj):
        self.set_waits = True
        bone_data = []
        orig_armature = context.active_object
        
        ### remove bone vertex_groups
        for weight in obj.vertex_groups:
            if weight.name in orig_armature.data.bones:
                obj.vertex_groups.remove(weight)
        ###         
        use_deform = []
        selected_bones = []
        for i,bone in enumerate(orig_armature.data.edit_bones):
            if bone.select and (bone.select_head or bone.select_tail):
                selected_bones.append(bone)
            use_deform.append(orig_armature.data.bones[i].use_deform)
            if bone.select and (bone.select_head or bone.select_tail):
                orig_armature.data.bones[i].use_deform = True
            else:
                orig_armature.data.bones[i].use_deform = False
        orig_armature.select = True     
        obj.select = True       
        
        obj_orig_location = Vector(obj.location)
        obj.location[1] = 0
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        obj.location = obj_orig_location
        
        for i,bone in enumerate(orig_armature.data.edit_bones):
            orig_armature.data.bones[i].use_deform = use_deform[i]
        i = 0
        for modifier in obj.modifiers:
            if modifier.type == "ARMATURE":
                i += 1
        if i > 1:
            obj.modifiers.remove(obj.modifiers[len(obj.modifiers)-1])
        for modifier in obj.modifiers:
            if modifier.type == "ARMATURE":
                modifier.object = orig_armature
        obj.parent = orig_armature
        orig_armature.select = True
        context.scene.objects.active = orig_armature
        obj.select = False
        
        bpy.ops.object.mode_set(mode='EDIT')
        self.set_waits = False  
        
    def return_ray_sprites(self,context,event):
        coord = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))
        transform = bpy_extras.view3d_utils.region_2d_to_location_3d
        region = bpy.context.region
        rv3d = bpy.context.space_data.region_3d
        depth_location = Vector((0,50,0))#bpy.context.scene.cursor_location
        end = transform(region, rv3d, coord, depth_location)
        start = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        return ray_cast(start,end,[])
        
    
    def modal(self, context, event):
        self.in_view_3d = check_region(context,event)
        if self.in_view_3d:
            if not event.alt:
                bpy.context.window.cursor_set("PAINT_BRUSH")
            else:
                bpy.context.window.cursor_set("EYEDROPPER") 
        else:
            bpy.context.window.cursor_set("DEFAULT")
        scene = context.scene
        ob = context.active_object
        
        
        ### lock posebone scale z value and then remove bone name from list
        for bone_name in self.created_bones:
            if bone_name in ob.pose.bones:
                pose_bone = ob.pose.bones[bone_name]
                pose_bone.lock_scale[2] = True
                self.created_bones.remove(bone_name)
        
        if self.in_view_3d:
            self.mouse_press_hist = self.mouse_press
            mouse_button = None
            if context.user_preferences.inputs.select_mouse == "RIGHT":
                mouse_button = 'LEFTMOUSE'
            else:
                mouse_button = 'RIGHTMOUSE'    
            ### Set Mouse click 
            if (event.value == 'PRESS') and event.type == mouse_button:
                self.mouse_press = True
                #return {'RUNNING_MODAL'}
            elif event.value in ['RELEASE','NOTHING'] and (event.type == mouse_button):
                self.mouse_press = False 
            #print(event.value,"-----------",event.type)
            ### Cast Ray from mousePosition and set Cursor to hitPoint
            rayStart,rayEnd, ray = self.project_cursor(event)
            
            if ray[0] == True and ray[1] != None:
                bpy.context.scene.cursor_location = ray[3]
            elif rayEnd != None:
                bpy.context.scene.cursor_location = rayEnd
            bpy.context.scene.cursor_location[1] = context.active_object.location[1]
            
            if event.value in ["RELEASE"]:
                if self.object_hover_hist != None :
                    self.object_hover_hist.show_x_ray = False
                    self.object_hover_hist.select = False
                    self.object_hover_hist.show_name = False
                    self.object_hover_hist = None
                if self.object_hover != None:
                    self.object_hover.show_x_ray = False
                    self.object_hover.select = False
                    self.object_hover.show_name = False
                        
                
            if not event.alt and not event.ctrl:
                self.object_hover = None
                ### mouse just pressed
                if not self.mouse_press_hist and self.mouse_press and self.in_view_3d:
                    #print("just pressed")
                    self.mouse_click_vec = Vector(context.scene.cursor_location)
                    self.create_bones(context,context.active_object)
                    
                    self.drag_bone(context,event,self.current_bone)
                    if context.active_bone != None:
                        bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Y')
                
                ### mouse pressed
                elif self.mouse_press_hist and self.mouse_press:
                    #print("pressed")
                    self.drag_bone(context,event,self.current_bone)
                    if context.active_bone != None:
                        bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Y')
                ### mouse release   
                elif not self.mouse_press and self.mouse_press_hist and self.current_bone != None:
                    bpy.ops.ed.undo_push(message="Add Bone: "+self.current_bone.name)
                    self.current_bone.hide = False   
                    self.current_bone = None
                    self.mouse_click_vec = Vector((1000000,1000000,1000000))
                    
                    self.set_waits = True
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.mode_set(mode='EDIT')
                    self.set_waits = False 
            
            elif (event.alt or "ALT" in event.type) and not event.ctrl:
                self.object_hover_hist = self.object_hover
                
                hover_objects = self.return_ray_sprites(context,event)
                distance = 1000000000
                if len(hover_objects) > 0:
                    for ray in hover_objects:
                        sprite_center = get_bounds_and_center(ray[1])[0]
                        if ((sprite_center) - ray[3]).length < distance:
                            distance = (sprite_center - ray[3]).length
                            self.object_hover = ray[1]
                else:
                    self.object_hover = None
                
                show_x_ray = False
                if self.object_hover != self.object_hover_hist:
                    if self.object_hover != None:
                        self.object_hover.show_name = True
                        self.object_hover.select = True
                        show_x_ray = self.object_hover.show_x_ray
                        self.object_hover.show_x_ray = True      
                    if self.object_hover_hist != None:
                        self.object_hover_hist.show_name = False
                        self.object_hover_hist.select = False
                        self.object_hover_hist.show_x_ray = False
                ### mouse just pressed
                if not self.mouse_press_hist and self.mouse_press and self.in_view_3d and self.object_hover != None:
                    selected_bones = context.selected_editable_bones
                    if ray[0] and ray[1] != None and len(selected_bones) == 1:
                        obj = ray[1]
                        self.set_weights(context,self.object_hover)
                        #self.set_parent(context,self.object_hover)
                    if ray[0] and ray[1] != None and len(selected_bones) > 1:
                        obj = ray[1]
                        self.set_weights(context,self.object_hover)
                return{'RUNNING_MODAL'}

            
            
            
                    
            ### cancel  
            if (event.type in {'ESC'} and self.in_view_3d) or (context.active_object.mode != "EDIT" and context.active_object.type == "ARMATURE" and self.set_waits == False) or not self.sprite_object.coa_edit_armature:
                bpy.context.space_data.show_manipulator = self.show_manipulator
                bpy.context.window.cursor_set("CROSSHAIR")
                bpy.ops.object.mode_set(mode=self.armature_mode)
                
                for pose_bone in context.active_object.pose.bones:
                    if "default_bones" in context.active_object.pose.bone_groups and pose_bone.bone_group == None:
                        pose_bone.bone_group = context.active_object.pose.bone_groups["default_bones"]
                
                #lock_sprites(context,get_sprite_object(context.active_object),get_sprite_object(context.active_object).lock_sprites)
                self.sprite_object.coa_edit_armature = False
                
                ### restore previous selection
                for obj in bpy.context.scene.objects:
                    obj.select = False
                for obj in self.selected_objects:
                    obj.select = True
                context.scene.objects.active = self.active_object   
                return{'CANCELLED'}
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        #bpy.ops.wm.coa_modal() ### start coa modal mode if not running
    
        for obj in context.scene.objects:
            if obj.select:
                self.selected_objects.append(obj)
        self.active_object = context.active_object
        
        self.sprite_object = get_sprite_object(context.active_object)
        self.sprite_object.coa_edit_armature = True
        lock_sprites(context,get_sprite_object(context.active_object),False)
        self.armature = self.create_armature(context)
            
        self.armature_mode = context.active_object.mode
        bpy.ops.object.mode_set(mode='EDIT')
        self.show_manipulator = bpy.context.space_data.show_manipulator
        bpy.context.space_data.show_manipulator = False

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        return {'CANCELLED'}
    
    
######################################################################################################################################### Set Stretch To Constraint
class SetStretchBone(bpy.types.Operator):
    bl_idname = "bone.coa_set_stretch_bone"
    bl_label = "Set Stretch Bone"
    
    def execute(self,context):
        armature = context.active_object
        p_bone = armature.pose.bones[context.active_pose_bone.name]
        bpy.ops.object.mode_set(mode="EDIT")
        
        bone_name = "Stretch_"+p_bone.name
        stretch_to_bone = armature.data.edit_bones.new(bone_name)
        stretch_to_bone.use_deform = False
        if p_bone.parent != None:
            stretch_to_bone.parent = context.active_object.data.edit_bones[p_bone.name].parent
        length = Vector(p_bone.tail - p_bone.head).length
        stretch_to_bone.head =  p_bone.tail
        stretch_to_bone.tail = Vector((p_bone.tail[0],0, p_bone.tail[2] + length * .5))
        bpy.ops.object.mode_set(mode="POSE")
        
        stretch_to_constraint = p_bone.constraints.new("STRETCH_TO")
        stretch_to_constraint.target = context.active_object
        stretch_to_constraint.subtarget = bone_name
        stretch_to_constraint.keep_axis = "PLANE_Z" 
        stretch_to_constraint.volume = "VOLUME_X"
        set_bone_group(self, context.active_object, context.active_object.pose.bones[bone_name],group="stretch_to",theme = "THEME07")
        return{'FINISHED'}

######################################################################################################################################### Set IK Constraint 
class SetIK(bpy.types.Operator):
    bl_idname = "object.coa_set_ik"
    bl_label = "Set IK Bone"
    
    replace_bone = BoolProperty(name="Replace IK Bone",description="Replaces active Bone as IK Bone", default=True)
    
    def invoke(self, context, event):
        wm = context.window_manager 
        return wm.invoke_props_dialog(self)   

    def execute(self,context):
        bone = context.active_object.pose.bones[context.active_pose_bone.name]
        bone2 = context.selected_pose_bones[0]
        ik_bone = None
        if self.replace_bone:
            ik_bone = bone.parent
        else:
            ik_bone = bone  
        next_bone = bone
        ik_length = 0
        while next_bone != bone2 and next_bone.parent != None:
            ik_length += 1 
            next_bone = next_bone.parent
        if not self.replace_bone:
            ik_length += 1
        
        for bone3 in context.active_object.data.bones:
            bone3.select = False
            
        bpy.ops.object.mode_set(mode="EDIT")
        ik_target_name = "IK_" + bone.name
        ik_target = context.active_object.data.edit_bones.new("IK_" + bone.name)
        if bone.parent != None:
            ik_target.parent = context.active_object.data.edit_bones[bone.name].parent_recursive[len(context.active_object.data.edit_bones[bone.name].parent_recursive)-1]
        if self.replace_bone:
            ik_target.head = bone.head
            ik_target.tail = bone.tail
        else:
             ik_target.head = bone.tail
             ik_target.tail = ik_target.head + Vector(((bone.tail - bone.head).length,0,0)) 
        ik_target.roll = context.active_object.data.edit_bones[bone.name].roll
        bpy.ops.object.mode_set(mode="POSE")
        context.active_object.data.bones[ik_target_name].select = True
        context.active_object.data.bones.active = context.active_object.data.bones[ik_target_name]

        ik_const = ik_bone.constraints.new("IK")
        ik_const.target = context.active_object
        ik_const.subtarget = ik_target_name
        ik_const.chain_count = ik_length
        
        set_bone_group(self, context.active_object, context.active_object.pose.bones[ik_target_name])
        
        if self.replace_bone:
            copy_loc_const = bone.constraints.new("COPY_LOCATION")
            copy_loc_const.target = context.active_object
            copy_loc_const.subtarget = ik_target_name
            
            copy_rot_const = bone.constraints.new("COPY_ROTATION")
            copy_rot_const.target = context.active_object
            copy_rot_const.subtarget = ik_target_name
            context.active_object.data.bones[bone.name].layers[1] = True
            context.active_object.data.bones[bone.name].layers[0] = False
            
        bpy.ops.ed.undo_push(message="Set Ik")
        return{'FINISHED'}    