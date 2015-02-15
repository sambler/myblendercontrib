#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

bl_info = {
    "name": "Batch Operations / Manager",
    "description": "Modifiers, Materials, Groups management / batch operations",
    "author": "dairin0d, moth3r",
    "version": (0, 5, 2),
    "blender": (2, 7, 0),
    "location": "View3D > Batch category in Tools panel",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"}
#============================================================================#

if "dairin0d" in locals():
    import imp
    imp.reload(dairin0d)
    imp.reload(batch_common)
    imp.reload(batch_modifiers)
    imp.reload(batch_materials)
    imp.reload(batch_groups)
    #imp.reload(batch_transform)

import bpy

import time
import json

from mathutils import Vector

try:
    import dairin0d
    dairin0d_location = ""
except ImportError:
    dairin0d_location = "."

exec("""
from {0}dairin0d.utils_view3d import SmartView3D
from {0}dairin0d.utils_userinput import KeyMapUtils
from {0}dairin0d.utils_ui import NestedLayout, find_ui_area, ui_context_under_coord
from {0}dairin0d.bpy_inspect import prop, BlRna
from {0}dairin0d.utils_addon import AddonManager
""".format(dairin0d_location))

from .batch_common import copyattrs, attrs_to_dict, dict_to_attrs, Pick_Base, LeftRightPanel, change_monitor, after_register_callbacks
from . import batch_modifiers
from . import batch_materials
from . import batch_groups
#from . import batch_transform

addon = AddonManager()

"""
// Temporary note:
if item is property group instance and item["pi"] = 3.14,
in UI it should be displayed like this: layout.prop(item, '["pi"]')

TODO: make it possible to use separately different change-detecting mechanisms?

Make sure copy/pasting doesn't crash Blender after Undo (seems like it doesn't crash, but pasted references to objects are invalid)
(TODO: clear clipbuffers on undo detection)
Make a general mechanism of serializing/deserializing links to ID blocks? (also useful for cut/copy/paste addon)

// add to addon "runtime" settings to hold python objects? (just for the convenience of accessing them from one place)

investigate if it's possible to make a shortcut to jump to certain tab in tool shelf

// seems like ANY menu/enum in panel header will have issues with background menus/enums (report a bug?)


make Batch Materials work in edit mode?

select by some attribute (e.g. by vertex group or mesh datablock)

// (not for Batch Operations, maybe Macro addon?):
preset system for modeling (sort of visual scripting/macro system)
(able to change order and parameters and add/remove operations)
apply to current selection or some vertex group(s)

* Operators
    * Batch apply operator (search field)
    * operator's draw (if not defined, use automatic draw)
    * For: selection, visible, layer, scene, .blend
    * [DONE] Repeat last N actions
* Object/Transform
    * Batch rename with some sort of name pattern detection
    * Set layers
    * Transform summary + ability to modify if possible
    * Coordinate systems?
    * Non-instant evaluation? Or, if determining the moment of change is possible, use instant evaluation?
    * single-click parenting: show a list of top-level objects? (i.e. without parents)
        * Actually there is a nice addon http://blenderaddonlist.blogspot.com/2014/06/addon-parent-to-empty.html
        * That could be shift+click or click operation for all selected objects depending on button.
    * moth3r suggested copy/pasting objects (in particular, so that pasting an object won't create duplicate materials)
    * copy/paste inside group? (in the selected batch groups)
    * for transforms: see Apply menu (rot/pos/scale, visual transform, make duplicates real?)
    * See also: https://github.com/sebastian-k/scripts/blob/master/power_snapping_pies.py (what of this is applicable to batch operations?)
* Material slots?
    ...
* Constraints
    ...
* Mesh layers
    * Notes:
        * different objects may have similarly different layers which mean different things in each case, so unless the user
          has taken the measures to name each layer properly, displaying a table of layer names won't help the user
          understand what each layer is responsible for.
        * copying/assigning layers is possible only between identical geometry
        * basically, the only batch operation that makes sense for default-named layers of inhomogenous data is "Remove"
    * Vertex Groups (also applicable to Lattice) - stored in object
    * Shape keys (also applicable to Lattice and Curve/Surface)
    * UV maps
    * Vertex colors
    * Custom layers
* Layers?
    * see also: Layer Management addon by Bastien Montagne
* Data?
    * replace/override some datas with another data (data type must be same)
    * some data-specific properties?
    * no add, no paste modes, no remove (? or remove the objects?), no "add"/"filter" assign actions
* Objects?
    * aggregate by object types?
    * batch convert object type?
    * replace a number of objects with some other object? (e.g. one type of screw with other type of screw)
"""

#============================================================================#

@addon.Operator(idname="object.batch_properties_copy", space_type='PROPERTIES', label="Batch Properties Copy")
def Batch_Properties_Copy(self, context):
    properties_context = context.space_data.context
    Category = addon.preferences.copy_paste_contexts.get(properties_context)
    if Category is None: return
    pin_id = context.space_data.pin_id
    object_name = (pin_id.name if isinstance(pin_id, bpy.types.Object) else "")
    getattr(bpy.ops.object, "batch_{}_copy".format(Category.category_name))(object_name=object_name)

@addon.Operator(idname="object.batch_properties_paste", space_type='PROPERTIES', label="Batch Properties Paste")
def Batch_Properties_Copy(self, context):
    properties_context = context.space_data.context
    Category = addon.preferences.copy_paste_contexts.get(properties_context)
    if Category is None: return
    getattr(bpy.ops.object, "batch_{}_paste".format(Category.category_name))()

@addon.Preferences.Include
class ThisAddonPreferences:
    refresh_interval = 0.5 | prop("Auto-refresh interval", name="Refresh interval", min=0.0)
    use_panel_left = True | prop("Show in T-panel", name="T (left panel)")
    use_panel_right = False | prop("Show in N-panel", name="N (right panel)")
    default_select_state = True | prop("Default row selection state", name="Rows selected by default")
    use_rename_popup = True | prop("Use a separate dialog for batch renaming", name="Use popup dialog for renaming")
    
    sync_lock = False
    
    def sync_names(self):
        cls = self.__class__
        names = []
        for Category in cls.categories:
            options = getattr(self, Category.category_name_plural)
            if options.synchronized:
                names.append(Category.Category_Name_Plural)
        return "/".join(names)
    
    def sync_copy(self, active_obj):
        cls = self.__class__
        for Category in cls.categories:
            options = getattr(self, Category.category_name_plural)
            if options.synchronized:
                Category.BatchOperations.copy(active_obj, Category.excluded)
    
    def sync_paste(self, context, paste_mode):
        cls = self.__class__
        for Category in cls.categories:
            options = getattr(self, Category.category_name_plural)
            if options.synchronized:
                Category.BatchOperations.paste(options.iterate_objects(context), paste_mode)
                category = getattr(addon.external, Category.category_name_plural)
                category.tag_refresh()
    
    def sync_add(self, active_options, active_category_name_plural):
        if not active_options.synchronized: return False
        cls = self.__class__
        if cls.sync_lock: return False
        cls.sync_lock = True
        
        src_options = None
        for Category in cls.categories:
            if (Category.category_name_plural == active_category_name_plural): continue
            options = getattr(self, Category.category_name_plural)
            if options.synchronized:
                src_options = options
                break
        
        if src_options:
            active_options.synchronize_selection = src_options.synchronize_selection
            active_options.prioritize_selection = src_options.prioritize_selection
            active_options.autorefresh = src_options.autorefresh
            active_options.paste_mode = src_options.paste_mode
            active_options.search_in = src_options.search_in
            active_options.aggregate_mode = src_options.aggregate_mode
        
        cls.sync_lock = False
        return True
    
    def sync_update(self, active_options, active_category_name_plural):
        if not active_options.synchronized: return False
        cls = self.__class__
        if cls.sync_lock: return False
        cls.sync_lock = True
        
        for Category in cls.categories:
            if (Category.category_name_plural == active_category_name_plural): continue
            options = getattr(self, Category.category_name_plural)
            if options.synchronized:
                options.synchronize_selection = active_options.synchronize_selection
                options.prioritize_selection = active_options.prioritize_selection
                options.autorefresh = active_options.autorefresh
                options.paste_mode = active_options.paste_mode
                options.search_in = active_options.search_in
                options.aggregate_mode = active_options.aggregate_mode
        
        cls.sync_lock = False
        return True
    
    def draw(self, context):
        layout = NestedLayout(self.layout)
        
        with layout.row()(alignment='LEFT'):
            layout.prop(self, "refresh_interval")
            layout.prop(self, "use_panel_left")
            layout.prop(self, "use_panel_right")
        
        with layout.row()(alignment='LEFT'):
            layout.prop(self, "default_select_state")
            layout.prop(self, "use_rename_popup")
        
        with layout.row()(alignment='LEFT'):
            with layout.column():
                for Category in self.categories:
                    category = getattr(self, Category.category_name_plural)
                    layout.label(text=Category.Category_Name_Plural+":", icon=Category.category_icon)
            with layout.column():
                for Category in self.categories:
                    category = getattr(self, Category.category_name_plural)
                    layout.prop_menu_enum(category, "quick_access", text="Quick access")

'''
def something_was_drawn():
    was_drawn = False
    was_drawn |= addon.external.modifiers.was_drawn
    was_drawn |= addon.external.materials.was_drawn
    return was_drawn

def on_change():
    addon.external.modifiers.was_drawn = False
    addon.external.modifiers.needs_refresh = True
    addon.external.modifiers.refresh(bpy.context)
    
    addon.external.materials.was_drawn = False
    addon.external.materials.needs_refresh = True
    addon.external.materials.refresh(bpy.context)

@addon.Operator(idname="wm.batch_changes_monitor")
class ChangeMonitoringOperator:
    is_running = False
    script_reload_kmis = []
    last_reset_time = 0.0
    
    def invoke(self, context, event):
        ChangeMonitoringOperator.is_running = True
        ChangeMonitoringOperator.script_reload_kmis = list(KeyMapUtils.search('script.reload'))
        
        wm = context.window_manager
        wm.modal_handler_add(self)
        
        # 'RUNNING_MODAL' MUST be present if modal_handler_add is used!
        return {'PASS_THROUGH', 'RUNNING_MODAL'}
    
    def cancel(self, context):
        ChangeMonitoringOperator.is_running = False
    
    def modal(self, context, event):
        # This doesn't seem to ever happen, but just in case:
        if addon.status != 'REGISTERED':
            self.cancel(context)
            return {'PASS_THROUGH', 'CANCELLED'}
        
        # Scripts cannot be reloaded while modal operators are running
        # Intercept the corresponding event and shut down CursorMonitor
        # (it would be relaunched automatically afterwards)
        for kc, km, kmi in ChangeMonitoringOperator.script_reload_kmis:
            if KeyMapUtils.equal(kmi, event):
                self.cancel(context)
                return {'PASS_THROUGH', 'CANCELLED'}
        
        mouse_context = ui_context_under_coord(event.mouse_x, event.mouse_y)
        if mouse_context and (mouse_context.get("area").type == 'INFO'):
            # let the user at least select info reports while the mouse is over the info area
            return {'PASS_THROUGH'}
        
        # When possible, try to use existing info area, since otherwise
        # temporary switching of area type will cause Blender to constantly update
        info_context = find_ui_area('INFO')
        
        context_override = info_context or mouse_context
        
        if (event.type == 'MOUSEMOVE'):
            if mouse_context:
                x, y = event.mouse_x, event.mouse_y
                r = mouse_context["region"]
                dx = min((x - r.x), (r.x+r.width - x))
                dy = min((y - r.y), (r.y+r.height - y))
                if time.clock() > ChangeMonitoringOperator.last_reset_time + 0.1:
                #if something_was_drawn():
                    if (dx > 3) and (dy > 3): # not too close to region's border
                        # The hope is that, if we call update only on mousemove events,
                        # crashes would happen with lesser pribability
                        if context_override and context_override.get("area"):
                            change_monitor.update(**context_override)
                            if change_monitor.something_changed:
                                on_change()
                            #elif time.clock() > ChangeMonitoringOperator.last_reset_time + 1:
                            #    on_change()
        elif 'MOUSEMOVE' in event.type:
            pass
        elif 'TIMER' in event.type:
            pass
        elif event.type == 'NONE':
            pass
        else:
            ChangeMonitoringOperator.last_reset_time = time.clock()
        
        return {'PASS_THROUGH'}

# We need to invoke batch_changes_monitor from somewhere other than
# keymap event, since keymap event can lock the batch_changes_monitor
# operator to the Preferences window. Scene update, on the other hand,
# is always in the main window.
# WARNING: if addon is saved as enabled in user preferences,
# for some reason scene_update_post/scene_update_pre callbacks
# won't be working until scripts are reloaded.
# BUT: if we put bpy.app.handlers.persistent decorator, it will work.
@bpy.app.handlers.persistent
def scene_update_post(scene):
    if not ChangeMonitoringOperator.is_running:
        ChangeMonitoringOperator.is_running = True
        bpy.ops.wm.batch_changes_monitor('INVOKE_DEFAULT')
'''

@bpy.app.handlers.persistent
def scene_update_post(scene):
    if after_register_callbacks:
        callbacks = tuple(after_register_callbacks)
        after_register_callbacks.clear()
        for callback in callbacks:
            callback()

def register():
    # I couldn't find a way to avoid the unpredictable crashes,
    # and some actions (like changing a material in material slot)
    # cannot be detected through the info log anyway.
    addon.handler_append("scene_update_post", scene_update_post)
    
    addon.register()
    
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Window")
        kmi = km.keymap_items.new("object.batch_properties_copy", 'C', 'PRESS', ctrl=True)
        kmi = km.keymap_items.new("object.batch_properties_paste", 'V', 'PRESS', ctrl=True)

def unregister():
    # Note: if we remove from non-addon keyconfigs, the keymap registration
    # won't work on the consequent addon enable/reload (until Blender restarts)
    kc = bpy.context.window_manager.keyconfigs.addon
    KeyMapUtils.remove("object.batch_properties_copy", place=kc)
    KeyMapUtils.remove("object.batch_properties_paste", place=kc)
    
    addon.unregister()
    
    # don't remove this, or on next addon enable the monitor will consider itself already running
    #ChangeMonitoringOperator.is_running = False
