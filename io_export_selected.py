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
    "name": "Export Selected",
    "author": "dairin0d, rking, moth3r",
    "version": (2, 1, 5),
    "blender": (2, 7, 0),
    "location": "File > Export > Selected",
    "description": "Export selected objects to a chosen format",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Import-Export/Export_Selected",
    "tracker_url": "https://github.com/dairin0d/export-selected/issues",
    "category": "Import-Export"}
#============================================================================#

import bpy

from bpy_extras.io_utils import ExportHelper

from mathutils import Vector, Matrix, Quaternion, Euler

import os
import json
import re
import hashlib

def bpy_path_normslash(path):
    return path.replace(os.path.sep, "/")

def bpy_path_join(*paths):
    # use os.path.join logic (it's not that simple)
    return bpy_path_normslash(os.path.join(*paths))

def bpy_path_splitext(path):
    path = bpy_path_normslash(path)
    i_split = path.rfind(".")
    if i_split < 0: return (path, "")
    return (path[:i_split], path[i_split:])

# For some reason, when path contains "//", os.path.split ignores single slashes
# When path ends with slash, return dir without slash, except when it's / or //
def bpy_path_split(path):
    path = bpy_path_normslash(path)
    i_split = path.rfind("/") + 1
    dir_part = path[:i_split]
    file_part = path[i_split:]
    dir_part_strip = dir_part.rstrip("/")
    if dir_part_strip: dir_part = dir_part[:len(dir_part_strip)]
    return (dir_part, file_part)

def bpy_path_dirname(path):
    return bpy_path_split(path)[0]

def bpy_path_basename(path):
    return bpy_path_split(path)[1]

operator_presets_dir = bpy_path_join(bpy.utils.resource_path('USER'), "scripts", "presets", "operator")

object_types = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE', 'LATTICE', 'EMPTY', 'CAMERA', 'LAMP', 'SPEAKER']

bpy_props = {
    bpy.props.BoolProperty,
    bpy.props.BoolVectorProperty,
    bpy.props.IntProperty,
    bpy.props.IntVectorProperty,
    bpy.props.FloatProperty,
    bpy.props.FloatVectorProperty,
    bpy.props.StringProperty,
    bpy.props.EnumProperty,
    bpy.props.PointerProperty,
    bpy.props.CollectionProperty,
}

def is_bpy_prop(value):
    return (isinstance(value, tuple) and (len(value) == 2) and (value[0] in bpy_props) and isinstance(value[1], dict))

def iter_public_bpy_props(cls, exclude_hidden=False):
    for key in dir(cls):
        if key.startswith("_"): continue
        value = getattr(cls, key)
        if not is_bpy_prop(value): continue
        if exclude_hidden:
            options = value[1].get("options", "")
            if 'HIDDEN' in options: continue
        yield (key, value)

def get_op(idname):
    category_name, op_name = idname.split(".")
    category = getattr(bpy.ops, category_name)
    return getattr(category, op_name)

def layers_intersect(a, b, name_a="layers", name_b=None):
    return any(l0 and l1 for l0, l1 in zip(getattr(a, name_a), getattr(b, name_b or name_a)))

def obj_root(obj):
    while obj.parent:
        obj = obj.parent
    return obj

def obj_parents(obj):
    while obj.parent:
        yield obj.parent
        obj = obj.parent

def belongs_to_group(obj, group, consider_dupli=False):
    if not obj: return None
    # Object is either IN some group or INSTANTIATES that group, never both
    if obj.dupli_group == group:
        return ('DUPLI' if consider_dupli else None)
    elif obj.name in group.objects:
        return 'PART'
    return None

# FRAMES copies the object itself, but not its children
# VERTS and FACES copy the children
# GROUP copies the group contents

def get_dupli_roots(obj, scene=None, settings='VIEWPORT'):
    if (not obj) or (obj.dupli_type == 'NONE'): return None
    if not scene: scene = bpy.context.scene
    
    filter = None
    if obj.dupli_type in ('VERTS', 'FACES'):
        filter = set(obj.children)
    elif (obj.dupli_type == 'GROUP') and obj.dupli_group:
        filter = set(obj.dupli_group.objects)
    
    roots = []
    if obj.dupli_list: obj.dupli_list_clear()
    obj.dupli_list_create(scene, settings)
    for dupli in obj.dupli_list:
        if (not filter) or (dupli.object in filter):
            roots.append((dupli.object, Matrix(dupli.matrix)))
    obj.dupli_list_clear()
    
    return roots

def instantiate_duplis(obj, scene=None, settings='VIEWPORT', depth=-1):
    if (not obj) or (obj.dupli_type == 'NONE'): return
    if not scene: scene = bpy.context.scene
    
    if depth == 0: return
    if depth > 0: depth -= 1
    
    roots = get_dupli_roots(obj, scene, settings)
    
    dupli_type = obj.dupli_type
    # Prevent recursive copying in FRAMES dupli mode
    obj.dupli_type = 'NONE'
    
    dst_info = []
    src_dst = {}
    for src_obj, matrix in roots:
        dst_obj = src_obj.copy()
        dst_obj.constraints.clear()
        scene.objects.link(dst_obj)
        if dupli_type == 'FRAMES':
            dst_obj.animation_data_clear()
        dst_info.append((dst_obj, src_obj, matrix))
        src_dst[src_obj] = dst_obj
    
    scene.update() # <-- important
    
    for dst_obj, src_obj, matrix in dst_info:
        dst_parent = src_dst.get(src_obj.parent)
        if dst_parent:
            # parent_type, parent_bone, parent_vertices
            # should be copied automatically
            dst_obj.parent = dst_parent
        else:
            dst_obj.parent_type = 'OBJECT'
            dst_obj.parent = obj
    
    for dst_obj, src_obj, matrix in dst_info:
        dst_obj.matrix_world = matrix
    
    for dst_obj, src_obj, matrix in dst_info:
        instantiate_duplis(dst_obj, scene, settings, depth)

class PrimitiveLock(object):
    "Primary use of such lock is to prevent infinite recursion"
    def __init__(self):
        self.count = 0
    def __bool__(self):
        return bool(self.count)
    def __enter__(self):
        self.count += 1
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.count -= 1

