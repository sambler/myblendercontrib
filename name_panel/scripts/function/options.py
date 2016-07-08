
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
from .. import storage
from ..defaults import defaults

# reset
def reset(context, panel, auto, names, name, copy):
  '''
    Resets the property values for the name panel add-on.
  '''

  # panel
  if panel:

    # defaults
    default = defaults['name panel']

    # name panel option
    option = context.scene.NamePanel

    # pin active object
    option.pinActiveObject = default['pin active object']

    # hide search
    option.hideSearch = default['hide search']

    # filters
    option.filters = default['filters']

    # options
    option.options = default['options']

    # selected
    option.displayNames = default['selected']

    # mode
    option.mode = default['mode']

    # search
    option.search = default['search']

    # regex
    option.regex = defatul['regex']

    # groups
    option.groups = default['groups']

    # action
    option.action = default['action']

    # grease pencil
    option.greasePencil = default['greasePencil']

    # constraints
    option.constraints = default['constraints']

    # modifiers
    option.modifiers = default['modifiers']

    # bone groups
    option.boneGroups = default['bone groups']

    # bone constraints
    option.boneConstraints = default['bone constraints']

    # vertex groups
    option.vertexGroups = default['vertex groups']

    # shapekeys
    option.shapekeys = default['shapekeys']

    # uvs
    option.uvs = default['uvs']

    # vertex colors
    option.vertexColors = default['vertex colors']

    # materials
    option.materials = default['materials']

    # textures
    option.textures = default['textures']

    # particle systems
    option.particleSystems = default['particle systems']

    # display bones
    option.displayBones = default['display bones']

    # bone mode
    option.boneMode = default['bone mode']

  # auto
  if auto:

    # default
    default = defaults['auto name']

    # auto name option
    option = context.scene.BatchAutoName

    # mode
    option.mode = default['mode']

    # objects
    option.objects = default['objects']

    # constraints
    option.constraints = default['constraints']

    # modifiers
    option.modifiers = default['modifiers']

    # object data
    option.objectData = default['object data']

    # bone constraints
    option.boneConstraints = default['bone constraints']

    # object type
    option.objectType = default['object type']

    # constraint type
    option.constraintType = default['constraint type']

    # modifier type
    option.modifierType = default['modifier type']

    # option
    option = context.scene.BatchShared

    # default
    default = defaults['shared']

    # sort
    option.sort = default['sort']

    # padding
    option.pad = default['pad']

    # start
    option.start = default['start']

    # step
    option.start = default['step']

    # separator
    option.separator = default['separator']

    # link
    option.link = default['link']

    # ignore ignore
    option.ignore = default['ignore']

  # names
  if names:

    # default
    default = defaults['auto name']['object names']

    # object name
    option = context.scene.BatchAutoName_ObjectNames

    # prefix
    option.prefix = default['prefix']

    # mesh
    option.mesh = default['mesh']

    # curve
    option.curve = default['curve']

    # surface
    option.surface = default['surface']

    # meta
    option.meta = default['meta']

    # font
    option.font = default['font']

    # armature
    option.armature = default['armature']

    # lattice
    option.lattice = default['lattice']

    # empty
    option.empty = default['empty']

    # speaker
    option.speaker = default['speaker']

    # camera
    option.camera = default['camera']

    # lamp
    option.lamp = default['lamp']

    # default
    default = defaults['auto name']['constraint names']

    # constraint name
    option = context.scene.BatchAutoName_ConstraintNames

    # prefix
    option.prefix = default['prefix']

    # camera solver
    option.cameraSolver = default['camera solver']

    # follow track
    option.followTrack = default['follow track']

    # object solver
    option.objectSolver = default['object solver']

    # copy location
    option.copyLocation = default['copy location']

    # copy rotation
    option.copyRotation = default['copy rotation']

    # copy scale
    option.copyScale = default['copy scale']

    # copy transforms
    option.copyTransforms = default['copy transforms']

    # limit distance
    option.limitDistance = default['limit distance']

    # limit location
    option.limitLocation = default['limit location']

    # limit rotation
    option.limitRotation = default['limit rotation']

    # limit scale
    option.limitScale = default['limit scale']

    # maintain volume
    option.maintainVolume = default['maintain volume']

    # transform
    option.transform = default['transform']

    # clamp to
    option.clampTo = default['clamp to']

    # damped track
    option.dampedTrack = default['damped track']

    # inverse kinematics
    option.inverseKinematics = default['inverse kinematics']

    # locked track
    option.lockedTrack = default['locked track']

    # spline inverse kinematics
    option.splineInverseKinematics = default['spline inverse kinematics']

    # stretch to
    option.stretchTo = default['stretch to']

    # track to
    option.trackTo = default['track to']

    # action
    option.action = default['action']

    # child of
    option.childOf = default['child of']

    # floor
    option.floor = default['floor']

    # follow path
    option.followPath = default['follow path']

    # pivot
    option.pivot = default['pivot']

    # rigid body joint
    option.rigidBodyJoint = default['rigid body joint']

    # shrinkwrap
    option.shrinkwrap = default['shrinkwrap']

    # default
    default = defaults['auto name']['modifier names']

    # modifier name
    option = context.scene.BatchAutoName_ModifierNames

    # prefix
    option.prefix = default['prefix']

    # data transfer
    option.dataTransfer = default['data transfer']

    # mesh cache
    option.meshCache = default['mesh cache']

    # normal edit
    option.normalEdit = default['normal edit']

    # uv project
    option.uvProject = default['uv project']

    # uv warp
    option.uvWarp = default['uv warp']

    # vertex weight edit
    option.vertexWeightEdit = default['vertex weight edit']

    # vertex weight mix
    option.vertexWeightMix = default['vertex weight mix']

    # vertex weight proximity
    option.vertexWeightProximity = default['vertex weight proximity']

    # array
    option.array = default['array']

    # bevel
    option.bevel = default['bevel']

    # boolean
    option.boolean = default['boolean']

    # build
    option.build = default['build']

    # decimate
    option.decimate = default['decimate']

    # edge split
    option.edgeSplit = default['edge split']

    # mask
    option.mask = default['mask']

    # mirror
    option.mirror = default['mirror']

    # multiresolution
    option.multiresolution = default['multiresolution']

    # remesh
    option.remesh = default['remesh']

    # screw
    option.screw = default['screw']

    # skin
    option.skin = default['skin']

    # solidify
    option.solidify = default['solidify']

    # subdivision surface
    option.subdivisionSurface = default['subdivision surface']

    # triangulate
    option.triangulate = default['triangulate']

    # wireframe
    option.wireframe = default['wireframe']

    # armature
    option.armature = default['armature']

    # cast
    option.cast = default['cast']

    # corrective smooth
    option.correctiveSmooth = default['corrective smooth']

    # curve
    option.curve = default['curve']

    # displace
    option.displace = default['displace']

    # hook
    option.hook = default['hook']

    # laplacian smooth
    option.laplacianSmooth = default['laplacian smooth']

    # laplacian deform
    option.laplacianDeform = default['laplacian deform']

    # lattice
    option.lattice = default['lattice']

    # mesh deform
    option.meshDeform = default['mesh deform']

    # shrinkwrap
    option.shrinkwrap = default['shrinkwrap']

    # simple deform
    option.simpleDeform = default['simple deform']

    # smooth
    option.smooth = default['smooth']

    # warp
    option.warp = default['warp']

    # wave
    option.wave = default['wave']

    # cloth
    option.cloth = default['cloth']

    # collision
    option.collision = default['collision']

    # dynamic paint
    option.dynamicPaint = default['dynamic paint']

    # explode
    option.explode = default['explode']

    # fluid simulation
    option.fluidSimulation = default['fluid simulation']

    # ocean
    option.ocean = default['ocean']

    # particle instance
    option.particleInstance = default['particle instance']

    # particle system
    option.particleSystem = default['particle system']

    # smoke
    option.smoke = default['smoke']

    # soft body
    option.softBody = default['soft body']

    # default
    default = defaults['auto name']['object data names']

    # object data name
    option = context.scene.BatchAutoName_ObjectDataNames

    # prefix
    option.prefix = default['prefix']

    # mesh
    option.mesh = default['mesh']

    # curve
    option.curve = default['curve']

    # surface
    option.surface = default['surface']

    # meta
    option.meta = default['meta']

    # font
    option.font = default['font']

    # armature
    option.armature = default['armature']

    # lattice
    option.lattice = default['lattice']

    # speaker
    option.speaker = default['speaker']

    # camera
    option.camera = default['camera']

    # lamp
    option.lamp = default['lamp']

  # name
  if name:

    # default
    default = defaults['batch name']

    # name option
    option = context.scene.BatchName

    # mode
    option.mode = default['mode']

    # actions
    option.actions = default['actions']

    # action groups
    option.actionGroups = default['action groups']

    # grease pencil
    option.greasePencil = default['grease pencil']

    # pencil layers
    option.pencilLayers = default['pencil layers']

    # objects
    option.objects = default['objects']

    # groups
    option.groups = default['groups']

    # constraints
    option.constraints = default['constraints']

    # modifiers
    option.modifiers = default['modifiers']

    # object data
    option.objectData = default['object data']

    # bone groups
    option.boneGroups = default['bone groups']

    # bones
    option.bones = default['bones']

    # bone constraints
    option.boneConstraints = default['bone constraints']

    # vertex groups
    option.vertexGroups = default['vertex groups']

    # shapekeys
    option.shapekeys = default['shapekeys']

    # uvs
    option.uvs = default['uvs']

    # vertex colors
    option.vertexColors = default['vertex colors']

    # materials
    option.materials = default['materials']

    # textures
    option.textures = default['textures']

    # particle systems
    option.particleSystems = default['particle systems']

    # particle settings
    option.particleSettings = default['particle settings']

    # object type
    option.objectType = default['object type']

    # constraint type
    option.constraintType = default['constraint type']

    # modifier type
    option.modifierType = default['modifier type']

    # sensors
    option.sensors = default['sensors']

    # controllers
    option.controllers = default['controllers']

    # actuators
    option.actuators = default['actuators']

    # line sets
    option.lineSets = default['line sets']

    # linestyles
    option.linestyles = default['linestyles']

    # linestyle modifiers
    option.linestyleModifiers = default['linestyle modifiers']

    # linestyle modifier type
    option.linestyleModifierType = default['linestyle modifier type']

    # scenes
    option.scenes = default['scenes']

    # render layers
    option.renderLayers = default['render layers']

    # worlds
    option.worlds = default['worlds']

    # libraries
    option.libraries = default['libraries']

    # images
    option.images = default['images']

    # masks
    option.masks = default['masks']

    # sequences
    option.sequences = default['sequences']

    # movie clips
    option.movieClips = default['movie clips']

    # sounds
    option.sounds = default['sounds']

    # screens
    option.screens = default['screens']

    # keying sets
    option.keyingSets = default['keying sets']

    # palettes
    option.palettes = default['palettes']

    # brushes
    option.brushes = default['brushes']

    # nodes
    option.nodes = default['nodes']

    # node labels
    option.nodeLabels = default['node labels']

    # frame nodes
    option.frameNodes = default['frame nodes']

    # node groups
    option.nodeGroups = default['node groups']

    # texts
    option.texts = default['texts']

    # ignore action
    option.ignoreAction = default['ignore action']

    # ignore grease pencil
    option.ignoreGreasePencil = default['ignore grease pencil']

    # ignore object
    option.ignoreObject = default['ignore object']

    # ignore group
    option.ignoreGroup = default['ignore group']

    # ignore constraint
    option.ignoreConstraint = default['ignore constraint']

    # ignore modifier
    option.ignoreModifier = default['ignore modifier']

    # ignore bone
    option.ignoreBone = default['ignore bone']

    # ignore bone group
    option.ignoreBoneGroup = default['ignore bone group']

    # ignore bone constraint
    option.ignoreBoneConstraint = default['ignore bone constraint']

    # ignore object data
    option.ignoreObjectData = default['ignore object data']

    # ignore vertex group
    option.ignoreVertexGroup = default['ignore vertex group']

    # ignore shapekey
    option.ignoreShapekey = default['ignore shapekey']

    # ignore uv
    option.ignoreUV = default['ignore uv']

    # ignore vertex color
    option.ignoreVertexColor = default['ignore vertex color']

    # ignore material
    option.ignoreMaterial = default['ignore material']

    # ignore texture
    option.ignoreTexture = default['ignore texture']

    # ignore particle system
    option.ignoreParticleSystem = default['ignore particle system']

    # ignore particle setting
    option.ignoreParticleSetting = default['ignore particle setting']

    # custom name
    option.customName = default['custom name']

    # find
    option.find = default['find']

    # regex
    option.regex = default['regex']

    # replace
    option.replace = default['replace']

    # prefix
    option.prefix = default['prefix']

    # suffix
    option.suffix = default['suffix']

    # suffix last
    option.suffixLast = default['suffix last']

    # trim start
    option.trimStart = default['trim start']

    # trim end
    option.trimEnd = default['trim end']

    # default
    default = defaults['shared']

    # option
    option = context.scene.BatchShared

    # sort
    option.sort = default['sort']

    # padding
    option.pad = default['pad']

    # start
    option.start = default['start']

    # step
    option.step = default['step']

    # separator
    option.separator = default['separator']

    # link
    option.link = default['link']

    # ignore
    option.ignore = default['ignore']

  # copy
  if copy:

    # default
    default = defaults['copy name']

    # copy option
    option = context.scene.BatchCopyName

    # mode
    option.mode = default['mode']

    # source
    option.source = default['source']

    # objects
    option.objects = default['objects']

    # object data
    option.objectData = default['object data']

    # materials
    option.materials = default['materials']

    # textures
    option.textures = default['textures']

    # particle systems
    option.particleSystems = default['particle systems']

    # particle settings
    option.particleSettings = default['particle settings']

    # use active object
    option.useActiveObject = default['use active object']

