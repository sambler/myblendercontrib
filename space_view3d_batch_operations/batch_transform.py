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

import math
import time
import json

from mathutils import Color, Vector, Euler, Quaternion, Matrix

try:
    import dairin0d
    dairin0d_location = ""
except ImportError:
    dairin0d_location = "."

exec("""
from {0}dairin0d.utils_math import matrix_compose, matrix_decompose
from {0}dairin0d.utils_view3d import SmartView3D
from {0}dairin0d.utils_blender import Selection
from {0}dairin0d.utils_userinput import KeyMapUtils
from {0}dairin0d.utils_ui import NestedLayout, tag_redraw
from {0}dairin0d.bpy_inspect import prop, BlRna, BlEnums, bpy_struct
from {0}dairin0d.utils_accumulation import Aggregator, VectorAggregator
from {0}dairin0d.utils_addon import AddonManager
""".format(dairin0d_location))

from .batch_common import (
    copyattrs, attrs_to_dict, dict_to_attrs, PatternRenamer,
    Pick_Base, LeftRightPanel, make_category,
    round_to_bool, is_visible, has_common_layers, idnames_separator,
    after_register_callbacks,
)

addon = AddonManager()

"""
Batch Transform:
* (batch) "geometry" property for all modes that can have selected elements
* (batch) apply rotation/scale/etc.
* (batch) change origin of geometry
* (batch) add/remove drivers/keyframes?
* batch editing modes (how the change is applied to multiple objects):
** set same value
** add (offset)
** multiply (proportional)
* vector editing modes / "uniformity" (when changing one component, how the others change):
** no change (independent)
** set same value (copy)
** add (offset/relative) (in Modo it's called "relative")
** multiply (proportional)
* Min/Max interpretation (how changes to min/max are interpreted)
** While min/max is changing, keep max/min the same
** Offset
** Scale from center
* Extra operations:
** Lock axis? (the corresponding axis won't participate in uniformity)
** Vector swizzle?
** Copy/Paste (option: using units or the raw values)

* "local grid" rendering (around object / cursor / etc.)

From http://wiki.blender.org/index.php/Dev:Doc/Quick_Hacks
- Use of 3d manipulator to move and scale Texture Space?

fusion 360 has a lot of cool features (moth3r says it's the most user-friendly CAD)

* CAD-like guides?
  Guides can be used for snapping during transform, but normal snapping
  is ignored by the Knife tool. However, guides can be used to at least
  visually show where to move the knife

* Spatial queries? ("select all objects wich satisfy the following conditions")
* Copy/Paste transform or its components? (respecting axis locks)
* Pick transform? (respecting axis locks)
* auto-refresh? (or maybe incremental refresh?)

* Stateless/incremental Selection walker?
* In addition to aggregating origins, also provide options for geometry aggregation?
  (e.g. min/max/range in certain coord system)
  maybe it's easier to just convert the objects to mesh(es), apply transforms,
  and then use Blender-calculated bbox?

* ability to set accumulation mode for each property independently?
* coordsystem / aggregation / etc. should be independent for each View3D?
  (convenient for cases when one wants to see same property in different coordsystems,
  or even use different views for different coordsystems)
  Theoretically it's possible to implement (UI elements keep their pointers
  while a file is opened, and their order is preserved even after reload
  BUT: for each different coordsystem, we'll need to use the same amount
  of aggregators and update them simultaneously.


* Option to treat isolated islands as separate objects?

moth3r suggests making it an option for where to "store" the coordinates system

See Modo's Absolute Scaling
https://www.youtube.com/watch?v=79BAHXLX9JQ
http://community.thefoundry.co.uk/discussion/topic.aspx?f=33&t=34229


In general, for each parameter, the user might want to see several aggregate characteristics simultaneously
Use table: each row is a separate attribute, and each column is a certain characteristic


[global options] Coord System panel:

// global options:
// * sync coordsystems between 3D views

// TODO: built-in coordinate systems should be not editable ?

["select coordsys" dropdown][add][remove]
["rename" text field]["display local grid" toggle]
[origin][object name][bone name][pick]
[orientation][object/orientation name][bone name][pick]
[space][object name][bone name][pick]

[guides?]
[bookmarks?]

// 3D cursor panel (merge with Enhanced 3D Cursor?)
[*] 3D cursor [u]
(0.0000)[&]
(0.0000)[&]
(0.0000)[&]

Batch Transform panel (an example):

// [*] is "fold this parameter"
// [+] is "add another statistic"
// [u] is "vector uniformity" (independent, copy, offset, proportional)
// [&] is "lock this axis"

// if modifier(?)+clicked on property name, a popup menu is shown?
// * Copy, Paste, Swizzle, add/remove drivers/keyframes

// if modifier(?)+clicked on aggregation name, a popup menu is shown?
// * Copy, Paste, Swizzle

// Batch Transform options:
// * autorefresh
// * sync settings between 3D views
// * batch editing uniformity (copy, offset, proportional)
// * // min/max mode (offset, lock other, scale) ? -- probably useless, since user can do precise "offset" and "scale" via math expressions
// * apply location/rotation/scale (in Object mode)
// * set geometry origin (can work in edit modes too, for selected elements)

[spatial queries?][pick][copy][paste] [refresh] [options]

[active][ min  ][ max  ][center][range ][ mean ][stddev][median][ mode ][+]

[*] Location                                                            [u]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]

[*] Rotation [rotation_mode] [4L]                                       [u]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]

[*] Scale                                                               [u]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]

[*] Dimensions                                                          [u]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]

[*] Geometry (?)                                                        [u]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]
(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)(0.0000)[&]






def get_transformed(context):
    v3d = context.space_data
    if (not v3d) or (v3d.type != 'VIEW_3D'):
        return
    
    v3d_key = v3d.as_pointer()
    
    transformeds = addon.internal.transformeds
    for transformed in transformeds:
        if transformed.v3d_key == v3d_key:
            return transformed
    
    transformed = transformeds.add()
    transformed.v3d_key = v3d_key
    return transformed

def iter_transformeds(context):
    spaces = set(space.as_pointer()
                 for area in context.screen.areas
                 for space in area.spaces
                 if space.type == 'VIEW_3D')
    
    transformeds = addon.internal.transformeds
    for transformed in transformeds:
        if transformed.v3d_key in spaces:
            yield transformed
"""