class ToggleObjectMode:
    def __init__(self, mode='OBJECT', undo=False):
        if not isinstance(mode, str):
            mode = ('OBJECT' if mode else None)
        
        obj = bpy.context.object
        self.mode = (mode if obj and (obj.mode != mode) else None)
        self.undo = undo
    
    def __enter__(self):
        if self.mode:
            edit_preferences = bpy.context.user_preferences.edit
            
            self.global_undo = edit_preferences.use_global_undo
            # if self.mode == True, bpy.context.object exists
            self.prev_mode = bpy.context.object.mode
            
            if self.prev_mode != self.mode:
                if self.undo is not None:
                    edit_preferences.use_global_undo = self.undo
                bpy.ops.object.mode_set(mode=self.mode)
        
        return self
    
    def __exit__(self, type, value, traceback):
        if self.mode:
            edit_preferences = bpy.context.user_preferences.edit
            
            if self.prev_mode != self.mode:
                bpy.ops.object.mode_set(mode=self.prev_mode)
                edit_preferences.use_global_undo = self.global_undo

#============================================================================#

# Adapted from https://gist.github.com/regularcoder/8254723
def fletcher(data, n): # n should be 16, 32 or 64
    nbytes = min(max(n // 16, 1), 4)
    mod = 2 ** (8 * nbytes) - 1
    sum1 = sum2 = 0
    for i in range(0, len(data), nbytes):
        block = int.from_bytes(data[i:i + nbytes], 'little')
        sum1 = (sum1 + block) % mod
        sum2 = (sum2 + sum1) % mod
    return sum1 + (sum2 * (mod+1))

def hashnames():
    hashnames_codes = [chr(o) for o in range(ord("0"), ord("9")+1)]
    hashnames_codes += [chr(o) for o in range(ord("A"), ord("Z")+1)]
    n = len(hashnames_codes)
    def _hashnames(names):
        binary_data = "\0".join(sorted(names)).encode()
        hash_value = fletcher(binary_data, 32)
        result = []
        while True:
            k = hash_value % n
            result.append(hashnames_codes[k])
            hash_value = (hash_value - k) // n
            if hash_value == 0: break
        return "".join(result)
    return _hashnames
hashnames = hashnames()

def replace_extension(path, ext):
    name = bpy_path_basename(path)
    if name and not name.lower().endswith(ext.lower()):
        path = bpy_path_splitext(path)[0] + ext
    return path

forbidden_chars = "\x00-\x1f/" # on all OSes
forbidden_chars += "<>:\"|?*\\\\" # on Windows/FAT/NTFS
forbidden_chars = "["+forbidden_chars+"]"
def clean_filename(filename, sub="-"):
    return re.sub(forbidden_chars, sub, filename)

def iter_exporters():
    for category_name in dir(bpy.ops):
        if "export" not in category_name: continue
        op_category = getattr(bpy.ops, category_name)
        for name in dir(op_category):
            idname = category_name + "." + name
            if idname == ExportSelected.bl_idname: continue
            if "export" not in idname: continue
            yield (idname, getattr(op_category, name))

def iter_exporter_info():
    # Special case: unconventional "exporter"
    yield ('BLEND', "Blend", ".blend", "*.blend")
    
    # Special case: unconventional operator name, ext/glob aren't exposed
    yield ('wm.collada_export', "Collada", ".dae", "*.dae")
    
    # Special case: unconventional operator name, ext/glob aren't exposed
    yield ('wm.alembic_export', "Alembic", ".abc", "*.abc")
    
    for idname, op in iter_exporters():
        op_class = type(op.get_instance())
        rna = op.get_rna()
        name = rna.rna_type.name
        if name.lower().startswith("export "): name = name[len("export "):]
        filename_ext = getattr(op_class, "filename_ext", "")
        filter_glob = getattr(rna, "filter_glob", "*"+filename_ext)
        yield (idname, name, filename_ext, filter_glob)

def get_exporter_name(idname):
    if idname == 'BLEND': return "Blend"
    op = get_op(idname)
    rna = op.get_rna()
    name = rna.rna_type.name
    if name.lower().startswith("export "): name = name[len("export "):]
    return name

def get_exporter_class(idname):
    if idname == 'BLEND':
        return None
    elif idname == 'wm.collada_export':
        return ColladaEmulator
    elif idname == 'wm.alembic_export':
        return AlembicEmulator
    else:
        op = get_op(idname)
        return type(op.get_instance())

class ColladaEmulator:
    # Special case: Collada (built-in) -- has no explicitly defined Python properties
    apply_modifiers = bpy.props.BoolProperty(name="Apply Modifiers", description="Apply modifiers to exported mesh (non destructive)", default=False)
    #export_mesh_type=0 # couldn't find correspondence in the UI
    export_mesh_type_selection = bpy.props.EnumProperty(name="Type of modifiers", description="Modifier resolution for export", default='view', items=[('render', "Render", "Apply modifier's render settings"), ('view', "View", "Apply modifier's view settings")])
    selected = bpy.props.BoolProperty(name="Selection Only", description="Export only selected elements", default=False)
    include_children = bpy.props.BoolProperty(name="Include Children", description="Export all children of selected objects (even if not selected)", default=False)
    include_armatures = bpy.props.BoolProperty(name="Include Armatures", description="Export related armatures (even if not selected)", default=False)
    include_shapekeys = bpy.props.BoolProperty(name="Include Shape Keys", description="Export all Shape Keys from Mesh Objects", default=True)
    deform_bones_only = bpy.props.BoolProperty(name="Deform Bones only", description="Only export deforming bones with armatures", default=False)
    active_uv_only = bpy.props.BoolProperty(name="Only Active UV layer", description="Export textures assigned to the object UV maps", default=False)
    include_uv_textures = bpy.props.BoolProperty(name="Include UV Textures", description="Export textures assigned to the object UV maps", default=False)
    include_material_textures = bpy.props.BoolProperty(name="Include Material Textures", description="Export textures assigned to the object Materials", default=False)
    use_texture_copies = bpy.props.BoolProperty(name="Copy Textures", description="Copy textures to the same folder where .dae file is exported", default=True)
    triangulate = bpy.props.BoolProperty(name="Triangulate", description="Export Polygons (Quads & NGons) as Triangles", default=True)
    use_object_instantiation = bpy.props.BoolProperty(name="Use Object Instances", description="Instantiate multiple Objects from same Data", default=True)
    sort_by_name = bpy.props.BoolProperty(name="Sort by Object name", description="Sort exported data by Object name", default=False)
    #export_transformation_type=0 # couldn't find correspondence in the UI
    export_transformation_type_selection = bpy.props.EnumProperty(name="Transformation Type", description="Transformation type for translation, scale and rotation", default='matrix', items=[('both', "Both", "Use <matrix> AND <translate>, <rotate>, <scale> to specify transformations"), ('transrotloc', "TransLocRot", "Use <translate>, <rotate>, <scale> to specify transformations"), ('matrix', "Matrix", "Use <matrix> to specify transformations")])
    open_sim = bpy.props.BoolProperty(name="Export for OpenSim", description="Compatibility mode for OpenSim and compatible online worlds", default=False)
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Export Data Options", icon='MESH_DATA')
        row = box.split(0.6)
        row.prop(self, "apply_modifiers")
        row.prop(self, "export_mesh_type_selection", text="")
        box.prop(self, "selected")
        box.prop(self, "include_children")
        box.prop(self, "include_armatures")
        box.prop(self, "include_shapekeys")
        
        box = layout.box()
        box.label(text="Texture Options", icon='TEXTURE')
        box.prop(self, "active_uv_only")
        box.prop(self, "include_uv_textures")
        box.prop(self, "include_material_textures")
        box.prop(self, "use_texture_copies", text="Copy")
        
        box = layout.box()
        box.label(text="Armature Options", icon='ARMATURE_DATA')
        box.prop(self, "deform_bones_only")
        box.prop(self, "open_sim")
        
        box = layout.box()
        box.label(text="Collada Options", icon='MODIFIER')
        box.prop(self, "triangulate")
        box.prop(self, "use_object_instantiation")
        row = box.split(0.6)
        row.label(text="Transformation Type")
        row.prop(self, "export_transformation_type_selection", text="")
        box.prop(self, "sort_by_name")

class AlembicEmulator:
    # Special case: Alembic (built-in) -- has no explicitly defined Python properties
    global_scale = bpy.props.FloatProperty(name="Scale", description="Value by which to enlarge or shrink the objects with respect to the world's origin", default=1.0, min=0.0001, max=1000.0, step=1, precision=3)
    start = bpy.props.IntProperty(name="Start Frame", description="Start Frame", default=1)
    end = bpy.props.IntProperty(name="End Frame", description="End Frame", default=1)
    xsamples = bpy.props.IntProperty(name="Transform Samples", description="Number of times per frame transformations are sampled", default=1, min=1, max=128)
    gsamples = bpy.props.IntProperty(name="Geometry Samples", description="Number of times per frame object data are sampled", default=1, min=1, max=128)
    sh_open = bpy.props.FloatProperty(name="Shutter Open", description="Time at which the shutter is open", default=0.0, min=-1, max=1, step=1, precision=3)
    sh_close = bpy.props.FloatProperty(name="Shutter Close", description="Time at which the shutter is closed", default=1.0, min=-1, max=1, step=1, precision=3)
    selected = bpy.props.BoolProperty(name="Selected Objects Only", description="Export only selected objects", default=False)
    renderable_only = bpy.props.BoolProperty(name="Renderable Objects Only", description="Export only objects marked renderable in the outliner", default=True)
    visible_layers_only = bpy.props.BoolProperty(name="Visible Layers Only", description="Export only objects in visible layers", default=False)
    flatten = bpy.props.BoolProperty(name="Flatten Hierarchy", description="Do not preserve objects' parent/children relationship", default=False)
    uvs = bpy.props.BoolProperty(name="UVs", description="Export UVs", default=True)
    packuv = bpy.props.BoolProperty(name="Pack UV Islands", description="Export UVs with packed island", default=True)
    normals = bpy.props.BoolProperty(name="Normals", description="Export normals", default=True)
    vcolors = bpy.props.BoolProperty(name="Vertex Colors", description="Export vertex colors", default=False)
    face_sets = bpy.props.BoolProperty(name="Face Sets", description="Export per face shading group assignments", default=False)
    subdiv_schema = bpy.props.BoolProperty(name="Use Subdivision Schema", description="Export meshes using Alembic's subdivision schema", default=False)
    apply_subdiv = bpy.props.BoolProperty(name="Apply Subsurf", description="Export subdivision surfaces as meshes", default=False)
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Manual Transform:")
        box.prop(self, "global_scale")
        
        box = layout.box()
        box.label(text="Scene Options:", icon='SCENE_DATA')
        box.prop(self, "start")
        box.prop(self, "end")
        box.prop(self, "xsamples")
        box.prop(self, "gsamples")
        box.prop(self, "sh_open")
        box.prop(self, "sh_close")
        box.prop(self, "selected")
        box.prop(self, "renderable_only")
        box.prop(self, "visible_layers_only")
        box.prop(self, "flatten")
        
        box = layout.box()
        box.label(text="Object Options:", icon='OBJECT_DATA')
        box.prop(self, "uvs")
        box.prop(self, "packuv")
        box.prop(self, "normals")
        box.prop(self, "vcolors")
        box.prop(self, "face_sets")
        box.prop(self, "subdiv_schema")
        box.prop(self, "apply_subdiv")

#============================================================================#

class CurrentExporterProperties(bpy.types.PropertyGroup):
    __dict = {}
    __exporter = None
    
    @classmethod
    def _check(cls, exporter):
        return (cls.__exporter == exporter)
    
    @classmethod
    def _load_props(cls, exporter):
        if (cls.__exporter == exporter): return
        cls.__exporter = exporter
        
        CurrentExporterProperties.__dict = {}
        for key in list(cls._keys()):
            delattr(cls, key)
        
        template = get_exporter_class(exporter)
        if template:
            for key in dir(template):
                value = getattr(template, key)
                if is_bpy_prop(value):
                    if not key.startswith("_"): setattr(cls, key, value)
                else:
                    CurrentExporterProperties.__dict[key] = value
    
    @classmethod
    def _keys(cls, exclude_hidden=False):
        for kv in iter_public_bpy_props(cls, exclude_hidden):
            yield kv[0]
    
    def __getattr__(self, name):
        return CurrentExporterProperties.__dict[name]
    
    def __setattr__(self, name, value):
        if hasattr(self.__class__, name) and (not name.startswith("_")):
            supercls = super(CurrentExporterProperties, self.__class__)
            supercls.__setattr__(self, name, value)
        else:
            CurrentExporterProperties.__dict[name] = value
    
    def draw(self, context):
        if not CurrentExporterProperties.__dict: return
        
        _draw = CurrentExporterProperties.__dict.get("draw")
        if _draw:
            try:
                _draw(self, context)
            except:
                _draw = None
                del CurrentExporterProperties.__dict["draw"]
        
        if not _draw:
            ignore = {"filepath", "filename_ext", "filter_glob"}
            for key in CurrentExporterProperties._keys(True):
                if key in ignore: continue
                self.layout.prop(self, key)

class ExportSelected_Base(ExportHelper):
    filename_ext = bpy.props.StringProperty(default="")
    filter_glob = bpy.props.StringProperty(default="*.*")
    
    __strings = {}
    __lock = PrimitiveLock()
    
    @staticmethod
    def __add_item(items, idname, name, description):
        # To avoid crash, references to Python strings must be kept alive
        # Seems like id/name/description have to be DIFFERENT OBJECTS, otherwise there will be glitches
        __strings = ExportSelected_Base.__strings
        idname = __strings.setdefault(idname, idname)
        name = __strings.setdefault(name, name)
        description = __strings.setdefault(description, description)
        items.append((idname, name, description))
    
    def get_preset_items(self, context):
        items = []
        preset_dir = bpy_path_join(operator_presets_dir, ExportSelected.bl_idname, "")
        if os.path.exists(preset_dir):
            for filename in os.listdir(preset_dir):
                if not os.path.isfile(bpy_path_join(preset_dir, filename)): continue
                name, ext = bpy_path_splitext(filename)
                if ext.lower() != ".json": continue
                ExportSelected_Base.__add_item(items, filename, name, name+" ")
        if not items: ExportSelected_Base.__add_item(items, '/NO_PRESETS/', "(No presets)", "")
        return items
    
    def update_preset(self, context):
        if self.preset_select == '/NO_PRESETS/': return
        
        preset_dir = bpy_path_join(operator_presets_dir, ExportSelected.bl_idname, "")
        preset_path = bpy_path_join(preset_dir, self.preset_select)
        
        if not os.path.isfile(preset_path): return
        
        try:
            with open(preset_path, "r") as f:
                json_data = json.loads(f.read())
        except (IOError, json.decoder.JSONDecodeError):
            self.preset_name = ""
            try:
                os.remove(preset_path)
            except IOError:
                pass
            return
        
        self.preset_name = bpy_path_splitext(self.preset_select)[0]
        
        def value_convert(value):
            if isinstance(value, list):
                if not value: return set()
                first_item = value[0]
                return set(value) if isinstance(first_item, str) else tuple(value)
            return value
        
        exporter_data = json_data.pop("exporter_props", {})
        
        for key, value in ExportSelected_Base.main_kwargs(self, True).items():
            if key not in json_data: continue
            setattr(self, key, value_convert(json_data[key]))
        
        self.exporter = self.exporter_str
        
        for key, value in ExportSelected_Base.exporter_kwargs(self).items():
            if key not in exporter_data: continue
            setattr(self.exporter_props, key, value_convert(exporter_data[key]))
    
    def update_preset_name(self, context):
        clean_name = clean_filename(self.preset_name)
        if self.preset_name != clean_name: self.preset_name = clean_name
    
    def save_preset(self, context):
        if not self.preset_save: return
        if not self.preset_name: return
        
        preset_dir = bpy_path_join(operator_presets_dir, ExportSelected.bl_idname, "")
        if not os.path.exists(preset_dir): os.makedirs(preset_dir)
        
        preset_path = bpy_path_join(preset_dir, self.preset_name+".json")
        
        exclude_keys = {"filepath", "filename_ext", "filter_glob", "check_existing"}
        
        def value_convert(value):
            if isinstance(value, set): return list(value)
            return value
        
        exporter_data = {}
        for key, value in ExportSelected_Base.exporter_kwargs(self).items():
            if key in exclude_keys: continue
            exporter_data[key] = value_convert(value)
        
        json_data = {"exporter_props":exporter_data}
        for key, value in ExportSelected_Base.main_kwargs(self, True).items():
            if key in exclude_keys: continue
            json_data[key] = value_convert(value)
        
        with open(preset_path, "w") as f:
            f.write(json.dumps(json_data, sort_keys=True, indent=4))
    
    def delete_preset(self, context):
        if not self.preset_delete: return
        if not self.preset_name: return
        
        preset_dir = bpy_path_join(operator_presets_dir, ExportSelected.bl_idname, "")
        preset_path = bpy_path_join(preset_dir, self.preset_name+".json")
        if os.path.isfile(preset_path): os.remove(preset_path)
        
        self.preset_name = ""
    
    preset_select = bpy.props.EnumProperty(name="Select preset", description="Select preset", items=get_preset_items, update=update_preset, options={'HIDDEN'})
    preset_name = bpy.props.StringProperty(name="Preset name", description="Preset name", default="", update=update_preset_name, options={'HIDDEN'})
    preset_save = bpy.props.BoolProperty(name="Save preset", description="Save preset", default=False, update=save_preset, options={'HIDDEN'})
    preset_delete = bpy.props.BoolProperty(name="Delete preset", description="Delete preset", default=False, update=delete_preset, options={'HIDDEN'})
    
    bundle_mode = bpy.props.EnumProperty(name="Bundling", description="Export to multiple files", default='NONE', items=[
        ('NONE', "Project", "No bundling (export to one file)", 'WORLD', 0),
        ('INDIVIDUAL', "Object", "Export each object separately", 'ROTATECOLLECTION', 1),
        ('ROOT', "Root", "Bundle by topmost parent", 'ARMATURE_DATA', 2),
        ('GROUP', "Group", "Bundle by group", 'GROUP', 3),
        ('LAYER', "Layer", "Bundle by layer", 'RENDERLAYERS', 4),
        ('MATERIAL', "Material", "Bundle by material", 'MATERIAL', 5),
    ])
    
    include_hierarchy = bpy.props.EnumProperty(name="Include", description="What objects to include", default='CHILDREN', items=[
        ('SELECTED', "Selected", "Selected objects", 'BONE_DATA', 0),
        ('CHILDREN', "Children", "Selected objects + their children", 'GROUP_BONE', 1),
        ('HIERARCHY', "Hierarchy", "Selected objects + their hierarchy", 'ARMATURE_DATA', 2),
        ('ALL', "All", "All objects", 'WORLD', 3),
    ])
    include_invisible = bpy.props.BoolProperty(name="Invisible", description="Allow invisible objects", default=True)
    
    object_types = bpy.props.EnumProperty(name="Object types", description="Object type(s) to export", options={'ENUM_FLAG'}, default=set(object_types), items=[
        ('MESH', "Mesh", "", 'OUTLINER_OB_MESH', 1 << 0),
        ('CURVE', "Curve", "", 'OUTLINER_OB_CURVE', 1 << 1),
        ('SURFACE', "Surface", "", 'OUTLINER_OB_SURFACE', 1 << 2),
        ('META', "Meta", "", 'OUTLINER_OB_META', 1 << 3),
        ('FONT', "Font", "", 'OUTLINER_OB_FONT', 1 << 4),
        ('ARMATURE', "Armature", "", 'OUTLINER_OB_ARMATURE', 1 << 5),
        ('LATTICE', "Lattice", "", 'OUTLINER_OB_LATTICE', 1 << 6),
        ('EMPTY', "Empty", "", 'OUTLINER_OB_EMPTY', 1 << 7),
        ('CAMERA', "Camera", "", 'OUTLINER_OB_CAMERA', 1 << 8),
        ('LAMP', "Lamp", "", 'OUTLINER_OB_LAMP', 1 << 9),
        ('SPEAKER', "Speaker", "", 'OUTLINER_OB_SPEAKER', 1 << 10),
    ])
    
    centering_mode = bpy.props.EnumProperty(name="Centering", description="Centering", default='WORLD', items=[
        ('WORLD', "World", "Center at world origin", 'MANIPUL', 0),
        ('ACTIVE_ELEMENT', "Active", "Center at active object", 'ROTACTIVE', 1),
        ('MEDIAN_POINT', "Average", "Center at the average position of exported objects", 'ROTATECENTER', 2),
        ('BOUNDING_BOX_CENTER', "Bounding box", "Center at the bounding box center of exported objects", 'ROTATE', 3),
        ('CURSOR', "Cursor", "Center at the 3D cursor", 'CURSOR', 4),
        ('INDIVIDUAL_ORIGINS', "Individual", "Center each exported object", 'ROTATECOLLECTION', 5),
    ])
    
    preserve_dupli_hierarchy = bpy.props.BoolProperty(name="Preserve dupli hierarchy", description="Preserve dupli hierarchy", default=True)
    use_convert_dupli = bpy.props.BoolProperty(name="Dupli->real", description="Make duplicates real", default=False)
    use_convert_mesh = bpy.props.BoolProperty(name="To meshes", description="Convert to mesh(es)", default=False)
    
    exporter_infos = {}
    exporter_items = [('BLEND', "Blend", "")] # has to be non-empty
    def get_exporter_items(self, context):
        exporter_infos = ExportSelected_Base.exporter_infos
        exporter_items = ExportSelected_Base.exporter_items
        
        if ExportSelected_Base.__lock: return exporter_items
        with ExportSelected_Base.__lock:
            exporter_infos.clear()
            exporter_items.clear()
            for idname, name, filename_ext, filter_glob in iter_exporter_info():
                exporter_infos[idname] = {"name":name, "ext":filename_ext, "glob":filter_glob, "index":len(exporter_items)}
                ExportSelected_Base.__add_item(exporter_items, idname, name, "Operator: "+idname)
            
            # If some exporter addon is enabled/disabled, the existing enum index must be updated
            if self.exporter_str in exporter_infos:
                if self.exporter_index != exporter_infos[self.exporter_str]["index"]:
                    self.exporter = self.exporter_str
            else:
                self.exporter = exporter_items[0][0]
        
        return exporter_items
    
    def update_exporter(self, context):
        exporter = self.exporter
        is_same = (exporter == self.exporter_str)
        
        self.exporter_str = exporter
        exporter_info = ExportSelected_Base.exporter_infos.get(self.exporter_str, {})
        self.exporter_index = exporter_info.get("index", -1)
        
        CurrentExporterProperties._load_props(self.exporter_str)
        self.filename_ext = exporter_info.get("ext", "")
        self.filter_glob = exporter_info.get("glob", "*")
        
        # Note: in file-browser mode it's impossible to alter the filepath after the invoke()
        self.filepath = replace_extension(self.filepath, self.filename_ext)
    
    exporter = bpy.props.EnumProperty(name="Exporter", description="Export format", items=get_exporter_items, update=update_exporter)
    exporter_str = bpy.props.StringProperty(default="", options={'HIDDEN'}) # an actual string value (enum is int)
    exporter_index = bpy.props.IntProperty(default=-1, options={'HIDDEN'}) # memorized index
    exporter_props = bpy.props.PointerProperty(type=CurrentExporterProperties)
    
    single_mesh_exporters = {
        "export_mesh.ply",
        "export_mesh.stl",
        "export_scene.autodesk_3ds",
    }
    
    def abspath(self, path):
        format = self.exporter_infos[self.exporter]["name"]
        return bpy.path.abspath(path.format(format=format))
    
    def generate_name(self, context=None):
        if not context: context = bpy.context
        file_dir = bpy_path_split(self.filepath)[0]
        objs = self.gather_objects(context.scene)
        roots = self.get_local_roots(objs)
        if len(roots) == 1:
            file_name = next(iter(roots)).name
        elif len(roots) == 0:
            file_name = ""
        else:
            file_name = bpy_path_basename(context.blend_data.filepath or "untitled")
            file_name = bpy_path_splitext(file_name)[0]
            if roots: file_name += "-"+hashnames(obj.name for obj in roots)
        if file_name:
            file_name = clean_filename(file_name) + self.filename_ext
        self.filepath = bpy_path_join(file_dir, file_name)
    
    def get_local_roots(self, objs):
        roots = set()
        for obj in objs:
            parents = set(obj_parents(obj))
            if parents.isdisjoint(objs): roots.add(obj)
        return roots
    
    def can_include(self, obj, scene):
        return (obj.type in self.object_types) and (self.include_invisible or obj.is_visible(scene))
    
    def gather_objects(self, scene):
        objs = set()
        
        def is_selected(obj):
            return obj.select and (not obj.hide) and (not obj.hide_select) and layers_intersect(obj, scene) and obj.is_visible(scene)
        
        def add_obj(obj):
            if obj in objs: return
            
            if self.can_include(obj, scene): objs.add(obj)
            
            if self.include_hierarchy in ('CHILDREN', 'HIERARCHY'):
                for child in obj.children:
                    add_obj(child)
        
        for obj in scene.objects:
            if (self.include_hierarchy != 'ALL') and (not is_selected(obj)): continue
            if self.include_hierarchy == 'HIERARCHY': obj = obj_root(obj)
            add_obj(obj)
        
        return objs
    
    _main_kwargs_ignore = {
        "filename_ext", "filter_glob", "exporter", "exporter_index", "exporter_props",
        "preset_select", "preset_name", "preset_save", "preset_delete",
    }
    _main_kwargs_ignore_presets = {
        "bundle_mode",
    }
    def main_kwargs(self, for_preset=False):
        kwargs = {}
        for key, value in iter_public_bpy_props(ExportSelected_Base): # NOT self.__class__
            if key in ExportSelected_Base._main_kwargs_ignore: continue
            if for_preset:
                if key in ExportSelected_Base._main_kwargs_ignore_presets: continue
            kwargs[key] = getattr(self, key)
        return kwargs
    
    def exporter_kwargs(self):
        kwargs = {key:getattr(self.exporter_props, key) for key in CurrentExporterProperties._keys()}
        kwargs["filepath"] = self.filepath
        return kwargs
    
    def draw(self, context):
        layout = self.layout
        
        if not CurrentExporterProperties._check(self.exporter_str): self.exporter = self.exporter_str
        
        row = layout.row(True)
        row.prop(self, "preset_select", text="", icon_only=True, icon='DOWNARROW_HLT')
        row.prop(self, "preset_name", text="")
        row.prop(self, "preset_save", text="", icon_only=True, icon=('FILE_TICK' if not self.preset_save else 'SAVE_AS'), toggle=True)
        row.prop(self, "preset_delete", text="", icon_only=True, icon=('X' if not self.preset_delete else 'PANEL_CLOSE'), toggle=True)
        
        row = layout.row(True)
        for obj_type in object_types:
            row.prop_enum(self, "object_types", obj_type, text="")
        
        row = layout.row(True)
        row.prop(self, "include_invisible", toggle=True, icon_only=True, icon='GHOST_ENABLED')
        row.prop(self, "include_hierarchy", text="")
        row.prop(self, "centering_mode", text="")
        
        row = layout.row(True)
        row.prop(self, "preserve_dupli_hierarchy", text="", icon='OOPS')
        row.prop(self, "use_convert_dupli", toggle=True)
        row.prop(self, "use_convert_mesh", toggle=True)
        
        box = layout.box()
        box.enabled = False
        
        self.exporter_props.layout = layout
        self.exporter_props.draw(context)
        
        if self.preset_save: self.preset_save = False
        if self.preset_delete: self.preset_delete = False

class ExportSelected(bpy.types.Operator, ExportSelected_Base):
    '''Export selected objects to a chosen format'''
    bl_idname = "export_scene.selected"
    bl_label = "Export Selected"
    bl_options = {'REGISTER'}
    
    use_file_browser = bpy.props.BoolProperty(name="Use file browser", description="Use file browser", default=True)
    
    def center_objects(self, scene, objs):
        if self.centering_mode == 'WORLD': return
        if not objs: return
        
        if self.centering_mode == 'INDIVIDUAL_ORIGINS':
            center_pos = None
        elif self.centering_mode == 'CURSOR':
            center_pos = Vector(scene.cursor_location)
        elif self.centering_mode == 'ACTIVE_ELEMENT':
            obj = scene.objects.active
            center_pos = (Vector(obj.matrix_world.translation) if obj else None)
        elif self.centering_mode == 'MEDIAN_POINT':
            center_pos = Vector()
            for obj in objs:
                center_pos += obj.matrix_world.translation
            center_pos *= (1.0 / len(objs))
        elif self.centering_mode == 'BOUNDING_BOX_CENTER':
            v_min, v_max = None, None
            for obj in objs:
                p = obj.matrix_world.translation
                if v_min is None:
                    v_min = (p[0], p[1], p[2])
                    v_max = (p[0], p[1], p[2])
                else:
                    v_min = (min(p[0], v_min[0]), min(p[1], v_min[1]), min(p[2], v_min[2]))
                    v_max = (max(p[0], v_max[0]), max(p[1], v_max[1]), max(p[2], v_max[2]))
            center_pos = (Vector(v_min) + Vector(v_max)) * 0.5
        
        roots = [obj for obj in objs if not obj.parent]
        for obj in roots:
            if center_pos is None:
                obj.matrix_world.translation = Vector()
            else:
                obj.matrix_world.translation -= center_pos
        
        scene.update() # required for children to actually update their matrices
        
        scene.cursor_location = Vector() # just to tidy up
    
    def convert_dupli(self, scene, objs):
        if not self.use_convert_dupli: return
        if not objs: return
        
        del_objs = {obj for obj in scene.objects if obj not in objs}
        
        if not self.preserve_dupli_hierarchy:
            for obj in scene.objects:
                obj.hide_select = False
                obj.select = obj in objs
            bpy.ops.object.duplicates_make_real(use_base_parent=False, use_hierarchy=False)
        else:
            for obj in objs:
                instantiate_duplis(obj, scene)
        
        for obj in scene.objects:
            if obj in del_objs: continue
            if self.can_include(obj, scene): objs.add(obj)
    
    def convert_mesh(self, scene, objs):
        if not self.use_convert_mesh: return
        if not objs: return
        
        for obj in scene.objects:
            obj.hide_select = False
            obj.select = obj in objs
        
        # For some reason object.convert() REQUIRES an active object to be present
        if scene.objects.active not in objs: scene.objects.active = next(iter(objs))
        
        bpy.ops.object.convert(target='MESH')
    
    def delete_other_objects(self, scene, objs):
        del_objs = {obj for obj in scene.objects if obj not in objs}
        
        for obj in del_objs:
            scene.objects.unlink(obj)
        
        # For non-.blend exporters, this is not necessary and may actually cause crashes
        if self.exporter == 'BLEND':
            while True:
                n = len(del_objs)
                for obj in tuple(del_objs):
                    try:
                        bpy.data.objects.remove(obj)
                        del_objs.discard(obj)
                    except RuntimeError: # non-zero users
                        pass
                if len(del_objs) == n: break
    
    def clear_world(self, context, objs):
        is_single_mesh = self.exporter in self.single_mesh_exporters
        self.use_convert_dupli |= is_single_mesh
        self.use_convert_mesh |= is_single_mesh
        
        for scene in bpy.data.scenes:
            if scene != context.scene:
                try:
                    bpy.data.scenes.remove(scene, do_unlink=True) # Blender 2.78
                except TypeError:
                    bpy.data.scenes.remove(scene) # earlier versions
        
        scene = context.scene
        
        self.center_objects(scene, objs)
        
        self.convert_dupli(scene, objs)
        
        self.convert_mesh(scene, objs)
        
        matrix_map = {obj:Matrix(obj.matrix_world) for obj in objs}
        
        self.delete_other_objects(scene, objs)
        
        for obj, matrix in matrix_map.items():
            obj.hide_select = False
            obj.select = True
            obj.matrix_world = matrix
        
        scene.update()
        
        if is_single_mesh: bpy.ops.object.join()
    
    def export(self, context):
        dirpath = self.abspath(bpy_path_split(self.filepath)[0])
        if not os.path.exists(dirpath): os.makedirs(dirpath)
        
        if self.exporter != 'BLEND':
            op = get_op(self.exporter)
            op(**self.exporter_kwargs())
            # NOTE: For some reason, Alembic prevents undoing the effects
            # of clear_world(), at least in Blender 2.78a.
            # The user can undo manually, but doing it from script appears impossible.
        else:
            if hasattr(bpy.data.libraries, "write"):
                # Hopefully this does not save unused libraries:
                refs = {context.scene} # {a, *b} syntax is only supported in recent Blender versions
                refs.update(context.scene.objects)
                bpy.data.libraries.write(self.filepath, refs)
            else:
                bpy.ops.wm.save_as_mainfile(filepath=self.filepath, copy=True) # fallback for earlier versions
    
    def export_bundle(self, context, filepath, bundle):
        self.filepath = filepath
        with ToggleObjectMode(undo=None):
            cursor_location = Vector(context.scene.cursor_location)
            bpy.ops.ed.undo_push(message="Delete unselected")
            self.clear_world(context, bundle)
            self.export(context)
            bpy.ops.ed.undo()
            bpy.ops.ed.undo_push(message="Export Selected")
            context.scene.cursor_location = cursor_location
    
    def get_bundle_keys_individual(self, obj):
        return {obj.name}
    def get_bundle_keys_root(self, obj):
        return {"Root="+obj_root(obj).name}
    def get_bundle_keys_group(self, obj):
        keys = {"Group="+group.name for group in bpy.data.groups if belongs_to_group(obj, group, True)}
        return (keys if keys else {"Group="})
    def get_bundle_keys_layer(self, obj):
        keys = {"Layer="+str(i) for i in range(len(obj.layers)) if obj.layers[i]}
        return (keys if keys else {"Layer="})
    def get_bundle_keys_material(self, obj):
        keys = {"Material="+slot.material.name for slot in obj.material_slots if slot.material}
        return (keys if keys else {"Material="})
    
    def resolve_key_conflicts(self, clean_keys):
        fixed_keys = {ck for k, ck in clean_keys.items() if k == ck}
        for k, ck in tuple((k, ck) for k, ck in clean_keys.items() if k != ck):
            ck0 = ck
            i = 1
            while ck in fixed_keys:
                ck = ck0 + "("+str(i)+")"
                i += 1
            fixed_keys.add(ck)
            clean_keys[k] = ck
    
    def bundle_objects(self, objs):
        basepath, ext = bpy_path_splitext(self.filepath)
        if self.bundle_mode == 'NONE':
            yield basepath+ext, objs
        else:
            keyfunc = getattr(self, "get_bundle_keys_"+self.bundle_mode.lower())
            clean_keys = {}
            bundles_dict = {}
            for obj in objs:
                for key in keyfunc(obj):
                    clean_keys[key] = clean_filename(key)
                    bundles_dict.setdefault(key, []).append(obj.name)
            self.resolve_key_conflicts(clean_keys)
            if bpy_path_basename(basepath): basepath += "-"
            for key, bundle in bundles_dict.items():
                # Due to Undo on export, object references will be invalid
                bundle = [bpy.data.objects[obj_name] for obj_name in bundle]
                yield basepath+clean_keys[key]+ext, bundle
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.objects) != 0
    
    def invoke(self, context, event):
        self.exporter = (self.exporter_str or self.exporter) # make sure properties are up-to-date
        if self.use_file_browser:
            self.filepath = context.blend_data.filepath or "untitled"
            self.generate_name(context)
            return ExportHelper.invoke(self, context, event)
        else:
            return self.execute(context)
    
    def execute(self, context):
        objs = self.gather_objects(context.scene)
        if not objs:
            self.report({'ERROR_INVALID_CONTEXT'}, "No objects to export")
            return {'CANCELLED'}
        self.filepath = self.abspath(self.filepath).replace("/", os.path.sep)
        for filepath, bundle in self.bundle_objects(objs):
            self.export_bundle(context, filepath, bundle)
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row(True)
        row.prop(self, "exporter", text="")
        row.prop(self, "bundle_mode", text="")
        
        ExportSelected_Base.draw(self, context)

class ExportSelectedPG(bpy.types.PropertyGroup, ExportSelected_Base):
    # "//" is relative to current .blend file
    filepath = bpy.props.StringProperty(default="//", subtype='FILE_PATH')
    
    def _get_filedir(self):
        return bpy_path_split(self.filepath)[0]
    def _set_filedir(self, value):
        self.filepath = bpy_path_join(value, bpy_path_split(self.filepath)[1])
    filedir = bpy.props.StringProperty(description="Export directory (red when does not exist)", get=_get_filedir, set=_set_filedir, subtype='DIR_PATH')
    
    def _get_filename(self):
        if self.auto_name: self.generate_name()
        return bpy_path_split(self.filepath)[1]
    def _set_filename(self, value):
        self.auto_name = False
        value = replace_extension(value, self.filename_ext)
        value = clean_filename(value)
        self.filepath = bpy_path_join(bpy_path_split(self.filepath)[0], value)
    filename = bpy.props.StringProperty(description="File name (red when already exists)", get=_get_filename, set=_set_filename, subtype='FILE_NAME')
    
    auto_name = bpy.props.BoolProperty(name="Auto name", description="Auto-generate file name", default=True)
    
    def draw_export(self, row):
        row2 = row.row(True)
        row2.enabled = bool(self.filename) or (self.bundle_mode != 'NONE')
        
        op_info = row2.operator(ExportSelected.bl_idname, text="Export", icon='EXPORT')
        op_info.use_file_browser = False
        
        for key, value in self.main_kwargs().items():
            setattr(op_info, key, value)
        
        for key, value in self.exporter_kwargs().items():
            setattr(op_info.exporter_props, key, value)
    
    def draw(self, context):
        layout = self.layout
        
        dir_exists = os.path.exists(self.abspath(self.filedir))
        file_exists = os.path.exists(self.abspath(self.filepath))
        
        column = layout.column(True)
        
        row = column.row(True)
        row.alert = not dir_exists
        row.prop(self, "filedir", text="")
        
        row = column.row(True)
        row2 = row.row(True)
        row2.alert = file_exists and (self.bundle_mode == 'NONE')
        row2.prop(self, "filename", text="")
        row.prop(self, "auto_name", text="", icon='SCENE_DATA', toggle=True)
        
        row = column.row(True)
        row2 = row.row(True)
        self.draw_export(row2)
        row2.prop(self, "exporter", text="")
        row2 = row.row(True)
        row2.alignment = 'RIGHT'
        row2.scale_x = 0.55
        row2.prop(self, "bundle_mode", text="", icon_only=True, expand=False)
        
        ExportSelected_Base.draw(self, context)

class ExportSelectedPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_export_selected"
    bl_label = "Export Selected"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Export"
    
    @classmethod
    def poll(cls, context):
        addon_prefs = context.user_preferences.addons[__name__].preferences
        if not addon_prefs: return False # can this happen?
        return addon_prefs.show_in_shelf
    
    def draw(self, context):
        layout = self.layout
        internal = get_internal_storage()
        internal.layout = layout
        internal.draw(context)

class OBJECT_MT_selected_export(bpy.types.Menu):
    bl_idname = "OBJECT_MT_selected_export"
    bl_label = "Selected"
    
    def draw(self, context):
        layout = self.layout
        for idname, name, filename_ext, filter_glob in iter_exporter_info():
            row = layout.row()
            if idname != 'BLEND': row.enabled = get_op(idname).poll()
            op_info = row.operator(ExportSelected.bl_idname, text=name)
            op_info.exporter_str = idname
            op_info.use_file_browser = True
    
    def menu(self, context):
        self.layout.menu("OBJECT_MT_selected_export", text="Selected")

class ExportSelectedPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__
    
    show_in_shelf = bpy.props.BoolProperty(name="Show in shelf", default=False)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_in_shelf")

storage_name_internal = "<%s-internal-storage>" % "io_export_selected"
def get_internal_storage():
    screens = bpy.data.screens
    screen = screens["Default" if ("Default" in screens) else 0]
    return getattr(screen, storage_name_internal)

def register():
    bpy.utils.register_class(CurrentExporterProperties)
    bpy.utils.register_class(ExportSelectedPreferences)
    bpy.utils.register_class(ExportSelectedPG)
    bpy.utils.register_class(ExportSelectedPanel)
    bpy.utils.register_class(ExportSelected)
    bpy.utils.register_class(OBJECT_MT_selected_export)
    bpy.types.INFO_MT_file_export.prepend(OBJECT_MT_selected_export.menu)
    setattr(bpy.types.Screen, storage_name_internal, bpy.props.PointerProperty(type=ExportSelectedPG, options={'HIDDEN'}))

def unregister():
    delattr(bpy.types.Screen, storage_name_internal)
    bpy.types.INFO_MT_file_export.remove(OBJECT_MT_selected_export.menu)
    bpy.utils.unregister_class(OBJECT_MT_selected_export)
    bpy.utils.unregister_class(ExportSelected)
    bpy.utils.unregister_class(ExportSelectedPanel)
    bpy.utils.unregister_class(ExportSelectedPG)
    bpy.utils.unregister_class(ExportSelectedPreferences)
    bpy.utils.unregister_class(CurrentExporterProperties)

if __name__ == "__main__":
    register()
