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
import bmesh
import json
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty
from collections import OrderedDict
from .. functions import *
import math
from mathutils import Vector,Matrix, Quaternion, Euler
from shutil import copyfile

db_json = OrderedDict()
db_json = {
                    "info":"Generated with COA Tools",
                    "frameRate": 24,
                    "isGlobal": 0,
                    "name": "Project Name",
                    "version": "4.5",
                    "armature": []
                    }

armature = OrderedDict()
armature = {
            "aabb":{"width":0,"y":0,"height":0,"x":0},
            "defaultActions":[{"gotoAndPlay":""}],
            "ik":[],
            "type":"Armature",
            "frameRate":24,
            "animation":[],
            
            "bone":[],
            "slot":[],
            "name":"Armature",
            "skin":[{"name":"","slot":[]}]
           }

animation = {
            "bone": [],
            "frame": [],
            "slot": [],
            "playTimes": 0,
            "name": "Anim Name",
            "ffd": [],
            "duration": 0
            }
    
skin = OrderedDict()
skin = {
        "name":"",
        "slot":[],
        }

display = OrderedDict()
display = [
            {
                "edges": [],
                "uvs": [],
                "type": "mesh",
                "vertices": [],
                "transform": {
                    "x": -2
                },
                "userEdges": [],
                "width": 480,
                "triangles": [],
                "height": 480,
                "name": "output_file"
            }
        ]


bone_default_pos = {}
bone_default_rot = {}
default_vert_coords = {}
texture_pathes = {}
ignore_bones = []


def get_uv_bounds(uv):
    top = 0
    left = 1
    right = 0
    bottom = 1
    for vert in uv.data:
        if vert.uv.x < left:
            left = float(vert.uv.x)
        if vert.uv.x > right:
            right = float(vert.uv.x)
        if vert.uv.y > top:
            top = float(vert.uv.y)
        if vert.uv.y < bottom:
            bottom = float(vert.uv.y)
    scale_x = 1/(right-left)
    scale_y = 1/(top-bottom)
    return ((left,top),(right,bottom)),(scale_x,scale_y)

