
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
import re
from random import random
from .. import storage

tag = False

# shared
class shared:
  '''
    Contains Lists;
      greasePencils
      objectData
      materials
      textures
  '''

  # grease pencils
  greasePencils = []

  particleSettings = []

  # object data
  objectData = []

  # materials
  materials = []

  # textures
  textures = []

# main
def main(context, quickBatch):
  '''
    Send datablock values to populate then send collections to process, action group & lineset names are sent to name.
  '''

  # tag
  global tag

  # panel
  panel = context.scene.NamePanel

  # option
  option = context.scene.BatchName

  # quick batch
  if quickBatch:

    # display names
    if panel.displayNames:

      # mode
      if panel.mode == 'SELECTED':

        for object in context.selected_objects[:]:

          # quick
          quick(context, object, panel, option)

      # mode
      else:
        for object in context.scene.objects[:]:
          if True in [x&y for (x,y) in zip(object.layers, context.scene.layers)]:

            # quick
            quick(context, object, panel, option)

    # display names
    else:

      # quick
      quick(context, context.active_object, panel, option)

    # all
    all = [
      # groups
      storage.batch.groups,

      # actions
      storage.batch.actions,

      # grease pencil
      storage.batch.greasePencils,

      # object
      storage.batch.objects,

      # cameras
      storage.batch.cameras,

      # meshes
      storage.batch.meshes,

      # curves
      storage.batch.curves,

      # lamps
      storage.batch.lamps,

      # lattices
      storage.batch.lattices,

      # metaballs
      storage.batch.metaballs,

      # speakers
      storage.batch.speakers,

      # armatures
      storage.batch.armatures,

      # bones
      storage.batch.bones,

      # materials
      storage.batch.materials,

      # textures
      storage.batch.textures,

      # particle settings
      storage.batch.particleSettings
    ]

    # process
    for collection in all:
      if collection != []:

        # clear duplicates
        list = []
        [list.append(item) for item in collection if item not in list]

        # process
        process(context, list)

        # clear storage
        collection.clear()

  # quick batch
  else:

    # mode
    if option.mode in {'SELECTED', 'OBJECTS'}:

      # actions
      if option.actions:
        for object in bpy.data.objects[:]:
          if hasattr(object.animation_data, 'action'):

            # mode
            if option.mode in 'SELECTED':
              if object.select:

                # object type
                if option.objectType in 'ALL':

                  # populate
                  populate(context, object.animation_data.action, object.animation_data)

                # object type
                elif option.objectType in object.type:

                  # populate
                  populate(context, object.animation_data.action, object.animation_data)

            # mode
            else:

              # object type
              if option.objectType in 'ALL':

                # populate
                populate(context, object.animation_data.action, object.animation_data)

              # object type
              elif option.objectType in object.type:

                # populate
                populate(context, object.animation_data.action, object.animation_data)

        # clear duplicates
        actions = []
        [actions.append(item) for item in storage.batch.actions if item not in actions]
        storage.batch.actions.clear()

        # process
        process(context, actions)

      # action groups
      if option.actionGroups:
        for object in bpy.data.objects[:]:
          if hasattr(object.animation_data, 'action'):
            if hasattr(object.animation_data.action, 'name'):

              # mode
              if option.mode in 'SELECTED':
                if object.select:

                  # object type
                  if option.objectType in 'ALL':

                    # populate
                    populate(context, object.animation_data.action)

                  # object type
                  elif option.objectType in object.type:

                    # populate
                    populate(context, object.animation_data.action)

              # mode
              else:

                # object type
                if option.objectType in 'ALL':

                  # populate
                  populate(context, object.animation_data.action)

                # object type
                elif option.objectType in object.type:

                  # populate
                  populate(context, object.animation_data.action)

        # clear duplicates
        actions = []
        [actions.append(item) for item in storage.batch.actions if item not in actions]
        storage.batch.actions.clear()

        # name action groups
        for action in actions:
          for group in action[1][1].groups:
            group.name = name(context, group.name) if not option.suffixLast else name(context, group.name) + option.suffix

      # grease pencil
      if option.greasePencil:
        for object in bpy.data.objects[:]:
          if hasattr(object.grease_pencil, 'name'):

            # mode
            if option.mode in 'SELECTED':
              if object.select:

                # object type
                if option.objectType in 'ALL':
                  if object.grease_pencil.users == 1:

                    # populate
                    populate(context, object.grease_pencil, object)
                  else:

                    # shared
                    if object.grease_pencil not in shared.greasePencils[:]:
                      shared.greasePencils.append(object.grease_pencil)

                      # populate
                      populate(context, object.grease_pencil, object)

                # object type
                elif option.objectType in object.type:
                  if object.grease_pencil.users == 1:

                    # populate
                    populate(context, object.grease_pencil, object)
                  else:

                    # shared
                    if object.grease_pencil not in shared.greasePencils[:]:
                      shared.greasePencils.append(object.grease_pencil)

                      # populate
                      populate(context, object.grease_pencil, object)

            # mode
            else:

              # object type
              if option.objectType in 'ALL':
                if object.grease_pencil.users == 1:

                  # populate
                  populate(context, object.grease_pencil, object)
                else:

                  # shared
                  if object.grease_pencil not in shared.greasePencils[:]:
                    shared.greasePencils.append(object.grease_pencil)

                    # populate
                    populate(context, object.grease_pencil, object)

              # object type
              elif option.objectType in object.type:
                if object.grease_pencil.users == 1:

                  # populate
                  populate(context, object.grease_pencil, object)

                else:

                  # shared
                  if object.grease_pencil not in shared.greasePencils[:]:
                    shared.greasePencils.append(object.grease_pencil)

                    # populate
                    populate(context, object.grease_pencil, object)


        # process
        process(context, storage.batch.greasePencils)

        # clear storage
        storage.batch.greasePencils.clear()

        # clear shared
        shared.greasePencils.clear()

      # pencil layers
      if option.pencilLayers:
        for object in bpy.data.objects[:]:
          if hasattr(object.grease_pencil, 'name'):

            # mode
            if option.mode in 'SELECTED':
              if object.select:

                # object type
                if option.objectType in 'ALL':
                  if object.grease_pencil.users == 1:

                    # layers
                    for layer in object.grease_pencil.layers[:]:

                      # populate
                      populate(context, layer)
                  else:

                    # shared
                    if object.grease_pencil not in shared.greasePencils[:]:
                      shared.greasePencils.append(object.grease_pencil)

                      # layers
                      for layer in object.grease_pencil.layers[:]:

                        # populate
                        populate(context, layer)

                # object type
                elif option.objectType in object.type:
                  if object.grease_pencil.users == 1:

                    # layers
                    for layer in object.grease_pencil.layers[:]:

                      # populate
                      populate(context, layer)
                  else:

                    # shared
                    if object.grease_pencil not in shared.greasePencils[:]:
                      shared.greasePencils.append(object.grease_pencil)

                      # layers
                      for layer in object.grease_pencil.layers[:]:

                        # populate
                        populate(context, layer)

            # mode
            else:

              # object type
              if option.objectType in 'ALL':
                if object.grease_pencil.users == 1:

                  # layers
                  for layer in object.grease_pencil.layers[:]:

                    # populate
                    populate(context, layer)
                else:

                  # shared
                  if object.grease_pencil not in shared.greasePencils[:]:
                    shared.greasePencils.append(object.grease_pencil)

                    # layers
                    for layer in object.grease_pencil.layers[:]:

                      # populate
                      populate(context, layer)

              # object type
              elif option.objectType in object.type:
                if object.grease_pencil.users == 1:

                  # layers
                  for layer in object.grease_pencil.layers[:]:

                    # populate
                    populate(context, layer)
                else:

                  # shared
                  if object.grease_pencil not in shared.greasePencils[:]:
                    shared.greasePencils.append(object.grease_pencil)

                    # layers
                    for layer in object.grease_pencil.layers[:]:

                      # populate
                      populate(context, layer)

            # process
            process(context, storage.batch.pencilLayers)

            # clear storage
            storage.batch.pencilLayers.clear()

        # clear shared
        shared.greasePencils.clear()

      # objects
      if option.objects:
        for object in bpy.data.objects[:]:

          # mode
          if option.mode in 'SELECTED':
            if object.select:

              # object type
              if option.objectType in 'ALL':

                # populate
                populate(context, object)

              # object type
              elif option.objectType in object.type:

                # populate
                populate(context, object)

          # mode
          else:

            # object type
            if option.objectType in 'ALL':

              # populate
              populate(context, object)

            # object type
            elif option.objectType in object.type:

              # populate
              populate(context, object)

        # process
        process(context, storage.batch.objects)

        # clear storage
        storage.batch.objects.clear()

      # groups
      if option.groups:
        for object in bpy.data.objects[:]:

          # mode
          if option.mode in 'SELECTED':
            if object.select:

              # object type
              if option.objectType in 'ALL':
                for group in bpy.data.groups[:]:
                  if object in group.objects[:]:

                    # populate
                    populate(context, group)


              # object type
              elif option.objectType in object.type:
                for group in bpy.data.groups[:]:
                  if object in group.objects[:]:

                    # populate
                    populate(context, group)

          # mode
          else:

            # object type
            if option.objectType in 'ALL':
              for group in bpy.data.groups[:]:
                if object in group.objects[:]:

                  # populate
                  populate(context, group)

            # object type
            elif option.objectType in object.type:
              for group in bpy.data.groups[:]:
                if object in group.objects[:]:

                  # populate
                  populate(context, group)

        # clear duplicates
        objectGroups = []
        [objectGroups.append(item) for item in storage.batch.groups if item not in objectGroups]

        # clear storage
        storage.batch.groups.clear()

        # process
        process(context, objectGroups)

      # constraints
      if option.constraints:
        for object in bpy.data.objects[:]:

          # mode
          if option.mode in 'SELECTED':
            if object.select:
              for constraint in object.constraints[:]:

                # constraint type
                if option.constraintType in 'ALL':

                  # populate
                  populate(context, constraint)

                # constraint type
                elif option.constraintType in constraint.type:

                  # populate
                  populate(context, constraint)

          # mode
          else:
            for constraint in object.constraints[:]:

              # constraint type
              if option.constraintType in 'ALL':

                # populate
                populate(context, constraint)

              # constraint type
              elif option.constraintType in constraint.type:

                # populate
                populate(context, constraint)

          # process
          process(context, storage.batch.constraints)

          # clear storage
          storage.batch.constraints.clear()

      # modifiers
      if option.modifiers:
        for object in bpy.data.objects[:]:

          # mode
          if option.mode in 'SELECTED':
            if object.select:
              for modifier in object.modifiers[:]:

                # modifier type
                if option.modifierType in 'ALL':

                  # populate
                  populate(context, modifier)

                # modifier tye
                elif option.modifierType in modifier.type:

                  # populate
                  populate(context, modifier)

          # mode
          else:
            for modifier in object.modifiers[:]:

              # modifier type
              if option.modifierType in 'ALL':

                # populate
                populate(context, modifier)

              # modifier tye
              elif option.modifierType in modifier.type:

                # populate
                populate(context, modifier)

          # process
          process(context, storage.batch.modifiers)

          # clear storage
          storage.batch.modifiers.clear()

      # object data
      if option.objectData:
        for object in bpy.data.objects[:]:
          if object.type not in 'EMPTY':

            # mode
            if option.mode in 'SELECTED':
              if object.select:

                # object type
                if option.objectType in 'ALL':
                  if object.data.users == 1:

                    # populate
                    populate(context, object.data, object)
                  else:

                    # shared
                    if object.data.name not in shared.objectData[:]:
                      shared.objectData.append(object.data.name)

                      # populate
                      populate(context, object.data, object)

                # object type
                elif option.objectType in object.type:
                  if object.data.users == 1:

                    # populate
                    populate(context, object.data, object)
                  else:

                    # shared shared
                    if object.data.name not in shared.objectData[:]:
                      shared.objectData.append(object.data.name)

                      # populate
                      populate(context, object.data, object)

            # mode
            else:

              # object type
              if option.objectType in 'ALL':
                if object.data.users == 1:

                  # populate
                  populate(context, object.data, object)
                else:

                  # shared shared
                  if object.data.name not in shared.objectData[:]:
                    shared.objectData.append(object.data.name)

                    # populate
                    populate(context, object.data, object)

              # object type
              elif option.objectType in object.type:
                if object.data.users == 1:

                  # populate
                  populate(context, object.data, object)
                else:

                  # shared shared
                  if object.data.name not in shared.objectData[:]:
                    shared.objectData.append(object.data.name)

                    # populate
                    populate(context, object.data, object)

        # clear shared
        shared.objectData.clear()

        # object data
        objectData = [
          storage.batch.curves,
          storage.batch.cameras,
          storage.batch.meshes,
          storage.batch.lamps,
          storage.batch.lattices,
          storage.batch.metaballs,
          storage.batch.speakers,
          storage.batch.armatures
        ]

        # process collection
        for collection in objectData:
          if collection != []:

            # process
            process(context, collection)

            # clear storage
            collection.clear()

      # bone groups
      if option.boneGroups:
        for object in bpy.data.objects[:]:

          # mode
          if option.mode in 'SELECTED':
            if object.select:
              if object.type in 'ARMATURE':
                for group in object.pose.bone_groups[:]:
                  if object.select:

                    # populate
                    populate(context, group)

          # mode
          else:
            if object.type in 'ARMATURE':
              for group in object.pose.bone_groups[:]:

                # populate
                populate(context, group)

          # process
          process(context, storage.batch.boneGroups)

          # clear storage
          storage.batch.boneGroups.clear()

      # bones
      if option.bones:
        for object in bpy.data.objects[:]:
          if object.type in 'ARMATURE':

            # mode
            if option.mode in 'SELECTED':
              if object.select:

                # edit mode
                if object.mode in 'EDIT':
                  for bone in bpy.data.armatures[object.data.name].edit_bones[:]:
                    if bone.select:

                      # populate
                      populate(context, bone)

                # pose or object mode
                else:
                  for bone in bpy.data.armatures[object.data.name].bones[:]:
                    if bone.select:

                      # populate
                      populate(context, bone)

            # mode
            else:

              # edit mode
              if object.mode in 'EDIT':
                for bone in bpy.data.armatures[object.data.name].edit_bones[:]:

                    # populate
                    populate(context, bone)

              # pose or object mode
              else:
                for bone in bpy.data.armatures[object.data.name].bones[:]:

                    # populate
                    populate(context, bone)

            # process
            process(context, storage.batch.bones)

            # clear storage
            storage.batch.bones.clear()

      # bone constraints
      if option.boneConstraints:
        for object in bpy.data.objects[:]:
          if object.type in 'ARMATURE':

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for bone in object.pose.bones[:]:
                  if bone.bone.select:
                    for constraint in bone.constraints[:]:

                      # constraint type
                      if option.constraintType in 'ALL':

                        # populate
                        populate(context, constraint)

                      # constraint type
                      elif option.constraintType in constraint.type:

                        # populate
                        populate(context, constraint)

                    # process
                    process(context, storage.batch.constraints)

                    # clear storage
                    storage.batch.constraints.clear()

            # mode
            else:
              for bone in object.pose.bones[:]:
                for constraint in bone.constraints[:]:

                  # constraint type
                  if option.constraintType in 'ALL':

                    # populate
                    populate(context, constraint)

                  # constraint type
                  elif option.constraintType in constraint.type:

                    # populate
                    populate(context, constraint)

                # process
                process(context, storage.batch.constraints)

                # clear storage
                storage.batch.constraints.clear()

      # vertex groups
      if option.vertexGroups:
        for object in bpy.data.objects[:]:
          if hasattr(object, 'vertex_groups'):

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for group in object.vertex_groups[:]:

                  # object type
                  if option.objectType in 'ALL':

                    # populate
                    populate(context, group)

                  # object type
                  elif option.objectType in object.type:

                    # populate
                    populate(context, group)

                # process
                process(context, storage.batch.vertexGroups)

                # clear storage
                storage.batch.vertexGroups.clear()

            # mode
            else:
              for group in object.vertex_groups[:]:

                # object type
                if option.objectType in 'ALL':

                  # populate
                  populate(context, group)

                # object type
                elif option.objectType in object.type:

                  # populate
                  populate(context, group)

              # process
              process(context, storage.batch.vertexGroups)

              # clear storage
              storage.batch.vertexGroups.clear()


      # shapekeys
      if option.shapekeys:
        for object in bpy.data.objects[:]:
          if hasattr(object.data, 'shape_keys'):
            if hasattr(object.data.shape_keys, 'key_blocks'):

              # mode
              if option.mode in 'SELECTED':
                if object.select:
                  for block in object.data.shape_keys.key_blocks[:]:

                    # object type
                    if option.objectType in 'ALL':

                      # populate
                      populate(context, block)

                    # object type
                    elif option.objectType in object.type:

                      # populate
                      populate(context, block)

              # mode
              else:
                for block in object.data.shape_keys.key_blocks[:]:

                  # object type
                  if option.objectType in 'ALL':

                    # populate
                    populate(context, block)

                  # object type
                  elif option.objectType in object.type:

                    # populate
                    populate(context, block)

              # process
              process(context, storage.batch.shapekeys)

              # clear storage
              storage.batch.shapekeys.clear()

      # uvs
      if option.uvs:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for uv in object.data.uv_textures[:]:

                  # populate
                  populate(context, uv)

            # mode
            else:
             for uv in object.data.uv_textures[:]:

                # populate
                populate(context, uv)

            # process
            process(context, storage.batch.uvs)

            # clear storage
            storage.batch.uvs.clear()

      # vertex colors
      if option.vertexColors:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for color in object.data.vertex_colors[:]:

                  # populate
                  populate(context, color)

            # mode
            else:
              for color in object.data.vertex_colors[:]:

                # populate
                populate(context, color)

            # process
            process(context, storage.batch.vertexColors)

            # clear storage
            storage.batch.vertexColors.clear()

      # materials
      if option.materials:
        for object in bpy.data.objects[:]:

          # mode
          if option.mode in 'SELECTED':
            if object.select:
              for slot in object.material_slots[:]:
                if slot.material != None:
                  if slot.material.users == 1:

                    # object type
                    if option.objectType in 'ALL':

                      # populate
                      populate(context, slot.material, slot)

                    # object type
                    elif option.objectType in object.type:

                      # populate
                      populate(context, slot.material, slot)
                  else:

                    # shared
                    if slot.material not in shared.materials[:]:
                      shared.materials.append(slot.material)

                      # populate
                      populate(context, slot.material, slot)

          # mode
          else:
            for slot in object.material_slots[:]:
              if slot.material != None:
                if slot.material.users == 1:

                  # object type
                  if option.objectType in 'ALL':

                    # populate
                    populate(context, slot.material, slot)

                  # object type
                  elif option.objectType in object.type:

                    # populate
                    populate(context, slot.material, slot)
                else:

                  # shared
                  if slot.material not in shared.materials[:]:
                    shared.materials.append(slot.material)

                    # populate
                    populate(context, slot.material, slot)

        # process
        process(context, storage.batch.materials)

        # clear storage
        storage.batch.materials.clear()

        # clear shared
        shared.materials.clear()

      # textures
      if option.textures:
        for object in bpy.data.objects[:]:
          if context.scene.render.engine not in 'CYCLES':

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for slot in object.material_slots[:]:
                  if slot.material != None:
                    if slot.material.users == 1:
                      for texslot in slot.material.texture_slots[:]:
                        if texslot != None:
                          if texslot.texture.users == 1:

                            # object type
                            if option.objectType in 'ALL':

                              # populate
                              populate(context, texslot.texture, texslot)

                            # object type
                            elif option.objectType in object.type:

                              # populate
                              populate(context, texslot.texture, texslot)
                          else:

                            # shared
                            if texslot.texture not in shared.textures[:]:
                              shared.textures.append(texslot.texture)

                              # populate
                              populate(context, texslot.texture, texslot)
                    else:

                      # shared
                      if slot.material not in shared.materials[:]:
                        shared.materials.append(slot.material)
                        for texslot in slot.material.texture_slots[:]:
                          if texslot != None:
                            if texslot.texture.users == 1:

                              # object type
                              if option.objectType in 'ALL':

                                # populate
                                populate(context, texslot.texture, texslot)

                              # object type
                              elif option.objectType in object.type:

                                # populate
                                populate(context, texslot.texture, texslot)
                            else:

                              # shared
                              if texslot.texture not in shared.textures[:]:
                                shared.textures.append(texslot.texture)

                                # populate
                                populate(context, texslot.texture, texslot)

                    # process
                    process(context, storage.batch.textures)

                    # clear storage
                    storage.batch.textures.clear()

            # mode
            else:
              for slot in object.material_slots[:]:
                if slot.material != None:
                  if slot.material.users == 1:
                    for texslot in slot.material.texture_slots[:]:
                      if texslot != None:
                        if texslot.texture.users == 1:

                          # object type
                          if option.objectType in 'ALL':

                            # populate
                            populate(context, texslot.texture, texslot)

                          # object type
                          elif option.objectType in object.type:

                            # populate
                            populate(context, texslot.texture, texslot)
                        else:

                          # shared
                          if texslot.texture not in shared.textures[:]:
                            shared.textures.append(texslot.texture)

                            # populate
                            populate(context, texslot.texture, texslot)
                  else:

                    # shared
                    if slot.material not in shared.materials[:]:
                      shared.materials.append(slot.material)
                      for texslot in slot.material.texture_slots[:]:
                        if texslot != None:
                          if texslot.texture.users == 1:

                            # object type
                            if option.objectType in 'ALL':

                              # populate
                              populate(context, texslot.texture, texslot)

                            # object type
                            elif option.objectType in object.type:

                              # populate
                              populate(context, texslot.texture, texslot)
                          else:

                            # shared
                            if texslot.texture not in shared.textures[:]:
                              shared.textures.append(texslot.texture, texslot)

                              # populate
                              populate(context, texslot.texture, texslot)

        # process
        process(context, storage.batch.textures)

        # clear storage
        storage.batch.textures.clear()

        # clear shared
        shared.textures.clear()

      # particle systems
      if option.particleSystems:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for system in object.particle_systems[:]:

                  # object type
                  if option.objectType in 'ALL':

                    # populate
                    populate(context, system)

                  # object type
                  elif option.objectType in object.type:

                    # populate
                    populate(context, system)

            # mode
            else:
              for system in object.particle_systems[:]:

                # object type
                if option.objectType in 'ALL':

                  # populate
                  populate(context, system)

                # object type
                elif option.objectType in object.type:

                  # populate
                  populate(context, system)

            # process
            process(context, storage.batch.particleSystems)

            # clear storage
            storage.batch.particleSystems.clear()

      # particle settings
      if option.particleSettings:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for system in object.particle_systems[:]:

                  # object type
                  if option.objectType in 'ALL':
                    if system.settings.users == 1:

                      # populate
                      populate(context, system.settings, system)
                    else:

                      # shared
                      if system.settings not in shared.particleSettings[:]:
                        shared.particleSettings.append(system.settings)

                        # populate
                        populate(context, system.settings, system)

                  # object type
                  elif option.objectType in object.type:
                    if system.settings.users == 1:

                      # populate
                      populate(context, system.settings, system)
                    else:

                      # shared
                      if system.settings not in shared.particleSettings[:]:
                        shared.particleSettings.append(system.settings)

                        # populate
                        populate(context, system.settings, system)

            # mode
            else:
              for system in object.particle_systems[:]:

                # object type
                if option.objectType in 'ALL':
                  if system.settings.users == 1:

                    # populate
                    populate(context, system.settings, system)
                  else:

                    # shared
                    if system.settings not in shared.particleSettings[:]:
                      shared.particleSettings.append(system.settings)

                      # populate
                      populate(context, system.settings, system)

                # object type
                elif option.objectType in object.type:
                  if system.settings.users == 1:

                    # populate
                    populate(context, system.settings, system)
                  else:

                    # shared
                    if system.settings not in shared.particleSettings[:]:
                      shared.particleSettings.append(system.settings)

                      # populate
                      populate(context, system.settings, system)

        # process
        process(context, storage.batch.particleSettings)

        # clear storage
        storage.batch.particleSettings.clear()

        # clear shared
        shared.particleSettings.clear()

    # sensors
    if option.sensors:
      for object in bpy.data.objects[:]:

        # mode
        if option.mode in 'SELECTED':
          if object.select:

            # object type
            if option.objectType in 'ALL':

              # populate
              for sensor in object.game.sensors[:]:
                populate(context, sensor)

            # object type
            elif option.objectType in object.type:

              # populate
              for sensor in object.game.sensors[:]:
                populate(context, sensor)

        # mode
        else:

          # object type
          if option.objectType in 'ALL':

            # populate
            for sensor in object.game.sensors[:]:
              populate(context, sensor)

          # object type
          elif option.objectType in object.type:

            # populate
            for sensor in object.game.sensors[:]:
              populate(context, sensor)

        # process
        process(context, storage.batch.sensors)

        # clear storage
        storage.batch.sensors.clear()

    # controllers
    if option.controllers:
      for object in bpy.data.objects[:]:

        # mode
        if option.mode in 'SELECTED':
          if object.select:

            # object type
            if option.objectType in 'ALL':

              # populate
              for controller in object.game.controllers[:]:
                populate(context, controller)

            # object type
            elif option.objectType in object.type:

              # populate
              for controller in object.game.controllers[:]:
                populate(context, controller)

        # mode
        else:

          # object type
          if option.objectType in 'ALL':

            # populate
            for controller in object.game.controllers[:]:
              populate(context, controller)

          # object type
          elif option.objectType in object.type:

            # populate
            for controller in object.game.controllers[:]:
              populate(context, controller)

        # process
        process(context, storage.batch.controllers)

        # clear storage
        storage.batch.controllers.clear()

    # actuators
    if option.actuators:
      for object in bpy.data.objects[:]:

        # mode
        if option.mode in 'SELECTED':
          if object.select:

            # object type
            if option.objectType in 'ALL':

              # populate
              for actuator in object.game.actuators[:]:
                populate(context, actuator)

            # object type
            elif option.objectType in object.type:

              # populate
              for actuator in object.game.actuators[:]:
                populate(context, actuator)

        # mode
        else:

          # object type
          if option.objectType in 'ALL':

            # populate
            for actuator in object.game.actuators[:]:
              populate(context, actuator)

          # object type
          elif option.objectType in object.type:

            # populate
            for actuator in object.game.actuators[:]:
              populate(context, actuator)

        # process
        process(context, storage.batch.actuators)

        # clear storage
        storage.batch.actuators.clear()

    # mode
    if option.mode in 'SCENE':

      # actions
      if option.actions:
        for object in context.scene.objects[:]:
          if hasattr(object.animation_data, 'action'):
            if hasattr(object.animation_data.action, 'name'):

              # object type
              if option.objectType in 'ALL':

                # populate
                populate(context, object.animation_data.action, object.animation_data)

              # object type
              elif option.objectType in object.type:

                # populate
                populate(context, object.animation_data.action, object.animation_data)

        # clear duplicates
        actions = []
        [actions.append(item) for item in storage.batch.actions if item not in actions]

        # clear storage
        storage.batch.actions.clear()

        # process
        process(context, actions)

      # action groups
      if option.actionGroups:
        for object in context.scene.objects[:]:
          if hasattr(object.animation_data, 'action'):
            if hasattr(object.animation_data.action, 'name'):

              # object type
              if option.objectType in 'ALL':

                # populate
                populate(context, object.animation_data.action)

              # object type
              elif option.objectType in object.type:

                # populate
                populate(context, object.animation_data.action)

        # clear duplicates
        actions = []
        [actions.append(item) for item in storage.batch.actions if item not in actions]
        storage.batch.actions.clear()

        # name action groups
        for action in actions:
          for group in action[1][1].groups:
            group.name = name(context, group.name) if not option.suffixLast else name(context, group.name) + option.suffix

      # grease pencil
      if option.greasePencil:
        for object in context.scene.objects[:]:
          if hasattr(object.grease_pencil, 'name'):

            # object type
            if option.objectType in 'ALL':
              if object.grease_pencil.users == 1:

                # populate
                populate(context, object.grease_pencil, object)

              else:

                # shared
                if object.grease_pencil not in shared.greasePencils[:]:
                  shared.greasePencils.append(object.grease_pencil)

                  # populate
                  populate(context, object.grease_pencil, object)

            # object type
            elif option.objectType in object.type:
              if object.grease_pencil.users == 1:

                # populate
                populate(context, object.grease_pencil, object)

              else:

                # shared
                if object.grease_pencil not in shared.greasePencils[:]:
                  shared.greasePencils.append(object.grease_pencil)

                  # populate
                  populate(context, object.grease_pencil, object)

        # process
        process(context, storage.batch.greasePencils)

        # clear storage
        storage.batch.greasePencils.clear()

        # clear shared
        shared.greasePencils.clear()

      # pencil layers
      if option.pencilLayers:
        for object in context.scene.objects[:]:
          if hasattr(object.grease_pencil, 'name'):

            # object type
            if option.objectType in 'ALL':
              if object.grease_pencil.users == 1:

                # layers
                for layer in object.grease_pencil.layers[:]:

                  # populate
                  populate(context, layer)
              else:

                # shared
                if object.grease_pencil not in shared.greasePencils[:]:
                  shared.greasePencils.append(object.grease_pencil)

                  # layers
                  for layer in object.grease_pencil.layers[:]:

                    # populate
                    populate(context, layer)

            # object type
            elif option.objectType in object.type:
              if object.grease_pencil.users == 1:

                # layers
                for layer in object.grease_pencil.layers[:]:

                  # populate
                  populate(context, layer)
              else:

                # shared
                if object.grease_pencil not in shared.greasePencils[:]:
                  shared.greasePencils.append(object.grease_pencil)

                  # layers
                  for layer in object.grease_pencil.layers[:]:

                    # populate
                    populate(context, layer)

            # process
            process(context, storage.batch.pencilLayers)

            # clear storage
            storage.batch.pencilLayers.clear()

        # clear shared
        shared.greasePencils.clear()

      # objects
      if option.objects:
        for object in context.scene.objects[:]:

          # object type
          if option.objectType in 'ALL':

            # populate
            populate(context, object)

          # object type
          elif option.objectType in object.type:

            # populate
            populate(context, object)

        # process
        process(context, storage.batch.objects)

        # clear storage
        storage.batch.objects.clear()

      # groups
      if option.groups:
        for object in context.scene.objects[:]:

          # object type
          if option.objectType in 'ALL':
            for group in bpy.data.groups[:]:
              if object in group.objects[:]:

                # populate
                populate(context, group)

          # object type
          elif option.objectType in object.type:
            for group in bpy.data.groups[:]:
              if object in group.objects[:]:

                # populate
                populate(context, group)

        # clear duplicates
        objectGroups = []
        [objectGroups.append(item) for item in storage.batch.groups if item not in objectGroups]

        # clear storage
        storage.batch.groups.clear()

        # process
        process(context, objectGroups)

      # constraints
      if option.constraints:
        for object in context.scene.objects[:]:
          for constraint in object.constraints[:]:

            # constraint type
            if option.constraintType in 'ALL':

              # populate
              populate(context, constraint)

            # constraint type
            elif option.constraintType in constraint.type:

              # populate
              populate(context, constraint)

          # process
          process(context, storage.batch.constraints)

          # clear storage
          storage.batch.constraints.clear()

      # modifiers
      if option.modifiers:
        for object in context.scene.objects[:]:
          for modifier in object.modifiers[:]:

            # modifier type
            if option.modifierType in 'ALL':

              # populate
              populate(context, modifier)

            # modifier tye
            elif option.modifierType in modifier.type:

              # populate
              populate(context, modifier)

          # process
          process(context, storage.batch.modifiers)

          # clear storage
          storage.batch.modifiers.clear()

      # object data
      if option.objectData:
        for object in context.scene.objects[:]:
          if object.type not in 'EMPTY':

            # object type
            if option.objectType in 'ALL':
              if object.data.users == 1:

                # populate
                populate(context, object.data, object)
              else:

                # shared shared
                if object.data.name not in shared.objectData[:]:
                  shared.objectData.append(object.data.name)

                  # populate
                  populate(context, object.data, object)

            # object type
            elif option.objectType in object.type:
              if object.data.users == 1:

                # populate
                populate(context, object.data, object)
              else:

                # shared shared
                if object.data.name not in shared.objectData[:]:
                  shared.objectData.append(object.data.name)

                  # populate
                  populate(context, object.data, object)

        # clear shared
        shared.objectData.clear()

        # object data
        objectData = [
          storage.batch.curves,
          storage.batch.cameras,
          storage.batch.meshes,
          storage.batch.lamps,
          storage.batch.lattices,
          storage.batch.metaballs,
          storage.batch.speakers,
          storage.batch.armatures
        ]
        for collection in objectData:
          if collection != []:

            # process
            process(context, collection)

            # clear storage
            collection.clear()

      # bone groups
      if option.boneGroups:
        for object in context.scene.objects[:]:
          if object.type in 'ARMATURE':
            for group in object.pose.bone_groups[:]:

              # populate
              populate(context, group)

          # process
          process(context, storage.batch.boneGroups)

          # clear storage
          storage.batch.boneGroups.clear()

      # bones
      if option.bones:
        for object in context.scene.objects[:]:
          if object.type in 'ARMATURE':

            # edit mode
            if object.mode in 'EDIT':
              for bone in bpy.data.armatures[object.data.name].edit_bones[:]:

                  # populate
                  populate(context, bone)

            # pose or object mode
            else:
              for bone in bpy.data.armatures[object.data.name].bones[:]:

                  # populate
                  populate(context, bone)

            # process
            process(context, storage.batch.bones)

            # clear storage
            storage.batch.bones.clear()

      # bone constraints
      if option.boneConstraints:
        for object in context.scene.objects[:]:
          if object.type in 'ARMATURE':
            for bone in object.pose.bones[:]:
              for constraint in bone.constraints[:]:

                # constraint type
                if option.constraintType in 'ALL':

                  # populate
                  populate(context, constraint)

                # constraint type
                elif option.constraintType in constraint.type:

                  # populate
                  populate(context, constraint)

              # process
              process(context, storage.batch.constraints)

              # clear storage
              storage.batch.constraints.clear()

      # vertex groups
      if option.vertexGroups:
        for object in context.scene.objects[:]:
          if hasattr(object, 'vertex_groups'):
            for group in object.vertex_groups[:]:

              # object type
              if option.objectType in 'ALL':

                # populate
                populate(context, group)

              # object type
              elif option.objectType in object.type:

                # populate
                populate(context, group)

            # process
            process(context, storage.batch.vertexGroups)

            # clear storage
            storage.batch.vertexGroups.clear()

      # shapekeys
      if option.shapekeys:
        for object in context.scene.objects[:]:
          if hasattr(object.data, 'shape_keys'):
            if hasattr(object.data.shape_keys, 'key_blocks'):
              for block in object.data.shape_keys.key_blocks[:]:

                # object type
                if option.objectType in 'ALL':

                  # populate
                  populate(context, block)

                # object type
                elif option.objectType in object.type:

                  # populate
                  populate(context, block)

              # process
              process(context, storage.batch.shapekeys)

              # clear storage
              storage.batch.shapekeys.clear()

      # uvs
      if option.uvs:
        for object in context.scene.objects[:]:
          if object.type in 'MESH':
            for uv in object.data.uv_textures[:]:

              # populate
              populate(context, uv)

            # process
            process(context, storage.batch.uvs)

            # clear storage
            storage.batch.uvs.clear()

      # vertex colors
      if option.vertexColors:
        for object in context.scene.objects[:]:
          if object.type in 'MESH':
            for color in object.data.vertex_colors[:]:

              # populate
              populate(context, color)

            # process
            process(context, storage.batch.vertexColors)

            # clear storage
            storage.batch.vertexColors.clear()

      # materials
      if option.materials:
        for object in context.scene.objects[:]:
          for slot in object.material_slots[:]:
            if slot.material != None:
              if slot.material.users == 1:

                # object type
                if option.objectType in 'ALL':

                  # populate
                  populate(context, slot.material, slot)

                # object type
                elif option.objectType in object.type:

                  # populate
                  populate(context, slot.material, slot)
              else:

                # shared
                if slot.material not in shared.materials[:]:
                  shared.materials.append(slot.material)

                  # populate
                  populate(context, slot.material, slot)


        # process
        process(context, storage.batch.materials)

        # clear storage
        storage.batch.materials.clear()

        # clear shared
        shared.materials.clear()

      # textures
      if option.textures:
        for object in context.scene.objects[:]:
          if context.scene.render.engine not in 'CYCLES':
            for slot in object.material_slots[:]:
              if slot.material != None:
                if slot.material.users == 1:
                  for texslot in slot.material.texture_slots[:]:
                    if texslot != None:
                      if texslot.texture.users == 1:

                        # object type
                        if option.objectType in 'ALL':

                          # populate
                          populate(context, texslot.texture, texslot)

                        # object type
                        elif option.objectType in object.type:

                          # populate
                          populate(context, texslot.texture, texslot)
                      else:

                        # shared
                        if texslot.texture not in shared.textures[:]:
                          shared.textures.append(texslot.texture)

                          # populate
                          populate(context, texslot.texture, texslot)
                else:

                  # shared
                  if slot.material not in shared.materials[:]:
                    shared.materials.append(slot.material)
                    for texslot in slot.material.texture_slots[:]:
                      if texslot != None:
                        if texslot.texture.users == 1:

                          # object type
                          if option.objectType in 'ALL':

                            # populate
                            populate(context, texslot.texture, texslot)

                          # object type
                          elif option.objectType in object.type:

                            # populate
                            populate(context, texslot.texture, texslot)
                        else:

                          # shared
                          if texslot.texture not in shared.textures[:]:
                            shared.textures.append(texslot.texture)

                            # populate
                            populate(context, texslot.texture, texslot)

        # process
        process(context, storage.batch.textures)

        # clear storage
        storage.batch.textures.clear()

        # clear shared
        shared.textures.clear()

      # particle systems
      if option.particleSystems:
        for object in context.scene.objects[:]:
          if object.type in 'MESH':
            for system in object.particle_systems[:]:

              # object type
              if option.objectType in 'ALL':

                # populate
                populate(context, system)

              # object type
              elif option.objectType in object.type:

                # populate
                populate(context, system)

            # process
            process(context, storage.batch.particleSystems)

            # clear storage
            storage.batch.particleSystems.clear()

      # particle settings
      if option.particleSettings:
        for object in context.scene.objects[:]:
          if object.type in 'MESH':
            for system in object.particle_systems[:]:

              # object type
              if option.objectType in 'ALL':
                if system.settings.users == 1:

                  # populate
                  populate(context, system.settings, system)
                else:

                  # shared
                  if system.settings not in shared.particleSettings[:]:
                    shared.particleSettings.append(system.settings)

                    # populate
                    populate(context, system.settings, system)

              # object type
              elif option.objectType in object.type:
                if system.settings.users == 1:

                  # populate
                  populate(context, system.settings, system)
                else:

                  # shared
                  if system.settings not in shared.particleSettings[:]:
                    shared.particleSettings.append(system.settings)

                    # populate
                    populate(context, system.settings, system)

        # process
        process(context, storage.batch.particleSettings)

        # clear storage
        storage.batch.particleSettings.clear()

        # clear shared
        shared.particleSettings.clear()

      # sensors
      if option.sensors:
        for object in context.scene.objects[:]:

          # object type
          if option.objectType in 'ALL':

            # populate
            for sensor in object.game.sensors[:]:
              populate(context, sensor)

          # object type
          elif option.objectType in object.type:

            # populate
            for sensor in object.game.sensors[:]:
              populate(context, sensor)

          # process
          process(context, storage.batch.sensors)

          # clear storage
          storage.batch.sensors.clear()

      # controllers
      if option.controllers:
        for object in context.scene.objects[:]:

          # object type
          if option.objectType in 'ALL':

            # populate
            for controller in object.game.controllers[:]:
              populate(context, controller)

          # object type
          elif option.objectType in object.type:

            # populate
            for controller in object.game.controllers[:]:
              populate(context, controller)

          # process
          process(context, storage.batch.controllers)

          # clear storage
          storage.batch.controllers.clear()

      # actuators
      if option.actuators:
        for object in context.scene.objects[:]:

          # object type
          if option.objectType in 'ALL':

            # populate
            for actuator in object.game.actuators[:]:
              populate(context, actuator)

          # object type
          elif option.objectType in object.type:

            # populate
            for actuator in object.game.actuators[:]:
              populate(context, actuator)

          # process
          process(context, storage.batch.actuators)

          # clear storage
          storage.batch.actuators.clear()

    # mode
    elif option.mode in 'GLOBAL':

      # actions
      if option.actions:
        for action in bpy.data.actions[:]:

          # populate
          populate(context, action)

        # process
        process(context, storage.batch.actions)

        # clear storage
        storage.batch.actions.clear()

      # action groups
      if option.actionGroups:
        for action in bpy.data.actions[:]:

          # populate
          populate(context, action)

        # process
        for action in storage.batch.actions:
          for group in action[1][1].groups:
            group.name = name(context, group.name) if not option.suffixLast else name(context, group.name) + option.suffix

          # bones
          if option.bones:

            # fix paths
            for curve in action[1][1].fcurves[:]:
              if 'pose' in curve.data_path:
                if not re.search(re.escape(']['), curve.data_path) and not re.search('constraints', curve.data_path):
                  try:
                    curve.data_path = 'pose.bones["' + curve.group.name + '"].' + (curve.data_path.rsplit('.', 1)[1]).rsplit('[', 1)[0]
                  except:
                    pass

        # clear storage
        storage.batch.actions.clear()

      # grease pencil
      if option.greasePencil:
        for pencil in bpy.data.grease_pencil[:]:

          # populate
          populate(context, pencil)

        # process
        process(context, storage.batch.greasePencils)

        # clear storage
        storage.batch.greasePencils.clear()

      # pencil layers
      if option.pencilLayers:
        for pencil in bpy.data.grease_pencil[:]:

          # layers
          for layer in pencil.layers[:]:

            # populate
            populate(context, layer)

          # process
          process(context, storage.batch.pencilLayers)

          # clear storage
          storage.batch.pencilLayers.clear()

      # objects
      if option.objects:
        for object in bpy.data.objects[:]:

          # object type
          if option.objectType in 'ALL':

            # populate
            populate(context, object)

          # object type
          elif option.objectType in object.type:

            # populate
            populate(context, object)

        # process
        process(context, storage.batch.objects)

        # clear storage
        storage.batch.objects.clear()

      # groups
      if option.groups:
        for group in bpy.data.groups[:]:

          # populate
          populate(context, group)

        # process
        process(context, storage.batch.groups)

        # clear storage
        storage.batch.groups.clear()

      # constraints
      if option.constraints:
        for object in bpy.data.objects[:]:
          for constraint in object.constraints[:]:

            # object type
            if option.objectType in 'ALL':

              # constraint type
              if option.constraintType in 'ALL':

                # populate
                populate(context, constraint)

              # constraint type
              elif option.constraintType in constraint.type:

                # populate
                populate(context, constraint)

            # object type
            elif option.objectType in object.type:

              # constraint type
              if option.constraintType in 'ALL':

                # populate
                populate(context, constraint)

                # constraint type
              elif option.constraintType in constraint.type:

                # populate
                populate(context, constraint)

          # process
          process(context, storage.batch.constraints)

          # clear storage
          storage.batch.constraints.clear()

      # modifiers
      if option.modifiers:
        for object in bpy.data.objects[:]:
          for modifier in object.modifiers[:]:

            # object type
            if option.objectType in 'ALL':

              # modifier type
              if option.modifierType in 'ALL':

                # populate
                populate(context, modifier)

              # modifier type
              elif option.modifierType in modifier.type:

                # populate
                populate(context, modifier)

            # object type
            elif option.objectType in object.type:

              # modifier type
              if option.modifierType in 'ALL':

                # populate
                populate(context, modifier)

              # modifier type
              elif option.modifierType in modifier.type:

                # populate
                populate(context, modifier)

          # process
          process(context, storage.batch.modifiers)

          # clear storage
          storage.batch.modifiers.clear()

      # object data
      if option.objectData:

        # cameras
        for camera in bpy.data.cameras[:]:

          # populate
          populate(context, camera)

        # process
        process(context, storage.batch.cameras)

        # clear storage
        storage.batch.cameras.clear()

        # meshes
        for mesh in bpy.data.meshes[:]:

          # populate
          populate(context, mesh)

        # process
        process(context, storage.batch.meshes)

        # clear storage
        storage.batch.meshes.clear()

        # curves
        for curve in bpy.data.curves[:]:

          # populate
          populate(context, curve)

        # process
        process(context, storage.batch.curves)

        # clear storage
        storage.batch.curves.clear()

        # lamps
        for lamp in bpy.data.lamps[:]:

          # populate
          populate(context, lamp)

        # process
        process(context, storage.batch.lamps)

        # clear storage
        storage.batch.lamps.clear()

        # lattices
        for lattice in bpy.data.lattices[:]:

          # populate
          populate(context, lattice)

        # process
        process(context, storage.batch.lattices)

        # clear storage
        storage.batch.lattices.clear()

        # metaballs
        for metaball in bpy.data.metaballs[:]:

          # populate
          populate(context, metaball)

        # process
        process(context, storage.batch.metaballs)

        # clear storage
        storage.batch.metaballs.clear()

        # speakers
        for speaker in bpy.data.speakers[:]:

          # populate
          populate(context, speaker)

        # process
        process(context, storage.batch.speakers)

        # clear storage
        storage.batch.speakers.clear()

        # armatures
        for armature in bpy.data.armatures[:]:

          # populate
          populate(context, armature)

        # process
        process(context, storage.batch.armatures)

        # clear storage
        storage.batch.armatures.clear()

      # bone groups
      if option.boneGroups:
        for object in bpy.data.objects[:]:
          if object.type in 'ARMATURE':
            for group in object.pose.bone_groups[:]:

              # populate
              populate(context, group)

            # process
            process(context, storage.batch.boneGroups)

            # clear storage
            storage.batch.boneGroups.clear()

      # bones
      if option.bones:
        for armature in bpy.data.armatures[:]:
          for bone in armature.bones[:]:

            # populate
            populate(context, bone)

          # process
          process(context, storage.batch.bones)

          # clear storage
          storage.batch.bones.clear()

      # bone constraints
      if option.boneConstraints:
        for object in bpy.data.objects[:]:
          if object.type in 'ARMATURE':
            for bone in object.pose.bones[:]:
              for constraint in bone.constraints[:]:

                # populate
                populate(context, constraint)

              # process
              process(context, storage.batch.constraints)

              # clear storage
              storage.batch.constraints.clear()

      # vertex groups
      if option.vertexGroups:
        for object in bpy.data.objects[:]:
          if object.type in {'MESH', 'LATTICE'}:
            for group in object.vertex_groups[:]:

              # populate
              populate(context, group)

            # process
            process(context, storage.batch.vertexGroups)

            # clear storage
            storage.batch.vertexGroups.clear()

      # shape keys
      if option.shapekeys:
        for shapekey in bpy.data.shape_keys[:]:

            # populate
            populate(context, shapekey)
            for block in shapekey.key_blocks[:]:

              # populate
              populate(context, block)

            # process
            process(context, storage.batch.shapekeys)

            # clear storage
            storage.batch.shapekeys.clear()

      # uvs
      if option.uvs:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':
            for uv in object.data.uv_textures[:]:

              # populate
              populate(context, uv)

            # process
            process(context, storage.batch.uvs)

            # clear storage
            storage.batch.uvs.clear()

      # vertex colors
      if option.vertexColors:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':
            for color in object.data.vertex_colors[:]:

              # populate
              populate(context, color)

            # process
            process(context, storage.batch.vertexColors)

            # clear storage
            storage.batch.vertexColors.clear()

      # materials
      if option.materials:
        for material in bpy.data.materials[:]:

          # populate
          populate(context, material)

        # process
        process(context, storage.batch.materials)

        # clear storage
        storage.batch.materials.clear()

      # textures
      if option.textures:
        for texture in bpy.data.textures[:]:

          # populate
          populate(context, texture)

        # process
        process(context, storage.batch.textures)

        # clear storage
        storage.batch.textures.clear()

      # particles systems
      if option.particleSystems:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':
            for system in object.particle_systems[:]:

              # populate
              populate(context, system)

            # process
            process(context, storage.batch.particleSystems)

            # clear storage
            storage.batch.particleSystems.clear()

      # particles settings
      if option.particleSettings:
        for settings in bpy.data.particles[:]:

          # populate
          populate(context, settings)

        # process
        process(context, storage.batch.particleSettings)

        # clear storage
        storage.batch.particleSettings.clear()

      # sensors
      if option.sensors:
        for object in bpy.data.objects[:]:

          # object type
          if option.objectType in 'ALL':

            # populate
            for sensor in object.game.sensors[:]:
              populate(context, sensor)

          # object type
          elif option.objectType in object.type:

            # populate
            for sensor in object.game.sensors[:]:
              populate(context, sensor)

          # process
          process(context, storage.batch.sensors)

          # clear storage
          storage.batch.sensors.clear()

      # controllers
      if option.controllers:
        for object in bpy.data.objects[:]:

          # object type
          if option.objectType in 'ALL':

            # populate
            for controller in object.game.controllers[:]:
              populate(context, controller)

          # object type
          elif option.objectType in object.type:

            # populate
            for controller in object.game.controllers[:]:
              populate(context, controller)

          # process
          process(context, storage.batch.controllers)

          # clear storage
          storage.batch.controllers.clear()

      # actuators
      if option.actuators:
        for object in bpy.data.objects[:]:

          # object type
          if option.objectType in 'ALL':

            # populate
            for actuator in object.game.actuators[:]:
              populate(context, actuator)

          # object type
          elif option.objectType in object.type:

            # populate
            for actuator in object.game.actuators[:]:
              populate(context, actuator)

          # process
          process(context, storage.batch.actuators)

          # clear storage
          storage.batch.actuators.clear()

    # line sets
    if option.lineSets:
      for scene in bpy.data.scenes[:]:
        for layer in scene.render.layers[:]:
          for lineset in layer.freestyle_settings.linesets[:]:
            if hasattr(lineset, 'name'):
              lineset.name = name(context, lineset.name) if not option.suffixLast else name(context, lineset.name) + option.suffix

    # linestyles
    if option.linestyles:
      for style in bpy.data.linestyles[:]:

        # populate
        populate(context, style)

      # process
      process(context, storage.batch.linestyles)

      # clear storage
      storage.batch.linestyles.clear()

    # linestyle modifiers
    if option.linestyleModifiers:
      for style in bpy.data.linestyles[:]:


        # color
        for modifier in style.color_modifiers[:]:

          # linestyle modifier type
          if option.linestyleModifierType in 'ALL':

            # populate
            populate(context, modifier)

          # linestyle modifier type
          elif option.linestyleModifierType in modifier.type:

            # populate
            populate(context, modifier)

        # process
        process(context, storage.batch.modifiers)

        # clear storage
        storage.batch.modifiers.clear()


        # alpha
        for modifier in style.alpha_modifiers[:]:

          # linestyle modifier type
          if option.linestyleModifierType in 'ALL':

            # populate
            populate(context, modifier)

          # linestyle modifier type
          elif option.linestyleModifierType in modifier.type:

            # populate
            populate(context, modifier)

        # process
        process(context, storage.batch.modifiers)

        # clear storage
        storage.batch.modifiers.clear()


        # thickness
        for modifier in style.thickness_modifiers[:]:

          # linestyle modifier type
          if option.linestyleModifierType in 'ALL':

            # populate
            populate(context, modifier)

          # linestyle modifier type
          elif option.linestyleModifierType in modifier.type:

            # populate
            populate(context, modifier)

        # process
        process(context, storage.batch.modifiers)

        # clear storage
        storage.batch.modifiers.clear()


        # geometry
        for modifier in style.geometry_modifiers[:]:

          # linestyle modifier type
          if option.linestyleModifierType in 'ALL':

            # populate
            populate(context, modifier)

          # linestyle modifier type
          elif option.linestyleModifierType in modifier.type:

            # populate
            populate(context, modifier)

        # process
        process(context, storage.batch.modifiers)

        # clear storage
        storage.batch.modifiers.clear()

    # scenes
    if option.scenes:
      for scene in bpy.data.scenes[:]:

        # populate
        populate(context, scene)

      # process
      process(context, storage.batch.scenes)

      # clear storage
      storage.batch.scenes.clear()

    # render layers
    if option.renderLayers:
      for scene in bpy.data.scenes[:]:
        for layer in scene.render.layers[:]:

          # populate
          populate(context, layer)

        # process
        process(context, storage.batch.renderLayers)

        # clear storage
        storage.batch.renderLayers.clear()

    # worlds
    if option.worlds:
      for world in bpy.data.worlds[:]:

        # populate
        populate(context, world)

      # process
      process(context, storage.batch.worlds)

      # clear storage
      storage.batch.worlds.clear()

    # libraries
    if option.libraries:
      for library in bpy.data.libraries[:]:

        # populate
        populate(context, library)

      # process
      process(context, storage.batch.libraries)

      # clear storage
      storage.batch.libraries.clear()

    # images
    if option.images:
      for image in bpy.data.images[:]:

        # populate
        populate(context, image)

      # process
      process(context, storage.batch.images)

      # clear storage
      storage.batch.images.clear()

    # masks
    if option.masks:
      for mask in bpy.data.masks[:]:

        # populate
        populate(context, mask)

      # process
      process(context, storage.batch.masks)

      # clear storage
      storage.batch.masks.clear()

    # sequences
    if option.sequences:
      for scene in bpy.data.scenes[:]:
        if hasattr(scene.sequence_editor, 'sequence_all'):
          for sequence in scene.sequence_editor.sequences_all[:]:

            # populate
            populate(context, sequence)

          # process
          process(context, storage.batch.sequences)

          # clear storage
          storage.batch.sequences.clear()

    # movie clips
    if option.movieClips:
      for clip in bpy.data.movieclips[:]:

        # populate
        populate(context, clip)

      # process
      process(context, storage.batch.movieClips)

      # clear storage
      storage.batch.movieClips.clear()

    # sounds
    if option.sounds:
      for sound in bpy.data.sounds[:]:

        # populate
        populate(context, sound)

      # process
      process(context, storage.batch.sounds)

      # clear storage
      storage.batch.sounds.clear()

    # screens
    if option.screens:
      for screen in bpy.data.screens[:]:

        # populate
        populate(context, screen)

      # process
      process(context, storage.batch.screens)

      # clear storage
      storage.batch.screens.clear()

    # keying sets
    if option.keyingSets:
      for scene in bpy.data.scenes[:]:
        for keyingSet in scene.keying_sets[:]:

          # populate
          populate(context, keyingSet)

        # process
        process(context, storage.batch.keyingSets)

        # clear storage
        storage.batch.keyingSets.clear()

    # palettes
    if option.palettes:
      for palette in bpy.data.palettes[:]:

        # populate
        populate(context, palette)

      # process
      process(context, storage.batch.palettes)

      # clear storage
      storage.batch.palettes.clear()

    # brushes
    if option.brushes:
      for brush in bpy.data.brushes[:]:

        # populate
        populate(context, brush)

      # process
      process(context, storage.batch.brushes)

      # clear storage
      storage.batch.brushes.clear()

    # nodes
    if option.nodes:

      # shader
      for material in bpy.data.materials[:]:
        if hasattr(material.node_tree, 'nodes'):
          for node in material.node_tree.nodes[:]:

            # populate
            populate(context, node)

          # process
          process(context, storage.batch.nodes)

          # clear storage
          storage.batch.nodes.clear()

      # compositing
      for scene in bpy.data.scenes[:]:
        if hasattr(scene.node_tree, 'nodes'):
          for node in scene.node_tree.nodes[:]:

            # populate
            populate(context, node)

          # process
          process(context, storage.batch.nodes)

          # clear storage
          storage.batch.nodes.clear()

      # texture
      for texture in bpy.data.textures[:]:
        if hasattr(texture.node_tree, 'nodes'):
          for node in texture.node_tree.nodes[:]:

            # populate
            populate(context, node)

          # process
          process(context, storage.batch.nodes)

          # clear storage
          storage.batch.nodes.clear()

      # groups
      for group in bpy.data.node_groups[:]:
        for node in group.nodes[:]:

          # populate
          populate(context, node)

        # process
        process(context, storage.batch.nodes)

        # clear storage
        storage.batch.nodes.clear()

    # node labels
    if option.nodeLabels:

      # batch tag
      tag = True

      # shader
      for material in bpy.data.materials[:]:
        if hasattr(material.node_tree, 'nodes'):
          for node in material.node_tree.nodes[:]:

            # populate
            populate(context, node)

          # process
          process(context, storage.batch.nodeLabels)

          # clear storage
          storage.batch.nodeLabels.clear()

      # compositing
      for scene in bpy.data.scenes[:]:
        if hasattr(scene.node_tree, 'nodes'):
          for node in scene.node_tree.nodes[:]:

            # populate
            populate(context, node)

          # process
          process(context, storage.batch.nodeLabels)

          # clear storage
          storage.batch.nodeLabels.clear()

      # texture
      for texture in bpy.data.textures[:]:
        if hasattr(texture.node_tree, 'nodes'):
          for node in texture.node_tree.nodes[:]:

            # populate
            populate(context, node)

          # process
          process(context, storage.batch.nodeLabels)

          # clear storage
          storage.batch.nodeLabels.clear()

      # groups
      for group in bpy.data.node_groups[:]:
        for node in group.nodes[:]:

          # populate
          populate(context, node)

        # process
        process(context, storage.batch.nodeLabels)

        # clear storage
        storage.batch.nodeLabels.clear()

      # batch tag
      tag = False

    # node groups
    if option.nodeGroups:
      for group in bpy.data.node_groups[:]:

        # populate
        populate(context, group)

      # process
      process(context, storage.batch.nodeGroups)

      # clear storage
      storage.batch.nodeGroups.clear()

    # texts
    if option.texts:
      for text in bpy.data.texts[:]:

        # populate
        populate(context, text)

      # process
      process(context, storage.batch.texts)

      # clear storage
      storage.batch.texts.clear()

    # frame nodes
    if option.frameNodes:

      # shader
      for material in bpy.data.materials[:]:
        if hasattr(material.node_tree, 'nodes'):
          for node in material.node_tree.nodes[:]:

            # populate
            populate(context, node)

          # process
          process(context, storage.batch.nodes)

          # clear storage
          storage.batch.nodes.clear()

      # compositing
      for scene in bpy.data.scenes[:]:
        if hasattr(scene.node_tree, 'nodes'):
          for node in scene.node_tree.nodes[:]:

            # populate
            populate(context, node)

          # process
          process(context, storage.batch.nodes)

          # clear storage
          storage.batch.nodes.clear()

      # texture
      for texture in bpy.data.textures[:]:
        if hasattr(texture.node_tree, 'nodes'):
          for node in texture.node_tree.nodes[:]:

            # populate
            populate(context, node)

          # process
          process(context, storage.batch.nodes)

          # clear storage
          storage.batch.nodes.clear()

      # groups
      for group in bpy.data.node_groups[:]:
        for node in group.nodes[:]:

          # populate
          populate(context, node)

        # process
        process(context, storage.batch.nodes)

        # clear storage
        storage.batch.nodes.clear()

