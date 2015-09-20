# --------------------------------------------------------------------------
# BlenderAndMBDyn
# Copyright (C) 2015 G. Douglas Baldwin - http://www.baldwintechnology.com
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of BlenderAndMBDyn.
#
#    BlenderAndMBDyn is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BlenderAndMBDyn is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#
#    You should have received a copy of the GNU General Public License
#    along with BlenderAndMBDyn.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 

if "bpy" in locals():
    import imp
    imp.reload(bpy)
    imp.reload(root_dot)
    imp.reload(Operator)
    imp.reload(Entity)
else:
    from .common import (safe_name, Type, aerodynamic_types, beam_types, force_types, genel_types, joint_types, environment_types, node_types,
        structural_static_types, structural_dynamic_types, Ellipsoid, RhombicPyramid, Teardrop, Cylinder, Sphere, RectangularCuboid)
    from .base import bpy, BPY, root_dot, database, Operator, Entity, Bundle, SelectedObjects, SegmentList
    from .base import update_element
    from mathutils import Vector
    from copy import copy
    import os
    import subprocess
    from tempfile import TemporaryFile
    from pickle import Pickler
    from io import StringIO

types = aerodynamic_types + beam_types + ["Body"] + force_types + genel_types + joint_types + environment_types + ["Driven"] + node_types

tree = ["Element",
    ["Aerodynamic", aerodynamic_types,
    "Beam", beam_types,
    Type("Body", 1),
    "Force", force_types,
    "GENEL", genel_types,
    "Joint", joint_types,
    "Environment", environment_types,
    "Driven",
    "Node", node_types,
    ]]

class Base(Operator):
    bl_label = "Elements"
    exclusive = False
    N_objects = 2
    @classmethod
    def poll(cls, context):
        obs = SelectedObjects(context)
        return ((cls.N_objects == 0 and not (cls.exclusive and database.element.filter(cls.bl_label)))
            or len(obs) == cls.N_objects - 1
            or (len(obs) == cls.N_objects and not (cls.exclusive and database.element.filter(cls.bl_label, obs[0]))))
    def sufficient_objects(self, context):
        objects = SelectedObjects(context)
        if len(objects) == self.N_objects - 1:
            bpy.ops.mesh.primitive_cube_add()
            for obj in objects:
                obj.select = True
            objects.insert(0, context.active_object)
            if 1 < len(objects):
                objects[0].location = objects[1].location
            exec("bpy.ops." + root_dot + "object_specifications('INVOKE_DEFAULT')")
        return objects
    def store(self, context):
        self.entity.objects = self.sufficient_objects(context)
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.element_uilist = bpy.props.CollectionProperty(type = ListItem)
        def select_and_activate(self, context):
            if database.element and self.element_index < len(database.element):
                bpy.ops.object.select_all(action='DESELECT')
                element = database.element[self.element_index]
                if hasattr(element, "objects"):
                    for ob in element.objects:
                        ob.select = True
                    if element.objects and element.objects[0].name in context.scene.objects:
                        context.scene.objects.active = element.objects[0]
                    element.remesh()
        bpy.types.Scene.element_index = bpy.props.IntProperty(default=-1, update=select_and_activate)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.element_uilist
        del bpy.types.Scene.element_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.element_index, context.scene.element_uilist
    def set_index(self, context, value):
        context.scene.element_index = value
    def draw_panel_post(self, context, layout):
        selected_obs = set(SelectedObjects(context))
        if selected_obs:
            used_obs = set()
            for e in database.element + database.drive + database.input_card:
                if hasattr(e, "objects"):
                    used_obs.update(set(e.objects))
            if selected_obs.intersection(used_obs):
                layout.menu(root_dot + "selected_objects")
            else:
                layout.operator_context = 'EXEC_DEFAULT'
                layout.operator("object.delete")

class Constitutive(Base):
    constitutive = bpy.props.PointerProperty(type = BPY.Constitutive)
    def prereqs(self, context):
        self.constitutive.mandatory = True
        self.constitutive.dimension = "3D"
    def assign(self, context):
        self.constitutive.assign(self.entity.constitutive)
    def store(self, context):
        self.entity.constitutive = self.constitutive.store()
        self.entity.objects = self.sufficient_objects(context)
    def draw(self, context):
        self.constitutive.draw(self.layout, text="Constitutive")
    def check(self, context):
        return self.constitutive.check(context)

class Drive(Base):
    drive = bpy.props.PointerProperty(type = BPY.Drive)
    def prereqs(self, context):
        self.drive.mandatory = True
    def assign(self, context):
        self.drive.assign(self.entity.drive)
    def store(self, context):
        self.entity.drive = self.drive.store()
        self.entity.objects = self.sufficient_objects(context)
    def draw(self, context):
        self.drive.draw(self.layout, "Drive")
    def check(self, context):
        return self.drive.check(context)

class Friction(Base):
    friction = bpy.props.PointerProperty(type = BPY.Friction)
    def assign(self, context):
        self.friction.assign(self.entity.friction)
    def store(self, context):
        self.entity.friction = self.friction.store()
        self.entity.objects = self.sufficient_objects(context)
    def draw(self, context):
        self.friction.draw(self.layout, text="Friction")
    def check(self, context):
        return self.friction.check(context)

klasses = dict()

class StructuralForce(Entity):
    elem_type = "force"
    file_ext = "frc"
    labels = "node Fx Fy Fz X Y Z".split()
    def write(self, f):
        rot_0, globalV_0, Node_0 = self.rigid_offset(0)
        rotT_0 = self.objects[0].matrix_world.to_quaternion().to_matrix()
        relative_dir = rot_0*rotT_0*Vector((0., 0., 1.))
        relative_arm_0 = rot_0*globalV_0
        string = "\tforce: " + self.safe_name() + ", " + self.orientation
        if self.orientation == "follower":
            relative_dir = rot_0*rotT_0*Vector((0., 0., 1.))
        else:
            relative_dir = rotT_0*Vector((0., 0., 1.))
        f.write(string+
        ",\n\t\t" + safe_name(Node_0.name) +
        ",\n\t\t\tposition, ")
        self.write_vector(f, relative_arm_0, ",\n\t\t\t")
        self.write_vector(f, relative_dir, ",\n\t\t")
        f.write("reference, " + self.drive.safe_name() + ";\n")
    def remesh(self):
        RhombicPyramid(self.objects[0])

