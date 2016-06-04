
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

# name
def main(context):
  '''
    Send datablock values to name.
  '''

  # option
  option = context.scene.BatchAutoName

  # mode
  if option.mode in {'SELECTED', 'OBJECTS'}:

    for object in bpy.data.objects[:]:

      # objects
      if option.objects:

        # mode
        if option.mode in 'SELECTED':
          if object.select:

            # object type
            if option.objectType in 'ALL':

              # name
              name(context, object, True, False, False, False)

            # object type
            elif option.objectType in object.type:

              # name
              name(context, object, True, False, False, False)

        # mode
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

        # mode
        if option.mode in 'SELECTED':
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

        # mode
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

        # mode
        if option.mode in 'SELECTED':
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

          # mode
          if option.mode in 'SELECTED':
            if object.select:

              # object type
              if option.objectType in 'ALL':

                # name
                name(context, object, False, False, False, True)

              # object type
              elif option.objectType in object.type:

                # name
                name(context, object, False, False, False, True)

          # mode
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

        # mode
        if option.mode in 'SELECTED':
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

  # mode
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
  option = context.scene.BatchAutoName

  # object name
  objectName = context.scene.BatchAutoName_ObjectNames

  # constraint name
  constraintName = context.scene.BatchAutoName_ConstraintNames

  # modifier name
  modifierName = context.scene.BatchAutoName_ModifierNames

  # object data name
  objectDataName = context.scene.BatchAutoName_ObjectDataNames

  # object
  if object:

    # mesh
    if datablock.type == 'MESH':
      datablock.name = objectName.mesh + datablock.name if objectName.prefix else objectName.mesh

    # curve
    if datablock.type == 'CURVE':
      datablock.name = objectName.curve + datablock.name if objectName.prefix else objectName.curve

    # surface
    if datablock.type == 'SURFACE':
      datablock.name = objectName.surface + datablock.name if objectName.prefix else objectName.surface

    # meta
    if datablock.type == 'META':
      datablock.name = objectName.meta + datablock.name if objectName.prefix else objectName.meta

    # font
    if datablock.type == 'FONT':
      datablock.name = objectName.font + datablock.name if objectName.prefix else objectName.font

    # armature
    if datablock.type == 'ARMATURE':
      datablock.name = objectName.armature + datablock.name if objectName.prefix else objectName.armature

    # lattice
    if datablock.type == 'LATTICE':
      datablock.name = objectName.lattice + datablock.name if objectName.prefix else objectName.lattice

    # empty
    if datablock.type == 'EMPTY':
      datablock.name = objectName.empty + datablock.name if objectName.prefix else objectName.empty

    # speaker
    if datablock.type == 'SPEAKER':
      datablock.name = objectName.speaker + datablock.name if objectName.prefix else objectName.speaker

    # camera
    if datablock.type == 'CAMERA':
      datablock.name = objectName.camera + datablock.name if objectName.prefix else objectName.camera

    # lamp
    if datablock.type == 'LAMP':
      datablock.name = objectName.lamp + datablock.name if objectName.prefix else objectName.lamp

  # constraint (bone constraint)
  if constraint:

    # camera solver
    if datablock.type == 'CAMERA_SOLVER':
      datablock.name = constraintName.cameraSolver + datablock.name if constraintName.prefix else constraintName.cameraSolver

    # follow track
    if datablock.type == 'FOLLOW_TRACK':
      datablock.name = constraintName.followTrack + datablock.name if constraintName.prefix else constraintName.followTrack

    # object solver
    if datablock.type == 'OBJECT_SOLVER':
      datablock.name = constraintName.objectSolver + datablock.name if constraintName.prefix else constraintName.objectSolver

    # copy location
    if datablock.type == 'COPY_LOCATION':
      datablock.name = constraintName.copyLocation + datablock.name if constraintName.prefix else constraintName.copyLocation

    # copy rotation
    if datablock.type == 'COPY_ROTATION':
      datablock.name = constraintName.copyRotation + datablock.name if constraintName.prefix else constraintName.copyRotation

    # copy scale
    if datablock.type == 'COPY_SCALE':
      datablock.name = constraintName.copyScale + datablock.name if constraintName.prefix else constraintName.copyScale

    # copy transforms
    if datablock.type == 'COPY_TRANSFORMS':
      datablock.name = constraintName.copyTransforms + datablock.name if constraintName.prefix else constraintName.copyTransforms

    # limit distance
    if datablock.type == 'LIMIT_DISTANCE':
      datablock.name = constraintName.limitDistance + datablock.name if constraintName.prefix else constraintName.limitDistance

    # limit location
    if datablock.type == 'LIMIT_LOCATION':
      datablock.name = constraintName.limitLocation + datablock.name if constraintName.prefix else constraintName.limitLocation

    # limit rotation
    if datablock.type == 'LIMIT_ROTATION':
      datablock.name = constraintName.limitRotation + datablock.name if constraintName.prefix else constraintName.limitRotation

    # limit scale
    if datablock.type == 'LIMIT_SCALE':
      datablock.name = constraintName.limitScale + datablock.name if constraintName.prefix else constraintName.limitScale

    # maintain volume
    if datablock.type == 'MAINTAIN_VOLUME':
      datablock.name = constraintName.maintainVolume + datablock.name if constraintName.prefix else constraintName.maintainVolume

    # transform
    if datablock.type == 'TRANSFORM':
      datablock.name = constraintName.transform + datablock.name if constraintName.prefix else constraintName.transform

    # clamp to
    if datablock.type == 'CLAMP_TO':
      datablock.name = constraintName.clampTo + datablock.name if constraintName.prefix else constraintName.clampTo

    # damped track
    if datablock.type == 'DAMPED_TRACK':
      datablock.name = constraintName.dampedTrack + datablock.name if constraintName.prefix else constraintName.dampedTrack

    # inverse kinematics
    if datablock.type == 'IK':
      datablock.name = constraintName.inverseKinematics + datablock.name if constraintName.prefix else constraintName.inverseKinematics

    # locked track
    if datablock.type == 'LOCKED_TRACK':
      datablock.name = constraintName.lockedTrack + datablock.name if constraintName.prefix else constraintName.lockedTrack

    # spline inverse kinematics
    if datablock.type == 'SPLINE_IK':
      datablock.name = constraintName.splineInverseKinematics + datablock.name if constraintName.prefix else constraintName.splineInverseKinematics

    # stretch to
    if datablock.type == 'STRETCH_TO':
      datablock.name = constraintName.stretchTo + datablock.name if constraintName.prefix else constraintName.stretchTo

    # track to
    if datablock.type == 'TRACK_TO':
      datablock.name = constraintName.trackTo + datablock.name if constraintName.prefix else constraintName.trackTo

    # action
    if datablock.type == 'ACTION':
      datablock.name = constraintName.action + datablock.name if constraintName.prefix else constraintName.action

    # child of
    if datablock.type == 'CHILD_OF':
      datablock.name = constraintName.childOf + datablock.name if constraintName.prefix else constraintName.childOf

    # floor
    if datablock.type == 'FLOOR':
      datablock.name = constraintName.floor + datablock.name if constraintName.prefix else constraintName.floor

    # follow path
    if datablock.type == 'FOLLOW_PATH':
      datablock.name = constraintName.followPath + datablock.name if constraintName.prefix else constraintName.followPath

    # pivot
    if datablock.type == 'PIVOT':
      datablock.name = constraintName.pivot + datablock.name if constraintName.prefix else constraintName.pivot

    # rigid body joint
    if datablock.type == 'RIGID_BODY_JOINT':
      datablock.name = constraintName.rigidBodyJoint + datablock.name if constraintName.prefix else constraintName.rigidBodyJoint

    # shrinkwrap
    if datablock.type == 'SHRINKWRAP':
      datablock.name = constraintName.shrinkwrap + datablock.name if constraintName.prefix else constraintName.shrinkwrap

  # modifier
  if modifier:

    # data transfer
    if datablock.type == 'DATA_TRANSFER':
      datablock.name = modifierName.dataTransfer + datablock.name if modifierName.prefix else modifierName.dataTransfer

    # mesh cache
    if datablock.type == 'MESH_CACHE':
      datablock.name = modifierName.meshCache + datablock.name if modifierName.prefix else modifierName.meshCache

    # normal edit
    if datablock.type == 'NORMAL_EDIT':
      datablock.name = modifierName.normalEdit + datablock.name if modifierName.prefix else modifierName.normalEdit

    # uv project
    if datablock.type == 'UV_PROJECT':
      datablock.name = modifierName.uvProject + datablock.name if modifierName.prefix else modifierName.uvProject

    # uv warp
    if datablock.type == 'UV_WARP':
      datablock.name = modifierName.uvWarp + datablock.name if modifierName.prefix else modifierName.uvWarp

    # vertex weight edit
    if datablock.type == 'VERTEX_WEIGHT_EDIT':
      datablock.name = modifierName.vertexWeightEdit + datablock.name if modifierName.prefix else modifierName.vertexWeightEdit

    # vertex weight mix
    if datablock.type == 'VERTEX_WEIGHT_MIX':
      datablock.name = modifierName.vertexWeightMix + datablock.name if modifierName.prefix else modifierName.vertexWeightMix

    # vertex weight proximity
    if datablock.type == 'VERTEX_WEIGHT_PROXIMITY':
      datablock.name = modifierName.vertexWeightProximity + datablock.name if modifierName.prefix else modifierName.vertexWeightProximity

    # array
    if datablock.type == 'ARRAY':
      datablock.name = modifierName.array + datablock.name if modifierName.prefix else modifierName.array

    # bevel
    if datablock.type == 'BEVEL':
      datablock.name = modifierName.bevel + datablock.name if modifierName.prefix else modifierName.bevel

    # boolean
    if datablock.type == 'BOOLEAN':
      datablock.name = modifierName.boolean + datablock.name if modifierName.prefix else modifierName.boolean

    # build
    if datablock.type == 'BUILD':
      datablock.name = modifierName.build + datablock.name if modifierName.prefix else modifierName.build

    # decimate
    if datablock.type == 'DECIMATE':
      datablock.name = modifierName.decimate + datablock.name if modifierName.prefix else modifierName.decimate

    # edge split
    if datablock.type == 'EDGE_SPLIT':
      datablock.name = modifierName.edgeSplit + datablock.name if modifierName.prefix else modifierName.edgeSplit

    # mask
    if datablock.type == 'MASK':
      datablock.name = modifierName.mask + datablock.name if modifierName.prefix else modifierName.mask

    # mirror
    if datablock.type == 'MIRROR':
      datablock.name = modifierName.mirror + datablock.name if modifierName.prefix else modifierName.mirror

    # multiresolution
    if datablock.type == 'MULTIRES':
      datablock.name = modifierName.multiresolution + datablock.name if modifierName.prefix else modifierName.multiresolution

    # remesh
    if datablock.type == 'REMESH':
      datablock.name = modifierName.remesh + datablock.name if modifierName.prefix else modifierName.remesh

    # screw
    if datablock.type == 'SCREW':
      datablock.name = modifierName.screw + datablock.name if modifierName.prefix else modifierName.screw

    # skin
    if datablock.type == 'SKIN':
      datablock.name = modifierName.skin + datablock.name if modifierName.prefix else modifierName.skin

    # solidify
    if datablock.type == 'SOLIDIFY':
      datablock.name = modifierName.solidify + datablock.name if modifierName.prefix else modifierName.solidify

    # subdivision surface
    if datablock.type == 'SUBSURF':
      datablock.name = modifierName.subdivisionSurface + datablock.name if modifierName.prefix else modifierName.subdivisionSurface

    # triangulate
    if datablock.type == 'TRIANGULATE':
      datablock.name = modifierName.triangulate + datablock.name if modifierName.prefix else modifierName.triangulate

    # wireframe
    if datablock.type == 'WIREFRAME':
      datablock.name = modifierName.wireframe + datablock.name if modifierName.prefix else modifierName.wireframe

    # armature
    if datablock.type == 'ARMATURE':
      datablock.name = modifierName.armature + datablock.name if modifierName.prefix else modifierName.armature

    # cast
    if datablock.type == 'CAST':
      datablock.name = modifierName.cast + datablock.name if modifierName.prefix else modifierName.cast

    # corrective smooth
    if datablock.type == 'CORRECTIVE_SMOOTH':
      datablock.name = modifierName.correctiveSmooth + datablock.name if modifierName.prefix else modifierName.correctiveSmooth

    # curve
    if datablock.type == 'CURVE':
      datablock.name = modifierName.curve + datablock.name if modifierName.prefix else modifierName.curve

    # displace
    if datablock.type == 'DISPLACE':
      datablock.name = modifierName.displace + datablock.name if modifierName.prefix else modifierName.displace

    # hook
    if datablock.type == 'HOOK':
      datablock.name = modifierName.hook + datablock.name if modifierName.prefix else modifierName.hook

    # laplacian smooth
    if datablock.type == 'LAPLACIANSMOOTH':
      datablock.name = modifierName.laplacianSmooth + datablock.name if modifierName.prefix else modifierName.laplacianSmooth

    # laplacian deform
    if datablock.type == 'LAPLACIANDEFORM':
      datablock.name = modifierName.laplacianDeform + datablock.name if modifierName.prefix else modifierName.laplacianDeform

    # lattice
    if datablock.type == 'LATTICE':
      datablock.name = modifierName.lattice + datablock.name if modifierName.prefix else modifierName.lattice

    # mesh deform
    if datablock.type == 'MESH_DEFORM':
      datablock.name = modifierName.meshDeform + datablock.name if modifierName.prefix else modifierName.meshDeform

    # shrinkwrap
    if datablock.type == 'SHRINKWRAP':
      datablock.name = modifierName.shrinkwrap + datablock.name if modifierName.prefix else modifierName.shrinkwrap

    # simple deform
    if datablock.type == 'SIMPLE_DEFORM':
      datablock.name = modifierName.simpleDeform + datablock.name if modifierName.prefix else modifierName.simpleDeform

    # smooth
    if datablock.type == 'SMOOTH':
      datablock.name = modifierName.smooth + datablock.name if modifierName.prefix else modifierName.smooth

    # warp
    if datablock.type == 'WARP':
      datablock.name = modifierName.warp + datablock.name if modifierName.prefix else modifierName.warp

    # wave
    if datablock.type == 'WAVE':
      datablock.name = modifierName.wave + datablock.name if modifierName.prefix else modifierName.wave

    # cloth
    if datablock.type == 'CLOTH':
      datablock.name = modifierName.cloth + datablock.name if modifierName.prefix else modifierName.cloth

    # collision
    if datablock.type == 'COLLISION':
      datablock.name = modifierName.collision + datablock.name if modifierName.prefix else modifierName.collision

    # dynamic paint
    if datablock.type == 'DYNAMIC_PAINT':
      datablock.name = modifierName.dynamicPaint + datablock.name if modifierName.prefix else modifierName.dynamicPaint

    # explode
    if datablock.type == 'EXPLODE':
      datablock.name = modifierName.explode + datablock.name if modifierName.prefix else modifierName.explode

    # fluid simulation
    if datablock.type == 'FLUID_SIMULATION':
      datablock.name = modifierName.fluidSimulation + datablock.name if modifierName.prefix else modifierName.fluidSimulation

    # ocean
    if datablock.type == 'OCEAN':
      datablock.name = modifierName.ocean + datablock.name if modifierName.prefix else modifierName.ocean

    # particle instance
    if datablock.type == 'PARTICLE_INSTANCE':
      datablock.name = modifierName.particleInstance + datablock.name if modifierName.prefix else modifierName.particleInstance

    # particle system
    if datablock.type == 'PARTICLE_SYSTEM':
      datablock.name = modifierName.particleSystem + datablock.name if modifierName.prefix else modifierName.particleSystem

    # smoke
    if datablock.type == 'SMOKE':
      datablock.name = modifierName.smoke + datablock.name if modifierName.prefix else modifierName.smoke

    # soft body
    if datablock.type == 'SOFT_BODY':
      datablock.name = modifierName.softBody + datablock.name if modifierName.prefix else modifierName.softBody

  # object data
  if objectData:

    # mesh
    if datablock.type == 'MESH':
      datablock.data.name = objectDataName.mesh + datablock.data.name if objectDataName.prefix else objectDataName.mesh

    # curve
    if datablock.type == 'CURVE':
      datablock.data.name = objectDataName.curve + datablock.data.name if objectDataName.prefix else objectDataName.curve

    # surface
    if datablock.type == 'SURFACE':
      datablock.data.name = objectDataName.surface + datablock.data.name if objectDataName.prefix else objectDataName.surface

    # meta
    if datablock.type == 'META':
      datablock.data.name = objectDataName.meta + datablock.data.name if objectDataName.prefix else objectDataName.meta

    # font
    if datablock.type == 'FONT':
      datablock.data.name = objectDataName.font + datablock.data.name if objectDataName.prefix else objectDataName.font

    # armature
    if datablock.type == 'ARMATURE':
      datablock.data.name = objectDataName.armature + datablock.data.name if objectDataName.prefix else objectDataName.armature

    # lattice
    if datablock.type == 'LATTICE':
      datablock.data.name = objectDataName.lattice + datablock.data.name if objectDataName.prefix else objectDataName.lattice

    # empty
    if datablock.type == 'EMPTY':
      pass
      # datablock.data.name = objectDataName.empty + datablock.data.name if objectDataName.prefix else objectDataName.empty

    # speaker
    if datablock.type == 'SPEAKER':
      datablock.data.name = objectDataName.speaker + datablock.data.name if objectDataName.prefix else objectDataName.speaker

    # camera
    if datablock.type == 'CAMERA':
      datablock.data.name = objectDataName.camera + datablock.data.name if objectDataName.prefix else objectDataName.camera

    # lamp
    if datablock.type == 'LAMP':
      datablock.data.name = objectDataName.lamp + datablock.data.name if objectDataName.prefix else objectDataName.lamp