# quick
def quick(context, object, panel, option):
  '''
    Quick batch mode for main.
  '''

  # search
  search = panel.search if panel.regex else re.escape(panel.search)

  # search
  if search == '' or re.search(search, object.name, re.I):

    # ignore Object
    if not option.ignoreObject:

      # populate
      populate(context, object)

  # action
  if panel.action:

    # ignore action
    if not option.ignoreAction:
      if hasattr(object.animation_data, 'action'):
        if hasattr(object.animation_data.action, 'name'):

          # search
          if search == '' or re.search(search, object.animation_data.action.name, re.I):

            # populate
            populate(context, object.animation_data.action, object.animation_data)

  # grease pencils
  if panel.greasePencil:

    # ignore grease pencil
    if not option.ignoreGreasePencil:
      if hasattr(object.grease_pencil, 'name'):

        # search
        if search == '' or re.search(search, object.grease_pencil.name, re.I):

          # populate
          populate(context, object.grease_pencil, object)

        # layers
        for layer in object.grease_pencil.layers[:]:

          # search
          if search == '' or re.search(search, layer.info, re.I):

            # populate
            populate(context, layer)

        # process
        process(context, storage.batch.pencilLayers)

        # clear storage
        storage.batch.pencilLayers.clear()

  # groups
  if panel.groups:

    # ignore group
    if not option.ignoreGroup:
      for group in bpy.data.groups[:]:
        for groupObject in group.objects[:]:
          if groupObject == object:

            # search
            if search == '' or re.search(search, group.name, re.I):

              # populate
              populate(context, group)

  # constraints
  if panel.constraints:

    # ignore constraint
    if not option.ignoreConstraint:
      for constraint in object.constraints[:]:

        # search
        if search == '' or re.search(search, constraint.name, re.I):

          # populate
          populate(context, constraint)

      # process
      process(context, storage.batch.constraints)

      # clear storage
      storage.batch.constraints.clear()

  # modifiers
  if panel.modifiers:

    # ignore modifier
    if not option.ignoreModifier:
      for modifier in object.modifiers[:]:

        # search
        if search == '' or re.search(search, modifier.name, re.I):

          # populate
          populate(context, modifier)

      # process
      process(context, storage.batch.modifiers)

      # clear storage
      storage.batch.modifiers.clear()

  # bone groups
  if panel.boneGroups:

    # ignore bone group
    if not option.ignoreBoneGroup:
      if object.type in 'ARMATURE':
        for group in object.pose.bone_groups[:]:

          # search
          if search == '' or re.search(search, group.name, re.I):

            # populate
            populate(context, group)

        # process
        process(context, storage.batch.boneGroups)

        # clear storage
        storage.batch.boneGroups.clear()

  # bones
  if object == context.active_object:

    # ignore bone
    if not option.ignoreBone:
      if object.type == 'ARMATURE':
        if object.mode in {'POSE', 'EDIT'}:

          # display bones
          if panel.displayBones:

            # bone mode
            if panel.boneMode == 'SELECTED':

              # pose
              if object.mode == 'POSE':

                # bones
                bones = context.selected_pose_bones[:]

              # edit
              elif object.mode == 'EDIT':

                # bones
                bones = context.selected_bones[:]

              # bone
              for bone in bones:

                # search
                if search == '' or re.search(search, bone.name, re.I):

                  # populate
                  populate(context, bone)

            # bone mode
            else:

              # pose
              if object.mode == 'POSE':

                # bones
                bones = [bone for bone in object.data.bones if True in [x&y for (x, y) in zip(bone.layers, object.data.layers)]]

                # edit
              elif object.mode == 'EDIT':

                # bones
                bones = [bone for bone in object.data.edit_bones if True in [x&y for (x, y) in zip(bone.layers, object.data.layers)]]

              # bone
              for bone in bones:

                # search
                if search == '' or re.search(search, bone.name, re.I):

                  # populate
                  populate(context, bone)

          # display bones
          else:

            # mode
            if object.mode == 'EDIT':

              # search
              if search == '' or re.search(search, context.active_bone, re.I):

                # name
                context.active_bone.name = name(context, context.active_bone.name) if option.suffixLast else name(context, context.active_bone.name) + option.suffix

            # mode
            elif object.mode == 'POSE':

              # search
              if search == '' or re.search(search, context.active_pose_bone, re.I):

                # name
                context.active_pose_bone.name = name(context, context.active_pose_bone.name) if option.suffixLast else name(context, context.active_pose_bone.name) + option.suffix

    # bone constraints
    if panel.boneConstraints:

      # ignore bone constraint
      if not option.ignoreBoneConstraint:
        if object.mode == 'POSE':

          # display bones
          if panel.displayBones:

            # bone mode
            if panel.boneMode == 'SELECTED':
              for bone in context.selected_pose_bones[:]:
                for constraint in bone.constraints[:]:

                  # search
                  if search == '' or re.search(search, constraint.name, re.I):

                    # append
                    storage.batch.constraints.append([constraint.name, [1, constraint]])

                # process
                process(context, storage.batch.constraints)

                # clear storage
                storage.batch.constraints.clear()

            # bone mode
            else:
              for bone in object.pose.bones[:]:
                if True in [x&y for (x, y) in zip(bone.bone.layers, object.data.layers)]:
                  for constraint in bone.constraints[:]:

                    # search
                    if search == '' or re.search(search, constraint.name, re.I):

                      # append
                      storage.batch.constraints.append([constraint.name, [1, constraint]])

                  # process
                  process(context, storage.batch.constraints)

                  # clear storage
                  storage.batch.constraints.clear()

          # display bones
          else:
            for constraint in context.active_pose_bone.constraints[:]:

              # search
              if search == '' or re.search(search, constraint.name, re.I):

                # append
                storage.batch.constraints.append([constraint.name, [1, constraint]])

            # process
            process(context, storage.batch.constraints)

            # clear storage
            storage.batch.constraints.clear()

  # object data
  if object.type != 'EMPTY':

    # ignore object data
    if not option.ignoreObjectData:

      # search
      if search == '' or re.search(search, object.data.name, re.I):

        # populate
        populate(context, object.data, object)

  # vertex groups
  if panel.vertexGroups:

    # ignore vertex group
    if not option.ignoreVertexGroup:
      if hasattr(object, 'vertex_groups'):
        for group in object.vertex_groups[:]:

          # search
          if search == '' or re.search(search, group.name, re.I):

            # populate
            populate(context, group)

        # process
        process(context, storage.batch.vertexGroups)

        # clear storage
        storage.batch.vertexGroups.clear()

  # shapekeys
  if panel.shapekeys:

    # ignore shapekey
    if not option.ignoreShapekey:
      if hasattr(object.data, 'shape_keys'):
        if hasattr(object.data.shape_keys, 'key_blocks'):
          for key in object.data.shape_keys.key_blocks[:]:

            # search
            if search == '' or re.search(search, key.name, re.I):

              # populate
              populate(context, key)

          # process
          process(context, storage.batch.shapekeys)

          # clear storage
          storage.batch.shapekeys.clear()

  # uv maps
  if panel.uvs:

    # ignore uv
    if not option.ignoreUV:
      if object.type in 'MESH':
        for uv in object.data.uv_textures[:]:

          # search
          if search == '' or re.search(search, uv.name, re.I):

            # populate
            populate(context, uv)

        # process
        process(context, storage.batch.uvs)

        # clear storage
        storage.batch.uvs.clear()

  # vertex colors
  if panel.vertexColors:

    # ignore vertex color
    if not option.ignoreVertexColor:
      if object.type in 'MESH':
        for vertexColor in object.data.vertex_colors[:]:

          # search
          if search == '' or re.search(search, vertexColor.name, re.I):

            # populate
            populate(context, vertexColor)

        # process
        process(context, storage.batch.vertexColors)

        # clear storage
        storage.batch.vertexColors.clear()

  # materials
  if panel.materials:

    # ignore material
    if not option.ignoreMaterial:
      for slot in object.material_slots:
        if slot.material != None:

          # search
          if search == '' or re.search(search, slot.material.name, re.I):

            # populate
            populate(context, slot.material, slot)

  # textures
  if panel.textures:

    # ignore texture
    if not option.ignoreTexture:

      # material textures
      for slot in object.material_slots:
        if slot.material != None:
          if context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}:
            for tslot in slot.material.texture_slots[:]:
              if hasattr(tslot, 'texture'):
                if tslot.texture != None:

                  # search
                  if search == '' or re.search(search, tslot.texture.name, re.I):

                    # populate
                    populate(context, tslot.texture, tslot)

      # particle system textures
      if panel.particleSystems:
        for modifier in object.modifiers[:]:
          if modifier.type == 'PARTICLE_SYSTEM':
            for slot in modifier.particle_system.settings.texture_slots[:]:
              if hasattr(slot, 'texture'):
                if slot.texture != None:

                  # search
                  if search == '' or re.search(search, slot.texture.name, re.I):

                    # populate
                    populate(context, slot.texture, slot)

      # modifier textures
      if panel.modifiers:
        for modifier in object.modifiers[:]:

          # texture
          if modifier.type in {'DISPLACE', 'WARP'}:
            if modifier.texture:

              # search
              if search == '' or re.search(search, modifier.texture.name, re.I):

                # populate
                populate(context, modifier.texture, modifier)

          # mask texture
          elif modifier.type in {'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_EDIT', 'VERTEX_WEIGHT_PROXIMITY'}:
            if modifier.mask_texture:

              # search
              if search == '' or re.search(search, modifier.mask_texture.name, re.I):

                # populate
                populate(context, modifier.mask_texture)

  # particle systems
  if panel.particleSystems:

    # ignore particle system
    if not option.ignoreParticleSystem:
      for modifier in object.modifiers[:]:
        if modifier.type in 'PARTICLE_SYSTEM':

          # search
          if search == '' or re.search(search, modifier.particle_system.name, re.I):

            # populate
            populate(context, modifier.particle_system)

      # process
      process(context, storage.batch.particleSystems)

      # clear storage
      storage.batch.particleSystems.clear()

  # particle settings
  if panel.particleSystems:

    # ignore particle setting
    if not option.ignoreParticleSetting:
      for modifier in object.modifiers[:]:
        if modifier.type in 'PARTICLE_SYSTEM':

          # search
          if search == '' or re.search(search, modifier.particle_system.settings.name, re.I):

            # populate
            populate(context, modifier.particle_system.settings, modifier.particle_system)

