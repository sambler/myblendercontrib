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

# <pep8 compliant>


bl_info = {
    'name': "Theme manager",
    'author': "Bart Crouch",
    'version': (1, 4, 0),
    'blender': (2, 5, 9),
    'api': 39720,
    'location': "User Preferences > Themes > Header",
    'warning': "",
    'description': "Load or save a custom theme",
    'wiki_url': "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/System/Theme_manager",
    'tracker_url': "http://projects.blender.org/tracker/index.php?"\
        "func=detail&aid=26659",
    'category': 'System'}


import bpy
import gzip
from bpy_extras.io_utils import ExportHelper, ImportHelper
import os
import pickle
import shutil


# function to change the theme
def apply_theme(self, context):
    theme = context.window_manager.theme_list
    if theme == "internal_tm_42_default":
        bpy.ops.ui.reset_default_theme()
        print("Applied Default theme")
        return
    
    match = False
    for (sort_name, theme_name, author, version, filename) in \
    context.window_manager["theme_list_id"]:
        if theme_name == theme:
            match = True
            break
    if not match:
        # should be impossible
        print("Could not find theme(internal mismatch)")
        return
    else:
        filepath = filename
    
    # load file
    try:
        file = gzip.open(filepath, mode='r')
        dump = pickle.load(file)
        file.close()
        dump["info"]["script"]
    except:
        print("Could not read theme")
        return
    
    # apply theme
    theme = bpy.context.user_preferences.themes["Default"]
    for ts, props in dump["values"].items():
        theme_struct = getattr(theme, ts)
        for prop, val in props.items():
            if type(val) != type({}):
                setattr(theme_struct, prop, val)
            else:
                # one level deeper
                if type(prop) == type(1):
                    # collection property (bone color set)
                    prop_struct = theme_struct[prop]
                else:
                    prop_struct = getattr(theme_struct, prop)
                for subprop, subval in val.items():
                    setattr(prop_struct, subprop, subval)
    
    # restore default values for miscellaneous items, before assigning
    bpy.context.user_preferences.view.object_origin_size = 6
    bpy.context.user_preferences.view.mini_axis_size = 25
    bpy.context.user_preferences.view.mini_axis_brightness = 8
    bpy.context.user_preferences.view.manipulator_size = 15
    bpy.context.user_preferences.view.manipulator_handle_size = 25
    bpy.context.user_preferences.view.manipulator_hotspot = 14
    bpy.context.user_preferences.edit.sculpt_paint_overlay_color = \
        [0.0, 0.0, 0.0]
    bpy.context.user_preferences.system.dpi = 72
    bpy.context.user_preferences.system.use_weight_color_range = False
    color_range = bpy.context.user_preferences.system.weight_color_range
    color_range.interpolation = 'LINEAR'
    while len(color_range.elements) > 1:
        color_range.elements.remove(color_range.elements[0])
    if len(color_range.elements) == 1:
        color_range.elements[0].position = 1.0
        color_range.elements[0].color = [0.0, 1.0, 0.0, 0.0]
    lights = bpy.context.user_preferences.system.solid_lights
    light_settings = [{"diffuse_color":[0.8, 0.8, 0.8],
        "direction":[-0.892, 0.3, 0.9], "specular_color":[0.5, 0.5, 0.5],
        "use":True}, {"diffuse_color":[0.498, 0.5, 0.6], 
        "direction":[0.588, 0.460, 0.248],
        "specular_color":[0.2, 0.2, 0.2], "use":True},
        {"diffuse_color":[0.798, 0.838, 1.0],
        "direction":[0.216, -0.392, -0.216],
        "specular_color":[0.066, 0.0, 0.0], "use":True}]
    for i, light in enumerate(lights):
        settings = light_settings[i]
        for prop, value in settings.items():
            setattr(light, prop, value)
    
    # theme file created with script version >= 1.3
    if "misc" in dump:
        for category, props in dump["misc"].items():
            category_struct = getattr(bpy.context.user_preferences,
                category)
            for prop_name, val in props.items():
                if type(val) != type({}):
                    # simple miscellaneous setting
                    setattr(category_struct, prop_name, val)
                else:
                    structs = getattr(category_struct, prop_name)
                    for subkey, subval in val.items():
                        if type(subkey) == type(1):
                            # solid_lights
                            struct = structs[subkey]
                            for subprop_name, subprop_val in \
                            subval.items():
                                setattr(struct, subprop_name, subprop_val)
                        else:
                            # weight paint color-range
                            if type(subval) != type({}):
                                setattr(structs, subkey, subval)
                            else:
                                elements = getattr(structs, subkey)
                                add_new = len(subval) - len(elements)
                                for i in range(add_new):
                                    elements.new(i / len(subval))
                                for i, element_prop in subval.items():
                                    for element_key, element_value in \
                                    element_prop.items():
                                        setattr(elements[i], element_key,
                                            element_value)
    
    # report to user
    author = dump["info"]["author"]
    theme_name = dump["info"]["theme_name"]
    print("Applied " + theme_name + " by " + author)