class Force(Drive):
    orientation = bpy.props.EnumProperty(items=[("follower", "Follower", ""), ("absolute", "Absolute", "")], name="Orientation", default="follower")
    def assign(self, context):
        self.orientation = self.entity.orientation
        super().assign(context)
    def store(self, context):
        self.entity.orientation = self.orientation
        super().store(context)
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "orientation")
        self.drive.draw(layout, "Drive")

class StructuralForceOperator(Force):
    bl_label = "Structural force"
    N_objects = 1
    def create_entity(self):
        return StructuralForce(self.name)

klasses[StructuralForceOperator.bl_label] = StructuralForceOperator

class StructuralInternalForce(Entity):
    elem_type = "force"
    file_ext = "frc"
    labels = "node1 F1x F1y F1z X1 Y1 Z1 node2 F2x F2y F2z X2 Y2 Z2".split()
    def write(self, f):
        rot_0, globalV_0, Node_0 = self.rigid_offset(0)
        rotT_0 = self.objects[0].matrix_world.to_quaternion().to_matrix()
        relative_arm_0 = rot_0*globalV_0
        rot_1, globalV_1, Node_1 = self.rigid_offset(1)
        relative_arm_1 = rot_1*globalV_1
        string = "\tforce: " + self.safe_name() + ", "
        if self.orientation == "follower":
            string += "follower internal"
            relative_dir = rot_0*rotT_0*Vector((0., 0., 1.))
        else:
            string += "absolute internal"
            relative_dir = rotT_0*Vector((0., 0., 1.))
        f.write(string+
        ",\n\t\t" + safe_name(Node_0.name) + ",\n\t\t\t")
        self.write_vector(f, relative_dir, ",\n\t\t\t")
        self.write_vector(f, relative_arm_0, ",\n\t\t")
        f.write(safe_name(Node_1.name) + ",\n\t\t\t")
        self.write_vector(f, relative_arm_1, ",\n\t\t")
        f.write("reference, " + self.drive.safe_name() + ";\n")
    def remesh(self):
        RhombicPyramid(self.objects[0])

class StructuralInternalForceOperator(Force):
    bl_label = "Structural internal force"
    def create_entity(self):
        return StructuralInternalForce(self.name)

klasses[StructuralInternalForceOperator.bl_label] = StructuralInternalForceOperator

class StructuralCouple(Entity):
    elem_type = "couple"
    file_ext = "frc"
    labels = "node Mx My Mz".split()
    def write(self, f):
        rot_0, globalV_0, Node_0 = self.rigid_offset(0)
        rotT_0 = self.objects[0].matrix_world.to_quaternion().to_matrix()
        string = "\tcouple: " + self.safe_name() + ", "
        if self.orientation == "follower":
            string += "follower"
            relative_dir = rot_0*rotT_0*Vector((0., 0., 1.))
        else:
            string += "absolute"
            relative_dir = rotT_0*Vector((0., 0., 1.))
        f.write(string+
        ",\n\t\t" + safe_name(Node_0.name) + ",\n\t\t\t")
        self.write_vector(f, relative_dir, ",\n\t\t")
        f.write("reference, " + self.drive.safe_name() + ";\n")
    def remesh(self):
        RhombicPyramid(self.objects[0])

class StructuralCoupleOperator(Force):
    bl_label = "Structural couple"
    N_objects = 1
    def create_entity(self):
        return StructuralCouple(self.name)

klasses[StructuralCoupleOperator.bl_label] = StructuralCoupleOperator

class StructuralInternalCouple(Entity):
    elem_type = "couple"
    file_ext = "frc"
    labels = "node1 M1x M1y M1z node2 M2x M2y M2z".split()
    def write(self, f):
        rot_0, globalV_0, Node_0 = self.rigid_offset(0)
        rotT_0 = self.objects[0].matrix_world.to_quaternion().to_matrix()
        rot_1, globalV_1, Node_1 = self.rigid_offset(1)
        string = "\tcouple: " + self.safe_name() + ", "
        if self.orientation == "follower":
            string += "follower internal"
            relative_dir = rot_0*rotT_0*Vector((0., 0., 1.))
        else:
            string += "absolute internal"
            relative_dir = rotT_0*Vector((0., 0., 1.))
        f.write(string+
        ",\n\t\t" + safe_name(Node_0.name) + ",\n\t\t\t")
        self.write_vector(f, relative_dir, ",\n\t\t")
        f.write(safe_name(Node_1.name) + ",\n\t\treference, " + self.drive.safe_name() + ";\n")
    def remesh(self):
        RhombicPyramid(self.objects[0])

class StructuralInternalCoupleOperator(Force):
    bl_label = "Structural internal couple"
    def create_entity(self):
        return StructuralInternalCouple(self.name)

klasses[StructuralInternalCoupleOperator.bl_label] = StructuralInternalCoupleOperator

class Joint(Entity):
    elem_type = "joint"
    file_ext = "jnt"
    labels = "Fx Fy Fz Mx My Mz FX FY FZ MX MY MZ".split()

class Hinge(Joint):
    def write_hinge(self, f, name, V1=True, V2=True, M1=True, M2=True):
        rot_0, globalV_0, Node_0 = self.rigid_offset(0)
        localV_0 = rot_0*globalV_0
        rot_1, globalV_1, Node_1 = self.rigid_offset(1)
        to_hinge = rot_1*(globalV_1 + self.objects[0].matrix_world.translation - self.objects[1].matrix_world.translation)
        rotT = self.objects[0].matrix_world.to_quaternion().to_matrix()
        f.write(
        "\tjoint: " + self.safe_name() + ", " + name + ",\n" +
        "\t\t" + safe_name(Node_0.name))
        if V1:
            f.write(", ")
            self.write_vector(f, localV_0)
        if M1:
            f.write(",\n\t\t\thinge, matr,\n")
            self.write_matrix(f, rot_0*rotT, "\t\t\t\t")
        f.write(", \n\t\t" + safe_name(Node_1.name))
        if V2:
            f.write(", ")
            self.write_vector(f, to_hinge)
        if M2:
            f.write(",\n\t\t\thinge, matr,\n")
            self.write_matrix(f, rot_1*rotT, "\t\t\t\t")

