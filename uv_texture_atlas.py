# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Texture Atlas",
    "author": "Andreas Esau, Paul Geraskin",
    "version": (0, 18),
    "blender": (2, 6, 6),
    "location": "Properties > Render",
    "description": "A simple Texture Atlas for baking of many objects. It creates additional UV",
    "wiki_url": "http://code.google.com/p/blender-addons-by-mifth/",
    "tracker_url": "http://code.google.com/p/blender-addons-by-mifth/issues/list",
    "category": "UV"}

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty
import mathutils

class TextureAtlas(bpy.types.Panel):
    bl_label = "Texture Atlas"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    COMPAT_ENGINES = {'BLENDER_RENDER'}
    
    def draw(self, context):
        col = self.layout.column()
        row = self.layout.row()
        split = self.layout.split()
        ob = context.object
        thisScene = context.scene
        row.template_list("UI_UL_list", "template_list_controls", thisScene, "ms_lightmap_groups", thisScene, "ms_lightmap_groups_index", rows=2,  maxrows=5)
        col = row.column(align=True)
        col.operator("scene.ms_add_lightmap_group", icon='ZOOMIN', text="")
        col.operator("scene.ms_del_lightmap_group", icon='ZOOMOUT', text="")
        
        row = self.layout.row(align=True)

        # Resolution and Unwrap types (only if Lightmap group is added)
        if len(context.scene.ms_lightmap_groups) > 0:
            row.prop(context.scene.ms_lightmap_groups[context.scene.ms_lightmap_groups_index], 'resolution', text='Resolution',expand=True)
            row = self.layout.row()
            row.prop(context.scene.ms_lightmap_groups[context.scene.ms_lightmap_groups_index], 'unwrap_type', text='Lightmap',expand=True)
            row = self.layout.row()            

            row = self.layout.row()
            row.operator("scene.ms_remove_other_uv", text="Remove Other UVs",icon="GROUP")
            row.operator("scene.ms_remove_selected", text="Remove Selected Group and UVs",icon="GROUP")          
            row = self.layout.row()
            row = self.layout.row()
            row = self.layout.row()
            row.operator("scene.ms_add_selected_to_group", text="Add Selection To Current Group",icon="GROUP")
            row.operator("scene.ms_select_group", text="Select Current Group",icon="GROUP")

            row = self.layout.row()
            row.operator("object.ms_auto",text="Auto Unwrap",icon="LAMP_SPOT")        
            row = self.layout.row()        
            row.operator("object.ms_run",text="Start Manual Unwrap/Bake",icon="LAMP_SPOT")
            row.operator("object.ms_run_remove",text="Finsh Manual Unwrap/Bake",icon="LAMP_SPOT")   

        
        
class runAuto(bpy.types.Operator):
    bl_idname = "object.ms_auto"
    bl_label = "Auto Unwrapping"
    bl_description = "Auto Unwrapping"
    
    def execute(self, context):
        old_context = context.area.type

        
        group = context.scene.ms_lightmap_groups[context.scene.ms_lightmap_groups_index]
        context.area.type = 'VIEW_3D'
        if context.scene.objects.active != None:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    
        if group.bake == True and len(bpy.data.groups[group.name].objects) > 0:

             res = int(context.scene.ms_lightmap_groups[group.name].resolution)
             bpy.ops.object.ms_create_lightmap(group_name=group.name, resolution=res)  
             bpy.ops.object.ms_merge_objects(group_name=group.name, unwrap=True)
             bpy.ops.object.ms_separate_objects(group_name=group.name) 
                 
        context.area.type = old_context

        return{'FINISHED'}   
        
        
