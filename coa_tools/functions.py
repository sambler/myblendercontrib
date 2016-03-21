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
from mathutils import Vector, Matrix, Quaternion, Euler
import math
import bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty
import os
from bpy_extras.io_utils import ExportHelper, ImportHelper
import json
from bpy.app.handlers import persistent

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def b_version_bigger_than(version):
    if bpy.app.version > version:
        return True
    else:
        return False

def get_local_dimension(obj):
    x0 = 10000000000*10000000000
    x1 = -10000000000*10000000000
    y0 = 10000000000*10000000000
    y1 = -100000000000*10000000000
    
    for vert in obj.data.vertices:
        if vert.co[0] < x0:
            x0 = vert.co[0]
        if vert.co[0] > x1:
            x1 = vert.co[0]
        if vert.co[2] < y0:
            y0 = vert.co[2]
        if vert.co[2] > y1:
            y1 = vert.co[2]
    return [(x1-x0)*obj.coa_tiles_x,(y1-y0)*obj.coa_tiles_y]

def get_addon_prefs(context):
    addon_name = __name__.split(".")[0]
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[addon_name].preferences
    return addon_prefs

def get_local_view(context):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            return area.spaces.active.local_view

def check_name(name_array,name):
    if name in name_array:
        counter = 1
        check_name = name
        while check_name + ".{0:03d}".format(counter) in name_array:
            counter+=1
        name = name+".{0:03d}".format(counter)
        return name
        if counter > 999:
            return name
    else:
        return name

def create_action(context,item=None):
    sprite_object = get_sprite_object(context.active_object)
    
    if len(sprite_object.coa_anim_collections) < 3:
        bpy.ops.my_operator.add_animation_collection()
    
    if item == None:
        item = sprite_object.coa_anim_collections[sprite_object.coa_anim_collections_index]
    obj = context.active_object
    action_name = item.name + "_" + obj.name
    
    if action_name not in bpy.data.actions:
        action = bpy.data.actions.new(action_name)
    else:
        action = bpy.data.actions[action_name]
        
    action.use_fake_user = True
    if obj.animation_data == None:
        obj.animation_data_create()
    obj.animation_data.action = action
    context.scene.update()    
        
def set_action(context,item=None):
    sprite_object = get_sprite_object(context.active_object)
    if item == None:
        item = sprite_object.coa_anim_collections[sprite_object.coa_anim_collections_index]

    for child in get_children(context,sprite_object,ob_list=[]):
        if child.animation_data != None:
            child.animation_data.action = None
            child.animation_data_clear()
            
        if child.type == "ARMATURE" and item.name == "Restpose":
            for bone in child.pose.bones:
                bone.scale = Vector((1,1,1))
                bone.location = Vector((0,0,0))
                bone.rotation_euler = Euler((0,0,0),"XYZ")
                bone.rotation_quaternion = Euler((0,0,0),"XYZ").to_quaternion()
        if child.type == "MESH" and item.name == "Restpose":
            child.coa_sprite_frame = 0
            child.coa_alpha = 1.0
            child.coa_modulate_color = (1.0,1.0,1.0)
        else:
            action_name = item.name + "_" + child.name
            
            action = None
            if action_name in bpy.data.actions:
                action = bpy.data.actions[action_name]
            if action != None:    
                action.use_fake_user = True    
                if child.animation_data == None:
                    child.animation_data_create()
                child.animation_data.action = action
    context.scene.update()        

def create_armature_parent(context):
    sprite = context.active_object
    armature = get_armature(get_sprite_object(sprite))
    armature.select = True
    context.scene.objects.active = armature
    bpy.ops.object.parent_set(type='ARMATURE_NAME')
    context.scene.objects.active = sprite

def set_local_view(local):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            if local:
                if area.spaces.active.local_view == None:
                    bpy.ops.view3d.localview()
            else:
                if area.spaces.active.local_view != None:
                    bpy.ops.view3d.localview()

def actions_callback(self,context):
    actions = []
    actions.append(("New Action...","New Action...","New Action","NEW",0))
    actions.append(("Clear Action","Clear Action","Clear Action","RESTRICT_SELECT_ON",1))
    i = 2
    for action in bpy.data.actions:
        actions.append((action.name,action.name,action.name,'ACTION',i))
        i+=1
    return actions

