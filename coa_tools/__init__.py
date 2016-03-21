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
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_donate_icon")
        layout.prop(self,"sprite_import_export_scale")
        layout.prop(self,"sprite_thumb_size")


addon_keymaps = []
def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")
    # insert keymap items here
    kmi = km.keymap_items.new("my_operator.select_frame_thumb", type = "F", value = "PRESS")
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
    bpy.types.Scene.coa_ticker = bpy.props.IntProperty()
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new('view3d.move', 'MIDDLEMOUSE', 'PRESS')
        kmi.active = False
        
    bpy.app.handlers.frame_change_post.append(update_sprites)    
    bpy.app.handlers.scene_update_pre.append(update_thumbs)
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
    bpy.app.handlers.scene_update_pre.remove(update_thumbs)
    bpy.app.handlers.load_post.remove(coa_startup)
    unregister_keymaps()
    
         
@persistent
def update_sprites(dummy):
    bpy.context.scene.coa_ticker += 1
    try:
        context = bpy.context
        for obj in bpy.context.visible_objects:
            if "sprite" in obj and obj.animation_data != None and obj.animation_data.action != None and obj.type == "MESH":
                update_uv(bpy.context,obj)
                set_alpha(obj,bpy.context,obj.coa_alpha)
                set_z_value(context,obj,obj.coa_z_value)
                set_modulate_color(obj,context,obj.coa_modulate_color)
                
    except:
        pass
    if bpy.context.scene.coa_ticker%3 == 0:
        bpy.context.scene.update()

@persistent
def update_thumbs(dummy):
    obj = bpy.context.active_object
    if obj != None and not obj.coa_sprite_updated:
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



import atexit

### delete thumbs on blender exit
def delete_thumb_previews():
    thumb_dir_path = os.path.join(tempfile.gettempdir(),"coa_thumbs")
    if os.path.exists(thumb_dir_path):
        shutil.rmtree(thumb_dir_path, ignore_errors=True)        
atexit.register(delete_thumb_previews)