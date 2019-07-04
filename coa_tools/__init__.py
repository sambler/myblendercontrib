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
    "name": "COA Tools",
    "description": "This Addon provides a Toolset for a 2D Animation Workflow.",
    "author": "Andreas Esau",
    "version": (1, 0, 4),
    "blender": (2, 80, 0),
    "location": "View 3D > Tools > Cutout Animation Tools",
    "warning": "",
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

from . import coa_properties as props

from . import ui as user_interface
from . ui import preview_collections
from . operators.pie_menu import preview_collections_pie
from . functions import *

from . operators import create_sprite_object
from . operators import help_display

from . operators import advanced_settings
from . operators import animation_handling
from . operators import create_ortho_cam
from . operators import create_spritesheet_preview
from . operators import donations
from . operators import draw_bone_shape
from . operators import edit_armature
from . operators import edit_mesh
from . operators import edit_shapekey
from . operators import edit_weights
from . operators import import_sprites
from . operators import material_converter
from . operators import modal_update
from . operators import pie_menu
from . operators import slot_handling
from . operators import toggle_animation_area
from . operators import view_sprites

# register
################################## 

import traceback



class COAToolsPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    
    alpha_update_frequency: bpy.props.IntProperty(name="Alpha Update Frequency",default=1,min=1,description="Updates alpha on each x frame.")
    show_donate_icon: bpy.props.BoolProperty(name="Show Donate Icon",default=False)
    sprite_import_export_scale: bpy.props.FloatProperty(name="Sprite import/export scale",default=0.01)
    sprite_thumb_size: bpy.props.IntProperty(name="Sprite thumbnail size",default=48)
    json_export: bpy.props.BoolProperty(name="Experimental Json export",default=False)
    dragon_bones_export: bpy.props.BoolProperty(name="Dragonbones Export",default=False)
    enable_spritesheets: bpy.props.BoolProperty(name="Enable Spritesheets",default=False, description="This feature is deprecated and should not be used for future projects. Use this only for older projects.")
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_donate_icon")
        layout.prop(self, "dragon_bones_export")
        layout.prop(self, "sprite_import_export_scale")
        layout.prop(self, "sprite_thumb_size")
        layout.prop(self, "alpha_update_frequency")


classes = (
    COAToolsPreferences,
    #properties
    props.UVData,
    props.SlotData,
    props.Event,
    props.TimelineEvent,
    props.AnimationCollections,
    props.ObjectProperties,
    props.SceneProperties,
    props.MeshProperties,
    props.BoneProperties,
    props.WindowManagerProperties,

    #operator
    create_sprite_object.COATOOLS_OT_CreateSpriteObject,
    import_sprites.JsonImportData,
    import_sprites.COATOOLS_OT_CreateMaterialGroup,
    import_sprites.COATOOLS_OT_ImportSprite,
    import_sprites.COATOOLS_OT_ImportSprites,
    import_sprites.COATOOLS_OT_LoadJsonData,
    import_sprites.COATOOLS_UL_JsonImport,
    import_sprites.COATOOLS_OT_ReImportSprite,

    user_interface.COATOOLS_OT_ChangeShadingMode,
    user_interface.COATOOLS_PT_Info,
    user_interface.COATOOLS_PT_ObjectProperties,
    user_interface.COATOOLS_PT_Tools,
    user_interface.COATOOLS_UL_AnimationCollections,
    user_interface.COATOOLS_UL_EventCollection,
    user_interface.COATOOLS_OT_SelectChild,
    user_interface.COATOOLS_PT_Collections,


    view_sprites.COATOOLS_OT_ChangeZOrdering,
    view_sprites.COATOOLS_OT_ViewSprite,

    advanced_settings.COATOOLS_OT_AdvancedSettings,

    edit_mesh.COATOOLS_OT_ReprojectSpriteTexture,
    edit_mesh.COATOOLS_OT_GenerateMeshFromEdgesAndVerts,
    edit_mesh.COATOOLS_OT_Fill,
    edit_mesh.COATOOLS_OT_DrawContour,
    edit_mesh.COATOOLS_OT_PickEdgeLength,

    edit_armature.COATOOLS_OT_BindMeshToBones,
    edit_armature.COATOOLS_OT_QuickArmature,
    edit_armature.COATOOLS_OT_SetStretchBone,
    edit_armature.COATOOLS_OT_RemoveIK,
    edit_armature.COATOOLS_OT_SetIK,
    edit_armature.COATOOLS_OT_CreateStretchIK,
    edit_armature.COATOOLS_OT_RemoveStretchIK,

    edit_shapekey.COATOOLS_OT_LeaveSculptmode,
    edit_shapekey.COATOOLS_OT_ShapekeyAdd,
    edit_shapekey.COATOOLS_OT_ShapekeyRemove,
    edit_shapekey.COATOOLS_OT_ShapekeyRename,
    edit_shapekey.COATOOLS_OT_EditShapekeyMode,

    edit_weights.COATOOLS_OT_EditWeights,

    slot_handling.COATOOLS_OT_ExtractSlots,
    slot_handling.COATOOLS_OT_CreateSlotObject,
    slot_handling.COATOOLS_OT_MoveSlotItem,
    slot_handling.COATOOLS_OT_RemoveFromSlot,

    animation_handling.COATOOLS_OT_AddKeyframe,
    animation_handling.COATOOLS_OT_DuplicateAnimationCollection,
    animation_handling.COATOOLS_OT_AddAnimationCollection,
    animation_handling.COATOOLS_OT_RemoveAnimationCollection,
    animation_handling.COATOOLS_OT_CreateNlaTrack,
    animation_handling.COATOOLS_OT_BatchRender,
    animation_handling.COATOOLS_OT_AddEvent,
    animation_handling.COATOOLS_OT_RemoveEvent,
    animation_handling.COATOOLS_OT_AddTimelineEvent,
    animation_handling.COATOOLS_OT_RemoveTimelineEvent,

    create_ortho_cam.COATOOLS_OT_CreateOrtpographicCamera,
    create_ortho_cam.COATOOLS_OT_AlignCamera,

    create_spritesheet_preview.COATOOLS_OT_SelectFrameThumb,

    help_display.COATOOLS_OT_ShowHelp,

    draw_bone_shape.COATOOLS_OT_DrawBoneShape,

    pie_menu.COATOOLS_MT_menu,
    pie_menu.COATOOLS_MT_keyframe_menu_01,
    pie_menu.COATOOLS_MT_keyframe_menu_add,
    pie_menu.COATOOLS_MT_keyframe_menu_remove,

    toggle_animation_area.COATOOLS_OT_ToggleAnimationArea,


)