class runStart(bpy.types.Operator):
    bl_idname = "object.ms_run"
    bl_label = "Make Manual Unwrapping Object"
    bl_description = "Makes Manual Unwrapping Object"
    
    def execute(self, context):
        old_context = context.area.type

        
        group = context.scene.ms_lightmap_groups[context.scene.ms_lightmap_groups_index]
        context.area.type = 'VIEW_3D'
        if context.scene.objects.active != None:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    
        if group.bake == True and len(bpy.data.groups[group.name].objects) > 0:

             res = int(context.scene.ms_lightmap_groups[group.name].resolution)
             bpy.ops.object.ms_create_lightmap(group_name=group.name, resolution=res)  
                    
             bpy.ops.object.ms_merge_objects(group_name=group.name, unwrap=False)

        context.area.type = old_context
        return{'FINISHED'}
    

class runFinish(bpy.types.Operator):
    bl_idname = "object.ms_run_remove"
    bl_label = "Remove Manual Unwrapping Object"
    bl_description = "Removes Manual Unwrapping Object"
    
    def execute(self, context):
        old_context = context.area.type

        
        group = context.scene.ms_lightmap_groups[context.scene.ms_lightmap_groups_index]
        context.area.type = 'VIEW_3D'
        if context.scene.objects.active != None:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    
        if group.bake == True and len(bpy.data.groups[group.name].objects) > 0:

             bpy.ops.object.ms_separate_objects(group_name=group.name) 
                      
        context.area.type = old_context
        #bpy.ops.object.select_all(action='DESELECT')
        return{'FINISHED'}
        
    