# transfer
def transfer(context, panel, auto, names, name, copy):
  '''
    Resets the property values for the name panel add-on.
  '''

  # panel settings
  if panel:
    for scene in bpy.data.scenes[:]:
      if scene != context.scene:

        # name panel option
        option = context.scene.NamePanel

        # pin active object
        scene.NamePanel.pinActiveObject = option.pinActiveObject

        # hide search
        scene.NamePanel.hideSearch = option.hideSearch

        # filters
        scene.NamePanel.filters = option.filters

        # options
        scene.NamePanel.options = option.options

        # display names
        scene.NamePanel.displayNames = option.displayNames

        # mode
        scene.NamePanel.mode = option.mode

        # search
        scene.NamePanel.search = option.search

        # regex
        scene.NamePanel.regex = option.regex

        # groups
        scene.NamePanel.groups = option.groups

        # action
        scene.NamePanel.action = option.action

        # grease pencil
        scene.NamePanel.greasePencil = option.greasePencil

        # constraint
        scene.NamePanel.constraints = option.constraints

        # modifiers
        scene.NamePanel.modifiers = option.modifiers

        # bone groups
        scene.NamePanel.boneGroups = option.boneGroups

        # bone constraints
        scene.NamePanel.boneConstraints = option.boneConstraints

        # vertex groups
        scene.NamePanel.vertexGroups = option.vertexGroups

        # shapekeys
        scene.NamePanel.shapekeys = option.shapekeys

        # uvs
        scene.NamePanel.uvs = option.uvs

        # vertex colors
        scene.NamePanel.vertexColors = option.vertexColors

        # materials
        scene.NamePanel.materials = option.materials

        # textures
        scene.NamePanel.textures = option.textures

        # particels systems
        scene.NamePanel.particleSystems = option.particleSystems

        # display bones
        scene.NamePanel.displayBones = option.displayBones

        # bone mode
        scene.NamePanel.boneMode = option.boneMode

  # auto
  if auto:
    for scene in bpy.data.scenes[:]:
      if scene != context.scene:

        # auto name option
        option = context.scene.BatchAutoName

        # type
        scene.BatchAutoName.mode = option.mode

        # objects
        scene.BatchAutoName.objects = option.objects

        # constraints
        scene.BatchAutoName.constraints = option.constraints

        # modifiers
        scene.BatchAutoName.modifiers = option.modifiers

        # objectData
        scene.BatchAutoName.objectData = option.objectData

        # bone Constraints
        scene.BatchAutoName.boneConstraints = option.boneConstraints

        # object type
        scene.BatchAutoName.objectType = option.objectType

        # constraint type
        scene.BatchAutoName.constraintType = option.constraintType

        # modifier type
        scene.BatchAutoName.modifierType = option.modifierType

        # batch shared option
        option = context.scene.BatchShared

        # sort
        scene.BatchShared.sort = option.sort

        # padding
        scene.BatchShared.pad = option.pad

        # start
        scene.BatchShared.start = option.start

        # step
        scene.BatchShared.step = option.step

        # separator
        scene.BatchShared.separator = option.separator

        # link
        scene.BatchShared.link = option.link

        # ignore
        scene.BatchShared.ignore = option.ignore

  # names
  if names:
    for scene in bpy.data.scenes[:]:
      if scene != context.scene:

        # object name
        option = context.scene.BatchAutoName_ObjectNames

        # prefix
        scene.BatchAutoName_ObjectNames.prefix = option.prefix

        # mesh
        scene.BatchAutoName_ObjectNames.mesh = option.mesh

        # curve
        scene.BatchAutoName_ObjectNames.curve = option.curve

        # surface
        scene.BatchAutoName_ObjectNames.surface = option.surface

        # meta
        scene.BatchAutoName_ObjectNames.meta = option.meta

        # font
        scene.BatchAutoName_ObjectNames.font = option.font

        # armature
        scene.BatchAutoName_ObjectNames.armature = option.armature

        # lattice
        scene.BatchAutoName_ObjectNames.lattice = option.lattice

        # empty
        scene.BatchAutoName_ObjectNames.empty = option.empty

        # speaker
        scene.BatchAutoName_ObjectNames.speaker = option.speaker

        # camera
        scene.BatchAutoName_ObjectNames.camera = option.camera

        # lamp
        scene.BatchAutoName_ObjectNames.lamp = option.lamp

        # constraint name
        option = context.scene.BatchAutoName_ConstraintNames

        # prefix
        scene.BatchAutoName_ConstraintNames.prefix = option.prefix

        # camera solver
        scene.BatchAutoName_ConstraintNames.cameraSolver = option.cameraSolver

        # follow track
        scene.BatchAutoName_ConstraintNames.followTrack = option.followTrack

        # object solver
        scene.BatchAutoName_ConstraintNames.objectSolver = option.objectSolver

        # copy location
        scene.BatchAutoName_ConstraintNames.copyLocation = option.copyLocation

        # copy rotation
        scene.BatchAutoName_ConstraintNames.copyRotation = option.copyRotation

        # copy scale
        scene.BatchAutoName_ConstraintNames.copyScale = option.copyScale

        # copy transforms
        scene.BatchAutoName_ConstraintNames.copyTransforms = option.copyTransforms

        # limit distance
        scene.BatchAutoName_ConstraintNames.limitDistance = option.limitDistance

        # limit location
        scene.BatchAutoName_ConstraintNames.limitLocation = option.limitLocation

        # limit rotation
        scene.BatchAutoName_ConstraintNames.limitRotation = option.limitRotation

        # limit scale
        scene.BatchAutoName_ConstraintNames.limitScale = option.limitScale

        # maintain volume
        scene.BatchAutoName_ConstraintNames.maintainVolume = option.maintainVolume

        # transform
        scene.BatchAutoName_ConstraintNames.transform = option.transform

        # clamp to
        scene.BatchAutoName_ConstraintNames.clampTo = option.clampTo

        # damped track
        scene.BatchAutoName_ConstraintNames.dampedTrack = option.dampedTrack

        # inverse kinematics
        scene.BatchAutoName_ConstraintNames.inverseKinematics = option.inverseKinematics

        # locked track
        scene.BatchAutoName_ConstraintNames.lockedTrack = option.lockedTrack

        # spline inverse kinematics
        scene.BatchAutoName_ConstraintNames.splineInverseKinematics = option.splineInverseKinematics

        # stretch to
        scene.BatchAutoName_ConstraintNames.stretchTo = option.stretchTo

        # track to
        scene.BatchAutoName_ConstraintNames.trackTo = option.trackTo

        # action
        scene.BatchAutoName_ConstraintNames.action = option.action

        # child of
        scene.BatchAutoName_ConstraintNames.childOf = option.childOf

        # floor
        scene.BatchAutoName_ConstraintNames.floor = option.floor

        # follow path
        scene.BatchAutoName_ConstraintNames.followPath = option.followPath

        # pivot
        scene.BatchAutoName_ConstraintNames.pivot = option.pivot

        # rigid body joint
        scene.BatchAutoName_ConstraintNames.rigidBodyJoint = option.rigidBodyJoint

        # shrinkwrap
        scene.BatchAutoName_ConstraintNames.shrinkwrap = option.shrinkwrap

        # modifier name
        option = context.scene.BatchAutoName_ModifierNames

        # prefix
        scene.BatchAutoName_ModifierNames.prefix = option.prefix

        # data transfer
        scene.BatchAutoName_ModifierNames.dataTransfer = option.dataTransfer

        # mesh cache
        scene.BatchAutoName_ModifierNames.meshCache = option.meshCache

        # normal edit
        scene.BatchAutoName_ModifierNames.normalEdit = option.normalEdit

        # uv project
        scene.BatchAutoName_ModifierNames.uvProject = option.uvProject

        # uv warp
        scene.BatchAutoName_ModifierNames.uvWarp = option.uvWarp

        # vertex weight edit
        scene.BatchAutoName_ModifierNames.vertexWeightEdit = option.vertexWeightEdit

        # vertex weight mix
        scene.BatchAutoName_ModifierNames.vertexWeightMix = option.vertexWeightMix

        # vertex weight proximity
        scene.BatchAutoName_ModifierNames.vertexWeightProximity = option.vertexWeightProximity

        # array
        scene.BatchAutoName_ModifierNames.array = option.array

        # bevel
        scene.BatchAutoName_ModifierNames.bevel = option.bevel

        # boolean
        scene.BatchAutoName_ModifierNames.boolean = option.boolean

        # build
        scene.BatchAutoName_ModifierNames.build = option.build

        # decimate
        scene.BatchAutoName_ModifierNames.decimate = option.decimate

        # edge split
        scene.BatchAutoName_ModifierNames.edgeSplit = option.edgeSplit

        # mask
        scene.BatchAutoName_ModifierNames.mask = option.mask

        # mirror
        scene.BatchAutoName_ModifierNames.mirror = option.mirror

        # multiresolution
        scene.BatchAutoName_ModifierNames.multiresolution = option.multiresolution

        # remesh
        scene.BatchAutoName_ModifierNames.remesh = option.remesh

        # screw
        scene.BatchAutoName_ModifierNames.screw = option.screw

        # skin
        scene.BatchAutoName_ModifierNames.skin = option.skin

        # solidify
        scene.BatchAutoName_ModifierNames.solidify = option.solidify

        # subdivision surface
        scene.BatchAutoName_ModifierNames.subdivisionSurface = option.subdivisionSurface

        # triangulate
        scene.BatchAutoName_ModifierNames.triangulate = option.triangulate

        # wireframe
        scene.BatchAutoName_ModifierNames.wireframe = option.wireframe

        # armature
        scene.BatchAutoName_ModifierNames.armature = option.armature

        # cast
        scene.BatchAutoName_ModifierNames.cast = option.cast

        # corrective smooth
        scene.BatchAutoName_ModifierNames.correctiveSmooth = option.correctiveSmooth

        # curve
        scene.BatchAutoName_ModifierNames.curve = option.curve

        # displace
        scene.BatchAutoName_ModifierNames.displace = option.displace

        # hook
        scene.BatchAutoName_ModifierNames.hook = option.hook

        # laplacian smooth
        scene.BatchAutoName_ModifierNames.laplacianSmooth = option.laplacianSmooth

        # laplacian deform
        scene.BatchAutoName_ModifierNames.laplacianDeform = option.laplacianDeform

        # lattice
        scene.BatchAutoName_ModifierNames.lattice = option.lattice

        # mesh deform
        scene.BatchAutoName_ModifierNames.meshDeform = option.meshDeform

        # shrinkwrap
        scene.BatchAutoName_ModifierNames.shrinkwrap = option.shrinkwrap

        # simple deform
        scene.BatchAutoName_ModifierNames.simpleDeform = option.simpleDeform

        # smooth
        scene.BatchAutoName_ModifierNames.smooth = option.smooth

        # warp
        scene.BatchAutoName_ModifierNames.warp = option.warp

        # wave
        scene.BatchAutoName_ModifierNames.wave = option.wave

        # cloth
        scene.BatchAutoName_ModifierNames.cloth = option.cloth

        # collision
        scene.BatchAutoName_ModifierNames.collision = option.collision

        # dynamic paint
        scene.BatchAutoName_ModifierNames.dynamicPaint = option.dynamicPaint

        # explode
        scene.BatchAutoName_ModifierNames.explode = option.explode

        # fluid simulation
        scene.BatchAutoName_ModifierNames.fluidSimulation = option.fluidSimulation

        # ocean
        scene.BatchAutoName_ModifierNames.ocean = option.ocean

        # particle instance
        scene.BatchAutoName_ModifierNames.particleInstance = option.particleInstance

        # particle system
        scene.BatchAutoName_ModifierNames.particleSystem = option.particleSystem

        # smoke
        scene.BatchAutoName_ModifierNames.smoke = option.smoke

        # soft body
        scene.BatchAutoName_ModifierNames.softBody = option.softBody

        # object data name
        option = context.scene.BatchAutoName_ObjectDataNames

        # prefix
        scene.BatchAutoName_ObjectDataNames.prefix = option.prefix

        # mesh
        scene.BatchAutoName_ObjectDataNames.mesh = option.mesh

        # curve
        scene.BatchAutoName_ObjectDataNames.curve = option.curve

        # surface
        scene.BatchAutoName_ObjectDataNames.surface = option.surface

        # meta
        scene.BatchAutoName_ObjectDataNames.meta = option.meta

        # font
        scene.BatchAutoName_ObjectDataNames.font = option.font

        # armature
        scene.BatchAutoName_ObjectDataNames.armature = option.armature

        # lattice
        scene.BatchAutoName_ObjectDataNames.lattice = option.lattice

        # speaker
        scene.BatchAutoName_ObjectDataNames.speaker = option.speaker

        # camera
        scene.BatchAutoName_ObjectDataNames.camera = option.camera

        # lamp
        scene.BatchAutoName_ObjectDataNames.lamp = option.lamp

  # name
  if name:
    for scene in bpy.data.scenes:
      if scene != context.scene:

        # name option
        option = context.scene.BatchName

        # batch type
        scene.BatchName.mode = option.mode

        # actions
        scene.BatchName.actions = option.actions

        # action groups
        scene.BatchName.actionGroups = option.actionGroups

        # grease pencil
        scene.BatchName.greasePencil = option.greasePencil

        # pencil layers
        scene.BatchName.pencilLayers = option.pencilLayers

        # objects
        scene.BatchName.objects = option.objects

        # groups
        scene.BatchName.groups = option.groups

        # constraints
        scene.BatchName.constraints = option.constraints

        # modifiers
        scene.BatchName.modifiers = option.modifiers

        # object data
        scene.BatchName.objectData = option.objectData

        # bone groups
        scene.BatchName.boneGroups = option.boneGroups

        # bones
        scene.BatchName.bones = option.bones

        # bone constraints
        scene.BatchName.boneConstraints = option.boneConstraints

        # vertex groups
        scene.BatchName.vertexGroups = option.vertexGroups

        # shapekeys
        scene.BatchName.shapekeys = option.shapekeys

        # uvs
        scene.BatchName.uvs = option.uvs

        # vertex colors
        scene.BatchName.vertexColors = option.vertexColors

        # materials
        scene.BatchName.materials = option.materials

        # textures
        scene.BatchName.textures = option.textures

        # particle systems
        scene.BatchName.particleSystems = option.particleSystems

        # particle settings
        scene.BatchName.particleSettings = option.particleSettings

        # object type
        scene.BatchName.objectType = option.objectType

        # constraint type
        scene.BatchName.constraintType = option.constraintType

        # modifier type
        scene.BatchName.modifierType = option.modifierType

        # sensors
        scene.BatchName.sensors = option.sensors

        # controllers
        scene.BatchName.controllers = option.controllers

        # actuators
        scene.BatchName.actuators = option.actuators

        # line sets
        scene.BatchName.lineSets = option.lineSets

        # linestyles
        scene.BatchName.linestyles = option.linestyles

        # linestyle modifiers
        scene.BatchName.linestyleModifiers = option.linestyleModifiers

        # linestyle modifier type
        scene.BatchName.linestyleModifierType = option.linestyleModifierType

        # scenes
        scene.BatchName.scenes = option.scenes

        # render layers
        scene.BatchName.renderLayers = option.renderLayers

        # worlds
        scene.BatchName.worlds = option.worlds

        # libraries
        scene.BatchName.libraries = option.libraries

        # images
        scene.BatchName.images = option.images

        # masks
        scene.BatchName.masks = option.masks

        # sequences
        scene.BatchName.sequences = option.sequences

        # movie clips
        scene.BatchName.movieClips = option.movieClips

        # sounds
        scene.BatchName.sounds = option.sounds

        # screens
        scene.BatchName.screens = option.screens

        # keying sets
        scene.BatchName.keyingSets = option.keyingSets

        # palettes
        scene.BatchName.palettes = option.palettes

        # brushes
        scene.BatchName.brushes = option.brushes

        # linestyles
        scene.BatchName.linestyles = option.linestyles

        # nodes
        scene.BatchName.nodes = option.nodes

        # node labels
        scene.BatchName.nodeLabels = option.nodeLabels

        # frame nodes
        scene.BatchName.frameNodes = option.frameNodes

        # node groups
        scene.BatchName.nodeGroups = option.nodeGroups

        # texts
        scene.BatchName.texts = option.texts

        # ignore action
        scene.BatchName.ignoreAction = option.ignoreAction

        # ignore grease pencil
        scene.BatchName.ignoreGreasePencil = option.ignoreGreasePencil

        # ignore object
        scene.BatchName.ignoreObject = option.ignoreObject

        # ignore group
        scene.BatchName.ignoreGroup = option.ignoreGroup

        # ignore constraint
        scene.BatchName.ignoreConstraint = option.ignoreConstraint

        # ignore modifier
        scene.BatchName.ignoreModifier = option.ignoreModifier

        # ignore bone
        scene.BatchName.ignoreBone = option.ignoreBone

        # ignore bone group
        scene.BatchName.ignoreBoneGroup = option.ignoreBoneGroup

        # ignore bone constraint
        scene.BatchName.ignoreBoneConstraint = option.ignoreBoneConstraint

        # ignore object data
        scene.BatchName.ignoreObjectData = option.ignoreObjectData

        # ignore vertex group
        scene.BatchName.ignoreVertexGroup = option.ignoreVertexGroup

        # ignore shapekey
        scene.BatchName.ignoreShapekey = option.ignoreShapekey

        # ignore uv
        scene.BatchName.ignoreUV = option.ignoreUV

        # ignore vertex color
        scene.BatchName.ignoreVertexColor = option.ignoreVertexColor

        # ignore material
        scene.BatchName.ignoreMaterial = option.ignoreMaterial

        # ignore texture
        scene.BatchName.ignoreTexture = option.ignoreTexture

        # ignore particle system
        scene.BatchName.ignoreParticleSystem = option.ignoreParticleSystem

        # ignore particle setting
        scene.BatchName.ignoreParticleSetting = option.ignoreParticleSetting

        # custom name
        scene.BatchName.customName = option.customName

        # find
        scene.BatchName.find = option.find

        # regex
        scene.BatchName.regex = option.regex

        # replace
        scene.BatchName.replace = option.replace

        # prefix
        scene.BatchName.prefix = option.prefix

        # suffix
        scene.BatchName.suffix = option.suffix

        # suffix last
        scene.BatchName.suffixLast = option.suffixLast

        # trim start
        scene.BatchName.trimStart = option.trimStart

        # trim end
        scene.BatchName.trimEnd = option.trimEnd

        # batch shared option
        option = context.scene.BatchShared

        # sort
        scene.BatchShared.sort = option.sort

        # padding
        scene.BatchShared.pad = option.pad

        # start
        scene.BatchShared.start = option.start

        # step
        scene.BatchShared.step = option.step

        # separator
        scene.BatchShared.separator = option.separator

        # link
        scene.BatchShared.link = option.link

        # ignore
        scene.BatchShared.ignore = option.ignore

  # copy
  if copy:
    for scene in bpy.data.scenes[:]:
      if scene != context.scene:

        # copy option
        option = context.scene.BatchCopyName

        # type
        scene.BatchCopyName.mode = option.mode

        # source
        scene.BatchCopyName.source = option.source

        # objects
        scene.BatchCopyName.objects = option.objects

        # object datas
        scene.BatchCopyName.objectData = option.objectData

        # materials
        scene.BatchCopyName.materials = option.materials

        # textures
        scene.BatchCopyName.textures = option.textures

        # particle systems
        scene.BatchCopyName.particleSystems = option.particleSystems

        # particle settings
        scene.BatchCopyName.particleSettings = option.particleSettings

        # use active object
        scene.BatchCopyName.useActiveObject = option.useActiveObject