# create list for dynamic EnumProperty
def dynamic_list(self, context):
    d_list = [('internal_tm_42_default', "Default", "Reset to the "\
        "default theme colors")]
    if "theme_list_id" in context.window_manager:
        for i, theme, author, version, path in \
        context.window_manager["theme_list_id"]:
            if version:
                version = " " + version
            d_list.append((theme, theme + version + " by " + author,
                "Apply " + theme + version))
    
    return(d_list)


# return path of the folder where all themes are located
def get_paths():
    # locate theme preset folder
    paths = bpy.utils.preset_paths("theme")
    if not paths:
        # theme preset folder doesn't exist, so create it
        paths = [os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets",
            "theme")]
        if not os.path.exists(paths[0]):
            os.makedirs(paths[0])
    
    return(paths)


# create list of all themes available
def load_presets():
    # find theme files
    paths = get_paths()
    theme_files = []
    for path in paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".blt"):
                    theme_files.append(os.path.join(root, file))
    
    # read author and theme names
    theme_list = []
    for filename in theme_files:
        # load file
        try:
            file = gzip.open(filename, mode='r')
            dump = pickle.load(file)
            file.close()
            author = dump["info"]["author"]
            theme_name = dump["info"]["theme_name"]
            sort_name = theme_name.lower()
            # theme_version available if created with script version >= 1.4
            theme_version = dump["info"].get("theme_version", "")
            theme_list.append([sort_name, theme_name, author, theme_version,
                filename])
        except:
            continue
    theme_list.sort()
    
    # store list in window-manager
    bpy.context.window_manager["theme_list_id"] = theme_list
    try:
        # check if EnumProp exists: overwrite might cause memory corruption
        bpy.context.window_manager.theme_list
    except:
        # create EnumProp, because it doesn't exist yet
        bpy.types.WindowManager.theme_list = bpy.props.EnumProperty(\
            name="Load Theme",
            items=dynamic_list,
            description="Load a theme",
            update=apply_theme)


def unload_presets():
    # remove settings from window-manager
    del bpy.context.window_manager["theme_list_id"]
    try:
        del bpy.types.WindowManager.theme_list
        print('successfully removed theme_list enum property')
    except:
        pass


# install operator
class InstallTheme(bpy.types.Operator, ImportHelper):
    bl_idname = "ui.install_theme"
    bl_label = "Install new theme"
    bl_description = "Install a new theme"
    
    filename_ext = ".blt"
    filter_glob = bpy.props.StringProperty(default="*.blt", options={'HIDDEN'})
    
    def execute(self, context):
        # copy theme to presets folder
        filename = os.path.basename(self.filepath)
        try:
            shutil.copyfile(self.filepath,
                os.path.join(get_paths()[0], filename))
        except:
            self.report({'ERROR'}, "Installing failed")
            return{'CANCELLED'}
        
        # reload presets list
        load_presets()
        
        # change active theme
        try:
            file = gzip.open(self.filepath, mode='r')
            dump = pickle.load(file)
            file.close()
            theme = dump["info"]["theme_name"]
        except:
            self.report({"ERROR"}, "Installing succeeded, but could not read "\
                "theme")
            return{'CANCELLED'}
        context.window_manager.theme_list = theme
        
        return{'FINISHED'}


