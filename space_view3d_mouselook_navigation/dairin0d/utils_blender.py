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

# <pep8 compliant>

import bpy

import bmesh

from .bpy_inspect import BlEnums

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

class Selection:
    def __init__(self, context=None, mode=None, elem_types=None, container=set):
        self.context = context
        self.mode = mode
        self.elem_types = elem_types
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
            if item[1]:
                yield item
    
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
            total = 0
            for spline in active_obj.data.splines:
                total += len(spline.bezier_points) + len(spline.points)
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
        if not is_actual_mode:
            return select_all_action, data
        
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
            type_names = build_info["names"]
            
            if use_kv:
                lines.append(tab + "for item, value in args[{}].items():".format(i))
                lines.append((tab*2) + "if not item: continue")
            else:
                lines.append(tab + "for item in args[{}]:".format(i))
            expr_tab = tab*2
            
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
        
        code = "def apply(*args, data=None):\n{}".format("\n".join(lines))
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
                selector = make_selector({"names":[(None, ["select"])]})
                selector(active_obj.data.bones, data=data)
            else:
                selector = make_selector({"names":[(None, ["select"])], "use_kv":True})
                selector(data)
        elif mode == 'PARTICLE':
            if select_all_action:
                bpy.ops.particle.select_all(action=select_all_action)
            # Theoretically, particle keys can be selected,
            # but there seems to be no API for working with this
        else:
            pass # no selectable elements in other modes

class SelectionSnapshot:
    def __init__(self, context=None):
        sel = Selection(context)
        self.snapshot_curr = (sel, sel.active, sel.history, sel.selected)
        
        self.mode = sel.normalized_mode
        if self.mode == 'OBJECT':
            self.snapshot_obj = self.snapshot_curr
        else:
            sel = Selection(context, 'OBJECT')
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