#============================================================================#
Category_Name = "Transform"
CATEGORY_NAME = Category_Name.upper()
category_name = Category_Name.lower()
Category_Name_Plural = "Transforms"
CATEGORY_NAME_PLURAL = Category_Name_Plural.upper()
category_name_plural = Category_Name_Plural.lower()
category_icon = 'MANIPUL'

#============================================================================#

class CoordSystemMatrix:
    def __init__(self, coordsys=None):
        self.update(coordsys)
    
    def update(self, coordsys):
        if coordsys:
            aspect = coordsys.aspect_L
            self.L = (aspect.mode, aspect.obj_name, aspect.bone_name)
            aspect = coordsys.aspect_R
            self.R = (aspect.mode, aspect.obj_name, aspect.bone_name)
            aspect = coordsys.aspect_S
            self.S = (aspect.mode, aspect.obj_name, aspect.bone_name)
            self.extra_matrix = coordsys.extra_matrix
        else:
            self.L = ('GLOBAL', "", "")
            self.R = ('GLOBAL', "", "")
            self.S = ('GLOBAL', "", "")
            self.extra_matrix = Matrix()
    
    def transform(self, context, obj):
        # For now -- just basis
        
        L = obj.location.copy()
        
        if obj.rotation_mode == 'QUATERNION':
            R = obj.rotation_quaternion.copy()
        elif obj.rotation_mode == 'AXIS_ANGLE':
            R = tuple(obj.rotation_axis_angle)
            R = Quaternion(R[:3], R[3])
        else:
            R = obj.rotation_euler.to_quaternion()
        
        S = obj.scale.copy()
        
        return (L, R, S)

