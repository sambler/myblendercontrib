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

# <pep8-80 compliant>

bl_addon_info = {
    'name': 'Batch Name Edit',
    'author': 'Richard Olsson',
    'version': (0,1),
    'blender': (2, 5, 3),
    'api': 31667,
    'location': 'ToolShelf Search',
    'warning': 'not compatible with last api, can crash blender',
    'description': 'Edit selected objects names (search: rename)',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/' \
        'Scripts/Object/Batch_Name_Edit',
    'tracker_url': 'https://projects.blender.org/tracker/index.php?'\
        'func=detail&aid=21681&group_id=153&atid=468',
    'category': 'Object'}



import re
import fnmatch

import bpy
from bpy.props import *


# Base class used for all batch name edit operators,
# since they share the same conditions for enabling
# and invoke mechanism (open property popup)
class BatchNameEdit:
    dialog_width = 250

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_props_dialog(self, self.dialog_width)
        return {'RUNNING_MODAL'}


    def _plural(n, singular, plural=None):
        if n==1:
            return singular
        else:
            if plural is None:
                plural = '%ss' % singular
            return plural


class BatchNameEditNewName(bpy.types.Operator, BatchNameEdit):
    '''Give all selected objects a common name'''
    bl_idname = "object.batch_name_edit_newname"
    bl_label = "Rename selected"
    bl_options = {'REGISTER', 'UNDO'}

    new_name = StringProperty(name="New name", 
        description="Selected object(s) will be given this name, " +
            "with a sequential numeric suffix when necessary")

    def execute(self, context):
        if self.properties.new_name:
            for o in context.selected_objects:
                o.name = self.properties.new_name

            count = len(context.selected_objects)
            self.report({'OPERATOR'}, 'Renamed %d selected %s' %
                (count, self._plural(count, 'object')))

            return {'FINISHED'}

        else:
            return {'PASS_THROUGH'}

    def draw(self, context):
        layout = self.layout
        props = self.properties

        layout.prop(props, "new_name")
    

class BatchNameEditReplace(bpy.types.Operator, BatchNameEdit):
    '''Replaces occurrences of a given string in object names'''
    bl_idname = "object.batch_name_edit_replace"
    bl_label = "Replace pattern"
    bl_options = {'REGISTER', 'UNDO'}

    pattern = StringProperty(name="Match pattern", 
        description="Search for this pattern in object names. " +
            "Supports Regular Expressions or UNIX shell wildcards.")

    replacement = StringProperty(name="Replace with", 
        description="Replace occurrances of pattern with this string")

    use_regex = BoolProperty(name="Use Regular Expressions", 
        description="Should Regular Expressions be used for pattern matching?")

    def execute(self, context):
        props = self.properties

        if props.pattern and props.replacement:
            # Retrieve pattern, and translate to regex unless
            # it's already a regex (according to user)
            if props.use_regex:
                p = props.pattern
            else:
                # Get rid of trailing $
                p = fnmatch.translate(props.pattern)[0:-1]

            num_renamed = 0
            reobj = re.compile(p)
            for o in context.selected_objects:
                old_name = o.name
                o.name = re.sub(reobj, props.replacement, old_name)
                if o.name != old_name:
                    num_renamed += 1

            num_sel = len(context.selected_objects)
            self.report({'OPERATOR'}, 'Renamed %d of %d selected %s.' % 
                (num_renamed, num_sel, self._plural(num_sel, 'object')))

            return {'FINISHED'}
        else:
            return {'PASS_THROUGH'}

    def draw(self, context):
        layout = self.layout
        props = self.properties

        layout.prop(props, "pattern")
        layout.prop(props, "use_regex")
        layout.prop(props, "replacement")
        

