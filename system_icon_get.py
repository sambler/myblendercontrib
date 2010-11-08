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


# create list with all icon names
def createIcons():
    # retrieving the masterlist with all icon names
    try:
        file = urllib.request.urlopen('https://svn.blender.org/svnroot/'\
        'bf-blender/trunk/blender/source/blender/editors/include/UI_icons.h')
    except:
        print("Couldn't find the urllib module or was unable to connect to"\
        " the internet")
        file = ''
    # get the icon names of existing non-blank icons
    icons = [str(l)[11:(-4 if l[-2]==b')' else (l.index(b')')+2))] for l in \
        file if ( (l[:9]==b'DEF_ICON(') and (l[9:19]!=b'ICON_BLANK') )]
    icons.sort()
    return icons


# create custom operator for each icon
def createOperators(icons):
    for i in icons:
        class custom_op(bpy.types.Operator):
            bl_idname = "ICONDISPLAY_OT_"+i
            bl_label = "ICONDISPLAY_OT_"+i
            bl_description = i
        
            def invoke(self, context, event):
                print(self.bl_description)
                return {'FINISHED'}


# main function that calls subroutines
def main():
    icons = createIcons()
    createOperators(icons)


# draw the panel with the icons
class OBJECT_PT_icons(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "All icons"
    
    icons = createIcons()
    
    def draw(self, context):
        amount = 10
        cols = []
        layout = self.layout
        split = layout.split(percentage=1.0/amount)
        for i,icon in enumerate(self.icons):
            if i<amount: cols.append(split.column())
            col = cols[i%amount].row()
            try:
                col.operator("icondisplay."+icon, text="", icon=icon)
            except:
                col.operator("icondisplay."+icon, text="new")


main()


def register():
    pass


def unregister():
    pass