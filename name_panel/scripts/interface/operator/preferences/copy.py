
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
from ....function import options
from ....function.preferences import copy

# addon
addon = bpy.context.user_preferences.addons.get(__name__.partition('.')[0])

# name
class name(Operator):
  '''
    Transfer names from some types of datablocks to others.
  '''
  bl_idname = 'wm.batch_copy_name_defaults'
  bl_label = 'Batch Name Copy Defaults'
  bl_description = 'Copy names from some types of datablocks to others.'
  bl_options = {'INTERNAL'}

  # check
  def check(self, context):
    return True

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.BatchCopyName

    # row
    row = layout.row(align=True)

    # mode
    row.prop(option, 'mode', expand=True)

    # reset settings
    op = row.operator('wm.reset_name_panel_settings', text='', icon='LOAD_FACTORY')
    op.panel = False
    op.auto = False
    op.names = False
    op.name = False
    op.copy = True

    # column
    column = layout.column(align=True)

    # source
    column.label(text='Copy:', icon='COPYDOWN')
    column = layout.column(align=True)
    column.prop(option, 'source', expand=True)
    column = layout.column(align=True)

    # targets
    column.label(text='Paste:', icon='PASTEDOWN')
    column = layout.column(align=True)
    split = column.split(align=True)
    split.prop(option, 'objects', text='', icon='OBJECT_DATA')
    split.prop(option, 'objectData', text='', icon='MESH_DATA')
    split.prop(option, 'materials', text='', icon='MATERIAL')
    split.prop(option, 'textures', text='', icon='TEXTURE')
    split.prop(option, 'particleSystems', text='', icon='PARTICLES')
    split.prop(option, 'particleSettings', text='', icon='MOD_PARTICLES')

    # use active object
    column = layout.column()
    column.prop(option, 'useActiveObject')

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''

    # copy
    copy.main(context)

    # transfer options
    options.transfer(context, False, False, False, False, True)
    return {'FINISHED'}

  # invoke
  def invoke(self, context, event):
    '''
      Invoke the operator panel/menu, control its width.
    '''

    # size
    try: size = 210 if addon.preferences['largePopups'] == 0 else 340
    except: size = 210

    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}