addon_keymaps = []
def register_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new('view3d.move', 'MIDDLEMOUSE', 'PRESS')
        kmi.active = False

    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    # insert keymap items here
    kmi = km.keymap_items.new("wm.call_menu_pie", type = "F", value = "PRESS")
    kmi.properties.name = "COATOOLS_MT_menu"
    addon_keymaps.append(km)

def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    # register classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # register tools
    bpy.utils.register_tool(edit_mesh.COATOOLS_TO_DrawPolygon, after={"builtin.cursor"}, separator=True, group=True)

    # register props and keymap
    props.register()
    register_keymaps()

    # create handler
    bpy.app.handlers.depsgraph_update_post.append(update_properties)
    bpy.app.handlers.frame_change_post.append(update_properties)
    bpy.app.handlers.load_post.append(check_view_2D_3D)
    bpy.app.handlers.load_post.append(set_shading)


def unregister():
    # unregister classes
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # unregister tools
    bpy.utils.unregister_tool(edit_mesh.COATOOLS_TO_DrawPolygon)

    # unregisters props and keymap
    props.unregister()
    unregister_keymaps()

    # delete handler
    bpy.app.handlers.depsgraph_update_post.remove(update_properties)
    bpy.app.handlers.frame_change_post.remove(update_properties)
    bpy.app.handlers.load_post.remove(check_view_2D_3D)
    bpy.app.handlers.load_post.remove(set_shading)


@persistent
def check_view_2D_3D(dummy):
    context = bpy.context
    if context != None:
        scene = context.scene
        if scene != None:
            if scene.coa_tools.view == "2D":
                set_middle_mouse_move(True)
            elif scene.coa_tools.view == "3D":
                set_middle_mouse_move(False)


@persistent
def set_shading(dummy):
    for obj in bpy.data.objects:
        if "coa_sprite_object" in obj:
            for screen in bpy.data.screens:
                for area in screen.areas:
                    if area.type == "VIEW_3D":
                        area.spaces[0].shading.type = "RENDERED"
            break

@persistent
def update_properties(dummy):
    context = bpy.context
    for obj in context.view_layer.objects:
        if obj.coa_tools.alpha != obj.coa_tools.alpha_last:
            set_alpha(obj, context, obj.coa_tools.alpha)
            obj.coa_tools.alpha_last = obj.coa_tools.alpha
        
        if obj.coa_tools.modulate_color != obj.coa_tools.modulate_color_last:
            set_modulate_color(obj, context, obj.coa_tools.modulate_color)
            obj.coa_tools.modulate_color_last = obj.coa_tools.modulate_color
        
        if obj.coa_tools.z_value != obj.coa_tools.z_value_last:
            set_z_value(context, obj, obj.coa_tools.z_value)
            obj.coa_tools.z_value_last = obj.coa_tools.z_value
        
        if obj.coa_tools.slot_index != obj.coa_tools.slot_index_last:
            change_slot_mesh_data(bpy.context, obj)
            obj.coa_tools.slot_index_last = obj.coa_tools.slot_index