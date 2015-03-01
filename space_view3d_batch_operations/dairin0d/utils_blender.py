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

import bpy

import bmesh

import time

from .bpy_inspect import BlEnums

# ========================== TOGGLE OBJECT MODE ============================ #
#============================================================================#
class ToggleObjectMode:
    def __init__(self, mode='OBJECT'):
        if not isinstance(mode, str):
            mode = ('OBJECT' if mode else None)
        
        self.mode = mode
    
    def __enter__(self):
        if self.mode:
            edit_preferences = bpy.context.user_preferences.edit
            
            self.global_undo = edit_preferences.use_global_undo
            self.prev_mode = bpy.context.object.mode
            
            if self.prev_mode != self.mode:
                edit_preferences.use_global_undo = False
                bpy.ops.object.mode_set(mode=self.mode)
        
        return self
    
    def __exit__(self, type, value, traceback):
        if self.mode:
            edit_preferences = bpy.context.user_preferences.edit
            
            if self.prev_mode != self.mode:
                bpy.ops.object.mode_set(mode=self.prev_mode)
                edit_preferences.use_global_undo = self.global_undo

# =============================== MESH CACHE =============================== #
#============================================================================#
class MeshCacheItem:
    def __init__(self):
        self.variants = {}
    
    def __getitem__(self, variant):
        return self.variants[variant][0]
    
    def __setitem__(self, variant, conversion):
        mesh = conversion[0].data
        #mesh.update(calc_tessface=True)
        #mesh.calc_tessface()
        mesh.calc_normals()
        
        self.variants[variant] = conversion
    
    def __contains__(self, variant):
        return variant in self.variants
    
    def dispose(self):
        for obj, converted in self.variants.values():
            if converted:
                mesh = obj.data
                bpy.data.objects.remove(obj)
                bpy.data.meshes.remove(mesh)
        self.variants = None