def generate_texture_atlas(context,objs,atlas_name,width,height,atlas_size,unwrap_method,island_margin):
    ### create new atlas Image
    atlas = bpy.data.images.new(atlas_name,width,height,alpha=True)
    
    ### deselect objects
    for obj in context.scene.objects:
        obj.select = False
        
    ### select given objects    
    for obj in objs:
        mesh_data = []
        ### get all mesh names if from type slot. Otherwise just append the obj mesh name 
        if obj.coa_type == "MESH":
            mesh_data.append(obj.data.name)
        elif obj.coa_type == "SLOT":
            for slot in obj.coa_slot:
                mesh_data.append(slot.name)
        ### loop over all mesh names        
        for i,name in enumerate(mesh_data):
            obj.data = bpy.data.meshes[name]
            ob_data = obj.data.copy()
            name = obj.name+"_atlas"
            new_ob = obj.copy()
            new_ob.data = ob_data
            new_ob.name = name
            new_ob.matrix_world = obj.matrix_world
            context.scene.objects.link(new_ob)
            
            new_ob.select = True
            context.scene.objects.active = new_ob
            
            
            for group in new_ob.vertex_groups:
                new_ob.vertex_groups.remove(group)
            
            ### generate vertex group with containing vertices    
            group_name = obj.name + "_coa_slot_"+obj.data.name ### append vertex group with object and meshname
            new_ob.vertex_groups.new(name=group_name)
            bpy.ops.object.mode_set(mode="EDIT")  
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.mode_set(mode="OBJECT")
            if new_ob.active_shape_key != None:#new_ob.data.shape_keys != None and len(new_ob.data.shape_keys.key_blocks) > 0:
                bpy.ops.object.shape_key_remove(all=True)  
                
            ### set active uv as default uv
            for mat in obj.data.materials:
                for tex_slot in mat.texture_slots:
                    if tex_slot != None:
                        if tex_slot.texture != None:
                            tex_slot.uv_layer = new_ob.data.uv_textures.active.name
                    
    
    ### join all selected objects into one 
    bpy.ops.object.join()
    obj = context.active_object
    
    ### generate new uv map item
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.reveal()
    uv_map = obj.data.uv_textures.new(name="COA_ATLAS")
    uv_map.active_render = True
    obj.data.uv_textures.active = uv_map
    
    ### create uv layout
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=island_margin)

    bpy.ops.object.mode_set(mode="OBJECT")
    
    for vert in obj.data.uv_textures["COA_ATLAS"].data:
        vert.image = atlas
        
    bpy.ops.object.mode_set(mode="EDIT")
    if unwrap_method == "ANGLE_BASED":
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=island_margin)
    elif unwrap_method == "SMART_UV":
        bpy.ops.uv.smart_project(island_margin=island_margin,use_aspect=True, stretch_to_bounds=False)

    
    bpy.ops.object.mode_set(mode="OBJECT")
    
    ### separate mesh parts into single objects and copy uv data to original sprites
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode="OBJECT")
    
    tmp_sprites = []
    for i,group in enumerate(obj.vertex_groups):
        tmp_sprite = None
        for vert in obj.data.vertices:
            for group2 in vert.groups:
                if group2.group == group.index:
                    vert.select = True
        ### separate mesh
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode="OBJECT")
        
        ### set proper selection to copy uv data
        obj.select = False
        tmp_sprite = bpy.context.selected_objects[0]
        tmp_sprites.append(tmp_sprite)
        context.scene.objects.active = tmp_sprite
        sprite = bpy.data.objects[group.name.split("_coa_slot_")[0]]
        sprite.data = bpy.data.meshes[group.name.split("_coa_slot_")[1]]
        sprite.select = True
        
        ### calc autoatic texture size
        if i == 0 and atlas_size == "AUTOMATIC":
            bounds,atlas_scale = get_uv_bounds(tmp_sprite.data.uv_layers["COA_ATLAS"])
            image_size = tmp_sprite.data.uv_textures[0].data[0].image.size
            width = image_size[0] * atlas_scale[0]
            height = image_size[1] * atlas_scale[1]
            atlas.generated_width = width
            atlas.generated_height = height
        
        ### generate new atlas uv layout and make it active for final sprites
        if "COA_ATLAS" in sprite.data.uv_textures:
            uv_map = sprite.data.uv_textures["COA_ATLAS"]
        else:    
            uv_map = sprite.data.uv_textures.new(name="COA_ATLAS")
        sprite.data.uv_textures.active = uv_map
        
        ### copy uv data from tmp sprites to original sprite
        bpy.ops.object.join_uvs()
        
        ### assign atlas texture to verts in edit mode
        for vert in sprite.data.uv_textures.active.data:
            vert.image = atlas
        
        ### restore selections
        context.scene.objects.active = obj
        obj.select = True
        tmp_sprite.select = False
        sprite.select = False
        
        
        
        ### delete tmp sprite
        #bpy.context.scene.objects.unlink(tmp_sprite)
        #bpy.data.objects.remove(tmp_sprite)
    
    obj = context.active_object
    bpy.context.scene.objects.unlink(obj)
    bpy.data.objects.remove(obj)
    
    ####
    for obj in context.scene.objects:
        obj.select = False
    for obj in tmp_sprites:
        obj.select = True
        context.scene.objects.active = obj
    
    
    bpy.ops.object.join()
    obj = context.active_object
    
    ### bake texture into new uv layout
    for vert in obj.data.uv_textures["COA_ATLAS"].data:
        vert.image = atlas
        
    context.scene.render.bake_type = "TEXTURE"
    bpy.ops.object.bake_image()
    bpy.context.scene.update()
    
    bpy.context.scene.objects.unlink(obj)
    bpy.data.objects.remove(obj)
    
        


def get_shapekey_driver(obj):
    bone_drivers = []
    armature = None
    if obj.data.shape_keys != None and obj.data.shape_keys.animation_data != None and obj.data.shape_keys.animation_data.drivers != None:
        drivers = obj.data.shape_keys.animation_data.drivers
        for driver in drivers:
            for var in driver.driver.variables:
                armature = var.targets[0].id
                if armature != None:
                    bone_target = var.targets[0].bone_target
                    if bone_target in armature.data.bones:
                        bone = armature.data.bones[bone_target]
                        bone_drivers.append(bone)           
    return armature, bone_drivers

def get_sprite_driver(obj):
    bone_drivers = []
    armature = None
    if obj.animation_data != None:
        for driver in obj.animation_data.drivers:
            if driver.data_path in ["coa_slot_index","coa_alpha","coa_modulate_color"]:
                for var in driver.driver.variables:
                    armature = var.targets[0].id
                    if armature != None:
                        bone_target = var.targets[0].bone_target
                        if bone_target in armature.data.bones:
                            bone = armature.data.bones[bone_target]
                            bone_drivers.append(bone)
    return armature, bone_drivers