# save operator
class SaveTheme(bpy.types.Operator, ExportHelper):
    bl_idname = "ui.save_theme"
    bl_label = "Save Theme"
    bl_description = "Save the current theme to a .blt file"
    
    filename_ext = ".blt"
    filepath = bpy.props.StringProperty(\
        default=os.path.join(get_paths()[0], "untitled"))
    filter_glob = bpy.props.StringProperty(default="*.blt", options={'HIDDEN'})
    author = bpy.props.StringProperty(name="Author",
        default=bpy.context.user_preferences.system.author,
        description="Name of the person who created the theme")
    theme_name = bpy.props.StringProperty(name="Theme name",
        default="",
        description="Name of the theme")
    version = bpy.props.StringProperty(name="Version",
        default="",
        description="Version number of the theme, eg: 1.0",
        maxlen=8)
    
    def execute(self, context):
        # create dictionary with all information
        dump = {"info":{}, "misc":{}, "values":{}}
        dump["info"]["script"] = bl_info['name']
        dump["info"]["script_version"] = bl_info['version']
        dump["info"]["version"] = bpy.app.version
        dump["info"]["build_revision"] = bpy.app.build_revision
        dump["info"]["author"] = self.author
        dump["info"]["theme_name"] = self.theme_name
        dump["info"]["theme_version"] = self.version
        
        # defaults
        if not self.author:
            dump["info"]["author"] = "Unknown"
        if not self.theme_name:
            dump["info"]["theme_name"] = "Custom theme"
        
        # get current theme settings
        theme = bpy.context.user_preferences.themes["Default"]
        theme_structs = [[ts.lower(), getattr(theme, ts.lower())] for ts in \
            bpy.types.Theme.bl_rna.properties['theme_area'].enum_items.keys()]
        for name, ts in theme_structs:
            dump["values"][name] = {}
            if str(type(ts)) == "<class 'bpy_prop_collection'>":
                # bone color sets
                for i, struct in enumerate(ts):
                    dump["values"][name][i] = {}
                    for prop in struct.bl_rna.properties:
                        if prop.identifier == "rna_type":
                            # not a setting, so skip
                            continue
                        val = getattr(ts[i], prop.identifier)
                        if str(type(val)) in ["<class 'bpy_prop_array'>",
                        "<class 'mathutils.Color'>"]:
                            # array
                            dump["values"][name][i][prop.identifier] = [v \
                                for v in val]
                        else:
                            # single value
                            dump["values"][name][i][prop.identifier] = val    
                continue
            for prop in ts.bl_rna.properties:
                if prop.identifier == "rna_type":
                    # not a setting, so skip
                    continue
                val = getattr(ts, prop.identifier)
                if prop.type != 'POINTER':
                    if str(type(val)) in ["<class 'bpy_prop_array'>",
                        "<class 'mathutils.Color'>"]:
                        # array
                        dump["values"][name][prop.identifier] = [v for v in \
                            val]
                    else:
                        # single value
                        dump["values"][name][prop.identifier] = val
                else:
                    # one level deeper
                    dump["values"][name][prop.identifier] = {}
                    for subprop in val.bl_rna.properties:
                        if subprop.identifier == "rna_type":
                            # not a setting, so skip
                            continue
                        subval = getattr(val, subprop.identifier)
                        if subprop.type != 'POINTER':
                            if str(type(subval)) in [\
                            "<class 'bpy_prop_array'>",
                            "<class 'mathutils.Color'>"]:
                                # array
                                dump["values"][name][prop.identifier]\
                                    [subprop.identifier] = [v for v in subval]
                            else:
                                # single value
                                dump["values"][name][prop.identifier]\
                                    [subprop.identifier] = subval
        
        # get simple settings which are spread out over various sections
        save_props = ["view.object_origin_size", "view.mini_axis_size",
            "view.mini_axis_brightness", "view.manipulator_size",
            "view.manipulator_handle_size", "view.manipulator_hotspot",
            "edit.sculpt_paint_overlay_color", "system.dpi",
            "system.use_weight_color_range"]
        for property in save_props:
            category, prop_name = property.split(".", 1)
            if not dump["misc"].get(category, False):
                dump["misc"][category] = {}
            prop = getattr(getattr(bpy.context.user_preferences, category),
                prop_name)
            if str(type(prop)) in ["<class 'bpy_prop_array'>",
            "<class 'mathutils.Color'>"]:
                prop = [val for val in prop]
            dump["misc"][category][prop_name] = prop
        
        # solid_light settings
        dump["misc"]["system"]["solid_lights"] = {}
        for i, light in enumerate(bpy.context.user_preferences.system.
        solid_lights):
            dump["misc"]["system"]["solid_lights"][i] = {}
            save_props = ["diffuse_color", "direction", "specular_color",
                "use"]
            for property in save_props:
                prop = getattr(bpy.context.user_preferences.system.\
                    solid_lights[i], property)
                if str(type(prop)) in ["<class 'bpy_prop_array'>",
                "<class 'mathutils.Color'>", "<class 'mathutils.Vector'>"]:
                    prop = [val for val in prop]
                dump["misc"]["system"]["solid_lights"][i][property] = prop
        
        # weight paint color-range settings
        dump["misc"]["system"]["weight_color_range"] = {}
        dump["misc"]["system"]["weight_color_range"]["interpolation"] = bpy.\
            context.user_preferences.system.weight_color_range.interpolation
        dump["misc"]["system"]["weight_color_range"]["elements"] = {}
        for i, element in enumerate(context.user_preferences.system.\
        weight_color_range.elements):
            dump["misc"]["system"]["weight_color_range"]["elements"][i] = {}
            dump["misc"]["system"]["weight_color_range"]["elements"][i]\
                ["position"] = bpy.context.user_preferences.system.\
                weight_color_range.elements[i].position
            dump["misc"]["system"]["weight_color_range"]["elements"][i]\
                ["color"] = [c for c in bpy.context.user_preferences.system.\
                weight_color_range.elements[i].color]
        
        # save to file
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)
        file = gzip.open(filepath, mode='w')
        pickle.dump(dump, file)
        file.close()
        load_presets()
        context.window_manager.theme_list = dump["info"]["theme_name"]
        
        return{'FINISHED'}