class AxialRotation(Hinge):
    def write(self, f):
        self.write_hinge(f, "axial rotation")
        f.write(",\n\t\treference, " + self.drive.safe_name() + ";\n")
    def remesh(self):
        Cylinder(self.objects[0])

class AxialRotationOperator(Drive):
    bl_label = "Axial rotation"
    def create_entity(self):
        return AxialRotation(self.name)

klasses[AxialRotationOperator.bl_label] = AxialRotationOperator

class Clamp(Joint):
    def write(self, f):
        f.write(
        "\tjoint: " + self.safe_name() + ", clamp,\n" +
        "\t\t" + safe_name(self.objects[0].name) + ", node, node;\n")
    def remesh(self):
        Teardrop(self.objects[0])

class ClampOperator(Base):
    bl_label = "Clamp"
    exclusive = True
    N_objects = 1
    def create_entity(self):
        return Clamp(self.name)

klasses[ClampOperator.bl_label] = ClampOperator

class DeformableDisplacementJoint(Hinge):
    labels = "Fx Fy Fz Mx My Mz FX FY FZ MX MY MZ ex ey ez ex_dot ey_dot ez_dot".split()
    def write(self, f):
        self.write_hinge(f, "deformable displacement joint")
        f.write(",\n\t\treference, " + self.constitutive.safe_name() + ";\n")
    def remesh(self):
        Cylinder(self.objects[0])

class DeformableDisplacementJointOperator(Constitutive):
    bl_label = "Deformable displacement joint"
    def create_entity(self):
        return DeformableDisplacementJoint(self.name)

klasses[DeformableDisplacementJointOperator.bl_label] = DeformableDisplacementJointOperator

class DeformableHinge(Hinge):
    def write(self, f):
        self.write_hinge(f, "deformable hinge", V1=False, V2=False)
        f.write(",\n\t\treference, " + self.constitutive.safe_name() + ";\n")
    def remesh(self):
        Sphere(self.objects[0])

class DeformableHingeOperator(Constitutive):
    bl_label = "Deformable hinge"
    def create_entity(self):
        return DeformableJoint(self.name)

klasses[DeformableHingeOperator.bl_label] = DeformableHingeOperator

class DeformableJoint(Hinge):
    labels = "Fx Fy Fz Mx My Mz FX FY FZ MX MY MZ ex ey ez".split()
    def write(self, f):
        self.write_hinge(f, "deformable joint")
        f.write(",\n\t\treference, " + self.constitutive.safe_name() + ";\n")
    def remesh(self):
        Sphere(self.objects[0])

class DeformableJointOperator(Constitutive):
    bl_label = "Deformable joint"
    def prereqs(self, context):
        self.constitutive.mandatory = True
        self.constitutive.dimension = "6D"
    def create_entity(self):
        return DeformableJoint(self.name)

klasses[DeformableJointOperator.bl_label] = DeformableJointOperator

class Distance(Joint):
    def write(self, f):
        f.write("\tjoint: " + self.safe_name() + ", distance,\n")
        for i in range(2):
            self.write_node(f, i, node=True, position=True, p_label="position")
            f.write(",\n")
        if self.drive is None:
            f.write("\t\tfrom nodes;\n")
        else:
            f.write("\t\treference, " + self.drive.safe_name() + ";\n")

class DistanceOperator(Drive):
    bl_label = "Distance"
    exclusive = True
    def prereqs(self, context):
        self.drive.mandatory = False
    def create_entity(self):
        return Distance(self.name)

klasses[DistanceOperator.bl_label] = DistanceOperator

class InLine(Joint):
    def write(self, f):
        rot0, globalV0, iNode0 = self.rigid_offset(0)
        localV0 = rot0*globalV0
        rot_1, globalV_1, Node_1 = self.rigid_offset(1)
        to_point = rot_1*(globalV_1 + self.objects[0].matrix_world.translation - self.objects[1].matrix_world.translation)
        rot = self.objects[0].matrix_world.to_quaternion().to_matrix()
        f.write("\tjoint: " + self.safe_name() + ", inline,\n")
        self.write_node(f, 0, node=True, position=True, orientation=True)
        f.write(",\n\t\t" + safe_name(Node_1.name))
        f.write(",\n\t\t\toffset, ")
        self.write_vector(f, to_point, ";\n")
    def remesh(self):
        RhombicPyramid(self.objects[0])

class InLineOperator(Base):
    bl_label = "Inline"
    def create_entity(self):
        return InLine(self.name)

klasses[InLineOperator.bl_label] = InLineOperator

class InPlane(Joint):
    def write(self, f):
        rot0, globalV0, iNode0 = self.rigid_offset(0)
        localV0 = rot0*globalV0
        rot1, globalV1, iNode1 = self.rigid_offset(1)
        to_point = rot1*(globalV1 + self.objects[0].matrix_world.translation - self.objects[1].matrix_world.translation)
        rot = self.objects[0].matrix_world.to_quaternion().to_matrix()
        normal = rot*rot0*Vector((0., 0., 1.))
        f.write(
        "\tjoint: " + self.safe_name() + ", inplane,\n" +
        "\t\t" + safe_name(iNode0.name) + ",\n\t\t\t")
        self.write_vector(f, localV0, ",\n\t\t\t")
        self.write_vector(f, normal, ",\n\t\t")
        f.write(safe_name(iNode1.name) + ",\n\t\t\toffset, " + ", ".join([BPY.FORMAT(x) for x in to_point]) + ";\n")
    def remesh(self):
        RhombicPyramid(self.objects[0])