def get_bone_keyframe_pos(armature, bones):
    action = None
    keyframes = []    
    if armature != None:
        if armature.animation_data != None and armature.animation_data.action != None:
            action = armature.animation_data.action
        
        if action != None:    
            for bone in bones:
                for fcurve in action.fcurves:
                    if bone.name in fcurve.data_path:
                        for keyframe in fcurve.keyframe_points:
                            if keyframe.co[0] not in keyframes:
                                keyframes.append(keyframe.co[0])
        keyframes = sorted(keyframes)
    return keyframes
    
### get objs and bones that are keyed on given frame    
def bone_key_on_frame(bone,frame,action):
    for fcurve in action.fcurves:
        if bone.name in fcurve.data_path:
            for keyframe in fcurve.keyframe_points:
                if keyframe.co[0] == frame:
                    return True
    return False            

def sprite_key_on_frame(sprite,frame,action):
    for fcurve in action.fcurves:
        for keyframe in fcurve.keyframe_points:
            if keyframe.co[0] == frame:
                return True
    return False

def get_animation_data(context,sprite_object,armature,bake_anim,bake_interval):
    m = Matrix() ### inverted posebone origin matrix
    m.row[0] = [0,0,1,0]
    m.row[1] = [1,0,0,0]
    m.row[2] = [0,1,0,0]
    m.row[3] = [0,0,0,1]
    
    data = []
    scale = 1/get_addon_prefs(context).sprite_import_export_scale
    anims = sprite_object.coa_anim_collections
    for anim in anims:
        anim_data = animation.copy()
        anim_data["name"] = anim.name
        anim_data["duration"] = anim.frame_end
        anim_data["playTimes"] = 1
        anim_data["bone"] = []
        anim_data["slot"] = []
        anim_data["ffd"] = []
        if anim.name not in ["NO ACTION"]:
            set_action(context,item=anims[1])
            context.scene.update()
            
            set_action(context,item=anim)
            context.scene.update()
            objs = get_children(context,sprite_object,ob_list=[])
            for obj in objs:
                if obj.animation_data != None:# and obj.animation_data.action != None:
                    action = None
                    if obj.animation_data.action != None:
                        action = obj.animation_data.action
                    ### get keyframes for Bones (Position, Rotation, Scale)
                    if obj.type == "ARMATURE":
                        ### loop over all bones and get data
                        for bone in obj.data.bones:
                                
                            pose_bone = armature.pose.bones[bone.name]
                            if bone.name not in ignore_bones:
                                bone_data = {}
                                bone_data["name"] = bone.name
                                bone_data["frame"] = []
                                ### loop over action framerange
                                for f in range(0,anim.frame_end+1):
                                    bpy.context.scene.frame_set(f)
                                    ### if bone has a keyframe on frame -> store data
                                    if (action != None and (bone_key_on_frame(bone,f,action)) or (bake_anim and f%bake_interval == 0) or f == 0):
                                        
                                        frame_data = {}
                                        frame_data["duration"] = f
                                        if len(bone_data["frame"]) > 0:
                                            idx = len(bone_data["frame"])-1
                                            bone_data["frame"][idx]["duration"] = f - bone_data["frame"][idx]["duration"] ### set duration of last keyframe
                                        frame_data["tweenEasing"] = 0
                                        #frame_data["curve"] = [0.25, 0.0, 0.75, 1.0]
                                        frame_data["transform"] = {}
                                        ### get bone position
                                        
                                        pos = get_bone_pos(armature,bone,scale)
                                        pos -= bone_default_pos[bone.name]
                                        if pos != Vector((0,0)):
                                            frame_data["transform"]["x"] = pos[0]
                                            frame_data["transform"]["y"] = pos[1]
                                        
                                        ### get bone angle    
                                        angle = get_bone_angle(armature,bone)
                                        angle -= bone_default_rot[bone.name]
                                        if angle != 0:
                                            frame_data["transform"]["skY"] = angle
                                            frame_data["transform"]["skX"] = angle
                                            
                                        ### get bone scale
                                        sca = get_bone_scale(armature,bone)
                                        if sca != Vector((1.0,1.0,1.0)):
                                            frame_data["transform"]["scX"] = sca[0]
                                            frame_data["transform"]["scY"] = sca[1]
                                        
                                        bone_data["frame"].append(frame_data)
                                anim_data["bone"].append(bone_data)          
            
                    ### get keyframes for slots (Color, Alpha, SlotIndex)
                    elif obj.type == "MESH":
                        slot_data = {}
                        slot_data["name"] = obj.name
                        slot_data["frame"] = []
                        
                        ### get sprite property driver bones
                        arm, bones = get_sprite_driver(obj)
                        arm_action = None
                        if arm != None and arm.animation_data != None:
                            arm_action = arm.animation_data.action
                        
                        ### loop over action framerange
                        for f in range(0,anim.frame_end+1):
                            bpy.context.scene.frame_set(f)
                            
                            ### check if property is manipulated by a bone driver
                            bone_key = False
                            if arm != None and arm_action != None:
                                for bone in bones:
                                    if bone_key_on_frame(bone,f,arm_action):
                                        bone_key = True
                                        break    
                                    
                            ### if slot has keyframe on frame -> store data
                            if (action != None and sprite_key_on_frame(obj,f,action)) or (bake_anim and f%bake_interval == 0) or f == 0 or bone_key:
                                frame_data = {}
                                frame_data["duration"] = f
                                if len(slot_data["frame"]) > 0:
                                    idx = len(slot_data["frame"])-1
                                    slot_data["frame"][idx]["duration"] = f - slot_data["frame"][idx]["duration"] ### set duration of last keyframe
                                frame_data ["displayIndex"] = obj.coa_slot_index
                                frame_data["color"] = {}
                                frame_data["tweenEasing"] = 0.0
                                #frame_data["curve"] = [0.5, 0.0, 0.5, 1.0]
                                
                                color_data = get_modulate_color(obj)

                                if color_data["rM"] != 100:
                                    frame_data["color"]["rM"] = color_data["rM"]
                                if color_data["gM"] != 100:
                                    frame_data["color"]["gM"] = color_data["gM"]
                                if color_data["bM"] != 100:
                                    frame_data["color"]["bM"] = color_data["bM"]
                                if color_data["aM"] != 100:
                                    frame_data["color"]["aM"] = color_data["aM"]
                                slot_data["frame"].append(frame_data)   
                        anim_data["slot"].append(slot_data)
            
            ### get shapekey deformation data
            sprites = get_children(context,sprite_object,[])
            for obj in sprites:
                if obj.type == "MESH":
                    arm, bones = get_shapekey_driver(obj)
                    keyframes = get_bone_keyframe_pos(arm,bones)

                    ffd_data = {}
                    ffd_data["name"] = texture_pathes[obj.name]
                    ffd_data["slot"] = obj.name
                    ffd_data["offset"] = 0
                    ffd_data["scale"] = 1
                    ffd_data["skin"] = ""
                    ffd_data["frame"] = []
                    for f in range(0,anim.frame_end+1):
                        bpy.context.scene.frame_set(f)
                        
                        if f in keyframes or f == 0 or (bake_anim and f%bake_interval == 0 and len(keyframes)>0):
                            ffd_frame_data = {}
                            ffd_frame_data["duration"] = f
                            ffd_frame_data["tweenEasing"] = 0
                            
                            ### get the keyframe duration by comparing to last set keyframe
                            if len(ffd_data["frame"]) > 0:
                                idx = len(ffd_data["frame"])-1
                                ffd_data["frame"][idx]["duration"] = f - ffd_data["frame"][idx]["duration"] ### set duration of last keyframe
                            
                            mixed_verts = get_mixed_vertex_data(obj)
                            coord_differences = []
                            for i,co in enumerate(mixed_verts):
                                diff = Vector(co) - Vector(default_vert_coords[obj.name][i])
                                coord_differences.append(diff)
                            ffd_frame_data["vertices"] = convert_vertex_data(coord_differences)
                                
                            ffd_data["frame"].append(ffd_frame_data)
                    anim_data["ffd"].append(ffd_data)  
            
            ### get event data             
            for i,event in enumerate(anim.event):
                if i == 0:
                    if event.frame > 0:
                        event_data = {}
                        event_data["duration"] = event.frame
                        anim_data["frame"].append(event_data)                
                
                event_data = {}
                event_data["duration"] = event.frame
                if i > 0:
                    anim_data["frame"]["duration"] = event.frame - anim_data["frame"]["duration"]
                
                event_data["action"] = event.action
                event_data["event"] = event.event
                event_data["sound"] = event.sound
                anim_data["frame"].append(event_data)        
            data.append(anim_data)
    return data                 

