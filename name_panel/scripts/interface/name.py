
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  this program; if not, write to the Free Software Foundation, Inc.,
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# imports
import bpy
import re
from bpy.types import Panel
from .. import storage
from . import icon

# addon
addon = bpy.context.user_preferences.addons.get(__name__.partition('.')[0])

# tools name
class toolsName(Panel):
  '''
    Name panel.
  '''
  bl_idname = 'VIEW3D_PT_TOOLS_name'
  bl_space_type = 'VIEW_3D'
  bl_label = 'Name'
  bl_region_type = 'TOOLS'
  bl_category = 'Name'

  # draw
  def draw(self, context):
    '''
      Name panel body.
    '''

    # main
    main(self, context)

# UI name
class UIName(Panel):
  '''
    Name panel.
  '''
  bl_idname = 'VIEW3D_PT_UI_name'
  bl_space_type = 'VIEW_3D'
  bl_label = 'Name'
  bl_region_type = 'UI'

  # draw
  def draw(self, context):
    '''
      Name panel body.
    '''

    # main
    main(self, context)

# main
def main(self, context):
  '''
    Name panel main.
  '''

  # layout
  layout = self.layout

  # panel
  panel = context.scene.NamePanel

  # column
  column = layout.column(align=True)

  # filter
  filters(self, context, column, panel)

  # search
  search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

  # mode
  if panel.mode == 'SELECTED':

    # member
    member = gather(context, {object.name: [] for object in context.selected_objects}) if panel.search != '' else {}

  # mode
  else:

    # member
    member = gather(context, {object.name: [] for object in context.scene.objects if True in [x&y for (x,y) in zip(object.layers, context.scene.layers)]}) if panel.search != '' else {}

  # pin active object
  if panel.pinActiveObject:
    if context.active_object:

      # search
      if search == '' or re.search(search, context.active_object.name, re.I) or [re.search(search, item, re.I) for item in member[context.active_object.name] if re.search(search, item, re.I) != None]:

        # populate
        populate(self, context, layout, context.active_object, panel)

    # display names
    if panel.displayNames:

      # mode
      if panel.mode == 'SELECTED':

        # objects
        objects = [[object.name, object] for object in context.selected_objects]

        # sorted
        for datablock in sorted(objects):
          if datablock[1] != context.active_object:

            # search
            if search == '' or re.search(search, datablock[1].name, re.I) or [re.search(search, item, re.I) for item in member[datablock[1].name] if re.search(search, item, re.I) != None]:

              # populate
              populate(self, context, layout, datablock[1], panel)

      # mode
      else:

        # objects
        objects = [[object.name, object] for object in context.scene.objects if True in [x&y for (x,y) in zip(object.layers, context.scene.layers)]]

        # sorted
        for datablock in sorted(objects):
          if datablock[1] != context.active_object:

            # search
            if search == '' or re.search(search, datablock[1].name, re.I) or [re.search(search, item, re.I) for item in member[datablock[1].name] if re.search(search, item, re.I) != None]:

              # populate
              populate(self, context, layout, datablock[1], panel)

  # pin active object
  else:

    # display names
    if panel.displayNames:

      # mode
      if panel.mode == 'SELECTED':

        # objects
        objects = [[object.name, object] for object in context.selected_objects]

        # sorted
        for datablock in sorted(objects):

          # search
          if search == '' or re.search(search, datablock[1].name, re.I) or [re.search(search, item, re.I) for item in member[datablock[1].name] if re.search(search, item, re.I) != None]:

            # populate
            populate(self, context, layout, datablock[1], panel)

      # mode
      else:

        # objects
        objects = [[object.name, object] for object in context.scene.objects if True in [x&y for (x,y) in zip(object.layers, context.scene.layers)]]

        # sorted
        for datablock in sorted(objects):

          # search
          if search == '' or re.search(search, datablock[1].name, re.I) or [re.search(search, item, re.I) for item in member[datablock[1].name] if re.search(search, item, re.I) != None]:

            # populate
            populate(self, context, layout, datablock[1], panel)
    else:

      # search
      if search == '' or re.search(search, context.active_object.name, re.I) or [re.search(search, item, re.I) for item in member[context.active_object.name] if re.search(search, item, re.I) != None]:

        # populate
        populate(self, context, layout, context.active_object, panel)