class InPlaneOperator(Base):
    bl_label = "Inplane"
    def create_entity(self):
        return InPlane(self.name)

klasses[InPlaneOperator.bl_label] = InPlaneOperator

class RevoluteHinge(Hinge):
    labels = "Fx Fy Fz Mx My Mz FX FY FZ MX MY MZ ex ey ez Ax Ay Az Ax_dot Ay_dot Az_dot".split()
    def write(self, f):
        self.write_hinge(f, "revolute hinge")
        if self.theta is not None:
            f.write(",\n\t\tinitial theta, " + BPY.FORMAT(self.theta))
        if self.average_radius is not None:
            f.write(",\n\t\tfriction, " + BPY.FORMAT(self.average_radius))
            if self.preload is not None:
                f.write(",\n\t\t\tpreload, " + BPY.FORMAT(self.preload))
            f.write(",\n\t\t\t" + self.friction.string())
        f.write(";\n")
    def remesh(self):
        Cylinder(self.objects[0])

class RevoluteHingeOperator(Friction):
    bl_label = "Revolute hinge"
    theta = bpy.props.PointerProperty(type = BPY.Float)
    average_radius = bpy.props.PointerProperty(type = BPY.Float)
    preload = bpy.props.PointerProperty(type = BPY.Float)
    def assign(self, context):
        self.theta.assign(self.entity.theta)
        self.average_radius.assign(self.entity.average_radius)
        self.preload.assign(self.entity.preload)
        super().assign(context)
    def store(self, context):
        self.entity.theta = self.theta.store()
        self.entity.average_radius = self.average_radius.store()
        self.entity.preload = self.preload.store()
        super().store(context)
    def draw(self, context):
        self.theta.draw(self.layout, text="Theta")
        self.average_radius.draw(self.layout, text="Average radius")
        if self.average_radius.select:
            self.preload.draw(self.layout, text="Preload")
            self.friction.draw(self.layout, text="Friction")
    def check(self, context):
        return self.theta.check(context) or self.average_radius.check(context) or self.preload.check(context) or self.friction.check(context)
    def create_entity(self):
        return RevoluteHinge(self.name)

klasses[RevoluteHingeOperator.bl_label] = RevoluteHingeOperator

class Rod(Joint):
    labels = "Fx Fy Fz Mx My Mz FX FY FZ MX MY MZ l ux uy uz l_dot".split()
    def write(self, f):
        f.write("\tjoint: " + self.safe_name() + ", rod,\n")
        for i in range(2):
            self.write_node(f, i, node=True, position=True, p_label="position")
            f.write(",\n")
        f.write("\t\tfrom nodes,\n\t\treference, " + self.constitutive.safe_name() + ";\n")

class RodOperator(Constitutive):
    bl_label = "Rod"
    def prereqs(self, context):
        self.constitutive.mandatory = True
        self.constitutive.dimension = "1D"
    def create_entity(self):
        return Rod(self.name)

klasses[RodOperator.bl_label] = RodOperator

class SphericalHinge(Hinge):
    def write(self, f):
        self.write_hinge(f, "spherical hinge")
        f.write(";\n")
    def remesh(self):
        Sphere(self.objects[0])

class SphericalHingeOperator(Base):
    bl_label = "Spherical hinge"
    def create_entity(self):
        return SphericalHinge(self.name)

klasses[SphericalHingeOperator.bl_label] = SphericalHingeOperator

class TotalJoint(Joint):
    labels = "Fx Fy Fz Mx My Mz FX FY FZ MX MY MZ dx dy dz dAx dAy dAz u v w dAx_dor dAy_dot dAz_dot".split()
    def write(self, f):
        rot_0, globalV_0, Node_0 = self.rigid_offset(0)
        localV_0 = rot_0*globalV_0
        rot_1, globalV_1, Node_1 = self.rigid_offset(1)
        to_joint = rot_1*(globalV_1 + self.objects[0].matrix_world.translation - self.objects[1].matrix_world.translation)
        rot = self.objects[0].matrix_world.to_quaternion().to_matrix()
        if Node_1 == self.objects[1]:
            rot_position = rot
        else:
            rot_position = self.objects[1].matrix_world.to_quaternion().to_matrix()
        f.write("\tjoint: " + self.safe_name() + ", total joint")
        if self.first == "rotate":
            f.write(",\n\t\t" + safe_name(Node_0.name) + ", position, ")
            self.write_vector(f, localV_0, ",\n\t\t\tposition orientation, matr,\n")
            self.write_matrix(f, rot_0*rot_position, "\t\t\t\t")
            f.write(",\n\t\t\trotation orientation, matr,\n")
            self.write_matrix(f, rot_0*rot, "\t\t\t\t")
        f.write(",\n\t\t" + safe_name(Node_1.name) + ", position, ")
        self.write_vector(f, to_joint, ",\n\t\t\tposition orientation, matr,\n")
        self.write_matrix(f, rot_1*rot_position, "\t\t\t\t")
        f.write(",\n\t\t\trotation orientation, matr,\n")
        self.write_matrix(f, rot_1*rot, "\t\t\t\t")
        if self.first == "displace":
            f.write(",\n\t\t" + safe_name(Node_0.name) + ", position, ")
            self.write_vector(f, localV_0, ",\n\t\t\tposition orientation, matr,\n")
            self.write_matrix(f, rot_0*rot_position, "\t\t\t\t")
            f.write(",\n\t\t\trotation orientation, matr,\n")
            self.write_matrix(f, rot_0*rot, "\t\t\t\t")
        f.write(",\n\t\t\tposition constraint")
        for d in self.drives[:3]: 
            if d:
                f.write(", active")
            else:
                f.write(", inactive")
        f.write(", component")
        database.drive_indenture += 2
        for d in self.drives[:3]:
            if d:
                f.write(",\n\t\treference, " + d.safe_name())
            else:
                f.write(",\n\t\t\t\tinactive")
        f.write(",\n\t\t\torientation constraint")
        for d in self.drives[3:6]: 
            if d:
                f.write(", active")
            else:
                f.write(", inactive")
        f.write(", component")
        for d in self.drives[3:6]:
            if d:
                f.write(",\n\t\treference, " + d.safe_name())
            else:
                f.write(",\n\t\t\t\tinactive")
        database.drive_indenture -= 2
        f.write(";\n")
    def remesh(self):
        Sphere(self.objects[0])