#@addon.PropertyGroup
@addon.IDBlock(name="Coordsys", icon='MANIPUL', show_empty=False)
class CoordSystemPG:
    items_LRS = [
        ('BASIS', "Basis", "Raw position/rotation/scale", 'BLENDER'),
        ('GLOBAL', "Global", "Global (world) coordinate system", 'WORLD'),
        ('PARENT', "Parent", "Parent's coordinate system (coincides with Global if there is no parent)", 'GROUP_BONE'),
        ('LOCAL', "Local", "Local (individual) coordinate system", 'ROTATECOLLECTION'),
        ('ACTIVE', "Active", "Coordinate system of active object (coincides with Global if there is no active object)", 'ROTACTIVE'),
        ('OBJECT', "Object/bone", "Coordinate system of the specified object/bone", 'OBJECT_DATA'),
        ('VIEW', "View", "Viewport coordinate system", 'CAMERA_DATA'),
    ]
    items_L = items_LRS + [
        ('SURFACE', "Surface", "Raycasted position", 'EDIT'),
        ('CURSOR', "Cursor", "3D cursor position", 'CURSOR'),
        ('BOOKMARK', "Bookmark", "Bookmark position", 'BOOKMARKS'),
        ('AVERAGE', "Average", "Average of selected items' positions", 'ROTATECENTER'),
        ('CENTER', "Center", "Center of selected items' positions", 'ROTATE'),
        ('MIN', "Min", "Minimum of selected items' positions", 'FRAME_PREV'),
        ('MAX', "Max", "Maximum of selected items' positions", 'FRAME_NEXT'),
        ('PIVOT', "Pivot", "Position of the transform manipulator", 'MANIPUL'),
    ]
    items_R = items_LRS + [
        ('SURFACE', "Surface", "Orientation aligned to the raycasted normal/tangents", 'EDIT'),
        ('NORMAL', "Normal", "Orientation aligned to the average of elements' normals or bones' Y-axes", 'SNAP_NORMAL'),
        ('GIMBAL', "Gimbal", "Orientation aligned to the Euler rotation axes", 'NDOF_DOM'),
        ('ORIENTATION', "Orientation", "Specified orientation", 'MANIPUL'),
    ]
    items_S = items_LRS + [
        ('RANGE', "Range", "Use bounding box dimensions as the scale of each axis", 'BBOX'),
        ('STDDEV', "Deviation", "Use standard deviation as the scale of the system", 'STICKY_UVS_DISABLE'),
    ]
    
    icons_L = {item[0]:item[3] for item in items_L}
    icons_R = {item[0]:item[3] for item in items_R}
    icons_S = {item[0]:item[3] for item in items_S}
    
    icon_L = 'MAN_TRANS'
    icon_R = 'MAN_ROT'
    icon_S = 'MAN_SCALE'
    
    customizable_L = {'OBJECT', 'BOOKMARK'}
    customizable_R = {'OBJECT', 'ORIENTATION'}
    customizable_S = {'OBJECT'}
    
    def make_aspect(name, items):
        title = "{} type".format(name)
        @addon.PropertyGroup
        class CoordsystemAspect:
            mode = 'GLOBAL' | prop(title, title, items=items)
            obj_name = "" | prop() # object/orientation/bookmark name
            bone_name = "" | prop()
        CoordsystemAspect.__name__ += name
        return CoordsystemAspect | prop()
    
    aspect_L = make_aspect("Origin", items_L)
    aspect_R = make_aspect("Orientation", items_R)
    aspect_S = make_aspect("Scale", items_S)
    
    del make_aspect
    
    show_grid_xy = False | prop("Show grid XY plane", "Show grid XY")
    show_grid_xz = False | prop("Show grid XZ plane", "Show grid XZ")
    show_grid_yz = False | prop("Show grid YZ plane", "Show grid YZ")
    grid_size = 3.0 | prop("Grid size", "Grid size", min=0)
    
    extra_X = Vector((1, 0, 0)) | prop("X axis", "X axis")
    extra_Y = Vector((0, 1, 0)) | prop("Y axis", "Y axis")
    extra_Z = Vector((0, 0, 1)) | prop("Z axis", "Z axis")
    extra_T = Vector((0, 0, 0)) | prop("Translation", "Translation")
    
    @property
    def extra_matrix(self):
        return matrix_compose(self.extra_X, self.extra_Y, self.extra_Z, self.extra_T)
    
    def make_get_reset(axis_id):
        def get_reset(self):
            return BlRna.is_default(getattr(self, "extra_"+axis_id), self, "extra_"+axis_id)
        return get_reset
    def make_set_reset(axis_id):
        def set_reset(self, value):
            if value: setattr(self, "extra_"+axis_id, BlRna.get_default(self, "extra_"+axis_id))
        return set_reset
    reset_X = False | prop("Reset X", "Reset X", get=make_get_reset("X"), set=make_set_reset("X"))
    reset_Y = False | prop("Reset Y", "Reset Y", get=make_get_reset("Y"), set=make_set_reset("Y"))
    reset_Z = False | prop("Reset Z", "Reset Z", get=make_get_reset("Z"), set=make_set_reset("Z"))
    reset_T = False | prop("Reset T", "Reset T", get=make_get_reset("T"), set=make_set_reset("T"))
    
    def draw(self, layout):
        layout = NestedLayout(layout, addon.module_name+".coordsystem")
        
        with layout.column(True):
            self.draw_aspect(layout, "L")
            self.draw_aspect(layout, "R")
            self.draw_aspect(layout, "S")
        
        with layout.row(True):
            layout.prop(self, "show_grid_xy", text="", icon='AXIS_TOP', toggle=True)
            layout.prop(self, "show_grid_xz", text="", icon='AXIS_FRONT', toggle=True)
            layout.prop(self, "show_grid_yz", text="", icon='AXIS_SIDE', toggle=True)
            layout.prop(self, "grid_size")
        
        with layout.fold("Extra Matrix", folded=True): # folded by default
            with layout.column(True):
                self.draw_axis(layout, "X")
                self.draw_axis(layout, "Y")
                self.draw_axis(layout, "Z")
                self.draw_axis(layout, "T")
    
    def draw_axis(self, layout, axis_id):
        with layout.row(True):
            with layout.row(True)(scale_x=0.1, enabled=(not getattr(self, "reset_"+axis_id))):
                layout.prop(self, "reset_"+axis_id, text=axis_id, toggle=True)
            layout.prop(self, "extra_"+axis_id, text="")
    
    def draw_aspect(self, layout, aspect_id):
        aspect = getattr(self, "aspect_"+aspect_id)
        aspect_icon = getattr(self, "icon_"+aspect_id)
        aspect_icons = getattr(self, "icons_"+aspect_id)
        customizable = getattr(self, "customizable_"+aspect_id)
        
        with layout.row(True):
            is_customizable = (aspect.mode in customizable)
            
            op = layout.operator("view3d.coordsystem_pick_aspect", text="", icon=aspect_icon)
            op.aspect_id = aspect_id
            
            with layout.row(True)(enabled=is_customizable):
                if aspect.mode == 'OBJECT':
                    obj = bpy.data.objects.get(aspect.obj_name)
                    with layout.row(True)(alert=bool(aspect.obj_name and not obj)):
                        layout.prop(aspect, "obj_name", text="")
                    
                    if obj and (obj.type == 'ARMATURE'):
                        bone = (obj.data.edit_bones if (obj.mode == 'EDIT') else obj.data.bones).get(aspect.bone_name)
                        with layout.row(True)(alert=bool(aspect.bone_name and not bone)):
                            layout.prop(aspect, "bone_name", text="")
                else:
                    layout.prop(aspect, "obj_name", text="")
            
            with layout.row(True)(scale_x=0.16):
                layout.prop(aspect, "mode", text="", icon=aspect_icons[aspect.mode])

