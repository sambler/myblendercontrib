
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
from random import random
from . import shared
from .. import storage

# name
def main(self, context):
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

      # constraints
      if option.constraints:

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

      # modifiers
      if option.modifiers:

        # mode
        if option.mode in 'SELECTED':
          if object.select:
            for modifier in object.modifiers[:]:

              # modifier type
              if option.modifierType in 'ALL':

                # populate
                populate(context, modifier)

              # modifier type
              elif option.modifierType in modifier.type:

                # populate
                populate(context, modifier)
        else:
          for modifier in object.modifiers[:]:

            # modifier type
            if option.modifierType in 'ALL':

              # populate
              populate(context, modifier)

            # modifier type
            elif option.modifierType in modifier.type:

              # populate
              populate(context, modifier)

      # object data
      if option.objectData:
        if object.type not in 'EMPTY':

          # mode
          if option.mode in 'SELECTED':
            if object.select:

              # object type
              if option.objectType in 'ALL':

                # populate
                populate(context, object.data, object)

              # object type
              elif option.objectType in object.type:

                # populate
                populate(context, object.data, object)

          # mode
          else:

            # object type
            if option.objectType in 'ALL':

              # populate
              populate(context, object.data, object)

            # object type
            elif option.objectType in object.type:

              # populate
              populate(context, object.data, object)

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

                      # populate
                      populate(context, constraint)

                    # constraint type
                    elif option.constraintType in constraint.type:

                      # populate
                      populate(context, constraint)
        else:
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

  # mode
  else:
    for object in context.scene.objects[:]:

      # objects
      if option.objects:

        # object type
        if option.objectType in 'ALL':

          # populate
          populate(context, object)

        # object type
        elif option.objectType in object.type:

          # populate
          populate(context, object)

      # constraints
      if option.constraints:
        for constraint in object.constraints[:]:

          # constraint type
          if option.constraintType in 'ALL':

            # populate
            populate(context, constraint)

          # constraint type
          elif option.constraintType in constraint.type:

            # populate
            populate(context, constraint)

      # modifiers
      if option.modifiers:
        for modifier in object.modifiers[:]:

          # modifier type
          if option.modifierType in 'ALL':

            # populate
            populate(context, modifier)

          # modifier type
          elif option.modifierType in modifier.type:

            # populate
            populate(context, modifier)

      # object data
      if option.objectData:
        if object.type not in 'EMPTY':

          # object type
          if option.objectType in 'ALL':

            # populate
            populate(context, object.data, object)

          # object type
          elif option.objectType in object.type:

            # populate
            populate(context, object.data, object)

      # bone constraints
      if option.boneConstraints:
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

  # all
  all = [
    # object
    storage.batch.objects,

    # constraints
    storage.batch.constraints,

    # modifiers
    storage.batch.modifiers,

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
  ]

  # process
  for collection in all:
    if collection != []:

      # process
      process(self, context, collection)

# populate
def populate(context, datablock, source=None):
  '''
    Sort datablocks into proper storage list.
  '''

  # option
  option = context.scene.BatchName

  # objects
  if datablock.rna_type.identifier == 'Object':
    storage.batch.objects.append([datablock.name, datablock.name, datablock.name, [datablock, ''], 'OBJECT'])

  # constraints
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier == 'Constraint':
      storage.batch.constraints.append([datablock.name, datablock.name, datablock.name, [datablock, ''], 'CONSTRAINT'])

  # modifiers
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier in 'Modifier':
      storage.batch.modifiers.append([datablock.name, datablock.name, datablock.name, [datablock, ''], 'MODIFIER'])

  # cameras
  if datablock.rna_type.identifier == 'Camera':
    storage.batch.cameras.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # meshes
  if datablock.rna_type.identifier == 'Mesh':
    storage.batch.meshes.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # curves
  if datablock.rna_type.identifier in {'SurfaceCurve', 'TextCurve', 'Curve'}:
    storage.batch.curves.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # lamps
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier == 'Lamp':
      storage.batch.lamps.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # lattices
  if datablock.rna_type.identifier == 'Lattice':
    storage.batch.lattices.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # metaballs
  if datablock.rna_type.identifier == 'MetaBall':
    storage.batch.metaballs.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # speakers
  if datablock.rna_type.identifier == 'Speaker':
    storage.batch.speakers.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # armatures
  if datablock.rna_type.identifier == 'Armature':
    storage.batch.armatures.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