def create_armature(context):
    obj = bpy.context.active_object
    sprite_object = get_sprite_object(obj)
    armature = get_armature(sprite_object)
    
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
        amt.draw_type = "BBONE"
        return armature

def set_alpha(obj,context,alpha):
    sprite_object = get_sprite_object(obj)
    
    for mat in obj.material_slots:
        if mat != None:
            for i,tex_slot in enumerate(mat.material.texture_slots):
                if tex_slot != None:
                    tex_slot.alpha_factor = alpha
                    
                    
def set_view(screen,mode):
    if mode == "2D":
        active_space_data = bpy.context.space_data
        region_3d = active_space_data.region_3d
        bpy.ops.view3d.viewnumpad(type='FRONT')
        if region_3d.view_perspective != "ORTHO":
            bpy.ops.view3d.view_persportho()
    elif mode == "3D":
        active_space_data = bpy.context.space_data
        region_3d = active_space_data.region_3d
        if region_3d.view_perspective == "ORTHO":
            bpy.ops.view3d.view_persportho()        


def set_middle_mouse_move(enable):
    km = bpy.context.window_manager.keyconfigs.addon.keymaps["3D View"]
    km.keymap_items["view3d.move"].active = enable
    
def assign_tex_to_uv(image,uv):
    for i,data in enumerate(uv.data):
        uv.data[i].image = image
        
def set_bone_group(self, armature, pose_bone,group = "ik_group" ,theme = "THEME09"):
    new_group = None
    if group not in armature.pose.bone_groups:
        new_group = armature.pose.bone_groups.new(group)
        new_group.color_set = theme
    else:
        new_group = armature.pose.bone_groups[group]
    pose_bone.bone_group = new_group
        
def get_sprite_object(obj):
    if obj != None:
        if "sprite_object" in obj:
            return obj
        elif obj.parent != None:
            return get_sprite_object(obj.parent)
        else:
            return None
    else:
        return None 
        
def get_armature(obj):
    for child in obj.children:
        if child.type == "ARMATURE":
            return child
    return None 

def get_bounds_and_center(obj):
    sprite_center = Vector((0,0,0))
    bounds = []
    for i,corner in enumerate(obj.bound_box):
        world_corner = obj.matrix_world * Vector(corner)
        sprite_center += world_corner
        if i in [0,1,4,5]:
            bounds.append(world_corner)
    sprite_center = sprite_center*0.125
    return[sprite_center,bounds]
    
    
def ray_cast(start,end,list=[]):
    if b_version_bigger_than((2,76,0)):
        end = end - start
    result = bpy.context.scene.ray_cast(start,end)
    
    if b_version_bigger_than((2,76,0)):
        result = [result[0],result[4],result[5],result[1],result[2]]
    
    if result[0]:
        if result not in list:
            list.append(result)
        
        dir_vec = (end - start).normalized()
        new_start = result[3] + (dir_vec*0.0001)
        return ray_cast(new_start,end,list)
    else:
        return list
    
def lock_sprites(context, obj, lock):
    for child in obj.children:
        if child.type == "MESH":
            if lock:
                child.hide_select = True
                child.select = False
                if child == context.scene.objects.active:
                    context.scene.objects.active = child.parent
            else:
                child.hide_select = False   
        if len(child.children) > 0:
            return lock_sprites(context,child,lock)
    return      


def get_children(context,obj,ob_list=[]):
    if obj != None:
        for child in obj.children:
            ob_list.append(child)
            if len(child.children) > 0:
                get_children(context,child,ob_list)
    return ob_list  

                        
