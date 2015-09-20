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
    imp.reload(aerodynamic_types, beam_types)
    imp.reload(force_types, genel_types)
    imp.reload(joint_types)
    imp.reload(environment_types)
    imp.reload(node_types)
    imp.reload(rigid_body_types)
    imp.reload(structural_static_types)
    imp.reload(structural_dynamic_types)
else:
    import bpy
    from .common import Common, aerodynamic_types, beam_types, force_types, genel_types, joint_types, environment_types, node_types, rigid_body_types, structural_static_types, structural_dynamic_types, safe_name
    import gc

from io import BytesIO
import pickle
from base64 import b64encode, b64decode
from mathutils import Vector
from collections import deque

class Pickler(pickle.Pickler):
    def persistent_id(self, obj):
        return repr(obj) if repr(obj).startswith("bpy.data") else None

class Unpickler(pickle.Unpickler):
    def persistent_load(self, pid):
        if not pid.startswith("bpy.data") and len(pid.split()) == 1:
            raise pickle.UnpicklingError(pid + " is forbidden")
        exec("id_data = " + pid)
        name = locals()["id_data"].mbdyn_name
        exec("id_data = " + pid.split("[")[0] + "[\"" + name + "\"]")
        return locals()["id_data"]
    def find_class(self, module, name):
        if module.startswith("BlenderAndMBDyn"):
            module = ".".join((__package__, module.split(".", 1)[1]))
        elif module == "builtins" and name in ("exec", "eval"):
            raise pickle.UnpicklingError("global " + ".".join((module, name)) + " is forbidden")
        return super().find_class(module, name)

bpy.types.Scene.pickled_database = bpy.props.StringProperty()

class EntityLookupError(LookupError):
    pass

class Entities(list):
    def filter(self, type_name, obj=None):
        return [e for e in self if e.type == type_name and 
            (not obj or (hasattr(e, "objects") and e.objects[0] == obj))]
    def get_by_name(self, name):
        if name != "New":
            for e in self:
                if e.name == name:
                    return e
        raise EntityLookupError
    def move(self, i, j):
        self[i], self[j] = self[j], self[i]