class TotalJointOperator(Base):
    bl_label = "Total joint"
    first = bpy.props.EnumProperty(items=[("displace", "Displacement", ""), ("rotate", "Angular Displacement", "")], default="displace")
    drives = bpy.props.CollectionProperty(type = BPY.Drive)
    def prereqs(self, context):
        for i in range(6):
            self.drives.add()
        self.titles = list()
        for t1 in ["Displacement-", "Angular Displacement-"]:
            for t2 in "XYZ":
                self.titles.append(t1 + t2)
    def assign(self, context):
        self.first = self.entity.first
        for i, d in enumerate(self.entity.drive):
            self.drives[i].assign(d)
    def store(self, context):
        self.entity.first = self.first
        self.entity.drives = [d.store() for d in self.drives]
        self.entity.objects = self.sufficient_objects(context)
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "first", text="Driven first")
        for d, t in zip(self.drives, self.titles):
            d.draw(layout, text = t)
    def check(self, context):
        return True in [d.check(context) for d in self.drives]
    def create_entity(self):
        return TotalJoint(self.name)

klasses[TotalJointOperator.bl_label] = TotalJointOperator

class ViscousBody(Joint):
    def write(self, f):
        f.write(
        "\tjoint: " + self.safe_name() + ", viscous body,\n\t\t" +
        safe_name(self.objects[0].name) +
        ",\n\t\tposition, reference, node, null" +
        ",\n\t\treference, " + self.constitutive.safe_name() + ";\n")
    def remesh(self):
        Sphere(self.objects[0])

class ViscousBodyOperator(Constitutive):
    bl_label = "Viscous body"
    N_objects = 1
    def prereqs(self, context):
        self.constitutive.mandatory = True
        self.constitutive.dimension = "6D"
    def create_entity(self):
        return ViscousBody(self.name)

klasses[ViscousBodyOperator.bl_label] = ViscousBodyOperator

class Body(Entity):
    elem_type = "body"
    def write(self, f):
        f.write("\tbody: " + self.safe_name() + ",\n")
        self.write_node(f, 0, node=True)
        f.write("\t\t\t" + BPY.FORMAT(self.mass) + ",\n")
        self.write_node(f, 0, position=True, p_label="")
        if self.inertial_matrix is not None:
            f.write(", " + self.inertial_matrix.string())
            self.write_node(f, 0, orientation=True, o_label="inertial")
        f.write(";\n")
    def remesh(self):
        Ellipsoid(self.objects[0], self.mass, self.inertial_matrix)

class BodyMass(bpy.types.PropertyGroup, BPY.ValueMode):
    value = bpy.props.FloatProperty(min=-9.9e10, max=9.9e10, step=100, precision=6, description="Mass of the body")
BPY.klasses.append(BodyMass)    

class BodyOperator(Base):
    bl_label = "Body"
    N_objects = 1
    mass = bpy.props.PointerProperty(type = BodyMass)
    inertial_matrix = bpy.props.PointerProperty(type = BPY.MatrixFloat)
    def prereqs(self, context):
        self.mass.mandatory = True
        self.mass.assign(1.0)
        self.inertial_matrix.mandatory = True
        self.inertial_matrix.type = "3x3"
    def assign(self, context):
        self.mass.assign(self.entity.mass)
        self.inertial_matrix.assign(self.entity.inertial_matrix)
    def store(self, context):
        self.entity.mass = self.mass.store()
        self.entity.inertial_matrix = self.inertial_matrix.store()
        self.entity.objects = self.sufficient_objects(context)
    def draw(self, context):
        layout = self.layout
        self.mass.draw(layout, "Mass")
        self.inertial_matrix.draw(layout, "Inertial matrix")
    def check(self, context):
        return self.mass.check(context) or self.inertial_matrix.check(context)
    def create_entity(self):
        return Body(self.name)

klasses[BodyOperator.bl_label] = BodyOperator

class RigidOffset(Entity):
    def remesh(self):
        RhombicPyramid(self.objects[0])

class RigidOffsetOperator(Base):
    bl_label = "Rigid offset"
    exclusive = True
    def store(self, context):
        self.entity.objects = self.sufficient_objects(context)
        self.entity.objects[0].parent = self.entity.objects[1]
        self.entity.objects[0].matrix_parent_inverse = self.entity.objects[1].matrix_basis.inverted()
    def create_entity(self):
        return RigidOffset(self.name)

klasses[RigidOffsetOperator.bl_label] = RigidOffsetOperator

class DummyNode(Entity):
    def remesh(self):
        RhombicPyramid(self.objects[0])

class DummyNodeOperator(Base):
    bl_label = "Dummy node"
    exclusive = True
    def create_entity(self):
        return DummyNode(self.name)

klasses[DummyNodeOperator.bl_label] = DummyNodeOperator

class BeamSegment(Entity):
    elem_type = "beam2"
    file_ext = "act"
    labels = "Fx Fy Fz Mx My Mz".split()
    def write(self, f):
        if hasattr(self, "consumer"):
            return
        f.write("\tbeam2: " + self.safe_name() + ",\n")
        for i in range(len(self.objects)):
            self.write_node(f, i, node=True, position=True, orientation=True, p_label="position", o_label="orientation")
            f.write(",\n")
        f.write("\t\tfrom nodes, reference, " + self.constitutive.safe_name() + ";\n")
    def remesh(self):
        for obj in self.objects:
            RectangularCuboid(obj)

class BeamSegmentOperator(Constitutive):
    bl_label = "Beam segment"
    def prereqs(self, context):
        self.constitutive.mandatory = True
        self.constitutive.dimension = "6D"
    def create_entity(self):
        return BeamSegment(self.name)