def get_modulate_color(sprite):
    color = sprite.coa_modulate_color
    alpha = sprite.coa_alpha
    color_data = {"rM":int(100*color[0]),"gM":int(100*color[1]),"bM":int(100*color[2]),"aM":int(100*alpha)}
    return color_data

def get_ik_data(armature,bone,const):
    data = {}
    pose_bone = armature.pose.bones[bone.name]
    
    data["target"] = const.subtarget
    data["bone"] = bone.name
    data["name"] = "bone_ik"
    data["weight"] = const.influence
    if min(const.chain_count-1,1) > 0:
        data["bendPositive"] = False
        data["chain"] = min(const.chain_count-1,1)
    return data
 
def get_bone_index(armature,bone_name):
    armature_bones = []
    for bone in armature.data.bones:
        if bone.name not in ignore_bones:
            armature_bones.append(bone)
    
    for i,bone in enumerate(armature_bones):#enumerate(armature.data.bones):
        if bone_name == bone.name:
            return i

### get weight data
def get_weight_data(obj,armature):
    data = []
    bone_names = []
    bones = []
    for vert in obj.data.vertices:
        groups = []
        for group in vert.groups:
            group_name = obj.vertex_groups[group.group].name
            if group_name in armature.data.bones:
                groups.append({"group":group,"group_name":group_name})
        
        data.append(len(groups))    
        for group in groups:
            bone_index = get_bone_index(armature,group["group_name"])+1
            data.append(bone_index)
            bone_weight = group["group"].weight
            data.append(bone_weight)
            
            if group["group_name"] not in bone_names:
                bone_names.append(group["group_name"])
    
    armature_bones = []
    for bone in armature.data.bones:
        if bone.name not in ignore_bones:
            armature_bones.append(bone)   
                
    for i,bone in enumerate(armature_bones):#enumerate(armature.data.bones):
        if bone.name in bone_names:
            bone = armature.data.bones[bone.name]            
            bones.append({"index":i,"bone":bone})
    return data, bones
                    
                
    