# filters
def filters(self, context, layout, panel):
  '''
    The name panel filters
  '''

  # row
  row = layout.row(align=True)

  # scale
  row.scale_y = 1.25

  # icon toggle
  iconToggle = 'RADIOBUT_ON' if panel.filters else 'RADIOBUT_OFF'

  # filters
  row.prop(panel, 'filters', text='Filters', icon=iconToggle, toggle=True)

  # display names
  row.prop(panel, 'displayNames', text='', icon='ZOOM_SELECTED')

  # options
  row.prop(panel, 'options', text='', icon='SETTINGS')

  # # operator menu
  row.menu('VIEW3D_MT_name_panel_specials', text='', icon='COLLAPSEMENU')

  # filters
  if panel.filters:

    # separator
    layout.separator()

    # row
    row = layout.row(align=True)

    # scale
    row.scale_x = 5 # hack: forces buttons to line up correctly

    # action
    row.prop(panel, 'action', text='', icon='ACTION')

    # grease pencil
    row.prop(panel, 'greasePencil', text='', icon='GREASEPENCIL')

    # groups
    row.prop(panel, 'groups', text='', icon='GROUP')

    # constraints
    row.prop(panel, 'constraints', text='', icon='CONSTRAINT')

    # modifiers
    row.prop(panel, 'modifiers', text='', icon='MODIFIER')

    # bone groups
    row.prop(panel, 'boneGroups', text='', icon='GROUP_BONE')

    # bone constraints
    row.prop(panel, 'boneConstraints', text='', icon='CONSTRAINT_BONE')

    # row
    row = layout.row(align=True)

    # scale
    row.scale_x = 5 # hack: forces buttons to line up correctly

    # vertex groups
    row.prop(panel, 'vertexGroups', text='', icon='GROUP_VERTEX')

    # shapekeys
    row.prop(panel, 'shapekeys', text='', icon='SHAPEKEY_DATA')

    # uvs
    row.prop(panel, 'uvs', text='', icon='GROUP_UVS')

    # vertex colors
    row.prop(panel, 'vertexColors', text='', icon='GROUP_VCOL')

    # materials
    row.prop(panel, 'materials', text='', icon='MATERIAL')

    # textures
    row.prop(panel, 'textures', text='', icon='TEXTURE')

    # particles systems
    row.prop(panel, 'particleSystems', text='', icon='PARTICLES')

    # separator
    layout.separator()

    # hide search
    if panel.hideSearch:

      # row
      row = layout.row(align=True)

      # search
      row.prop(panel, 'search', text='', icon='VIEWZOOM')
      row.operator('wm.regular_expression_cheatsheet', text='', icon='FILE_TEXT')
      row.prop(panel, 'regex', text='', icon='SCRIPTPLUGINS')
      row.operator('wm.batch_name', text='', icon='SORTALPHA').quickBatch = True

  # hide search
  if not panel.hideSearch:

    # row
    row = layout.row(align=True)

    # search
    row.prop(panel, 'search', text='', icon='VIEWZOOM')
    row.operator('wm.regular_expression_cheatsheet', text='', icon='FILE_TEXT')
    row.prop(panel, 'regex', text='', icon='SCRIPTPLUGINS')
    row.operator('wm.batch_name', text='', icon='SORTALPHA').quickBatch = True

  # enabled
  if panel.displayNames:

    # separator()
    layout.separator()

    # row
    row = layout.row()

    # mode
    row.prop(panel, 'mode', expand=True)

# gather
def gather(context, member):
  '''
    Creates a object datablock dictionary for name panel.
  '''

  # panel
  panel = context.scene.NamePanel

  # selected
  if panel.displayNames:
    if panel.mode == 'SELECTED':
      for object in context.selected_objects:
        sort(context, member, object)

    else:
      for object in context.scene.objects:
        if True in [x&y for (x,y) in zip(object.layers, context.scene.layers)]:
          sort(context, member, object)
  else:
    sort(context, member, context.active_object)

  return member