class MeshCache:
    """
    Keeps a cache of mesh equivalents of requested objects.
    It is assumed that object's data does not change while
    the cache is in use.
    """
    
    variants_enum = {'RAW', 'PREVIEW', 'RENDER'}
    variants_normalization = {
        'MESH':{},
        'CURVE':{},
        'SURFACE':{},
        'FONT':{},
        'META':{'RAW':'PREVIEW'},
        'ARMATURE':{'RAW':'PREVIEW', 'RENDER':'PREVIEW'},
        'LATTICE':{'RAW':'PREVIEW', 'RENDER':'PREVIEW'},
        'EMPTY':{'RAW':'PREVIEW', 'RENDER':'PREVIEW'},
        'CAMERA':{'RAW':'PREVIEW', 'RENDER':'PREVIEW'},
        'LAMP':{'RAW':'PREVIEW', 'RENDER':'PREVIEW'},
        'SPEAKER':{'RAW':'PREVIEW', 'RENDER':'PREVIEW'},
    }
    conversible_types = {'MESH', 'CURVE', 'SURFACE', 'FONT',
                         'META', 'ARMATURE', 'LATTICE'}
    convert_types = conversible_types
    
    def __init__(self, scene, convert_types=None):
        self.scene = scene
        if convert_types:
            self.convert_types = convert_types
        self.cached = {}
    
    def __del__(self):
        self.clear()
    
    def clear(self, expect_zero_users=False):
        for cache_item in self.cached.values():
            if cache_item:
                try:
                    cache_item.dispose()
                except RuntimeError:
                    if expect_zero_users:
                        raise
        self.cached.clear()
    
    def __delitem__(self, obj):
        cache_item = self.cached.pop(obj, None)
        if cache_item:
            cache_item.dispose()
    
    def __contains__(self, obj):
        return obj in self.cached
    
    def __getitem__(self, obj):
        if isinstance(obj, tuple):
            return self.get(*obj)
        return self.get(obj)
    
    def get(self, obj, variant='PREVIEW', reuse=True):
        if variant not in self.variants_enum:
            raise ValueError("Mesh variant must be one of %s" %
                             self.variants_enum)
        
        # Make sure the variant is proper for this type of object
        variant = (self.variants_normalization[obj.type].
                   get(variant, variant))
        
        if obj in self.cached:
            cache_item = self.cached[obj]
            try:
                # cache_item is None if object isn't conversible to mesh
                return (None if (cache_item is None)
                        else cache_item[variant])
            except KeyError:
                pass
        else:
            cache_item = None
        
        if obj.type not in self.conversible_types:
            self.cached[obj] = None
            return None
        
        if not cache_item:
            cache_item = MeshCacheItem()
            self.cached[obj] = cache_item
        
        conversion = self._convert(obj, variant, reuse)
        cache_item[variant] = conversion
        
        return conversion[0]
    
    def _convert(self, obj, variant, reuse=True):
        obj_type = obj.type
        obj_mode = obj.mode
        data = obj.data
        
        if obj_type == 'MESH':
            if reuse and ((variant == 'RAW') or (len(obj.modifiers) == 0)):
                return (obj, False)
            else:
                force_objectmode = (obj_mode in ('EDIT', 'SCULPT'))
                return (self._to_mesh(obj, variant, force_objectmode), True)
        elif obj_type in ('CURVE', 'SURFACE', 'FONT'):
            if variant == 'RAW':
                bm = bmesh.new()
                for spline in data.splines:
                    for point in spline.bezier_points:
                        bm.verts.new(point.co)
                        bm.verts.new(point.handle_left)
                        bm.verts.new(point.handle_right)
                    for point in spline.points:
                        bm.verts.new(point.co[:3])
                return (self._make_obj(bm, obj), True)
            else:
                if variant == 'RENDER':
                    resolution_u = data.resolution_u
                    resolution_v = data.resolution_v
                    if data.render_resolution_u != 0:
                        data.resolution_u = data.render_resolution_u
                    if data.render_resolution_v != 0:
                        data.resolution_v = data.render_resolution_v
                
                result = (self._to_mesh(obj, variant), True)
                
                if variant == 'RENDER':
                    data.resolution_u = resolution_u
                    data.resolution_v = resolution_v
                
                return result
        elif obj_type == 'META':
            if variant == 'RAW':
                # To avoid the hassle of snapping metaelements
                # to themselves, we just create an empty mesh
                bm = bmesh.new()
                return (self._make_obj(bm, obj), True)
            else:
                if variant == 'RENDER':
                    resolution = data.resolution
                    data.resolution = data.render_resolution
                
                result = (self._to_mesh(obj, variant), True)
                
                if variant == 'RENDER':
                    data.resolution = resolution
                
                return result
        elif obj_type == 'ARMATURE':
            bm = bmesh.new()
            if obj_mode == 'EDIT':
                for bone in data.edit_bones:
                    head = bm.verts.new(bone.head)
                    tail = bm.verts.new(bone.tail)
                    bm.edges.new((head, tail))
            elif obj_mode == 'POSE':
                for bone in obj.pose.bones:
                    head = bm.verts.new(bone.head)
                    tail = bm.verts.new(bone.tail)
                    bm.edges.new((head, tail))
            else:
                for bone in data.bones:
                    head = bm.verts.new(bone.head_local)
                    tail = bm.verts.new(bone.tail_local)
                    bm.edges.new((head, tail))
            return (self._make_obj(bm, obj), True)
        elif obj_type == 'LATTICE':
            bm = bmesh.new()
            for point in data.points:
                bm.verts.new(point.co_deform)
            return (self._make_obj(bm, obj), True)
    
    def _to_mesh(self, obj, variant, force_objectmode=False):
        tmp_name = chr(0x10ffff) # maximal Unicode value
        
        with ToggleObjectMode(force_objectmode):
            if variant == 'RAW':
                mesh = obj.to_mesh(self.scene, False, 'PREVIEW')
            else:
                mesh = obj.to_mesh(self.scene, True, variant)
            mesh.name = tmp_name
        
        return self._make_obj(mesh, obj)
    
    def _make_obj(self, mesh, src_obj):
        tmp_name = chr(0x10ffff) # maximal Unicode value
        
        if isinstance(mesh, bmesh.types.BMesh):
            bm = mesh
            mesh = bpy.data.meshes.new(tmp_name)
            bm.to_mesh(mesh)
        
        tmp_obj = bpy.data.objects.new(tmp_name, mesh)
        
        if src_obj:
            tmp_obj.matrix_world = src_obj.matrix_world
            
            # This is necessary for correct bbox display # TODO
            # (though it'd be better to change the logic in the raycasting)
            tmp_obj.show_x_ray = src_obj.show_x_ray
            
            tmp_obj.dupli_faces_scale = src_obj.dupli_faces_scale
            tmp_obj.dupli_frames_end = src_obj.dupli_frames_end
            tmp_obj.dupli_frames_off = src_obj.dupli_frames_off
            tmp_obj.dupli_frames_on = src_obj.dupli_frames_on
            tmp_obj.dupli_frames_start = src_obj.dupli_frames_start
            tmp_obj.dupli_group = src_obj.dupli_group
            #tmp_obj.dupli_list = src_obj.dupli_list
            tmp_obj.dupli_type = src_obj.dupli_type
        
        # Make Blender recognize object as having geometry
        # (is there a simpler way to do this?)
        self.scene.objects.link(tmp_obj)
        self.scene.update()
        # We don't need this object in scene
        self.scene.objects.unlink(tmp_obj)
        
        return tmp_obj