klasses[BeamSegmentOperator.bl_label] = BeamSegmentOperator

class SegmentPair:
    N_objects = 0
    segments = bpy.props.CollectionProperty(type=BPY.Segment)
    in_process = False
    @classmethod
    def begin_process(cls):
        cls.in_process = True
    @classmethod
    def end_process(cls):
        cls.in_process = False
    @classmethod
    def selected_pair(cls, context, segment_type="Beam segment"):
        obs = SelectedObjects(context)
        if len(obs) != 3:
            return list()
        selected_pair = list()
        for ob in obs:
            selected_pair.extend(database.element.filter(segment_type, ob))
        if len(selected_pair) == 2 and not selected_pair[0].objects[1] == selected_pair[1].objects[0]:
            selected_pair.reverse()
        if len(selected_pair) != 2 or not selected_pair[0].objects[1] == selected_pair[1].objects[0]:
            return list()
        for ob in obs:
            if ob not in selected_pair[0].objects + selected_pair[1].objects:
                return list()
        return selected_pair
    @classmethod
    def poll(cls, context):
        if cls.in_process:
            return True
        selected_pair = cls.selected_pair(context, cls.segment_type)
        if not selected_pair:
            return False
        entity = database.element[context.scene.element_index]
        for s in selected_pair:
            if hasattr(s, "consumer") and (not hasattr(entity, "segments") or not s in entity.segments):
                return False
        return True
    def prereqs(self, context):
        self.begin_process()
        self.segments.clear()
        for segment in self.selected_pair(context, self.segment_type):
            s = self.segments.add()
            s.assign(segment)
    def store(self, context):
        if not hasattr(self.entity, "segments"):
            self.entity.segments = SegmentList()
        self.entity.segments.clear()
        for segment in self.segments:
            self.entity.segments.append(segment.store())
        self.entity.objects = self.entity.segments[0].objects + self.entity.segments[1].objects[1:]
        self.end_process()
    def draw(self, context):
        layout = self.layout
        for i, s in enumerate(self.segments):
            row = layout.row()
            row.label("Segment-" + str(i + 1) + ":")
            row.prop(s, "edit", toggle=True, text=s.name)

class ThreeNodeBeam(Entity):
    elem_type = "beam3"
    file_ext = "act"
    labels = "F1x F1y F1z M1x M1y M1z F2x F2y F2z M2x M2y M2z".split()
    def write(self, f):
        f.write("\tbeam3: " + self.safe_name() + ",\n")
        self.objects = self.segments[0].objects + self.segments[1].objects[1:]
        for i in range(3):
            self.write_node(f, i, node=True, position=True, orientation=True, p_label="position", o_label="orientation")
            f.write(",\n")
        f.write("\t\tfrom nodes, reference, " + self.segments[0].constitutive.safe_name())
        f.write(",\n\t\tfrom nodes, reference, " + self.segments[1].constitutive.safe_name() + ";\n")
        del self.objects
    def remesh(self):
        for s in self.segments:
            s.remesh()

class ThreeNodeBeamOperator(SegmentPair, Base):
    bl_label = "Three node beam"
    segment_type = "Beam segment"
    def create_entity(self):
        return ThreeNodeBeam(self.name)

klasses[ThreeNodeBeamOperator.bl_label] = ThreeNodeBeamOperator

class Gravity(Entity):
    elem_type = "gravity"
    file_ext = "grv"
    labels = "X_dotdot Y_dotdot Z_dotdot".split()
    def write(self, f):
        f.write("\tgravity: " + self.matrix.string() + ", reference, " + self.drive.safe_name() + ";\n")

class GravityOperator(Drive):
    bl_label = "Gravity"
    matrix = bpy.props.PointerProperty(type = BPY.Matrix)
    @classmethod
    def poll(cls, context):
        return cls.bl_idname.startswith(root_dot+"e_") or not database.element.filter("Gravity")
    def prereqs(self, context):
        self.matrix.mandatory = True
        self.matrix.type = "3x1"
        super().prereqs(context)
    def assign(self, context):
        self.matrix.assign(self.entity.matrix)
        super().assign(context)
    def store(self, context):
        self.entity.matrix = self.matrix.store()
        self.entity.drive = self.drive.store()
    def draw(self, context):
        layout = self.layout
        self.matrix.draw(layout, "Vector")
        self.drive.draw(layout, "Drive")
    def check(self, context):
        return self.matrix.check(context) or super().check(context)
    def create_entity(self):
        return Gravity(self.name)

klasses[GravityOperator.bl_label] = GravityOperator

class Driven(Entity):
    elem_type = "driven"
    def write(self, f):
        f.write("\tdriven: " + self.safe_name() + ",\n" +
        self.drive.safe_name() + ",\n" +
        "\t\texisting: " + self.element.elem_type + ", " + self.element.safe_name() + ";\n")

class DrivenOperator(Drive):
    bl_label = "Driven"
    element = bpy.props.PointerProperty(type = BPY.Element)
    @classmethod
    def poll(cls, context):
        return context.scene.element_uilist
    def prereqs(self, context):
        self.element.mandatory = True
        self.element.assign(database.element[context.scene.element_index])
        super().prereqs(context)
    def assign(self, context):
        self.element.assign(self.entity.element)
        super().assign(context)
    def store(self, context):
        self.entity.element = self.element.store()
        self.entity.drive = self.drive.store()
    def draw(self, context):
        layout = self.layout
        self.drive.draw(layout, "Drive")
        self.element.draw(layout, "Element")
    def check(self, context):
        return self.element.check(context) or super().check(context)
    def create_entity(self):
        return Driven(self.name)

klasses[DrivenOperator.bl_label] = DrivenOperator

