
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.types import Menu

##########
## MENU ##
##########

class specials(Menu):
  '''
    Menu for item panel operators.
  '''
  bl_idname = 'VIEW3D_MT_item_panel_specials'
  bl_label = 'Operators'
  bl_description = 'Operators and settings.'

  def draw(self, context):
    '''
      Draw the menu body.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.itemPanelSettings

    # batch auto name
    layout.operator('view3d.batch_auto_name', icon='AUTO')

    # bath name
    layout.operator('wm.batch_name', icon='SORTALPHA')

    # batch copy
    layout.operator('view3d.batch_copy', icon='COPYDOWN')
    layout.separator()

    # batch reset
    layout.operator('view3d.batch_reset_settings', icon='FILE_REFRESH')

    # batch transfer
    layout.operator('view3d.batch_transfer_settings', icon='RECOVER_AUTO')

    # separator
    layout.separator()

    # pin active object
    layout.prop(option, 'pinActiveObject')

    # serparator
    # layout.separator()

    # object names
    # layout.operator('view3d.auto_name_object_names', icon='OBJECT_DATA')

    # constraint names
    # layout.operator('view3d.auto_name_constraint_names', icon='CONSTRAINT')

    # modifier names
    # layout.operator('view3d.auto_name_modifier_names', icon='MODIFIER')