# =============================== SELECTION ================================ #
#============================================================================#
class Selection:
    def __init__(self, context=None, mode=None, elem_types=None, container=set, brute_force_update=False, pose_bones=True):
        self.context = context
        self.mode = mode
        self.elem_types = elem_types
        self.brute_force_update = brute_force_update
        self.pose_bones = pose_bones
        # In some cases, user might want a hashable type (e.g. frozenset or tuple)
        self.container = container
        # We MUST keep reference to bmesh, or it will be garbage-collected
        self.bmesh = None
    
    def get_context(self):
        context = self.context or bpy.context
        mode = self.mode or context.mode
        active_obj = context.active_object
        actual_mode = BlEnums.mode_from_object(active_obj)
        mode = BlEnums.normalize_mode(mode, active_obj)
        if not BlEnums.is_mode_valid(mode, active_obj):
            mode = None # invalid request
        return context, active_obj, actual_mode, mode
    
    @property
    def normalized_mode(self):
        return self.get_context()[-1]
    
    @property
    def stateless_info(self):
        history, active, total = next(self.walk(), (None,None,0))
        active_id = active.name if hasattr(active, "name") else hash(active)
        return (total, active_id)
    
    @property
    def active(self):
        return next(self.walk(), (None,None))[1]
    @active.setter
    def active(self, value):
        self.update_active(value)
    
    @property
    def history(self):
        return next(self.walk(), (None,))[0]
    @history.setter
    def history(self, value):
        self.update_history(value)
    
    @property
    def selected(self):
        walker = self.walk()
        next(walker, None) # skip active item
        return dict(item for item in walker if item[1])
    @selected.setter
    def selected(self, value):
        self.update(value)
    
    def __iter__(self):
        walker = self.walk()
        next(walker, None) # skip active item
        for item in walker:
            if item[1]: yield item
    
    def __bool__(self):
        """Returns True if there is at least 1 element selected"""
        context, active_obj, actual_mode, mode = self.get_context()
        if not mode: return False
        
        if mode == 'OBJECT':
            return bool(context.selected_objects)
        elif mode == 'EDIT_MESH':
            mesh = active_obj.data
            if actual_mode == 'EDIT_MESH':
                return bool(mesh.total_vert_sel)
            else:
                return any(item.select for item in mesh.vertices)
        elif mode in {'EDIT_CURVE', 'EDIT_SURFACE'}:
            for spline in active_obj.data.splines:
                for item in spline.bezier_points:
                    if (item.select_control_point or
                        item.select_left_handle or
                        item.select_right_handle):
                        return True
                for item in spline.points:
                    if item.select:
                        return True
        elif mode == 'EDIT_METABALL':
            return bool(active_obj.data.elements.active)
        elif mode == 'EDIT_LATTICE':
            return any(item.select for item in active_obj.data.points)
        elif mode == 'EDIT_ARMATURE':
            return any(item.select_head or item.select_tail
                       for item in active_obj.data.edit_bones)
        elif mode == 'POSE':
            return any(item.select for item in active_obj.data.bones)
        elif mode == 'PARTICLE':
            # Theoretically, particle keys can be selected,
            # but there seems to be no API for working with this
            pass
        else:
            pass # no selectable elements in other modes
        
        return False
    
    def walk(self):
        """Iterates over selection, returning (history, active, count) first, then (element, selected_attributes) until exhausted"""
        context, active_obj, actual_mode, mode = self.get_context()
        if not mode: return
        
        container = self.container
        sel_map = {False: container(), True: container(("select",))}
        
        if mode == 'OBJECT':
            total = len(context.selected_objects)
            item = active_obj
            yield ([], item, total)
            
            select = sel_map[True] # selected by definition
            for item in context.selected_objects:
                yield (item, select)
        elif mode == 'EDIT_MESH':
            mesh = active_obj.data
            elem_types = self.elem_types
            if actual_mode == 'EDIT_MESH':
                bm = self.bmesh or bmesh.from_edit_mesh(mesh)
                self.bmesh = bm
                
                item = bm.faces.active
                
                if mesh.total_vert_sel == 0: # non-0 only in Edit mode
                    yield ([], item, 0)
                    return
                
                # No, by default all selected elements should be returned!
                #if not elem_types:
                #    elem_types = bm.select_mode
                
                colls = []
                if (not elem_types) or ('FACE' in elem_types):
                    colls.append(bm.faces)
                if (not elem_types) or ('EDGE' in elem_types):
                    colls.append(bm.edges)
                if (not elem_types) or ('VERT' in elem_types):
                    colls.append(bm.verts)
                
                total = sum(len(items) for items in colls)
                if bm.select_history:
                    yield (list(bm.select_history), item, total)
                else:
                    yield ([], item, total)
                
                for items in colls:
                    for item in items:
                        yield (item, sel_map[item.select])
            else:
                colls = []
                if (not elem_types) or ('FACE' in elem_types):
                    colls.append(mesh.polygons)
                if (not elem_types) or ('EDGE' in elem_types):
                    colls.append(mesh.edges)
                if (not elem_types) or ('VERT' in elem_types):
                    colls.append(mesh.vertices)
                
                total = sum(len(items) for items in colls)
                item = None
                if mesh.polygons.active >= 0:
                    item = mesh.polygons[mesh.polygons.active]
                yield ([], item, total)
                
                for items in colls:
                    for item in items:
                        yield (item, sel_map[item.select])
        elif mode in {'EDIT_CURVE', 'EDIT_SURFACE'}:
            total = sum(len(spline.bezier_points) + len(spline.points)
                for spline in active_obj.data.splines)
            yield ([], None, total)
            
            bezier_sel_map = {
                (False, False, False): container(),
                (True, False, False): container(("select_left_handle",)),
                (False, True, False): container(("select_control_point",)),
                (False, False, True): container(("select_right_handle",)),
                (True, True, False): container(("select_left_handle", "select_control_point")),
                (False, True, True): container(("select_control_point", "select_right_handle")),
                (True, False, True): container(("select_left_handle", "select_right_handle")),
                (True, True, True): container(("select_left_handle", "select_control_point", "select_right_handle")),
            }
            
            for spline in active_obj.data.splines:
                for item in spline.bezier_points:
                    yield (item, bezier_sel_map[(item.select_left_handle, item.select_control_point, item.select_right_handle)])
                
                for item in spline.points:
                    yield (item, sel_map[item.select])
        elif mode == 'EDIT_METABALL':
            total = 1 # only active is known in current API
            item = active_obj.data.elements.active
            yield ([], item, total)
            
            # We don't even know if active element is actually selected
            # Just assume it is, to have at least some information
            yield (item, container())
        elif mode == 'EDIT_LATTICE':
            total = len(active_obj.data.points)
            yield ([], None, total)
            
            for item in active_obj.data.points:
                yield (item, sel_map[item.select])
        elif mode == 'EDIT_ARMATURE':
            total = len(active_obj.data.edit_bones)
            item = active_obj.data.edit_bones.active
            yield ([], item, total)
            
            editbone_sel_map = {
                (False, False, False): container(),
                (True, False, False): container(("select_head",)),
                (False, True, False): container(("select",)),
                (False, False, True): container(("select_tail",)),
                (True, True, False): container(("select_head", "select")),
                (False, True, True): container(("select", "select_tail")),
                (True, False, True): container(("select_head", "select_tail")),
                (True, True, True): container(("select_head", "select", "select_tail")),
            }
            
            for item in active_obj.data.edit_bones:
                yield (item, editbone_sel_map[(item.select_head, item.select, item.select_tail)])
        elif mode == 'POSE':
            total = len(active_obj.data.bones)
            item = active_obj.data.bones.active
            
            if self.pose_bones:
                pose_bones = active_obj.pose.bones
                
                pb = (pose_bones.get(item.name) if item else None)
                yield ([], pb, total)
                
                for item in active_obj.data.bones:
                    pb = (pose_bones.get(item.name) if item else None)
                    yield (pb, sel_map[item.select])
            else:
                yield ([], item, total)
                
                for item in active_obj.data.bones:
                    yield (item, sel_map[item.select])
        elif mode == 'PARTICLE':
            # Theoretically, particle keys can be selected,
            # but there seems to be no API for working with this
            pass
        else:
            pass # no selectable elements in other modes
    
    def update_active(self, item):
        context, active_obj, actual_mode, mode = self.get_context()
        if not mode: return
        
        if mode == 'OBJECT':
            context.scene.objects.active = item
        elif mode == 'EDIT_MESH':
            mesh = active_obj.data
            if actual_mode == 'EDIT_MESH':
                bm = self.bmesh or bmesh.from_edit_mesh(mesh)
                self.bmesh = bm
                bm.faces.active = item
            else:
                mesh.polygons.active = (item.index if item else -1)
        elif mode in {'EDIT_CURVE', 'EDIT_SURFACE'}:
            pass # no API for active element
        elif mode == 'EDIT_METABALL':
            active_obj.data.elements.active = item
        elif mode == 'EDIT_LATTICE':
            pass # no API for active element
        elif mode == 'EDIT_ARMATURE':
            active_obj.data.edit_bones.active = item
        elif mode == 'POSE':
            if item: item = active_obj.data.bones.get(item.name)
            active_obj.data.bones.active = item
        elif mode == 'PARTICLE':
            # Theoretically, particle keys can be selected,
            # but there seems to be no API for working with this
            pass
        else:
            pass # no selectable elements in other modes
    
    def update_history(self, history):
        context, active_obj, actual_mode, mode = self.get_context()
        if not mode: return
        
        if mode == 'EDIT_MESH':
            mesh = active_obj.data
            if actual_mode == 'EDIT_MESH':
                bm = self.bmesh or bmesh.from_edit_mesh(mesh)
                self.bmesh = bm
                
                bm.select_history.clear()
                for item in history:
                    bm.select_history.add(item)
                #bm.select_history.validate()
            else:
                pass # history not supported
        else:
            pass # history not supported
    
    def __update_strategy(self, is_actual_mode, data, expr_info):
        # We use select_all(action) only when the context is right
        # and iterating over all objects can be avoided.
        select_all_action = None
        if not is_actual_mode: return select_all_action, data
        
        operation, new_toggled, invert_new, old_toggled, invert_old = expr_info
        
        # data = {} translates to "no exceptions"
        if operation == 'SET':
            if new_toggled is False:
                select_all_action = 'DESELECT'
                data = {} # False --> False
            elif new_toggled is True:
                select_all_action = 'SELECT'
                data = {} # True --> True
            elif invert_new:
                select_all_action = 'SELECT'
            else:
                select_all_action = 'DESELECT'
        elif operation == 'OR':
            if new_toggled is False:
                if old_toggled is False:
                    select_all_action = 'DESELECT'
                    data = {} # False OR False --> False
                elif old_toggled is True:
                    select_all_action = 'SELECT'
                    data = {} # True OR False --> True
                else:
                    data = {} # x OR False --> x
            elif new_toggled is True:
                select_all_action = 'SELECT'
                data = {} # x OR True --> True
            elif invert_new:
                pass # need to iterate over all objects anyway
            else:
                if invert_old:
                    select_all_action = 'INVERT'
                else:
                    select_all_action = '' # use data, but no select_all
        elif operation == 'AND':
            if new_toggled is False:
                select_all_action = 'DESELECT'
                data = {} # x AND False --> False
            elif new_toggled is True:
                if old_toggled is False:
                    select_all_action = 'DESELECT'
                    data = {} # False AND False --> False
                elif old_toggled is True:
                    select_all_action = 'DESELECT'
                    data = {} # True AND False --> False
                else:
                    data = {} # x AND True --> x
            elif invert_new:
                if invert_old:
                    select_all_action = 'INVERT'
                else:
                    select_all_action = '' # use data, but no select_all
            else:
                pass # need to iterate over all objects anyway
        elif operation == 'XOR':
            if new_toggled is False:
                if old_toggled is False:
                    select_all_action = 'DESELECT'
                    data = {} # False != False --> False
                elif old_toggled is True:
                    select_all_action = 'SELECT'
                    data = {} # True != False --> True
            elif new_toggled is True:
                if old_toggled is False:
                    select_all_action = 'SELECT'
                    data = {} # False != True --> True
                elif old_toggled is True:
                    select_all_action = 'DESELECT'
                    data = {} # True != True --> False
            elif invert_new:
                pass # need to iterate over all objects anyway
            else:
                pass # need to iterate over all objects anyway
        
        return select_all_action, data
    
    def __update_make_selector_expression(self, name, use_kv, expr_info):
        operation, new_toggled, invert_new, old_toggled, invert_old = expr_info
        
        data_code = ("value" if use_kv else "data.get(item, '')")
        
        if new_toggled is not None:
            code_new = repr(new_toggled)
        elif invert_new:
            code_new = "({} not in {})".format(repr(name), data_code)
        else:
            code_new = "({} in {})".format(repr(name), data_code)
        
        if old_toggled is not None:
            code_old = repr(old_toggled)
        elif invert_old:
            code_old = "(not item.{})".format(name)
        else:
            code_old = "item.{}".format(name)
        
        if operation == 'OR':
            code = "{} or {}".format(code_old, code_new)
        elif operation == 'AND':
            code = "{} and {}".format(code_old, code_new)
        elif operation == 'XOR':
            code = "{} != {}".format(code_old, code_new)
        else:
            code = code_new # SET
        
        return "item.{0} = ({1})".format(name, code)
    
    def __update_make_selector(self, build_infos, expr_info):
        tab = "    "
        expr_maker = self.__update_make_selector_expression
        localvars = {"isinstance":isinstance}
        type_cnt = 0
        lines = []
        for i, build_info in enumerate(build_infos):
            use_kv = build_info.get("use_kv", False)
            item_map = build_info.get("item_map", None)
            type_names = build_info["names"]
            
            expr_tab = tab*2
            
            if item_map: lines.append(tab + "item_map = {}".format(item_map))
            
            if use_kv:
                lines.append(tab + "for item, value in args[{}].items():".format(i))
                lines.append(expr_tab + "if not item: continue")
            else:
                lines.append(tab + "for item in args[{}]:".format(i))
            
            if item_map:
                lines.append(expr_tab + "item = item_map.get(item.name)")
                lines.append(expr_tab + "if not item: continue")
            
            if len(type_names) < 2:
                item_type, names = type_names[0]
                if (not use_kv) and (len(names) > 1):
                    lines.append(expr_tab + "value = data.get(item, '')")
                    use_kv = True
                for name in names:
                    lines.append(expr_tab + expr_maker(name, use_kv, expr_info))
            else:
                tab_if = expr_tab
                expr_tab += tab
                j = 0
                for item_type, names in type_names:
                    j += 1
                    type_name = "type{}".format(type_cnt)
                    type_cnt += 1
                    localvars[type_name] = item_type
                    if j == 1:
                        lines.append(tab_if + "if isinstance(item, {}):".format(type_name))
                    elif j < len(type_names):
                        lines.append(tab_if + "elif isinstance(item, {}):".format(type_name))
                    else:
                        lines.append(tab_if + "else:")
                    
                    for name in names:
                        lines.append(expr_tab + expr_maker(name, use_kv, expr_info))
        
        code = "def apply(*args, data=None, context=None):\n{}".format("\n".join(lines))
        #print(code.strip())
        
        exec(code, localvars, localvars)
        return localvars["apply"]
    
    __cached_selectors = {}
    
    def update(self, data, operation='SET'):
        if not isinstance(data, dict):
            raise ValueError("data must be a dict")
        
        toggle_old = operation.startswith("^")
        invert_old = operation.startswith("!")
        toggle_new = operation.endswith("^")
        invert_new = operation.endswith("!")
        operation = operation.replace("!", "").replace("^", "")
        
        if operation not in {'SET', 'OR', 'AND', 'XOR'}:
            raise ValueError("operation must be one of {'SET', 'OR', 'AND', 'XOR'}")
        
        context, active_obj, actual_mode, mode = self.get_context()
        if not mode: return
        
        new_toggled = (not any(data.values()) if toggle_new else None)
        old_toggled = (not bool(self) if toggle_old else None)
        
        expr_info = (operation, new_toggled, invert_new, old_toggled, invert_old)
        
        is_actual_mode = (mode == actual_mode)
        if self.brute_force_update:
            select_all_action = None
        else:
            select_all_action, data = self.__update_strategy(is_actual_mode, data, expr_info)
        #print("Strategy: action={}, data={}".format(repr(select_all_action), bool(data)))
        use_brute_force = select_all_action is None
        
        def make_selector(*build_infos):
            selector_key = (mode, is_actual_mode, use_brute_force, expr_info)
            selector = Selection.__cached_selectors.get(selector_key)
            #print(selector_key)
            if selector is None:
                selector = self.__update_make_selector(build_infos, expr_info)
                Selection.__cached_selectors[selector_key] = selector
            #print(selector)
            return selector
        
        if mode == 'OBJECT':
            if select_all_action:
                bpy.ops.object.select_all(action=select_all_action)
            
            if use_brute_force:
                selector = make_selector({"names":[(None, ["select"])]})
                selector(context.scene.objects, data=data)
            else:
                selector = make_selector({"names":[(None, ["select"])], "use_kv":True})
                selector(data)
        elif mode == 'EDIT_MESH':
            if select_all_action:
                bpy.ops.mesh.select_all(action=select_all_action)
            
            mesh = active_obj.data
            if is_actual_mode:
                bm = self.bmesh or bmesh.from_edit_mesh(mesh)
                self.bmesh = bm
                faces, edges, verts = bm.faces, bm.edges, bm.verts
            else:
                faces, edges, verts = mesh.polygons, mesh.edges, mesh.vertices
            
            if use_brute_force:
                selector = make_selector({"names":[(None, ["select"])]})
                selector(faces, data=data)
                selector(edges, data=data)
                selector(verts, data=data)
            else:
                selector = make_selector({"names":[(None, ["select"])], "use_kv":True})
                selector(data)
            
            if is_actual_mode:
                #bm.select_flush(True) # ?
                #bm.select_flush(False) # ?
                #bm.select_flush_mode() # ?
                pass
        elif mode in {'EDIT_CURVE', 'EDIT_SURFACE'}:
            if select_all_action:
                bpy.ops.curve.select_all(action=select_all_action)
            
            bezier_names = (bpy.types.BezierSplinePoint, ["select_control_point", "select_left_handle", "select_right_handle"])
            if use_brute_force:
                selector = make_selector({"names":[bezier_names]}, {"names":[(None, ["select"])]})
                for spline in active_obj.data.splines:
                    selector(spline.bezier_points, spline.points, data=data)
            else:
                selector = make_selector({"names":[bezier_names, (None, ["select"])], "use_kv":True})
                selector(data)
        elif mode == 'EDIT_METABALL':
            if select_all_action:
                bpy.ops.mball.select_all(action=select_all_action)
            # Otherwise, we can't do anything with current API
        elif mode == 'EDIT_LATTICE':
            if select_all_action:
                bpy.ops.lattice.select_all(action=select_all_action)
            
            if use_brute_force:
                selector = make_selector({"names":[(None, ["select"])]})
                selector(active_obj.data.points, data=data)
            else:
                selector = make_selector({"names":[(None, ["select"])], "use_kv":True})
                selector(data)
        elif mode == 'EDIT_ARMATURE':
            if select_all_action:
                bpy.ops.armature.select_all(action=select_all_action)
            
            if use_brute_force:
                selector = make_selector({"names":[(None, ["select_head", "select", "select_tail"])]})
                selector(active_obj.data.edit_bones, data=data)
            else:
                selector = make_selector({"names":[(None, ["select_head", "select", "select_tail"])], "use_kv":True})
                selector(data)
        elif mode == 'POSE':
            if select_all_action:
                bpy.ops.pose.select_all(action=select_all_action)
            
            if use_brute_force:
                selector = make_selector({"names":[(None, ["select"])], "item_map":"context.data.bones"})
                selector(active_obj.data.bones, data=data, context=active_obj)
            else:
                selector = make_selector({"names":[(None, ["select"])], "item_map":"context.data.bones", "use_kv":True})
                selector(data, context=active_obj)
        elif mode == 'PARTICLE':
            if select_all_action:
                bpy.ops.particle.select_all(action=select_all_action)
            # Theoretically, particle keys can be selected,
            # but there seems to be no API for working with this
        else:
            pass # no selectable elements in other modes