@addon.Operator(idname="view3d.coordsystem_pick_aspect", options={'INTERNAL', 'REGISTER'}, description=
"Click: Pick this aspect from active object")
def Operator_Coordsystem_Pick_Aspect(self, context, event, aspect_id=""):
    manager = context.screen.coordsystem_manager
    coordsys = manager.current
    if not coordsys: return {'CANCELLED'}
    
    aspect = getattr(coordsys, "aspect_"+aspect_id)
    if aspect.mode != 'OBJECT': return {'CANCELLED'}
    
    obj = context.active_object
    if obj:
        aspect.obj_name = obj.name
        if obj.type == 'ARMATURE':
            bone = (obj.data.edit_bones if (obj.mode == 'EDIT') else obj.data.bones).active
            aspect.bone_name = (bone.name if bone else "")
        else:
            aspect.bone_name = ""
    else:
        aspect.obj_name = ""
        aspect.bone_name = ""
    
    return {'FINISHED'}

@addon.Operator(idname="view3d.coordsystem_new", options={'INTERNAL', 'REGISTER'}, description="New coordsystem")
def Operator_Coordsystem_New(self, context, event):
    manager = context.screen.coordsystem_manager
    item = manager.coordsystems.new("Coordsys")
    manager.coordsystem.selector = item.name
    return {'FINISHED'}

@addon.Operator(idname="view3d.coordsystem_delete", options={'INTERNAL', 'REGISTER'}, description="Delete coordsystem")
def Operator_Coordsystem_Delete(self, context, event):
    manager = context.screen.coordsystem_manager
    manager.coordsystems.discard(manager.coordsystem.selector)
    if manager.coordsystems:
        manager.coordsystem.selector = manager.coordsystems[len(manager.coordsystems)-1].name
    return {'FINISHED'}

@addon.PropertyGroup
class CoordSystemManagerPG:
    defaults_initialized = False | prop()
    coordsystems = [CoordSystemPG] | prop() # IDBlocks
    coordsystem = CoordSystemPG | prop() # IDBlock selector
    current = property(lambda self: self.coordsystems.get(self.coordsystem.selector))
    
    def draw(self, layout):
        self.coordsystem.draw(layout)
        coordsys = self.current
        if coordsys: coordsys.draw(layout)
    
    def init_default_coordystems(self):
        if self.defaults_initialized: return
        
        for item in CoordSystemPG.items_LRS:
            if item[0] == 'OBJECT': continue
            coordsys = self.coordsystems.new(item[1])
            coordsys.aspect_L.mode = item[0]
            coordsys.aspect_R.mode = item[0]
            coordsys.aspect_S.mode = item[0]
        
        coordsys = self.coordsystems.new("Normal")
        coordsys.aspect_L.mode = 'AVERAGE'
        coordsys.aspect_R.mode = 'NORMAL'
        coordsys.aspect_S.mode = 'GLOBAL'
        
        self.coordsystem.selector = "Global"
        
        self.defaults_initialized = True
    
    @classmethod
    def after_register(cls):
        manager = bpy.context.screen.coordsystem_manager
        if not manager.coordsystem.is_bound:
            manager.coordsystem.bind(manager.coordsystems, new="view3d.coordsystem_new", delete="view3d.coordsystem_delete", reselect=True)
        manager.init_default_coordystems() # assignment to selector must be done AFTER the binding

addon.type_extend("Screen", "coordsystem_manager", (CoordSystemManagerPG | prop()))

# We can't do this in register() because of the restricted context
after_register_callbacks.append(CoordSystemManagerPG.after_register)

@LeftRightPanel(idname="VIEW3D_PT_coordsystem", space_type='VIEW_3D', category="Batch", label="Coordinate System")
class Panel_Coordsystem:
    def draw(self, context):
        layout = NestedLayout(self.layout)
        context.screen.coordsystem_manager.draw(layout)

def make_vector_base():
    class VectorBase:
        uniformity_items = [
            ('INDEPENDENT', "Independent", "", 'UNLINKED'),
            ('COPY', "Copy", "", 'LINKED'),
            ('OFFSET', "Offset", "", 'ZOOMIN'), # PLUS
            ('PROPORTIONAL', "Proportional", "", 'PROP_CON'), # X CURVE_PATH
        ]
        uniformity_icons = {item[0]:item[3] for item in uniformity_items}
        uniformity = 'INDEPENDENT' | prop("Uniformity", items=uniformity_items)
    return VectorBase

@addon.PropertyGroup
class FloatPG3:
    value = 0.0 | prop(precision=3)

@addon.PropertyGroup
class FloatPG4:
    value = 0.0 | prop(precision=4)

@addon.PropertyGroup
class FloatPG5:
    value = 0.0 | prop(precision=5)

