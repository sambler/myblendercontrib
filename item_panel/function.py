
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
from . import storage

###############
## FUNCTIONS ##
###############

# batch
class batch:
  '''
  Contains Class;
    shared
    auto

  Contains Functions;
    main
    process
    name
    copy
    resetSettings
    transferSettings
  '''

  # count
  count = 0

  # tag
  tag = False

  # shared
  class shared:
    '''
      Contains Lists;
        actions
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

  # auto
  class auto:
    '''
      Contains Functions;
        main
        name
    '''

    # name
    def main(context):
      '''
        Send datablock values to name.
      '''

      # option
      option = context.scene.batchAutoNameSettings

      # name
      name = batch.auto.name

      # batch type
      if option.batchType in {'SELECTED', 'OBJECTS'}:

        for object in bpy.data.objects[:]:

          # objects
          if option.objects:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:

                # object type
                if option.objectType in 'ALL':

                  # name
                  name(context, object, True, False, False, False)

                # object type
                elif option.objectType in object.type:

                  # name
                  name(context, object, True, False, False, False)

            # batch type
            else:

              # object type
              if option.objectType in 'ALL':

                # name
                name(context, object, True, False, False, False)

              # object type
              elif option.objectType in object.type:

                # name
                name(context, object, True, False, False, False)

          # constraints
          if option.constraints:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for constraint in object.constraints[:]:

                  # constraint type
                  if option.constraintType in 'ALL':

                    # name
                    name(context, constraint, False, True, False, False)

                  # constraint type
                  elif option.constraintType in constraint.type:

                    # name
                    name(context, constraint, False, True, False, False)

            # batch type
            else:
              for constraint in object.constraints[:]:

                # constraint type
                if option.constraintType in 'ALL':

                  # name
                  name(context, constraint, False, True, False, False)

                # constraint type
                elif option.constraintType in constraint.type:

                  # name
                  name(context, constraint, False, True, False, False)

          # modifiers
          if option.modifiers:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for modifier in object.modifiers[:]:

                  # modifier type
                  if option.modifierType in 'ALL':

                    # name
                    name(context, modifier, False, False, True, False)

                  # modifier type
                  elif option.modifierType in modifier.type:

                    # name
                    name(context, modifier, False, False, True, False)
            else:
              for modifier in object.modifiers[:]:

                # modifier type
                if option.modifierType in 'ALL':

                  # name
                  name(context, modifier, False, False, True, False)

                # modifier type
                elif option.modifierType in modifier.type:

                  # name
                  name(context, modifier, False, False, True, False)

          # object data
          if option.objectData:
            if object.type not in 'EMPTY':

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:

                  # object type
                  if option.objectType in 'ALL':

                    # name
                    name(context, object, False, False, False, True)

                  # object type
                  elif option.objectType in object.type:

                    # name
                    name(context, object, False, False, False, True)

              # batch type
              else:

                # object type
                if option.objectType in 'ALL':

                  # name
                  name(context, object, False, False, False, True)

                # object type
                elif option.objectType in object.type:

                  # name
                  name(context, object, False, False, False, True)

          # bone constraints
          if option.boneConstraints:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                if object.type in 'ARMATURE':
                  for bone in object.pose.bones[:]:
                    if bone.bone.select:
                      for constraint in bone.constraints[:]:

                        # constraint type
                        if option.constraintType in 'ALL':

                          # name
                          name(context, constraint, False, True, False, False)

                        # constraint type
                        elif option.constraintType in constraint.type:

                          # name
                          name(context, constraint, False, True, False, False)
            else:
              if object.type in 'ARMATURE':
                for bone in object.pose.bones[:]:
                  for constraint in bone.constraints[:]:

                    # constraint type
                    if option.constraintType in 'ALL':

                      # name
                      name(context, constraint, False, True, False, False)

                    # constraint type
                    elif option.constraintType in constraint.type:

                      # name
                      name(context, constraint, False, True, False, False)

      # batch type
      else:
        for object in context.scene.objects[:]:

          # objects
          if option.objects:

            # object type
            if option.objectType in 'ALL':

              # name
              name(context, object, True, False, False, False)

            # object type
            elif option.objectType in object.type:

              # name
              name(context, object, True, False, False, False)

          # constraints
          if option.constraints:
            for constraint in object.constraints[:]:

              # constraint type
              if option.constraintType in 'ALL':

                # name
                name(context, constraint, False, True, False, False)

              # constraint type
              elif option.constraintType in constraint.type:

                # name
                name(context, constraint, False, True, False, False)

          # modifiers
          if option.modifiers:
            for modifier in object.modifiers[:]:

              # modifier type
              if option.modifierType in 'ALL':

                # name
                name(context, modifier, False, False, True, False)

              # modifier type
              elif option.modifierType in modifier.type:

                # name
                name(context, modifier, False, False, True, False)

          # object data
          if option.objectData:
            if object.type not in 'EMPTY':

              # object type
              if option.objectType in 'ALL':

                # name
                name(context, object, False, False, False, True)

              # object type
              elif option.objectType in object.type:

                # name
                name(context, object, False, False, False, True)

          # bone constraints
          if option.boneConstraints:
            if object.type in 'ARMATURE':
              for bone in object.pose.bones[:]:
                for constraint in bone.constraints[:]:

                  # constraint type
                  if option.constraintType in 'ALL':

                    # name
                    name(context, constraint, False, True, False, False)

                  # constraint type
                  elif option.constraintType in constraint.type:

                    # name
                    name(context, constraint, False, True, False, False)

    # object
    def name(context, datablock, object, constraint, modifier, objectData):
      '''
        Change the datablock names based on its type.
      '''

      # option
      option = context.scene.batchAutoNameSettings

      # object name
      objectName = context.scene.batchAutoNameObjectNames

      # constraint name
      constraintName = context.scene.batchAutoNameConstraintNames

      # modifier name
      modifierName = context.scene.batchAutoNameModifierNames

      # object data name
      objectDataName = context.scene.batchAutoNameObjectDataNames

      # object
      if object:

        # mesh
        if datablock.type in 'MESH':
          datablock.name = objectName.mesh

        # curve
        if datablock.type in 'CURVE':
          datablock.name = objectName.curve

        # surface
        if datablock.type in 'SURFACE':
          datablock.name = objectName.surface

        # meta
        if datablock.type in 'META':
          datablock.name = objectName.meta

        # font
        if datablock.type in 'FONT':
          datablock.name = objectName.font

        # armature
        if datablock.type in 'ARMATURE':
          datablock.name = objectName.armature

        # lattice
        if datablock.type in 'LATTICE':
          datablock.name = objectName.lattice

        # empty
        if datablock.type in 'EMPTY':
          datablock.name = objectName.empty

        # speaker
        if datablock.type in 'SPEAKER':
          datablock.name = objectName.speaker

        # camera
        if datablock.type in 'CAMERA':
          datablock.name = objectName.camera

        # lamp
        if datablock.type in 'LAMP':
          datablock.name = objectName.lamp

      # constraint (bone constraint)
      if constraint:

        # camera solver
        if datablock.type in 'CAMERA_SOLVER':
          datablock.name = constraintName.cameraSolver

        # follow track
        if datablock.type in 'FOLLOW_TRACK':
          datablock.name = constraintName.followTrack

        # object solver
        if datablock.type in 'OBJECT_SOLVER':
          datablock.name = constraintName.objectSolver

        # copy location
        if datablock.type in 'COPY_LOCATION':
          datablock.name = constraintName.copyLocation

        # copy rotation
        if datablock.type in 'COPY_ROTATION':
          datablock.name = constraintName.copyRotation

        # copy scale
        if datablock.type in 'COPY_SCALE':
          datablock.name = constraintName.copyScale

        # copy transforms
        if datablock.type in 'COPY_TRANSFORMS':
          datablock.name = constraintName.copyTransforms

        # limit distance
        if datablock.type in 'LIMIT_DISTANCE':
          datablock.name = constraintName.limitDistance

        # limit location
        if datablock.type in 'LIMIT_LOCATION':
          datablock.name = constraintName.limitLocation

        # limit rotation
        if datablock.type in 'LIMIT_ROTATION':
          datablock.name = constraintName.limitRotation

        # limit scale
        if datablock.type in 'LIMIT_SCALE':
          datablock.name = constraintName.limitScale

        # maintain volume
        if datablock.type in 'MAINTAIN_VOLUME':
          datablock.name = constraintName.maintainVolume

        # transform
        if datablock.type in 'TRANSFORM':
          datablock.name = constraintName.transform

        # clamp to
        if datablock.type in 'CLAMP_TO':
          datablock.name = constraintName.clampTo

        # damped track
        if datablock.type in 'DAMPED_TRACK':
          datablock.name = constraintName.dampedTrack

        # inverse kinematics
        if datablock.type in 'IK':
          datablock.name = constraintName.inverseKinematics

        # locked track
        if datablock.type in 'LOCKED_TRACK':
          datablock.name = constraintName.lockedTrack

        # spline inverse kinematics
        if datablock.type in 'SPLINE_IK':
          datablock.name = constraintName.splineInverseKinematics

        # stretch to
        if datablock.type in 'STRETCH_TO':
          datablock.name = constraintName.stretchTo

        # track to
        if datablock.type in 'TRACK_TO':
          datablock.name = constraintName.trackTo

        # action
        if datablock.type in 'ACTION':
          datablock.name = constraintName.action

        # child of
        if datablock.type in 'CHILD_OF':
          datablock.name = constraintName.childOf

        # floor
        if datablock.type in 'FLOOR':
          datablock.name = constraintName.floor

        # follor path
        if datablock.type in 'FOLLOW_PATH':
          datablock.name = constraintName.followPath

        # pivot
        if datablock.type in 'PIVOT':
          datablock.name = constraintName.pivot

        # rigid body joint
        if datablock.type in 'RIGID_BODY_JOINT':
          datablock.name = constraintName.rigidBodyJoint

        # shrinkwrap
        if datablock.type in 'SHRINKWRAP':
          datablock.name = constraintName.shrinkwrap

      # modifier
      if modifier:

        # data transfer
        if datablock.type in 'DATA_TRANSFER':
          datablock.name = modifierName.dataTransfer

        # mesh cache
        if datablock.type in 'MESH_CACHE':
          datablock.name = modifierName.meshCache

        # normal edit
        if datablock.type in 'NORMAL_EDIT':
          datablock.name = modifierName.normalEdit

        # uv project
        if datablock.type in 'UV_PROJECT':
          datablock.name = modifierName.uvProject

        # uv warp
        if datablock.type in 'UV_WARP':
          datablock.name = modifierName.uvWarp

        # vertex weight edit
        if datablock.type in 'VERTEX_WEIGHT_EDIT':
          datablock.name = modifierName.vertexWeightEdit

        # vertex weight mix
        if datablock.type in 'VERTEX_WEIGHT_MIX':
          datablock.name = modifierName.vertexWeightMix

        # vertex weight proximity
        if datablock.type in 'VERTEX_WEIGHT_PROXIMITY':
          datablock.name = modifierName.vertexWeightProximity

        # array
        if datablock.type in 'ARRAY':
          datablock.name = modifierName.array

        # bevel
        if datablock.type in 'BEVEL':
          datablock.name = modifierName.bevel

        # boolean
        if datablock.type in 'BOOLEAN':
          datablock.name = modifierName.boolean

        # build
        if datablock.type in 'BUILD':
          datablock.name = modifierName.build

        # decimate
        if datablock.type in 'DECIMATE':
          datablock.name = modifierName.decimate

        # edge split
        if datablock.type in 'EDGE_SPLIT':
          datablock.name = modifierName.edgeSplit

        # mask
        if datablock.type in 'MASK':
          datablock.name = modifierName.mask

        # mirror
        if datablock.type in 'MIRROR':
          datablock.name = modifierName.mirror

        # multiresolution
        if datablock.type in 'MULTIRES':
          datablock.name = modifierName.multiresolution

        # remesh
        if datablock.type in 'REMESH':
          datablock.name = modifierName.remesh

        # screw
        if datablock.type in 'SCREW':
          datablock.name = modifierName.screw

        # skin
        if datablock.type in 'SKIN':
          datablock.name = modifierName.skin

        # solidify
        if datablock.type in 'SOLIDIFY':
          datablock.name = modifierName.solidify

        # subdivision surface
        if datablock.type in 'SUBSURF':
          datablock.name = modifierName.subdivisionSurface

        # triangulate
        if datablock.type in 'TRIANGULATE':
          datablock.name = modifierName.triangulate

        # wireframe
        if datablock.type in 'WIREFRAME':
          datablock.name = modifierName.wireframe

        # armature
        if datablock.type in 'ARMATURE':
          datablock.name = modifierName.armature

        # cast
        if datablock.type in 'CAST':
          datablock.name = modifierName.cast

        # corrective smooth
        if datablock.type in 'CORRECTIVE_SMOOTH':
          datablock.name = modifierName.correctiveSmooth

        # curve
        if datablock.type in 'CURVE':
          datablock.name = modifierName.curve

        # displace
        if datablock.type in 'DISPLACE':
          datablock.name = modifierName.displace

        # hook
        if datablock.type in 'HOOK':
          datablock.name = modifierName.hook

        # laplacian smooth
        if datablock.type in 'LAPLACIANSMOOTH':
          datablock.name = modifierName.laplacianSmooth

        # laplacian deform
        if datablock.type in 'LAPLACIANDEFORM':
          datablock.name = modifierName.laplacianDeform

        # lattice
        if datablock.type in 'LATTICE':
          datablock.name = modifierName.lattice

        # mesh deform
        if datablock.type in 'MESH_DEFORM':
          datablock.name = modifierName.meshDeform

        # shrinkwrap
        if datablock.type in 'SHRINKWRAP':
          datablock.name = modifierName.shrinkwrap

        # simple deform
        if datablock.type in 'SIMPLE_DEFORM':
          datablock.name = modifierName.simpleDeform

        # smooth
        if datablock.type in 'SMOOTH':
          datablock.name = modifierName.smooth

        # warp
        if datablock.type in 'WARP':
          datablock.name = modifierName.warp

        # wave
        if datablock.type in 'WAVE':
          datablock.name = modifierName.wave

        # cloth
        if datablock.type in 'CLOTH':
          datablock.name = modifierName.cloth

        # collision
        if datablock.type in 'COLLISION':
          datablock.name = modifierName.collision

        # dynamic paint
        if datablock.type in 'DYNAMIC_PAINT':
          datablock.name = modifierName.dynamicPaint

        # explode
        if datablock.type in 'EXPLODE':
          datablock.name = modifierName.explode

        # fluid simulation
        if datablock.type in 'FLUID_SIMULATION':
          datablock.name = modifierName.fluidSimulation

        # ocean
        if datablock.type in 'OCEAN':
          datablock.name = modifierName.ocean

        # particle instance
        if datablock.type in 'PARTICLE_INSTANCE':
          datablock.name = modifierName.particleInstance

        # particle system
        if datablock.type in 'PARTICLE_SYSTEM':
          datablock.name = modifierName.particleSystem

        # smoke
        if datablock.type in 'SMOKE':
          datablock.name = modifierName.smoke

        # soft body
        if datablock.type in 'SOFT_BODY':
          datablock.name = modifierName.softBody

      # object data
      if objectData:

        # mesh
        if datablock.type in 'MESH':
          datablock.data.name = objectDataName.mesh

        # curve
        if datablock.type in 'CURVE':
          datablock.data.name = objectDataName.curve

        # surface
        if datablock.type in 'SURFACE':
          datablock.data.name = objectDataName.surface

        # meta
        if datablock.type in 'META':
          datablock.data.name = objectDataName.meta

        # font
        if datablock.type in 'FONT':
          datablock.data.name = objectDataName.font

        # armature
        if datablock.type in 'ARMATURE':
          datablock.data.name = objectDataName.armature

        # lattice
        if datablock.type in 'LATTICE':
          datablock.data.name = objectDataName.lattice

        # empty
        if datablock.type in 'EMPTY':
          datablock.data.name = objectDataName.empty

        # speaker
        if datablock.type in 'SPEAKER':
          datablock.data.name = objectDataName.speaker

        # camera
        if datablock.type in 'CAMERA':
          datablock.data.name = objectDataName.camera

        # lamp
        if datablock.type in 'LAMP':
          datablock.data.name = objectDataName.lamp

  # main
  def main(context):
    '''
      Send datablock values to sort then send collections to process.
    '''

    # option
    option = context.scene.batchNameSettings

    # batch type
    if option.batchType in {'SELECTED', 'OBJECTS'}:

      # objects
      if option.objects:
        for object in bpy.data.objects[:]:

          # batch type
          if option.batchType in 'SELECTED':
            if object.select:

              # object type
              if option.objectType in 'ALL':

                # sort
                batch.sort(context, object)

              # object type
              elif option.objectType in object.type:

                # sort
                batch.sort(context, object)

          # batch type
          else:

            # object type
            if option.objectType in 'ALL':

              # sort
              batch.sort(context, object)

            # object type
            elif option.objectType in object.type:

              # sort
              batch.sort(context, object)

      # groups
      if option.groups:
        for object in bpy.data.objects[:]:

          # batch type
          if option.batchType in 'SELECTED':
            if object.select:

              # object type
              if option.objectType in 'ALL':
                for group in bpy.data.groups[:]:
                  if object in group.objects[:]:

                    # sort
                    batch.sort(context, group)

              # object type
              elif option.objectType in object.type:
                for group in bpy.data.groups[:]:
                  if object in group.objects[:]:

                    # sort
                    batch.sort(context, group)

          # batch type
          else:

              # object type
              if option.objectType in 'ALL':
                for group in bpy.data.groups[:]:
                  if object in group.objects[:]:

                    # sort
                    batch.sort(context, group)

              # object type
              elif option.objectType in object.type:
                for group in bpy.data.groups[:]:
                  if object in group.objects[:]:

                    # sort
                    batch.sort(context, group)

      # actions
      if option.actions:
        for object in bpy.data.objects[:]:
          if hasattr(object.animation_data, 'action'):
            if hasattr(object.animation_data.action, 'name'):

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:

                  # object type
                  if option.objectType in 'ALL':

                    # sort
                    batch.sort(context, object.animation_data.action)

                  # object type
                  elif option.objectType in object.type:

                    # sort
                    batch.sort(context, object.animation_data.action)

              # batch type
              else:

                # object type
                if option.objectType in 'ALL':

                  # sort
                  batch.sort(context, object.animation_data.action)

                # object type
                elif option.objectType in object.type:

                  # sort
                  batch.sort(context, object.animation_data.action)

      # grease pencil
      if option.greasePencil:
        for object in bpy.data.objects[:]:
          if hasattr(object.grease_pencil, 'name'):

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:

                # object type
                if option.objectType in 'ALL':
                  if object.grease_pencil.users == 1:

                    # sort
                    batch.sort(context, object.grease_pencil)

                    # layers
                    for layer in object.grease_pencil.layers[:]:

                      # sort
                      batch.sort(context, layer)
                  else:

                    # shared
                    if object.grease_pencil not in batch.shared.greasePencils[:]:
                      batch.shared.greasePencils.append(object.grease_pencil)

                      # sort
                      batch.sort(context, object.grease_pencil)

                      # layers
                      for layer in object.grease_pencil.layers[:]:

                        # sort
                        batch.sort(context, layer)

                # object type
                elif option.objectType in object.type:
                  if object.grease_pencil.users == 1:

                    # sort
                    batch.sort(context, object.grease_pencil)

                    # layers
                    for layer in object.grease_pencil.layers[:]:

                      # sort
                      batch.sort(context, layer)
                  else:

                    # shared
                    if object.grease_pencil not in batch.shared.greasePencils[:]:
                      batch.shared.greasePencils.append(object.grease_pencil)

                      # sort
                      batch.sort(context, object.grease_pencil)

                      # layers
                      for layer in object.grease_pencil.layers[:]:

                        # sort
                        batch.sort(context, layer)

            # batch type
            else:

                # object type
                if option.objectType in 'ALL':
                  if object.grease_pencil.users == 1:

                    # sort
                    batch.sort(context, object.grease_pencil)

                    # layers
                    for layer in object.grease_pencil.layers[:]:

                      # sort
                      batch.sort(context, layer)
                  else:

                    # shared
                    if object.grease_pencil not in batch.shared.greasePencils[:]:
                      batch.shared.greasePencils.append(object.grease_pencil)

                      # sort
                      batch.sort(context, object.grease_pencil)

                      # layers
                      for layer in object.grease_pencil.layers[:]:

                        # sort
                        batch.sort(context, layer)

                # object type
                elif option.objectType in object.type:
                  if object.grease_pencil.users == 1:

                    # sort
                    batch.sort(context, object.grease_pencil)

                    # layers
                    for layer in object.grease_pencil.layers[:]:

                      # sort
                      batch.sort(context, layer)
                  else:

                    # shared
                    if object.grease_pencil not in batch.shared.greasePencils[:]:
                      batch.shared.greasePencils.append(object.grease_pencil)

                      # sort
                      batch.sort(context, object.grease_pencil)

                      # layers
                      for layer in object.grease_pencil.layers[:]:

                        # sort
                        batch.sort(context, layer)

        # clear shared
        batch.shared.greasePencils.clear()

      # constraints
      if option.constraints:
        for object in bpy.data.objects[:]:

          # batch type
          if option.batchType in 'SELECTED':
            if object.select:
              for constraint in object.constraints[:]:

                # constraint type
                if option.constraintType in 'ALL':

                  # sort
                  batch.sort(context, constraint)

                # constraint type
                elif option.constraintType in constraint.type:

                  # sort
                  batch.sort(context, constraint)

          # batch type
          else:
            for constraint in object.constraints[:]:

              # constraint type
              if option.constraintType in 'ALL':

                # sort
                batch.sort(context, constraint)

              # constraint type
              elif option.constraintType in constraint.type:

                # sort
                batch.sort(context, constraint)

      # modifiers
      if option.modifiers:
        for object in bpy.data.objects[:]:

          # batch type
          if option.batchType in 'SELECTED':
            if object.select:
              for modifier in object.modifiers[:]:

                # modifier type
                if option.modifierType in 'ALL':

                  # sort
                  batch.sort(context, modifier)

                # modifier tye
                elif option.modifierType in modifier.type:

                  # sort
                  batch.sort(context, modifier)

          # batch type
          else:
            for modifier in object.modifiers[:]:

              # modifier type
              if option.modifierType in 'ALL':

                # sort
                batch.sort(context, modifier)

              # modifier tye
              elif option.modifierType in modifier.type:

                # sort
                batch.sort(context, modifier)

      # object data
      if option.objectData:
        for object in bpy.data.objects[:]:
          if object.type not in 'EMPTY':

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:

                # object type
                if option.objectType in 'ALL':
                  if object.data.users == 1:

                    # sort
                    batch.sort(context, object.data)
                  else:

                    # shared shared
                    if object.data.name not in batch.shared.objectData[:]:
                      batch.shared.objectData.append(object.data.name)

                      # sort
                      batch.sort(context, object.data)

                # object type
                elif option.objectType in object.type:
                  if object.data.users == 1:

                    # sort
                    batch.sort(context, object.data)
                  else:

                    # shared shared
                    if object.data.name not in batch.shared.objectData[:]:
                      batch.shared.objectData.append(object.data.name)

                      # sort
                      batch.sort(context, object.data)

            # batch type
            else:

              # object type
              if option.objectType in 'ALL':
                if object.data.users == 1:

                  # sort
                  batch.sort(context, object.data)
                else:

                  # shared shared
                  if object.data.name not in batch.shared.objectData[:]:
                    batch.shared.objectData.append(object.data.name)

                    # sort
                    batch.sort(context, object.data)

              # object type
              elif option.objectType in object.type:
                if object.data.users == 1:

                  # sort
                  batch.sort(context, object.data)
                else:

                  # shared shared
                  if object.data.name not in batch.shared.objectData[:]:
                    batch.shared.objectData.append(object.data.name)

                    # sort
                    batch.sort(context, object.data)

        # clear shared
        batch.shared.objectData.clear()

      # bone groups
      if option.boneGroups:
        for object in bpy.data.objects[:]:

          # batch type
          if option.batchType in 'SELECTED':
            if object.select:
              if object.type in 'ARMATURE':
                for group in object.pose.bone_groups[:]:
                  if object.select:

                    # sort
                    batch.sort(context, group)

          # batch type
          else:
            if object.type in 'ARMATURE':
              for group in object.pose.bone_groups[:]:

                # sort
                batch.sort(context, group)

      # bones
      if option.bones:
        for object in bpy.data.objects[:]:

          # batch type
          if option.batchType in 'SELECTED':
            if object.select:
              if object.type in 'ARMATURE':

                # edit mode
                if object.mode in 'EDIT':
                  for bone in bpy.data.armatures[object.data.name].edit_bones[:]:
                    if bone.select:

                      # sort
                      batch.sort(context, bone)

                # pose or object mode
                else:
                  for bone in bpy.data.armatures[object.data.name].bones[:]:
                    if bone.select:

                      # sort
                      batch.sort(context, bone)

          # batch type
          else:
            if object.type in 'ARMATURE':

              # edit mode
              if object.mode in 'EDIT':
                for bone in bpy.data.armatures[object.data.name].edit_bones[:]:

                    # sort
                    batch.sort(context, bone)

              # pose or object mode
              else:
                for bone in bpy.data.armatures[object.data.name].bones[:]:

                    # sort
                    batch.sort(context, bone)

      # bone constraints
      if option.boneConstraints:
        for object in bpy.data.objects[:]:

          # batch type
          if option.batchType in 'SELECTED':
            if object.select:
              if object.type in 'ARMATURE':
                for bone in object.pose.bones[:]:
                  if bone.bone.select:
                    for constraint in bone.constraints[:]:

                      # constraint type
                      if option.constraintType in 'ALL':

                        # sort
                        batch.sort(context, constraint)

                      # constraint type
                      elif option.constraintType in constraint.type:

                        # sort
                        batch.sort(context, constraint)

          # batch type
          else:
            if object.type in 'ARMATURE':
              for bone in object.pose.bones[:]:
                for constraint in bone.constraints[:]:

                  # constraint type
                  if option.constraintType in 'ALL':

                    # sort
                    batch.sort(context, constraint)

                  # constraint type
                  elif option.constraintType in constraint.type:

                    # sort
                    batch.sort(context, constraint)

      # vertex groups
      if option.vertexGroups:
        for object in bpy.data.objects[:]:
          if hasattr(object, 'vertex_groups'):

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for group in object.vertex_groups[:]:

                  # object type
                  if option.objectType in 'ALL':

                    # sort
                    batch.sort(context, group)

                  # object type
                  elif option.objectType in object.type:

                    # sort
                    batch.sort(context, group)

            # batch type
            else:
              for group in object.vertex_groups[:]:

                # object type
                if option.objectType in 'ALL':

                  # sort
                  batch.sort(context, group)

                # object type
                elif option.objectType in object.type:

                  # sort
                  batch.sort(context, group)

      # shapekeys
      if option.shapekeys:
        for object in bpy.data.objects[:]:
          if hasattr(object.data, 'shape_keys'):
            if hasattr(object.data.shape_keys, 'key_blocks'):

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for block in object.data.shape_keys.key_blocks[:]:

                    # object type
                    if option.objectType in 'ALL':

                      # sort
                      batch.sort(context, block)

                    # object type
                    elif option.objectType in object.type:

                      # sort
                      batch.sort(context, block)

              # batch type
              else:
                for block in object.data.shape_keys.key_blocks[:]:

                  # object type
                  if option.objectType in 'ALL':

                    # sort
                    batch.sort(context, block)

                  # object type
                  elif option.objectType in object.type:

                    # sort
                    batch.sort(context, block)

      # uvs
      if option.uvs:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for uv in object.data.uv_textures[:]:

                  # sort
                  batch.sort(context, uv)

            # batch type
            else:
             for uv in object.data.uv_textures[:]:

                # sort
                batch.sort(context, uv)

      # vertex colors
      if option.vertexColors:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for color in object.data.vertex_colors[:]:

                  # sort
                  batch.sort(context, color)

            # batch type
            else:
              for color in object.data.vertex_colors[:]:

                # sort
                batch.sort(context, color)

      # materials
      if option.materials:
        for object in bpy.data.objects[:]:

          # batch type
          if option.batchType in 'SELECTED':
            if object.select:
              for slot in object.material_slots[:]:
                if slot.material != None:
                  if slot.material.users == 1:

                    # object type
                    if option.objectType in 'ALL':

                      # sort
                      batch.sort(context, slot.material)

                    # object type
                    elif option.objectType in object.type:

                      # sort
                      batch.sort(context, slot.material)
                  else:

                    # shared
                    if slot.material not in batch.shared.materials[:]:
                      batch.shared.materials.append(slot.material)

                      # sort
                      batch.sort(context, slot.material)

          # batch type
          else:
            for slot in object.material_slots[:]:
              if slot.material != None:
                if slot.material.users == 1:

                  # object type
                  if option.objectType in 'ALL':

                    # sort
                    batch.sort(context, slot.material)

                  # object type
                  elif option.objectType in object.type:

                    # sort
                    batch.sort(context, slot.material)
                else:

                  # shared
                  if slot.material not in batch.shared.materials[:]:
                    batch.shared.materials.append(slot.material)

                    # sort
                    batch.sort(context, slot.material)

        # clear shared
        batch.shared.materials.clear()

      # textures
      if option.textures:
        for object in bpy.data.objects[:]:
          if context.scene.render.engine not in 'CYCLES':

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for slot in object.material_slots[:]:
                  if slot.material != None:
                    if slot.material.users == 1:
                      for texslot in slot.material.texture_slots[:]:
                        if texslot != None:
                          if texslot.texture.users == 1:

                            # object type
                            if option.objectType in 'ALL':

                              # sort
                              batch.sort(context, texslot.texture)

                            # object type
                            elif option.objectType in object.type:

                              # sort
                              batch.sort(context, texslot.texture)
                          else:

                            # shared
                            if texslot.texture not in batch.shared.textures[:]:
                              batch.shared.textures.append(texslot.texture)

                              # sort
                              batch.sort(context, texslot.texture)
                    else:

                      # shared
                      if slot.material not in batch.shared.materials[:]:
                        batch.shared.materials.append(slot.material)
                        for texslot in slot.material.texture_slots[:]:
                          if texslot != None:
                            if texslot.texture.users == 1:

                              # object type
                              if option.objectType in 'ALL':

                                # sort
                                batch.sort(context, texslot.texture)

                              # object type
                              elif option.objectType in object.type:

                                # sort
                                batch.sort(context, texslot.texture)
                            else:

                              # shared
                              if texslot.texture not in batch.shared.textures[:]:
                                batch.shared.textures.append(texslot.texture)

                                # sort
                                batch.sort(context, texslot.texture)

            # batch type
            else:
              for slot in object.material_slots[:]:
                if slot.material != None:
                  if slot.material.users == 1:
                    for texslot in slot.material.texture_slots[:]:
                      if texslot != None:
                        if texslot.texture.users == 1:

                          # object type
                          if option.objectType in 'ALL':

                            # sort
                            batch.sort(context, texslot.texture)

                          # object type
                          elif option.objectType in object.type:

                            # sort
                            batch.sort(context, texslot.texture)
                        else:

                          # shared
                          if texslot.texture not in batch.shared[:]:
                            batch.shared.append(texslot.texture)

                            # sort
                            batch.sort(context, texslot.texture)
                  else:

                    # shared
                    if slot.material not in batch.shared.materials[:]:
                      batch.shared.materials.append(slot.material)
                      for texslot in slot.material.texture_slots[:]:
                        if texslot != None:
                          if texslot.texture.users == 1:

                            # object type
                            if option.objectType in 'ALL':

                              # sort
                              batch.sort(context, texslot.texture)

                            # object type
                            elif option.objectType in object.type:

                              # sort
                              batch.sort(context, texslot.texture)
                          else:

                            # shared
                            if texslot.texture not in batch.shared.textures[:]:
                              batch.shared.textures.append(texslot.texture)

                              # sort
                              batch.sort(context, texslot.texture)

        # clear shared
        batch.shared.textures.clear()

      # particle systems
      if option.particleSystems:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for system in object.particle_systems[:]:

                  # object type
                  if option.objectType in 'ALL':

                    # sort
                    batch.sort(context, system)

                  # object type
                  elif option.objectType in object.type:

                    # sort
                    batch.sort(context, system)

            # batch type
            else:
              for system in object.particle_systems[:]:

                # object type
                if option.objectType in 'ALL':

                  # sort
                  batch.sort(context, system)

                # object type
                elif option.objectType in object.type:

                  # sort
                  batch.sort(context, system)

      # particle settings
      if option.particleSettings:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for system in object.particle_systems[:]:

                  # object type
                  if option.objectType in 'ALL':
                    if system.settings.users == 1:

                      # sort
                      batch.sort(context, system.settings)
                    else:

                      # shared
                      if system.settings not in batch.shared.particleSettings[:]:
                        batch.shared.particleSettings.append(system.settings)

                        # sort
                        batch.sort(context, system.settings)

                  # object type
                  elif option.objectType in object.type:
                    if system.settings.users == 1:

                      # sort
                      batch.sort(context, system.settings)
                    else:

                      # shared
                      if system.settings not in batch.shared.particleSettings[:]:
                        batch.shared.particleSettings.append(system.settings)

                        # sort
                        batch.sort(context, system.settings)

            # batch type
            else:
              for system in object.particle_systems[:]:

                # object type
                if option.objectType in 'ALL':
                  if system.settings.users == 1:

                    # sort
                    batch.sort(context, system.settings)
                  else:

                    # shared
                    if system.settings not in batch.shared.particleSettings[:]:
                      batch.shared.particleSettings.append(system.settings)

                      # sort
                      batch.sort(context, system.settings)

                # object type
                elif option.objectType in object.type:
                  if system.settings.users == 1:

                    # sort
                    batch.sort(context, system.settings)
                  else:

                    # shared
                    if system.settings not in batch.shared.particleSettings[:]:
                      batch.shared.particleSettings.append(system.settings)

                      # sort
                      batch.sort(context, system.settings)

        # clear shared
        batch.shared.particleSettings.clear()

    # batch type
    if option.batchType in 'SCENE':

      # objects
      if option.objects:
        for object in context.scene.objects[:]:

          # object type
          if option.objectType in 'ALL':

            # sort
            batch.sort(context, object)

          # object type
          elif option.objectType in object.type:

            # sort
            batch.sort(context, object)

      # groups
      if option.groups:
        for object in context.scene.objects[:]:

          # object type
          if option.objectType in 'ALL':
            for group in bpy.data.groups[:]:
              if object in group.objects[:]:

                # sort
                batch.sort(context, group)

          # object type
          elif option.objectType in object.type:
            for group in bpy.data.groups[:]:
              if object in group.objects[:]:

                # sort
                batch.sort(context, group)

      # actions
      if option.actions:
        for object in context.scene.objects[:]:
          if hasattr(object.animation_data, 'action'):
            if hasattr(object.animation_data.action, 'name'):

              # object type
              if option.objectType in 'ALL':

                # sort
                batch.sort(context, object.animation_data.action)

              # object type
              elif option.objectType in object.type:

                # sort
                batch.sort(context, object.animation_data.action)

      # grease pencil
      if option.greasePencil:
        for object in context.scene.objects[:]:
          if hasattr(object.grease_pencil, 'name'):

            # object type
            if option.objectType in 'ALL':
              if object.grease_pencil.users == 1:

                # sort
                batch.sort(context, object.grease_pencil)

                # layers
                for layer in object.grease_pencil.layers[:]:

                  # sort
                  batch.sort(context, layer)
              else:

                # shared
                if object.grease_pencil not in batch.shared.greasePencils[:]:
                  batch.shared.greasePencils.append(object.grease_pencil)

                  # sort
                  batch.sort(context, object.grease_pencil)

                  # layers
                  for layer in object.grease_pencil.layers[:]:

                    # sort
                    batch.sort(context, layer)

            # object type
            elif option.objectType in object.type:
              if object.grease_pencil.users == 1:

                # sort
                batch.sort(context, object.grease_pencil)

                # layers
                for layer in object.grease_pencil.layers[:]:

                  # sort
                  batch.sort(context, layer)
              else:

                # shared
                if object.grease_pencil not in batch.shared.greasePencils[:]:
                  batch.shared.greasePencils.append(object.grease_pencil)

                  # sort
                  batch.sort(context, object.grease_pencil)

                  # layers
                  for layer in object.grease_pencil.layers[:]:

                    # sort
                    batch.sort(context, layer)

        # clear shared
        batch.shared.greasePencils.clear()

      # constraints
      if option.constraints:
        for object in context.scene.objects[:]:
          for constraint in object.constraints[:]:

            # constraint type
            if option.constraintType in 'ALL':

              # sort
              batch.sort(context, constraint)

            # constraint type
            elif option.constraintType in constraint.type:

              # sort
              batch.sort(context, constraint)

      # modifiers
      if option.modifiers:
        for object in context.scene.objects[:]:
          for modifier in object.modifiers[:]:

            # modifier type
            if option.modifierType in 'ALL':

              # sort
              batch.sort(context, modifier)

            # modifier tye
            elif option.modifierType in modifier.type:

              # sort
              batch.sort(context, modifier)

      # object data
      if option.objectData:
        for object in context.scene.objects[:]:
          if object.type not in 'EMPTY':

            # object type
            if option.objectType in 'ALL':
              if object.data.users == 1:

                # sort
                batch.sort(context, object.data)
              else:

                # shared shared
                if object.data.name not in batch.shared.objectData[:]:
                  batch.shared.objectData.append(object.data.name)

                  # sort
                  batch.sort(context, object.data)

            # object type
            elif option.objectType in object.type:
              if object.data.users == 1:

                # sort
                batch.sort(context, object.data)
              else:

                # shared shared
                if object.data.name not in batch.shared.objectData[:]:
                  batch.shared.objectData.append(object.data.name)

                  # sort
                  batch.sort(context, object.data)

        # clear shared
        batch.shared.objectData.clear()

      # bone groups
      if option.boneGroups:
        for object in context.scene.objects[:]:
          if object.type in 'ARMATURE':
            for group in object.pose.bone_groups[:]:

              # sort
              batch.sort(context, group)

      # bones
      if option.bones:
        for object in context.scene.objects[:]:
          if object.type in 'ARMATURE':

            # edit mode
            if object.mode in 'EDIT':
              for bone in bpy.data.armatures[object.data.name].edit_bones[:]:

                  # sort
                  batch.sort(context, bone)

            # pose or object mode
            else:
              for bone in bpy.data.armatures[object.data.name].bones[:]:

                  # sort
                  batch.sort(context, bone)

      # bone constraints
      if option.boneConstraints:
        for object in context.scene.objects[:]:
          if object.type in 'ARMATURE':
            for bone in object.pose.bones[:]:
              for constraint in bone.constraints[:]:

                # constraint type
                if option.constraintType in 'ALL':

                  # sort
                  batch.sort(context, constraint)

                # constraint type
                elif option.constraintType in constraint.type:

                  # sort
                  batch.sort(context, constraint)

      # vertex groups
      if option.vertexGroups:
        for object in context.scene.objects[:]:
          if hasattr(object, 'vertex_groups'):
            for group in object.vertex_groups[:]:

              # object type
              if option.objectType in 'ALL':

                # sort
                batch.sort(context, group)

              # object type
              elif option.objectType in object.type:

                # sort
                batch.sort(context, group)

      # shapekeys
      if option.shapekeys:
        for object in context.scene.objects[:]:
          if hasattr(object.data, 'shape_keys'):
            if hasattr(object.data.shape_keys, 'key_blocks'):
              for block in object.data.shape_keys.key_blocks[:]:

                # object type
                if option.objectType in 'ALL':

                  # sort
                  batch.sort(context, block)

                # object type
                elif option.objectType in object.type:

                  # sort
                  batch.sort(context, block)

      # uvs
      if option.uvs:
        for object in context.scene.objects[:]:
          if object.type in 'MESH':
            for uv in object.data.uv_textures[:]:

              # sort
              batch.sort(context, uv)

      # vertex colors
      if option.vertexColors:
        for object in context.scene.objects[:]:
          if object.type in 'MESH':
            for color in object.data.vertex_colors[:]:

              # sort
              batch.sort(context, color)

      # materials
      if option.materials:
        for object in context.scene.objects[:]:
          for slot in object.material_slots[:]:
            if slot.material != None:
              if slot.material.users == 1:

                # object type
                if option.objectType in 'ALL':

                  # sort
                  batch.sort(context, slot.material)

                # object type
                elif option.objectType in object.type:

                  # sort
                  batch.sort(context, slot.material)
              else:

                # shared
                if slot.material not in batch.shared.materials[:]:
                  batch.shared.materials.append(slot.material)

                  # sort
                  batch.sort(context, slot.material)

        # clear shared
        batch.shared.materials.clear()

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

                          # sort
                          batch.sort(context, texslot.texture)

                        # object type
                        elif option.objectType in object.type:

                          # sort
                          batch.sort(context, texslot.texture)
                      else:

                        # shared
                        if texslot.texture not in batch.shared[:]:
                          batch.shared.append(texslot.texture)

                          # sort
                          batch.sort(context, texslot.texture)
                else:

                  # shared
                  if slot.material not in batch.shared.materials[:]:
                    batch.shared.materials.append(slot.material)
                    for texslot in slot.material.texture_slots[:]:
                      if texslot != None:
                        if texslot.texture.users == 1:

                          # object type
                          if option.objectType in 'ALL':

                            # sort
                            batch.sort(context, texslot.texture)

                          # object type
                          elif option.objectType in object.type:

                            # sort
                            batch.sort(context, texslot.texture)
                        else:

                          # shared
                          if texslot.texture not in batch.shared.textures[:]:
                            batch.shared.textures.append(texslot.texture)

                            # sort
                            batch.sort(context, texslot.texture)

        # clear shared
        batch.shared.textures.clear()

      # particle systems
      if option.particleSystems:
        for object in context.scene.objects[:]:
          if object.type in 'MESH':
            for system in object.particle_systems[:]:

              # object type
              if option.objectType in 'ALL':

                # sort
                batch.sort(context, system)

              # object type
              elif option.objectType in object.type:

                # sort
                batch.sort(context, system)

      # particle settings
      if option.particleSettings:
        for object in context.scene.objects[:]:
          if object.type in 'MESH':
            for system in object.particle_systems[:]:

              # object type
              if option.objectType in 'ALL':
                if system.settings.users == 1:

                  # sort
                  batch.sort(context, system.settings)
                else:

                  # shared
                  if system.settings not in batch.shared.particleSettings[:]:
                    batch.shared.particleSettings.append(system.settings)

                    # sort
                    batch.sort(context, system.settings)

              # object type
              elif option.objectType in object.type:
                if system.settings.users == 1:

                  # sort
                  batch.sort(context, system.settings)
                else:

                  # shared
                  if system.settings not in batch.shared.particleSettings[:]:
                    batch.shared.particleSettings.append(system.settings)

                    # sort
                    batch.sort(context, system.settings)

        # clear shared
        batch.shared.particleSettings.clear()

    # batch type
    elif option.batchType in 'GLOBAL':

      # objects
      if option.objects:
        for object in bpy.data.objects[:]:

          # sort
          batch.sort(context, object)

      # groups
      if option.groups:
        for group in bpy.data.groups[:]:

          # sort
          batch.sort(context, group)

      # actions
      if option.actions:
        for action in bpy.data.actions[:]:

          # sort
          batch.sort(context, action)

      # grease pencil
      if option.greasePencil:
        for pencil in bpy.data.grease_pencil[:]:

          # sort
          batch.sort(context, pencil)

          # layers
          for layer in pencil.layers[:]:

            # sort
            batch.sort(context, layer)

      # constraints
      if option.constraints:
        for object in bpy.data.objects[:]:
          for constraint in object.constraints[:]:

            # sort
            batch.sort(context, constraint)

      # modifiers
      if option.modifiers:
        for object in bpy.data.objects[:]:
          for modifier in object.modifiers[:]:

            # sort
            batch.sort(context, modifier)

      # object data
      if option.objectData:

        # cameras
        for camera in bpy.data.cameras[:]:

          # sort
          batch.sort(context, camera)

        # meshes
        for mesh in bpy.data.meshes[:]:

          # sort
          batch.sort(context, mesh)

        # lamps
        for lamp in bpy.data.lamps[:]:

          # sort
          batch.sort(context, lamp)

        # lattices
        for lattice in bpy.data.lattices[:]:

          # sort
          batch.sort(context, lattice)

        # curves
        for curve in bpy.data.curves[:]:

          # sort
          batch.sort(context, curve)

        # metaballs
        for metaball in bpy.data.metaballs[:]:

          # sort
          batch.sort(context, metaball)

        # speakers
        for speaker in bpy.data.speakers[:]:

          # sort
          batch.sort(context, speaker)

        # armatures
        for armature in bpy.data.armatures[:]:

          # sort
          batch.sort(context, armature)

      # bone groups
      if option.boneGroups:
        for object in bpy.data.objects[:]:
          if object.type in 'ARMATURE':
            for group in object.pose.bone_groups[:]:

              # sort
              batch.sort(context, group)

      # bones
      if option.bones:
        for armature in bpy.data.armatures[:]:
          for bone in armature.bones[:]:

            # sort
            batch.sort(context, bone)

      # bone constraints
      if option.boneConstraints:
        for object in bpy.data.objects[:]:
          if object.type in 'ARMATURE':
            for bone in object.pose.bones[:]:
              for constraint in bone.constraints[:]:

                # sort
                batch.sort(context, constraint)

      # vertex groups
      if option.vertexGroups:
        for object in bpy.data.objects[:]:
          if object.type in {'MESH', 'LATTICE'}:
            for group in object.vertex_groups[:]:

              # sort
              batch.sort(context, group)

      # shape keys
      if option.shapekeys:
        for shapekey in bpy.data.shape_keys[:]:

            # sort
            batch.sort(context, shapekey)
            for block in shapekey.key_blocks[:]:

              # sort
              batch.sort(context, block)

      # uvs
      if option.uvs:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':
            for uv in object.data.uv_textures[:]:

              # sort
              batch.sort(context, uv)

      # vertex colors
      if option.vertexColors:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':
            for color in object.data.vertex_colors[:]:

              # sort
              batch.sort(context, color)

      # materials
      if option.materials:
        for material in bpy.data.materials[:]:

          # sort
          batch.sort(context, material)

      # textures
      if option.textures:
        for texture in bpy.data.textures[:]:

          # sort
          batch.sort(context, texture)

      # particles systems
      if option.particleSystems:
        for object in bpy.data.objects[:]:
          if object.type in 'MESH':
            for system in object.particle_systems[:]:

              # sort
              batch.sort(context, system)

      # particles settings
      if option.particleSettings:
        for settings in bpy.data.particles[:]:

          # sort
          batch.sort(context, settings)

    # scenes
    if option.scenes:
      for scene in bpy.data.scenes[:]:

        # sort
        batch.sort(context, scene)

    # render layers
    if option.renderLayers:
      for scene in bpy.data.scenes[:]:
        for layer in scene.render.layers[:]:

          # sort
          batch.sort(context, layer)

    # worlds
    if option.worlds:
      for world in bpy.data.worlds[:]:

        # sort
        batch.sort(context, world)

    # libraries
    if option.libraries:
      for library in bpy.data.libraries[:]:

        # sort
        batch.sort(context, library)

    # images
    if option.images:
      for image in bpy.data.images[:]:

        # sort
        batch.sort(context, image)

    # masks
    if option.masks:
      for mask in bpy.data.masks[:]:

        # sort
        batch.sort(context, mask)

    # sequences
    if option.sequences:
      for scene in bpy.data.scenes[:]:
        if hasattr(scene.sequence_editor, 'sequence_all'):
          for sequence in scene.sequence_editor.sequences_all[:]:

            # sort
            batch.sort(context, sequence)

    # movie clips
    if option.movieClips:
      for clip in bpy.data.movieclips[:]:

        # sort
        batch.sort(context, clip)

    # sounds
    if option.sounds:
      for sound in bpy.data.sounds[:]:

        # sort
        batch.sort(context, sound)

    # screens
    if option.screens:
      for screen in bpy.data.screens[:]:

        # sort
        batch.sort(context, screen)

    # keying sets
    if option.keyingSets:
      for scene in bpy.data.scenes[:]:
        for keyingSet in scene.keying_sets[:]:

          # sort
          batch.sort(context, keyingSet)

    # palettes
    if option.palettes:
      for palette in bpy.data.palettes[:]:

        # sort
        batch.sort(context, palette)

    # brushes
    if option.brushes:
      for brush in bpy.data.brushes[:]:

        # sort
        batch.sort(context, brush)

    # line styles
    if option.linestyles:
      for style in bpy.data.linestyles[:]:

        # sort
        batch.sort(context, style)

    # nodes
    if option.nodes:

      # shader
      for material in bpy.data.materials[:]:
        if hasattr(material.node_tree, 'nodes'):
          for node in material.node_tree.nodes[:]:

            # sort
            batch.sort(context, node)

      # compositing
      for scene in bpy.data.scenes[:]:
        if hasattr(scene.node_tree, 'nodes'):
          for node in scene.node_tree.nodes[:]:

            # sort
            batch.sort(context, node)

      # texture
      for texture in bpy.data.textures[:]:
        if hasattr(texture.node_tree, 'nodes'):
          for node in texture.node_tree.nodes[:]:

            # sort
            batch.sort(context, node)

      # groups
      for group in bpy.data.node_groups[:]:
        for node in group.nodes[:]:

          # sort
          batch.sort(context, node)

    # node labels
    if option.nodeLabels:

      # batch tag
      batch.tag = True

      # shader
      for material in bpy.data.materials[:]:
        if hasattr(material.node_tree, 'nodes'):
          for node in material.node_tree.nodes[:]:

            # sort
            batch.sort(context, node)

      # compositing
      for scene in bpy.data.scenes[:]:
        if hasattr(scene.node_tree, 'nodes'):
          for node in scene.node_tree.nodes[:]:

            # sort
            batch.sort(context, node)

      # texture
      for texture in bpy.data.textures[:]:
        if hasattr(texture.node_tree, 'nodes'):
          for node in texture.node_tree.nodes[:]:

            # sort
            batch.sort(context, node)

      # groups
      for group in bpy.data.node_groups[:]:
        for node in group.nodes[:]:

          # sort
          batch.sort(context, node)

      # batch tag
      batch.tag = False

    # node groups
    if option.nodeGroups:
      for group in bpy.data.node_groups[:]:

        # sort
        batch.sort(context, group)

    # texts
    if option.texts:
      for text in bpy.data.texts[:]:

        # sort
        batch.sort(context, text)

    all = [

      # surface
      storage.batch.curves.surface,

      # text
      storage.batch.curves.text,

      # curve
      storage.batch.curves.curve,

      # objects
      storage.batch.objects,

      # groups
      storage.batch.groups,

      # actions
      storage.batch.actions,

      # grease pencils
      storage.batch.greasePencils,

      # pencil layers
      storage.batch.pencilLayers,

      # constraints
      storage.batch.constraints,

      # modifiers
      storage.batch.modifiers,

      # cameras
      storage.batch.cameras,

      # meshes
      storage.batch.meshes,

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

      # vertex groups
      storage.batch.vertexGroups,

      # shapekeys
      storage.batch.shapekeys,

      # uvs
      storage.batch.uvs,

      # vertex colors
      storage.batch.vertexColors,

      # materials
      storage.batch.materials,

      # textures
      storage.batch.textures,

      # particle systems
      storage.batch.particleSystems,

      # particle settings
      storage.batch.particleSettings,

      # bone groups
      storage.batch.boneGroups,

      # bones
      storage.batch.bones,

      # scenes
      storage.batch.scenes,

      # render layers
      storage.batch.renderLayers,

      # worlds
      storage.batch.worlds,

      # libraries
      storage.batch.libraries,

      # images
      storage.batch.images,

      # masks
      storage.batch.masks,

      # sequences
      storage.batch.sequences,

      # movie clips
      storage.batch.movieClips,

      # sounds
      storage.batch.sounds,

      # screens
      storage.batch.screens,

      # keying sets
      storage.batch.keyingSets,

      # palettes
      storage.batch.palettes,

      # brushes
      storage.batch.brushes,

      # linestyles
      storage.batch.linestyles,

      # nodes
      storage.batch.nodes,

      # node labels
      storage.batch.nodeLabels,

      # node groups
      storage.batch.nodeGroups,

      # texts
      storage.batch.texts,
    ]

    # debug
    # print(all)

    # process
    for collection in all[:]:
      batch.process(context, collection)

  # sort
  def sort(context, datablock):
    '''
      Sort datablocks into proper storage list.
    '''

    # option
    option = context.scene.batchNameSettings

    # objects
    if option.objects:
      if datablock.rna_type.identifier in 'Object':
        storage.batch.objects.append([datablock.name, [1, datablock]])

    # groups
    if option.groups:
      if datablock.rna_type.identifier in 'Group':
        storage.batch.groups.append([datablock.name, [1, datablock]])

    # actions
    if option.actions:
      if datablock.rna_type.identifier in 'Action':
        storage.batch.actions.append([datablock.name, [1, datablock]])

    # grease pencils
    if option.greasePencil:
      if datablock.rna_type.identifier in 'GreasePencil':
        storage.batch.greasePencils.append([datablock.name, [1, datablock]])

      # pencil layers
      if datablock.rna_type.identifier in 'GPencilLayer':
        storage.batch.pencilLayers.append([datablock.info, [1, datablock]])

    # constraints
    if option.constraints:
      if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier in 'Constraint':
          storage.batch.constraints.append([datablock.name, [1, datablock]])

    # modifiers
    if option.modifiers:
      if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier in 'Modifier':
          storage.batch.modifiers.append([datablock.name, [1, datablock]])

    # object data
    if option.objectData:

      # cameras
      if datablock.rna_type.identifier in 'Camera':
        storage.batch.cameras.append([datablock.name, [1, datablock]])

      # meshes
      if datablock.rna_type.identifier in 'Mesh':
        storage.batch.meshes.append([datablock.name, [1, datablock]])

      # lamps
      if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier in 'Lamp':
          storage.batch.lamps.append([datablock.name, [1, datablock]])

      # lattices
      if datablock.rna_type.identifier in 'Lattice':
        storage.batch.lattices.append([datablock.name, [1, datablock]])

      # surface
      if datablock.rna_type.identifier in 'SurfaceCurve':
        storage.batch.curves.surface.append([datablock.name, [1, datablock]])

      # text
      if datablock.rna_type.identifier in 'TextCurve':
        storage.batch.curves.text.append([datablock.name, [1, datablock]])

      # curves
      if datablock.rna_type.identifier in 'Curve':
        storage.batch.curves.curve.append([datablock.name, [1, datablock]])

      # metaballs
      if datablock.rna_type.identifier in 'MetaBall':
        storage.batch.metaballs.append([datablock.name, [1, datablock]])

      # speakers
      if datablock.rna_type.identifier in 'Speaker':
        storage.batch.speakers.append([datablock.name, [1, datablock]])

      # armatures
      if datablock.rna_type.identifier in 'Armature':
        storage.batch.armatures.append([datablock.name, [1, datablock]])

    # bones
    if option.bones:
      if datablock.rna_type.identifier in {'PoseBone', 'EditBone', 'Bone'}:
        storage.batch.bones.append([datablock.name, [1, datablock]])

    # vertex groups
    if option.vertexGroups:
      if datablock.rna_type.identifier in 'VertexGroup':
        storage.batch.vertexGroups.append([datablock.name, [1, datablock]])

    # shapekeys
    if option.shapekeys:
      if datablock.rna_type.identifier in 'ShapeKey':
        storage.batch.shapekeys.append([datablock.name, [1, datablock]])

    # uvs
    if option.uvs:
      if datablock.rna_type.identifier in 'MeshTexturePolyLayer':
        storage.batch.uvs.append([datablock.name, [1, datablock]])

    # vertex colors
    if option.vertexColors:
      if datablock.rna_type.identifier in 'MeshLoopColorLayer':
        storage.batch.vertexColors.append([datablock.name, [1, datablock]])

    # materials
    if option.materials:
      if datablock.rna_type.identifier in 'Material':
        storage.batch.materials.append([datablock.name, [1, datablock]])

    # textures
    if option.textures:
      if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier in 'Texture':
          storage.batch.textures.append([datablock.name, [1, datablock]])

    # particle systems
    if option.particleSystems:
      if datablock.rna_type.identifier in 'ParticleSystem':
        storage.batch.particleSystems.append([datablock.name, [1, datablock]])

    # particle settings
    if option.particleSettings:
      if datablock.rna_type.identifier in 'ParticleSettings':
        storage.batch.particleSettings.append([datablock.name, [1, datablock]])

    # scenes
    if option.scenes:
      if datablock.rna_type.identifier in 'Scene':
        storage.batch.scenes.append([datablock.name, [1, datablock]])

    # render layers
    if option.renderLayers:
      if datablock.rna_type.identifier in 'SceneRenderLayer':
        storage.batch.renderLayers.append([datablock.name, [1, datablock]])

    # worlds
    if option.worlds:
      if datablock.rna_type.identifier in 'World':
        storage.batch.worlds.append([datablock.name, [1, datablock]])

    # libraries
    if option.libraries:
      if datablock.rna_type.identifier in 'Library':
        storage.batch.libraries.append([datablock.name, [1, datablock]])

    # images
    if option.images:
      if datablock.rna_type.identifier in 'Image':
        storage.batch.images.append([datablock.name, [1, datablock]])

    # masks
    if option.masks:
      if datablock.rna_type.identifier in 'Mask':
        storage.batch.masks.append([datablock.name, [1, datablock]])

    # sequences
    if option.sequences:
      if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier in 'Sequence':
          storage.batch.sequences.append([datablock.name, [1, datablock]])

    # movie clips
    if option.movieClips:
      if datablock.rna_type.identifier in 'MovieClip':
        storage.batch.moviewClips.append([datablock.name, [1, datablock]])

    # sounds
    if option.sounds:
      if datablock.rna_type.identifier in 'Sound':
        storage.batch.sounds.append([datablock.name, [1, datablock]])

    # screens
    if option.screens:
      if datablock.rna_type.identifier in 'Screen':
        storage.batch.screens.append([datablock.name, [1, datablock]])

    # keying sets
    if option.keyingSets:
      if datablock.rna_type.identifier in 'KeyingSet':
        storage.batch.keyingSets.append([datablock.bl_label, [1, datablock]])

    # palettes
    if option.palettes:
      if datablock.rna_type.identifier in 'Palette':
        storage.batch.palettes.append([datablock.name, [1, datablock]])

    # brushes
    if option.brushes:
      if datablock.rna_type.identifier in 'Brush':
        storage.batch.brushes.append([datablock.name, [1, datablock]])

    # linestyles
    if option.linestyles:
      if datablock.rna_type.identifier in 'FreestyleLineStyle':
        storage.batch.linestyles.append([datablock.name, [1, datablock]])

    # nodes
    if option.nodes:
      if hasattr(datablock.rna_type.base, 'base'):
        if hasattr(datablock.rna_type.base.base, 'base'):
          if hasattr(datablock.rna_type.base.base.base, 'identifier'):
            if datablock.rna_type.base.base.base.identifier in 'Node':
              storage.batch.nodes.append([datablock.name, [1, datablock]])

              if batch.tag:
                datablock.label = batch.name(context, datablock.label)

    # node groups
    if option.nodeGroups:
      if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier in 'NodeTree':
          storage.batch.nodeGroups.append([datablock.name, [1, datablock]])

    # texts
    if option.texts:
      if datablock.rna_type.identifier in 'Text':
        storage.batch.texts.append([datablock.name, [1, datablock]])

  def process(context, collection):
    '''
      Process collection, send names to name.
    '''

    # option
    option = context.scene.batchNameSettings

    # count
    count = [
      # 'datablock.name', ...
    ]

    # datablocks
    datablocks = [
      # ['datablock.name', datablock], [...
    ]

    # duplicates
    duplicates = [
      # 'datablock.name', ...
    ]

    # collection
    for item in collection[:]:

      # sort
      if option.sort:

        # name
        item[0] = batch.name(context, (re.split(r'\W[0-9]*$|_[0-9]*$', item[0]))[0])
      else:
        item[0] = batch.name(context, item[0])

      # count
      count.append(item[0])

    # name count
    i = 0
    for item in collection[:]:

      # name count
      item[1][0] = count.count(count[i])
      i += 1

    # randomize
    for item in collection[:]:

      if option.sort:
        if item[1][0] > 1:

          # name
          if hasattr(item[1][1], 'name'):
            item[1][1].name = str(random())
          elif hasattr(item[1][1], 'info'):
            item[1][1].info = str(random())
          elif hasattr(item[1][1], 'bl_label'):
            item[1][1].bl_label = str(random())

          # batch count
          batch.count += 1
        elif not option.sortOnly:

          # name
          if hasattr(item[1][1], 'name'):
            item[1][1].name = str(random())
          elif hasattr(item[1][1], 'info'):
            item[1][1].info = str(random())
          elif hasattr(item[1][1], 'bl_label'):
            item[1][1].bl_label = str(random())

          # batch count
          batch.count += 1
      else:

        # name
        if hasattr(item[1][1], 'name'):
          item[1][1].name = str(random())
        elif hasattr(item[1][1], 'info'):
          item[1][1].info = str(random())
        elif hasattr(item[1][1], 'bl_label'):
          item[1][1].bl_label = str(random())

        # batch count
        batch.count += 1

    # sort
    if option.sort:
      i = 0
      for item in collection[:]:
        datablocks.append([item[0], i])
        i += 1
      i = 0
      for item in sorted(datablocks):

        # name count
        if collection[item[1]][1][0] > 1:

          # duplicates
          if collection[item[1]][0] not in duplicates:

            # name
            if hasattr(collection[item[1]][1][1], 'name'):
              collection[item[1]][1][1].name = collection[item[1]][0] + option.separator + '0'*option.padding + str(i + option.start).zfill(len(str(collection[item[1]][1][0])))
            elif hasattr(collection[item[1]][1][1], 'info'):
              collection[item[1]][1][1].info = collection[item[1]][0] + option.separator + '0'*option.padding + str(i + option.start).zfill(len(str(collection[item[1]][1][0])))
            elif hasattr(collection[item[1]][1][1], 'bl_label'):
              collection[item[1]][1][1].bl_label = collection[item[1]][0] + option.separator + '0'*option.padding + str(i + option.start).zfill(len(str(collection[item[1]][1][0])))
            i += 1
          if i == collection[item[1]][1][0]:
            i = 0

            # duplicates
            duplicates.append(collection[item[1]][0])

    # assign names
    if not option.sortOnly:
      for item in collection[:]:
        if item[0] not in duplicates:

          # name
          if hasattr(item[1][1], 'name'):
            item[1][1].name = item[0]
          elif hasattr(item[1][1], 'info'):
            item[1][1].info = item[0]
          elif hasattr(item[1][1], 'bl_label'):
            item[1][1].bl_label = item[0]

    # clear count
    count.clear()

    # clear sorted
    datablocks.clear()

    # clear duplicates
    duplicates.clear()

    # clear collection
    collection.clear()

  # name
  def name(context, datablock):
    '''
      Name datablocks received from process.
    '''

    # option
    option = context.scene.batchNameSettings

    # name check
    nameCheck = datablock

    # custom name
    if option.customName != '':

      # new name
      newName = option.customName
    else:

      # new name
      newName = datablock

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
    newName = option.prefix + newName + option.suffix

    # name check
    if nameCheck != newName:
      return newName
    else:
      return datablock

  # copy
  def copy(context):
    '''
      Get names from source datablock and assign to destination datablock.
    '''

    # option
    option = context.scene.batchCopySettings

    # batch type
    if option.batchType in {'SELECTED', 'OBJECTS'}:
      for object in bpy.data.objects[:]:

        # source object
        if option.source in 'OBJECT':

          # objects
          if option.objects:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:

                # use active object
                if option.useActiveObject:
                  object.name = context.active_object.name
                else:
                  object.name = object.name
            else:

              # use active object
              if option.useActiveObject:
                object.name = context.active_object.name
              else:
                object.name = object.name

          # object data
          if option.objectData:
            if object.type not in 'EMPTY':

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:

                  # use active object
                  if option.useActiveObject:
                    object.data.name = context.active_object.name
                  else:
                    object.data.name = object.name
              else:

                # use active object
                if option.useActiveObject:
                  object.data.name = context.active_object.name
                else:
                  object.data.name = object.name

          # materials
          if option.materials:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for material in object.material_slots[:]:
                  if material.material != None:

                    # use active object
                    if option.useActiveObject:
                      material.material.name = context.active_object.name
                    else:
                      material.material.name = object.name
            else:
              for material in object.material_slots[:]:
                if material.material != None:

                  # use active object
                  if option.useActiveObject:
                    material.material.name = context.active_object.name
                  else:
                    material.material.name = object.name

          # textures
          if option.textures:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for material in object.material_slots[:]:
                  if material.material != None:
                    for texture in material.material.texture_slots[:]:
                      if texture != None:

                        # use active object
                        if option.useActiveObject:
                          texture.texture.name = context.active_object.name
                        else:
                          texture.texture.name = object.name
            else:
              for material in object.material_slots[:]:
                if material.material != None:
                  for texture in material.material.texture_slots[:]:
                    if texture != None:

                      # use active object
                      if option.useActiveObject:
                        texture.texture.name = context.active_object.name
                      else:
                        texture.texture.name = object.name

          # particle systems
          if option.particleSystems:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for system in object.particle_systems[:]:

                  # use active object
                  if option.useActiveObject:
                    system.name = context.active_object.name
                  else:
                    system.name = object.name
            else:
              for system in object.particle_systems[:]:

                # use active object
                if option.useActiveObject:
                  system.name = context.active_object.name
                else:
                  system.name = object.name

          # particle settings
          if option.particleSettings:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for system in object.particle_systems[:]:

                  # use active object
                  if option.useActiveObject:
                    system.settings.name = context.active_object.name
                  else:
                    system.settings.name = object.name
            else:
              for system in object.particle_systems[:]:

                # use active object
                if option.useActiveObject:
                  system.settings.name = context.active_object.name
                else:
                  system.settings.name = object.name

        # source data
        if option.source in 'DATA':
          if object.type not in 'EMPTY':

            # objects
            if option.objects:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:

                  # use active object
                  if option.useActiveObject:
                    object.name = context.active_object.data.name
                  else:
                    object.name = object.data.name
              else:

                # use active object
                if option.useActiveObject:
                  object.name = context.active_object.data.name
                else:
                  object.name = object.data.name

            # object data
            if option.objectData:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:

                  # use active object
                  if option.useActiveObject:
                    object.data.name = context.active_object.data.name
                  else:
                    object.data.name = object.data.name
              else:

                # use active object
                if option.useActiveObject:
                  object.data.name = context.active_object.data.name
                else:
                  object.data.name = object.data.name

            # materials
            if option.materials:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for material in object.material_slots[:]:
                    if material.material != None:

                      # use active object
                      if option.useActiveObject:
                        material.material.name = context.active_object.data.name
                      else:
                        material.material.name = object.data.name
              else:
                for material in object.material_slots[:]:
                  if material.material != None:

                    # use active object
                    if option.useActiveObject:
                      material.material.name = context.active_object.data.name
                    else:
                      material.material.name = object.data.name

            # textures
            if option.textures:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for material in object.material_slots[:]:
                    if material.material != None:
                      for texture in material.material.texture_slots[:]:
                        if texture != None:

                          # use active object
                          if option.useActiveObject:
                            texture.texture.name = context.active_object.data.name
                          else:
                            texture.texture.name = object.data.name
              else:
                for material in object.material_slots[:]:
                  if material.material != None:
                    for texture in material.material.texture_slots[:]:
                      if texture != None:

                        # use active object
                        if option.useActiveObject:
                          texture.texture.name = context.active_object.data.name
                        else:
                          texture.texture.name = object.data.name

            # particle systems
            if option.particleSystems:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for system in object.particle_systems[:]:

                    # use active object
                    if option.useActiveObject:
                      system.name = context.active_object.data.name
                    else:
                      system.name = object.data.name
              else:
                for system in object.particle_systems[:]:

                  # use active object
                  if option.useActiveObject:
                    system.name = context.active_object.data.name
                  else:
                    system.name = object.data.name

            # particle settings
            if option.particleSettings:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for system in object.particle_systems[:]:

                    # use active object
                    if option.useActiveObject:
                      system.settings.name = context.active_object.data.name
                    else:
                      system.settings.name = object.data.name
              else:
                for system in object.particle_systems[:]:

                  # use active object
                  if option.useActiveObject:
                    system.settings.name = context.active_object.data.name
                  else:
                    system.settings.name = object.data.name

        # source material
        if option.source in 'MATERIAL':

          # objects
          if option.objects:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'name'):
                    object.name = context.active_object.active_material.name
                else:
                  if hasattr(object.active_material, 'name'):
                    object.name = object.active_material.name
            else:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'name'):
                  object.name = context.active_object.active_material.name
              else:
                if hasattr(object.active_material, 'name'):
                  object.name = object.active_material.name

          # object data
          if option.objectData:
            if object.type not in 'EMPTY':

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'name'):
                      object.data.name = context.active_object.active_material.name
                  else:
                    if hasattr(object.active_material, 'name'):
                      object.data.name = object.active_material.name
              else:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'name'):
                    object.data.name = context.active_object.active_material.name
                else:
                  if hasattr(object.active_material, 'name'):
                    object.data.name = object.active_material.name

          # materials
          if option.materials:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for material in object.material_slots[:]:
                  if material.material != None:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.active_material, 'name'):
                        material.material.name = context.active_object.active_material.name
                    else:
                      if hasattr(object.active_material, 'name'):
                        material.material.name = object.active_material.name
            else:
              for material in object.material_slots[:]:
                if material.material != None:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'name'):
                      material.material.name = context.active_object.active_material.name
                  else:
                    if hasattr(object.active_material, 'name'):
                      material.material.name = object.active_material.name

          # textures
          if option.textures:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for material in object.material_slots[:]:
                  if material.material != None:
                    for texture in material.material.texture_slots[:]:
                      if texture != None:

                        # use active object
                        if option.useActiveObject:
                          if hasattr(context.active_object.active_material, 'name'):
                            texture.texture.name = context.active_object.active_material.name
                        else:
                          if hasattr(object.active_material, 'name'):
                            texture.texture.name = object.active_material.name
            else:
              for material in object.material_slots[:]:
                if material.material != None:
                  for texture in material.material.texture_slots[:]:
                    if texture != None:

                      # use active object
                      if option.useActiveObject:
                        if hasattr(context.active_object.active_material, 'name'):
                          texture.texture.name = context.active_object.active_material.name
                      else:
                        if hasattr(object.active_material, 'name'):
                          texture.texture.name = object.active_material.name

          # particle systems
          if option.particleSystems:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for system in object.particle_systems[:]:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'name'):
                      system.name = context.active_object.active_material.name
                  else:
                    if hasattr(object.active_material, 'name'):
                      system.name = object.active_material.name
            else:
              for system in object.particle_systems[:]:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'name'):
                    system.name = context.active_object.active_material.name
                else:
                  if hasattr(object.active_material, 'name'):
                    system.name = object.active_material.name

          # particle settings
          if option.particleSettings:

            # batch type
            if option.batchType in 'SELECTED':
              if object.select:
                for system in object.particle_systems[:]:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'name'):
                      system.settings.name = context.active_object.active_material.name
                  else:
                    if hasattr(object.active_material, 'name'):
                      system.settings.name = object.active_material.name
            else:
              for system in object.particle_systems[:]:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'name'):
                    system.settings.name = context.active_object.active_material.name
                else:
                  if hasattr(object.active_material, 'name'):
                    system.settings.name = object.active_material.name

        # source texture
        if option.source in 'TEXTURE':
          if context.scene.render.engine not in 'CYCLES':

            # objects
            if option.objects:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'active_texture'):
                      if hasattr(context.active_object.active_material.active_texture, 'name'):
                        object.name = context.active_object.active_material.active_texture.name
                  else:
                    if hasattr(object.active_material, 'active_texture'):
                      if hasattr(object.active_material.active_texture, 'name'):
                        object.name = object.active_material.active_texture.name
              else:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'active_texture'):
                    if hasattr(context.active_object.active_material.active_texture, 'name'):
                      object.name = context.active_object.active_material.active_texture.name
                else:
                  if hasattr(object.active_material, 'active_texture'):
                    if hasattr(object.active_material.active_texture, 'name'):
                      object.name = object.active_material.active_texture.name

            # object data
            if option.objectData:
              if object.type not in 'EMPTY':

                # batch type
                if option.batchType in 'SELECTED':
                  if object.select:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.active_material, 'active_texture'):
                        if hasattr(context.active_object.active_material.active_texture, 'name'):
                          object.data.name = context.active_object.active_material.active_texture.name
                    else:
                      if hasattr(object.active_material, 'active_texture'):
                        if hasattr(object.active_material.active_texture, 'name'):
                          object.data.name = object.active_material.active_texture.name
                else:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'active_texture'):
                      if hasattr(context.active_object.active_material.active_texture, 'name'):
                        object.data.name = context.active_object.active_material.active_texture.name
                  else:
                    if hasattr(object.active_material, 'active_texture'):
                      if hasattr(object.active_material.active_texture, 'name'):
                        object.data.name = object.active_material.active_texture.name

            # materials
            if option.materials:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for material in object.material_slots[:]:
                    if material.material != None:

                      # use active object
                      if option.useActiveObject:
                        if hasattr(context.active_object.active_material, 'active_texture'):
                          if hasattr(context.active_object.active_material.active_texture, 'name'):
                            material.material.name = context.active_object.active_material.active_texture.name
                      else:
                        if hasattr(object.active_material, 'active_texture'):
                          if hasattr(object.active_material.active_texture, 'name'):
                            material.material.name = object.active_material.active_texture.name
              else:
                for material in object.material_slots[:]:
                  if material.material != None:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.active_material, 'active_texture'):
                        if hasattr(context.active_object.active_material.active_texture, 'name'):
                          material.material.name = context.active_object.active_material.active_texture.name
                    else:
                      if hasattr(object.active_material, 'active_texture'):
                        if hasattr(object.active_material.active_texture, 'name'):
                          material.material.name = object.active_material.active_texture.name

            # textures
            if option.textures:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for material in object.material_slots[:]:
                    if material.material != None:
                      for texture in material.material.texture_slots[:]:
                        if texture != None:

                          # use active object
                          if option.useActiveObject:
                            if hasattr(context.active_object.active_material, 'active_texture'):
                              if hasattr(context.active_object.active_material.active_texture, 'name'):
                                texture.texture.name = context.active_object.active_material.active_texture.name
                          else:
                            if hasattr(object.active_material, 'active_texture'):
                              if hasattr(object.active_material.active_texture, 'name'):
                                texture.texture.name = object.active_material.active_texture.name
              else:
                for material in object.material_slots[:]:
                  if material.material != None:
                    for texture in material.material.texture_slots[:]:
                      if texture != None:

                        # use active object
                        if option.useActiveObject:
                          if hasattr(context.active_object.active_material, 'active_texture'):
                            if hasattr(context.active_object.active_material.active_texture, 'name'):
                              texture.texture.name = context.active_object.active_material.active_texture.name
                        else:
                          if hasattr(object.active_material, 'active_texture'):
                            if hasattr(object.active_material.active_texture, 'name'):
                              texture.texture.name = object.active_material.active_texture.name

            # particle systems
            if option.particleSystems:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for system in object.particle_systems[:]:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.active_material, 'active_texture'):
                        if hasattr(context.active_object.active_material.active_texture, 'name'):
                          system.name = context.active_object.active_material.active_texture.name
                    else:
                      if hasattr(object.active_material, 'active_texture'):
                        if hasattr(object.active_material.active_texture, 'name'):
                          system.name = object.active_material.active_texture.name
              else:
                for system in object.particle_systems[:]:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'active_texture'):
                      if hasattr(context.active_object.active_material.active_texture, 'name'):
                        system.name = context.active_object.active_material.active_texture.name
                  else:
                    if hasattr(object.active_material, 'active_texture'):
                      if hasattr(object.active_material.active_texture, 'name'):
                        system.name = object.active_material.active_texture.name

            # particle settings
            if option.particleSettings:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for system in object.particle_systems[:]:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.active_material, 'active_texture'):
                        if hasattr(context.active_object.active_material.active_texture, 'name'):
                          system.settings.name = context.active_object.active_material.active_texture.name
                    else:
                      if hasattr(object.active_material, 'active_texture'):
                        if hasattr(object.active_material.active_texture, 'name'):
                          system.settings.name = object.active_material.active_texture.name
              else:
                for system in object.particle_systems[:]:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'active_texture'):
                      if hasattr(context.active_object.active_material.active_texture, 'name'):
                        system.settings.name = context.active_object.active_material.active_texture.name
                  else:
                    if hasattr(object.active_material, 'active_texture'):
                      if hasattr(object.active_material.active_texture, 'name'):
                        system.settings.name = object.active_material.active_texture.name

        # source particle system
        if option.source in 'PARTICLE_SYSTEM':

            # objects
            if option.objects:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'name'):
                      object.name = context.active_object.particle_systems.active.name
                  else:
                    if hasattr(object.particle_systems.active, 'name'):
                      object.name = object.particle_systems.active.name
              else:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'name'):
                    object.name = context.active_object.particle_systems.active.name
                else:
                  if hasattr(object.particle_systems.active, 'name'):
                    object.name = object.particle_systems.active.name

            # object data
            if option.objectData:
              if object.type not in 'EMPTY':

                # batch type
                if option.batchType in 'SELECTED':
                  if object.select:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.particle_systems.active, 'name'):
                        object.data.name = context.active_object.particle_systems.active.name
                    else:
                      if hasattr(object.particle_systems.active, 'name'):
                        object.data.name = object.particle_systems.active.name
                else:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'name'):
                      object.data.name = context.active_object.particle_systems.active.name
                  else:
                    if hasattr(object.particle_systems.active, 'name'):
                      object.data.name = object.particle_systems.active.name

            # materials
            if option.materials:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for material in object.material_slots[:]:
                    if material.material != None:

                      # use active object
                      if option.useActiveObject:
                        if hasattr(context.active_object.particle_systems.active, 'name'):
                          material.material.name = context.active_object.particle_systems.active.name
                      else:
                        if hasattr(object.particle_systems.active, 'name'):
                          material.material.name = object.particle_systems.active.name
              else:
                for material in object.material_slots[:]:
                  if material.material != None:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.particle_systems.active, 'name'):
                        material.material.name = context.active_object.particle_systems.active.name
                    else:
                      if hasattr(object.particle_systems.active, 'name'):
                        material.material.name = object.particle_systems.active.name

            # textures
            if option.textures:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for material in object.material_slots[:]:
                    if material.material != None:
                      for texture in material.material.texture_slots[:]:
                        if texture != None:

                          # use active object
                          if option.useActiveObject:
                            if hasattr(context.active_object.particle_systems.active, 'name'):
                              texture.texture.name = context.active_object.particle_systems.active.name
                          else:
                            if hasattr(object.particle_systems.active, 'name'):
                              texture.texture.name = object.particle_systems.active.name
              else:
                for material in object.material_slots[:]:
                  if material.material != None:
                    for texture in material.material.texture_slots[:]:
                      if texture != None:

                        # use active object
                        if option.useActiveObject:
                          if hasattr(context.active_object.particle_systems.active, 'name'):
                            texture.texture.name = context.active_object.particle_systems.active.name
                        else:
                          if hasattr(object.particle_systems.active, 'name'):
                            texture.texture.name = object.particle_systems.active.name

            # particle system
            if option.particleSystems:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for system in object.particle_systems[:]:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.particle_systems.active, 'name'):
                        system.name = context.active_object.particle_systems.active.name
                    else:
                      if hasattr(object.particle_systems.active, 'name'):
                        system.name = object.particle_systems.active.name
              else:
                for system in object.particle_systems[:]:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'name'):
                      system.name = context.active_object.particle_systems.active.name
                  else:
                    if hasattr(object.particle_systems.active, 'name'):
                      system.name = object.particle_systems.active.name

            # particle settings
            if option.particleSettings:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for system in object.particle_systems[:]:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.particle_systems.active, 'name'):
                        system.settings.name = context.active_object.particle_systems.active.name
                    else:
                      if hasattr(object.particle_systems.active, 'name'):
                        system.settings.name = object.particle_systems.active.name
              else:
                for system in object.particle_systems[:]:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'name'):
                      system.settings.name = context.active_object.particle_systems.active.name
                  else:
                    if hasattr(object.particle_systems.active, 'name'):
                      system.settings.name = object.particle_systems.active.name

        # source particle settings
        if option.source in 'PARTICLE_SETTINGS':

            # objects
            if option.objects:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'settings'):
                      object.name = context.active_object.particle_systems.active.settings.name
                  else:
                    if hasattr(object.particle_systems.active, 'settings'):
                      object.name = object.particle_systems.active.settings.name
              else:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'settings'):
                    object.name = context.active_object.particle_systems.active.settings.name
                else:
                  if hasattr(object.particle_systems.active, 'settings'):
                    object.name = object.particle_systems.active.settings.name

            # object data
            if option.objectData:
              if object.type not in 'EMPTY':

                # batch type
                if option.batchType in 'SELECTED':
                  if object.select:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.particle_systems.active, 'settings'):
                        object.data.name = context.active_object.particle_systems.active.settings.name
                    else:
                      if hasattr(object.particle_systems.active, 'settings'):
                        object.data.name = object.particle_systems.active.settings.name
                else:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'settings'):
                      object.data.name = context.active_object.particle_systems.active.settings.name
                  else:
                    if hasattr(object.particle_systems.active, 'settings'):
                      object.data.name = object.particle_systems.active.settings.name

            # materials
            if option.materials:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for material in object.material_slots[:]:
                    if material.material != None:

                      # use active object
                      if option.useActiveObject:
                        if hasattr(context.active_object.particle_systems.active, 'settings'):
                          material.material.name = context.active_object.particle_systems.active.settings.name
                      else:
                        if hasattr(object.particle_systems.active, 'settings'):
                          material.material.name = object.particle_systems.active.settings.name
              else:
                for material in object.material_slots[:]:
                  if material.material != None:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.particle_systems.active, 'settings'):
                        material.material.name = context.active_object.particle_systems.active.settings.name
                    else:
                      if hasattr(object.particle_systems.active, 'settings'):
                        material.material.name = object.particle_systems.active.settings.name

            # textures
            if option.textures:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for material in object.material_slots[:]:
                    if material.material != None:
                      for texture in material.material.texture_slots[:]:
                        if texture != None:

                          # use active object
                          if option.useActiveObject:
                            if hasattr(context.active_object.particle_systems.active, 'settings'):
                              texture.texture.name = context.active_object.particle_systems.active.settings.name
                          else:
                            if hasattr(object.particle_systems.active, 'settings'):
                              texture.texture.name = object.particle_systems.active.settings.name
              else:
                for material in object.material_slots[:]:
                  if material.material != None:
                    for texture in material.material.texture_slots[:]:
                      if texture != None:

                        # use active object
                        if option.useActiveObject:
                          if hasattr(context.active_object.particle_systems.active, 'settings'):
                            texture.texture.name = context.active_object.particle_systems.active.settings.name
                        else:
                          if hasattr(object.particle_systems.active, 'settings'):
                            texture.texture.name = object.particle_systems.active.settings.name

            # particle systems
            if option.particleSystems:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for system in object.particle_systems[:]:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.particle_systems.active, 'settings'):
                        system.name = context.active_object.particle_systems.active.settings.name
                    else:
                      if hasattr(object.particle_systems.active, 'settings'):
                        system.name = object.particle_systems.active.settings.name
              else:
                for system in object.particle_systems[:]:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'settings'):
                      system.name = context.active_object.particle_systems.active.settings.name
                  else:
                    if hasattr(object.particle_systems.active, 'settings'):
                      system.name = object.particle_systems.active.settings.name

            # particle settings
            if option.particleSettings:

              # batch type
              if option.batchType in 'SELECTED':
                if object.select:
                  for system in object.particle_systems[:]:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.particle_systems.active, 'settings'):
                        system.settings.name = context.active_object.particle_systems.active.settings.name
                    else:
                      if hasattr(object.particle_systems.active, 'settings'):
                        system.settings.name = object.particle_systems.active.settings.name
              else:
                for system in object.particle_systems[:]:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'settings'):
                      system.settings.name = context.active_object.particle_systems.active.settings.name
                  else:
                    if hasattr(object.particle_systems.active, 'settings'):
                      system.settings.name = object.particle_systems.active.settings.name
    # batch type
    else:
      for object in context.scene.objects[:]:

        # source object
        if option.source in 'OBJECT':

          # objects
          if option.objects:

            # use active object
            if option.useActiveObject:
              object.name = context.active_object.name
            else:
              object.name = object.name

          # object data
          if option.objectData:
            if object.type not in 'EMPTY':

              # use active object
              if option.useActiveObject:
                object.data.name = context.active_object.name
              else:
                object.data.name = object.name

          # materials
          if option.materials:
            for material in object.material_slots[:]:
              if material.material != None:

                # use active object
                if option.useActiveObject:
                  material.material.name = context.active_object.name
                else:
                  material.material.name = object.name

          # textures
          if option.textures:
            for material in object.material_slots[:]:
              if material.material != None:
                for texture in material.material.texture_slots[:]:
                  if texture != None:

                    # use active object
                    if option.useActiveObject:
                      texture.texture.name = context.active_object.name
                    else:
                      texture.texture.name = object.name

          # particle systems
          if option.particleSystems:
            for system in object.particle_systems[:]:

              # use active object
              if option.useActiveObject:
                system.name = context.active_object.name
              else:
                system.name = object.name

          # particle settings
          if option.particleSettings:
            for system in object.particle_systems[:]:

              # use active object
              if option.useActiveObject:
                system.settings.name = context.active_object.name
              else:
                system.settings.name = object.name

        # source data
        if option.source in 'DATA':
          if object.type not in 'EMPTY':

            # objects
            if option.objects:

              # use active object
              if option.useActiveObject:
                object.name = context.active_object.data.name
              else:
                object.name = object.data.name

            # object data
            if option.objectData:

              # use active object
              if option.useActiveObject:
                object.data.name = context.active_object.data.name
              else:
                object.data.name = object.data.name

            # materials
            if option.materials:
              for material in object.material_slots[:]:
                if material.material != None:

                  # use active object
                  if option.useActiveObject:
                    material.material.name = context.active_object.data.name
                  else:
                    material.material.name = object.data.name

            # textures
            if option.textures:
              for material in object.material_slots[:]:
                if material.material != None:
                  for texture in material.material.texture_slots[:]:
                    if texture != None:

                      # use active object
                      if option.useActiveObject:
                        texture.texture.name = context.active_object.data.name
                      else:
                        texture.texture.name = object.data.name

            # particle systems
            if option.particleSystems:
              for system in object.particle_systems[:]:

                # use active object
                if option.useActiveObject:
                  system.name = context.active_object.data.name
                else:
                  system.name = object.data.name

            # particle settings
            if option.particleSettings:
              for system in object.particle_systems[:]:

                # use active object
                if option.useActiveObject:
                  system.settings.name = context.active_object.data.name
                else:
                  system.settings.name = object.data.name

        # source material
        if option.source in 'MATERIAL':

          # objects
          if option.objects:

            # use active object
            if option.useActiveObject:
              if hasattr(context.active_object.active_material, 'name'):
                object.name = context.active_object.active_material.name
            else:
              if hasattr(object.active_material, 'name'):
                object.name = object.active_material.name

          # object data
          if option.objectData:
            if object.type not in 'EMPTY':

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'name'):
                  object.data.name = context.active_object.active_material.name
              else:
                if hasattr(object.active_material, 'name'):
                  object.data.name = object.active_material.name

          # materials
          if option.materials:
            for material in object.material_slots[:]:
              if material.material != None:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'name'):
                    material.material.name = context.active_object.active_material.name
                else:
                  if hasattr(object.active_material, 'name'):
                    material.material.name = object.active_material.name

          # textures
          if option.textures:
            for material in object.material_slots[:]:
              if material.material != None:
                for texture in material.material.texture_slots[:]:
                  if texture != None:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.active_material, 'name'):
                        texture.texture.name = context.active_object.active_material.name
                    else:
                      if hasattr(object.active_material, 'name'):
                        texture.texture.name = object.active_material.name

          # particle systems
          if option.particleSystems:
            for system in object.particle_systems[:]:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'name'):
                  system.name = context.active_object.active_material.name
              else:
                if hasattr(object.active_material, 'name'):
                  system.name = object.active_material.name

          # particle settings
          if option.particleSettings:
            for system in object.particle_systems[:]:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'name'):
                  system.settings.name = context.active_object.active_material.name
              else:
                if hasattr(object.active_material, 'name'):
                  system.settings.name = object.active_material.name

        # source texture
        if option.source in 'TEXTURE':
          if context.scene.render.engine not in 'CYCLES':

            # objects
            if option.objects:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'active_texture'):
                  if hasattr(context.active_object.active_material.active_texture, 'name'):
                    object.name = context.active_object.active_material.active_texture.name
              else:
                if hasattr(object.active_material, 'active_texture'):
                  if hasattr(object.active_material.active_texture, 'name'):
                    object.name = object.active_material.active_texture.name

            # object data
            if option.objectData:
              if object.type not in 'EMPTY':

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'active_texture'):
                    if hasattr(context.active_object.active_material.active_texture, 'name'):
                      object.data.name = context.active_object.active_material.active_texture.name
                else:
                  if hasattr(object.active_material, 'active_texture'):
                    if hasattr(object.active_material.active_texture, 'name'):
                      object.data.name = object.active_material.active_texture.name

            # materials
            if option.materials:
              for material in object.material_slots[:]:
                if material.material != None:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'active_texture'):
                      if hasattr(context.active_object.active_material.active_texture, 'name'):
                        material.material.name = context.active_object.active_material.active_texture.name
                  else:
                    if hasattr(object.active_material, 'active_texture'):
                      if hasattr(object.active_material.active_texture, 'name'):
                        material.material.name = object.active_material.active_texture.name

            # textures
            if option.textures:
              for material in object.material_slots[:]:
                if material.material != None:
                  for texture in material.material.texture_slots[:]:
                    if texture != None:

                      # use active object
                      if option.useActiveObject:
                        if hasattr(context.active_object.active_material, 'active_texture'):
                          if hasattr(context.active_object.active_material.active_texture, 'name'):
                            texture.texture.name = context.active_object.active_material.active_texture.name
                      else:
                        if hasattr(object.active_material, 'active_texture'):
                          if hasattr(object.active_material.active_texture, 'name'):
                            texture.texture.name = object.active_material.active_texture.name

            # particle systems
            if option.particleSystems:
              for system in object.particle_systems[:]:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'active_texture'):
                    if hasattr(context.active_object.active_material.active_texture, 'name'):
                      system.name = context.active_object.active_material.active_texture.name
                else:
                  if hasattr(object.active_material, 'active_texture'):
                    if hasattr(object.active_material.active_texture, 'name'):
                      system.name = object.active_material.active_texture.name

            # particle settings
            if option.particleSettings:
              for system in object.particle_systems[:]:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'active_texture'):
                    if hasattr(context.active_object.active_material.active_texture, 'name'):
                      system.settings.name = context.active_object.active_material.active_texture.name
                else:
                  if hasattr(object.active_material, 'active_texture'):
                    if hasattr(object.active_material.active_texture, 'name'):
                      system.settings.name = object.active_material.active_texture.name

        # source particle system
        if option.source in 'PARTICLE_SYSTEM':

            # objects
            if option.objects:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.particle_systems.active, 'name'):
                  object.name = context.active_object.particle_systems.active.name
              else:
                if hasattr(object.particle_systems.active, 'name'):
                  object.name = object.particle_systems.active.name

            # object data
            if option.objectData:
              if object.type not in 'EMPTY':

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'name'):
                    object.data.name = context.active_object.particle_systems.active.name
                else:
                  if hasattr(object.particle_systems.active, 'name'):
                    object.data.name = object.particle_systems.active.name

            # materials
            if option.materials:
              for material in object.material_slots[:]:
                if material.material != None:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'name'):
                      material.material.name = context.active_object.particle_systems.active.name
                  else:
                    if hasattr(object.particle_systems.active, 'name'):
                      material.material.name = object.particle_systems.active.name

            # textures
            if option.textures:
              for material in object.material_slots[:]:
                if material.material != None:
                  for texture in material.material.texture_slots[:]:
                    if texture != None:

                      # use active object
                      if option.useActiveObject:
                        if hasattr(context.active_object.particle_systems.active, 'name'):
                          texture.texture.name = context.active_object.particle_systems.active.name
                      else:
                        if hasattr(object.particle_systems.active, 'name'):
                          texture.texture.name = object.particle_systems.active.name

            # particle system
            if option.particleSystems:
              for system in object.particle_systems[:]:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'name'):
                    system.name = context.active_object.particle_systems.active.name
                else:
                  if hasattr(object.particle_systems.active, 'name'):
                    system.name = object.particle_systems.active.name

            # particle settings
            if option.particleSettings:
              for system in object.particle_systems[:]:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'name'):
                    system.settings.name = context.active_object.particle_systems.active.name
                else:
                  if hasattr(object.particle_systems.active, 'name'):
                    system.settings.name = object.particle_systems.active.name

        # source particle settings
        if option.source in 'PARTICLE_SETTINGS':

            # objects
            if option.objects:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.particle_systems.active, 'settings'):
                  object.name = context.active_object.particle_systems.active.settings.name
              else:
                if hasattr(object.particle_systems.active, 'settings'):
                  object.name = object.particle_systems.active.settings.name

            # object data
            if option.objectData:
              if object.type not in 'EMPTY':

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'settings'):
                    object.data.name = context.active_object.particle_systems.active.settings.name
                else:
                  if hasattr(object.particle_systems.active, 'settings'):
                    object.data.name = object.particle_systems.active.settings.name

            # materials
            if option.materials:
              for material in object.material_slots[:]:
                if material.material != None:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'settings'):
                      material.material.name = context.active_object.particle_systems.active.settings.name
                  else:
                    if hasattr(object.particle_systems.active, 'settings'):
                      material.material.name = object.particle_systems.active.settings.name

            # textures
            if option.textures:
              for material in object.material_slots[:]:
                if material.material != None:
                  for texture in material.material.texture_slots[:]:
                    if texture != None:

                      # use active object
                      if option.useActiveObject:
                        if hasattr(context.active_object.particle_systems.active, 'settings'):
                          texture.texture.name = context.active_object.particle_systems.active.settings.name
                      else:
                        if hasattr(object.particle_systems.active, 'settings'):
                          texture.texture.name = object.particle_systems.active.settings.name

            # particle systems
            if option.particleSystems:
              for system in object.particle_systems[:]:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'settings'):
                    system.name = context.active_object.particle_systems.active.settings.name
                else:
                  if hasattr(object.particle_systems.active, 'settings'):
                    system.name = object.particle_systems.active.settings.name

            # particle settings
            if option.particleSettings:
              for system in object.particle_systems[:]:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'settings'):
                    system.settings.name = context.active_object.particle_systems.active.settings.name
                else:
                  if hasattr(object.particle_systems.active, 'settings'):
                    system.settings.name = object.particle_systems.active.settings.name

  # reset settings
  def resetSettings(context, panel, auto, names, name, copy):
    '''
      Resets the property values for the item panel add-on.
    '''

    # panel
    if panel:

      # item panel option
      itemPanelOption = context.scene.itemPanelSettings

      # filters
      itemPanelOption.filters = False

      # options
      itemPanelOption.options = False

      # selected
      itemPanelOption.selected = False

      # pin active object
      itemPanelOption.pinActiveObject = True

      # groups
      itemPanelOption.groups = False

      # action
      itemPanelOption.action = False

      # grease pencil
      itemPanelOption.greasePencil = False

      # constraints
      itemPanelOption.constraints = False

      # modifiers
      itemPanelOption.modifiers = False

      # bone groups
      itemPanelOption.boneGroups = False

      # bone constraints
      itemPanelOption.boneConstraints = False

      # vertex groups
      itemPanelOption.vertexGroups = False

      # shapekeys
      itemPanelOption.shapekeys = False

      # uvs
      itemPanelOption.uvs = False

      # vertex colors
      itemPanelOption.vertexColors = False

      # materials
      itemPanelOption.materials = False

      # textures
      itemPanelOption.textures = False

      # particle systems
      itemPanelOption.particleSystems = False

      # selected bones
      itemPanelOption.selectedBones = False

    # auto
    if auto:

      # batch auto name option
      batchAutoNameOption = context.scene.batchAutoNameSettings

      # batch type
      batchAutoNameOption.batchType = 'SELECTED'

      # objects
      batchAutoNameOption.objects = False

      # constraints
      batchAutoNameOption.constraints = False

      # modifiers
      batchAutoNameOption.modifiers = False

      # objectData
      batchAutoNameOption.objectData = False

      # bone Constraints
      batchAutoNameOption.boneConstraints = False

      # object type
      batchAutoNameOption.objectType = 'ALL'

      # constraint type
      batchAutoNameOption.constraintType = 'ALL'

      # modifier type
      batchAutoNameOption.modifierType = 'ALL'

    # names
    if names:

      # object name
      objectName = context.scene.batchAutoNameObjectNames

      # mesh
      objectName.mesh = 'Mesh'

      # curve
      objectName.curve = 'Curve'

      # surface
      objectName.surface = 'Surface'

      # meta
      objectName.meta = 'Meta'

      # font
      objectName.font = 'Text'

      # armature
      objectName.armature = 'Armature'

      # lattice
      objectName.lattice = 'Lattice'

      # empty
      objectName.empty = 'Empty'

      # speaker
      objectName.speaker = 'Speaker'

      # camera
      objectName.camera = 'Camera'

      # lamp
      objectName.lamp = 'Lamp'

      # constraint name
      constraintName = context.scene.batchAutoNameConstraintNames

      # camera solver
      constraintName.cameraSolver = 'Camera Solver'

      # follow track
      constraintName.followTrack = 'Follow Track'

      # object solver
      constraintName.objectSolver = 'Object Solver'

      # copy location
      constraintName.copyLocation = 'Copy Location'

      # copy rotation
      constraintName.copyRotation = 'Copy Rotation'

      # copy scale
      constraintName.copyScale = 'Copy Scale'

      # copy transforms
      constraintName.copyTransforms = 'Copy Transforms'

      # limit distance
      constraintName.limitDistance = 'Limit Distance'

      # limit location
      constraintName.limitLocation = 'Limit Location'

      # limit rotation
      constraintName.limitRotation = 'Limit Rotation'

      # limit scale
      constraintName.limitScale = 'Limit Scale'

      # maintain volume
      constraintName.maintainVolume = 'Maintain Volume'

      # transform
      constraintName.transform = 'Transform'

      # clamp to
      constraintName.clampTo = 'Clamp To'

      # damped track
      constraintName.dampedTrack = 'Damped Track'

      # inverse kinematics
      constraintName.inverseKinematics = 'Inverse Kinematics'

      # locked track
      constraintName.lockedTrack = 'Locked Track'

      # spline inverse kinematics
      constraintName.splineInverseKinematics = 'Spline Inverse Kinematics'

      # stretch to
      constraintName.stretchTo = 'Stretch To'

      # track to
      constraintName.trackTo = 'Track To'

      # action
      constraintName.action = 'Action'

      # child of
      constraintName.childOf = 'Child Of'

      # floor
      constraintName.floor = 'Floor'

      # follow path
      constraintName.followPath = 'Follow Path'

      # pivot
      constraintName.pivot = 'Pivot'

      # rigid body joint
      constraintName.rigidBodyJoint = 'Rigid Body Joint'

      # shrinkwrap
      constraintName.shrinkwrap = 'Shrinkwrap'

      # modifier name
      modifierName = context.scene.batchAutoNameModifierNames

      # data transfer
      modifierName.dataTransfer = 'Data Transfer'

      # mesh cache
      modifierName.meshCache = 'Mesh Cache'

      # normal edit
      modifierName.normalEdit = 'Normal Edit'

      # uv project
      modifierName.uvProject = 'UV Project'

      # uv warp
      modifierName.uvWarp = 'UV Warp'

      # vertex weight edit
      modifierName.vertexWeightEdit = 'Vertex Weight Edit'

      # vertex weight mix
      modifierName.vertexWeightMix = 'Vertex Weight Mix'

      # vertex weight proximity
      modifierName.vertexWeightProximity = 'Vertex Weight Proximity'

      # array
      modifierName.array = 'Array'

      # bevel
      modifierName.bevel = 'Bevel'

      # boolean
      modifierName.boolean = 'Boolean'

      # build
      modifierName.build = 'Build'

      # decimate
      modifierName.decimate = 'Decimate'

      # edge split
      modifierName.edgeSplit = 'Edge Split'

      # mask
      modifierName.mask = 'Mask'

      # mirror
      modifierName.mirror = 'Mirror'

      # multiresolution
      modifierName.multiresolution = 'Multiresolution'

      # remesh
      modifierName.remesh = 'Remesh'

      # screw
      modifierName.screw = 'Screw'

      # skin
      modifierName.skin = 'Skin'

      # solidify
      modifierName.solidify = 'Solidify'

      # subdivision surface
      modifierName.subdivisionSurface = 'Subdivision Surface'

      # triangulate
      modifierName.triangulate = 'Triangulate'

      # wireframe
      modifierName.wireframe = 'Wireframe'

      # armature
      modifierName.armature = 'Armature'

      # cast
      modifierName.cast = 'Cast'

      # corrective smooth
      modifierName.correctiveSmooth = 'Corrective Smooth'

      # curve
      modifierName.curve = 'Curve'

      # displace
      modifierName.displace = 'Displace'

      # hook
      modifierName.hook = 'Hook'

      # laplacian smooth
      modifierName.laplacianSmooth = 'Laplacian Smooth'

      # laplacian deform
      modifierName.laplacianDeform = 'Laplacian Deform'

      # lattice
      modifierName.lattice = 'Lattice'

      # mesh deform
      modifierName.meshDeform = 'Mesh Deform'

      # shrinkwrap
      modifierName.shrinkwrap = 'Shrinkwrap'

      # simple deform
      modifierName.simpleDeform = 'Simple Deform'

      # smooth
      modifierName.smooth = 'Smooth'

      # warp
      modifierName.warp = 'Warp'

      # wave
      modifierName.wave = 'Wave'

      # cloth
      modifierName.cloth = 'Cloth'

      # collision
      modifierName.collision = 'Collision'

      # dynamic paint
      modifierName.dynamicPaint = 'Dynamic Paint'

      # explode
      modifierName.explode = 'Explode'

      # fluid simulation
      modifierName.fluidSimulation = 'Fluid Simulation'

      # ocean
      modifierName.ocean = 'Ocean'

      # particle instance
      modifierName.particleInstance = 'Particle Instance'

      # particle system
      modifierName.particleSystem = 'Particle System'

      # smoke
      modifierName.smoke = 'Smoke'

      # soft body
      modifierName.softBody = 'Soft Body'

      # object data names

      # mesh
      modifierName.mesh = 'Mesh'

      # curve
      modifierName.curve = 'Curve'

      # surface
      modifierName.surface = 'Surface'

      # meta
      modifierName.meta = 'Meta'

      # font
      modifierName.font = 'Text'

      # armature
      modifierName.armature = 'Armature'

      # lattice
      modifierName.lattice = 'Lattice'

      # empty
      modifierName.empty = 'Empty'

      # speaker
      modifierName.speaker = 'Speaker'

      # camera
      modifierName.camera = 'Camera'

      # lamp
      modifierName.lamp = 'Lamp'

      # object data name
      objectDataName = context.scene.batchAutoNameObjectDataNames

      # mesh
      objectDataName.mesh = 'Mesh'

      # curve
      objectDataName.curve = 'Curve'

      # surface
      objectDataName.surface = 'Surface'

      # meta
      objectDataName.meta = 'Meta'

      # font
      objectDataName.font = 'Text'

      # armature
      objectDataName.armature = 'Armature'

      # lattice
      objectDataName.lattice = 'Lattice'

      # speaker
      objectDataName.speaker = 'Speaker'

      # camera
      objectDataName.camera = 'Camera'

      # lamp
      objectDataName.lamp = 'Lamp'

    # name
    if name:

      # batch name option
      batchNameOption = context.scene.batchNameSettings

      # batch type
      batchNameOption.batchType = 'SELECTED'

      # batch objects
      batchNameOption.objects = False

      # batch groups
      batchNameOption.groups = False

      # batch actions
      batchNameOption.actions = False

      # batch grease pencil
      batchNameOption.greasePencil = False

      # batch object constraints
      batchNameOption.constraints = False

      # batch modifiers
      batchNameOption.modifiers = False

      # batch object data
      batchNameOption.objectData = False

      # batch bones
      batchNameOption.bones = False

      # batch bone constraints
      batchNameOption.boneConstraints = False

      # batch materials
      batchNameOption.materials = False

      # batch textures
      batchNameOption.textures = False

      # batch particle systems
      batchNameOption.particleSystems = False

      # batch particle settings
      batchNameOption.particleSettings = False

      # batch vertex groups
      batchNameOption.vertexGroups = False

      # batch shape keys
      batchNameOption.shapekeys = False

      # batch uvs
      batchNameOption.uvs = False

      # batch vertex colors
      batchNameOption.vertexColors = False

      # batch bone groups
      batchNameOption.boneGroups = False

      # object type
      batchNameOption.objectType = 'ALL'

      # constraint type
      batchNameOption.constraintType = 'ALL'

      # modifier type
      batchNameOption.modifierType = 'ALL'

      # scenes
      batchNameOption.scenes = False

      # render layers
      batchNameOption.renderLayers = False

      # worlds
      batchNameOption.worlds = False

      # libraries
      batchNameOption.libraries = False

      # images
      batchNameOption.images = False

      # masks
      batchNameOption.masks = False

      # sequences
      batchNameOption.sequences = False

      # movie clips
      batchNameOption.movieClips = False

      # sounds
      batchNameOption.sounds = False

      # layouts
      batchNameOption.screens = False

      # keying sets
      batchNameOption.keyingSets = False

      # palettes
      batchNameOption.palettes = False

      # brushes
      batchNameOption.brushes = False

      # linestyles
      batchNameOption.linestyles = False

      # nodes
      batchNameOption.nodes = False

      # node labels
      batchNameOption.nodeLabels = False

      # node groups
      batchNameOption.nodeGroups = False

      # texts
      batchNameOption.texts = False

      # custom name
      batchNameOption.customName = ''

      # find
      batchNameOption.find = ''

      # regex
      batchNameOption.regex = False

      # replace
      batchNameOption.replace = ''

      # prefix
      batchNameOption.prefix = ''

      # suffix
      batchNameOption.suffix = ''

      # trim start
      batchNameOption.trimStart = 0

      # trim end
      batchNameOption.trimEnd = 0

      # process
      batchNameOption.sort = False

      # padding
      batchNameOption.padding = 0

      # start
      batchNameOption.start = 1

      # separator
      batchNameOption.separator = '.'

      # process only
      batchNameOption.sortOnly = False

    # copy
    if copy:

      # batch copy option
      batchCopyOption = context.scene.batchCopySettings

      # batch type
      batchCopyOption.batchType = 'SELECTED'

      # source
      batchCopyOption.source = 'OBJECT'

      # objects
      batchCopyOption.objects = False

      # object datas
      batchCopyOption.objectData = False

      # materials
      batchCopyOption.materials = False

      # textures
      batchCopyOption.textures = False

      # particle systems
      batchCopyOption.particleSystems = False

      # particle settings
      batchCopyOption.particleSettings = False

      # use active object
      batchCopyOption.useActiveObject = False

  # transfer settings
  def transferSettings(context, panel, auto, names, name, copy):
    '''
      Resets the property values for the item panel add-on.
    '''

    # panel settings
    if panel:
      for scene in bpy.data.scenes[:]:
        if scene != context.scene:

          # item panel option
          itemPanelOption = context.scene.itemPanelSettings

          # filters
          scene.itemPanelSettings.filters = itemPanelOption.filters

          # options
          scene.itemPanelSettings.options = itemPanelOption.options

          # selected
          scene.itemPanelSettings.selected = itemPanelOption.selected

          # pin active object
          scene.itemPanelSettings.pinActiveObject = itemPanelOption.pinActiveObject

          # groups
          scene.itemPanelSettings.groups = itemPanelOption.groups

          # action
          scene.itemPanelSettings.action = itemPanelOption.action

          # grease pencil
          scene.itemPanelSettings.greasePencil = itemPanelOption.greasePencil

          # constraint
          scene.itemPanelSettings.constraints = itemPanelOption.constraints

          # modifiers
          scene.itemPanelSettings.modifiers = itemPanelOption.modifiers

          # bone groups
          scene.itemPanelSettings.boneGroups = itemPanelOption.boneGroups

          # bone constraints
          scene.itemPanelSettings.boneConstraints = itemPanelOption.boneConstraints

          # vertex groups
          scene.itemPanelSettings.vertexGroups = itemPanelOption.vertexGroups

          # shapekeys
          scene.itemPanelSettings.shapekeys = itemPanelOption.shapekeys

          # uvs
          scene.itemPanelSettings.uvs = itemPanelOption.uvs

          # vertex colors
          scene.itemPanelSettings.vertexColors = itemPanelOption.vertexColors

          # materials
          scene.itemPanelSettings.materials = itemPanelOption.materials

          # textures
          scene.itemPanelSettings.textures = itemPanelOption.textures

          # particels systems
          scene.itemPanelSettings.particleSystems = itemPanelOption.particleSystems

          # selected bones
          scene.itemPanelSettings.selectedBones = itemPanelOption.selectedBones

    # auto
    if auto:
      for scene in bpy.data.scenes[:]:
        if scene != context.scene:

          # auto name option
          batchAutoNameOption = context.scene.batchAutoNameSettings

          # batch type
          scene.batchAutoNameSettings.batchType = batchAutoNameOption.batchType

          # objects
          scene.batchAutoNameSettings.objects = batchAutoNameOption.objects

          # constraints
          scene.batchAutoNameSettings.constraints = batchAutoNameOption.constraints

          # modifiers
          scene.batchAutoNameSettings.modifiers = batchAutoNameOption.modifiers

          # objectData
          scene.batchAutoNameSettings.objectData = batchAutoNameOption.objectData

          # bone Constraints
          scene.batchAutoNameSettings.boneConstraints = batchAutoNameOption.boneConstraints

          # object type
          scene.batchAutoNameSettings.objectType = batchAutoNameOption.objectType

          # constraint type
          scene.batchAutoNameSettings.constraintType = batchAutoNameOption.constraintType

          # modifier type
          scene.batchAutoNameSettings.modifierType = batchAutoNameOption.modifierType

    # names
    if names:
      for scene in bpy.data.scenes[:]:
        if scene != context.scene:

          # object name
          objectName = context.scene.batchAutoNameObjectNames

          # mesh
          scene.batchAutoNameObjectNames.mesh = objectName.mesh

          # curve
          scene.batchAutoNameObjectNames.curve = objectName.curve

          # surface
          scene.batchAutoNameObjectNames.surface = objectName.surface

          # meta
          scene.batchAutoNameObjectNames.meta = objectName.meta

          # font
          scene.batchAutoNameObjectNames.font = objectName.font

          # armature
          scene.batchAutoNameObjectNames.armature = objectName.armature

          # lattice
          scene.batchAutoNameObjectNames.lattice = objectName.lattice

          # empty
          scene.batchAutoNameObjectNames.empty = objectName.empty

          # speaker
          scene.batchAutoNameObjectNames.speaker = objectName.speaker

          # camera
          scene.batchAutoNameObjectNames.camera = objectName.camera

          # lamp
          scene.batchAutoNameObjectNames.lamp = objectName.lamp

          # constraint name
          constraintName = context.scene.batchAutoNameConstraintNames

          # camera solver
          scene.batchAutoNameConstraintNames.cameraSolver = constraintName.cameraSolver

          # follow track
          scene.batchAutoNameConstraintNames.followTrack = constraintName.followTrack

          # object solver
          scene.batchAutoNameConstraintNames.objectSolver = constraintName.objectSolver

          # copy location
          scene.batchAutoNameConstraintNames.copyLocation = constraintName.copyLocation

          # copy rotation
          scene.batchAutoNameConstraintNames.copyRotation = constraintName.copyRotation

          # copy scale
          scene.batchAutoNameConstraintNames.copyScale = constraintName.copyScale

          # copy transforms
          scene.batchAutoNameConstraintNames.copyTransforms = constraintName.copyTransforms

          # limit distance
          scene.batchAutoNameConstraintNames.limitDistance = constraintName.limitDistance

          # limit location
          scene.batchAutoNameConstraintNames.limitLocation = constraintName.limitLocation

          # limit rotation
          scene.batchAutoNameConstraintNames.limitRotation = constraintName.limitRotation

          # limit scale
          scene.batchAutoNameConstraintNames.limitScale = constraintName.limitScale

          # maintain volume
          scene.batchAutoNameConstraintNames.maintainVolume = constraintName.maintainVolume

          # transform
          scene.batchAutoNameConstraintNames.transform = constraintName.transform

          # clamp to
          scene.batchAutoNameConstraintNames.clampTo = constraintName.clampTo

          # damped track
          scene.batchAutoNameConstraintNames.dampedTrack = constraintName.dampedTrack

          # inverse kinematics
          scene.batchAutoNameConstraintNames.inverseKinematics = constraintName.inverseKinematics

          # locked track
          scene.batchAutoNameConstraintNames.lockedTrack = constraintName.lockedTrack

          # spline inverse kinematics
          scene.batchAutoNameConstraintNames.splineInverseKinematics = constraintName.splineInverseKinematics

          # stretch to
          scene.batchAutoNameConstraintNames.stretchTo = constraintName.stretchTo

          # track to
          scene.batchAutoNameConstraintNames.trackTo = constraintName.trackTo

          # action
          scene.batchAutoNameConstraintNames.action = constraintName.action

          # child of
          scene.batchAutoNameConstraintNames.childOf = constraintName.childOf

          # floor
          scene.batchAutoNameConstraintNames.floor = constraintName.floor

          # follow path
          scene.batchAutoNameConstraintNames.followPath = constraintName.followPath

          # pivot
          scene.batchAutoNameConstraintNames.pivot = constraintName.pivot

          # rigid body joint
          scene.batchAutoNameConstraintNames.rigidBodyJoint = constraintName.rigidBodyJoint

          # shrinkwrap
          scene.batchAutoNameConstraintNames.shrinkwrap = constraintName.shrinkwrap

          # modifier name
          modifierName = context.scene.batchAutoNameModifierNames

          # data transfer
          scene.batchAutoNameModifierNames.dataTransfer = modifierName.dataTransfer

          # mesh cache
          scene.batchAutoNameModifierNames.meshCache = modifierName.meshCache

          # normal edit
          scene.batchAutoNameModifierNames.normalEdit = modifierName.normalEdit

          # uv project
          scene.batchAutoNameModifierNames.uvProject = modifierName.uvProject

          # uv warp
          scene.batchAutoNameModifierNames.uvWarp = modifierName.uvWarp

          # vertex weight edit
          scene.batchAutoNameModifierNames.vertexWeightEdit = modifierName.vertexWeightEdit

          # vertex weight mix
          scene.batchAutoNameModifierNames.vertexWeightMix = modifierName.vertexWeightMix

          # vertex weight proximity
          scene.batchAutoNameModifierNames.vertexWeightProximity = modifierName.vertexWeightProximity

          # array
          scene.batchAutoNameModifierNames.array = modifierName.array

          # bevel
          scene.batchAutoNameModifierNames.bevel = modifierName.bevel

          # boolean
          scene.batchAutoNameModifierNames.boolean = modifierName.boolean

          # build
          scene.batchAutoNameModifierNames.build = modifierName.build

          # decimate
          scene.batchAutoNameModifierNames.decimate = modifierName.decimate

          # edge split
          scene.batchAutoNameModifierNames.edgeSplit = modifierName.edgeSplit

          # mask
          scene.batchAutoNameModifierNames.mask = modifierName.mask

          # mirror
          scene.batchAutoNameModifierNames.mirror = modifierName.mirror

          # multiresolution
          scene.batchAutoNameModifierNames.multiresolution = modifierName.multiresolution

          # remesh
          scene.batchAutoNameModifierNames.remesh = modifierName.remesh

          # screw
          scene.batchAutoNameModifierNames.screw = modifierName.screw

          # skin
          scene.batchAutoNameModifierNames.skin = modifierName.skin

          # solidify
          scene.batchAutoNameModifierNames.solidify = modifierName.solidify

          # subdivision surface
          scene.batchAutoNameModifierNames.subdivisionSurface = modifierName.subdivisionSurface

          # triangulate
          scene.batchAutoNameModifierNames.triangulate = modifierName.triangulate

          # wireframe
          scene.batchAutoNameModifierNames.wireframe = modifierName.wireframe

          # armature
          scene.batchAutoNameModifierNames.armature = modifierName.armature

          # cast
          scene.batchAutoNameModifierNames.cast = modifierName.cast

          # corrective smooth
          scene.batchAutoNameModifierNames.correctiveSmooth = modifierName.correctiveSmooth

          # curve
          scene.batchAutoNameModifierNames.curve = modifierName.curve

          # displace
          scene.batchAutoNameModifierNames.displace = modifierName.displace

          # hook
          scene.batchAutoNameModifierNames.hook = modifierName.hook

          # laplacian smooth
          scene.batchAutoNameModifierNames.laplacianSmooth = modifierName.laplacianSmooth

          # laplacian deform
          scene.batchAutoNameModifierNames.laplacianDeform = modifierName.laplacianDeform

          # lattice
          scene.batchAutoNameModifierNames.lattice = modifierName.lattice

          # mesh deform
          scene.batchAutoNameModifierNames.meshDeform = modifierName.meshDeform

          # shrinkwrap
          scene.batchAutoNameModifierNames.shrinkwrap = modifierName.shrinkwrap

          # simple deform
          scene.batchAutoNameModifierNames.simpleDeform = modifierName.simpleDeform

          # smooth
          scene.batchAutoNameModifierNames.smooth = modifierName.smooth

          # warp
          scene.batchAutoNameModifierNames.warp = modifierName.warp

          # wave
          scene.batchAutoNameModifierNames.wave = modifierName.wave

          # cloth
          scene.batchAutoNameModifierNames.cloth = modifierName.cloth

          # collision
          scene.batchAutoNameModifierNames.collision = modifierName.collision

          # dynamic paint
          scene.batchAutoNameModifierNames.dynamicPaint = modifierName.dynamicPaint

          # explode
          scene.batchAutoNameModifierNames.explode = modifierName.explode

          # fluid simulation
          scene.batchAutoNameModifierNames.fluidSimulation = modifierName.fluidSimulation

          # ocean
          scene.batchAutoNameModifierNames.ocean = modifierName.ocean

          # particle instance
          scene.batchAutoNameModifierNames.particleInstance = modifierName.particleInstance

          # particle system
          scene.batchAutoNameModifierNames.particleSystem = modifierName.particleSystem

          # smoke
          scene.batchAutoNameModifierNames.smoke = modifierName.smoke

          # soft body
          scene.batchAutoNameModifierNames.softBody = modifierName.softBody

          # object data name
          objectDataName = context.scene.batchAutoNameObjectDataNames

          # mesh
          scene.batchAutoNameObjectDataNames.mesh = objectDataName.mesh

          # curve
          scene.batchAutoNameObjectDataNames.curve = objectDataName.curve

          # surface
          scene.batchAutoNameObjectDataNames.surface = objectDataName.surface

          # meta
          scene.batchAutoNameObjectDataNames.meta = objectDataName.meta

          # font
          scene.batchAutoNameObjectDataNames.font = objectDataName.font

          # armature
          scene.batchAutoNameObjectDataNames.armature = objectDataName.armature

          # lattice
          scene.batchAutoNameObjectDataNames.lattice = objectDataName.lattice

          # speaker
          scene.batchAutoNameObjectDataNames.speaker = objectDataName.speaker

          # camera
          scene.batchAutoNameObjectDataNames.camera = objectDataName.camera

          # lamp
          scene.batchAutoNameObjectDataNames.lamp = objectDataName.lamp

    # name
    if name:
      for scene in bpy.data.scenes:
        if scene != context.scene:

          # batch name option
          batchNameOption = context.scene.batchNameSettings

          # batch type
          scene.batchNameSettings.batchType = batchNameOption.batchType

          # batch objects
          scene.batchNameSettings.objects = batchNameOption.objects

          # batch object constraints
          scene.batchNameSettings.constraints = batchNameOption.constraints

          # batch modifiers
          scene.batchNameSettings.modifiers = batchNameOption.modifiers

          # batch object data
          scene.batchNameSettings.objectData = batchNameOption.objectData

          # batch bones
          scene.batchNameSettings.bones = batchNameOption.bones

          # batch bone constraints
          scene.batchNameSettings.boneConstraints = batchNameOption.boneConstraints

          # batch materials
          scene.batchNameSettings.materials = batchNameOption.materials

          # batch textures
          scene.batchNameSettings.textures = batchNameOption.textures

          # batch particle systems
          scene.batchNameSettings.particleSystems = batchNameOption.particleSystems

          # batch particle settings
          scene.batchNameSettings.particleSettings = batchNameOption.particleSettings

          # batch groups
          scene.batchNameSettings.groups = batchNameOption.groups

          # batch vertex groups
          scene.batchNameSettings.vertexGroups = batchNameOption.vertexGroups

          # batch shape keys
          scene.batchNameSettings.shapekeys = batchNameOption.shapekeys

          # batch uvs
          scene.batchNameSettings.uvs = batchNameOption.uvs

          # batch vertex colors
          scene.batchNameSettings.vertexColors = batchNameOption.vertexColors

          # batch bone groups
          scene.batchNameSettings.boneGroups = batchNameOption.boneGroups

          # object type
          scene.batchNameSettings.objectType = batchNameOption.objectType

          # constraint type
          scene.batchNameSettings.constraintType = batchNameOption.constraintType

          # modifier type
          scene.batchNameSettings.modifierType = batchNameOption.modifierType

          # scenes
          scene.batchNameSettings.scenes = batchNameOption.scenes

          # render layers
          scene.batchNameSettings.renderLayers = batchNameOption.renderLayers

          # worlds
          scene.batchNameSettings.worlds = batchNameOption.worlds

          # libraries
          scene.batchNameSettings.libraries = batchNameOption.libraries

          # images
          scene.batchNameSettings.images = batchNameOption.images

          # masks
          scene.batchNameSettings.masks = batchNameOption.masks

          # sequences
          scene.batchNameSettings.sequences = batchNameOption.sequences

          # movie clips
          scene.batchNameSettings.movieClips = batchNameOption.movieClips

          # sounds
          scene.batchNameSettings.sounds = batchNameOption.sounds

          # screens
          scene.batchNameSettings.screens = batchNameOption.screens

          # keying sets
          scene.batchNameSettings.keyingSets = batchNameOption.keyingSets

          # palettes
          scene.batchNameSettings.palettes = batchNameOption.palettes

          # brushes
          scene.batchNameSettings.brushes = batchNameOption.brushes

          # linestyles
          scene.batchNameSettings.linestyles = batchNameOption.linestyles

          # nodes
          scene.batchNameSettings.nodes = batchNameOption.nodes

          # node labels
          scene.batchNameSettings.nodeLabels = batchNameOption.nodeLabels

          # node groups
          scene.batchNameSettings.nodeGroups = batchNameOption.nodeGroups

          # texts
          scene.batchNameSettings.texts = batchNameOption.texts

          # name
          scene.batchNameSettings.customName = batchNameOption.customName

          # find
          scene.batchNameSettings.find = batchNameOption.find

          # regex
          scene.batchNameSettings.regex = batchNameOption.regex

          # replace
          scene.batchNameSettings.replace = batchNameOption.replace

          # prefix
          scene.batchNameSettings.prefix = batchNameOption.prefix

          # suffix
          scene.batchNameSettings.suffix = batchNameOption.suffix

          # trim start
          scene.batchNameSettings.trimStart = batchNameOption.trimStart

          # trim end
          scene.batchNameSettings.trimEnd = batchNameOption.trimEnd

          # process
          scene.batchNameSettings.sort = batchNameOption.sort

          # padding
          scene.batchNameSettings.padding = batchNameOption.padding

          # start
          scene.batchNameSettings.start = batchNameOption.start

          # separator
          scene.batchNameSettings.separator = batchNameOption.separator

          # process only
          scene.batchNameSettings.sortOnly = batchNameOption.sortOnly

    # copy
    if copy:
      for scene in bpy.data.scenes[:]:
        if scene != context.scene:

          # batch copy option
          batchCopyOption = context.scene.batchCopySettings

          # batch type
          scene.batchCopySettings.batchType = batchCopyOption.batchType

          # source
          scene.batchCopySettings.source = batchCopyOption.source

          # objects
          scene.batchCopySettings.objects = batchCopyOption.objects

          # object datas
          scene.batchCopySettings.objectData = batchCopyOption.objectData

          # materials
          scene.batchCopySettings.materials = batchCopyOption.materials

          # textures
          scene.batchCopySettings.textures = batchCopyOption.textures

          # particle systems
          scene.batchCopySettings.particleSystems = batchCopyOption.particleSystems

          # particle settings
          scene.batchCopySettings.particleSettings = batchCopyOption.particleSettings

          # use active object
          scene.batchCopySettings.useActiveObject = batchCopyOption.useActiveObject