# uninstall operator
class UninstallTheme(bpy.types.Operator):
    bl_idname = "ui.uninstall_theme"
    bl_label = "Uninstall theme"
    bl_description = "Uninstall this theme preset"
    
    def execute(self, context):
        theme = context.window_manager.theme_list
        match = False
        for (sort_name, theme_name, author, version, filename) in \
        context.window_manager["theme_list_id"]:
            if theme_name == theme:
                match = True
                break
        if not match:
            # should be impossible
            self.report({'ERROR'}, "Could not remove theme preset (internal "\
                "mismatch)")
            return{'CANCELLED'}
        else:
            filepath = filename
        
        try:
            os.remove(filepath)
        except:
            self.report({'ERROR'}, "Could not remove theme preset")
            return{'CANCELLED'}
        
        # reload presets list and reset to default
        load_presets()
        bpy.ops.ui.reset_default_theme()
        context.window_manager.theme_list = 'internal_tm_42_default'
        
        return{'FINISHED'}


# draw function for integration in header
def header_func(self, context):
    if context.user_preferences.active_section == 'THEMES':
        self.layout.separator()
        row = self.layout.row(align=True)
        row.prop(context.window_manager, "theme_list", text="")
        row.operator("ui.install_theme", icon='ZOOMIN', text="")
        row = row.row()
        row.enabled = context.window_manager.theme_list != \
            'internal_tm_42_default'
        row.operator("ui.uninstall_theme", icon='X', text="")
        self.layout.operator("ui.save_theme")


classes = [InstallTheme,
    SaveTheme,
    UninstallTheme]


def register():
    load_presets()
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.USERPREF_HT_header.append(header_func)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.USERPREF_HT_header.remove(header_func)
    unload_presets()


if __name__ == "__main__":
    register()