# sort
def sort(context, member, object):
  '''
    Sorts object related datablocks for search panel population.
  '''

  # panel
  panel = context.scene.NamePanel

  # search
  search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

  # group
  if panel.groups:
    for group in bpy.data.groups[:]:
      for groupobject in group.objects[:]:
        if groupobject == object:

          # search
          if search == '' or re.search(search, group.name, re.I):

            # member
            member[object.name].append(group.name)

  # action
  if panel.action:
    if hasattr(object.animation_data, 'action'):
      if hasattr(object.animation_data.action, 'name'):

        # search
        if search == '' or re.search(search, object.animation_data.action.name, re.I):

          # member
          member[object.name].append(object.animation_data.action.name)

  # grease pencil
  if panel.greasePencil:
    if hasattr(object.grease_pencil, 'name'):

      # layers
      layers = [layer.info for layer in bpy.data.objects[object.name].grease_pencil.layers]

      # search
      if search == '' or re.search(search, object.grease_pencil.name, re.I) or [re.search(search, item, re.I) for item in layers if re.search(search, item, re.I) != None]:

        # member
        member[object.name].append(object.grease_pencil.name)

        # pencil layers
        for layer in bpy.data.objects[object.name].grease_pencil.layers:

          # search
          if search == '' or re.search(search, layer.info, re.I):

            # member
            member[object.name].append(layer.info)

  # constraints
  if panel.constraints:
    for constraint in object.constraints[:]:

      # search
      if search == '' or re.search(search, constraint.name, re.I):

        # member
        member[object.name].append(constraint.name)

  # modifiers
  if panel.modifiers:
    for modifier in object.modifiers[:]:

      if modifier.type == 'PARTICLE_SYSTEM':
        # particle
        particle = [modifier.particle_system.name, modifier.particle_system.settings.name]

        # texture
        texture = [slot.texture.name for slot in modifier.particle_system.settings.texture_slots[:] if slot != None]

      elif modifier.type in {'DISPLACE', 'WARP'}:
        if modifier.texture:

          # texture
          texture = [modifier.texture.name]

      elif modifier.type in {'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_EDIT', 'VERTEX_WEIGHT_PROXIMITY'}:
        if modifier.mask_texture:

          # texture
          texture = [modifier.mask_texture.name]

      else:

        particle = []

        # texture:
        texture = []

      # search
      if search == '' or re.search(search, modifier.name, re.I) or [re.search(search, item, re.I) for item in particle if re.search(search, item, re.I) != None] or [re.search(search, item, re.I) for item in texture if re.search(search, item, re.I) != None]:

        # member
        member[object.name].append(modifier.name)

        # particle systems
        if panel.particleSystems:
          if modifier.type in 'PARTICLE_SYSTEM':

            # search
            if search == '' or re.search(search, particle[0], re.I) or re.search(search, particle[1], re.I) or [re.search(search, item, re.I) for item in texture if re.search(search, item, re.I) != None]:

              # member
              member[object.name].append(modifier.particle_system.name)

              # search
              if search == '' or re.search(search, modifier.particle_system.settings.name, re.I) or [re.search(search, item, re.I) for item in texture if re.search(search, item, re.I) != None]:

                # member
                member[object.name].append(modifier.particle_system.settings.name)

                for slot in modifier.particle_system.settings.texture_slots[:]:
                  if slot != None:

                    # search
                    if search == '' or re.search(search, slot.texture.name, re.I):

                      # member
                      member[object.name].append(slot.texture.name)

  # materials
  if panel.materials:
    for slot in object.material_slots:
      if slot.material != None:

        # textures
        textures = [tslot.texture.name for tslot in slot.material.texture_slots[:] if hasattr(tslot, 'texture')]

        # search
        if search == '' or re.search(search, slot.material.name, re.I) or [re.search(search, item, re.I) for item in textures if re.search(search, item, re.I) != None]:

          # member
          member[object.name].append(slot.material.name)

          # textures
          if panel.textures:
            if context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}:
              for tslot in slot.material.texture_slots[:]:
                if hasattr(tslot, 'texture'):
                  if tslot.texture != None:

                    # search
                    if search == '' or re.search(search, tslot.texture.name, re.I):

                      # member
                      member[object.name].append(tslot.texture.name)

  # object data
  if object.type != 'EMPTY':

    # search
    if search == '' or re.search(search, object.data.name, re.I):

      # member
      member[object.name].append(object.data.name)

  # vertex groups
  if panel.vertexGroups:
    if hasattr(object, 'vertex_groups'):
      for group in object.vertex_groups[:]:

        # search
        if search == '' or re.search(search, group.name, re.I):

          # member
          member[object.name].append(group.name)

  # shapekeys
  if panel.shapekeys:
    if hasattr(object.data, 'shape_keys'):
      if hasattr(object.data.shape_keys, 'key_blocks'):
        for key in object.data.shape_keys.key_blocks[:]:

          # search
          if search == '' or re.search(search, key.name, re.I):

            # member
            member[object.name].append(key.name)

  # uvs
  if panel.uvs:
    if object.type in 'MESH':
      for uv in object.data.uv_textures[:]:

        # search
        if search == '' or re.search(search, uv.name, re.I):

          # member
          member[object.name].append(uv.name)

  # vertex colors
  if panel.vertexColors:
    if object.type in 'MESH':
      for vertexColor in object.data.vertex_colors[:]:

        # search
        if search == '' or re.search(search, vertexColor.name, re.I):

          # member
          member[object.name].append(vertexColor.name)

  # bone groups
  if panel.boneGroups:
    if object.type in 'ARMATURE':
      for group in object.pose.bone_groups[:]:

        # search
        if search == '' or re.search(search, group.name, re.I):

          # member
          member[object.name].append(group.name)

  # bones
  if object == context.active_object:
    if object.type in 'ARMATURE':
      if object.mode in {'POSE', 'EDIT'}:

        # constraints
        try: constraints = [item.name for item in context.active_pose_bone.constraints[:]]
        except: constraints = []

        # search
        if search == '' or re.search(search, context.active_bone.name, re.I) or [re.search(search, item, re.I) for item in constraints if re.search(search, item, re.I) != None]:

          # member
          member[object.name].append(context.active_bone.name)

        # bone constraints
        if panel.boneConstraints:
          if object.mode in 'POSE':
            for constraint in context.active_pose_bone.constraints[:]:

              # search
              if search == '' or re.search(search, constraint.name, re.I):

                # member
                member[object.name].append(constraint.name)

        # display bones
        if panel.displayBones:

          # pose mode
          if object.mode in 'POSE':
            bones = object.pose.bones[:]

          # edit mode
          elif object.mode == 'EDIT':
            bones = object.data.edit_bones[:]

          # other modes
          else:
            bones = object.data.bones[:]

          # sort and display
          for bone in bones:
            if bone.name != context.active_bone:

              # constraints
              try:
                constraints = [constraint.name for constraint in object.pose.bones[bone.name].constraints[:]]
              except:
                constraints = []

              # search
              if search == '' or re.search(search, bone.name, re.I) or [re.search(search, item, re.I) for item in constraints if re.search(search, item, re.I) != None]:

                # member
                member[object.name].append(bone.name)

              # bone constraints
              if panel.boneConstraints:
                if object.mode in 'POSE':
                  for constraint in bone.constraints[:]:

                    # search
                    if search == '' or re.search(search, constraint.name, re.I):

                      # member
                      member[object.name].append(constraint.name)

  return member

