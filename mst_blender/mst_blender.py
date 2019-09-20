from . import mstree
from . import diameter
import bpy
import numpy as np
import mathutils
import math
import random

DENDRITE_GROUP_NAME = "DENDRITE_TREES"

def buildTreeMesh(root_node, skin = False):
    nodes = mstree.tree_to_list(root_node)

    vertices = [node.pos for node in nodes]

    edges = []
    for i, node in enumerate(nodes):
        if node.parent is not None:
            edges.append([i, nodes.index(node.parent)])

    mesh = bpy.data.meshes.new("Tree")
    mesh.from_pydata(vertices, edges, [])
    mesh.update()

    obj = bpy.data.objects.new("Tree", mesh)
    bpy.context.scene.collection.objects.link(obj)

    if skin:
        obj.modifiers.new("DendriteThickness", 'SKIN')
        obj.modifiers["DendriteThickness"].use_smooth_shade = True
        for i, node in enumerate(nodes):
            obj.data.skin_vertices[0].data[i].radius= (node.thickness * 0.005, node.thickness * 0.005)

    return obj

def buildTreeCurve(root_node):
    curve = bpy.data.curves.new('Tree', 'CURVE')
    curve.dimensions = '3D'

    nodes = mstree.tree_to_list(root_node)

    curve.splines.new('BEZIER')
    for i, node in enumerate(nodes):
        spline = curve.splines[-1]
        spline.bezier_points.add(count=1)

        point = spline.bezier_points[-1]
        point.co = mathutils.Vector(node.pos)
        point.handle_left_type = 'VECTOR'
        point.handle_right_type = 'VECTOR'
        
        if hasattr(node, 'thickness'):
            point.radius = node.thickness
        
        if not node.children and len(nodes) > i + 1:
            node = nodes[i+1].parent
            curve.splines.new('BEZIER')
            spline = curve.splines[-1]
            point = spline.bezier_points[0]
            point.co = mathutils.Vector(node.pos)
            point.handle_left_type = 'VECTOR'
            point.handle_right_type = 'VECTOR'
            if hasattr(node, 'thickness'):
                point.radius = node.thickness

    curve_object = bpy.data.objects.new("Tree", curve)
    bpy.context.scene.collection.objects.link(curve_object)

    curve.fill_mode = 'FULL'
    return curve_object

def spinPoints(points, axis, axis_direction, radians = math.pi, seed = None):
    rng = random.Random()
    rng.seed(seed)

    dir_n = axis_direction / np.linalg.norm(axis_direction)
    a = axis[0]; b = axis[1]; c = axis[2]
    u = dir_n[0]; v = dir_n[1]; w = dir_n[2]

    new_points = []

    # Formula: http://inside.mines.edu/fs_home/gmurray/ArbitraryAxisRotation/
    for point in points:
        rotation = rng.random() * radians
        x = point[0]; y = point[1]; z = point[2]
        v1 = (a*(v**2 + w**2) - u*(b*v + c*w - u*x - v*y - w*z)) * (1 - np.cos(rotation)) + x*np.cos(rotation) + (-c*v + b*w - w*y + v*z) * np.sin(rotation)
        v2 = (b*(u**2 + w**2) - v*(a*u + c*w - u*x - v*y - w*z)) * (1 - np.cos(rotation)) + y*np.cos(rotation) + ( c*u - a*w + w*x - u*z) * np.sin(rotation)
        v3 = (c*(u**2 + v**2) - w*(a*u + b*v - u*x - v*y - w*z)) * (1 - np.cos(rotation)) + z*np.cos(rotation) + (-b*u + a*v - v*x + u*y) * np.sin(rotation)
        new_points.append((v1,v2,v3))

    return np.array(new_points)

