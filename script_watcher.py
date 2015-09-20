"""
script_watcher.py: Reload watched script upon changes.

Copyright (C) 2015 Isaac Weaver
Author: Isaac Weaver <wisaac407@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

bl_info = {
    "name": "Script Watcher",
    "author": "Isaac Weaver",
    "version": (0, 3),
    "blender": (2, 75, 0),
    "location": "Properties > Scene > Script Watcher",
    "description": "Reloads an external script on edits.",
    "warning": "Still in beta stage.",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Development/Script_Watcher",
    "tracker_url": "https://github.com/wisaac407/blender-script-watcher/issues/new",
    "category": "Development",
}

import os, sys
import io
import traceback
import bpy

def add_scrollback(ctx, text, text_type):
    for l in text.split("\n"):
        bpy.ops.console.scrollback_append(ctx, text=l.replace("\t", "    "),
                                          type=text_type)

# Define the script watching operator.
class WatchScriptOperator(bpy.types.Operator):
    """Polls the script being watched. If any changes occur re-runs script."""
    bl_idname = "wm.sw_watch_start"
    bl_label = "Watch Script"

    _timer = None
    _running = False
    _times = None
    filepath = None
    
    sys_paths = None # List of sys paths for current script.
    
    def get_paths(self, filepath):
        """Find all the python paths surrounding the given filepath."""
        
        dirname = os.path.dirname(filepath)
        
        paths = []
        filepaths = []
        
        for root, dirs, files in os.walk(dirname, topdown=True):
            if '__init__.py' in files:
                paths.append(root)
                for f in files:
                    filepaths.append(os.path.join(root, f))
            else:
                dirs[:] = [] # No __init__ so we stop walking this dir.
        
        return paths, filepaths or [filepath] # If we just have one (non __init__) file then that will be the file we watch.
    
    def remove_cached_mods(self, paths):
        """Remove any cached modules that where imported in the last excecution."""
        for name, mod in list(sys.modules.items()):
            # If the module is not internal and it came from a script path then it should be reloaded.
            if hasattr(mod, '__file__') and os.path.dirname(mod.__file__) in paths:
                del sys.modules[name]
    
    def get_globals(self):
        # Grab globals from the main module and override the key values.
        globs = sys.modules['__main__'].__dict__.copy()
        globs['__file__'] = self.filepath
        
        return globs

    def reload_script(self, filepath):
        print('Reloading script:', filepath)
        try:
            f = open(filepath)
            paths, files = self.get_paths(filepath)
            # Make sure that the script is in the sys path.
            for path in paths:
                self.sys_paths.add(path) # Keep track of all our sys paths.                
                if path not in sys.path:
                    sys.path.append(path)

            self.remove_cached_mods(paths)
            exec(compile(f.read(), filepath, 'exec'), self.get_globals())
        except IOError:
            print('Could not open script file.')
        except:
            sys.stderr.write("There was an error when running the script:\n" + traceback.format_exc())
        else:
            f.close()
            
    def reload_with_py(self, context, filepath):
        """Reload this script while printing the output to blenders python console."""
        
        # Setup stdout and stderr.
        stdout = io.StringIO()
        stderr = io.StringIO()
        
        sys.stdout = stdout
        sys.stderr = stderr
        
        # Run the script.
        self.reload_script(filepath)
        
        # Store the output in variables.
        stdout.seek(0)
        stderr.seek(0)
        
        output = stdout.read()
        output_err = stderr.read()
        
        # Print the output to the consoles.
        for area in context.screen.areas:
            if area.spaces.active.type == "CONSOLE":
                ctx = context.copy()
                ctx.update({"area": area})
                
                # Actually print the output.
                if output:
                    add_scrollback(ctx, output, 'OUTPUT')
                    
                if output_err:
                    add_scrollback(ctx, output_err, 'ERROR')
        
        # Cleanup
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        # Lastly, feed the output to the actual sys.stdout and sys.stderr.
        sys.stdout.write(output)
        sys.stderr.write(output_err)
        

    def modal(self, context, event):
        if not context.scene.sw_settings.running:
            self.cancel(context)
            return {'CANCELLED'}
        if event.type == 'TIMER':
            for path in self._times:
                cur_time = os.stat(path).st_mtime
                
                if cur_time != self._times[path]:
                    self._times[path] = cur_time
                    
                    if self.use_py_console:
                        self.reload_with_py(context, self.filepath)
                    else:
                        self.reload_script(self.filepath)

        return {'PASS_THROUGH'}

    def execute(self, context):
        if context.scene.sw_settings.running:
            return {'CANCELLED'}
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        
        self.filepath = bpy.path.abspath(context.scene.sw_settings.filepath)
        self.use_py_console = context.scene.sw_settings.use_py_console
        
        files, dirs = self.get_paths(self.filepath)
        self._times = dict((path, os.stat(path).st_mtime) for path in files) # Where we store the times of all the paths.
        self._times[files[0]] = 0  # We set one of the times to 0 so the script will be loaded on startup.
        
        self.sys_paths = set()
        
        context.scene.sw_settings.running = True
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        
        # Remove all the paths form the watched script.
        for path in self.sys_paths:
            sys.path.remove(path)

        context.scene.sw_settings.running = False


class CancelScriptWatcher(bpy.types.Operator):
    """Sets a flag which tells the modal to cancel itself."""
    bl_idname = "wm.sw_watch_end"
    bl_label = "Stop Watching"

    def execute(self, context):
        # Setting the running flag to false will cause the modal to cancel itself.
        context.scene.sw_settings.running = False
        return {'FINISHED'}


# Create the UI for the operator. NEEDS FINISHING!!
class ScriptWatcherPanel(bpy.types.Panel):
    """UI for the script watcher."""
    bl_label = "Script Watcher"
    bl_idname = "SCENE_PT_script_watcher"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        running = context.scene.sw_settings.running

        col = layout.column()
        col.prop(context.scene.sw_settings, 'filepath')
        col.prop(context.scene.sw_settings, 'use_py_console')
        col.operator('wm.sw_watch_start', icon='VISIBLE_IPO_ON')
        col.enabled = not running
        if running:
            layout.operator('wm.sw_watch_end', icon='CANCEL')


class ScriptWatcherSettings(bpy.types.PropertyGroup):
    """All the script watcher settings."""
    running = bpy.props.BoolProperty(default=False)
    
    filepath = bpy.props.StringProperty(
        name        = 'Script',
        description = 'Script file to watch for changes.',
        subtype     = 'FILE_PATH'
    )
    
    use_py_console = bpy.props.BoolProperty(
        name        = 'Use py console',
        description = 'Use blenders built-in python console for program output (i.e. print statments and error messages)',
        default     = False
    )


def register():
    bpy.utils.register_class(WatchScriptOperator)
    bpy.utils.register_class(ScriptWatcherPanel)
    bpy.utils.register_class(CancelScriptWatcher)
    bpy.utils.register_class(ScriptWatcherSettings)
    
    bpy.types.Scene.sw_settings = \
        bpy.props.PointerProperty(type=ScriptWatcherSettings)


def unregister():
    bpy.utils.unregister_class(WatchScriptOperator)
    bpy.utils.unregister_class(ScriptWatcherPanel)
    bpy.utils.unregister_class(CancelScriptWatcher)

    del bpy.types.Scene.sw_settings


if __name__ == "__main__":
    register()