### get skin data
def get_skin_data(obj,tex_path,scale,armature,texture_atlas=False):
    context = bpy.context
    obj.select = True
    context.scene.objects.active = obj
    
    texture_pathes[obj.name] = tex_path
    
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    
    d = OrderedDict()
    d["type"] = "mesh"
    d["name"] = tex_path
    d["user_edges"] = []
    if not texture_atlas:
        d["width"] = get_img_tex(obj).size[0]
        d["height"] = get_img_tex(obj).size[1]
    else:
        d["width"] = bpy.data.images[tex_path.split("/")[1]].size[0]
        d["height"] = bpy.data.images[tex_path.split("/")[1]].size[1]
    
    verts = get_mixed_vertex_data(obj,store_tmp=True)
    d["vertices"] = convert_vertex_data(verts)
    
    bm = bmesh.from_edit_mesh(obj.data)
    #d["vertices"] = get_vertex_data(bm)
    d["edges"] = get_edge_data(bm)
    d["triangles"] = get_triangle_data(bm)
    d["uvs"] = get_uv_data(bm)
    if armature != None:
        d["weights"] = get_weight_data(obj,armature)[0]
    
        d["bonePose"] = []
        armature.data.pose_position = "REST"
        bpy.context.scene.update()
        bones = get_weight_data(obj,armature)[1]
        for bone in bones:
            mat = get_bone_matrix(armature,bone["bone"],relative=False)
            d["bonePose"].append(bone["index"]+1)
            d["bonePose"].append(mat[0][0])
            d["bonePose"].append(mat[0][1])
            d["bonePose"].append(mat[1][0])
            d["bonePose"].append(mat[1][1])
            d["bonePose"].append(mat[1][3] * scale )#pos x
            d["bonePose"].append(-mat[0][3] *scale )#pos y
        armature.data.pose_position = "POSE"    
        bpy.context.scene.update()
        
        w = obj.matrix_local[0][0]
        x = obj.matrix_local[0][2]
        y = obj.matrix_local[2][0]
        z = obj.matrix_local[2][2]
        d["slotPose"] = [w,x,y,z, obj.matrix_local.to_translation()[0]*scale, -obj.matrix_local.to_translation()[2]*scale]
    
    d["transform"] = OrderedDict()
    
    d["transform"]["x"] = obj.matrix_local.to_translation()[0]*scale
    d["transform"]["y"] = -obj.matrix_local.to_translation()[2]*scale
    d["transform"]["skX"] = math.degrees(obj.matrix_local.to_euler().y)
    d["transform"]["skY"] = math.degrees(obj.matrix_local.to_euler().y)
    d["transform"]["scY"] = obj.matrix_local.to_scale()[0]
    d["transform"]["scX"] = obj.matrix_local.to_scale()[2]
    
    bpy.ops.object.mode_set(mode="OBJECT")
    
    display = OrderedDict()
    display["name"] = obj.name
    display["display"] = [d]
    return d

### get mesh vertex corrseponding uv vertex        
def uv_from_vert_first(uv_layer, v):
    for l in v.link_loops:
        uv_data = l[uv_layer]
        return uv_data.uv
    return None