# populate
def populate(self, context, layout, object, panel):
  '''
    Populates the name panel with datablock names.
  '''

  # search
  search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

  # column
  column = layout.column()

  # object
  Object(self, context, column, object, panel)

  # action
  block.object.action(self, context, column, object, panel)

  # group
  block.object.group(self, context, column, object, panel)

  # grease pencil
  block.object.greasePencil(self, context, column, object, panel)

  # constraint
  block.object.constraint(self, context, column, object, panel)

  # modifier
  block.object.modifier(self, context, column, object, panel)

  # material
  block.object.material(self, context, column, object, panel)

  # object data
  ObjectData(self, context, column, object, panel)

  # vertex group
  block.objectData.vertexGroup(self, context, column, object, panel)

  # shapekey
  block.objectData.shapekey(self, context, column, object, panel)

  # uv
  block.objectData.uv(self, context, column, object, panel)

  # vertex color
  block.objectData.vertexColor(self, context, column, object, panel)

  # material
  block.objectData.material(self, context, column, object, panel)

  # bone group
  block.objectData.boneGroup(self, context, column, object, panel)

  # row
  row = column.row()

  # separator
  row.separator()

  # object
  if object == context.active_object:

    # bone
    block.bone(self, context, column, object, panel)

# block
class block:
  '''
    contains classes;
      object
      objectData

    contains functions;
      bone
      material
  '''

  # object
  class object:
    '''
      contains functions;
        group
        action
        greasepencil
        constraint
        modifier
        material
    '''

    # group
    def group(self, context, layout, object, panel):
      '''
        group related code block.
      '''

      # search
      search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

      # groups
      if panel.groups:
        for group in bpy.data.groups[:]:
          for groupObject in group.objects[:]:
            if groupObject == object:

              # search
              if search == '' or re.search(search, group.name, re.I):

                # group
                Group(self, context, layout, group, object, panel)

    # action
    def action(self, context, layout, object, panel):
      '''
        action related code block.
      '''

      # search
      search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

      # action
      if panel.action:
        if hasattr(object.animation_data, 'action'):
          if hasattr(object.animation_data.action, 'name'):

            # search
            if search == '' or re.search(search, object.animation_data.action.name, re.I):

              # action
              Action(self, context, layout, object.animation_data.action, object, panel)

    # greasePencil
    def greasePencil(self, context, layout, object, panel):
      '''
        grease pencil related code block.
      '''

      # search
      search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

      # grease pencil
      if panel.greasePencil:
        if hasattr(object.grease_pencil, 'name'):

          # layers
          layers = [layer.info for layer in bpy.data.objects[object.name].grease_pencil.layers[:]]

          # search
          if search == '' or re.search(search, object.grease_pencil.name, re.I) or [re.search(search, item, re.I) for item in layers if re.search(search, item, re.I) != None]:

            # grease pencil
            GreasePencil(self, context, layout, object.grease_pencil, object, panel)

            # pencil layers
            for layer in bpy.data.objects[object.name].grease_pencil.layers[:]:

              # search
              if search == '' or re.search(search, layer.info, re.I):

                # pencil layer
                PencilLayer(self, context, layout, layer, object, panel)

    # constraint
    def constraint(self, context, layout, object, panel):
      '''
        Constraint related code block.
      '''

      # search
      search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

      # constraints
      if panel.constraints:
        for constraint in object.constraints[:]:

          # search
          if search == '' or re.search(search, constraint.name, re.I):

            # constraint
            Constraint(self, context, layout, constraint, object, None, panel)

    # modifier
    def modifier(self, context, layout, object, panel):
      '''
        Modifier related code block.
      '''

      # search
      search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

      # modifiers
      if panel.modifiers:
        for modifier in object.modifiers[:]:

          # particle
          particle = []

          # texture:
          texture = []

          if modifier.type == 'PARTICLE_SYSTEM':
            # particle
            particle = [modifier.particle_system.name, modifier.particle_system.settings.name]

            # texture
            texture = [slot.texture.name for slot in modifier.particle_system.settings.texture_slots[:] if slot != None]

          if modifier.type in {'DISPLACE', 'WARP'}:
            if modifier.texture:

              # texture
              texture = [modifier.texture.name]

          if modifier.type in {'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_EDIT', 'VERTEX_WEIGHT_PROXIMITY'}:
            if modifier.mask_texture:

              # texture
              texture = [modifier.mask_texture.name]

          # member
          member = particle + texture

          # search
          if search == '' or re.search(search, modifier.name, re.I) or [re.search(search, item, re.I) for item in member if re.search(search, item, re.I) != None]:

            # modifier
            Modifier(self, context, layout, modifier, object, panel)

            # texture
            if panel.textures:
              if modifier.type in {'DISPLACE', 'WARP'}:
                if modifier.texture:

                  # search
                  if search == '' or re.search(search, modifier.texture.name, re.I):

                    # texture
                    Texture(self, context, layout, modifier, object, panel)

              # mask texture
              elif modifier.type in {'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_EDIT', 'VERTEX_WEIGHT_PROXIMITY'}:
                if modifier.mask_texture:

                  # search
                  if search == '' or re.search(search, modifier.mask_texture.name, re.I):

                    # mask texture
                    MaskTexture(self, context, layout, modifier, object, panel)

            # particle systems
            if panel.particleSystems:
              if modifier.type in 'PARTICLE_SYSTEM':

                # search
                if search == '' or re.search(search, particle[0], re.I) or re.search(search, particle[1], re.I) or [re.search(search, item, re.I) for item in texture if re.search(search, item, re.I) != None]:

                  # particle
                  Particle(self, context, layout, modifier, object, panel)

                  # texture
                  if panel.textures:
                    # if context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}:
                    for slot in modifier.particle_system.settings.texture_slots[:]:
                      if hasattr(slot, 'texture'):
                        if slot.texture:

                          # search
                          if search == '' or re.search(search, slot.texture.name, re.I):

                            # texture
                            Texture(self, context, layout, slot, object, panel)

      else:
        context.scene['NamePanel']['particleSystems'] = 0

    # material
    def material(self, context, layout, object, panel):
      '''
        Material related code block.
      '''

      # search
      search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

      # materials
      if panel.materials:
        for slot in object.material_slots:
          if slot.link == 'OBJECT':
            if slot.material != None:

              # textures
              textures = [tslot.texture.name for tslot in slot.material.texture_slots[:] if hasattr(tslot, 'texture')]

              # search
              if search == '' or re.search(search, slot.material.name, re.I) or [re.search(search, item, re.I) for item in textures if re.search(search, item, re.I) != None]:

                # material
                Material(self, context, layout, slot, object, panel)

                # textures
                if panel.textures:
                  if context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}:
                    for tslot in slot.material.texture_slots[:]:
                      if hasattr(tslot, 'texture'):
                        if tslot.texture != None:

                          # search
                          if search == '' or re.search(search, tslot.texture.name, re.I):

                            # texture
                            Texture(self, context, layout, tslot, object, panel)

  # object data
  class objectData:
    '''
      Constains Functions;
        vertexGroup
        shapekey
        uv
        vertexColor
        material
        boneGroup
    '''

    # vertex group
    def vertexGroup(self, context, layout, object, panel):
      '''
        Vertex group related code block.
      '''

      # search
      search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

      # vertex groups
      if panel.vertexGroups:
        if hasattr(object, 'vertex_groups'):
          for group in object.vertex_groups[:]:

            # search
            if search == '' or re.search(search, group.name, re.I):

              # vertex group
              VertexGroup(self, context, layout, group, object, panel)

    # shapekey
    def shapekey(self, context, layout, object, panel):
      '''
        Shapekey related code block.
      '''

      # search
      search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

      # shapekeys
      if panel.shapekeys:
        if hasattr(object.data, 'shape_keys'):
          if hasattr(object.data.shape_keys, 'key_blocks'):
            for key in object.data.shape_keys.key_blocks[:]:

              # search
              if search == '' or re.search(search, key.name, re.I):

                # shapekey
                Shapekey(self, context, layout, key, object, panel)

    # uv
    def uv(self, context, layout, object, panel):
      '''
        UV related code block.
      '''

      # search
      search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

      # uvs
      if panel.uvs:
        if object.type in 'MESH':
          for uv in object.data.uv_textures[:]:

            # search
            if search == '' or re.search(search, uv.name, re.I):

              # uv
              UV(self, context, layout, uv, object, panel)

    # vertex color
    def vertexColor(self, context, layout, object, panel):
      '''
        Vertex color related code block.
      '''

      # search
      search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

      # vertex colors
      if panel.vertexColors:
        if object.type in 'MESH':
          for vertexColor in object.data.vertex_colors[:]:

            # search
            if search == '' or re.search(search, vertexColor.name, re.I):

              # vertex color
              VertexColor(self, context, layout, vertexColor, object, panel)

    # material
    def material(self, context, layout, object, panel):
      '''
        Material related code block.
      '''

      # search
      search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

      # materials
      if panel.materials:
        for slot in object.material_slots:
          if slot.link == 'DATA':
            if slot.material != None:

              # textures
              textures = [tslot.texture.name for tslot in slot.material.texture_slots[:] if hasattr(tslot, 'texture')]

              # search
              if search == '' or re.search(search, slot.material.name, re.I) or [re.search(search, item, re.I) for item in textures if re.search(search, item, re.I) != None]:

                # material
                Material(self, context, layout, slot, object, panel)

                # textures
                if panel.textures:
                  if context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}:
                    for tslot in slot.material.texture_slots[:]:
                      if hasattr(tslot, 'texture'):
                        if tslot.texture != None:

                          # search
                          if search == '' or re.search(search, tslot.texture.name, re.I):

                            # texture
                            Texture(self, context, layout, tslot, object, panel)

    # bone groups
    def boneGroup(self, context, layout, object, panel):
      '''
        Bone group related code block.
      '''

      # search
      search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

      # bone groups
      if panel.boneGroups:
        if object.type in 'ARMATURE':
          for group in object.pose.bone_groups[:]:

            # search
            if search == '' or re.search(search, group.name, re.I):

              # bone group
              BoneGroup(self, context, layout, group, object)

  # bones
  def bone(self, context, layout, object, panel):
    '''
      Bone related code block.
    '''

    # search
    search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

    # active bone
    if object.type in 'ARMATURE':
      if context.active_bone:
        if object.mode in {'POSE', 'EDIT'}:

          # constraints
          try: constraints = [item.name for item in context.active_pose_bone.constraints[:]]
          except: constraints = []

          # display bones
          if panel.displayBones:

            row = layout.row()

            row.prop(panel, 'boneMode', expand=True)

            layout.separator()

          # search
          if search == '' or re.search(search, context.active_bone.name, re.I) or [re.search(search, item, re.I) for item in constraints if re.search(search, item, re.I) != None]:

            # bone
            Bone(self, context, layout, context.active_bone, object, panel)

            # bone constraints
            if panel.boneConstraints:
              if object.mode in 'POSE':
                bone = context.active_pose_bone
                if bone:
                  for constraint in bone.constraints[:]:

                    # search
                    if search == '' or re.search(search, constraint.name, re.I):

                      # constraint
                      Constraint(self, context, layout, constraint, object, bone, panel)

                  # constraints
                  if constraints != []:

                    # row
                    row = layout.row()

                    # separator
                    row.separator()

          # display bones
          if panel.displayBones:

            # pose mode
            if object.mode in 'POSE':

              # bones
              bones = object.data.bones[:]

            # edit mode
            else:

              # bones
              bones = object.data.edit_bones[:]

            # selected
            if panel.boneMode == 'SELECTED':

              # bones
              bones = [[bone.name, bone] for bone in bones if bone.select]

            # layers
            else:

              # bones
              bones = [[bone.name, bone] for bone in bones if True in [x&y for (x, y) in zip(bone.layers, object.data.layers)]]

            # sort and display
            for bone in sorted(bones):
              if bone[1] != context.active_bone:

                # constraints
                try: constraints = [item.name for item in object.pose.bones[bone[1].name].constraints[:]]
                except: constraints = []

                # search
                if search == '' or re.search(search, bone[1].name, re.I) or [re.search(search, item, re.I) for item in constraints if re.search(search, item, re.I) != None]:

                  # bone
                  Bone(self, context, layout, bone[1], object, panel)

                  # bone constraints
                  if panel.boneConstraints:
                    if object.mode in 'POSE':
                      for constraint in object.pose.bones[bone[1].name].constraints[:]:

                        # search
                        if search == '' or re.search(search, constraint.name, re.I):

                          # constraint
                          Constraint(self, context, layout, constraint, object, bone[1], panel)

                      # constraints
                      if constraints != []:

                        # row
                        row = layout.row()

                        # separator
                        row.separator()