def process(self, context, collection):
  '''
    Process collection, send names to rename and shared sort.
  '''

  # compare
  compare = []

  # clean
  clean = []

  # clean duplicates
  for name in collection:

    # remove duplicates
    if name[3][0] not in compare:

      # append
      compare.append(name[3][0])
      clean.append(name)

  # don with collection
  collection.clear()

  # name
  for name in clean:
    rename(self, context, name)

  # randomize names (prevents conflicts)
  for name in clean:

    # randomize name
    name[3][0].name = str(random())

  # is shared sort
  if context.scene.BatchShared.sort:

    # sort
    shared.sort(self, context, clean, context.scene.BatchShared)

  # isnt shared sort
  else:

    # apply names
    for name in clean:
      name[3][0].name = name[1]

      # count
      if name[1] != name[2]:
        self.count += 1

    # done with clean
    clean.clear()

# object
def rename(self, context, name):
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
  if name[4] == 'OBJECT':

    # mesh
    if name[3][0].type == 'MESH':
      name[1] = objectName.mesh + name[1] if objectName.prefix else objectName.mesh

    # curve
    if name[3][0].type == 'CURVE':
      name[1] = objectName.curve + name[1] if objectName.prefix else objectName.curve

    # surface
    if name[3][0].type == 'SURFACE':
      name[1] = objectName.surface + name[1] if objectName.prefix else objectName.surface

    # meta
    if name[3][0].type == 'META':
      name[1] = objectName.meta + name[1] if objectName.prefix else objectName.meta

    # font
    if name[3][0].type == 'FONT':
      name[1] = objectName.font + name[1] if objectName.prefix else objectName.font

    # armature
    if name[3][0].type == 'ARMATURE':
      name[1] = objectName.armature + name[1] if objectName.prefix else objectName.armature

    # lattice
    if name[3][0].type == 'LATTICE':
      name[1] = objectName.lattice + name[1] if objectName.prefix else objectName.lattice

    # empty
    if name[3][0].type == 'EMPTY':
      name[1] = objectName.empty + name[1] if objectName.prefix else objectName.empty

    # speaker
    if name[3][0].type == 'SPEAKER':
      name[1] = objectName.speaker + name[1] if objectName.prefix else objectName.speaker

    # camera
    if name[3][0].type == 'CAMERA':
      name[1] = objectName.camera + name[1] if objectName.prefix else objectName.camera

    # lamp
    if name[3][0].type == 'LAMP':
      name[1] = objectName.lamp + name[1] if objectName.prefix else objectName.lamp

  # constraint (bone constraint)
  if name[4] == 'CONSTRAINT':

    # camera solver
    if name[3][0].type == 'CAMERA_SOLVER':
      name[1] = constraintName.cameraSolver + name[1] if constraintName.prefix else constraintName.cameraSolver

    # follow track
    if name[3][0].type == 'FOLLOW_TRACK':
      name[1] = constraintName.followTrack + name[1] if constraintName.prefix else constraintName.followTrack

    # object solver
    if name[3][0].type == 'OBJECT_SOLVER':
      name[1] = constraintName.objectSolver + name[1] if constraintName.prefix else constraintName.objectSolver

    # copy location
    if name[3][0].type == 'COPY_LOCATION':
      name[1] = constraintName.copyLocation + name[1] if constraintName.prefix else constraintName.copyLocation

    # copy rotation
    if name[3][0].type == 'COPY_ROTATION':
      name[1] = constraintName.copyRotation + name[1] if constraintName.prefix else constraintName.copyRotation

    # copy scale
    if name[3][0].type == 'COPY_SCALE':
      name[1] = constraintName.copyScale + name[1] if constraintName.prefix else constraintName.copyScale

    # copy transforms
    if name[3][0].type == 'COPY_TRANSFORMS':
      name[1] = constraintName.copyTransforms + name[1] if constraintName.prefix else constraintName.copyTransforms

    # limit distance
    if name[3][0].type == 'LIMIT_DISTANCE':
      name[1] = constraintName.limitDistance + name[1] if constraintName.prefix else constraintName.limitDistance

    # limit location
    if name[3][0].type == 'LIMIT_LOCATION':
      name[1] = constraintName.limitLocation + name[1] if constraintName.prefix else constraintName.limitLocation

    # limit rotation
    if name[3][0].type == 'LIMIT_ROTATION':
      name[1] = constraintName.limitRotation + name[1] if constraintName.prefix else constraintName.limitRotation

    # limit scale
    if name[3][0].type == 'LIMIT_SCALE':
      name[1] = constraintName.limitScale + name[1] if constraintName.prefix else constraintName.limitScale

    # maintain volume
    if name[3][0].type == 'MAINTAIN_VOLUME':
      name[1] = constraintName.maintainVolume + name[1] if constraintName.prefix else constraintName.maintainVolume

    # transform
    if name[3][0].type == 'TRANSFORM':
      name[1] = constraintName.transform + name[1] if constraintName.prefix else constraintName.transform

    # clamp to
    if name[3][0].type == 'CLAMP_TO':
      name[1] = constraintName.clampTo + name[1] if constraintName.prefix else constraintName.clampTo

    # damped track
    if name[3][0].type == 'DAMPED_TRACK':
      name[1] = constraintName.dampedTrack + name[1] if constraintName.prefix else constraintName.dampedTrack

    # inverse kinematics
    if name[3][0].type == 'IK':
      name[1] = constraintName.inverseKinematics + name[1] if constraintName.prefix else constraintName.inverseKinematics

    # locked track
    if name[3][0].type == 'LOCKED_TRACK':
      name[1] = constraintName.lockedTrack + name[1] if constraintName.prefix else constraintName.lockedTrack

    # spline inverse kinematics
    if name[3][0].type == 'SPLINE_IK':
      name[1] = constraintName.splineInverseKinematics + name[1] if constraintName.prefix else constraintName.splineInverseKinematics

    # stretch to
    if name[3][0].type == 'STRETCH_TO':
      name[1] = constraintName.stretchTo + name[1] if constraintName.prefix else constraintName.stretchTo

    # track to
    if name[3][0].type == 'TRACK_TO':
      name[1] = constraintName.trackTo + name[1] if constraintName.prefix else constraintName.trackTo

    # action
    if name[3][0].type == 'ACTION':
      name[1] = constraintName.action + name[1] if constraintName.prefix else constraintName.action

    # child of
    if name[3][0].type == 'CHILD_OF':
      name[1] = constraintName.childOf + name[1] if constraintName.prefix else constraintName.childOf

    # floor
    if name[3][0].type == 'FLOOR':
      name[1] = constraintName.floor + name[1] if constraintName.prefix else constraintName.floor

    # follow path
    if name[3][0].type == 'FOLLOW_PATH':
      name[1] = constraintName.followPath + name[1] if constraintName.prefix else constraintName.followPath

    # pivot
    if name[3][0].type == 'PIVOT':
      name[1] = constraintName.pivot + name[1] if constraintName.prefix else constraintName.pivot

    # rigid body joint
    if name[3][0].type == 'RIGID_BODY_JOINT':
      name[1] = constraintName.rigidBodyJoint + name[1] if constraintName.prefix else constraintName.rigidBodyJoint

    # shrinkwrap
    if name[3][0].type == 'SHRINKWRAP':
      name[1] = constraintName.shrinkwrap + name[1] if constraintName.prefix else constraintName.shrinkwrap

  # modifier
  if name[4] == 'MODIFIER':

    # data transfer
    if name[3][0].type == 'DATA_TRANSFER':
      name[1] = modifierName.dataTransfer + name[1] if modifierName.prefix else modifierName.dataTransfer

    # mesh cache
    if name[3][0].type == 'MESH_CACHE':
      name[1] = modifierName.meshCache + name[1] if modifierName.prefix else modifierName.meshCache

    # normal edit
    if name[3][0].type == 'NORMAL_EDIT':
      name[1] = modifierName.normalEdit + name[1] if modifierName.prefix else modifierName.normalEdit

    # uv project
    if name[3][0].type == 'UV_PROJECT':
      name[1] = modifierName.uvProject + name[1] if modifierName.prefix else modifierName.uvProject

    # uv warp
    if name[3][0].type == 'UV_WARP':
      name[1] = modifierName.uvWarp + name[1] if modifierName.prefix else modifierName.uvWarp

    # vertex weight edit
    if name[3][0].type == 'VERTEX_WEIGHT_EDIT':
      name[1] = modifierName.vertexWeightEdit + name[1] if modifierName.prefix else modifierName.vertexWeightEdit

    # vertex weight mix
    if name[3][0].type == 'VERTEX_WEIGHT_MIX':
      name[1] = modifierName.vertexWeightMix + name[1] if modifierName.prefix else modifierName.vertexWeightMix

    # vertex weight proximity
    if name[3][0].type == 'VERTEX_WEIGHT_PROXIMITY':
      name[1] = modifierName.vertexWeightProximity + name[1] if modifierName.prefix else modifierName.vertexWeightProximity

    # array
    if name[3][0].type == 'ARRAY':
      name[1] = modifierName.array + name[1] if modifierName.prefix else modifierName.array

    # bevel
    if name[3][0].type == 'BEVEL':
      name[1] = modifierName.bevel + name[1] if modifierName.prefix else modifierName.bevel

    # boolean
    if name[3][0].type == 'BOOLEAN':
      name[1] = modifierName.boolean + name[1] if modifierName.prefix else modifierName.boolean

    # build
    if name[3][0].type == 'BUILD':
      name[1] = modifierName.build + name[1] if modifierName.prefix else modifierName.build

    # decimate
    if name[3][0].type == 'DECIMATE':
      name[1] = modifierName.decimate + name[1] if modifierName.prefix else modifierName.decimate

    # edge split
    if name[3][0].type == 'EDGE_SPLIT':
      name[1] = modifierName.edgeSplit + name[1] if modifierName.prefix else modifierName.edgeSplit

    # mask
    if name[3][0].type == 'MASK':
      name[1] = modifierName.mask + name[1] if modifierName.prefix else modifierName.mask

    # mirror
    if name[3][0].type == 'MIRROR':
      name[1] = modifierName.mirror + name[1] if modifierName.prefix else modifierName.mirror

    # multiresolution
    if name[3][0].type == 'MULTIRES':
      name[1] = modifierName.multiresolution + name[1] if modifierName.prefix else modifierName.multiresolution

    # remesh
    if name[3][0].type == 'REMESH':
      name[1] = modifierName.remesh + name[1] if modifierName.prefix else modifierName.remesh

    # screw
    if name[3][0].type == 'SCREW':
      name[1] = modifierName.screw + name[1] if modifierName.prefix else modifierName.screw

    # skin
    if name[3][0].type == 'SKIN':
      name[1] = modifierName.skin + name[1] if modifierName.prefix else modifierName.skin

    # solidify
    if name[3][0].type == 'SOLIDIFY':
      name[1] = modifierName.solidify + name[1] if modifierName.prefix else modifierName.solidify

    # subdivision surface
    if name[3][0].type == 'SUBSURF':
      name[1] = modifierName.subdivisionSurface + name[1] if modifierName.prefix else modifierName.subdivisionSurface

    # triangulate
    if name[3][0].type == 'TRIANGULATE':
      name[1] = modifierName.triangulate + name[1] if modifierName.prefix else modifierName.triangulate

    # wireframe
    if name[3][0].type == 'WIREFRAME':
      name[1] = modifierName.wireframe + name[1] if modifierName.prefix else modifierName.wireframe

    # armature
    if name[3][0].type == 'ARMATURE':
      name[1] = modifierName.armature + name[1] if modifierName.prefix else modifierName.armature

    # cast
    if name[3][0].type == 'CAST':
      name[1] = modifierName.cast + name[1] if modifierName.prefix else modifierName.cast

    # corrective smooth
    if name[3][0].type == 'CORRECTIVE_SMOOTH':
      name[1] = modifierName.correctiveSmooth + name[1] if modifierName.prefix else modifierName.correctiveSmooth

    # curve
    if name[3][0].type == 'CURVE':
      name[1] = modifierName.curve + name[1] if modifierName.prefix else modifierName.curve

    # displace
    if name[3][0].type == 'DISPLACE':
      name[1] = modifierName.displace + name[1] if modifierName.prefix else modifierName.displace

    # hook
    if name[3][0].type == 'HOOK':
      name[1] = modifierName.hook + name[1] if modifierName.prefix else modifierName.hook

    # laplacian smooth
    if name[3][0].type == 'LAPLACIANSMOOTH':
      name[1] = modifierName.laplacianSmooth + name[1] if modifierName.prefix else modifierName.laplacianSmooth

    # laplacian deform
    if name[3][0].type == 'LAPLACIANDEFORM':
      name[1] = modifierName.laplacianDeform + name[1] if modifierName.prefix else modifierName.laplacianDeform

    # lattice
    if name[3][0].type == 'LATTICE':
      name[1] = modifierName.lattice + name[1] if modifierName.prefix else modifierName.lattice

    # mesh deform
    if name[3][0].type == 'MESH_DEFORM':
      name[1] = modifierName.meshDeform + name[1] if modifierName.prefix else modifierName.meshDeform

    # shrinkwrap
    if name[3][0].type == 'SHRINKWRAP':
      name[1] = modifierName.shrinkwrap + name[1] if modifierName.prefix else modifierName.shrinkwrap

    # simple deform
    if name[3][0].type == 'SIMPLE_DEFORM':
      name[1] = modifierName.simpleDeform + name[1] if modifierName.prefix else modifierName.simpleDeform

    # smooth
    if name[3][0].type == 'SMOOTH':
      name[1] = modifierName.smooth + name[1] if modifierName.prefix else modifierName.smooth

    # warp
    if name[3][0].type == 'WARP':
      name[1] = modifierName.warp + name[1] if modifierName.prefix else modifierName.warp

    # wave
    if name[3][0].type == 'WAVE':
      name[1] = modifierName.wave + name[1] if modifierName.prefix else modifierName.wave

    # cloth
    if name[3][0].type == 'CLOTH':
      name[1] = modifierName.cloth + name[1] if modifierName.prefix else modifierName.cloth

    # collision
    if name[3][0].type == 'COLLISION':
      name[1] = modifierName.collision + name[1] if modifierName.prefix else modifierName.collision

    # dynamic paint
    if name[3][0].type == 'DYNAMIC_PAINT':
      name[1] = modifierName.dynamicPaint + name[1] if modifierName.prefix else modifierName.dynamicPaint

    # explode
    if name[3][0].type == 'EXPLODE':
      name[1] = modifierName.explode + name[1] if modifierName.prefix else modifierName.explode

    # fluid simulation
    if name[3][0].type == 'FLUID_SIMULATION':
      name[1] = modifierName.fluidSimulation + name[1] if modifierName.prefix else modifierName.fluidSimulation

    # ocean
    if name[3][0].type == 'OCEAN':
      name[1] = modifierName.ocean + name[1] if modifierName.prefix else modifierName.ocean

    # particle instance
    if name[3][0].type == 'PARTICLE_INSTANCE':
      name[1] = modifierName.particleInstance + name[1] if modifierName.prefix else modifierName.particleInstance

    # particle system
    if name[3][0].type == 'PARTICLE_SYSTEM':
      name[1] = modifierName.particleSystem + name[1] if modifierName.prefix else modifierName.particleSystem

    # smoke
    if name[3][0].type == 'SMOKE':
      name[1] = modifierName.smoke + name[1] if modifierName.prefix else modifierName.smoke

    # soft body
    if name[3][0].type == 'SOFT_BODY':
      name[1] = modifierName.softBody + name[1] if modifierName.prefix else modifierName.softBody

  # object data
  if name[4] == 'DATA':

    # mesh
    if name[3][2].type == 'MESH':
      name[1] = objectDataName.mesh + name[1] if objectDataName.prefix else objectDataName.mesh

    # curve
    if name[3][2].type == 'CURVE':
      name[1] = objectDataName.curve + name[1] if objectDataName.prefix else objectDataName.curve

    # surface
    if name[3][2].type == 'SURFACE':
      name[1] = objectDataName.surface + name[1] if objectDataName.prefix else objectDataName.surface

    # meta
    if name[3][2].type == 'META':
      name[1] = objectDataName.meta + name[1] if objectDataName.prefix else objectDataName.meta

    # font
    if name[3][2].type == 'FONT':
      name[1] = objectDataName.font + name[1] if objectDataName.prefix else objectDataName.font

    # armature
    if name[3][2].type == 'ARMATURE':
      name[1] = objectDataName.armature + name[1] if objectDataName.prefix else objectDataName.armature

    # lattice
    if name[3][2].type == 'LATTICE':
      name[1] = objectDataName.lattice + name[1] if objectDataName.prefix else objectDataName.lattice

    # empty
    if name[3][2].type == 'EMPTY':
      pass
      # name[1] = objectDataName.empty + name[1] if objectDataName.prefix else objectDataName.empty

    # speaker
    if name[3][2].type == 'SPEAKER':
      name[1] = objectDataName.speaker + name[1] if objectDataName.prefix else objectDataName.speaker

    # camera
    if name[3][2].type == 'CAMERA':
      name[1] = objectDataName.camera + name[1] if objectDataName.prefix else objectDataName.camera

    # lamp
    if name[3][2].type == 'LAMP':
      name[1] = objectDataName.lamp + name[1] if objectDataName.prefix else objectDataName.lamp