class uv_layers(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(default="")

   
class vertex_groups(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(default="") 
    
class groups(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(default="") 

class ms_lightmap_groups(bpy.types.PropertyGroup):
    
    #def update(self,context):
        #for object in bpy.data.groups[self.name].objects:
            #for material in object.data.materials:
                #material.texture_slots[self.name].use = self.bake
    
    name = bpy.props.StringProperty(default="")
    bake = bpy.props.BoolProperty(default=True)
    #bake = bpy.props.BoolProperty(default=True, update=update)

    unwrap_type = EnumProperty(name="unwrap_type",items=(('0','Smart_Unwrap', 'Smart_Unwrap'),('1','Lightmap', 'Lightmap'), ('2','No_Unwrap', 'No_Unwrap')))
    resolution = EnumProperty(name="resolution",items=(('256','256','256'),('512','512','512'),('1024','1024','1024'),('2048','2048','2048'),('4096','4096','4096')))
    template_list_controls = StringProperty(default="bake", options={"HIDDEN"})
    
    

class mergedObjects(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(default="")
    vertex_groups = bpy.props.CollectionProperty(type=vertex_groups)
    groups = bpy.props.CollectionProperty(type=groups)
    uv_layers = bpy.props.CollectionProperty(type=uv_layers)
    

class addSelectedToGroup(bpy.types.Operator):
    bl_idname = "scene.ms_add_selected_to_group" 
    bl_label = ""
    bl_description = "Adds selected Objects to current Group"
    
    
    def execute(self, context):
        
        group_name = context.scene.ms_lightmap_groups[context.scene.ms_lightmap_groups_index].name
            
        #Create a New Group if it was deleted.
        isExist = False
        for groupObj in bpy.data.groups:
             if groupObj == group_name:
                 isExist = True
        if isExist == False:
            bpy.data.groups.new(group_name)

        # Add objects to  ag roup    
        if context.scene.objects.active != None:    
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)    
            
        for object in context.selected_objects:
            if object.type == 'MESH' and bpy.data.groups[group_name] not in object.users_group:
                bpy.data.groups[group_name].objects.link(object)
                                    
        return {'FINISHED'}

class selectGroup(bpy.types.Operator):
    bl_idname = "scene.ms_select_group" 
    bl_label = ""
    bl_description = "Selected Objects of current Group"
    
    
    def execute(self, context):
        
        group_name = context.scene.ms_lightmap_groups[context.scene.ms_lightmap_groups_index].name

        if context.scene.objects.active != None:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        for object in bpy.data.groups[group_name].objects:
              object.select = True 
                            
        return {'FINISHED'}    
        
        
class removeFromGroup(bpy.types.Operator):
    bl_idname = "scene.ms_remove_selected" 
    bl_label = ""
    bl_description = "Remove Selected Group and UVs"
    
    ### removeUV method
    def removeUV(self, mesh, name):
             for uv in mesh.data.uv_textures:
                   if uv.name == name:
                        uv.active = True
                        bpy.ops.mesh.uv_texture_remove()
                        
        
        #remove all modifiers
        #for m in mesh.modifiers:
            #bpy.ops.object.modifier_remove(modifier=m.name)
            
    
    def execute(self, context):
        ### set 3dView context
        old_context = context.area.type        
        context.area.type = 'VIEW_3D'
        
        if context.scene.objects.active != None:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        for group in context.scene.ms_lightmap_groups:        
            group_name = group.name

            for object in context.selected_objects:
                  context.scene.objects.active = object
        
                  if object.type == 'MESH' and bpy.data.groups[group_name] in object.users_group:

                         ### remove UV has crash
                         self.removeUV(object, group_name)

                         #### remove from group
                         bpy.data.groups[group_name].objects.unlink(object)
                         object.hide_render = False

                         
        context.area.type = old_context
        return {'FINISHED'}          

class removeOtherUVs(bpy.types.Operator):
    bl_idname = "scene.ms_remove_other_uv" 
    bl_label = ""
    bl_description = "Remove Other UVs from Selected"
    
    
    def execute(self, context):
        group_name = context.scene.ms_lightmap_groups[context.scene.ms_lightmap_groups_index].name
        
        # set 3dView context
        old_context = context.area.type        
        context.area.type = 'VIEW_3D'
        
        if context.scene.objects.active != None:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        #bpy.ops.object.select_all(action='DESELECT')
            
            
        # Remove other UVs of selected objects
        for object in context.selected_objects:
              context.scene.objects.active = object
              if object.type == 'MESH' and bpy.data.groups[group_name] in object.users_group:
    
                   #remove UVs
                   UVLIST = []
                   for uv in object.data.uv_textures:
                         if uv.name != group_name:
                              UVLIST.append(uv.name)
                         
                   for uvName in UVLIST:
                        object.data.uv_textures[uvName].active = True
                        bpy.ops.mesh.uv_texture_remove()                  
                  
                   UVLIST = [] #clear array
                  
                  
        context.area.type = old_context                  
        return {'FINISHED'}          
        
        
class addLightmapGroup(bpy.types.Operator):
    bl_idname = "scene.ms_add_lightmap_group" 
    bl_label = ""
    bl_description = "Adds a new Lightmap Group"
    
    name = StringProperty(name="Group Name",default='lightmap') 

    def execute(self, context):
        group = bpy.data.groups.new(self.name)
        
        item = context.scene.ms_lightmap_groups.add() 
        item.name = group.name
        item.resolution = '1024'
        context.scene.ms_lightmap_groups_index = len(context.scene.ms_lightmap_groups)-1
        
        if len(context.selected_objects) > 0:
             for object in context.selected_objects:
                 context.scene.objects.active = object
                 if context.active_object.type == 'MESH':
                     bpy.data.groups[group.name].objects.link(object)

        
        return {'FINISHED'}
    
    def invoke(self, context, event): 
        wm = context.window_manager 
        return wm.invoke_props_dialog(self) 
    
class delLightmapGroup(bpy.types.Operator):
    bl_idname = "scene.ms_del_lightmap_group" 
    bl_label = ""
    bl_description = "Deletes active Lightmap Group"
    

    def execute(self, context):
        idx = context.scene.ms_lightmap_groups_index
        group_name = context.scene.ms_lightmap_groups[idx].name
        
        # Remove Group
        for groupObj in bpy.data.groups:
             if groupObj.name == group_name:
       
                 # Unhide Objects if they are hidden
                 for obj in bpy.data.groups[group_name].objects:
                      obj.hide_render = False
        
                 bpy.data.groups.remove(bpy.data.groups[context.scene.ms_lightmap_groups[idx].name])
                 
        # Remove Lightmap Group         
        context.scene.ms_lightmap_groups.remove(context.scene.ms_lightmap_groups_index)
        context.scene.ms_lightmap_groups_index -= 1
        if context.scene.ms_lightmap_groups_index < 0:
              context.scene.ms_lightmap_groups_index = 0
        
        return {'FINISHED'}

        
class createLightmap(bpy.types.Operator):
    bl_idname = "object.ms_create_lightmap" 
    bl_label = "TextureAtlas - Generate Lightmap"
    bl_description = "Generates a Lightmap"
    
    group_name = StringProperty(default='')
    resolution = IntProperty(default=1024)
    
    def execute(self, context):  
        
      ### create lightmap uv layout
      
      
      for object in bpy.data.groups[self.group_name].objects:  
          bpy.ops.object.select_all(action='DESELECT')
          object.select = True
          context.scene.objects.active = object
          bpy.ops.object.mode_set(mode = 'EDIT')
          
        
          if context.object.data.uv_textures.active == None:
              bpy.ops.mesh.uv_texture_add()
              context.object.data.uv_textures.active.name = self.group_name
          else:    
              if self.group_name not in context.object.data.uv_textures:
                  bpy.ops.mesh.uv_texture_add()
                  context.object.data.uv_textures.active.name = self.group_name
                  context.object.data.uv_textures[self.group_name].active = True
                  context.object.data.uv_textures[self.group_name].active_render = True
              else:
                  context.object.data.uv_textures[self.group_name].active = True
                  context.object.data.uv_textures[self.group_name].active_render = True
        
          bpy.ops.mesh.select_all(action='SELECT')
        
          ### set Image  
          bpy.ops.object.mode_set(mode = 'EDIT')
          bpy.ops.mesh.select_all(action='SELECT')
          if self.group_name not in bpy.data.images:
              bpy.ops.image.new(name=self.group_name,width=self.resolution,height=self.resolution)
              bpy.ops.object.mode_set(mode = 'EDIT')
              bpy.data.screens['UV Editing'].areas[1].spaces[0].image = bpy.data.images[self.group_name]
          else:
              bpy.ops.object.mode_set(mode = 'EDIT')
              bpy.data.screens['UV Editing'].areas[1].spaces[0].image = bpy.data.images[self.group_name]
              bpy.data.images[self.group_name].generated_type = 'COLOR_GRID'
              bpy.data.images[self.group_name].generated_width = self.resolution
              bpy.data.images[self.group_name].generated_height = self.resolution
            
          if context.scene.objects.active != None:  
              bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
      return{'FINISHED'}        
        
        
class mergeObjects(bpy.types.Operator):
    bl_idname = "object.ms_merge_objects" 
    bl_label = "TextureAtlas - MergeObjects"
    bl_description = "Merges Objects and stores Origins"
    
    group_name = StringProperty(default='')
    unwrap = BoolProperty(default=False)
    
    def execute(self, context):
      
        #objToDelete = None
        bpy.ops.object.select_all(action='DESELECT')
        for obj in context.scene.objects:
             if obj.name == self.group_name + "_mergedObject":
                  obj.select = True
                  context.scene.objects.active = obj
                  bpy.ops.object.delete(use_global=False)        


  
        
        me = bpy.data.meshes.new(self.group_name + '_mergedObject')
        ob_merge = bpy.data.objects.new(self.group_name + '_mergedObject', me)
        ob_merge.location = context.scene.cursor_location   # position object at 3d-cursor
        context.scene.objects.link(ob_merge)                # Link object to scene
        me.update()
        ob_merge.select = False      
      
        activeNowObject = bpy.data.groups[self.group_name].objects[0]
        bpy.ops.object.select_all(action='DESELECT')
        
        OBJECTLIST = []
        for object in bpy.data.groups[self.group_name].objects:
            OBJECTLIST.append(object)   
            object.select = True   
        context.scene.objects.active = activeNowObject      

        
        ### Make Object Single User
        #bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)

        for object in OBJECTLIST:
            
            bpy.ops.object.select_all(action='DESELECT')
            object.select = True
            
            ### activate lightmap uv if existant
            for uv in object.data.uv_textures:
                if uv.name == self.group_name:
                    uv.active = True
                    context.scene.objects.active = object

                    
            ### generate temp Duplicate Objects with copied modifier,properties and logic bricks
            bpy.ops.object.select_all(action='DESELECT')
            object.select = True
            context.scene.objects.active = object
            bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
            activeNowObject = context.scene.objects.active
            activeNowObject.select = True

            ### hide render of original mesh
            object.hide_render = True
            object.hide = True
            object.select = False

            ### delete vertex groups of the object
            #for group in activeNowObject.vertex_groups:
                #id = context.activeNowObject.vertex_groups[group.name]
                #context.activeNowObject.vertex_groups.remove(id)               
                
            ### remove unused UV
            #remove UVs
            UVLIST = []
            for uv in activeNowObject.data.uv_textures:
                  if uv.name != self.group_name:
                       UVLIST.append(uv.name)
                             
            for uvName in UVLIST:
                 activeNowObject.data.uv_textures[uvName].active = True
                 bpy.ops.mesh.uv_texture_remove()     
            
            UVLIST = [] #clear array
            
            
            ### create vertex groups for each selected object
            context.scene.objects.active = bpy.data.objects[activeNowObject.name]
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.vertex_group_add()
            bpy.ops.object.vertex_group_assign()
            id = len(context.object.vertex_groups)-1
            context.active_object.vertex_groups[id].name = object.name
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            
            
            ### save object name and object location in merged object
            item = ob_merge.ms_merged_objects.add()
            item.name = object.name
            #item.scale = mathutils.Vector(object.scale)
            #item.rotation = mathutils.Vector(object.rotation_euler)
            

            ### merge objects together
            bpy.ops.object.select_all(action='DESELECT')
            activeNowObject.select = True
            ob_merge.select = True
            context.scene.objects.active = ob_merge
            bpy.ops.object.join()

        OBJECTLIST = [] #clear array
        
        
        ### make Unwrap    
        bpy.ops.object.select_all(action='DESELECT')        
        ob_merge.select = True
        context.scene.objects.active = ob_merge
        bpy.ops.object.mode_set(mode = 'EDIT')        
        bpy.ops.mesh.select_all(action='SELECT')
        
        if self.unwrap == True and context.scene.ms_lightmap_groups[self.group_name].unwrap_type == '0':
               bpy.ops.uv.smart_project(angle_limit=72.0, island_margin=0.2, user_area_weight=0.0)
        elif self.unwrap == True and context.scene.ms_lightmap_groups[self.group_name].unwrap_type == '1':
               bpy.ops.uv.lightmap_pack(PREF_CONTEXT='ALL_FACES', PREF_PACK_IN_ONE=True, PREF_NEW_UVLAYER=False, PREF_APPLY_IMAGE=False, PREF_IMG_PX_SIZE=1024, PREF_BOX_DIV=48, PREF_MARGIN_DIV=0.2)        
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)    
        
        ### remove all materials
        for material in ob_merge.material_slots:
             bpy.ops.object.material_slot_remove()  
             
        return{'FINISHED'}

        
class separateObjects(bpy.types.Operator):
    bl_idname = "object.ms_separate_objects" 
    bl_label = "TextureAtlas - Separate Objects"
    bl_description = "Separates Objects and restores Origin"
    
    group_name = StringProperty(default='')

    def execute(self, context):
        for obj in context.scene.objects:
             if obj.name == self.group_name + "_mergedObject":
  
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.object.select_all(action='DESELECT')
                ob_merged = obj
                ob_merged.select = True
                groupSeparate = bpy.data.groups.new(ob_merged.name)
                bpy.data.groups[groupSeparate.name].objects.link(ob_merged)
                ob_merged.select = False

                OBJECTLIST = []
                for object in ob_merged.ms_merged_objects:
                      OBJECTLIST.append(object.name)
                      ### select vertex groups and separate group from merged object
                      bpy.ops.object.select_all(action='DESELECT')
                      ob_merged.select = True
                      context.scene.objects.active = ob_merged
                      #context.scene.objects[object.name]
                      #context.scene.objects.active
                      bpy.ops.object.mode_set(mode = 'EDIT')
                      bpy.ops.mesh.select_all(action='DESELECT')
                      context.active_object.vertex_groups.active_index = context.active_object.vertex_groups[object.name].index            
                      bpy.ops.object.vertex_group_select()
                      bpy.ops.mesh.separate(type='SELECTED')
                      bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                      #context.scene.objects.active.select = False
            
                      ### copy UVs
                      ob_separeted = None
                      for obj in groupSeparate.objects:
                           if obj != ob_merged:
                               ob_separeted = obj
                               
                      ob_merged.select = False
                      #ob_separeted = context.selected_objects[0]
                      ob_original = context.scene.objects[object.name]
                      ob_original.hide = False
                      ob_original.select = True
                      context.scene.objects.active = ob_separeted
                      bpy.ops.object.join_uvs()

                      ### unhide render of original mesh
                      ob_original.hide_render = False                      
                      
                      ### delete separeted object
                      bpy.ops.object.select_all(action='DESELECT')
                      ob_separeted.select = True
                      bpy.ops.object.delete(use_global=False)

                OBJECTLIST = [] #clear array                      
                      
                ### delete duplicated object
                bpy.ops.object.select_all(action='DESELECT')
                ob_merged.select = True
                bpy.ops.object.delete(use_global=False)
        
            
        return{'FINISHED'}



def register():
    bpy.utils.register_class(TextureAtlas)
    
    bpy.utils.register_class(addLightmapGroup)
    bpy.utils.register_class(delLightmapGroup)
    bpy.utils.register_class(addSelectedToGroup)
    bpy.utils.register_class(selectGroup)
    bpy.utils.register_class(removeFromGroup)
    bpy.utils.register_class(removeOtherUVs)
    
    bpy.utils.register_class(runAuto)
    bpy.utils.register_class(runStart)
    bpy.utils.register_class(runFinish)
    bpy.utils.register_class(mergeObjects)
    bpy.utils.register_class(separateObjects)
    bpy.utils.register_class(createLightmap)

    bpy.utils.register_class(uv_layers)
    bpy.utils.register_class(vertex_groups)
    bpy.utils.register_class(groups)
    
    bpy.utils.register_class(mergedObjects)
    bpy.types.Object.ms_merged_objects = bpy.props.CollectionProperty(type=mergedObjects)
    
    bpy.utils.register_class(ms_lightmap_groups)
    bpy.types.Scene.ms_lightmap_groups = bpy.props.CollectionProperty(type=ms_lightmap_groups)
    bpy.types.Scene.ms_lightmap_groups_index = bpy.props.IntProperty()
    


def unregister():
    bpy.utils.unregister_class(TextureAtlas)
    
    bpy.utils.unregister_class(addLightmapGroup)
    bpy.utils.unregister_class(delLightmapGroup)
    bpy.utils.unregister_class(addSelectedToGroup)
    bpy.utils.unregister_class(selectGroup)
    bpy.utils.unregister_class(removeFromGroup)
    bpy.utils.unregister_class(removeOtherUVs)
    
    bpy.utils.unregister_class(runAuto)
    bpy.utils.unregister_class(runStart)
    bpy.utils.unregister_class(runFinish)
    bpy.utils.unregister_class(mergeObjects)
    bpy.utils.unregister_class(separateObjects)
    bpy.utils.unregister_class(createLightmap)
    
    bpy.utils.unregister_class(uv_layers)
    bpy.utils.unregister_class(vertex_groups)
    bpy.utils.unregister_class(groups)
    
    bpy.utils.unregister_class(mergedObjects)
    
    bpy.utils.unregister_class(ms_lightmap_groups)
    
    
if __name__ == "__main__":
    register()