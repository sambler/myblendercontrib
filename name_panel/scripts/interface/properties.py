
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
from .buttons import properties as Buttons

# tools properties
class toolsProperties(Panel):
  '''
    Name Panel context sensitive properties panel for the 3D View toolshelf.
  '''
  bl_idname = 'VIEW3D_PT_TOOLS_properties'
  bl_space_type = 'VIEW_3D'
  bl_label = 'Properties'
  bl_region_type = 'TOOLS'
  bl_category = 'Name'

  # draw header
  def draw_header(self, context):
    '''
      Properties panel header.
    '''
    # layout
    layout = self.layout

    # panel
    panel = context.scene.PropertiesPanel

    # display active
    layout.prop(panel, 'displayActive', text='')

  # draw
  def draw(self, context):
    '''
      Properties panel body.
    '''

    layout = self.layout

    try:

      # main
      main(self, context)

    except:

      # label
      layout.label(text='Nothing to show')


# UI properties
class UIProperties(Panel):
  '''
    Name Panel context sensitive properties panel for the 3D View property shelf.
  '''
  bl_idname = 'VIEW3D_PT_UI_properties'
  bl_space_type = 'VIEW_3D'
  bl_label = 'Properties'
  bl_region_type = 'UI'

  # draw header
  def draw_header(self, context):
    '''
      Properties panel header.
    '''
    # layout
    layout = self.layout

    # panel
    panel = context.scene.PropertiesPanel

    # display active
    layout.prop(panel, 'displayActive', text='')

  # draw
  def draw(self, context):
    '''
      Properties panel body.
    '''

    try:

      # main
      main(self, context)

    except:

      # label
      layout.label(text='Nothing to show')

# main
def main(self, context):
  '''
    Get the owner, target and context of name panel, populate accordingly.
  '''

  # panel
  panel = context.scene.NamePanel

  # display active
  displayActive = context.scene.PropertiesPanel.displayActive

  # layout
  layout = self.layout

  # context
  layout.prop(panel, 'context', text='')

  # object
  if panel.context == 'OBJECT':

    # datablock
    datablock = context.object if displayActive else bpy.data.objects[panel.target]

    # object
    Buttons.Object(self, context, layout, datablock)

  # group
  elif panel.context == 'GROUP':

    # group
    Buttons.Group(self, context, layout, bpy.data.groups[panel.target])

  # action
  elif panel.context == 'ACTION':

    # action
    Buttons.Action(self, context, layout, bpy.data.actions[panel.target])

  # grease pencil
  elif panel.context == 'GREASE_PENCIL':

    # grease pencil
    Buttons.GreasePencil(self, context, layout, bpy.data.grease_pencil[panel.target])

  # constraint
  elif panel.context == 'CONSTRAINT':

    # constraint
    Buttons.Constraint(self, context, layout, bpy.data.objects[panel.owner].constraints[panel.target])

  # modifier
  elif panel.context == 'MODIFIER':

    # modifier
    Buttons.Modifier(self, context, layout, bpy.data.objects[panel.owner], bpy.data.objects[panel.owner].modifiers[panel.target])

  # object data
  elif panel.context == 'OBJECT_DATA':

    # datablock
    datablock = context.object if displayActive else bpy.data.objects[panel.target]

    # object
    Buttons.ObjectData(self, context, layout, datablock)

  # bone group
  elif panel.context == 'BONE_GROUP':

    # bone group
    Buttons.BoneGroup(self, context, layout, bpy.data.objects[panel.target])

  # bone
  elif panel.context == 'BONE':

    # datablock
    datablock = context.active_bone if displayActive else bpy.data.armatures[panel.owner].bones[panel.target] if context.mode == 'POSE' else bpy.data.armatures[panel.owner].editable_bones[panel.target]

    # bone
    Buttons.Bone(self, context, layout, datablock)


  # bone constraint
  elif panel.context == 'BONE_CONSTRAINT':

    # bone constraint
    Buttons.BoneConstraint(self, context, layout, bpy.data.objects[context.active_object.name].pose.bones[panel.owner].constraints[panel.target])

  # vertex group
  elif panel.context == 'VERTEX_GROUP':

    # vertex group
    Buttons.VertexGroup(self, context, layout, bpy.data.objects[panel.owner].vertex_groups[panel.target])

  # shapekey
  elif panel.context == 'SHAPEKEY':

    # shapekey
    Buttons.Shapekey(self, context, layout, bpy.data.objects[panel.owner].data.shape_keys.key_blocks[panel.target])

  # uv
  elif panel.context == 'UV':

    # uv
    Buttons.UV(self, context, layout, bpy.data.objects[panel.owner].data.uv_textures[panel.target])

  # vertex color
  elif panel.context == 'VERTEX_COLOR':

    # vertex color
    Buttons.VertexColor(self, context, layout, bpy.data.objects[panel.owner].data.vertex_colors[panel.target])

  # material
  elif panel.context == 'MATERIAL':

    # material
    Buttons.Material(self, context, layout, bpy.data.materials[panel.target])

  # texture
  elif panel.context == 'TEXTURE':

    # texture
    Buttons.Texture(self, context, layout, bpy.data.textures[panel.target])

  # particle system
  elif panel.context == 'PARTICLE_SYSTEM':

    # particle systems
    Buttons.ParticleSystem(self, context, layout, bpy.data.objects[panel.owner].particle_systems[panel.target])

  # particle setting
  elif panel.context == 'PARTICLE_SETTING':

    # particle settings
    Buttons.ParticleSettings(self, context, layout, bpy.data.particles[panel.target])