class SelectionSnapshot:
    # The goal of SelectionSnapshot is to leave as little side-effects as possible,
    # so brute_force_update=True (since select_all operators are recorded in the info log)
    def __init__(self, context=None, brute_force_update=True):
        sel = Selection(context, brute_force_update=brute_force_update)
        self.snapshot_curr = (sel, sel.active, sel.history, sel.selected)
        
        self.mode = sel.normalized_mode
        if self.mode == 'OBJECT':
            self.snapshot_obj = self.snapshot_curr
        else:
            sel = Selection(context, 'OBJECT', brute_force_update=brute_force_update)
            self.snapshot_obj = (sel, sel.active, sel.history, sel.selected)
    
    # Attention: it is assumed that there was no Undo,
    # objects' modes didn't change, and all elements are still valid
    def restore(self):
        if self.mode != 'OBJECT':
            sel, active, history, selected = self.snapshot_obj
            sel.selected = selected
            sel.history = history
            sel.active = active
        
        sel, active, history, selected = self.snapshot_curr
        sel.selected = selected
        sel.history = history
        sel.active = active
    
    def __str__(self):
        if self.mode != 'OBJECT':
            return str({'OBJECT':self.snapshot_obj[1:], self.mode:self.snapshot_curr[1:]})
        else:
            return str({'OBJECT':self.snapshot_obj[1:]})
    
    def __enter__(self):
        pass
    
    def __exit__(self, type, value, traceback):
        self.restore()