@addon.PropertyGroup
class LocationPG(make_vector_base()):
    x = [FloatPG5] | prop()
    x_lock = False | prop()
    
    y = [FloatPG5] | prop()
    y_lock = False | prop()
    
    z = [FloatPG5] | prop()
    z_lock = False | prop()
    
    def safe_vector(self, vc):
        return (0.0 if vc is None else vc)
    def set_vector(self, i, v):
        self.x[i].value = self.safe_vector(v[0])
        self.y[i].value = self.safe_vector(v[1])
        self.z[i].value = self.safe_vector(v[2])
    
    def safe_lock(self, vc):
        return (True if vc is None else vc)
    def set_lock(self, v):
        self.x_lock = self.safe_lock(v[0])
        self.y_lock = self.safe_lock(v[1])
        self.z_lock = self.safe_lock(v[2])
    
    def draw(self, layout, summaries, text, folded=False):
        with layout.row():
            with layout.fold(text, "row"):
                is_folded = layout.folded
            
            icon = self.uniformity_icons[self.uniformity]
            layout.prop_menu_enum(self, "uniformity", text="", icon=icon)
        
        if (not is_folded) and summaries:
            with layout.column(True):
                self.draw_axis(layout, summaries, 0, "x", "x")
                self.draw_axis(layout, summaries, 1, "y", "y")
                self.draw_axis(layout, summaries, 2, "z", "z")
    
    def match_summaries(self, summaries, axis=None):
        if axis is None:
            self.match_summaries(summaries, self.x)
            self.match_summaries(summaries, self.y)
            self.match_summaries(summaries, self.z)
        elif len(axis) != len(summaries):
            axis.clear()
            for i in range(len(summaries)):
                axis.add()
    
    def draw_axis(self, layout, summaries, axis_i, axis_id, axis_name):
        axis = getattr(self, axis_id)
        axis_lock = getattr(self, axis_id+"_lock")
        
        self.match_summaries(summaries, axis)
        
        vector_same = self.get("vector:same", True)
        lock_same = self.get("lock:same", True)
        
        with layout.row(True):
            with layout.row(True)(alert=not vector_same[axis_i]):
                for axis_item in axis:
                    layout.prop(axis_item, "value", text=axis_name)
            
            with layout.row(True)(alert=not lock_same[axis_i]):
                icon = ('LOCKED' if axis_lock else 'UNLOCKED')
                layout.prop(self, axis_id+"_lock", text="", icon=icon, toggle=True)

@addon.PropertyGroup
class RotationPG(make_vector_base()):
    x = [FloatPG3] | prop()
    x_lock = False | prop()
    
    y = [FloatPG3] | prop()
    y_lock = False | prop()
    
    z = [FloatPG3] | prop()
    z_lock = False | prop()
    
    w = [FloatPG3] | prop()
    w_lock = False | prop()
    
    def safe_vector(self, vc):
        return (0.0 if vc is None else vc)
    def set_vector(self, i, v):
        self.x[i].value = self.safe_vector(v[0])
        self.y[i].value = self.safe_vector(v[1])
        self.z[i].value = self.safe_vector(v[2])
        self.w[i].value = self.safe_vector(v[3])
    
    def safe_lock(self, vc):
        return (True if vc is None else vc)
    def set_lock(self, v):
        self.x_lock = self.safe_lock(v[0])
        self.y_lock = self.safe_lock(v[1])
        self.z_lock = self.safe_lock(v[2])
        self.w_lock = self.safe_lock(v[3])
    
    def draw(self, layout, summaries, text, folded=False):
        with layout.row():
            with layout.fold(text, "row"):
                is_folded = layout.folded
            
            icon = self.uniformity_icons[self.uniformity]
            layout.prop_menu_enum(self, "uniformity", text="", icon=icon)
        
        if (not is_folded) and summaries:
            with layout.column(True):
                self.draw_axis(layout, summaries, "x", "x")
                self.draw_axis(layout, summaries, "y", "y")
                self.draw_axis(layout, summaries, "z", "z")
                self.draw_axis(layout, summaries, "w", "w")
    
    def match_summaries(self, summaries, axis=None):
        if axis is None:
            self.match_summaries(summaries, self.x)
            self.match_summaries(summaries, self.y)
            self.match_summaries(summaries, self.z)
            self.match_summaries(summaries, self.w)
        elif len(axis) != summaries:
            axis.clear()
            for i in range(len(summaries)):
                axis.add()
    
    def draw_axis(self, layout, summaries, axis_id, axis_name):
        axis = getattr(self, axis_id)
        axis_lock = getattr(self, axis_id+"_lock")
        self.match_summaries(summaries, axis)
        with layout.row(True):
            for axis_item in axis:
                layout.prop(axis_item, "value", text=axis_name)
            icon = ('LOCKED' if axis_lock else 'UNLOCKED')
            layout.prop(self, axis_id+"_lock", text="", icon=icon, toggle=True)