class Database(Common):
    def __init__(self):
        self.element = Entities()
        self.drive = Entities()
        self.driver = Entities()
        self.friction = Entities()
        self.shape = Entities()
        self.function = Entities()
        self.ns_node = Entities()
        self.constitutive = Entities()
        self.matrix = Entities()
        self.input_card = Entities()
        self.definition = Entities()
        self.simulator = Entities()
        self.node = list()
        self.rigid_dict = dict()
        self.dummy_dict = dict()
        self.structural_dynamic_nodes = set()
        self.structural_static_nodes = set()
        self.structural_dummy_nodes = set()
        self.clear()
    def clear(self):
        self.element.clear()
        self.drive.clear()
        self.driver.clear()
        self.friction.clear()
        self.shape.clear()
        self.function.clear()
        self.ns_node.clear()
        self.constitutive.clear()
        self.matrix.clear()
        self.input_card.clear()
        self.definition.clear()
        self.simulator.clear()
        self.node.clear()
        self.rigid_dict.clear()
        self.dummy_dict.clear()
        self.structural_dynamic_nodes.clear()
        self.structural_static_nodes.clear()
        self.structural_dummy_nodes.clear()
        self.scene = None
    def all_entities(self):
        return (self.element + self.drive + self.driver + self.friction + self.shape + self.function +
            self.ns_node + self.constitutive + self.matrix + self.input_card + self.definition + self.simulator)
    def entities_using(self, objects):
        set_objects = set(objects)
        entities = list()
        for entity in self.all_entities():
            if hasattr(entity, "objects"):
                if not set_objects.isdisjoint(set(entity.objects)):
                    entities.append(entity)
        entities.extend([e for e in self.element if (e.type == 'Driven' and e.element in entities)])
        return entities
    def entities_originating_from(self, objects):
        entities = list()
        for entity in self.all_entities():
            if hasattr(entity, "objects"):
                if entity.objects[0] in objects:
                    entities.append(entity)
        entities.extend([e for e in self.element if (e.type == 'Driven' and e.element in entities)])
        return entities
    def users_of(self, entity):
        ret = list()
        for e in self.all_entities():
            if True in [((entity == v) or (isinstance(v, list) and entity in v)) for v in vars(e).values()]:
                ret.append(e)
        return ret
    def pickle(self):
        if not self.scene:
            self.scene = bpy.context.scene
        bpy.context.scene.mbdyn_name = bpy.context.scene.name
        for obj in bpy.context.scene.objects:
            obj.mbdyn_name = obj.name
        with BytesIO() as f:
            p = Pickler(f)
            p.dump(self)
            self.scene.pickled_database = b64encode(f.getvalue()).decode()
            del p
        gc.collect()
    def unpickle(self):
        self.clear()
        if bpy.context.scene.pickled_database:
            with BytesIO(b64decode(bpy.context.scene.pickled_database.encode())) as f:
                up = Unpickler(f)
                database = up.load()
                for k, v in vars(database).items():
                    if type(v) in [list, Entities]:
                        self.__dict__[k].extend(v)
                        #v.clear()
                    elif type(v) in [dict, set]:
                        self.__dict__[k].update(v)
                        #v.clear()
                    else:
                        self.__dict__[k] = v
                del up, database
        gc.collect()
    def replace(self):
        self.pickle()
        self.unpickle()
    def write_indexes(self, f):
        self.structural_dynamic_nodes.clear()
        self.structural_static_nodes.clear()
        self.structural_dummy_nodes.clear()
        self.rigid_dict = {e.objects[0] : e.objects[1] for e in self.element.filter("Rigid offset")}
        nodes = set()
        for e in (e for e in self.element + self.drive if hasattr(e, "objects")):
            ob = self.rigid_dict[e.objects[0]] if e.objects[0] in self.rigid_dict else e.objects[0]
            nodes |= set([ob])
            if e.type in structural_dynamic_types:
                self.structural_dynamic_nodes |= set([ob])
            elif e.type in structural_static_types:
                self.structural_static_nodes |= set([ob])
            elif e.type == "Dummy":
                self.structural_dummy_nodes |= set([ob])
                dummy_dict[ob] = e.objects[1]
        self.structural_static_nodes -= self.structural_dynamic_nodes | self.structural_dummy_nodes
        self.node.clear()
        self.node.extend(sorted(nodes, key=lambda x: x.name))
    def write_control(self, f, context):
        structural_node_count = len(
            self.structural_static_nodes | self.structural_dynamic_nodes | self.structural_dummy_nodes)
        joint_count = len([e for e in self.element if e.type in joint_types])
        force_count = len([e for e in self.element if e.type in force_types])
        rigid_body_count = len([e for e in self.element if e.type in rigid_body_types])
        aerodynamic_element_count = len([e for e in self.element if e.type in aerodynamic_types])
        rotor_count = len([e for e in self.element if e.type in ["Rotor"]])
        genel_count = len([e for e in self.element if e.type in genel_types])
        beam_count = len([e for e in self.element if e.type in beam_types and not hasattr(e, "consumer")])
        air_properties = bool([e for e in self.element if e.type in ["Air properties"]])
        gravity = bool([e for e in self.element if e.type in ["Gravity"]])
        self.file_driver_count = 0
        bailout_upper = False
        upper_bailout_time = 0.0
        for driver in self.driver:
            driver.columns = list()
        """
        for drive in self.drive:
            if drive.type == "File drive":
                drive.links[0].columns.append(drive)
        """
        for driver in self.driver:
            if driver.columns:
                self.file_driver_count += 1
                if driver.bailout_upper:
                    if driver.filename:
                        name = driver.filename.replace(" ", "")
                    else:
                        name = driver.name.replace(" ", "")
                    command = "tail -n 1 " + os.path.splitext(context.blend_data.filepath)[0] + ".echo_" + name + " | awk '{print $1}'"
                    f1 = TemporaryFile()
                    call(command, shell=True, stdout=f1)
                    try:
                        f1.seek(0)
                        upper_bailout_time = min(upper_bailout_time, float(f1.read()) - 1e-3)
                    except:
                        pass
                    f1.close()
        electric_node_count = len([e for e in self.ns_node if e.type in ["Electric"]])
        abstract_node_count = len([e for e in self.ns_node if e.type in ["Abstract"]])
        hydraulic_node_count = len([e for e in self.ns_node if e.type in ["Hydraulic"]])
        #parameter_node_count = len([e for e in self.ns_node if e.type in ["Parameter"]])
        if structural_node_count:
            f.write("\tstructural nodes: " + str(structural_node_count) + ";\n")
        if electric_node_count:
            f.write("\telectric nodes: " + str(electric_node_count) + ";\n")
        if abstract_node_count:
            f.write("\tabstract nodes: " + str(abstract_node_count) + ";\n")
        if hydraulic_node_count:
            f.write("\thydraulic nodes: " + str(hydraulic_node_count) + ";\n")
        if joint_count:
            f.write("\tjoints: " + str(joint_count) + ";\n")
        if force_count:
            f.write("\tforces: " + str(force_count) + ";\n")
        if genel_count:
            f.write("\tgenels: " + str(genel_count) + ";\n")
        if beam_count:
            f.write("\tbeams: " + str(beam_count) + ";\n")
        if rigid_body_count:
            f.write("\trigid bodies: " + str(rigid_body_count) + ";\n")
        if air_properties:
            f.write("\tair properties;\n")
        if gravity:
            f.write("\tgravity;\n")
        if aerodynamic_element_count:
            f.write("\taerodynamic elements: " + str(aerodynamic_element_count) + ";\n")
        if rotor_count:
            f.write("\trotors: " + str(rotor_count) + ";\n")
        if self.file_driver_count:
            f.write("\tfile drivers: " + str(self.file_driver_count) + ";\n")
    def write_structural_node(self, f, structural_type, node, frame):
        f.write("\tstructural: " + ", ".join([safe_name(node.name), structural_type]) + ",\n")
        frame_label = frame.safe_name() if frame else "global"
        location, orientation = node.matrix_world.translation, node.matrix_world.to_quaternion().to_matrix()
        if frame:
            location = location - frame.objects[0].matrix_world.translation
            orientation = frame.objects[0].matrix_world.to_quaternion().to_matrix().transposed()*orientation
        f.write("\t\treference, " + frame_label + ", ")
        self.write_vector(f, location, ",\n")
        f.write("\t\treference, " + frame_label + ", matr,\n")
        self.write_matrix(f, orientation, "\t"*3)
        f.write(",\n" +
            "\t\treference, " + frame_label + ", null,\n" +
            "\t\treference, " + frame_label + ", null;\n")
    def write(self, f):
        set_cards = self.input_card.filter("Set")
        if set_cards:
            f.write("\n")
            for set_card in set_cards:
                set_card.write(f)
        frame_for, frames, parent_of = dict(), list(), dict()
        reference_frames = self.input_card.filter("Reference frame")
        for frame in reference_frames:
            frame_for.update({ob : frame for ob in frame.objects[1:]})
            frames.append(frame)
            parent_of.update({frame : parent for parent in reference_frames if frame.objects[0] in parent.objects[1:]})
        frames_to_write = list()
        while frames:
            frame = frames.pop()
            if frame in parent_of and parent_of[frame] in frames:
                frames.appendleft(frame)
            else:
                frames_to_write.append(frame)
        if frames_to_write:
            f.write("\n")
            for i, frame in enumerate(sorted(frames_to_write, key=lambda x: x.name)):
                f.write("set: const integer " + safe_name(frame.name) + " = " + str(i) + ";\n")
            for frame in frames_to_write:
                frame.write(f, parent_of[frame] if frame in parent_of else None)
        if self.node:
            f.write("\n")
            for i, node in enumerate(self.node):
                f.write("set: const integer " + safe_name(node.name) + " = " + str(i) + ";\n")
            f.write("begin: nodes;\n")
            for node in self.structural_static_nodes:
                self.write_structural_node(f, "static", node, frame_for[node] if node in frame_for else None)
            for node in self.structural_dynamic_nodes:
                self.write_structural_node(f, "dynamic", node, frame_for[node] if node in frame_for else None)
            for node in self.structural_dummy_nodes:
                base_node = dummy_dict[node]
                rot = base_node.matrix_world.to_quaternion().to_matrix()
                globalV = node.matrix_world.translation - base_node.matrix_world.translation
                localV = rot*globalV
                rotT = node.matrix_world.to_quaternion().to_matrix()
                f.write("\tstructural: " + str(self.node.index(node)) + ", dummy,\n\t\t" +
                    str(self.node.index(base_node)) + ", offset,\n\t\t\t")
                self.write_vector(f, localV, ",\n\t\t\tmatr,\n")
                self.write_matrix(f, rot*rotT, "\t\t\t\t")
                f.write(";\n")
            """
            for i, ns_node in enumerate(self.ns_node):
                if ns_node.type == "Electric":
                    f.write("\telectric: " + str(i) + ", value, " + str(ns_node._args[0]))
                    if ns_node._args[1]: f.write(", derivative, " + str(ns_node._args[2]))
                    f.write(";\n")
                if ns_node.type == "Abstract":
                    f.write("\tabstract: " + str(i) + ", value, " + str(ns_node._args[0]))
                    if ns_node._args[1]: f.write(", differential, " + str(ns_node._args[2]))
                    f.write(";\n")
                if ns_node.type == "Hydraulic":
                    f.write("\thydraulic: " + str(i) + ", value, " + str(ns_node._args[0]) + ";\n")
            """
            f.write("end: nodes;\n")
        if self.file_driver_count:
            f.write("\nbegin: drivers;\n")
            for driver in sorted(self.driver, key=lambda x: x.name):
                driver.write(f)
            f.write("end: drivers;\n")
        self.drive_indenture = 1
        if self.function:
            f.write("\n")
            for function in sorted(self.function, key=lambda x: x.name):
                function.write(f)
        if self.constitutive:
            f.write("\n")
            for i, constitutive in enumerate(sorted(self.constitutive, key=lambda x: x.name)):
                f.write("set: const integer " + constitutive.safe_name() + " = " + str(i + 1) + ";\n")
            for i, constitutive in enumerate(self.constitutive):
                f.write("constitutive law: " + ", ".join([constitutive.safe_name(), constitutive.dimension[0], constitutive.string()]) + ";\n")
        if self.drive:
            f.write("\n")
            for i, drive in enumerate(sorted(self.drive, key=lambda x: x.name)):
                f.write("set: const integer " + drive.safe_name() + " = " + str(i) + ";\n")
            for i, drive in enumerate(self.drive):
                f.write("drive caller: " + ", ".join([drive.safe_name(), drive.string()]) + ";\n")
        if self.element:
            f.write("\n")
            for i, element in enumerate(sorted(self.element, key=lambda x: x.name)):
                f.write("set: const integer " + element.safe_name() + " = " + str(i) + ";\n")
            self.drive_indenture = 2
            f.write("begin: elements;\n")
            try:
                for element_type in aerodynamic_types + beam_types + ["Body"] + force_types + genel_types + joint_types + ["Rotor"] + environment_types + ["Driven"]:
                    for element in self.element:
                        if element.type == element_type:
                            element.write(f)
            except Exception as e:
                print(e)
                f.write(str(e) + "\n")
            f.write("end: elements;\n")
        del self.drive_indenture