class Plot:
    bl_options = {'REGISTER', 'INTERNAL'}
    prereqs_met = bpy.props.BoolProperty(default=False)
    label_names = bpy.props.CollectionProperty(type=BPY.Str)
    def load(self, context, exts, pd):
        if not self.prereqs_met:
            for prereq in "pandas matplotlib.pyplot".split():
                if subprocess.call(("python", "-c", "import " + prereq)):
                    raise ImportError("No module named " + prereq)
            self.prereqs_met = True
        self.base = os.path.join(os.path.splitext(context.blend_data.filepath)[0], context.scene.name)
        if 'frequency' not in BPY.plot_data:
            with open(".".join((self.base, "log")), 'r') as f:
                for line in f:
                    if line.startswith("output frequency:"):
                        BPY.plot_data['frequency'] = int(line.split()[-1])
                        break
        if 'out' not in BPY.plot_data:
            BPY.plot_data['out'] = pd.read_table(".".join((self.base, 'out')), sep=" ", skiprows=2, usecols=[i for i in range(2, 9)])
            BPY.plot_data['timeseries'] = BPY.plot_data['out']['Time'][::BPY.plot_data['frequency']]
        for ext in exts:
            if ext not in BPY.plot_data:
                df = pd.read_csv(".".join((self.base, ext)), sep=" ", header=None, skipinitialspace=True, names=[i for i in range(50)], lineterminator="\n")
                value_counts = df[0].value_counts()
                p = dict()
                for node_label in df[0].unique():
                    p[str(int(node_label))] = df.ix[df[0]==node_label, 1:].dropna(1, 'all')
                    p[str(int(node_label))].index = [i for i in range(value_counts[node_label])]
                BPY.plot_data[ext] = pd.Panel(p)
    def execute(self, context):
        select = [name.select for name in self.label_names]
        if True in select:
            dataframe = self.dataframe.T[select].T.rename(BPY.plot_data['timeseries'])
            dataframe.columns = [name.value for name in self.label_names if name.select]
            plot_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plot.py")
            with TemporaryFile('w') as f:
                f.write(self.entity.name + "\n")
                dataframe.to_csv(f)
                f.seek(0)
                subprocess.Popen(("python", plot_script), stdin=f)
        elif self.label_names:
            self.report({'ERROR'}, "None selected.")
        return{'FINISHED'}
    def draw(self, context):
        layout = self.layout
        for name in self.label_names:
            row = layout.row()
            row.prop(name, "select", text="")
            row.label(name.value)

class PlotElement(bpy.types.Operator, Plot):
    bl_label = "Plot output"
    bl_description = "Plot the simulated output for the selected element"
    bl_idname = root_dot + "plot_element"
    @classmethod
    def poll(cls, context):
        return context.scene.clean_log and hasattr(database.element[context.scene.element_index], "file_ext")
    def invoke(self, context, event):
        self.entity = database.element[context.scene.element_index]
        import pandas as pd
        self.load(context, [self.entity.file_ext], pd)
        self.label_names.clear()
        key = "1" if self.entity.file_ext == "grv" else str(database.element.index(self.entity))
        self.dataframe = BPY.plot_data[self.entity.file_ext][key].dropna(1, 'all')
        for i in range(self.dataframe.shape[1]):
            name = self.label_names.add()
            name.value = self.entity.labels[i] if i < len(self.entity.labels) else str(i + 2)
            name.select = False
        return context.window_manager.invoke_props_dialog(self)
BPY.klasses.append(PlotElement)

class PlotNode(bpy.types.Operator, Plot):
    bl_label = "Plot the node"
    bl_description = "Plot the simulated trajectory of a selected node"
    bl_idname = root_dot + "plot_node"
    @classmethod
    def poll(cls, context):
        obs = SelectedObjects(context)
        return context.scene.clean_log and len(obs) == 1 and obs[0] in database.node
    def invoke(self, context, event):
        self.entity = SelectedObjects(context)[0]
        import pandas as pd
        self.load(context, "ine mov".split(), pd)
        node_label = str(database.node.index(SelectedObjects(context)[0]))
        self.dataframe = BPY.plot_data['mov'][node_label].dropna(1, 'all')
        #self.dataframe.columns = "X Y Z Phi_x Phi_y Phi_z U V W Omega_x Omega_y Omeda_z dU/dt dV/dt dW/dt dOmega_x/dt dOmega_y/dt dOmega_z/dt 20 21 22 23 24 25".split()[:self.dataframe.shape[1]]
        self.dataframe.columns = "X Y Z".split() + [str(i) for i in range(5, self.dataframe.shape[1] + 2)]
        if node_label in BPY.plot_data['ine']:
            df = BPY.plot_data['ine'][node_label].dropna(1, 'all')
            df.columns = "px py pz Lx Ly Lz dpx/dt dpy/dt dpz/dt dLx/dt dLy/dt dLz/dt".split()
            self.dataframe = self.dataframe.join(df)
        self.label_names.clear()
        for label in self.dataframe.columns:
            name = self.label_names.add()
            name.value = label
            name.select = False
        return context.window_manager.invoke_props_dialog(self)
BPY.klasses.append(PlotNode)