### get vertices information
def convert_vertex_data(verts):
    data = []
    for vert in verts:
        for i,coord in enumerate(vert):
            if i in [0,2]:
                multiplier = 1
                if i == 2:
                    multiplier = -1
                data.append(multiplier*int(coord*100))
    return data            
    
def get_mixed_vertex_data(obj,store_tmp = False):
    shapes = obj.data.shape_keys
    verts = []
    index = int(obj.active_shape_key_index)
    shape_key = obj.shape_key_add("tmp_mixed_mesh",from_mix=True)
    for vert in shape_key.data:
        verts.append([vert.co[0],vert.co[1],vert.co[2]])
    obj.shape_key_remove(shape_key)            
    obj.active_shape_key_index = index
    if store_tmp:
        default_vert_coords[obj.name] = verts
    return verts    

def get_vertex_data(bm):
    verts = []
    for vert in bm.verts:
        #if vert.hide == False:
        for i,coord in enumerate(vert.co):
            if i in [0,2]:
                multiplier = 1
                if i == 2:
                    multiplier = -1
                verts.append(multiplier*int(coord*100))
    return verts

### get edge information
def get_edge_data(bm):
    edges = []
    for edge in bm.edges:
        #if edge.hide == False:
        if edge.is_boundary:
            for i,vert in enumerate(edge.verts):
                edges.append(vert.index)
    return edges
                


### get triangle information
def get_triangle_data(bm):
    triangles = []
    for face in bm.faces:
        #if face.hide == False:
        for i,vert in enumerate(face.verts):
            triangles.append(vert.index)
    return triangles


### get uv information
def get_uv_data(bm):
    uvs = []
    uv_layer = bm.loops.layers.uv.active
    for vert in bm.verts:
        #if vert.hide == False:
        uv_first = uv_from_vert_first(uv_layer,vert)
        for i,val in enumerate(uv_first):
            if i == 1:
                uvs.append(-val + 1)
            else:
                uvs.append(val)    
    return uvs

def get_bone_matrix(armature,bone,relative=True):
    pose_bone = armature.pose.bones[bone.name]
    
    m = Matrix() ### inverted posebone origin matrix
    m.row[0] = [0,0,1,0]
    m.row[1] = [1,0,0,0]
    m.row[2] = [0,1,0,0]
    m.row[3] = [0,0,0,1]
    
    if bone.parent == None:
        mat_bone_space = m * pose_bone.matrix.copy()
    else:
        if relative:
            mat_bone_space = pose_bone.parent.matrix.inverted() * pose_bone.matrix
        else:
            mat_bone_space = m * pose_bone.matrix
    
    #### remap matrix
    loc, rot, scale = mat_bone_space.decompose()
    
    if not bone.use_inherit_scale:
        scale = (m * pose_bone.matrix).decompose()[2]
    
    loc_mat = Matrix.Translation(loc)
    
    rot_mat = rot.inverted().to_matrix().to_4x4()
    
    scale_mat = Matrix()
    scale_mat[0][0] = scale[1]
    scale_mat[1][1] = scale[0]
    
    mat_bone_space = loc_mat * rot_mat * scale_mat
    
    return mat_bone_space
        
def get_bone_angle(armature,bone,relative=True):
    loc, rot, scale = get_bone_matrix(armature,bone,relative).decompose()
    compat_euler = Euler((0.0,0.0,math.pi),"XYZ")
    angle = -rot.to_euler().z  # negate angle to fit dragonbones angle
        
    return round(math.degrees(angle),2)

def get_bone_pos(armature,bone,scale):
    loc, rot, sca = get_bone_matrix(armature,bone).decompose()
    
    pos_2d = Vector((loc[1],-loc[0])) * scale # flip x and y and negate x to fit dragonbones coordinate system
    return pos_2d 

def get_bone_scale(armature,bone):
    loc, rot, scale = get_bone_matrix(armature,bone).decompose()
    return Vector((round(scale[0],2),round(scale[1],2),round(scale[2],2)))
 
def get_bone_data(armature,bone,scale):
    data = {}
    data["name"] = bone.name
    data["transform"] = {}
    
    ### get bone position
    pos = get_bone_pos(armature,bone,scale)
    bone_default_pos[bone.name] = Vector(pos)
    if pos != Vector((0,0)):
        data["transform"]["x"] = pos[0]
        data["transform"]["y"] = pos[1]
    
    ### get bone angle    
    angle = get_bone_angle(armature,bone)
    bone_default_rot[bone.name] = angle
    if angle != 0:
        data["transform"]["skX"] = angle
        data["transform"]["skY"] = angle
        
    ### get bone scale
    sca = get_bone_scale(armature,bone)
    if sca != Vector((1.0,1.0,1.0)):
        data["transform"]["scX"] = sca[0]
        data["transform"]["scY"] = sca[1]
    
    if int(bone.use_inherit_rotation) != 1:
        data["inheritRotation"] = int(bone.use_inherit_rotation)
    if int(bone.use_inherit_scale) != 1:    
        data["inheritScale"] = int(bone.use_inherit_scale)
    if bone.parent != None:
        data["parent"] = bone.parent.name
    else:
        data["parent"] = armature.name
    data["length"] = int((bone.head - bone.tail).length*scale)
    
    return data