@addon.PropertyGroup
class ScalePG(make_vector_base()):
    x = [FloatPG3] | prop()
    x_lock = False | prop()
    
    y = [FloatPG3] | prop()
    y_lock = False | prop()
    
    z = [FloatPG3] | prop()
    z_lock = False | prop()
    
    def safe_vector(self, vc):
        return (0.0 if vc is None else vc)
    def set_vector(self, i, v):
        self.x[i].value = self.safe_vector(v[0])
        self.y[i].value = self.safe_vector(v[1])
        self.z[i].value = self.safe_vector(v[2])
    
    def safe_lock(self, vc):
        return (True if vc is None else vc)
    def set_lock(self, v):
        self.x_lock = self.safe_lock(v[0])
        self.y_lock = self.safe_lock(v[1])
        self.z_lock = self.safe_lock(v[2])
    
    def draw(self, layout, summaries, text, folded=False):
        with layout.row():
            with layout.fold(text, "row"):
                is_folded = layout.folded
            
            icon = self.uniformity_icons[self.uniformity]
            layout.prop_menu_enum(self, "uniformity", text="", icon=icon)
        
        if (not is_folded) and summaries:
            with layout.column(True):
                self.draw_axis(layout, summaries, "x", "x")
                self.draw_axis(layout, summaries, "y", "y")
                self.draw_axis(layout, summaries, "z", "z")
    
    def match_summaries(self, summaries, axis=None):
        if axis is None:
            self.match_summaries(summaries, self.x)
            self.match_summaries(summaries, self.y)
            self.match_summaries(summaries, self.z)
        elif len(axis) != summaries:
            axis.clear()
            for i in range(len(summaries)):
                axis.add()
    
    def draw_axis(self, layout, summaries, axis_id, axis_name):
        axis = getattr(self, axis_id)
        axis_lock = getattr(self, axis_id+"_lock")
        self.match_summaries(summaries, axis)
        with layout.row(True):
            for axis_item in axis:
                layout.prop(axis_item, "value", text=axis_name)
            icon = ('LOCKED' if axis_lock else 'UNLOCKED')
            layout.prop(self, axis_id+"_lock", text="", icon=icon, toggle=True)

@addon.PropertyGroup
class ObjectTransformPG:
    location = LocationPG | prop()
    rotation = RotationPG | prop()
    scale = ScalePG | prop()
    dimensions = ScalePG | prop()
    
    def refresh(self, context, summaries, queries, coordsystem):
        csm = CoordSystemMatrix(coordsystem)
        
        lock_queries = {"count", "same", "mean"}
        
        self.location.match_summaries(summaries)
        aggr_location = VectorAggregator(3, 'NUMBER', queries)
        aggr_location_lock = VectorAggregator(3, 'BOOL', lock_queries)
        
        for obj in context.selected_objects:
            obj_LRS = csm.transform(context, obj)
            
            aggr_location.add(obj_LRS[0])
            aggr_location_lock.add(obj.lock_location)
        
        obj = context.active_object
        if obj:
            obj_LRS = csm.transform(context, obj)
        else:
            obj_LRS = (Vector(), Quaternion(), Vector((1,1,1)))
        
        for i, summary in enumerate(summaries):
            if summary == 'ACTIVE':
                self.location.set_vector(i, obj_LRS[0])
            else:
                query = summary.lower()
                self.location.set_vector(i, getattr(aggr_location, query))
        
        self.location["vector:same"] = aggr_location.same
        
        self.location.set_lock(aggr_location_lock.mean)
        self.location["lock:same"] = aggr_location_lock.same
    
    def draw(self, layout, summaries):
        self.location.draw(layout, summaries, "Location", folded=False)
        self.rotation.draw(layout, summaries, "Rotation", folded=False)
        self.scale.draw(layout, summaries, "Scale", folded=False)
        self.dimensions.draw(layout, summaries, "Dimensions", folded=False)

@addon.PropertyGroup
class MeshTransformPG:
    pass

@addon.PropertyGroup
class CurveTransformPG:
    pass

@addon.PropertyGroup
class MetaTransformPG:
    pass

@addon.PropertyGroup
class LatticeTransformPG:
    pass

@addon.PropertyGroup
class PoseTransformPG:
    pass

@addon.PropertyGroup
class BoneTransformPG:
    pass

@addon.PropertyGroup
class GreaseTransformPG:
    pass

@addon.PropertyGroup
class CursorTransformPG:
    pass

@addon.Operator(idname="object.batch_{}_summary".format(category_name), options={'INTERNAL'}, description=
"Click: Summary menu")
def Operator_Summary(self, context, event, summary_name=""):
    category = get_category()
    options = get_options()

@addon.Operator(idname="object.batch_{}_property".format(category_name), options={'INTERNAL'}, description=
"Click: Property menu")
def Operator_Property(self, context, event, property_name=""):
    category = get_category()
    options = get_options()