def IndividuallyActiveSelected(objects, context=None):
    if context is None: context = bpy.context
    
    prev_selection = SelectionSnapshot(context)
    sel, active, history, selected = prev_selection.snapshot_obj
    
    sel.selected = {}
    
    scene = context.scene
    scene_objects = scene.objects
    
    for obj in objects:
        try:
            scene_objects.active = obj
            obj.select = True
        except Exception as exc:
            continue # for some reason object doesn't exist anymore
        
        yield obj
        
        obj.select = False
    
    prev_selection.restore()

class ResumableSelection:
    def __init__(self, *args, **kwargs):
        self.selection = Selection(*args, **kwargs)
        self.selection_walker = None
        self.selection_initialized = False
        
        # Screen change doesn't actually invalidate the selection,
        # but it's a big enough change to justify the extra wait.
        # I added it to make batch-transform a bit more efficient.
        self.mode = ""
        self.obj_hash = 0
        self.screen_hash = 0
        self.scene_hash = 0
        self.undo_hash = 0
        self.operators_len = 0
    
    def __call__(self, duration=0):
        if duration is None: duration = float("inf")
        context = bpy.context
        wm = context.window_manager
        active_obj = context.object
        mode = context.mode
        obj_hash = (active_obj.as_pointer() if active_obj else 0)
        screen_hash = context.screen.as_pointer()
        scene_hash = context.scene.as_pointer()
        undo_hash = bpy.data.as_pointer()
        operators_len = len(wm.operators)
        
        object_updated = False
        if active_obj and ('EDIT' in active_obj.mode):
            object_updated |= (active_obj.is_updated or active_obj.is_updated_data)
            data = active_obj.data
            if data: object_updated |= (data.is_updated or data.is_updated_data)
        
        reset = (self.mode != mode)
        reset |= (self.obj_hash != obj_hash)
        reset |= (self.screen_hash != screen_hash)
        reset |= (self.scene_hash != scene_hash)
        reset |= (self.undo_hash != undo_hash)
        reset |= (self.operators_len != operators_len)
        if reset:
            self.mode = mode
            self.obj_hash = obj_hash
            self.screen_hash = screen_hash
            self.scene_hash = scene_hash
            self.undo_hash = undo_hash
            self.operators_len = operators_len
            
            self.selection.bmesh = None
            self.selection_walker = None
        
        clock = time.clock
        time_stop = clock() + duration
        
        if self.selection_walker is None:
            self.selection.bmesh = None
            self.selection_walker = self.selection.walk()
            self.selection_initialized = False
            yield (-2, None) # RESET
            if clock() > time_stop: return
        
        if not self.selection_initialized:
            item = next(self.selection_walker, None)
            if item: # can be None if active mode does not support selections
                history, active, total = item
                if mode == 'EDIT_MESH': active = (history[-1] if history else None)
                self.selection_initialized = True
                yield (0, active) # ACTIVE
                if clock() > time_stop: return
        
        for item in self.selection_walker:
            if item[1]: yield (1, item[0]) # SELECTED
            if clock() > time_stop: break
        else: # the iterator is exhausted
            self.selection.bmesh = None
            self.selection_walker = None
            yield (-1, None) # FINISHED
    
    RESET = -2
    FINISHED = -1
    ACTIVE = 0
    SELECTED = 1