def createTreeObject(options = None):
    if options is None:
        options = bpy.context.scene.mst_options

    # Determine from where to take points
    if options.point_data_type == 'PARTICLE':
        source_object = bpy.data.objects[options.source_object].evaluated_get(bpy.context.evaluated_depsgraph_get())  # Blender 2.80 requires this for accessing particles
        particle_system = source_object.particle_systems[options.source_particle_system]
        seed = particle_system.seed
        particle_points = [(x.location[0], x.location[1], x.location[2]) for x in particle_system.particles]
    elif options.point_data_type == 'GROUP':
        source_group = bpy.data.groups[options.source_group]
        seed = 0
        particle_points = [(x.location[0], x.location[1], x.location[2]) for x in source_group.objects]
    else:
        seed = 0

    # Get starting point from object, cursor or first particle and create numpy array from it
    if options.root_data_type == 'OBJECT':
        root_point = bpy.data.objects[options.root_data_object].location
        root_list = [(root_point[0], root_point[1], root_point[2])]
        root_list.extend(particle_points)
        points = np.array(root_list) - root_point
    elif options.root_data_type == 'CURSOR':
        root_point = bpy.context.scene.cursor.location
        root_list = [(root_point[0], root_point[1], root_point[2])]
        root_list.extend(particle_points)
        points = np.array(root_list) - root_point
    else:
        root_point = particle_points[0]
        points = np.array(particle_points) - root_point

    # Spin points randomly on an axis if enabled
    if options.random_spin:
        if options.spin_axis == 'Y':
            up_axis = mathutils.Vector((0.0, 1.0, 0.0))
        elif options.spin_axis == 'Z':
            up_axis = mathutils.Vector((0.0, 0.0, 1.0))
        else:
            up_axis = mathutils.Vector((1.0, 0.0, 0.0))

        axis = bpy.data.objects[options.spin_object].rotation_euler.to_matrix() * up_axis
        location = bpy.data.objects[options.spin_object].location - root_point

        points = spinPoints(points, np.array(location), np.array(axis), options.spin_degrees, seed)

    # Create the tree structure
    root_node = mstree.mstree(points, balancing_factor = options.balancing_factor)

    if options.add_thickness:
        # Calculate the diameter of the tree
        diameter.add_quad_diameter(root_node, scale = options.thickness_scale, offset = options.thickness_offset, path_scale = options.path_scale)

    # Build the blender object from the tree data
    if options.build_type == 'MESH':
        obj = buildTreeMesh(root_node, options.add_thickness)
    elif options.build_type == 'CURVE':
        obj = buildTreeCurve(root_node)
        if options.add_thickness:
            obj.data.bevel_depth = 0.005

    obj.location = root_point

    return obj

def createMultipleTrees(points, normals, options = None):
    if normals is not None:
        if len(points) != len(normals):
            raise ValueError("Points and normals need to be the same length")

    if options is None:
        options = bpy.context.scene.mst_options

    ob = bpy.data.objects[options.source_object]

    particle_system = ob.particle_systems[options.source_particle_system]
    intial_seed = particle_system.seed

    objects = []

    for i, point in enumerate(points):
        if normals is not None:
            normal = normals[i]
        else:
            normal = (0,0,1)

        particle_system.seed = intial_seed + i

        # Update the view layer so the particle system gets updated
        bpy.context.view_layer.update()

        obj = createTreeObject(options)

        obj.location = mathutils.Vector(point)

        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = mathutils.Vector(normal).to_track_quat('Z', 'Y')

        objects.append(obj)

    particle_system.seed = intial_seed

    return objects


# --- Operators ---