# object
def Object(self, context, layout, datablock, panel):
  '''
    The object name row.
  '''
  # search
  search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

  # active object
  if datablock == context.active_object:

    # row
    row = layout.row(align=True)
    row.active = (search == '' or re.search(search, datablock.name, re.I) != None)

    # template
    row.template_ID(context.scene.objects, 'active')

  # selected object
  else:

    # row
    row = layout.row(align=True)
    row.active = (search == '' or re.search(search, datablock.name, re.I) != None)

    # sub
    sub = row.row(align=True)

    # scale
    sub.scale_x = 1.6

    # icon
    op = sub.operator('view3d.name_panel_icon', text='', icon=icon.object(datablock))
    op.owner = datablock.name
    op.target = datablock.name
    op.context = 'OBJECT'

    # object
    row.prop(datablock, 'name', text='')

    # options
    if panel.options:

      # hide
      row.prop(datablock, 'hide', text='')

      # hide select
      row.prop(datablock, 'hide_select', text='')

      # hide render
      row.prop(datablock, 'hide_render', text='')

# group
def Group(self, context, layout, datablock, object, panel):
  '''
    The object group name row.
  '''

  # row
  row = layout.row(align=True)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon='GROUP', emboss=False)
  op.owner = object.name
  op.target = datablock.name
  op.context = 'GROUP'

  # label
  # sub.label(text='', icon='GROUP')

  # name
  row.prop(datablock, 'name', text='')

