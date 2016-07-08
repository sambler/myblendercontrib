
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

# batch
class batch:
  '''
    Contains Classes;
      menu

    Contains Lists;
      actions
      action groups
      grease pencils
      pencil layers
      objects
      groups
      constraints
      modifiers
      cameras
      meshes
      curves
      lamps
      lattices
      metaballs
      speakers
      armatures
      bone groups
      bones
      vertex groups
      shapekeys
      uvs
      vertex colors
      materials
      textures
      particle systems
      particle settings
      linestyles
      sensors
      controllers
      actuators
      scenes
      render layers
      worlds
      libraries
      images
      masks
      sequences
      movie clips
      sounds
      screens
      keying sets
      palettes
      brushes
      nodes
      node labels
      node groups
      texts
  '''

  # classes

  # menu
  class menu:
    '''
      Contains Lists;
        objects
        modifiers
        constraints
        linestyle modifiers
    '''
    # object
    objects = [
      ('ALL', 'All Objects', '', 'OBJECT_DATA', 0),
      ('MESH', 'Mesh', '', 'OUTLINER_OB_MESH', 1),
      ('CURVE', 'Curve', '', 'OUTLINER_OB_CURVE', 2),
      ('SURFACE', 'Surface', '', 'OUTLINER_OB_SURFACE', 3),
      ('META', 'Meta', '', 'OUTLINER_OB_META', 4),
      ('FONT', 'Text', '', 'OUTLINER_OB_FONT', 5),
      ('ARMATURE', 'Armature', '', 'OUTLINER_OB_ARMATURE', 6),
      ('LATTICE', 'Lattice', '', 'OUTLINER_OB_LATTICE', 7),
      ('EMPTY', 'Empty', '', 'OUTLINER_OB_EMPTY', 8),
      ('SPEAKER', 'Speaker', '', 'OUTLINER_OB_SPEAKER', 9),
      ('CAMERA', 'Camera', '', 'OUTLINER_OB_CAMERA', 10),
      ('LAMP', 'Lamp', '', 'OUTLINER_OB_LAMP', 11)
    ]

    # constraint
    constraints = [
      ('ALL', 'All Constraints', '', 'CONSTRAINT', 0),

      # motion tracking
      ('CAMERA_SOLVER', 'Camera Solver', '', 'CONSTRAINT_DATA', 1),
      ('FOLLOW_TRACK', 'Follow Track', '', 'CONSTRAINT_DATA', 2),
      ('OBJECT_SOLVER', 'Object Solver', '', 'CONSTRAINT_DATA', 3),

      # transform
      ('COPY_LOCATION', 'Copy Location', '', 'CONSTRAINT_DATA', 4),
      ('COPY_ROTATION', 'Copy Rotation', '', 'CONSTRAINT_DATA', 5),
      ('COPY_SCALE', 'Copy Scale', '', 'CONSTRAINT_DATA', 6),
      ('COPY_TRANSFORMS', 'Copy Transforms', '', 'CONSTRAINT_DATA', 7),
      ('LIMIT_DISTANCE', 'Limit Distance', '', 'CONSTRAINT_DATA', 8),
      ('LIMIT_LOCATION', 'Limit Location', '', 'CONSTRAINT_DATA', 9),
      ('LIMIT_ROTATION', 'Limit Rotation', '', 'CONSTRAINT_DATA', 10),
      ('LIMIT_SCALE', 'Limit Scale', '', 'CONSTRAINT_DATA', 11),
      ('MAINTAIN_VOLUME', 'Maintain Volume', '', 'CONSTRAINT_DATA', 12),
      ('TRANSFORM', 'Transformation', '', 'CONSTRAINT_DATA', 13),

      # tracking
      ('CLAMP_TO', 'Clamp To', '', 'CONSTRAINT_DATA', 14),
      ('DAMPED_TRACK', 'Damped Track', '', 'CONSTRAINT_DATA', 15),
      ('IK', 'Inverse Kinematics', '', 'CONSTRAINT_DATA', 16),
      ('LOCKED_TRACK', 'Locked Track', '', 'CONSTRAINT_DATA', 17),
      ('SPLINE_IK', 'Spline IK', '', 'CONSTRAINT_DATA', 18),
      ('STRETCH_TO', 'Stretch To', '', 'CONSTRAINT_DATA', 19),
      ('TRACK_TO', 'Track To', '', 'CONSTRAINT_DATA', 20),

      # relationship
      ('ACTION', 'Action', '', 'CONSTRAINT_DATA', 21),
      ('CHILD_OF', 'Child Of', '', 'CONSTRAINT_DATA', 22),
      ('FLOOR', 'Floor', '', 'CONSTRAINT_DATA', 23),
      ('FOLLOW_PATH', 'Follow Path', '', 'CONSTRAINT_DATA', 24),
      ('PIVOT', 'Pivot', '', 'CONSTRAINT_DATA', 25),
      ('RIGID_BODY_JOINT', 'Rigid Body Joint', '', 'CONSTRAINT_DATA', 26),
      ('SHRINKWRAP', 'Shrinkwrap', '', 'CONSTRAINT_DATA', 27)
    ]

    # modifier
    modifiers = [
      ('ALL', 'All Modifiers', '', 'MODIFIER', 0),

      # modify
      ('DATA_TRANSFER', 'Data Transfer', '', 'MOD_DATA_TRANSFER', 1),
      ('MESH_CACHE', 'Mesh Cache', '', 'MOD_MESHDEFORM', 2),
      ('NORMAL_EDIT', 'Normal Edit', '', 'MOD_NORMALEDIT', 3),
      ('UV_PROJECT', 'UV Project', '', 'MOD_UVPROJECT', 4),
      ('UV_WARP', 'UV Warp', '', 'MOD_UVPROJECT', 5),
      ('VERTEX_WEIGHT_EDIT', 'Vertex Weight Edit', '', 'MOD_VERTEX_WEIGHT', 6),
      ('VERTEX_WEIGHT_MIX', 'Vertex Weight Mix', '', 'MOD_VERTEX_WEIGHT', 7),
      ('VERTEX_WEIGHT_PROXIMITY', 'Vertex Weight Proximity', '', 'MOD_VERTEX_WEIGHT', 8),

      # generate
      ('ARRAY', 'Array', '', 'MOD_ARRAY', 9),
      ('BEVEL', 'Bevel', '', 'MOD_BEVEL', 10),
      ('BOOLEAN', 'Boolean', '', 'MOD_BOOLEAN', 11),
      ('BUILD', 'Build', '', 'MOD_BUILD', 12),
      ('DECIMATE', 'Decimate', '', 'MOD_DECIM', 13),
      ('EDGE_SPLIT', 'Edge Split', '', 'MOD_EDGESPLIT', 14),
      ('MASK', 'Mask', '', 'MOD_MASK', 15),
      ('MIRROR', 'Mirror', '', 'MOD_MIRROR', 16),
      ('MULTIRES', 'Multiresolution', '', 'MOD_MULTIRES', 17),
      ('REMESH', 'Remesh', '', 'MOD_REMESH', 18),
      ('SCREW', 'Screw', '', 'MOD_SCREW', 19),
      ('SKIN', 'Skin', '', 'MOD_SKIN', 20),
      ('SOLIDIFY', 'Solidify', '', 'MOD_SOLIDIFY', 21),
      ('SUBSURF', 'Subdivision Surface', '', 'MOD_SUBSURF', 22),
      ('TRIANGULATE', 'Triangulate', '', 'MOD_TRIANGULATE', 23),
      ('WIREFRAME', 'Wireframe', '', 'MOD_WIREFRAME', 24),

      # deform
      ('ARMATURE', 'Armature', '', 'MOD_ARMATURE', 25),
      ('CAST', 'Cast', '', 'MOD_CAST', 26),
      ('CORRECTIVE_SMOOTH', 'Corrective Smooth', '', 'MOD_SMOOTH', 27),
      ('CURVE', 'Curve', '', 'MOD_CURVE', 28),
      ('DISPLACE', 'Displace', '', 'MOD_DISPLACE', 29),
      ('HOOK', 'Hook', '', 'HOOK', 30),
      ('LAPLACIANSMOOTH', 'Laplacian Smooth', '', 'MOD_SMOOTH', 31),
      ('LAPLACIANDEFORM', 'Laplacian Deform', '', 'MOD_MESHDEFORM', 32),
      ('LATTICE', 'Lattice', '', 'MOD_LATTICE', 33),
      ('MESH_DEFORM', 'Mesh Deform', '', 'MOD_MESHDEFORM', 34),
      ('SHRINKWRAP', 'Shrinkwrap', '', 'MOD_SHRINKWRAP', 35),
      ('SIMPLE_DEFORM', 'Simple Deform', '', 'MOD_SIMPLEDEFORM', 36),
      ('SMOOTH', 'Smooth', '', 'MOD_SMOOTH', 37),
      ('WARP', 'Warp', '', 'MOD_WARP', 38),
      ('WAVE', 'Wave', '', 'MOD_WAVE', 39),

      # simulate
      ('CLOTH', 'Cloth', '', 'MOD_CLOTH', 40),
      ('COLLISION', 'Collision', '', 'MOD_PHYSICS', 41),
      ('DYNAMIC_PAINT', 'Dynamic Paint', '', 'MOD_DYNAMICPAINT', 42),
      ('EXPLODE', 'Explode', '', 'MOD_EXPLODE', 43),
      ('FLUID_SIMULATION', 'Fluid Simulation', '', 'MOD_FLUIDSIM', 44),
      ('OCEAN', 'Ocean', '', 'MOD_OCEAN', 45),
      ('PARTICLE_INSTANCE', 'Particle Instance', '', 'MOD_PARTICLES', 46),
      ('PARTICLE_SYSTEM', 'Particle System', '', 'MOD_PARTICLES', 47),
      ('SMOKE', 'Smoke', '', 'MOD_SMOKE', 48),
      ('SOFT_BODY', 'Soft Body', '', 'MOD_SOFT', 49)
    ]

    linestyleModifiers = [
      ('ALL', 'All Modifiers', '', 'MODIFIER', 0),
      ('ALONG_STROKE', 'Along Stroke', '', 'MODIFIER', 1),
      ('CREASE_ANGLE', 'Crease Angle', '', 'MODIFIER', 2),
      ('CURVATURE_3D', 'Curvature 3D', '', 'MODIFIER', 3),
      ('DISTANCE_FROM_CAMERA', 'Distance from Camera', '', 'MODIFIER', 4),
      ('DISTANCE_FROM_OBJECT', 'Distance from Object', '', 'MODIFIER', 5),
      ('MATERIAL', 'Material', '', 'MODIFIER', 6),
      ('NOISE', 'Noise', '', 'MODIFIER', 7),
      ('TANGENT', 'Tangent', '', 'MODIFIER', 8),
      ('CALLIGRAPHY', 'Calligraphy', '', 'MODIFIER', 9),
      ('2D_OFFSET', '2D Offset', '', 'MODIFIER', 10),
      ('2D_TRANSFORM', '2D Transform', '', 'MODIFIER', 11),
      ('BACKBONE_STRETCHER', 'Backbone Stretcher', '', 'MODIFIER', 12),
      ('BEZIER_CURVE', 'Bezier Curve', '', 'MODIFIER', 13),
      ('BLUEPRINT', 'Blue Print', '', 'MODIFIER', 14),
      ('GUIDING_LINES', 'Guiding Lines', '', 'MODIFIER', 15),
      ('PERLIN_NOISE_1D', 'Perlin Noise 1D', '', 'MODIFIER', 16),
      ('PERLIN_NOISE_2D', 'Perlin Noise 2D', '', 'MODIFIER', 17),
      ('POLYGONIZATION', 'Polygonization', '', 'MODIFIER', 18),
      ('SAMPLING', 'Sampling', '', 'MODIFIER', 19),
      ('SIMPLIFICATION', 'Simplification', '', 'MODIFIER', 20),
      ('SINUS_DISPLACEMENT', 'Sinus Displacement', '', 'MODIFIER', 21),
      ('SPATIAL_NOISE', 'Spatial Noise', '', 'MODIFIER', 22),
      ('TIP_REMOVER', 'Tip Remover', '', 'MODIFIER', 23)
    ]

  # defaults (never used directly)
  defaults = {
    'name panel': {
      'pin active object': True,
      'hide search': True,
      'filters': False,
      'options': False,
      'display names': False,
      'search': '',
      'regex': False,
      'mode': 'SELECTED',
      'groups': False,
      'action': False,
      'grease pencil': False,
      'constraints': False,
      'modifiers': False,
      'bone groups': False,
      'bone constraints': False,
      'vertex groups': False,
      'shapekeys': False,
      'uvs': False,
      'vertex color': False,
      'materials': False,
      'textures': False,
      'particle systems': False,
      'bone mode': 'SELECTED',
      'display bones': False,
    },

    'shared': {
      'sort': True,
      'link': False,
      'pad': 0,
      'start': 1,
      'step': 1,
      'separator': '.',
      'ignore': False
    },

    'auto name': {
      'mode': 'SELECTED',
      'objects': False,
      'constraints': False,
      'modifiers': False,
      'object data': False,
      'bone constraints': False,
      'object type': 'ALL',
      'constraint type': 'ALL',
      'modifier type': 'ALL',

      'object names': {
        'prefix': False,
        'mesh': 'Mesh',
        'curve': 'Curve',
        'surface': 'Surface',
        'meta': 'Meta',
        'font': 'Text',
        'armature': 'Armature',
        'lattice': 'Lattice',
        'empty': 'Empty',
        'speaker': 'Speaker',
        'camera': 'Camera',
        'lamp': 'Lamp',
      },

      'constraint names': {
        'prefix': False,
        'camera solver': 'Camera Solver',
        'follow track': 'Follow Track',
        'object solver': 'Object Solver',
        'copy location': 'Copy Location',
        'copy rotation': 'Copy Rotation',
        'copy scale': 'Copy Scale',
        'copy transforms': 'Copy Transforms',
        'limit distance': 'Limit Distance',
        'limit location': 'Limit Location',
        'limit rotation': 'Limit Rotation',
        'limit scale': 'Limit Scale',
        'maintain volume': 'Maintain Volume',
        'transform': 'Transform',
        'clamp to': 'Clamp To',
        'damped track': 'Damped Track',
        'inverse kinematics': 'Inverse Kinematics',
        'locked track': 'Locked Track',
        'spline inverse kinematics': 'Spline Inverse Kinematics',
        'stretch to': 'Stretch To',
        'track to': 'Track To',
        'action': 'Action',
        'child of': 'Child Of',
        'floor': 'Floor',
        'follow path': 'Follow Path',
        'pivot': 'Pivot',
        'rigid body joint': 'Rigid Body Joint',
        'shrinkwrap': 'Shrinkwrap',
      },

      'modifier names': {
        'prefix': False,
        'data transfer': 'Data Transfer',
        'mesh cache': 'Mesh Cache',
        'normal edit': 'Normal Edit',
        'uv project': 'UV Project',
        'uv warp': 'UV Warp',
        'vertex weight edit': 'Vertex Weight Edit',
        'vertex weight mix': 'Vertex Weight Mix',
        'vertex weight proximity': 'Vertex Weight Proximity',
        'array': 'Array',
        'bevel': 'Bevel',
        'boolean': 'Boolean',
        'build': 'Build',
        'decimate': 'Decimate',
        'edge split': 'Edge Split',
        'mask': 'Mask',
        'mirror': 'Mirror',
        'multiresolution': 'Multiresolution',
        'remesh': 'Remesh',
        'screw': 'Screw',
        'skin': 'Skin',
        'solidify': 'Solidify',
        'subdivision surface': 'Subdivision Surface',
        'triangulate': 'Triangulate',
        'wireframe': 'Wireframe',
        'armature': 'Armature',
        'cast': 'Cast',
        'corrective smooth': 'Corrective Smooth',
        'curve': 'Curve',
        'displace': 'Displace',
        'hook': 'Hook',
        'laplacian smooth': 'Laplacian Smooth',
        'laplacian deform': 'Laplacian Deform',
        'lattice': 'Lattice',
        'mesh deform': 'Mesh Deform',
        'shrinkwrap': 'Shrinkwrap',
        'simple deform': 'Simple Deform',
        'smooth': 'Smooth',
        'warp': 'Warp',
        'wave': 'Wave',
        'cloth': 'Cloth',
        'collision': 'Collision',
        'dynamic paint': 'Dynamic Paint',
        'explode': 'Explode',
        'fluid simulation': 'Fluid Simulation',
        'ocean': 'Ocean',
        'particle instance': 'Particle Instance',
        'particle system': 'Particle System',
        'smoke': 'Smoke',
        'soft body': 'Soft Body',
      },

      'object data names': {
        'prefix': False,
        'mesh': 'Mesh',
        'curve': 'Curve',
        'surface': 'Surface',
        'meta': 'Meta',
        'font': 'Text',
        'armature': 'Armature',
        'lattice': 'Lattice',
        'empty': 'Empty',
        'speaker': 'Speaker',
        'camera': 'Camera',
        'lamp': 'Lamp',
      },
    },

    'batch name': {
      'mode': 'SELECTED',
      'actions': False,
      'action groups': False,
      'grease pencil': False,
      'pencil layers': False,
      'objects': False,
      'groups': False,
      'constraints': False,
      'modifiers': False,
      'object data': False,
      'bone groups': False,
      'bones': False,
      'bone constraints': False,
      'vertex groups': False,
      'shapekeys': False,
      'uvs': False,
      'vertex colors': False,
      'materials': False,
      'textures': False,
      'particle systems': False,
      'particle settings': False,
      'object type': 'ALL',
      'constraint type': 'ALL',
      'modifier type': 'ALL',
      'sensors': False,
      'controllers': False,
      'actuators': False,
      'line sets': False,
      'linestyles': False,
      'linestyle modifiers': False,
      'linestyle modifier type': 'ALL',
      'scenes': False,
      'render layers': False,
      'worlds': False,
      'libraries': False,
      'images': False,
      'masks': False,
      'sequences': False,
      'movie clips': False,
      'sounds': False,
      'screens': False,
      'keying sets': False,
      'palettes': False,
      'brushes': False,
      'nodes': False,
      'node labels': False,
      'frame nodes': False,
      'node groups': False,
      'texts': False,
      'ignore action': False,
      'ignore grease pencil': False,
      'ignore object': False,
      'ignore group': False,
      'ignore constraint': False,
      'ignore modifier': False,
      'ignore bone': False,
      'ignore bone group': False,
      'ignore bone constraint': False,
      'ignore object data': False,
      'ignore vertex group': False,
      'ignore shapekey': False,
      'ignore uv': False,
      'ignore vertex color': False,
      'ignore material': False,
      'ignore texture': False,
      'ignore particle system': False,
      'ignore particle setting': False,
      'custom name': '',
      'find': '',
      'regex': False,
      'replace': '',
      'prefix': '',
      'suffix': '',
      'suffix last': False,
      'trim start': 0,
      'trim end': 0,
    },

    'copy name': {
      'mode': 'SELECTED',
      'source': 'OBJECT',
      'objects': False,
      'object data': False,
      'materials': False,
      'textures': False,
      'particle systems': False,
      'particle settings': False,
      'use active object': False,
    },
  }

  # lists

  # structure
  # list = [
  #  [sort name, modified name, original name, [count, datablock, [], source datablock]
  # ]

  # actions
  actions = []

  # action groups
  actionsGroups = []

  # grease pencils
  greasePencils = []

  # pencil layers
  pencilLayers = []

  # objects
  objects = []

  # groups
  groups = []

  # constraints
  constraints = []

  # modifiers
  modifiers = []

  # cameras
  cameras = []

  # meshes
  meshes = []

  # curves
  curves = []

  # lamps
  lamps = []

  # lattices
  lattices = []

  # metaballs
  metaballs = []

  # speakers
  speakers = []

  # armatures
  armatures = []

  # bone groups
  boneGroups = []

  # bones
  bones = []

  # vertex groups
  vertexGroups = []

  # shapekeys
  shapekeys = []

  # uvs
  uvs = []

  # vertex colors
  vertexColors = []

  # materials
  materials = []

  # textures
  textures = []

  # particle systems
  particleSystems = []

  # particle settings
  particleSettings = []

  # linestyles
  linestyles = []

  # sensors
  sensors = []

  # controllers
  controllers = []

  # actuators
  actuators = []

  # scenes
  scenes = []

  # render layers
  renderLayers = []

  # worlds
  worlds = []

  # libraries
  libraries = []

  # images
  images = []

  # masks
  masks = []

  # sequences
  sequences = []

  # movie clips
  movieClips = []

  # sounds
  sounds = []

  # screens
  screens = []

  # keying sets
  keyingSets = []

  # palettes
  palettes = []

  # brushes
  brushes = []

  # nodes
  nodes = []

  # node labels
  nodeLabels = []

  # node groups
  nodeGroups = []

  # texts
  texts = []