# ============================ CHANGE MONITOR ============================== #
#============================================================================#
class ChangeMonitor:
    reports_cleanup_trigger = 512
    reports_cleanup_count = 128
    max_evaluation_time = 0.002
    
    def __init__(self, context=None, update=True, **kwargs):
        if not context: context = bpy.context
        wm = context.window_manager
        
        self.selection = Selection(container=frozenset)
        
        self.mode = None
        self.active_obj = None
        self.selection_walker = None
        self.selection_recorded = False
        self.selection_recorder = []
        self.selection_record_id = 0
        self.scene_hash = 0
        self.undo_hash = 0
        self.operators_len = 0
        self.reports = []
        self.reports_len = 0
        
        if update: self.update(context, **kwargs)
        
        self.mode_changed = False
        self.active_obj_changed = False
        self.selection_changed = False
        self.scene_changed = False
        self.undo_performed = False
        self.object_updated = False
        self.operators_changed = 0
        self.reports_changed = 0
    
    def get_reports(self, context=None, **kwargs):
        if not context: context = bpy.context
        wm = context.window_manager
        
        area = kwargs.get("area") or context.area
        
        try:
            prev_clipboard = wm.clipboard
        except UnicodeDecodeError as exc:
            #print(exc)
            prev_clipboard = ""
        
        prev_type = area.type
        if prev_type != 'INFO':
            area.type = 'INFO'
        
        try:
            bpy.ops.info.report_copy(kwargs)
            if wm.clipboard: # something was selected
                bpy.ops.info.select_all_toggle(kwargs) # something is selected: deselect all
                #bpy.ops.info.reports_display_update(kwargs)
            bpy.ops.info.select_all_toggle(kwargs) # nothing is selected: select all
            #bpy.ops.info.reports_display_update(kwargs)
            
            bpy.ops.info.report_copy(kwargs)
            reports = wm.clipboard.splitlines()
            
            bpy.ops.info.select_all_toggle(kwargs) # deselect everything
            #bpy.ops.info.reports_display_update(kwargs)
            
            if len(reports) >= self.reports_cleanup_trigger:
                for i in range(self.reports_cleanup_count):
                    bpy.ops.info.select_pick(kwargs, report_index=i)
                    #bpy.ops.info.reports_display_update(kwargs)
                bpy.ops.info.report_delete(kwargs)
                #bpy.ops.info.reports_display_update(kwargs)
        except Exception as exc:
            #print(exc)
            reports = []
        
        if prev_type != 'INFO':
            area.type = prev_type
        
        wm.clipboard = prev_clipboard
        
        return reports
    
    something_changed = property(lambda self:
        self.mode_changed or
        self.active_obj_changed or
        self.selection_changed or
        self.scene_changed or
        self.undo_performed or
        self.object_updated or
        bool(self.operators_changed) or
        bool(self.reports_changed)
    )
    
    def hash(self, obj):
        if obj is None: return 0
        if hasattr(obj, "as_pointer"): return obj.as_pointer()
        return hash(obj)
    
    def update(self, context=None, **kwargs):
        if not context: context = bpy.context
        wm = context.window_manager
        
        self.mode_changed = False
        self.active_obj_changed = False
        self.selection_changed = False
        self.scene_changed = False
        self.undo_performed = False
        self.object_updated = False
        self.operators_changed = 0
        self.reports_changed = 0
        
        mode = kwargs.get("mode") or context.mode
        active_obj = kwargs.get("object") or context.object
        scene = kwargs.get("scene") or context.scene
        
        if (self.mode != mode):
            self.mode = mode
            self.mode_changed = True
        
        if (self.active_obj != active_obj):
            self.active_obj = active_obj
            self.active_obj_changed = True
        
        scene_hash = self.hash(scene)
        if (self.scene_hash != scene_hash):
            self.scene_hash = scene_hash
            self.scene_changed = True
        
        undo_hash = self.hash(bpy.data)
        if (self.undo_hash != undo_hash):
            self.undo_hash = undo_hash
            self.undo_performed = True
        
        if active_obj and ('EDIT' in active_obj.mode):
            if active_obj.is_updated or active_obj.is_updated_data:
                self.object_updated = True
            data = active_obj.data
            if data and (data.is_updated or data.is_updated_data):
                self.object_updated = True
        
        operators_len = len(wm.operators)
        if (operators_len != self.operators_len):
            self.operators_changed = operators_len - self.operators_len
            self.operators_len = operators_len
        else: # maybe this would be a bit safer?
            reports = self.get_reports(context, **kwargs) # sometimes this causes Blender to crash
            reports_len = len(reports)
            if (reports_len != self.reports_len):
                self.reports_changed = reports_len - self.reports_len
                self.reports = reports
                self.reports_len = reports_len
        
        self.analyze_selection()
    
    def reset_selection(self):
        self.selection.bmesh = None
        self.selection_walker = None
        self.selection_recorded = False
        self.selection_recorder = []
        self.selection_record_id = 0
    
    def analyze_selection(self):
        reset_selection = self.mode_changed
        reset_selection |= self.active_obj_changed
        reset_selection |= self.scene_changed
        reset_selection |= self.undo_performed
        reset_selection |= self.object_updated
        reset_selection |= self.operators_changed
        reset_selection |= self.reports_changed
        if reset_selection:
            #print("Selection reseted for external reasons")
            self.reset_selection()
            # At this point we have no idea if the selection
            # has actually changed. This is more of a warning
            # about a potential change of selection.
            self.selection_changed = True
        
        if self.selection_walker is None:
            self.selection.bmesh = None
            self.selection_walker = self.selection.walk()
        
        clock = time.clock()
        hash = self.hash
        
        if self.selection_recorded:
            time_stop = clock() + self.max_evaluation_time
            
            if self.selection_record_id == 0:
                item = next(self.selection_walker, None)
                history, active, total = item
                item = tuple(hash(h) for h in history), hash(active), total
                self.selection_record_id = 1
                if self.selection_recorder[0] != item:
                    #print("Active/history/total changed")
                    self.selection_changed = True
                    self.reset_selection()
                    return
            
            recorded_count = len(self.selection_recorder)
            for item in self.selection_walker:
                if item[1]:
                    item = hash(item[0]), item[1]
                    i = self.selection_record_id
                    if (i >= recorded_count) or (self.selection_recorder[i] != item):
                        #print("More than necessary or selection changed")
                        self.selection_changed = True
                        self.reset_selection()
                        return
                    self.selection_record_id = i + 1
                if clock() > time_stop: break
            else: # the iterator is exhausted
                if self.selection_record_id < recorded_count:
                    #print("Less than necessary")
                    self.selection_changed = True
                    self.reset_selection()
                    return
                self.selection.bmesh = None
                self.selection_walker = None
                self.selection_record_id = 0
        else:
            time_stop = clock() + self.max_evaluation_time
            
            if self.selection_record_id == 0:
                item = next(self.selection_walker, None)
                history, active, total = item
                item = tuple(hash(h) for h in history), hash(active), total
                self.selection_record_id = 1
                self.selection_recorder.append(item) # first item is special
            
            for item in self.selection_walker:
                if item[1]:
                    item = hash(item[0]), item[1]
                    self.selection_recorder.append(item)
                if clock() > time_stop: break
            else: # the iterator is exhausted
                self.selection.bmesh = None
                self.selection_walker = None
                self.selection_recorded = True
                self.selection_record_id = 0