# action
def Action(self, context, layout, datablock, object, panel):
  '''
    The object action name row.
  '''

  # row
  row = layout.row(align=True)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon='ACTION', emboss=False)
  op.owner = object.name
  op.target = datablock.name
  op.context = 'ACTION'

  # name
  row.prop(datablock, 'name', text='')

# grease pencil
def GreasePencil(self, context, layout, datablock, object, panel):
  '''
    The object grease pencil name row.
  '''

  # search
  search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

  # row
  row = layout.row(align=True)
  row.active = (search == '' or re.search(search, datablock.name, re.I) != None)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon='GREASEPENCIL', emboss=False)
  op.owner = object.name
  op.target = datablock.name
  op.context = 'GREASE_PENCIL'

  # name
  row.prop(datablock, 'name', text='')

# pencil layer
def PencilLayer(self, context, layout, datablock, object, panel):
  '''
    The object pencil layer name row.
  '''

  # row
  row = layout.row(align=True)

  # sub
  sub = row.row(align=True)

  # scale
  sub.scale_x = 0.085

  # fill color
  sub.prop(datablock, 'fill_color', text='')

  # color
  sub.prop(datablock, 'color', text='')

  # info (name)
  row.prop(datablock, 'info', text='')

  # options
  if panel.options:

    # lock
    row.prop(datablock, 'lock', text='')

    # hide
    row.prop(datablock, 'hide', text='')

# constraint
def Constraint(self, context, layout, datablock, object, bone, panel):
  '''
    The object or pose bone constraint name row.
  '''

  # row
  row = layout.row(align=True)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon='CONSTRAINT', emboss=False)
  op.owner = object.name if not bone else bone.name
  op.target = datablock.name
  op.context = 'CONSTRAINT' if not bone else 'BONE_CONSTRAINT'

  # name
  row.prop(datablock, 'name', text='')

  # options
  if panel.options:

    # influence
    if datablock.type not in {'RIGID_BODY_JOINT', 'NULL'}:

      # sub
      sub = row.row(align=True)

      # scale
      sub.scale_x = 0.17

      # influence
      sub.prop(datablock, 'influence', text='')

    # icon view
    iconView = 'RESTRICT_VIEW_ON' if datablock.mute else 'RESTRICT_VIEW_OFF'

    # mute
    row.prop(datablock, 'mute', text='', icon=iconView)