class BatchNameEditAdd(bpy.types.Operator, BatchNameEdit):
    '''Appends and/or prepends text to object names'''
    bl_idname = "object.batch_name_edit_add"
    bl_label = "Append or prepend string"
    bl_options = {'REGISTER', 'UNDO'}

    dialog_width = 150

    prefix = StringProperty(name="Prefix", 
        description="String of text to add to beginning of object name")
    suffix = StringProperty(name="Suffix", 
        description="String of text to add to end of object name")

    def execute(self, context):
        props = self.properties
        if props.prefix or props.suffix:
            for o in context.selected_objects:
                o.name = ''.join([props.prefix, o.name, props.suffix])

            num_selected = len(context.selected_objects)
            self.report({'OPERATOR'}, 'Renamed %d selected %s' %
                (num_selected, self._plural(num_selected, 'object')))

            return {'FINISHED'}
        else:
            return {'PASS_THROUGH'}

    def draw(self, context):
        layout = self.layout
        props = self.properties

        layout.prop(props, "prefix")
        layout.prop(props, "suffix")


class BatchNameEditTruncate(bpy.types.Operator, BatchNameEdit):
    '''Removes a number of characters from start and/or end of object names'''
    bl_idname = "object.batch_name_edit_truncate"
    bl_label = "Truncate"
    bl_options = {'REGISTER', 'UNDO'}
    
    dialog_width = 120

    trunc_start = IntProperty(name="Truncate start", min=0, 
        description="Number of characters to remove from start of object name")
    trunc_end = IntProperty(name="Truncate end", min=0, 
        description="Number of characters to remove from end of object name")

    def execute(self, context):
        props = self.properties

        print("executing trunc")

        if props.trunc_start or props.trunc_end:
            num_renamed = 0
            num_skipped = 0
            for o in context.selected_objects:
                s_idx = props.trunc_start
                e_idx = len(o.name)-props.trunc_end
                if s_idx < e_idx:
                    o.name = o.name[s_idx : e_idx]
                    num_renamed += 1
                else:
                    num_skipped += 1

            report = 'Renamed %d selected %s' % (num_renamed, 
                self._plural(num_renamed, 'object'))

            if num_skipped > 0:
                report = ' '.join([report, 'and skipped %d (name too short)' %
                    num_skipped])

            self.report({'OPERATOR'}, report)

            return {'FINISHED'}
        else:
            return {'PASS_THROUGH'}

    def draw(self, context):
        layout = self.layout
        props = self.properties

        layout.prop(props, "trunc_start")
        layout.prop(props, "trunc_end")


class BatchNameEditTransfer(bpy.types.Operator, BatchNameEdit):
    '''Give all selected objects a common name'''
    bl_idname = "object.batch_name_edit_transfer"
    bl_label = "Copy to/from data block"
    bl_options = {'REGISTER', 'UNDO'}

    dirs = [("DIR_O2D", "Rename data as object", ""),
        ("DIR_D2O", "Rename object as data", ""),
        ("DIR_O2G", "Rename DupGroup as object", ""),
        ("DIR_G2O", "Rename object as DupGroup", "")]
    direction = EnumProperty(items=dirs, name="Direction", 
        description="The direction in which names should be transferred")

    def execute(self, context):
        props = self.properties
        
        def trans_o2d(obj):
            obj.data.name = obj.name
        def trans_d2o(obj):
            obj.name = obj.data.name
        def trans_o2g(obj):
            obj.dupli_group.name = obj.name
        def trans_g2o(obj):
            obj.name = obj.dupli_group.name

        func = {
            'DIR_O2D': trans_o2d,
            'DIR_D2O': trans_d2o,
            'DIR_O2G': trans_o2g,
            'DIR_G2O': trans_g2o
        }[props.direction]

        num_renamed = 0

        for o in context.selected_objects:
            try:
                func(o)
                num_renamed += 1
            except Exception:
                pass  # No renaming occurred

        self.report({'OPERATOR'}, 'Transferred names for %d selected %s.' % 
            (num_renamed, self._plural(num_renamed, 'object')))

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        props = self.properties

        layout.prop(props, "direction")


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
