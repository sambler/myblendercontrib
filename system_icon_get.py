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


bl_addon_info = {
    'name': 'Icons',
    'author': 'Crouch, N.tox, PKHG',
    'version': (1, 3, 1),
    'blender': (2, 5, 5),
    'api': 32738,
    'location': 'Properties window > Object tab',
    'warning': '',
    'description': 'Creates a panel displaying all icons and their names.',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'System'}


import bpy
import urllib.request

class WM_OT_icon_info(bpy.types.Operator):
    bl_label = "Icon Info"
    icon = bpy.props.StringProperty()

    def invoke(self, context, event):
        self.report({'INFO'}, "Icon ID: '%s'" % self.icon)
        return {'FINISHED'}


class OBJECT_PT_icons(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "All icons"

    @staticmethod
    def _icon_list():
        return sorted(bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].items.keys())

    def draw(self, context):
        amount = 10
        cols = []
        layout = self.layout
        split = layout.split(percentage=1.0 / amount)

        for i, icon in enumerate(self._icon_list()):
            if i < amount:
                cols.append(split.column())

            col = cols[i % amount].row()
            col.operator("wm.icon_info", text="", icon=icon).icon = icon


def register():
    pass

def unregister():
    pass