def get_slot_data(obj):
    data = {}
    data["name"] = obj.name
    data["parent"] = obj.parent.name
    #data["color"] = {}
    if len(obj.coa_slot) > 0:
        data["displayIndex"] = obj.coa_slot_index
    color = get_modulate_color(obj)
    if color["rM"] != 100 or color["gM"] != 100 or color["bM"] != 100 or color["aM"] != 100:
        data["color"] = color
    return data
    
def create_texture_dir(texture_path):
    if not os.path.isdir(texture_path):
        os.makedirs(texture_path)

def get_img_tex(obj):
    if len(obj.material_slots) > 0:
        mat = obj.material_slots[0].material
        tex = mat.texture_slots[0].texture
        img = tex.image
        return img

def save_texture(obj,texture_path):
    if len(obj.material_slots) > 0:
        mat = obj.material_slots[0].material
        tex = mat.texture_slots[0].texture
        img = tex.image
        src_path = img.filepath
        src_path = src_path.replace("\\","/")
        src_path = bpy.path.abspath(src_path)
        
        file_name = src_path[src_path.rfind("/")+1:]
        dst_path = os.path.join(texture_path, file_name)
        if os.path.isfile(dst_path):
            os.remove(dst_path)
            
        if os.path.isfile(src_path):
            copyfile(src_path,dst_path)
        else:
            img.save_render(dst_path)

        rel_path = os.path.join("sprites",file_name[:file_name.rfind(".")])
        rel_path = rel_path.replace("\\","/")
        return rel_path
            
class DragonBonesExport(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "coa_tools.export_dragon_bones"
    bl_label = "Dragonbones Export"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    filename_ext = ".json"

    filter_glob = StringProperty(default="*.json",options={'HIDDEN'},)
    bake_anim = BoolProperty(name="Bake Animation", description="If checked, keyframes will be set for each frame. This is good if the Animation has to look exactly as in Blender.",default=False)
    bake_interval = IntProperty(name="Bake Interval",default=1,min=1)
    reduce_size = BoolProperty(name="Reduce Export Size", description="Reduces the export size by writing all data into one row.",default=True)
    generate_atlas = BoolProperty(name="Generate Texture Atlas",description="Generates a Texture Atlas to reduce size and bundle all graphics in one Image",default=True)
    atlas_size = EnumProperty(name="Atlas Size",items=(("AUTOMATIC","Automatic","Automatic"),("MANUAL","Manual","Manual")))
    atlas_dimension = IntVectorProperty(name="Dimension",size=2,default=(512,512))
    unwrap_method = EnumProperty(name="Unwrap Method",items=(("SMART_UV","Smart UV","Smart UV"),("ANGLE_BASED","Angle Based","Angle Based")))
    island_margin = FloatProperty(default=.01,min=0.0,step=.1)
    
    sprite_object = None
    armature = None
    sprites = None
    scale = 0.0
    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self,context):
        layout = self.layout
        col = layout.column()
        col.prop(self,"bake_anim",text="Bake Animation")
        if self.bake_anim:
            col.prop(self,"bake_interval",text="Bake Interval")
        col.prop(self,"reduce_size",text="Reduce Export Size")
        
        if self.generate_atlas:
            box = col.box()
        else:
            box = col    
        box.prop(self,"generate_atlas",text="Generate Texture Atlas")
        if self.generate_atlas:
            row = box.row()
            row.prop(self,"atlas_size",text="Atlas Size",expand=True)
            if self.atlas_size == "MANUAL":
                row = box.row()
                row.prop(self,"atlas_dimension",text="")
            row = box.row()    
            row.prop(self,"unwrap_method",text="Unwrap Method",expand=True)  
            row = box.row()
            row.prop(self,"island_margin",text="Sprite Margin")  
    
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Export Undo")
        self.scale = 1/get_addon_prefs(context).sprite_import_export_scale
        self.sprite_object = get_sprite_object(context.active_object)
        self.armature = get_armature(self.sprite_object)
        self.sprites = get_children(context,self.sprite_object,[])
        self.sprites = sorted(self.sprites, key=lambda obj: obj.location[1], reverse=True) ### sort objects based on the z depth. needed for draw order
        export_path = os.path.dirname(self.filepath)
        texture_path = os.path.join(export_path,"texture","sprites")
        
        
        set_action(context,item=self.sprite_object.coa_anim_collections[1]) # set animation to restpose
        
        create_texture_dir(texture_path)
        
        ### delete base sprite if hidden for export
        for sprite in self.sprites:
            if sprite.type == "MESH":
                if sprite.coa_hide_base_sprite:
                    bpy.context.scene.objects.active = sprite
                    sprite.select = True
                    remove_base_mesh(sprite)
        
        ### if generate atlas is toggled a texture atlas is generated
        if self.generate_atlas:            
            sprites = []            
            for sprite in self.sprites:
                if sprite.type == "MESH":
                    sprites.append(sprite)
            name = self.sprite_object.name+"_atlas"
            generate_texture_atlas(context,sprites,name,self.atlas_dimension[0],self.atlas_dimension[1],self.atlas_size,self.unwrap_method,self.island_margin)
            bpy.data.images[name].save_render(os.path.join(texture_path,name+".png"))
        
        armature["slot"] = []
        
        skin = OrderedDict()
        skin = {
                "name":"",
                "slot":[]
                }
        armature["skin"] = [skin]
        
        for sprite in self.sprites:
            if sprite.type == "MESH":
