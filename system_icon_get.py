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
    'author': 'Crouch, N.tox, PKHG, Campbell Barton, Dany Lebel',
    'version': (1, 4, 0),
    'blender': (2, 5, 6),
    'api': 33479,
    'location': 'Text window > Properties panel (ctrl+F)',
    'warning': '',
    'description': 'Click an icon to display its name and copy it '\
        'to the clipboard',
    'wiki_url': '',
    'tracker_url': 'http://projects.blender.org/tracker/index.php?'\
        'func=detail&aid=22011&group_id=153&atid=468',
    'category': 'System'}


import bpy


class IconProps(bpy.types.IDPropertyGroup):
    """
    Fake module like class
    bpy.context.scene.icon_props
    """
    pass


class WM_OT_icon_info(bpy.types.Operator):
    bl_label = "Icon Info"
    icon = bpy.props.StringProperty()
    icon_scroll = bpy.props.IntProperty()
    
    def invoke(self, context, event):
        bpy.data.window_managers['WinMan'].clipboard = self.icon
        self.report({'INFO'}, "Icon ID: %s" % self.icon)
        return {'FINISHED'}


class OBJECT_PT_icons(bpy.types.Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "All icons"
    
    @staticmethod
    def _icon_list():
        list = sorted(bpy.types.UILayout.bl_rna.functions['prop'].\
            parameters['icon'].items.keys())
        list.remove("BLENDER") # hack for icon that messes up layout
        return list
    
    @staticmethod
    def _amount():
        return 10
    
    def draw(self, context):
        split = self.layout.split(percentage=0.05)
        
        # scroll view
        if not context.scene.icon_props.expand:
            split.prop(context.scene.icon_props, "expand",
                icon="TRIA_RIGHT", icon_only=True, emboss=False)
            split.prop(context.scene.icon_props, "scroll", slider=True)
            
            row = self.layout.row(align=True)
            for icon in self._icon_list()[context.scene.icon_props.scroll-1:
            context.scene.icon_props.scroll-1+self._amount()]:
                row.operator("wm.icon_info", text="", icon=icon).icon = icon
        
        # expanded view
        else:
            split.prop(context.scene.icon_props, "expand",
                icon="TRIA_DOWN", icon_only=True, emboss=False)
            row = split.row()
            row.active = False
            row.prop(context.scene.icon_props, "scroll", slider=True)
            
            col = self.layout.column(align=True)
            for i, icon in enumerate(self._icon_list()):
                if i % self._amount() == 0:
                    row = col.row(align=True)
                row.operator("wm.icon_info", text="", icon=icon).icon = icon


def register():
    icons_total = len(bpy.types.OBJECT_PT_icons._icon_list())
    icons_per_row = bpy.types.OBJECT_PT_icons._amount()
    
    bpy.types.Scene.icon_props = bpy.props.PointerProperty(type = IconProps)
    IconProps.scroll = bpy.props.IntProperty(default=1, min=1,
        max=icons_total - icons_per_row + 1,
        description="Drag to scroll icons")
    IconProps.expand = bpy.props.BoolProperty(default=False,
        description="Expand, to display all icons at once")


def unregister():
    if bpy.context.scene.get('icon_props') != None:
        del bpy.context.scene['icon_props']
    try:
        del bpy.types.Scene.icon_props
    except:
        pass


if __name__ == "__main__":
    register()