# modifier
def Modifier(self, context, layout, datablock, object, panel):
  '''
    The object modifier name row.
  '''

  # search
  search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

  # row
  row = layout.row(align=True)
  row.active = (search == '' or re.search(search, datablock.name, re.I) != None)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon=icon.modifier(datablock), emboss=False)
  op.owner = object.name
  op.target = datablock.name
  op.context = 'MODIFIER'

  # name
  row.prop(datablock, 'name', text='')

  # options
  if panel.options:
    if datablock.type not in {'COLLISION', 'SOFT_BODY'}:

      # icon render
      iconRender = 'RESTRICT_RENDER_OFF' if datablock.show_render else 'RESTRICT_RENDER_ON'

      # show render
      row.prop(datablock, 'show_render', text='', icon=iconRender)

      # icon view
      iconView = 'RESTRICT_VIEW_OFF' if datablock.show_viewport else 'RESTRICT_VIEW_ON'

      # show viewport
      row.prop(datablock, 'show_viewport', text='', icon=iconView)

# object data
def ObjectData(self, context, layout, datablock, panel):
  '''
    The object data name row.
  '''

  # search
  search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

  # row
  row = layout.row(align=True)
  if datablock.type != 'EMPTY':
    row.active = (search == '' or re.search(search, datablock.data.name, re.I) != None)

  # empty
  if datablock.type in 'EMPTY':

    # empty image draw type
    if datablock.empty_draw_type in 'IMAGE':

      # image
      row.template_ID(datablock, 'data', open='image.open', unlink='image.unlink')

  else:

    if datablock == context.active_object:

      # name
      row.template_ID(datablock, 'data')

    else:

      # sub
      sub = row.row(align=True)
      sub.scale_x = 1.6

      # icon
      op = sub.operator('view3d.name_panel_icon', text='', icon=icon.objectData(datablock))
      op.owner = datablock.name
      op.target = datablock.name
      op.context = 'OBJECT_DATA'

      # name
      row.prop(datablock.data, 'name', text='')

# vertex group
def VertexGroup(self, context, layout, datablock, object, panel):
  '''
    The object data vertex group name row.
  '''

  # row
  row = layout.row(align=True)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon='GROUP_VERTEX', emboss=False)
  op.owner = object.name
  op.target = datablock.name
  op.context = 'VERTEX_GROUP'

  # name
  row.prop(datablock, 'name', text='')

  # options
  if panel.options:

    # icon lock
    iconLock = 'LOCKED' if datablock.lock_weight else 'UNLOCKED'

    # lock weight
    row.prop(datablock, 'lock_weight', text='', icon=iconLock)

# shapekey
def Shapekey(self, context, layout, datablock, object, panel):
  '''
    The object animation data data shapekey name row.
  '''

  # row
  row = layout.row(align=True)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon='SHAPEKEY_DATA', emboss=False)
  op.owner = object.name
  op.target = datablock.name
  op.context = 'SHAPEKEY'

  # name
  row.prop(datablock, 'name', text='')

  # options
  if panel.options:
    if datablock != object.data.shape_keys.key_blocks[0]:

      # sub
      sub = row.row(align=True)

      # scale
      sub.scale_x = 0.17

      # value
      sub.prop(datablock, 'value', text='')

    # mute
    row.prop(datablock, 'mute', text='', icon='RESTRICT_VIEW_OFF')

# uv
def UV(self, context, layout, datablock, object, panel):
  '''
    The object data uv name row.
  '''

  # row
  row = layout.row(align=True)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon='GROUP_UVS', emboss=False)
  op.owner = object.name
  op.target = datablock.name
  op.context = 'UV'

  # name
  row.prop(datablock, 'name', text='')

  # options
  if panel.options:

    # icon active
    iconActive = 'RESTRICT_RENDER_OFF' if datablock.active_render else 'RESTRICT_RENDER_ON'

    # active render
    row.prop(datablock, 'active_render', text='', icon=iconActive)

# vertex color
def VertexColor(self, context, layout, datablock, object, panel):
  '''
    The object data vertex color name row.
  '''

  # row
  row = layout.row(align=True)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon='GROUP_VCOL', emboss=False)
  op.owner = object.name
  op.target = datablock.name
  op.context = 'VERTEX_COLOR'

  # name
  row.prop(datablock, 'name', text='')

  # options
  if panel.options:

    # icon active
    iconActive = 'RESTRICT_RENDER_OFF' if datablock.active_render else 'RESTRICT_RENDER_ON'

    # active_render
    row.prop(datablock, 'active_render', text='', icon=iconActive)

# material
def Material(self, context, layout, datablock, object, panel):
  '''
    The object material name row.
  '''

  # search
  search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

  # row
  row = layout.row(align=True)
  row.active = (search == '' or re.search(search, datablock.name, re.I) != None)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon='MATERIAL', emboss=False)
  op.owner = object.name
  op.target = datablock.name
  op.context = 'MATERIAL'

  # name
  row.prop(datablock.material, 'name', text='')

