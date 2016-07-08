
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
from bpy.props import BoolProperty, IntProperty
from bpy.types import Operator
from . import shared
from ...function import batch, options

# addon
addon = bpy.context.user_preferences.addons.get(__name__.partition('.')[0])

# name
class name(Operator):
  '''
    Batch name datablocks.
  '''
  bl_idname = 'wm.batch_name'
  bl_label = 'Batch Name'
  bl_description = 'Batch name datablocks.'
  bl_options = {'UNDO'}

  # quick batch
  quickBatch = BoolProperty(
    name = 'Quick Batch',
    description = 'Quickly batch name datablocks visible in the name panel.',
    default = False
  )

  # tag
  tag = BoolProperty(
    name = 'Tag',
    description = 'Generic tag.',
    default = False
  )

  # count
  count = IntProperty(
    name = 'Total named',
    description = 'Total number of names changed during the batch name process',
    default = 0
  )

  # check
  def check(self, context):
    return True

  # draw
  def draw(self, context):
    '''
      Operator body.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.BatchName

    # column
    column = layout.column(align=True)

    # quick batch
    if not self.quickBatch:

      # label
      column.label(text='Targets:')

      # row
      row = column.row(align=True)

      # batch type
      row.prop(option, 'mode', expand=True)

      # reset
      op = row.operator('wm.reset_name_panel_settings', text='', icon='LOAD_FACTORY')
      op.panel = False
      op.auto = False
      op.names = False
      op.name = True
      op.copy = False

      # column
      column = layout.column(align=True)

      # row 1
      row = column.row(align=True)
      row.scale_x = 5
      row.prop(option, 'actions', text='', icon='ACTION')
      row.prop(option, 'greasePencil', text='', icon='GREASEPENCIL')
      row.prop(option, 'objects', text='', icon='OBJECT_DATA')
      row.prop(option, 'groups', text='', icon='GROUP')
      row.prop(option, 'constraints', text='', icon='CONSTRAINT')
      row.prop(option, 'modifiers', text='', icon='MODIFIER')
      row.prop(option, 'objectData', text='', icon='MESH_DATA')
      row.prop(option, 'bones', text='', icon='BONE_DATA')
      row.prop(option, 'boneGroups', text='', icon='GROUP_BONE')
      row.prop(option, 'boneConstraints', text='', icon='CONSTRAINT_BONE')

      # row 2
      row = column.row(align=True)
      row.scale_x = 5
      row.prop(option, 'actionGroups', text='', icon='NLA')
      row.prop(option, 'pencilLayers', text='', icon='OOPS')
      row.prop(option, 'vertexGroups', text='', icon='GROUP_VERTEX')
      row.prop(option, 'shapekeys', text='', icon='SHAPEKEY_DATA')
      row.prop(option, 'uvs', text='', icon='GROUP_UVS')
      row.prop(option, 'vertexColors', text='', icon='GROUP_VCOL')
      row.prop(option, 'materials', text='', icon='MATERIAL')
      row.prop(option, 'textures', text='', icon='TEXTURE')
      row.prop(option, 'particleSystems', text='', icon='PARTICLES')
      row.prop(option, 'particleSettings', text='', icon='MOD_PARTICLES')

      # type filters
      column = layout.column()
      column.prop(option, 'objectType', text='')
      column.prop(option, 'constraintType', text='')
      column.prop(option, 'modifierType', text='')

      # column
      column = layout.column(align=True)

      # label
      column.label(text='Game Engine:')

      # row
      row = column.row(align=True)
      row.prop(option, 'sensors', text='Sensors', toggle=True)
      row.prop(option, 'controllers', text='Controllers', toggle=True)
      row.prop(option, 'actuators', text='Actuators', toggle=True)


      # column
      column = layout.column(align=True)

      # label
      column.label(text='Global:')

      # row 1
      row = column.row(align=True)
      row.scale_x = 5
      row.prop(option, 'scenes', text='', icon='SCENE_DATA')
      row.prop(option, 'renderLayers', text='', icon='RENDERLAYERS')
      row.prop(option, 'worlds', text='', icon='WORLD')
      row.prop(option, 'libraries', text='', icon='LIBRARY_DATA_DIRECT')
      row.prop(option, 'images', text='', icon='IMAGE_DATA')
      row.prop(option, 'masks', text='', icon='MOD_MASK')
      row.prop(option, 'sequences', text='', icon='SEQUENCE')
      row.prop(option, 'movieClips', text='', icon='CLIP')
      row.prop(option, 'sounds', text='', icon='SOUND')

      # row 2
      row = column.row(align=True)
      row.scale_x = 5
      row.prop(option, 'screens', text='', icon='SPLITSCREEN')
      row.prop(option, 'keyingSets', text='', icon='KEYINGSET')
      row.prop(option, 'palettes', text='', icon='COLOR')
      row.prop(option, 'brushes', text='', icon='BRUSH_DATA')
      row.prop(option, 'texts', text='', icon='TEXT')
      row.prop(option, 'nodes', text='', icon='NODE_SEL')
      row.prop(option, 'nodeLabels', text='', icon='NODE')
      row.prop(option, 'frameNodes', text='', icon='FULLSCREEN')
      row.prop(option, 'nodeGroups', text='', icon='NODETREE')

      # column
      column = layout.column(align=True)

      # label
      column.label(text='Freestyle:')

      # row
      row = column.row(align=True)
      row.scale_x = 1.5
      row.prop(option, 'lineSets', text='', icon='BRUSH_TEXDRAW')
      row.prop(option, 'linestyles', text='', icon='LINE_DATA')
      row.prop(option, 'linestyleModifiers', text='', icon='MODIFIER')
      row.prop(option, 'linestyleModifierType', text='')

      # input fields
      column.separator()
      column.separator()
      column.separator()
      column.separator()

    # quick batch
    else:

      # label
      column.label(text='Ignore:')

      # split
      split = layout.split(align=True, percentage=0.9)

      # column
      column = split.column(align=True)

      # row
      row = column.row(align=True)
      row.scale_x = 5
      row.prop(option, 'ignoreObject', text='', icon='OBJECT_DATA')
      row.prop(option, 'ignoreAction', text='', icon='ACTION')
      row.prop(option, 'ignoreGreasePencil', text='', icon='GREASEPENCIL')
      row.prop(option, 'ignoreGroup', text='', icon='GROUP')
      row.prop(option, 'ignoreConstraint', text='', icon='CONSTRAINT')
      row.prop(option, 'ignoreModifier', text='', icon='MODIFIER')
      row.prop(option, 'ignoreBone', text='', icon='BONE_DATA')
      row.prop(option, 'ignoreBoneGroup', text='', icon='GROUP_BONE')
      row.prop(option, 'ignoreBoneConstraint', text='', icon='CONSTRAINT_BONE')

      # row
      row = column.row(align=True)
      row.scale_x = 5
      row.prop(option, 'ignoreObjectData', text='', icon='MESH_DATA')
      row.prop(option, 'ignoreVertexGroup', text='', icon='GROUP_VERTEX')
      row.prop(option, 'ignoreShapekey', text='', icon='SHAPEKEY_DATA')
      row.prop(option, 'ignoreUV', text='', icon='GROUP_UVS')
      row.prop(option, 'ignoreVertexColor', text='', icon='GROUP_VCOL')
      row.prop(option, 'ignoreMaterial', text='', icon='MATERIAL')
      row.prop(option, 'ignoreTexture', text='', icon='TEXTURE')
      row.prop(option, 'ignoreParticleSystem', text='', icon='PARTICLES')
      row.prop(option, 'ignoreParticleSetting', text='', icon='MOD_PARTICLES')

      # column
      column = split.column(align=True)
      column.scale_y = 2

      # reset
      op = column.operator('wm.reset_name_panel_settings', text='', icon='LOAD_FACTORY')
      op.panel = False
      op.auto = False
      op.names = False
      op.name = True
      op.copy = False

      # input fields
      column.separator()
      column.separator()

    # column
    column = layout.column(align=True)

    # custom name
    column.prop(option, 'customName')

    # separator
    column.separator()
    column.separator()

    # find
    row = column.row(align=True)
    row.prop(option, 'find', icon='VIEWZOOM')

    # cheatsheet
    row.operator('wm.regular_expression_cheatsheet', text='', icon='FILE_TEXT')

    # regex
    row.prop(option, 'regex', text='', icon='SCRIPT')
    column.separator()

    # replace
    column.prop(option, 'replace', icon='FILE_REFRESH')
    column.separator()
    column.separator()

    # prefix
    column.prop(option, 'prefix', icon='LOOP_BACK')
    column.separator()

    # row
    row = column.row(align=True)

    # suffix
    row.prop(option, 'suffix', icon='LOOP_FORWARDS')
    row.prop(option, 'suffixLast', text='', icon='FORWARD')
    column.separator()
    column.separator()
    row = column.row()

    # trim start
    row.label(text='Trim Start:')
    row.prop(option, 'trimStart', text='')
    column.separator()
    row = column.row()

    # trim end
    row.label(text='Trim End:')
    row.prop(option, 'trimEnd', text='')
    column.separator()

    # sort
    shared.sort(column, context.scene.BatchShared)

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''

    # main
    batch.main(self, context)

    # transfer options
    options.transfer(context, False, False, False, True, False)

    # report
    self.report({'INFO'}, 'Datablocks named: ' + str(self.count))

    # tag
    self.tag = False

    # count
    self.count = 0

    return {'FINISHED'}

  # invoke
  def invoke(self, context, event):
    '''
      Invoke the operator panel/menu, control its width.
    '''

    # alt
    if event.alt:
      self.quickBatch = False

    # size
    try: size = 330 if addon.preferences['largePopups'] == 0 else 460
    except: size = 330

    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}

def register():
    bpy.utils.unregister_class(name)

def unregister():
    bpy.utils.unregister_class(name)