class OBJECT_OT_mstadd(bpy.types.Operator):
    bl_idname = "object.add_minimum_spanning_tree"
    bl_label = "Add Minimum Spanning Tree"

    balancing_factor : bpy.props.FloatProperty(name = "Balancing factor", default = 0.5, min = 0.0, max = 1.0)

    point_data_type : bpy.props.EnumProperty(
        name = "Point data type",
        items = (
            ('PARTICLE', 'Particle system', 'Use the particles of a particle system as points'),
            ('GROUP', 'Group', 'Use locations of objects in group as points')
        ),
        default = 'PARTICLE'
    )

    source_object : bpy.props.StringProperty(name = "Object")
    source_particle_system : bpy.props.StringProperty(name = "Particle System")

    source_group : bpy.props.StringProperty(name = "Object group")

    root_data_type : bpy.props.EnumProperty(
        name = "Root data type",
        items = (
            ('PARTICLE', 'First Particle/Object', 'Use the first particle in particle system as root point'),
            ('CURSOR', '3D cursor', 'Use 3D cursor location as root point'),
            ('OBJECT', 'Object center', 'Use an object center as root point')
        ),
        default = 'CURSOR'
    )

    root_data_object : bpy.props.StringProperty(name = "Root object")

    build_type : bpy.props.EnumProperty(
        name = "Build type",
        items = (
            ('MESH', 'Mesh', 'Build the tree out of vertices'),
            ('CURVE', 'Curve', 'Build the tree out of curves')
        ),
        default = 'MESH'
    )

    random_spin : bpy.props.BoolProperty(name = "Random spin", default = False)
    spin_object : bpy.props.StringProperty(name = "Axis object")
    spin_degrees : bpy.props.FloatProperty(name = "Spin degrees", subtype = 'ANGLE', min = 0.0, max = 2*math.pi, default = math.pi)
    spin_axis : bpy.props.EnumProperty(name = "Spin axis", items = (('X', 'X', 'Spin along the X-axis of the object'), ('Y', 'Y', 'Spin along the Y-axis of the object'), ('Z', 'Z', 'Spin along the Z-axis of the object')), default = 'Y')

    add_thickness : bpy.props.BoolProperty(name = "Add thickness")
    thickness_scale : bpy.props.FloatProperty(name = "Scale", min = 0.0, default = 1.0)
    thickness_offset : bpy.props.FloatProperty(name = "Offset", min = 0.0, default = 0.5)
    path_scale : bpy.props.FloatProperty(name = "Path scale", min = 0.0, default = 100.0)

    def invoke(self, context, event):
        ao = context.active_object
        if ao is not None:
            self.source_object = ao.name
            self.root_data_object = ao.name
            if len(ao.particle_systems):
                self.source_particle_system = context.active_object.particle_systems[0].name
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        op = self

        layout = self.layout

        row = layout.row()
        row.prop(op, "balancing_factor")
        
        row = layout.row()
        row.prop(op, "point_data_type")
        row = layout.row()
        
        if op.point_data_type == 'PARTICLE':
            row.prop_search(op, "source_object", bpy.data, 'objects')
            if op.source_object in bpy.data.objects:
                row = layout.row()
                row.prop_search(op, "source_particle_system", bpy.data.objects[op.source_object], 'particle_systems')
        elif op.point_data_type == 'GROUP':
            row.prop_search(op, "source_group", bpy.data, 'groups')

        row = layout.row()
        row.prop(op, "root_data_type")

        if op.root_data_type == 'OBJECT':
            row = layout.row()
            row.prop_search(op, "root_data_object", bpy.data, 'objects')

        row = layout.row()
        row.prop(op, "build_type")

        row = layout.row()
        row.prop(op, "random_spin")

        if op.random_spin:
            row = layout.row()
            row.prop_search(op, "spin_object", bpy.data, 'objects')

            row = layout.row()
            row.prop(op, "spin_axis")

            row = layout.row()
            row.prop(op, "spin_degrees")

        row = layout.row()
        row.prop(op, "add_thickness")

        if op.add_thickness:
            row = layout.row()
            row.prop(op, "thickness_scale")

            row = layout.row()
            row.prop(op, "thickness_offset")

            row = layout.row()
            row.prop(op, "path_scale")

    def execute(self, context):
        createTreeObject(self)
        return {'FINISHED'}