# Should probably be stored in each Screen?
@addon.PropertyGroup
class ContextTransformPG:
    # Currently Blender doesn't support user-defined properties
    # for SpaceView3D -> we have to maintain a separate mapping.
    v3d_key = 0 | prop()
    
    # Summaries are stored here because they might be different for each 3D view
    summary_items = [
        ('ACTIVE', "Active", "", 'ROTACTIVE'),
        ('MIN', "Min", "", 'MOVE_DOWN_VEC'),
        ('MAX', "Max", "", 'MOVE_UP_VEC'),
        ('CENTER', "Center", "", 'ROTATE'),
        ('RANGE', "Range", "", 'STICKY_UVS_VERT'),
        ('MEAN', "Mean", "", 'ROTATECENTER'),
        ('STDDEV', "StdDev", "", 'SMOOTHCURVE'),
        ('MEDIAN', "Median", "", 'SORTSIZE'),
        #('MODE', "Mode", "", 'GROUP_VERTEX'),
    ]
    summaries = {'ACTIVE'} | prop("Summaries", items=summary_items)
    
    use_pinned_coordsystem = False | prop()
    coordsystem_selector = CoordSystemPG | prop() # IDBlock selector
    
    @property
    def coordsystem(self):
        manager = bpy.context.screen.coordsystem_manager
        return manager.coordsystems.get(self.coordsystem_selector.selector)
    
    def draw_coordsystem_selector(self, layout):
        manager = bpy.context.screen.coordsystem_manager
        if not self.coordsystem_selector.is_bound:
            self.coordsystem_selector.bind(manager.coordsystems, rename=False)
        
        with layout.row(True):
            icon = ('PINNED' if self.use_pinned_coordsystem else 'UNPINNED')
            layout.prop(self, "use_pinned_coordsystem", text="", icon=icon, toggle=True)
            if self.use_pinned_coordsystem:
                self.coordsystem_selector.draw(layout)
            else:
                self.coordsystem_selector.selector = manager.coordsystem.selector
                with layout.row(True)(enabled=False):
                    self.coordsystem_selector.draw(layout)
    
    object = ObjectTransformPG | prop()
    mesh = MeshTransformPG | prop()
    curve = CurveTransformPG | prop()
    meta = MetaTransformPG | prop()
    lattice = LatticeTransformPG | prop()
    pose = PoseTransformPG | prop()
    bone = BoneTransformPG | prop()
    
    # Since Blender 2.73, grease pencil data is editable too
    grease = GreaseTransformPG | prop()
    
    # TODO: move this to a separate place
    # Cursor isn't aggregated, but it still might be useful
    # to see/manipulate it in non-global coordsystem
    cursor = CursorTransformPG | prop()
    
    def refresh(self, context):
        # Here we actually need them in order
        summaries = [item[0] for item in self.summary_items if item[0] in self.summaries]
        queries = set(("count", "same"))
        queries.update(summary.lower() for summary in summaries if summary != 'ACTIVE')
        
        mode = context.mode
        if mode == 'EDIT':
            pass
        elif mode == 'POSE':
            pass
        else: # OBJECT and others
            self.object.refresh(context, summaries, queries, self.coordsystem)
    
    def draw(self, layout):
        self.draw_coordsystem_selector(layout)
        
        with layout.row(True):
            for item in self.summary_items:
                if item[0] in self.summaries:
                    layout.operator("object.batch_{}_summary".format(category_name), text=item[1])
            
            if not self.summaries: layout.label(" ") # just to fill space
            
            with layout.row(True)(scale_x=1.0): # scale_x to prevent up/down arrows from appearing
                layout.prop_menu_enum(self, "summaries", text="", icon='DOTSDOWN')
        
        mode = bpy.context.mode
        if mode == 'EDIT':
            pass
        elif mode == 'POSE':
            pass
        else: # OBJECT and others
            self.object.draw(layout, self.summaries)

@addon.PropertyGroup
class CategoryPG:
    was_drawn = False | prop()
    next_refresh_time = -1.0 | prop()
    
    needs_refresh = True | prop()
    def tag_refresh(self):
        self.needs_refresh = True
        tag_redraw()
    
    transforms = [ContextTransformPG] | prop()
    
    selection_info = None
    
    def refresh(self, context, needs_refresh=False):
        cls = self.__class__
        options = get_options()
        preferences = addon.preferences
        
        selection_info = Selection().stateless_info
        needs_refresh |= (selection_info != cls.selection_info)
        
        needs_refresh |= self.needs_refresh
        needs_refresh |= options.autorefresh and (time.clock() > self.next_refresh_time)
        if not needs_refresh: return
        self.next_refresh_time = time.clock() + preferences.refresh_interval
        cls.selection_info = selection_info
        
        processing_time = time.clock()
        
        # TODO
        if not self.transforms: # for now
            self.transforms.add() # for now
        for transform in self.transforms:
            transform.refresh(context)
        
        processing_time = time.clock() - processing_time
        # Disable autorefresh if it takes too much time
        #if processing_time > 0.05: options.autorefresh = False
        
        self.needs_refresh = False
    
    def draw(self, layout):
        layout = NestedLayout(layout, addon.module_name+".transform")
        
        self.was_drawn = True
        self.refresh(bpy.context)
        
        options = get_options()
        
        # TODO: search for current context's SpaceView3D
        for transform in self.transforms:
            transform.draw(layout)
            break # for now

@addon.Menu(idname="OBJECT_MT_batch_{}_spatial_queries".format(category_name), label="Spatial queries", description="Spatial queries")
def Menu_Spatial_Queries(self, context):
    layout = NestedLayout(self.layout)
    layout.label("Distance 0D (to point)")
    layout.label("Distance 1D (to curve)")
    layout.label("Distance 2D (to surface)")
    layout.label("Distance 3D (to volume)")
    layout.label("Half-spaces")