def update_uv(context,obj):
    if "sprite" in obj and len(obj.data.vertices) == 4:
        mode_prev = obj.mode
        if obj == context.active_object and obj.type == "MESH":
            bpy.ops.object.mode_set(mode="OBJECT")
        coord1 = obj.data.uv_layers[obj.data.uv_layers.active.name].data[0]
        coord2 = obj.data.uv_layers[obj.data.uv_layers.active.name].data[1]
        coord3 = obj.data.uv_layers[obj.data.uv_layers.active.name].data[2]
        coord4 = obj.data.uv_layers[obj.data.uv_layers.active.name].data[3]
        
        sprite_object = get_sprite_object(obj)
        #anim_data = sprite_object.coa_anim_data[obj.name]
        anim_data = obj
        
        frame_size = Vector((1 / anim_data.coa_tiles_x,1 / anim_data.coa_tiles_y))
        pos_x = frame_size.x * (anim_data.coa_sprite_frame % anim_data.coa_tiles_x)
        pos_y = frame_size.y *  -int(int(anim_data.coa_sprite_frame) / int(anim_data.coa_tiles_x))
        frame = Vector((pos_x,pos_y))
        
        offset = Vector((0,1))-Vector((0,frame_size.y))
        
        coord1.uv = Vector((0.0 / anim_data.coa_tiles_x,0.0 / anim_data.coa_tiles_y)) + offset + frame
        coord2.uv = Vector((1.0 / anim_data.coa_tiles_x,0.0 / anim_data.coa_tiles_y)) + offset + frame
        coord3.uv = Vector((1.0 / anim_data.coa_tiles_x,1.0 / anim_data.coa_tiles_y)) + offset + frame
        coord4.uv = Vector((0.0 / anim_data.coa_tiles_x,1.0 / anim_data.coa_tiles_y)) + offset + frame
        
        if obj == context.active_object and obj.type == "MESH":
            bpy.ops.object.mode_set(mode=mode_prev)
        #obj.scale = Vector((1.0 / obj.coa_tiles_x,1,1.0 / obj.coa_tiles_y))
        
def update_verts(context,obj):  
    if "sprite" in obj and len(obj.data.vertices) == 4:
        mode_prev = obj.mode
        armature = get_armature(get_sprite_object(obj))
        pose_position = ""
        if armature != None:
            pose_position = armature.data.pose_position
            armature.data.pose_position = "REST"
            context.scene.objects.active = armature
            mode = armature.mode
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.object.mode_set(mode=mode)
            context.scene.objects.active = obj
        
        obj.coa_dimensions_old = Vector(obj.dimensions)
        sprite_sheet_width = obj.data.uv_textures[0].data[0].image.size[0]
        sprite_sheet_height = obj.data.uv_textures[0].data[0].image.size[1]
        
        scale_x = round(obj.coa_sprite_dimension[0] / sprite_sheet_width,5)
        scale_y = round(obj.coa_sprite_dimension[2] / sprite_sheet_height,5)
        
        sprite_object = get_sprite_object(obj)
        #anim_data = sprite_object.coa_anim_data[obj.name]
        anim_data = obj
        
        for vert in obj.data.vertices:
            vert.co[0] = vert.co[0] / obj.coa_dimensions_old[0] * sprite_sheet_width / anim_data.coa_tiles_x * scale_x * obj.matrix_world.to_scale()[0]
            vert.co[2] = vert.co[2] / obj.coa_dimensions_old[2] * sprite_sheet_height / anim_data.coa_tiles_y * scale_y * obj.matrix_world.to_scale()[2]
            
        if armature != None:
            armature.data.pose_position = pose_position
        bpy.ops.object.mode_set(mode=mode_prev)    

def set_z_value(context,obj,z):
    scale = get_addon_prefs(context).sprite_import_export_scale
    obj.location[1] = -z  * scale

def set_modulate_color(obj,context,color):
    if obj.type == "MESH":
        if not obj.material_slots[0].material.use_object_color:
            obj.material_slots[0].material.use_object_color = True
        obj.color[:3] = color    
    
        