# populate
def populate(context, datablock, source=None):
  '''
    Sort datablocks into proper storage list.
  '''

  # tag
  global tag

  # option
  option = context.scene.BatchName

  # objects
  if datablock.rna_type.identifier == 'Object':
    storage.batch.objects.append([datablock.name, [1, datablock]])

  # groups
  if datablock.rna_type.identifier == 'Group':
    storage.batch.groups.append([datablock.name, [1, datablock]])

  # actions
  if datablock.rna_type.identifier == 'Action':
    storage.batch.actions.append([datablock.name, [1, datablock, source]])

  # grease pencils
  if datablock.rna_type.identifier == 'GreasePencil':
    storage.batch.greasePencils.append([datablock.name, [1, datablock, source]])

  # pencil layers
  if datablock.rna_type.identifier == 'GPencilLayer':
    storage.batch.pencilLayers.append([datablock.info, [1, datablock]])

  # constraints
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier == 'Constraint':
      storage.batch.constraints.append([datablock.name, [1, datablock]])

  # modifiers
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier in 'Modifier':
      storage.batch.modifiers.append([datablock.name, [1, datablock]])

  # cameras
  if datablock.rna_type.identifier == 'Camera':
    storage.batch.cameras.append([datablock.name, [1, datablock, source]])

  # meshes
  if datablock.rna_type.identifier == 'Mesh':
    storage.batch.meshes.append([datablock.name, [1, datablock, source]])

  # curves
  if datablock.rna_type.identifier in {'SurfaceCurve', 'TextCurve', 'Curve'}:
    storage.batch.curves.append([datablock.name, [1, datablock, source]])

  # lamps
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier == 'Lamp':
      storage.batch.lamps.append([datablock.name, [1, datablock, source]])

  # lattices
  if datablock.rna_type.identifier == 'Lattice':
    storage.batch.lattices.append([datablock.name, [1, datablock, source]])

  # metaballs
  if datablock.rna_type.identifier == 'MetaBall':
    storage.batch.metaballs.append([datablock.name, [1, datablock, source]])

  # speakers
  if datablock.rna_type.identifier == 'Speaker':
    storage.batch.speakers.append([datablock.name, [1, datablock, source]])

  # armatures
  if datablock.rna_type.identifier == 'Armature':
    storage.batch.armatures.append([datablock.name, [1, datablock, source]])

  # bones
  if datablock.rna_type.identifier in {'PoseBone', 'EditBone', 'Bone'}:
    storage.batch.bones.append([datablock.name, [1, datablock]])

  # vertex groups
  if datablock.rna_type.identifier == 'VertexGroup':
    storage.batch.vertexGroups.append([datablock.name, [1, datablock]])

  # shapekeys
  if datablock.rna_type.identifier == 'ShapeKey':
    storage.batch.shapekeys.append([datablock.name, [1, datablock]])

  # uvs
  if datablock.rna_type.identifier == 'MeshTexturePolyLayer':
    storage.batch.uvs.append([datablock.name, [1, datablock]])

  # vertex colors
  if datablock.rna_type.identifier == 'MeshLoopColorLayer':
    storage.batch.vertexColors.append([datablock.name, [1, datablock]])

  # materials
  if datablock.rna_type.identifier == 'Material':
    storage.batch.materials.append([datablock.name, [1, datablock, source]])

  # textures
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier == 'Texture':
      storage.batch.textures.append([datablock.name, [1, datablock, source]])

  # particle systems
  if datablock.rna_type.identifier == 'ParticleSystem':
    storage.batch.particleSystems.append([datablock.name, [1, datablock]])

  # particle settings
  if datablock.rna_type.identifier == 'ParticleSettings':
    storage.batch.particleSettings.append([datablock.name, [1, datablock, source]])

  # line style
  if datablock.rna_type.identifier == 'FreestyleLineStyle':
    storage.batch.linestyles.append([datablock.name, [1, datablock]])

  # line style modifiers
  if hasattr(datablock.rna_type.base, 'identifier'):
    if hasattr(datablock.rna_type.base.base, 'identifier'):
      if datablock.rna_type.base.base.identifier == 'LineStyleModifier':
        storage.batch.modifiers.append([datablock.name, [1, datablock]])

  # sensors
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier == 'Sensor':
      storage.batch.sensors.append([datablock.name, [1, datablock]])

  # controllers
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier == 'Controller':
      storage.batch.controllers.append([datablock.name, [1, datablock]])

  # actuators
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier == 'Actuator':
      storage.batch.actuators.append([datablock.name, [1, datablock]])

  # scenes
  if datablock.rna_type.identifier == 'Scene':
    storage.batch.scenes.append([datablock.name, [1, datablock]])

  # render layers
  if datablock.rna_type.identifier == 'SceneRenderLayer':
    storage.batch.renderLayers.append([datablock.name, [1, datablock]])

  # worlds
  if datablock.rna_type.identifier == 'World':
    storage.batch.worlds.append([datablock.name, [1, datablock]])

  # libraries
  if datablock.rna_type.identifier == 'Library':
    storage.batch.libraries.append([datablock.name, [1, datablock]])

  # images
  if datablock.rna_type.identifier == 'Image':
    storage.batch.images.append([datablock.name, [1, datablock]])

  # masks
  if datablock.rna_type.identifier == 'Mask':
    storage.batch.masks.append([datablock.name, [1, datablock]])

  # sequences
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier == 'Sequence':
      storage.batch.sequences.append([datablock.name, [1, datablock]])

  # movie clips
  if datablock.rna_type.identifier == 'MovieClip':
    storage.batch.movieClips.append([datablock.name, [1, datablock]])

  # sounds
  if datablock.rna_type.identifier == 'Sound':
    storage.batch.sounds.append([datablock.name, [1, datablock]])

  # screens
  if datablock.rna_type.identifier == 'Screen':
    storage.batch.screens.append([datablock.name, [1, datablock]])

  # keying sets
  if datablock.rna_type.identifier == 'KeyingSet':
    storage.batch.keyingSets.append([datablock.bl_label, [1, datablock]])

  # palettes
  if datablock.rna_type.identifier == 'Palette':
    storage.batch.palettes.append([datablock.name, [1, datablock]])

  # brushes
  if datablock.rna_type.identifier == 'Brush':
    storage.batch.brushes.append([datablock.name, [1, datablock]])

  # nodes
  if hasattr(datablock.rna_type.base, 'base'):
    if hasattr(datablock.rna_type.base.base, 'base'):
      if hasattr(datablock.rna_type.base.base.base, 'identifier'):
        if datablock.rna_type.base.base.base.identifier == 'Node':
          storage.batch.nodes.append([datablock.name, [1, datablock]])

          if tag:
            datablock.label = name(context, datablock.label)

  # node groups
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier == 'NodeTree':
      storage.batch.nodeGroups.append([datablock.name, [1, datablock]])

  # frame nodes
  if datablock.rna_type.identifier == 'NodeFrame':
    storage.batch.nodes.append([datablock.name, [1, datablock]])

    if tag:
      datablock.label = name(context, datablock.label)

  # texts
  if datablock.rna_type.identifier == 'Text':
    storage.batch.texts.append([datablock.name, [1, datablock]])