#                ### find export bones that have to be ignored
#                bones = get_shapekey_driver(sprite)[1]
#                for bone in bones:
#                    if bone.name not in ignore_bones:
#                        ignore_bones.append(bone.name)
                
                armature["slot"].append(get_slot_data(sprite))
                
                display = {"name":sprite.name,"display":[]}
                
                ### export mesh directly when of type "MESH"
                if sprite.coa_type == "MESH":
                    if not self.generate_atlas:
                        tex_path = save_texture(sprite,texture_path)
                    else:
                        
                        tex_path = os.path.join("sprites",self.sprite_object.name+"_atlas")
                        tex_path = tex_path.replace("\\","/")
                    display["display"].append(get_skin_data(sprite,tex_path,self.scale,self.armature,texture_atlas=self.generate_atlas))
                    
                ### loop over all slots if of type "SLOT"    
                elif sprite.coa_type == "SLOT":
                    data_name = sprite.data.name
                    ### loop over all other slot items
                    for i,slot in enumerate(sprite.coa_slot):
                        data = bpy.data.meshes[slot.name]
                        sprite.data = data
                        
                        if not self.generate_atlas:
                            tex_path = save_texture(sprite,texture_path)
                        else:
                            
                            tex_path = os.path.join("sprites",self.sprite_object.name+"_atlas")
                            tex_path = tex_path.replace("\\","/")
                        display["display"].append(get_skin_data(sprite,tex_path,self.scale,self.armature,texture_atlas=self.generate_atlas))
                    sprite.data = bpy.data.meshes[data_name]
                    
                armature["skin"][0]["slot"].append(display)
        armature["name"] = self.sprite_object.name
        armature["bone"] = []
        armature["ik"] = []
        if self.armature == None:
            armature["bone"].append({"name":self.sprite_object.name,"transform":{}})
        else:    
            armature["bone"].append({"name":self.armature.name,"transform":{}})

            for bone in self.armature.data.bones:
                pose_bone = self.armature.pose.bones[bone.name]

                if bone.name not in ignore_bones:
                    armature["bone"].append(get_bone_data(self.armature,bone,self.scale))
                    
                    for const in self.armature.pose.bones[bone.name].constraints:
                        if const.type == "IK" and const.subtarget != "":
                            armature["ik"].append(get_ik_data(self.armature,bone,const))
        
        
        ### get animation data
        if len(self.sprite_object.coa_anim_collections)>0:
            armature["animation"] = []
            armature["animation"] = get_animation_data(context,self.sprite_object,self.armature,self.bake_anim,self.bake_interval)
            
        db_json["armature"] = []
        db_json["armature"].append(armature)
        db_json["name"] = self.sprite_object.name
        
        if self.reduce_size:
            json_file = json.dumps(db_json,separators=(',',':'))
        else:    
            json_file = json.dumps(db_json, indent="\t", sort_keys=False)
        
        text_file = open(self.filepath, "w")
        text_file.write(json_file)
        text_file.close()
        
        bpy.ops.ed.undo()
        bpy.ops.ed.undo_push(message="Dragonbones Export")
        
        return {"FINISHED"}
        