def display_children(self, context, obj):
    layout = self.layout
    box = layout.box()
    col = box.column(align=True)
    children = get_children(context,obj,ob_list=[])
    row = col.row(align=True)
    row.prop(obj,"coa_filter_names",text="",icon="VIEWZOOM")
    if obj.coa_favorite:
        row.prop(obj,"coa_favorite",text="",icon="SOLO_ON")
    else:
        row.prop(obj,"coa_favorite",text="",icon="SOLO_OFF")
    
    col = box.column(align=True)
    if context.active_object.mode == "EDIT":
        col.enabled = False
    else:
        col.enabled = True
    
    sprite_object = get_sprite_object(context.active_object)
    row = col.row(align=True)
    icon = "LAYER_USED"
    if sprite_object.select:
        icon = "LAYER_ACTIVE"
    row.label(text="",icon=icon)
    row.label(text="",icon="EMPTY_DATA")
    if sprite_object.coa_show_children:
        row.prop(sprite_object,"coa_show_children",text="",icon="TRIA_DOWN",emboss=False)
    else:
        row.prop(sprite_object,"coa_show_children",text="",icon="TRIA_RIGHT",emboss=False) 
        
    op = row.operator("object.coa_select_child",text=sprite_object.name,emboss=False)
    op.mode = "object"
    op.ob_name = sprite_object.name
    
    
    if sprite_object.coa_show_children:    
        for child in children:
            if (obj.coa_favorite and child.coa_favorite) or not obj.coa_favorite:
                if obj.coa_filter_names in child.name:
                    row = col.row(align=True)
                    row.separator()
                    row.separator()
                    row.separator()
                    name = child.name
                    icon = "LAYER_USED"
                    if child.select:
                        icon = "LAYER_ACTIVE"
                    row.label(text="",icon=icon)
                    if child.type == "ARMATURE":
                        row.label(text="",icon="ARMATURE_DATA")
                    elif child.type == "MESH":
                        row.label(text="",icon="TEXTURE")
                    if child.type == "ARMATURE":
                        if child.coa_show_bones:
                            row.prop(child,"coa_show_bones",text="",icon="TRIA_DOWN",emboss=False)
                        else:
                            row.prop(child,"coa_show_bones",text="",icon="TRIA_RIGHT",emboss=False) 
                    op = row.operator("object.coa_select_child",text=name,emboss=False)
                    op.mode = "object"
                    op.ob_name = child.name
                    
                    
                    if child.coa_favorite:
                        row.prop(child,"coa_favorite",emboss=False,text="",icon="SOLO_ON")
                    else:
                        row.prop(child,"coa_favorite",emboss=False,text="",icon="SOLO_OFF")
                    if child.coa_hide:  
                        row.prop(child,"coa_hide",emboss=False,text="",icon="VISIBLE_IPO_OFF")
                    else:   
                        row.prop(child,"coa_hide",emboss=False,text="",icon="VISIBLE_IPO_ON")
                    if child.coa_hide_select:   
                        row.prop(child,"coa_hide_select",emboss=False,text="",icon="RESTRICT_SELECT_ON")
                    else:   
                        row.prop(child,"coa_hide_select",emboss=False,text="",icon="RESTRICT_SELECT_OFF")   
                    #row.prop(child,"hide_select",emboss=False,text="")
                    
                    if child.type == "ARMATURE":
                        if child.coa_show_bones:
                            for bone in child.data.bones:
                                if (obj.coa_favorite and bone.coa_favorite or not obj.coa_favorite):#  and child.pose.bones[bone.name] in context.visible_pose_bones:
                                    row = col.row(align=True)
                                    row.separator()
                                    row.separator()
                                    row.separator()
                                    row.separator()
                                    row.separator()
                                    row.separator()
                                    icon = "LAYER_USED"
                                    if bone.select:
                                        icon = "LAYER_ACTIVE"   
                                    row.label(text="",icon=icon)
                                    row.label(text="",icon="BONE_DATA")
                                    bone_name = ""+bone.name
                                    op = row.operator("object.coa_select_child",text=bone_name,emboss=False)
                                    op.mode = "bone"
                                    op.ob_name = child.name
                                    op.bone_name = bone.name
                                    if bone.coa_favorite:
                                        row.prop(bone,"coa_favorite",emboss=False,text="",icon="SOLO_ON")
                                    else:
                                        row.prop(bone,"coa_favorite",emboss=False,text="",icon="SOLO_OFF")
                                    if bone.hide:
                                        row.prop(bone,"coa_hide",text="",emboss=False,icon="VISIBLE_IPO_OFF")
                                    else:   
                                        row.prop(bone,"coa_hide",text="",emboss=False,icon="VISIBLE_IPO_ON")
                                    if bone.hide_select:
                                        row.prop(bone,"coa_hide_select",text="",emboss=False,icon="RESTRICT_SELECT_ON")
                                    else:   
                                        row.prop(bone,"coa_hide_select",text="",emboss=False,icon="RESTRICT_SELECT_OFF")            