@addon.Operator(idname="view3d.pick_{}".format(category_name_plural), options={'INTERNAL', 'REGISTER'}, description=
"Pick {}(s) from the object under mouse".format(Category_Name))
class Operator_Pick(Pick_Base):
    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT')
    
    def obj_to_info(self, obj):
        L, R, S = obj.matrix_world.decompose()
        L = "{:.5f}, {:.5f}, {:.5f}".format(*tuple(L))
        R = "{:.3f}, {:.3f}, {:.3f}".format(*tuple(math.degrees(axis) for axis in R.to_euler()))
        S = "{:.3f}, {:.3f}, {:.3f}".format(*tuple(S))
        return "Location: {}, Rotation: {}, Scale: {}".format(L, R, S)
    
    def on_confirm(self, context, obj):
        category = get_category()
        options = get_options()
        bpy.ops.ed.undo_push(message="Pick {}".format(Category_Name_Plural))
        #BatchOperations.copy(obj)
        self.report({'INFO'}, "{} copied".format(Category_Name_Plural))
        #BatchOperations.paste(options.iterate_objects(context), options.paste_mode)
        category.tag_refresh()

# NOTE: only when 'REGISTER' is in bl_options and {'FINISHED'} is returned,
# the operator will be recorded in wm.operators and info reports

@addon.Operator(idname="object.batch_{}_copy".format(category_name), options={'INTERNAL'}, description=
"Click: Copy")
def Operator_Copy(self, context, event, object_name=""):
    active_obj = (bpy.data.objects.get(object_name) if object_name else context.object)
    if not active_obj: return
    category = get_category()
    options = get_options()
    # TODO ?

@addon.Operator(idname="object.batch_{}_paste".format(category_name), options={'INTERNAL', 'REGISTER'}, description=
"Click: Paste (+Ctrl: Override, +Shift: Add, +Alt: Filter)")
def Operator_Paste(self, context, event):
    category = get_category()
    options = get_options()
    # TODO ?
    return {'FINISHED'}

@addon.PropertyGroup
class CategoryOptionsPG:
    autorefresh = True | prop("Auto-refresh")
    
    sync_3d_views = True | prop("Synchronize between 3D views")
    
    uniformity_items = [
        ('COPY', "Copy", "", 'LINKED'),
        ('OFFSET', "Offset", "", 'ZOOMIN'), # PLUS
        ('PROPORTIONAL', "Proportional", "", 'PROP_CON'), # X CURVE_PATH
    ]
    uniformity = 'COPY' | prop("Batch modification", items=uniformity_items)

@addon.Menu(idname="VIEW3D_MT_batch_{}_options".format(category_name_plural), label="Options", description="Options")
def Menu_Options(self, context):
    layout = NestedLayout(self.layout)
    options = get_options()
    layout.prop_menu_enum(options, "uniformity", text="Batch modification")
    layout.prop(options, "autorefresh", text="Auto refresh")
    layout.prop(options, "sync_3d_views", text="Sync 3D views")
    layout.label("Apply pos/rot/scale") # TODO
    layout.label("Set geometry origin") # TODO

@addon.Operator(idname="object.batch_{}_refresh".format(category_name), options={'INTERNAL', 'REGISTER'}, description=
"Click: Force refresh, Ctrl+Click: Toggle auto-refresh")
def Operator_Refresh(self, context, event):
    category = get_category()
    options = get_options()
    if event.ctrl:
        options.autorefresh = not options.autorefresh
    else:
        category.refresh(context, True)
    return {'FINISHED'}

@LeftRightPanel(idname="VIEW3D_PT_batch_{}".format(category_name_plural), space_type='VIEW_3D', category="Batch", label="Batch {}".format(Category_Name_Plural))
class Panel_Category:
    def draw(self, context):
        layout = NestedLayout(self.layout)
        category = get_category()
        options = get_options()
        
        with layout.row():
            with layout.row(True):
                layout.menu("OBJECT_MT_batch_{}_spatial_queries".format(category_name), icon='BORDERMOVE', text="")
                layout.operator("view3d.pick_{}".format(category_name_plural), icon='EYEDROPPER', text="")
                layout.operator("object.batch_{}_copy".format(category_name), icon='COPYDOWN', text="")
                layout.operator("object.batch_{}_paste".format(category_name), icon='PASTEDOWN', text="")
            
            icon = ('PREVIEW_RANGE' if options.autorefresh else 'FILE_REFRESH')
            layout.operator("object.batch_{}_refresh".format(category_name), icon=icon, text="")
            
            icon = 'SCRIPTWIN'
            layout.menu("VIEW3D_MT_batch_{}_options".format(category_name_plural), icon=icon, text="")
        
        category.draw(layout)

setattr(addon.External, category_name_plural, CategoryPG | -prop())
get_category = eval("lambda: addon.external.{}".format(category_name_plural))

setattr(addon.Preferences, category_name_plural, CategoryOptionsPG | prop())
get_options = eval("lambda: addon.preferences.{}".format(category_name_plural))
