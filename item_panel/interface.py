
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

#############
## CLASSES ##
#############

class icon:

  # object icon
  def object(object):
    '''
      Returns a icon based on object type.
    '''

    # mesh
    if object.type in 'MESH':
      icon = 'OUTLINER_OB_MESH'

    # curve
    elif object.type in 'CURVE':
      icon = 'OUTLINER_OB_CURVE'

    # surface
    elif object.type in 'SURFACE':
      icon = 'OUTLINER_OB_SURFACE'

    # meta
    elif object.type in 'META':
      icon = 'OUTLINER_OB_META'

    # font
    elif object.type in 'FONT':
      icon = 'OUTLINER_OB_FONT'

    # armature
    elif object.type in 'ARMATURE':
      icon = 'OUTLINER_OB_ARMATURE'

    # lattice
    elif object.type in 'LATTICE':
      icon = 'OUTLINER_OB_LATTICE'

    # empty
    elif object.type in 'EMPTY':
      icon = 'OUTLINER_OB_EMPTY'

    # speaker
    elif object.type in 'SPEAKER':
      icon = 'OUTLINER_OB_SPEAKER'

    # camera
    elif object.type in 'CAMERA':
      icon = 'OUTLINER_OB_CAMERA'

    # lamp
    elif object.type in 'LAMP':
      icon = 'OUTLINER_OB_LAMP'

    # default
    else:
      icon = 'OUTLINER_OB_MESH'
    return icon

  # modifier icon
  def modifier(modifier):
    '''
      Returns a icon based on modifier type.
    '''

    # data transfer
    if modifier.type in 'DATA_TRANSFER':
      icon = 'MOD_DATA_TRANSFER'

    # mesh cache
    elif modifier.type in 'MESH_CACHE':
      icon = 'MOD_MESHDEFORM'

    # normal edit
    elif modifier.type in 'NORMAL_EDIT':
      icon = 'MOD_NORMALEDIT'

    # uvs project
    elif modifier.type in 'UV_PROJECT':
      icon = 'MOD_UVPROJECT'

    # uvs warp
    elif modifier.type in 'UV_WARP':
      icon = 'MOD_UVPROJECT'

    # vertex weight edit
    elif modifier.type in 'VERTEX_WEIGHT_EDIT':
      icon = 'MOD_VERTEX_WEIGHT'

    # vertex weight mix
    elif modifier.type in 'VERTEX_WEIGHT_MIX':
      icon = 'MOD_VERTEX_WEIGHT'

    # vertex weight proximity
    elif modifier.type in 'VERTEX_WEIGHT_PROXIMITY':
      icon = 'MOD_VERTEX_WEIGHT'

    # array
    elif modifier.type in 'ARRAY':
      icon = 'MOD_ARRAY'

    # bevel
    elif modifier.type in 'BEVEL':
      icon = 'MOD_BEVEL'

    # bolean
    elif modifier.type in 'BOOLEAN':
      icon = 'MOD_BOOLEAN'

    # boptionld
    elif modifier.type in 'BUILD':
      icon = 'MOD_BUILD'

    # decimate
    elif modifier.type in 'DECIMATE':
      icon = 'MOD_DECIM'

    # edge split
    elif modifier.type in 'EDGE_SPLIT':
      icon = 'MOD_EDGESPLIT'

    # mask
    elif modifier.type in 'MASK':
      icon = 'MOD_MASK'

    # mirror
    elif modifier.type in 'MIRROR':
      icon = 'MOD_MIRROR'

    # multires
    elif modifier.type in 'MULTIRES':
      icon = 'MOD_MULTIRES'

    # remesh
    elif modifier.type in 'REMESH':
      icon = 'MOD_REMESH'

    # screw
    elif modifier.type in 'SCREW':
      icon = 'MOD_SCREW'

    # skin
    elif modifier.type in 'SKIN':
      icon = 'MOD_SKIN'

    # solidify
    elif modifier.type in 'SOLIDIFY':
      icon = 'MOD_SOLIDIFY'

    # subsurf
    elif modifier.type in 'SUBSURF':
      icon = 'MOD_SUBSURF'

    # triangulate
    elif modifier.type in 'TRIANGULATE':
      icon = 'MOD_TRIANGULATE'

    # wireframe
    elif modifier.type in 'WIREFRAME':
      icon = 'MOD_WIREFRAME'

    # armature
    elif modifier.type in 'ARMATURE':
      icon = 'MOD_ARMATURE'

    # cast
    elif modifier.type in 'CAST':
      icon = 'MOD_CAST'

    # corrective smooth
    elif modifier.type in 'CORRECTIVE_SMOOTH':
      icon = 'MOD_SMOOTH'

    # curve
    elif modifier.type in 'CURVE':
      icon = 'MOD_CURVE'

    # displace
    elif modifier.type in 'DISPLACE':
      icon = 'MOD_DISPLACE'

    # hook
    elif modifier.type in 'HOOK':
      icon = 'HOOK'

    # laplacian smooth
    elif modifier.type in 'LAPLACIANSMOOTH':
      icon = 'MOD_SMOOTH'

    # laplacian deform
    elif modifier.type in 'LAPLACIANDEFORM':
      icon = 'MOD_MESHDEFORM'

    # lattice
    elif modifier.type in 'LATTICE':
      icon = 'MOD_LATTICE'

    # mesh deform
    elif modifier.type in 'MESH_DEFORM':
      icon = 'MOD_MESHDEFORM'

    # shrinkwrap
    elif modifier.type in 'SHRINKWRAP':
      icon = 'MOD_SHRINKWRAP'

    # simple deform
    elif modifier.type in 'SIMPLE_DEFORM':
      icon = 'MOD_SIMPLEDEFORM'

    # smooth
    elif modifier.type in 'SMOOTH':
      icon = 'MOD_SMOOTH'

    # warp
    elif modifier.type in 'WARP':
      icon = 'MOD_WARP'

    # wave
    elif modifier.type in 'WAVE':
      icon = 'MOD_WAVE'

    # cloth
    elif modifier.type in 'CLOTH':
      icon = 'MOD_CLOTH'

    # collision
    elif modifier.type in 'COLLISION':
      icon = 'MOD_PHYSICS'

    # dynamic paint
    elif modifier.type in 'DYNAMIC_PAINT':
      icon = 'MOD_DYNAMICPAINT'

    # explode
    elif modifier.type in 'EXPLODE':
      icon = 'MOD_EXPLODE'

    # floptiond simulation
    elif modifier.type in 'FLUID_SIMULATION':
      icon = 'MOD_FLUIDSIM'

    # ocean
    elif modifier.type in 'OCEAN':
      icon = 'MOD_OCEAN'

    # particle instance
    elif modifier.type in 'PARTICLE_INSTANCE':
      icon = 'MOD_PARTICLES'

    # particle system
    elif modifier.type in 'PARTICLE_SYSTEM':
      icon = 'MOD_PARTICLES'

    # smoke
    elif modifier.type in 'SMOKE':
      icon = 'MOD_SMOKE'

    # soft body
    elif modifier.type in 'SOFT_BODY':
      icon = 'MOD_SOFT'

    # default
    else:
      icon = 'MODIFIER'
    return icon

  # object data icon
  def objectData(object):
    '''
      Returns a icon based on object type.
    '''

    # mesh
    if object.type in 'MESH':
      icon = 'MESH_DATA'

    # curve
    elif object.type in 'CURVE':
      icon = 'CURVE_DATA'

    # surface
    elif object.type in 'SURFACE':
      icon = 'SURFACE_DATA'

    # meta
    elif object.type in 'META':
      icon = 'META_DATA'

    # font
    elif object.type in 'FONT':
      icon = 'FONT_DATA'

    # armature
    elif object.type in 'ARMATURE':
      icon = 'ARMATURE_DATA'

    # lattice
    elif object.type in 'LATTICE':
      icon = 'LATTICE_DATA'

    # speaker
    elif object.type in 'SPEAKER':
      icon = 'SPEAKER'

    # camera
    elif object.type in 'CAMERA':
      icon = 'CAMERA_DATA'

    # lamp
    elif object.type in 'LAMP':
      icon = 'LAMP_DATA'

    # default
    else:
      icon = 'MESH_DATA'
    return icon