def process(context, collection):
  '''
    Process collection, send names to name.
  '''

  # option
  option = context.scene.BatchName

  # counter
  counter = [
    # 'datablock.name', ...
  ]

  # sort
  try:
    collection.sort()
  except:
    pass

  # collection
  for item in collection[:]:

    # sort
    if option.sort:

      # name
      item[0] = name(context, (re.split(r'\W[0-9]*$|_[0-9]*$', item[0]))[0])

    # sort
    else:

      # name
      item[0] = name(context, item[0])

    # count
    counter.append(item[0])

  # start
  i = 0

  # collection
  for item in collection[:]:

    # count
    item[1][0] = counter.count(counter[i])

    # add
    i += 1

  # clear counter
  counter.clear()

  # collection
  for item in collection[:]:

    # sort
    if option.sort:

      # count
      if item[1][0] > 1:

        # name
        if hasattr(item[1][1], 'name'):

          # randomize name
          item[1][1].name = str(random())

        # info
        elif hasattr(item[1][1], 'info'):

          # randomize name
          item[1][1].info = str(random())

        # bl_label
        elif hasattr(item[1][1], 'bl_label'):

          # randomize name
          item[1][1].bl_label = str(random())

      # sort only
      elif not option.sortOnly:

        # name
        if hasattr(item[1][1], 'name'):

          # randomize name
          item[1][1].name = str(random())

        # info
        elif hasattr(item[1][1], 'info'):

          # randomize name
          item[1][1].info = str(random())

        # bl_label
        elif hasattr(item[1][1], 'bl_label'):

          # randomize name
          item[1][1].bl_label = str(random())

    # sort
    else:

      # name
      if hasattr(item[1][1], 'name'):

        # randomize name
        item[1][1].name = str(random())

      # info
      elif hasattr(item[1][1], 'info'):

        # randomize name
        item[1][1].info = str(random())

      # bl_label
      elif hasattr(item[1][1], 'bl_label'):

        # randomize name
        item[1][1].bl_label = str(random())

  # list
  list = []

  # sort
  if option.sort:

    # start
    i = 0

    # datablocks
    for item in collection[:]:

      # count
      if item[1][0] > 1:

        # duplicates
        if item[0] not in list:

          # suffix last
          if option.suffixLast:

            # rename
            rename = item[0] + option.separator + '0'*option.padding + str(i + option.start).zfill(len(str(item[1][0]))) + option.suffix

          # suffix lasr
          else:

            # rename
            rename = item[0] + option.separator + '0'*option.padding + str(i + option.start).zfill(len(str(item[1][0])))

          # name
          if hasattr(item[1][1], 'name'):

            # rename
            item[1][1].name = rename

          # info
          elif hasattr(item[1][1], 'info'):

            # rename
            item[1][1].info = rename

          # bl_label
          elif hasattr(item[1][1], 'bl_label'):

            # rename
            item[1][1].bl_label = rename

          # add
          i += 1

        # count
        if i == item[1][0]:

          # reset
          i = 0

          # duplicates
          list.append(item[0])

  # sort only
  if not option.sortOnly:

    # collection
    for item in collection[:]:

      # duplicates
      if item[0] not in list:

        # suffix last
        if option.suffixLast:

          # rename
          rename = item[0] + option.suffix

        # suffix last
        else:

          # rename
          rename = item[0]

        # name
        if hasattr(item[1][1], 'name'):

          # rename
          item[1][1].name = rename

        # info
        elif hasattr(item[1][1], 'info'):

          # rename
          item[1][1].info = rename

        # bl_label
        elif hasattr(item[1][1], 'bl_label'):

          # rename
          item[1][1].bl_label = rename

  # link
  if option.link:

    try:

      list = []

      for item in collection[:]:

        if item[0] not in list:

          source = item[1]

          # source[1].name = re.split(r'\W[0-9]*$|_[0-9]*$', source[1].name)[0]

          list.append(item[0])

        if item[1][1] != source[1]:

          # actions
          if item[1][1].rna_type.identifier == 'Action':
            item[1][2].action = source[1]

          # grease pencils
          if item[1][1].rna_type.identifier == 'GreasePencil':
            item[1][2].grease_pencil = source[1]

          # cameras
          if item[1][1].rna_type.identifier == 'Camera':
            item[1][2].data = source[1]

          # meshes
          if item[1][1].rna_type.identifier == 'Mesh':
            item[1][2].data = source[1]

          # curves
          if item[1][1].rna_type.identifier in {'SurfaceCurve', 'TextCurve', 'Curve'}:
            item[1][2].data = source[1]

          # lamps
          if hasattr(item[1][1].rna_type.base, 'identifier'):
            if item[1][1].rna_type.base.identifier == 'Lamp':
              item[1][2].data = source[1]

          # lattices
          if item[1][1].rna_type.identifier == 'Lattice':
            item[1][2].data = source[1]

          # metaballs
          if item[1][1].rna_type.identifier == 'MetaBall':
            item[1][2].data = source[1]

          # speakers
          if item[1][1].rna_type.identifier == 'Speaker':
            item[1][2].data = source[1]

          # armatures
          if item[1][1].rna_type.identifier == 'Armature':
            item[1][2].data = source[1]

          # materials
          if item[1][1].rna_type.identifier == 'Material':
            item[1][2].material = source[1]

          # textures
          if hasattr(item[1][1].rna_type.base, 'identifier'):
            if item[1][1].rna_type.base.identifier == 'Texture':
              item[1][2].texture = source[1]

          # particle settings
          if item[1][1].rna_type.identifier == 'ParticleSettings':
            item[1][2].settings = source[1]

    except:
      pass

# name
def name(context, oldName):
  '''
    Name datablocks received from process.
  '''

  # option
  option = context.scene.BatchName

  # name check
  nameCheck = oldName

  # custom name
  if option.customName != '':

    # new name
    newName = option.customName
  else:

    # new name
    newName = oldName

  # trim start
  newName = newName[option.trimStart:]

  # trim end
  if option.trimEnd > 0:
    newName = newName[:-option.trimEnd]

  # find & replace
  if option.regex:
    newName = re.sub(option.find, option.replace, newName)
  else:
    newName = re.sub(re.escape(option.find), option.replace, newName)

  # prefix & suffix
  newName = option.prefix + newName + option.suffix if not option.suffixLast else option.prefix + newName

  # name check
  if nameCheck != newName:
    return newName
  else:
    return oldName