class OBJECT_OT_dendriteadd(OBJECT_OT_mstadd):
    bl_idname = "object.add_mst_dendrites"
    bl_label = "Create Dendrites"

    balancing_factor : bpy.props.FloatProperty(name = "Balancing factor", default = 0.5, min = 0.0, max = 1.0)

    point_data_type : bpy.props.EnumProperty(
        name = "Point data type",
        items = (
            ('PARTICLE', 'Particle system', 'Use the particles of a particle system as points'),
            ('GROUP', 'Group', 'Use locations of objects in group as points')
        ),
        default = 'PARTICLE'
    )

    source_object : bpy.props.StringProperty(name = "Object")
    source_particle_system : bpy.props.StringProperty(name = "Particle System")

    source_group : bpy.props.StringProperty(name = "Object group")

    root_data_type : bpy.props.EnumProperty(
        name = "Root data type",
        items = (
            ('PARTICLE', 'First Particle/Object', 'Use the first particle in particle system as root point'),
            ('CURSOR', '3D cursor', 'Use 3D cursor location as root point'),
            ('OBJECT', 'Object center', 'Use an object center as root point')
        ),
        default = 'CURSOR'
    )

    root_data_object : bpy.props.StringProperty(name = "Root object")

    build_type : bpy.props.EnumProperty(
        name = "Build type",
        items = (
            ('MESH', 'Mesh', 'Build the tree out of vertices'),
            ('CURVE', 'Curve', 'Build the tree out of curves')
        ),
        default = 'MESH'
    )

    random_spin : bpy.props.BoolProperty(name = "Random spin", default = False)
    spin_object : bpy.props.StringProperty(name = "Axis object")
    spin_degrees : bpy.props.FloatProperty(name = "Spin degrees", subtype = 'ANGLE', min = 0.0, max = 2*math.pi, default = math.pi)
    spin_axis : bpy.props.EnumProperty(name = "Spin axis", items = (('X', 'X', 'Spin along the X-axis of the object'), ('Y', 'Y', 'Spin along the Y-axis of the object'), ('Z', 'Z', 'Spin along the Z-axis of the object')), default = 'Y')

    add_thickness : bpy.props.BoolProperty(name = "Add thickness")
    thickness_scale : bpy.props.FloatProperty(name = "Scale", min = 0.0, default = 1.0)
    thickness_offset : bpy.props.FloatProperty(name = "Offset", min = 0.0, default = 0.5)
    path_scale : bpy.props.FloatProperty(name = "Path scale", min = 0.0, default = 100.0)

    target_object: bpy.props.StringProperty(name = "Target object")
    target_particle_system: bpy.props.StringProperty(name = "Target particle system")

    def draw(self, context):
        op = self

        super().draw(context)

        layout = self.layout

        row = layout.row()
        row.prop_search(op, "target_object", bpy.data, "objects")

        if op.target_object in bpy.data.objects:
            row = layout.row()
            row.prop_search(op, "target_particle_system", bpy.data.objects[op.target_object], "particle_systems")


    def execute(self, context):
        options = self

        if DENDRITE_GROUP_NAME not in bpy.data.collections:
            group = bpy.data.collections.new(DENDRITE_GROUP_NAME)
            context.scene.collection.children.link(group)
        else:
            group = bpy.data.collections[DENDRITE_GROUP_NAME]

        ob = bpy.data.objects[options.target_object].evaluated_get(bpy.context.evaluated_depsgraph_get())

        particle_system = ob.particle_systems[options.target_particle_system]

        points = [(x.location[0], x.location[1], x.location[2]) for x in particle_system.particles]

        normals = [bpy.data.objects[options.target_object].closest_point_on_mesh(x.location)[1] for x in particle_system.particles]

        trees = createMultipleTrees(points, normals, self)

        # Add trees to group
        for tree in trees:
            group.objects.link(tree)

        return {'FINISHED'}

class OBJECT_OT_dendritedelete(bpy.types.Operator):
    bl_idname = "object.delete_mst_dendrites"
    bl_label = "Delete Dendrites"

    def execute(self, context):
        if DENDRITE_GROUP_NAME in bpy.data.collections:
            trees = bpy.data.collections[DENDRITE_GROUP_NAME].objects
            for tree in trees:
                context.scene.collection.objects.unlink(tree)
                bpy.data.objects.remove(tree)

        return {'FINISHED'}

