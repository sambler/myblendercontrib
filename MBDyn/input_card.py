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
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BlenderAndMBDyn.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 

if "bpy" in locals():
    import imp
    imp.reload(bpy)
    imp.reload(Operator)
    imp.reload(Entity)
    imp.reload(subsurf)
else:
    from .base import bpy, BPY, root_dot, database, Operator, Entity, Bundle, SelectedObjects, update_matrix
    from .common import RhombicPyramid, write_vector, write_matrix
    from mathutils import Vector
    from copy import copy

types = ["c81 data", "Hydraulic fluid", "Include", "Module load", "Print symbol table", "Reference frame", "Remark", "Set", "Setenv"]

tree = ["Input Card", types]

klasses = dict()

class Base(Operator):
    bl_label = "Input Cards"
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return True
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.input_card_uilist = bpy.props.CollectionProperty(type = ListItem)
        def select_and_activate(self, context):
            if database.input_card and self.input_card_index < len(database.input_card) and hasattr(database.input_card[self.input_card_index], "objects"):
                bpy.ops.object.select_all(action='DESELECT')
                input_card = database.input_card[self.input_card_index]
                for ob in input_card.objects:
                    ob.select = True
                context.scene.objects.active = input_card.objects[0]
                input_card.remesh()
        bpy.types.Scene.input_card_index = bpy.props.IntProperty(default=-1, update=select_and_activate)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.input_card_uilist
        del bpy.types.Scene.input_card_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.input_card_index, context.scene.input_card_uilist
    def set_index(self, context, value):
        context.scene.input_card_index = value

for t in types:
    class Tester(Base):
        bl_label = t
        @classmethod
        def poll(cls, context):
            return False
        def create_entity(self):
            return Entity(self.name)
    klasses[t] = Tester

class ReferenceFrame(Entity):
    def write(self, f, parent):
        parent_label = parent.safe_name() if parent else "global"
        vectors = list()
        for r in [self.linear_rate, self.angular_rate]:
            vectors.append(Vector([0., 0., r if r is not None else 0.]))
        location = self.objects[0].matrix_world.translation - (parent.objects[0].matrix_world.translation if parent else Vector([0., 0., 0.]))
        rot = self.objects[0].matrix_world.to_quaternion().to_matrix()
        rot_parent = parent.objects[0].matrix_world.to_quaternion().to_matrix() if parent else rot
        orientation = rot_parent.transposed()*rot if parent else rot
        f.write("reference: " + self.safe_name() + ",\n" + "\treference, " + parent_label + ", ")
        write_vector(f, rot_parent.transposed()*location if parent else location, ",\n")
        f.write("\treference, " + parent_label + ", matr,\n")
        write_matrix(f, orientation, "\t\t")
        f.write(",\n\treference, " + parent_label + ", ")
        write_vector(f, orientation*vectors[0], ",\n")
        f.write("\treference, " + parent_label + ", ")
        write_vector(f, orientation*vectors[1], ";\n")
    def remesh(self):
        RhombicPyramid(self.objects[0])

class ReferenceFrameOperator(Base):
    bl_label = "Reference frame"
    linear_rate = bpy.props.PointerProperty(type = BPY.Float)
    angular_rate = bpy.props.PointerProperty(type = BPY.Float)
    @classmethod
    def poll(self, context):
        frames = copy(database.input_card.filter("Reference frame"))
        if self.bl_idname.startswith(root_dot + "e_"):
            frames.pop(context.scene.input_card_index)
        selected = SelectedObjects(context)
        overlapped = False in [set(selected[1:]).isdisjoint(set(f.objects[1:])) for f in frames]
        duplicate = True in [selected[0] == f.objects[0] for f in frames if hasattr(f, "objects")]
        if len(selected) < 2 or overlapped or duplicate:
            return False
        frame_objects = [f.objects for f in frames]
        head, hold = selected[0], None
        while frame_objects and head != hold:
            hold = head
            for objects in frame_objects:
                if head in objects[1:]:
                    head = objects[0]
                    frame_objects.remove(objects)
        return head not in selected[1:]
    def assign(self, context):
        self.linear_rate.assign(self.entity.linear_rate)
        self.angular_rate.assign(self.entity.angular_rate)
    def store(self, context):
        self.entity.linear_rate = self.linear_rate.store()
        self.entity.angular_rate = self.angular_rate.store()
        self.entity.objects = SelectedObjects(context)
    def draw(self, context):
        layout = self.layout
        self.linear_rate.draw(layout, "Linear rate", "Set")
        self.angular_rate.draw(layout, "Angular rate", "Set")
    def check(self, context):
        return True in [v.check(context) for v in [self.linear_rate, self.angular_rate]]
    def create_entity(self):
        return ReferenceFrame(self.name)

klasses[ReferenceFrameOperator.bl_label] = ReferenceFrameOperator

class Set(Entity):
    def write(self, f):
        modifiers = list()
        if self.ifndef:
            modifiers.append("ifndef")
        if self.const:
            modifiers.append("const")
        modifiers.append
        f.write("set: " +
            ("ifndef " if self.ifndef else "") +
            ("const " if self.const else "") +
            self.value_type + " " + self.safe_name() + ((" = " + self.value) if self.value else "") + ";\n")

class SetOperator(Base):
    bl_label = "Set"
    ifndef = bpy.props.BoolProperty(name="If not defined", description="Define only if not already defined", default=False)
    const = bpy.props.BoolProperty(name="Constant", description="Constant value", default=False)
    value_type = bpy.props.EnumProperty(items=[("bool", "Boolean", ""), ("integer", "Integer", ""), ("real", "Real", ""), ("string", "String", "")], name="Type", default="real")
    value = bpy.props.StringProperty(name="Value", description="Set value", default="")
    def assign(self, context):
        self.ifndef = self.entity.ifndef
        self.const = self.entity.const
        self.value_type = self.entity.value_type
        self.value = self.entity.value
    def store(self, context):
        self.entity.ifndef = self.ifndef
        self.entity.const = self.const
        self.entity.value_type = self.value_type
        self.entity.value = self.value
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "value")
        row = layout.row()
        row.prop(self, "value_type", text="")
        row.prop(self, "const")
        row.prop(self, "ifndef")
    def create_entity(self):
        return Set(self.name)

klasses[SetOperator.bl_label] = SetOperator

bundle = Bundle(tree, Base, klasses, database.input_card)
