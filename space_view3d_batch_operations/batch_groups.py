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

#============================================================================#

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
from {0}dairin0d.utils_blender import Selection
from {0}dairin0d.utils_userinput import KeyMapUtils
from {0}dairin0d.utils_ui import NestedLayout, tag_redraw
from {0}dairin0d.bpy_inspect import prop, BlRna, BlEnums, bpy_struct
from {0}dairin0d.utils_accumulation import Aggregator
from {0}dairin0d.utils_addon import AddonManager
""".format(dairin0d_location))

from .batch_common import (
    copyattrs, attrs_to_dict, dict_to_attrs, PatternRenamer,
    Pick_Base, LeftRightPanel, make_category,
    round_to_bool, is_visible, has_common_layers, idnames_separator
)

addon = AddonManager()

#============================================================================#
Category_Name = "Group"
CATEGORY_NAME = Category_Name.upper()
category_name = Category_Name.lower()
Category_Name_Plural = "Groups"
CATEGORY_NAME_PLURAL = Category_Name_Plural.upper()
category_name_plural = Category_Name_Plural.lower()
category_icon = 'GROUP'

Group = bpy.types.Group

class BatchOperations:
    clipbuffer = None
    
    @classmethod
    def to_group(cls, group):
        if isinstance(group, Group): return group
        return bpy.data.groups.get(group)
    
    @classmethod
    def add_group_to_obj(cls, obj, idname):
        group = cls.to_group(idname)
        if not group: return
        if obj.name not in group.objects: group.objects.link(obj)
    
    @classmethod
    def clear_obj_groups(cls, obj, idnames=None, check_in=True):
        for group in bpy.data.groups:
            if (idnames is None) or ((group.name in idnames) == check_in):
                if obj.name in group.objects: group.objects.unlink(obj)
    
    @classmethod
    def clean_name(cls, group):
        return group.name
    
    @classmethod
    def iter_names(cls, obj):
        for group in bpy.data.groups:
            if obj.name in group.objects: yield group.name
    
    @classmethod
    def iter_idnames(cls, obj):
        for group in bpy.data.groups:
            if obj.name in group.objects: yield group.name
    
    @classmethod
    def iter_scene_objs_idnames(cls, scene):
        scene_objects = set(scene.objects)
        for group in bpy.data.groups:
            for obj in group.objects:
                if obj in scene_objects: yield (obj, group.name)
    
    @classmethod
    def enum_all(cls):
        for group in bpy.data.groups:
            yield (group.name, group.name, group.name)
    
    @classmethod
    def icon_kwargs(cls, idname, use_value=True):
        return {"icon": category_icon}
    
    @classmethod
    def iterate(cls, search_in, context=None):
        if search_in != 'FILE':
            for obj in cls.iterate_objects(search_in, context):
                for group in bpy.data.groups:
                    if obj.name in group.objects: yield group
        else:
            yield from bpy.data.groups
    
    @classmethod
    def iterate_objects(cls, search_in, context=None):
        if context is None: context = bpy.context
        scene = context.scene
        if search_in == 'SELECTION':
            for obj in context.selected_objects:
                yield obj
        elif search_in == 'VISIBLE':
            for obj in scene.objects:
                if is_visible(obj, scene):
                    yield obj
        elif search_in == 'LAYER':
            for obj in scene.objects:
                if has_common_layers(obj, scene):
                    yield obj
        elif search_in == 'SCENE':
            for obj in scene.objects:
                yield obj
        elif search_in == 'FILE':
            for obj in bpy.data.objects:
                yield obj
    
    @classmethod
    def split_idnames(cls, idnames):
        if idnames is None: return None
        if not isinstance(idnames, str): return set(idnames)
        return set(idnames.split(idnames_separator))
    
    @classmethod
    def new(cls, idname):
        group = bpy.data.groups.new(idname)
        return group.name
    
    @classmethod
    def set_attr(cls, name, value, objects, idnames, **kwargs):
        idnames = cls.split_idnames(idnames)
        
        if name == "use_fake_user":
            obj = None
            
            for idname in idnames:
                group = cls.to_group(idname)
                if not group: continue
                
                if value:
                    # can't set use_fake_user if 0 users
                    if group.users == 0:
                        if obj is None: obj = bpy.data.objects.new("TmpObj", None)
                        group.objects.link(obj)
                else:
                    # can't unset use_fake_user if fake is the only user
                    if group.users == 1:
                        if obj is None: obj = bpy.data.objects.new("TmpObj", None)
                        group.objects.link(obj)
                
                group.use_fake_user = value
                
                if obj: group.objects.unlink(obj)
            
            if obj: bpy.data.objects.remove(obj)
        else:
            use_kwargs = False
            
            _setattr = setattr
            if isinstance(value, str):
                if PatternRenamer.is_pattern(value):
                    _setattr = PatternRenamer.apply_to_attr
                    use_kwargs = True
            
            if not use_kwargs: kwargs = {}
            
            for obj in objects:
                if isinstance(obj, Group):
                    if obj.name in idnames:
                        _setattr(obj, name, value, **kwargs)
                else:
                    for group in bpy.data.groups:
                        if obj.name not in group.objects: continue
                        if group.name in idnames:
                            _setattr(ms.group, name, value, **kwargs)
    
    @classmethod
    def clear(cls, objects):
        for obj in objects:
            cls.clear_obj_groups(obj)
    
    @classmethod
    def add(cls, objects, idnames):
        idnames = cls.split_idnames(idnames)
        for obj in objects:
            for idname in idnames:
                cls.add_group_to_obj(obj, idname)
    
    @classmethod
    def remove(cls, objects, idnames, from_file=False):
        cls.assign('REPLACE', None, objects, idnames, "", from_file)
    
    @classmethod
    def find_objects(cls, idnames, search_in, context=None):
        idnames = cls.split_idnames(idnames)
        groups = [group for group in bpy.data.groups if group.name in idnames]
        for obj in cls.iterate_objects(search_in, context):
            if any((obj.name in group.objects) for group in groups):
                yield obj
    
    @classmethod
    def select(cls, context, idnames, operation='SET'):
        idnames = cls.split_idnames(idnames)
        groups = [group for group in bpy.data.groups if group.name in idnames]
        data = {obj:"select" for obj in context.scene.objects if any((obj.name in group.objects) for group in groups)}
        Selection(context).update(data, operation)
        #for obj in context.scene.objects:
        #    obj.select = any((obj.name in group.objects) for group in groups)
    
    @classmethod
    def purge(cls, even_with_fake_users, idnames=None):
        if idnames is None:
            if even_with_fake_users:
                fake_idnames = (group.name for group in bpy.data.groups if group.use_fake_user and (group.users == 1))
                cls.set_attr("use_fake_user", False, None, fake_idnames)
            for group in tuple(bpy.data.groups):
                if group.users > 0: continue
                bpy.data.groups.remove(group)
        else:
            cls.remove(None, idnames, True)
            cls.set_attr("use_fake_user", False, None, idnames)
            idnames = cls.split_idnames(idnames)
            for group in tuple(bpy.data.groups):
                if group.name in idnames:
                    bpy.data.groups.remove(group)
    
    @classmethod
    def copy(cls, active_obj, exclude=()):
        if not active_obj:
            cls.clipbuffer = []
        else:
            cls.clipbuffer = [group.name for group in bpy.data.groups
                if (group.name not in exclude) and (active_obj.name in group.objects)]
    
    @classmethod
    def paste(cls, objects, paste_mode):
        idnames = cls.clipbuffer
        if idnames is None: return
        if paste_mode != 'AND':
            for obj in objects:
                if paste_mode == 'SET': cls.clear_obj_groups(obj)
                for idname in idnames:
                    cls.add_group_to_obj(obj, idname)
        else:
            for obj in objects:
                cls.clear_obj_groups(obj, idnames, False)
    
    @classmethod
    def merge_identical(cls):
        unique = set(bpy.data.groups)
        identical = []
        # ignore all properties from bpy_struct
        ignore = {"name", "id_data", "users", "use_fake_user", "tag", "is_updated", "is_updated_data", "is_library_indirect", "library"}
        
        for item in bpy.data.groups:
            duplicates = None
            unique.discard(item)
            
            for item2 in unique:
                if BlRna.compare(item, item2, ignore=ignore):
                    if duplicates is None: duplicates = {item}
                    duplicates.add(item2)
            
            if duplicates is not None:
                identical.append(duplicates)
                unique.difference_update(duplicates)
        
        for duplicates in identical:
            # find best candidate for preservation
            best, best_users, best_len = None, 0, 0
            for item in duplicates:
                if item.users >= best_users:
                    is_better = (item.users > best_users)
                    is_better |= (best_len <= 0)
                    is_better |= (len(item.name) < best_len)
                    if is_better:
                        best, best_users, best_len = item, item.users, len(item.name)
            duplicates.discard(best)
            src_idnames = idnames_separator.join(item.name for item in duplicates)
            dst_idname = best.name
            cls.assign('REPLACE', None, None, src_idnames, dst_idname, from_file=True, purge=True)
    
    assign_mode_default = 'ADD'
    assign_mode_default1 = 'FILTER'
    assign_mode_default2 = 'OVERRIDE'
    assign_modes = [
        ('ADD', "Add", "Add"),
        ('FILTER', "Filter", "Filter"),
        ('REPLACE', "Replace", "Replace"),
        ('OVERRIDE', "Override", "Override"),
    ]
    @classmethod
    def assign(cls, assign_mode, active_obj, objects, src_idnames, dst_idnames, from_file=False, purge=False):
        src_idnames = cls.split_idnames(src_idnames) # can be None
        dst_idnames = cls.split_idnames(dst_idnames)
        
        if assign_mode == 'ADD': # previously known as "Ensure"
            for obj in objects:
                existing_idnames = set(cls.iter_idnames(obj))
                idnames_to_add = dst_idnames.difference(existing_idnames)
                idnames_to_add.discard("")
                
                for idname in idnames_to_add:
                    cls.add_group_to_obj(obj, idname)
        elif assign_mode == 'FILTER':
            for obj in objects:
                for group in bpy.data.groups:
                    if obj.name not in group.objects: continue
                    if group.name not in dst_idnames:
                        group.objects.unlink(obj)
        else:
            replaced_idnames = set()
            
            dst_groups = set(cls.to_group(idname) for idname in sorted(dst_idnames) if idname)
            
            objects = (bpy.data.objects if from_file else tuple(objects)) # need to iterate multiple times
            
            if assign_mode == 'REPLACE':
                def should_replace(group):
                    if (src_idnames is None) or (group.name in src_idnames):
                        replaced_idnames.add(group.name)
                        return True
                    return False
                
                for obj in objects:
                    for group in bpy.data.groups:
                        if obj.name not in group.objects: continue
                        
                        if should_replace(group):
                            group.objects.unlink(obj)
                            
                            for dst_group in dst_groups:
                                if (obj.name not in dst_group.objects):
                                    dst_group.objects.link(obj)
            else:
                def should_replace(group):
                    if (group.name not in dst_idnames):
                        replaced_idnames.add(group.name)
                        return True
                    return False
                
                for obj in objects:
                    for group in bpy.data.groups:
                        if obj.name not in group.objects: continue
                        
                        if should_replace(group):
                            group.objects.unlink(obj)
                    
                    for dst_group in dst_groups:
                        if (obj.name not in dst_group.objects):
                            dst_group.objects.link(obj)
            
            replaced_idnames.difference_update(dst_idnames)
            
            if purge and replaced_idnames:
                cls.set_attr("use_fake_user", False, None, replaced_idnames)
                for group in tuple(bpy.data.groups):
                    if group.name in replaced_idnames:
                        bpy.data.groups.remove(group)

#============================================================================#

make_category(globals(), is_ID=True)
