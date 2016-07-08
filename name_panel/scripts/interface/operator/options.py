
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
from bpy.types import Operator
from bpy.props import BoolProperty
from ...function import options

# reset
class reset(Operator):
  '''
    Reset option values.
  '''
  bl_idname = 'wm.reset_name_panel_settings'
  bl_label = 'Reset Settings'
  bl_description = 'Reset settings to the default values.'
  bl_options = {'REGISTER', 'UNDO'}

  # panel
  panel = BoolProperty(
    name = 'Name Panel',
    description = 'Reset the setting values for the name panel.',
    default = False
  )

  # auto
  auto = BoolProperty(
    name = 'Auto Name',
    description = 'Reset the setting values for batch auto name.',
    default = True
  )

  # names
  names = BoolProperty(
    name = 'Auto Name \N{Rightwards Arrow} Names',
    description = 'Reset the setting values for batch auto name \N{Rightwards Arrow} name settings.',
    default = False
  )

  # name
  name = BoolProperty(
    name = 'Batch Name',
    description = 'Reset the setting values for batch name.',
    default = True
  )

  # copy
  copy = BoolProperty(
    name = 'Batch Name Copy',
    description = 'Reset the setting values for batch name copy.',
    default = True
  )

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # column
    column = layout.column()

    # options
    column.prop(self, 'panel')
    column.prop(self, 'auto')
    column.prop(self, 'names')
    column.prop(self, 'name')
    column.prop(self, 'copy')

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''

    # reset
    options.reset(context, self.panel, self.auto, self.names, self.name, self.copy)
    return {'FINISHED'}

# transfer
class transfer(Operator):
  '''
    Transfer option values.
  '''
  bl_idname = 'wm.transfer_name_panel_settings'
  bl_label = 'Transfer Settings'
  bl_description = 'Transfer current name panel setting values to other scenes.'
  bl_options = {'REGISTER', 'UNDO'}

  # panel
  panel = BoolProperty(
    name = 'Name Panel',
    description = 'Transfer the setting values for the name panel.',
    default = True
  )

  # auto
  auto = BoolProperty(
    name = 'Auto Name',
    description = 'Transfer the setting values for auto name.',
    default = True
  )

  # names
  names = BoolProperty(
    name = 'Auto Name \N{Rightwards Arrow} Names',
    description = 'Transfer the setting values for the auto name \N{Rightwards Arrow} names.',
    default = True
  )

  # name
  name = BoolProperty(
    name = 'Batch Name',
    description = 'Transfer the setting values for batch name.',
    default = True
  )

  # copy
  copy = BoolProperty(
    name = 'Batch Name Copy',
    description = 'Transfer the setting values for batch name copy.',
    default = True
  )

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # column
    column = layout.column()

    # options
    column.prop(self, 'panel')
    column.prop(self, 'auto')
    column.prop(self, 'names')
    column.prop(self, 'name')
    column.prop(self, 'copy')

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''

    # reset
    options.transfer(context, self.panel, self.auto, self.names, self.name, self.copy)
    return {'FINISHED'}
