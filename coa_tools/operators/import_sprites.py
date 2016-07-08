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

######################################################################################################################################### Import Single Sprite
class ImportSprite(bpy.types.Operator):
    bl_idname = "wm.coa_import_sprite"
    bl_label = "Import Sprite"
    bl_options = {"REGISTER","UNDO"}
    
    path = StringProperty(name="Sprite Path", default="",subtype="FILE_PATH")
    pos = FloatVectorProperty(default=Vector((0,0,0)))
    scale = FloatProperty(name="Sprite Scale",default = .01)
    offset = FloatVectorProperty(default=Vector((0,0,0)))
    tilesize = FloatVectorProperty(default = Vector((1,1)),size=2)
    parent = StringProperty(name="Parent Object",default="None")
    
    
    def create_mesh(self,context,name="Sprite",width=100,height=100,pos=Vector((0,0,0))):
        me = bpy.data.meshes.new(name)
        me.show_double_sided = True
        obj = bpy.data.objects.new(name,me)
        context.scene.objects.link(obj)
        context.scene.objects.active = obj
        obj.select = True
        
        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(me)
        vert1 = bm.verts.new(Vector((0,0,-height))*self.scale)
        vert2 = bm.verts.new(Vector((width,0,-height))*self.scale)
        vert3 = bm.verts.new(Vector((width,0,0))*self.scale)
        vert4 = bm.verts.new(Vector((0,0,0))*self.scale)
        
        bm.faces.new([vert1,vert2,vert3,vert4])
        
        bmesh.update_edit_mesh(me)
        bpy.ops.object.mode_set(mode="OBJECT")
        obj.data.uv_textures.new("UVMap")
        set_uv_default_coords(context,obj)
        
        obj.location = Vector((pos[0],pos[1],-pos[2]))*self.scale + Vector((self.offset[0],self.offset[1],self.offset[2]))*self.scale
        obj["coa_sprite"] = True
        if self.parent != "None":
            obj.parent = bpy.data.objects[self.parent]
        return obj
    
    def create_material(self,context,obj,name="Sprite"):
        mat = bpy.data.materials.new(name)
        #mat.use_shadeless = True
        mat.use_transparency = True
        mat.alpha = 0.0
        mat.specular_intensity = 0.0
        mat.diffuse_intensity = 1.0
        mat.emit = 1.0
        mat.use_object_color = True
        mat.diffuse_color = (1.0,1.0,1.0)
        obj.data.materials.append(mat)
        return mat
    
    def create_texture(self,context,mat,img,name="Sprite"):
        tex = bpy.data.textures.new(name,"IMAGE")
        tex.extension = "CLIP"
        tex.filter_type = "BOX"
        tex.image = img
        tex_slot = mat.texture_slots.add()
        tex_slot.texture = tex
        tex_slot.use_map_alpha = True
        
        if img.source == "MOVIE":
            tex.image_user.frame_duration = img.frame_duration
            tex.image_user.frame_start = 0
            tex.image_user.use_auto_refresh = True
    
    def execute(self,context):
        if os.path.exists(self.path):
            data = bpy.data
            sprite_name = os.path.basename(self.path)
            
            sprite_found = False
            for image in bpy.data.images:
                if os.path.exists(bpy.path.abspath(image.filepath)) and os.path.exists(self.path):
                    if os.path.samefile(bpy.path.abspath(image.filepath),self.path):
                        sprite_found = True
                        img = image
                        img.reload()
                        break
            if not sprite_found:
                img = data.images.load(self.path)
                
            obj = self.create_mesh(context,name=img.name,width=img.size[0],height=img.size[1],pos=self.pos)
            mat = self.create_material(context,obj,name=img.name)
            tex = self.create_texture(context,mat,img,name=img.name)
            msg = sprite_name + " Sprite created."
            assign_tex_to_uv(img,obj.data.uv_textures.active)
            
            obj.coa_sprite_dimension = Vector((get_local_dimension(obj)[0],0,get_local_dimension(obj)[1]))
            
            obj.coa_tiles_x = self.tilesize[0]
            obj.coa_tiles_y = self.tilesize[1]
            
            selected_objects = []
            for obj2 in context.selected_objects:
                selected_objects.append(obj2)
                if obj2 != context.active_object:
                    obj2.select = False
            obj.coa_z_value = -self.pos[1]
            for obj2 in selected_objects:
                obj2.select = True
            
            self.report({'INFO'},msg)
            return{'FINISHED'}
        else:
            self.report({'WARNING'},'File does not exist.')
            return{'CANCELLED'}
    
    def invoke(self, context, event):
        wm = context.window_manager 
        return wm.invoke_props_dialog(self)
        
######################################################################################################################################### Import Multiple Sprites
class ImportSprites(bpy.types.Operator, ImportHelper):
    bl_idname = "import.coa_import_sprites" 
    bl_label = "Import Sprites"
    bl_description="Imports sprites into Blender"
    
    files = CollectionProperty(type=bpy.types.PropertyGroup)
    
    filepath = StringProperty(
        default="test"
         )
    
    filter_image = BoolProperty(default=True,options={'HIDDEN','SKIP_SAVE'})
    filter_movie = BoolProperty(default=True,options={'HIDDEN','SKIP_SAVE'})
    filter_folder = BoolProperty(default=True,options={'HIDDEN','SKIP_SAVE'})
    filter_glob = StringProperty(default="*.json",options={'HIDDEN'})

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting = None
    
    def execute(self, context):
        bpy.context.space_data.viewport_shade = "TEXTURED"
        bpy.context.scene.game_settings.material_mode = "GLSL"
        
        ext = os.path.splitext(self.filepath)[1]
        folder = (os.path.dirname(self.filepath))
        
        for object in bpy.context.selected_objects:
            object.select = False
                
        sprite_object = get_sprite_object(context.active_object)            
        #if ext in [".png",".jpg",".psd",".jpeg",".gif"] or ext in [".avi",".wmv",".webm",".mpeg",".mp4",".mov"]:
        if ext not in [".json"]:
            for i in self.files:
                filepath = (os.path.join(folder, i.name))
                bpy.ops.wm.coa_import_sprite(path=filepath,parent=sprite_object.name,scale=get_addon_prefs(context).sprite_import_export_scale)
        else:
            data_file = open(self.filepath)
            sprite_data = json.load(data_file)
            data_file.close()
            
            if "name" in sprite_data:
                sprite_object.name = sprite_data["name"]
                
            if "nodes" in sprite_data:
                for i,sprite in enumerate(sprite_data["nodes"]):
                    filepath = os.path.join(folder,sprite["resource_path"])
                    pos = [sprite["position"][0],-sprite["z"],sprite["position"][1]]
                    offset = [sprite["offset"][0],0,sprite["offset"][1]]
                    parent = sprite_object.name
                    tilesize = [sprite["tiles_x"],sprite["tiles_y"]]
                    scale = get_addon_prefs(context).sprite_import_export_scale
                    
                    bpy.ops.wm.coa_import_sprite(path = filepath, pos = pos, offset = offset, parent = parent, tilesize = tilesize, scale = scale)
                    obj = context.active_object
                    obj.parent = sprite_object
                    
            context.scene.objects.active = sprite_object
        if bpy.context.screen.coa_view == "3D":
            bpy.ops.view3d.viewnumpad(type="FRONT")
        if context.space_data.region_3d.is_perspective:
            bpy.ops.view3d.view_persportho()
        bpy.ops.ed.undo_push(message="Sprite Import")                   
        return{'FINISHED'}