# texture
def Texture(self, context, layout, datablock, object, panel):
  '''
    The texture name row.
  '''

  # row
  row = layout.row(align=True)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon='TEXTURE', emboss=False)
  op.owner = object.name
  op.target = datablock.name
  op.context = 'TEXTURE'

  # name
  row.prop(datablock.texture, 'name', text='')

  # options
  if panel.options:
    if hasattr(datablock, 'use'):

      # icon toggle
      iconToggle = 'RADIOBUT_ON' if datablock.use else 'RADIOBUT_OFF'

      # use
      row.prop(datablock, 'use', text='', icon=iconToggle)

# mask texture
def MaskTexture(self, context, layout, datablock, object, panel):
  '''
    The mask texture name row.
  '''

  # row
  row = layout.row(align=True)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon='TEXTURE', emboss=False)
  op.owner = object.name
  op.target = datablock.name
  op.context = 'TEXTURE'

  # name
  row.prop(datablock.mask_texture, 'name', text='')

  # options
  if panel.options:
    if hasattr(datablock, 'use'):

      # icon toggle
      iconToggle = 'RADIOBUT_ON' if datablock.use else 'RADIOBUT_OFF'

      # use
      row.prop(datablock, 'use', text='', icon=iconToggle)

# particle
def Particle(self, context, layout, datablock, object, panel):
  '''
    The modifier particle system and setting name row.
  '''

  # search
  search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

  # row
  row = layout.row(align=True)
  row.active = (search == '' or re.search(search, datablock.particle_system.name, re.I) != None)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon='PARTICLES', emboss=False)
  op.owner = object.name
  op.target = datablock.particle_system.name
  op.context = 'PARTICLE_SYSTEM'

  # name
  row.prop(datablock.particle_system, 'name', text='')

  # search
  if search == '' or re.search(search, datablock.particle_system.settings.name, re.I):

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # icon
    op = sub.operator('view3d.name_panel_icon', text='', icon='DOT', emboss=False)
    op.owner = object.name
    op.target = datablock.particle_system.settings.name
    op.context = 'PARTICLE_SETTING'

    # name
    row.prop(datablock.particle_system.settings, 'name', text='')

# bone group
def BoneGroup(self, context, layout, datablock, object):
  '''
    The armature data bone group name row.
  '''

  # row
  row = layout.row(align=True)

  # sub
  sub = row.row()

  # scale
  sub.scale_x = 1.6

  # icon
  op = sub.operator('view3d.name_panel_icon', text='', icon='GROUP_BONE', emboss=False)
  op.owner = object.name
  op.target = datablock.name
  op.context = 'BONE_GROUP'

  # name
  row.prop(datablock, 'name', text='')

# bone
def Bone(self, context, layout, datablock, object, panel):
  '''
    The object data bone.
  '''

  # search
  search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

  # row
  row = layout.row(align=True)

  # enabled
  row.active = (search == '' or re.search(search, datablock.name, re.I) != None)

  # sub
  sub = row.row(align=True)

  # scale
  sub.scale_x = 1.6

  # active
  if datablock == context.active_bone:

    # display bones
    sub.prop(panel, 'displayBones', text='', icon='BONE_DATA')

  # pose mode
  if object.mode in 'POSE':

    # datablock
    if not datablock == context.active_bone:

      # icon
      op = sub.operator('view3d.name_panel_icon', text='', icon='BONE_DATA')
      op.owner = object.name
      op.target = datablock.name
      op.context = 'BONE'

      # name
      row.prop(datablock, 'name', text='')

    # datablock
    else:

      # name
      row.prop(datablock, 'name', text='')

    # options
    if panel.options:

      # icon view
      iconView = 'RESTRICT_VIEW_ON' if datablock.hide else 'RESTRICT_VIEW_OFF'

      # hide
      row.prop(datablock, 'hide', text='', icon=iconView)

      # icon hide select
      iconSelect = 'RESTRICT_SELECT_ON' if datablock.hide_select else 'RESTRICT_SELECT_OFF'

      # hide select
      row.prop(datablock, 'hide_select', text='', icon=iconSelect)

  # edit mode
  else:

    # name
    if not datablock == context.active_bone:

      # icon
      op = sub.operator('view3d.name_panel_icon', text='', icon='BONE_DATA')
      op.owner = object.name
      op.target = datablock.name
      op.context = 'BONE'

    # name
    row.prop(datablock, 'name', text='')

    # options
    if panel.options:

      # icon view
      iconView = 'RESTRICT_VIEW_ON' if datablock.hide else 'RESTRICT_VIEW_OFF'

      # hide
      row.prop(datablock, 'hide', text='', icon=iconView)

      # icon select
      iconSelect = 'RESTRICT_SELECT_ON' if datablock.hide_select else 'RESTRICT_SELECT_OFF'

      # hide select
      row.prop(datablock, 'hide_select', text='', icon=iconSelect)

      # icon lock
      iconLock = 'LOCKED' if datablock.lock else 'UNLOCKED'

      # lock
      row.prop(datablock, 'lock', text='', icon=iconLock)

  if object.mode in 'EDIT':
    # row
    row = layout.row()

    # separator
    row.separator()

  elif object.mode in 'POSE':
    if not panel.boneConstraints or bpy.data.objects[object.name].pose.bones[datablock.name].constraints[:] == []:

      # row
      row = layout.row()

      # separator
      row.separator()
