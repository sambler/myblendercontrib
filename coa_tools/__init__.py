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
    "version": (0, 1, 0, "Beta"),
    "blender": (2, 75, 0),
    "location": "View 3D > Tools > Cutout Animation Tools",
    "warning": "This addon is still in development.",
    "wiki_url": "https://github.com/ndee85/coa_tools/wiki",
    "tracker_url": "https://github.com/ndee85/coa_tools/issues",
    "category": "Ndee Tools" }


import bpy
import os
import shutil
import tempfile
from bpy.app.handlers import persistent

# load and reload submodules
##################################    
    
from . import developer_utils
modules = developer_utils.setup_addon_modules(__path__, __name__)

from . ui import *
from . ui import preview_collections
from . functions import *

# register
################################## 

import traceback

class ExampleAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    show_donate_icon = bpy.props.BoolProperty(name="Show Donate Icon",default=True)
    sprite_import_export_scale = bpy.props.FloatProperty(name="Sprite import/export scale",default=0.01)
    sprite_thumb_size = bpy.props.IntProperty(name="Sprite thumbnail size",default=48)
    json_export = bpy.props.BoolProperty(name="Experimental Json export",default=False)
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_donate_icon")
        layout.prop(self,"json_export")
        layout.prop(self,"sprite_import_export_scale")
        layout.prop(self,"sprite_thumb_size")


addon_keymaps = []
def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")
    # insert keymap items here
    kmi = km.keymap_items.new("wm.call_menu_pie", type = "F", value = "PRESS")
    kmi.properties.name = "view3d.coa_pie_menu"
    addon_keymaps.append(km)

def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    import bpy.utils.previews
    pcoll2 = bpy.utils.previews.new() 
    pcoll2.my_previews = ()
    preview_collections["coa_thumbs"] = pcoll2
    
    pcoll = bpy.utils.previews.new()
    pcoll.my_previews = ()
    my_icons_dir = os.path.join(os.path.dirname(__file__),"icons")
    pcoll.load("donate_icon", os.path.join(my_icons_dir,"donate_icon.png"),'IMAGE')
    pcoll.load("twitter_icon", os.path.join(my_icons_dir,"twitter_icon.png"),'IMAGE')
    
    preview_collections["main"] = pcoll
    
    
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()
    
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    
    bpy.types.Object.coa_anim_collections = bpy.props.CollectionProperty(type=AnimationCollections)
    bpy.types.Object.coa_uv_default_state = bpy.props.CollectionProperty(type=UVData)
    bpy.types.Object.coa_slot = bpy.props.CollectionProperty(type=SlotData)
    
    bpy.types.Scene.coa_ticker = bpy.props.IntProperty()
    bpy.types.WindowManager.coa_update_uv = bpy.props.BoolProperty(default=False)
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new('view3d.move', 'MIDDLEMOUSE', 'PRESS')
        kmi.active = False
        
    bpy.app.handlers.frame_change_post.append(update_sprites)    
    bpy.app.handlers.scene_update_pre.append(scene_update)
    bpy.app.handlers.load_post.append(coa_startup)

    register_keymaps()
    
def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()
    
    print("Unregistered {}".format(bl_info["name"]))
    bpy.context.window_manager.coa_running_modal = False
    
    bpy.app.handlers.frame_change_post.remove(update_sprites)
    bpy.app.handlers.scene_update_pre.remove(scene_update)
    bpy.app.handlers.load_post.remove(coa_startup)
    
    unregister_keymaps()
    

         
@persistent
def update_sprites(dummy):
    update_scene = False

    context = bpy.context
    objects = []
    
    if hasattr(context,"visible_objects"):
        objects = context.visible_objects
    else:
        objects = bpy.data.objects
    
        
    for obj in objects:
        if "coa_sprite" in obj and obj.animation_data != None and obj.type == "MESH":
            if obj.coa_sprite_frame != obj.coa_sprite_frame_last:
                update_uv(bpy.context,obj)
                obj.coa_sprite_frame_last = obj.coa_sprite_frame
            if obj.coa_alpha != obj.coa_alpha_last:
                set_alpha(obj,bpy.context,obj.coa_alpha)
                obj.coa_alpha_last = obj.coa_alpha
                update_scene = True
            if obj.coa_z_value != obj.coa_z_value_last:
                set_z_value(context,obj,obj.coa_z_value)
                obj.coa_z_value_last = obj.coa_z_value
            if obj.coa_modulate_color != obj.coa_modulate_color_last:
                set_modulate_color(obj,context,obj.coa_modulate_color)
                obj.coa_modulate_color_last = obj.coa_modulate_color
            if obj.coa_type == "SLOT":
                change_slot_mesh(obj,context,obj.coa_slot_index)    

        if update_scene:
            bpy.context.scene.update()

    ### animation wrap mode
    if hasattr(context,"active_object"):
        sprite_object = get_sprite_object(context.active_object)
        if sprite_object != None and sprite_object.coa_animation_loop:
            if context.scene.frame_current > context.scene.frame_end:
                context.scene.frame_current = 0


ticker = 0
@persistent
def scene_update(dummy):
    global ticker
    ticker += 1
    context = bpy.context
    if hasattr(context,"visible_objects"):
        objects = context.visible_objects
    else:
        objects = bpy.data.objects
    if  hasattr(context,"window_manager"):   
        wm = bpy.context.window_manager
        if wm.coa_update_uv:
            for obj in objects:
                if "coa_sprite" in obj and obj.animation_data != None and obj.type == "MESH":
                    if obj.coa_sprite_frame != obj.coa_sprite_frame_last:
                        update_uv(bpy.context,obj)
                        obj.coa_sprite_frame_last = obj.coa_sprite_frame 
                    if ticker%5 == 0:
                        if obj.coa_alpha != obj.coa_alpha_last:
                            set_alpha(obj,bpy.context,obj.coa_alpha)
                            obj.coa_alpha_last = obj.coa_alpha                
                
    if hasattr(bpy.context,"active_object"):
        obj = bpy.context.active_object
        if obj != None and not obj.coa_sprite_updated and "coa_sprite" in obj:
            for thumb in preview_collections["coa_thumbs"]:
                preview_collections["coa_thumbs"][thumb].reload()
            obj.coa_sprite_updated = True


### start modal operator 
def scene_update_callback(scene):
    bpy.app.handlers.scene_update_pre.remove(scene_update_callback)
    bpy.context.window_manager.coa_running_modal = False
    bpy.ops.wm.coa_modal()
    
    if bpy.context.screen.coa_view == "2D":
        set_middle_mouse_move(True)
    elif bpy.context.screen.coa_view == "3D":
        set_middle_mouse_move(False)
        
@persistent
def coa_startup(dummy):
    print("startup coa modal operator")
    bpy.app.handlers.scene_update_pre.append(scene_update_callback)
    
    ### version fix
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            if "sprite" in obj:
                obj["coa_sprite"] = True
                del obj["sprite"]
            if "coa_sprite" in obj:
                obj.coa_sprite_updated = False
                obj.coa_tiles_changed = True
                set_uv_default_coords(bpy.context,obj)


import atexit

### delete thumbs on blender exit
def delete_thumb_previews():
    thumb_dir_path = os.path.join(tempfile.gettempdir(),"coa_thumbs")
    if os.path.exists(thumb_dir_path):
        shutil.rmtree(thumb_dir_path, ignore_errors=True)        
atexit.register(delete_thumb_previews)