class DuplicateFromObjects(bpy.types.Operator):
    bl_label = "Duplicate"
    bl_description = "Duplicate the selected objects along with some or all of the entities using them"
    bl_idname = root_dot + "duplicate_from_objects"
    bl_options = {'REGISTER', 'INTERNAL'}
    to_scene = bpy.props.PointerProperty(type = BPY.Scene)
    entity_names = bpy.props.CollectionProperty(type=BPY.Str)
    @classmethod
    def poll(cls, context):
        return SelectedObjects(context)
    def invoke(self, context, event):
        self.entity_names.clear()
        self.users = database.entities_originating_from(SelectedObjects(context))
        for user in self.users:
            name = self.entity_names.add()
            name.value = user.name
            name.select = True
        return context.window_manager.invoke_props_dialog(self)
    def execute(self, context):
        entities = [u for u, n in zip(self.users, self.entity_names) if n.select]
        keys = [e for e in entities if e.type != "Reference frame"]
        if self.to_scene.select:
            old_entities = database.all_entities()
            new_entities = dict()
            def duplicate_if_singlet(x, initialize=False):
                if x not in new_entities:
                    database.to_be_duplicated = x
                    exec("bpy.ops." + root_dot + "d_" + "_".join(x.type.lower().split()) + "()")
                    new_entities[x] = database.dup
                    del database.dup
                    if not initialize:
                        keys.append(x)
            while keys:
                key = keys.pop()
                duplicate_if_singlet(key, initialize=True)
                for k, v in vars(key).items():
                    if isinstance(v, Entity):
                        duplicate_if_singlet(v)
                        new_entities[key].__dict__[k] = new_entities[v]
                    elif isinstance(v, list):
                        for i, x in enumerate(v):
                            if isinstance(x, Entity):
                                duplicate_if_singlet(x)
                                new_entities[key].__dict__[k][i] = new_entities[x]
            for frame in [e for e in entities if e.type == "Reference frame"]:
                duplicate_if_singlet(frame, initialize=True)
            new_obs = dict()
            for v in new_entities.values():
                if hasattr(v, "objects"):
                    for i, ob in enumerate(v.objects):
                        if ob not in new_obs:
                            bpy.ops.object.select_all(action='DESELECT')
                            ob.select = True
                            bpy.ops.object.duplicate()
                            new_obs[ob] = context.selected_objects[0]
                        v.objects[i] = new_obs[ob]
            if self.to_scene.name != context.scene.name:
                parent = dict()
                for v in new_obs.values():
                    context.scene.objects.unlink(v)
                for v in new_entities.values():
                    database.to_be_unlinked = v
                    exec("bpy.ops." + root_dot + "u_" + "_".join(v.type.lower().split()) + "()")
                context.screen.scene = bpy.data.scenes[self.to_scene.name]
                database.pickle()
                for e in old_entities:
                    if e in new_entities:
                        new_entities[e].name = e.name
                        database.to_be_linked = new_entities[e]
                        exec("bpy.ops." + root_dot + "l_" + "_".join(new_entities[e].type.lower().split()) + "()")
                for k, v in new_obs.items():
                    context.scene.objects.link(v)
                    v.parent = new_obs[v.parent] if v.parent in new_obs else None
                    v.matrix_parent_inverse = k.matrix_parent_inverse
        else:
            for e in keys:
                exec("bpy.ops." + root_dot + "d_" + "_".join(e.type.lower().split()) + "()")
        del self.users
        context.scene.dirty_simulator = True
        return {'FINISHED'}
    def draw(self, context):
        layout = self.layout
        self.to_scene.draw(layout, "Full copy")
        for name in self.entity_names:
            row = layout.row()
            row.prop(name, "select", text="", toggle=True)
            row.label(name.value)
    def check(self, context):
        return self.to_scene.check(context)
BPY.klasses.append(DuplicateFromObjects)

class Users(bpy.types.Operator):
    bl_label = "Users"
    bl_description = "Users of the selected objects"
    bl_idname = root_dot + "users"
    bl_options = {'REGISTER', 'INTERNAL'}
    entity_names = bpy.props.CollectionProperty(type=BPY.Str)
    @classmethod
    def poll(cls, context):
        return SelectedObjects(context)
    def invoke(self, context, event):
        self.entity_names.clear()
        self.users = database.entities_using(SelectedObjects(context))
        for user in self.users:
            name = self.entity_names.add()
            name.value = user.name
        return context.window_manager.invoke_props_dialog(self)
    def execute(self, context):
        for name, user in zip(self.entity_names, self.users):
            if name.select:
                module = user.__module__.split(".")[-1]
                entity_list = {"element": database.element, "drive": database.drive, "input_card": database.input_card}[module]
                context.scene[module + "_index"] = entity_list.index(user)
                exec("bpy.ops." + root_dot + "e_" + "_".join(user.type.lower().split()) + "('INVOKE_DEFAULT')")
        return {'FINISHED'}
    def draw(self, context):
        layout = self.layout
        for name in self.entity_names:
            row = layout.row()
            row.prop(name, "select", text="", toggle=True)
            row.label(name.value)
    def check(self, context):
        return False
BPY.klasses.append(Users)

class ObjectSpecifications(bpy.types.Operator):
    bl_label = "Object specifications"
    bl_description = "Name, location, and orientation of the selected objects"
    bl_idname = root_dot + "object_specifications"
    bl_options = {'REGISTER', 'INTERNAL'}
    @classmethod
    def poll(cls, context):
        return SelectedObjects(context)
    def invoke(self, context, event):
        self.objects = SelectedObjects(context)
        return context.window_manager.invoke_props_dialog(self)
    def execute(self, context):
        return {'FINISHED'}
    def draw(self, context):
        self.basis = [obj.rotation_mode for obj in self.objects]
        layout = self.layout
        for i, obj in enumerate(self.objects):
            layout.label("")
            layout.prop(obj, "name", text="")
            layout.prop(obj, "location")
            if obj.rotation_mode == 'QUATERNION':
                layout.prop(obj, "rotation_quaternion")
            elif obj.rotation_mode == 'AXIS_ANGLE':
                layout.prop(obj, "rotation_axis_angle")
            else:
                layout.prop(obj, "rotation_euler")
            layout.prop(obj, "rotation_mode")
    def check(self, context):
        return self.basis != [obj.rotation_mode for obj in self.objects]
BPY.klasses.append(ObjectSpecifications)

class Menu(bpy.types.Menu):
    bl_label = "Selected Objects"
    bl_description = "Actions for the selected object(s)"
    bl_idname = root_dot + "selected_objects"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator(root_dot + "object_specifications")
        layout.operator(root_dot + "users")
        layout.operator(root_dot + "duplicate_from_objects")
        layout.operator(root_dot + "plot_node")
BPY.klasses.append(Menu)

for t in types:
    class Tester(Base):
        bl_label = t[0] if isinstance(t, tuple) else t
        @classmethod
        def poll(cls, context):
            return False
        def create_entity(self):
            return Entity(self.name)
    if Tester.bl_label not in klasses:
        klasses[Tester.bl_label] = Tester

bundle = Bundle(tree, Base, klasses, database.element, "element")