# button
class button:
  '''
    Contains Function;
      batchName
  '''

  # batch name
  def batchName(self, context):
    '''
      Button for the batch name operator.
    '''

    # row
    row = self.layout
    row.operator('wm.batch_name', icon='SORTALPHA')

# panel
class panel:
  '''
    Contains Classes;
      blocks

    Contains Functions;
      filters
      populate
      object
      group
      action
      greasePencil
      pencilLayer
      constraint
      modifier
      objectData
      vertexGroup
      shapekey
      uv
      vertexColor
      material
      texture
      particle
      boneGroup
      bone
  '''

  # block
  class blocks:
    '''
      Contains Classes;
        object
        objectData

      Contains Functions;
        bone
        material
    '''

    # object
    class object:
      '''
        Contains Functions;
          group
          action
          greasePencil
          constraint
          modifier
          material
      '''

      # group
      def group(self, context, layout, object, option):
        '''
          Group related code block.
        '''

        # groups
        if option.groups:
          for group in bpy.data.groups[:]:
            for groupObject in group.objects[:]:
              if groupObject == object:

                # group
                panel.group(self, context, layout, group, object)

      # action
      def action(self, context, layout, object, option):
        '''
          Action related code block.
        '''

        # action
        if option.action:
          if hasattr(object.animation_data, 'action'):
            if hasattr(object.animation_data.action, 'name'):

              panel.action(self, context, layout, object.animation_data.action, object)

      # greasePencil
      def greasePencil(self, context, layout, object, option):
        '''
          Grease pencil related code block.
        '''

        # grease pencil
        if option.greasePencil:

          # layers
          if hasattr(object.grease_pencil, 'name'):

            # grease pencil
            panel.greasePencil(self, context, layout, object.grease_pencil, object)

            # pencil layers
            for layer in bpy.data.objects[object.name].grease_pencil.layers[:]:

              # pencil layer
              panel.pencilLayer(self, context, layout, layer, object, option)

      # constraint
      def constraint(self, context, layout, object, option):
        '''
          Constraint related code block.
        '''

        # constraints
        if option.constraints:
          for constraint in object.constraints[:]:

            # constraint
            panel.constraint(self, context, layout, constraint, object, None, option)

      # modifier
      def modifier(self, context, layout, object, option):
        '''
          Modifier related code block.
        '''
        # modifiers
        if option.modifiers:
          for modifier in object.modifiers[:]:

            # modifier
            panel.modifier(self, context, layout, modifier, object, option)

            # particle systems
            if option.particleSystems:
              if modifier.type in 'PARTICLE_SYSTEM':

                # particle
                panel.particle(self, context, layout, modifier, object, option)

      # materials
      def material(self, context, layout, object, option):
        '''
          Material related code block.
        '''

        # materials
        if option.materials:
          for material in object.material_slots[:]:
            if material.material != None:
              if material.link == 'OBJECT':

                # material
                panel.blocks.material(self, context, layout, material, object, option)

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
      def vertexGroup(self, context, layout, object, option):
        '''
          Vertex group related code block.
        '''

        # vertex groups
        if option.vertexGroups:
          if hasattr(object, 'vertex_groups'):
            for group in object.vertex_groups[:]:

              # vertex group
              panel.vertexGroup(self, context, layout, group, object, option)

      # shapekey
      def shapekey(self, context, layout, object, option):
        '''
          Shapekey related code block.
        '''

        # shapekeys
        if option.shapekeys:
          if hasattr(object.data, 'shape_keys'):
            if hasattr(object.data.shape_keys, 'key_blocks'):
              for key in object.data.shape_keys.key_blocks[:]:

                # shapekey
                panel.shapekey(self, context, layout, key, object, option)

      # uv
      def uv(self, context, layout, object, option):
        '''
          UV related code block.
        '''

        # uvs
        if option.uvs:
          if object.type in 'MESH':
            for uv in object.data.uv_textures[:]:

              # uv
              panel.uv(self, context, layout, uv, object, option)

      # vertex color
      def vertexColor(self, context, layout, object, option):
        '''
          Vertex color related code block.
        '''

        # vertex colors
        if option.vertexColors:
          if object.type in 'MESH':
            for vertexColor in object.data.vertex_colors[:]:

              # vertex color
              panel.vertexColor(self, context, layout, vertexColor, object, option)

      # materials
      def material(self, context, layout, object, option):
        '''
          Material related code block.
        '''

        # materials
        if option.materials:
          for material in object.material_slots[:]:
            if material.material != None:
              if material.link == 'DATA':

                # material
                panel.blocks.material(self, context, layout, material, object, option)

      # bone groups
      def boneGroup(self, context, layout, object, option):
        '''
          Bone group related code block.
        '''

        # bone groups
        if option.boneGroups:
          if object.type in 'ARMATURE':
            for group in object.pose.bone_groups[:]:

              # bone group
              panel.boneGroup(self, context, layout, group, object)

    # bones
    def bone(self, context, layout, object, option):
      '''
        Bone related code block.
      '''

      # active bone
      if object.type in 'ARMATURE':
        if object.mode in {'POSE', 'EDIT'}:

          layout.separator()

          # bones
          if object.mode in 'POSE':
            bone = context.active_bone
          else:
            bone = context.active_bone

          panel.bone(self, context, layout, bone, object, option)

          # bone constraints
          if option.boneConstraints:
            if object.mode in 'POSE':
              bone = context.active_pose_bone
              for constraint in bone.constraints[:]:

                panel.constraint(self, context, layout, constraint, object, bone, option)

          # selected bones
          if option.selectedBones:

            # row
            row = layout.row()

            # separator
            row.separator()

            # edit mode
            if object.mode in 'POSE':
              bones = object.data.bones[:]

            # pose mode
            else:
              bones = object.data.edit_bones[:]

            # selected bones
            selectedBones = [
              # [name, object]
            ]

            for bone in bones:

              # pose mode
              if object.mode in 'POSE':
                if bone.select:
                  selectedBones.append([bone.name, bone])

              # edit mode
              else:
                if bone.select:
                  selectedBones.append([bone.name, bone])

            # sort and display
            for bone in sorted(selectedBones):
              if bone[1] != context.active_bone:

                # bone
                panel.bone(self, context, layout, bone[1], object, option)

                # bone constraints
                if option.boneConstraints:
                  if object.mode in 'POSE':
                    for constraint in object.pose.bones[bone[1].name].constraints[:]:

                      # constraint
                      panel.constraint(self, context, layout, constraint, object, bone[1], option)

                # row
                row = layout.row()

                # separator
                row.separator()
          else:

            # row
            row = layout.row()

            # separator
            row.separator()

    # material
    def material(self, context, layout, datablock, object, option):
      '''
        Material related code block.
      '''

      # material
      panel.material(self, context, layout, datablock, object)

      # textures
      if option.textures:
        if context.scene.render.engine not in 'CYCLES':
          for texture in datablock.material.texture_slots[:]:
            if texture != None:

              # texture
              panel.texture(self, context, layout, texture, object, option)

  # filters
  def filters(self, context, layout, option):
    '''
      The item panel filters
    '''

    # row
    row = layout.row(align=True)

    # scale
    row.scale_y = 1.25

    # icon toggle
    if option.filters:
      iconToggle = 'RADIOBUT_ON'
    else:
      iconToggle = 'RADIOBUT_OFF'

    # filters
    row.prop(option, 'filters', text='Filters', icon=iconToggle, toggle=True)

    # options
    row.prop(option, 'options', text='', icon='SETTINGS')

    # selected
    row.prop(option, 'selected', text='', icon='OOPS')

    # operator menu
    row.menu('VIEW3D_MT_item_panel_specials', text='', icon='COLLAPSEMENU')

    # filters
    if option.filters:

      # row 1
      row = layout.row(align=True)

      # scale
      row.scale_x = 5 # hack: forces buttons to line up correctly

      # groups
      row.prop(option, 'groups', text='', icon='GROUP')

      # action
      row.prop(option, 'action', text='', icon='ACTION')

      # grease pencil
      row.prop(option, 'greasePencil', text='', icon='GREASEPENCIL')

      # constraints
      row.prop(option, 'constraints', text='', icon='CONSTRAINT')

      # modifiers
      row.prop(option, 'modifiers', text='', icon='MODIFIER')

      # bone groups
      row.prop(option, 'boneGroups', text='', icon='GROUP_BONE')

      # bone constraints
      row.prop(option, 'boneConstraints', text='', icon='CONSTRAINT_BONE')

      # row 2
      row = layout.row(align=True)

      # scale
      row.scale_x = 5 # hack: forces buttons to line up correctly

      # vertex groups
      row.prop(option, 'vertexGroups', text='', icon='GROUP_VERTEX')

      # shapekeys
      row.prop(option, 'shapekeys', text='', icon='SHAPEKEY_DATA')

      # uvs
      row.prop(option, 'uvs', text='', icon='GROUP_UVS')

      # vertex colors
      row.prop(option, 'vertexColors', text='', icon='GROUP_VCOL')

      # materials
      row.prop(option, 'materials', text='', icon='MATERIAL')

      # textures
      row.prop(option, 'textures', text='', icon='TEXTURE')

      # particles systems
      row.prop(option, 'particleSystems', text='', icon='PARTICLES')

  # populate
  def populate(self, context, layout, object, option):
    '''
      Populates the item panel with datablock names.
    '''

    if object == context.active_object:

      # column
      column = layout.column()

      # separator
      column.separator()

      # object
      panel.object(self, context, column, object, option)

      # group
      panel.blocks.object.group(self, context, column, object, option)

      # action
      panel.blocks.object.action(self, context, column, object, option)

      # grease pencil
      panel.blocks.object.greasePencil(self, context, column, object, option)

      # constraint
      panel.blocks.object.constraint(self, context, column, object, option)

      # modifier
      panel.blocks.object.modifier(self, context, column, object, option)

      # material
      panel.blocks.object.material(self, context, column, object, option)

      # object data
      panel.objectData(self, context, column, object, option)

      # vertex group
      panel.blocks.objectData.vertexGroup(self, context, column, object, option)

      # shapekey
      panel.blocks.objectData.shapekey(self, context, column, object, option)

      # uv
      panel.blocks.objectData.uv(self, context, column, object, option)

      # vertex color
      panel.blocks.objectData.vertexColor(self, context, column, object, option)

      # material
      panel.blocks.objectData.material(self, context, column, object, option)

      # bone group
      panel.blocks.objectData.boneGroup(self, context, column, object, option)

      # bones
      panel.blocks.bone(self, context, column, object, option)

    else:
      if option.selected:

        # column
        column = layout.column()

        # separator
        column.separator()

        # object
        panel.object(self, context, column, object, option)

        # group
        panel.blocks.object.group(self, context, column, object, option)

        # action
        panel.blocks.object.action(self, context, column, object, option)

        # grease pencil
        panel.blocks.object.greasePencil(self, context, column, object, option)

        # constraint
        panel.blocks.object.constraint(self, context, column, object, option)

        # modifier
        panel.blocks.object.modifier(self, context, column, object, option)

        # material
        panel.blocks.object.material(self, context, column, object, option)

        # object data
        panel.objectData(self, context, column, object, option)

        # vertex group
        panel.blocks.objectData.vertexGroup(self, context, column, object, option)

        # shapekey
        panel.blocks.objectData.shapekey(self, context, column, object, option)

        # uv
        panel.blocks.objectData.uv(self, context, column, object, option)

        # vertex color
        panel.blocks.objectData.vertexColor(self, context, column, object, option)

        # material
        panel.blocks.objectData.material(self, context, column, object, option)

        # bone group
        panel.blocks.objectData.boneGroup(self, context, column, object, option)

  # object
  def object(self, context, layout, datablock, option):
    '''
      The object.
    '''

    # active object
    if datablock == context.active_object:

      # row
      row = layout.row(align=True)

      # template
      row.template_ID(context.scene.objects, 'active')

    # selected object
    else:

      # row
      row = layout.row(align=True)

      # sub
      sub = row.row(align=True)

      # scale
      sub.scale_x = 1.6

      # make active
      sub.operator('view3d.make_active_object', text='', icon=icon.object(datablock)).target = datablock.name

      # object
      row.prop(datablock, 'name', text='')

      # options
      if option.options:

        # hide
        row.prop(datablock, 'hide', text='')

        # hide select
        row.prop(datablock, 'hide_select', text='')

        # hide render
        row.prop(datablock, 'hide_render', text='')

  # group
  def group(self, context, layout, datablock, object):
    '''
      The object group.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    sub.label(text='', icon='GROUP')

    # name
    row.prop(datablock, 'name', text='')


  # action
  def action(self, context, layout, datablock, object):
    '''
      The object action.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    sub.label(text='', icon='ACTION')

    # name
    row.prop(datablock, 'name', text='')

  # grease pencil
  def greasePencil(self, context, layout, datablock, object):
    '''
      The object grease pencil.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    sub.label(text='', icon='GREASEPENCIL')

    # name
    row.prop(datablock, 'name', text='')

  # pencil layer
  def pencilLayer(self, context, layout, datablock, object, option):
    '''
      The object pencil layer.
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
    if option.options:

      # lock
      row.prop(datablock, 'lock', text='')

      # hide
      row.prop(datablock, 'hide', text='')

  # constraint
  def constraint(self, context, layout, datablock, object, bone, option):
    '''
      The object or pose bone constraint.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    sub.label(text='', icon='CONSTRAINT')

    # name
    row.prop(datablock, 'name', text='')

    # options
    if option.options:

      # influence
      if datablock.type not in {'RIGID_BODY_JOINT', 'NULL'}:

        # sub
        sub = row.row(align=True)

        # scale
        sub.scale_x = 0.17

        # influence
        sub.prop(datablock, 'influence', text='')

      # icon view
      if datablock.mute:
        iconView = 'RESTRICT_VIEW_ON'
      else:
        iconView = 'RESTRICT_VIEW_OFF'

      # mute
      row.prop(datablock, 'mute', text='', icon=iconView)

    # modal
    prop = row.operator('view3d.constraint_settings', text='', icon='COLLAPSEMENU')
    prop.object = object.name
    if object.type in 'ARMATURE' and object.mode in 'POSE':
      prop.bone = bone.name
    prop.target = datablock.name

  # modifier
  def modifier(self, context, layout, datablock, object, option):
    '''
      The object modifier.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    sub.label(text='', icon=icon.modifier(datablock))

    # name
    row.prop(datablock, 'name', text='')

    # options
    if option.options:
      if datablock.type not in {'COLLISION', 'SOFT_BODY'}:

        # icon render
        if datablock.show_render:
          iconRender = 'RESTRICT_RENDER_OFF'
        else:
          iconRender = 'RESTRICT_RENDER_ON'

        # show render
        row.prop(datablock, 'show_render', text='', icon=iconRender)

        # icon view
        if datablock.show_viewport:
          iconView = 'RESTRICT_VIEW_OFF'
        else:
          iconView = 'RESTRICT_VIEW_ON'

        # show viewport
        row.prop(datablock, 'show_viewport', text='', icon=iconView)

    # modal
    prop = row.operator('view3d.modifier_settings', text='', icon='COLLAPSEMENU')
    prop.object = object.name
    prop.target = datablock.name

  # object data
  def objectData(self, context, layout, datablock, option):
    '''
      The object data.
    '''

    # row
    row = layout.row(align=True)

    # empty
    if datablock.type in 'EMPTY':

      # empty image draw type
      if datablock.empty_draw_type in 'IMAGE':

        # image
        row.template_ID(datablock, 'data', open='image.open', unlink='image.unlink')

    else:

      # active
      if datablock == context.active_object:

        # name
        row.template_ID(datablock, 'data')

      # selected
      else:

        # name
        row.prop(datablock.data, 'name', text='', icon=icon.objectData(datablock))

  # vertex group
  def vertexGroup(self, context, layout, datablock, object, option):
    '''
      The object data vertex group.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    # sub.label(text='', icon='GROUP_VERTEX')

    # select vertex group
    prop = sub.operator('object.select_vertex_group', text='', icon='GROUP_VERTEX', emboss=False)
    prop.object = object.name
    prop.target = datablock.name

    # name
    row.prop(datablock, 'name', text='')

    # options
    if option.options:

      # icon lock
      if datablock.lock_weight:
        iconLock = 'LOCKED'
      else:
        iconLock = 'UNLOCKED'

      # lock weight
      row.prop(datablock, 'lock_weight', text='', icon=iconLock)

  # shapekey
  def shapekey(self, context, layout, datablock, object, option):
    '''
      The object animation data data shapekey.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    sub.label(text='', icon='SHAPEKEY_DATA')

    # name
    row.prop(datablock, 'name', text='')

    # options
    if option.options:
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
  def uv(self, context, layout, datablock, object, option):
    '''
      The object data uv.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    sub.label(text='', icon='GROUP_UVS')

    # name
    row.prop(datablock, 'name', text='')

    # options
    if option.options:

      # icon active
      if datablock.active_render:
        iconActive = 'RESTRICT_RENDER_OFF'
      else:
        iconActive = 'RESTRICT_RENDER_ON'

      # active render
      row.prop(datablock, 'active_render', text='', icon=iconActive)

  # vertex color
  def vertexColor(self, context, layout, datablock, object, option):
    '''
      The object data vertex color.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    sub.label(text='', icon='GROUP_VCOL')

    # name
    row.prop(datablock, 'name', text='')

    # options
    if option.options:

      # icon active
      if datablock.active_render:
        iconActive = 'RESTRICT_RENDER_OFF'
      else:
        iconActive = 'RESTRICT_RENDER_ON'

      # active_render
      row.prop(datablock, 'active_render', text='', icon=iconActive)

  # material
  def material(self, context, layout, datablock, object):
    '''
      The object material.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    sub.label(text='', icon='MATERIAL')

    # name
    row.prop(datablock.material, 'name', text='')

  # texture
  def texture(self, context, layout, datablock, object, option):
    '''
      The object material texture.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    sub.label(text='', icon='TEXTURE')

    # name
    row.prop(datablock.texture, 'name', text='')

    # options
    if option.options:

      # icon toggle
      if datablock.use:
        iconToggle = 'RADIOBUT_ON'
      else:
        iconToggle = 'RADIOBUT_OFF'

      # use
      row.prop(datablock, 'use', text='', icon=iconToggle)

  # particle
  def particle(self, context, layout, datablock, object, option):
    '''
      The modifier particle system and settings.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    sub.label(text='', icon='PARTICLES')

    # name
    row.prop(datablock.particle_system, 'name', text='')

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    sub.label(text='', icon='DOT')

    # name
    row.prop(datablock.particle_system.settings, 'name', text='')

  # bone group
  def boneGroup(self, context, layout, datablock, object):
    '''
      The object data bone group.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale
    sub.scale_x = 1.6

    # label
    sub.label(text='', icon='GROUP_BONE')

    # name
    row.prop(datablock, 'name', text='')

  # bone
  def bone(self, context, layout, datablock, object, option):
    '''
      The object data bone.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row(align=True)

    # scale
    sub.scale_x = 1.6

    # active
    if datablock == context.active_bone:

      # selected bones
      sub.prop(option, 'selectedBones', text='', icon='BONE_DATA')

    # selected
    # else:
    #   sub.label(text='', icon='BONE_DATA')

    # pose mode
    if object.mode in 'POSE':

      # name
      if not datablock == context.active_bone:

        # make active bone
        sub.operator('view3d.make_active_bone', text='', icon='BONE_DATA').target = datablock.name

        row.prop(datablock, 'name', text='')
      else:
        row.prop(datablock, 'name', text='')

      # options
      if option.options:

        # icon view
        if datablock.hide:
          iconView = 'RESTRICT_VIEW_ON'
        else:
          iconView = 'RESTRICT_VIEW_OFF'

        # hide
        row.prop(datablock, 'hide', text='', icon=iconView)

        # icon hide select
        if datablock.hide_select:
          iconSelect = 'RESTRICT_SELECT_ON'
        else:
          iconSelect = 'RESTRICT_SELECT_OFF'

        # hide select
        row.prop(datablock, 'hide_select', text='', icon=iconSelect)

    # edit mode
    else:

      # name
      if not datablock == context.active_bone:

        # make active bone
        sub.operator('view3d.make_active_bone', text='', icon='BONE_DATA').target = datablock.name
      row.prop(datablock, 'name', text='')

      # options
      if option.options:

        # icon view
        if datablock.hide:
          iconView = 'RESTRICT_VIEW_ON'
        else:
          iconView = 'RESTRICT_VIEW_OFF'

        # hide
        row.prop(datablock, 'hide', text='', icon=iconView)

        # icon select
        if datablock.hide_select:
          iconSelect = 'RESTRICT_SELECT_ON'
        else:
          iconSelect = 'RESTRICT_SELECT_OFF'

        # hide select
        row.prop(datablock, 'hide_select', text='', icon=iconSelect)

        # icon lock
        if datablock.lock:
          iconLock = 'LOCKED'
        else:
          iconLock = 'UNLOCKED'

        # lock
        row.prop(datablock, 'lock', text='', icon=iconLock)
