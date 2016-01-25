
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

# imports
import bpy
from bpy.types import Panel
from . import interface, storage

###########
## PANEL ##
###########

# item
class item(Panel):
  '''
    Item panel
  '''
  bl_label = 'Item'
  bl_idname = 'VIEW3D_PT_item'
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'

  # draw
  def draw(self, context):
    '''
      Item panel body.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.itemPanelSettings

    # selected objects
    selectedObjects = [
      # [object.name, object]
    ]

    # column
    column = layout.column(align=True)

    # filters
    interface.panel.filters(self, context, column, option)

    # objects
    for object in context.selected_objects[:]:

      # append selected objects
      selectedObjects.append([object.name, object])

    # pin active object
    if option.pinActiveObject:
      if context.active_object:

        # populate
        interface.panel.populate(self, context, layout, context.active_object, option)

      # selected
      if option.selected:

        # sorted
        for datablock in sorted(selectedObjects):
          if datablock:
            if datablock[1] != context.active_object:

              # populate
              interface.panel.populate(self, context, layout, datablock[1], option)
    else:
      for datablock in sorted(selectedObjects):
        if datablock:

          # populate
          interface.panel.populate(self, context, layout, datablock[1], option)
