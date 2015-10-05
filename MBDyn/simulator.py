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
else:
    from .base import bpy, BPY, root_dot, database, Operator, Entity, Bundle
    from .common import FORMAT, aerodynamic_types, beam_types, force_types, genel_types, joint_types, environment_types, node_types, rigid_body_types, structural_static_types, structural_dynamic_types, safe_name, write_vector, write_matrix
    from mathutils import Matrix
    import subprocess
    from tempfile import TemporaryFile
    import os


types = ["Initial value"]

tree = ["Simulator", types]

klasses = dict()

class Base(Operator):
    bl_label = "Simulators"
    @classmethod
    def poll(cls, context):
        return True
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.simulator_uilist = bpy.props.CollectionProperty(type = ListItem)
        def update(self, context):
            if database.simulator and self.simulator_index < len(database.simulator):
                exec("bpy.ops." + root_dot + "save('INVOKE_DEFAULT')")
        bpy.types.Scene.simulator_index = bpy.props.IntProperty(default=-1, update=update)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.simulator_uilist
        del bpy.types.Scene.simulator_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.simulator_index, context.scene.simulator_uilist
    def set_index(self, context, value):
        context.scene.simulator_index = value
    def prereqs(self, context):
        pass
    def draw_panel_post(self, context, layout):
        if context.scene.dirty_simulator:
            layout.label("Choose a simulator")
        else:
            layout.operator(root_dot + "simulate")
            if context.scene.clean_log:
                layout.operator(root_dot + "animate")

for t in types:
    class Tester(Base):
        bl_label = t
        @classmethod
        def poll(cls, context):
            return False
        def create_entity(self):
            return Entity(self.name)
    klasses[t] = Tester

class InitialValue(Entity):
    def write_input_file(self, context, directory):
        def write_structural_node(f, structural_type, node, frame):
            f.write("\tstructural: " + ", ".join([safe_name(node.name), structural_type]) + ",\n")
            frame_label = frame.safe_name() if frame else "global"
            location, orientation = node.matrix_world.translation, node.matrix_world.to_quaternion().to_matrix()
            if frame:
                location = location - frame.objects[0].matrix_world.translation
                orientation = frame.objects[0].matrix_world.to_quaternion().to_matrix().transposed()*orientation
            f.write("\t\treference, " + frame_label + ", ")
            write_vector(f, location, ",\n")
            f.write("\t\treference, " + frame_label + ", matr,\n")
            write_matrix(f, orientation, "\t"*3)
            f.write(",\n" +
                "\t\treference, " + frame_label + ", null,\n" +
                "\t\treference, " + frame_label + ", null;\n")
        with open(os.path.join(directory, context.scene.name + ".mbd"), "w") as f:
            f.write("# MBDyn v1.6 input file generated using BlenderAndMBDyn v2.0\n\n")
            frame_for, frames, parent_of = dict(), list(), dict()
            reference_frames = database.input_card.filter("Reference frame")
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
                f.write("# Frame names:\n")
                for i, frame in enumerate(sorted(frames_to_write, key=lambda x: x.name)):
                    f.write("set: const integer " + safe_name(frame.name) + " = " + str(i) + ";\n")
                f.write("\n")
            else:
                f.write("# Frame names: None\n")
            nodes = set()
            dummy_dict = dict()
            structural_dynamic_nodes = set()
            structural_static_nodes = set()
            structural_dummy_nodes = set()
            database.rigid_dict = {e.objects[0] : e.objects[1] for e in database.element.filter("Rigid offset")}
            names = [e.name for e in database.all_entities()]
            for e in (e for e in database.element + database.drive if hasattr(e, "objects")):
                ob = database.rigid_dict[e.objects[0]] if e.objects[0] in database.rigid_dict else e.objects[0]
                if ob.name in names:
                    ob.name = "Node"
                nodes |= set([ob])
                if e.type in structural_dynamic_types:
                    structural_dynamic_nodes |= set([ob])
                elif e.type in structural_static_types:
                    structural_static_nodes |= set([ob])
                elif e.type == "Dummy":
                    structural_dummy_nodes |= set([ob])
                    dummy_dict[ob] = e.objects[1]
            structural_static_nodes -= structural_dynamic_nodes | structural_dummy_nodes
            database.node.clear()
            database.node.extend(sorted(nodes, key=lambda x: x.name))
            if database.node:
                f.write("# Node names:\n")
                for i, node in enumerate(database.node):
                    f.write("set: const integer " + safe_name(node.name) + " = " + str(i) + ";\n")
                f.write("\n")
            else:
                f.write("# Node names: None\n\n")
            if database.element:
                f.write("# Element names:\n")
                for i, element in enumerate(sorted(database.element, key=lambda x: x.name)):
                    f.write("set: const integer " + element.safe_name() + " = " + str(i) + ";\n")
                f.write("\n")
            else:
                f.write("# Element names: None\n\n")
            if database.drive:
                f.write("# Drive names:\n")
                for i, drive in enumerate(sorted(database.drive, key=lambda x: x.name)):
                    f.write("set: const integer " + drive.safe_name() + " = " + str(i) + ";\n")
                f.write("\n")
            else:
                f.write("# Drive names: None\n\n")
            if database.constitutive:
                f.write("# Constitutive names:\n")
                for i, constitutive in enumerate(sorted(database.constitutive, key=lambda x: x.name)):
                    f.write("set: const integer " + constitutive.safe_name() + " = " + str(i) + ";\n")
                f.write("\n")
            else:
                f.write("# Constitutive names: None\n\n")
            set_cards = database.input_card.filter("Set")
            if set_cards:
                f.write("# Parameters:\n")
                for set_card in set_cards:
                    set_card.write(f)
                f.write("\n")
            else:
                f.write("# Parameters: None\n\n")
            structural_node_count = len(structural_static_nodes | structural_dynamic_nodes | structural_dummy_nodes)
            joint_count = len([e for e in database.element if e.type in joint_types])
            force_count = len([e for e in database.element if e.type in force_types])
            rigid_body_count = len([e for e in database.element if e.type in rigid_body_types])
            aerodynamic_element_count = len([e for e in database.element if e.type in aerodynamic_types])
            rotor_count = len([e for e in database.element if e.type in ["Rotor"]])
            genel_count = len([e for e in database.element if e.type in genel_types])
            beam_count = len([e for e in database.element if e.type in beam_types and not hasattr(e, "consumer")])
            air_properties = bool([e for e in database.element if e.type in ["Air properties"]])
            gravity = bool([e for e in database.element if e.type in ["Gravity"]])
            file_driver_count = 0
            bailout_upper = False
            upper_bailout_time = 0.0
            for driver in database.driver:
                driver.columns = list()
            """
            for drive in database.drive:
                if drive.type == "File drive":
                    drive.links[0].columns.append(drive)
            """
            for driver in database.driver:
                if driver.columns:
                    file_driver_count += 1
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
#            electric_node_count = len([e for e in database.ns_node if e.type in ["Electric"]])
#            abstract_node_count = len([e for e in database.ns_node if e.type in ["Abstract"]])
#            hydraulic_node_count = len([e for e in database.ns_node if e.type in ["Hydraulic"]])
#            parameter_node_count = len([e for e in database.ns_node if e.type in ["Parameter"]])
            f.write(
                "begin: data" +
                ";\n\tproblem: initial value" +
                ";\nend: data" +
                ";\n\nbegin: initial value" +
                ";\n\tinitial time: " + (BPY.FORMAT(self.initial_time) if self.initial_time is not None else "0") +
                ";\n\tfinal time: " + (BPY.FORMAT(self.final_time) if self.final_time is not None else "forever") +
                ";\n")
            for a in [self.general_data, self.method, self.nonlinear_solver, self.eigenanalysis, self.abort_after, self.linear_solver, self.dummy_steps, self.output_data, self.real_time]:
                if a is not None:
                    a.write(f)
            f.write("end: initial value;\n" +
                "\nbegin: control data;\n")
            for a in [self.assembly, self.job_control, self.default_output, self.default_aerodynamic_output, self.default_beam_output]:
                if a is not None:
                    a.write(f)
            if structural_node_count:
                f.write("\tstructural nodes: " + str(structural_node_count) + ";\n")
            """
            if electric_node_count:
                f.write("\telectric nodes: " + str(electric_node_count) + ";\n")
            if abstract_node_count:
                f.write("\tabstract nodes: " + str(abstract_node_count) + ";\n")
            if hydraulic_node_count:
                f.write("\thydraulic nodes: " + str(hydraulic_node_count) + ";\n")
            """
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
            if file_driver_count:
                f.write("\tfile drivers: " + str(file_driver_count) + ";\n")
            f.write("end: control data;\n")
            if frames_to_write:
                f.write("\n")
                for frame in frames_to_write:
                    frame.write(f, parent_of[frame] if frame in parent_of else None)
            if database.node:
                f.write("\nbegin: nodes;\n")
                for node in structural_static_nodes:
                    write_structural_node(f, "static", node, frame_for[node] if node in frame_for else None)
                for node in structural_dynamic_nodes:
                    write_structural_node(f, "dynamic", node, frame_for[node] if node in frame_for else None)
                for node in structural_dummy_nodes:
                    base_node = dummy_dict[node]
                    rot = base_node.matrix_world.to_quaternion().to_matrix()
                    globalV = node.matrix_world.translation - base_node.matrix_world.translation
                    localV = rot*globalV
                    rotT = node.matrix_world.to_quaternion().to_matrix()
                    f.write("\tstructural: " + str(database.node.index(node)) + ", dummy,\n\t\t" +
                        str(database.node.index(base_node)) + ", offset,\n\t\t\t")
                    write_vector(f, localV, ",\n\t\t\tmatr,\n")
                    write_matrix(f, rot*rotT, "\t\t\t\t")
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
            if file_driver_count:
                f.write("\nbegin: drivers;\n")
                for driver in sorted(database.driver, key=lambda x: x.name):
                    driver.write(f)
                f.write("end: drivers;\n")
            if database.function:
                f.write("\n# Functions:\n")
                for function in sorted(database.function, key=lambda x: x.name):
                    function.write(f)
            if database.drive:
                f.write("\n# Drives:\n")
                for drive in database.drive:
                    f.write("drive caller: " + ", ".join([drive.safe_name(), drive.string()]) + ";\n")
            if database.constitutive:
                f.write("\n# Constitutives:\n")
                for constitutive in database.constitutive:
                    f.write("constitutive law: " + ", ".join([constitutive.safe_name(), constitutive.dimension[0], constitutive.string()]) + ";\n")
            if database.element:
                f.write("\nbegin: elements;\n")
                try:
                    for element_type in aerodynamic_types + beam_types + ["Body"] + force_types + genel_types + joint_types + ["Rotor"] + environment_types + ["Driven"]:
                        for element in database.element:
                            if element.type == element_type:
                                element.write(f)
                except Exception as e:
                    print(e)
                    f.write(str(e) + "\n")
                f.write("end: elements;\n")
            del database.rigid_dict
            del dummy_dict

class InitialValueOperator(Base):
    bl_label = "Initial value"
    mbdyn_path = bpy.props.PointerProperty(type=BPY.Str)
    initial_time = bpy.props.PointerProperty(type=BPY.Float)
    final_time = bpy.props.PointerProperty(type=BPY.Float)
    general_data = bpy.props.PointerProperty(type=BPY.Definition)
    method = bpy.props.PointerProperty(type=BPY.Definition)
    nonlinear_solver = bpy.props.PointerProperty(type=BPY.Definition)
    eigenanalysis = bpy.props.PointerProperty(type=BPY.Definition)
    abort_after = bpy.props.PointerProperty(type=BPY.Definition)
    linear_solver = bpy.props.PointerProperty(type=BPY.Definition)
    dummy_steps = bpy.props.PointerProperty(type=BPY.Definition)
    output_data = bpy.props.PointerProperty(type=BPY.Definition)
    real_time = bpy.props.PointerProperty(type=BPY.Definition)
    assembly = bpy.props.PointerProperty(type=BPY.Definition)
    job_control = bpy.props.PointerProperty(type=BPY.Definition)
    default_output = bpy.props.PointerProperty(type=BPY.Definition)
    default_aerodynamic_output = bpy.props.PointerProperty(type=BPY.Definition)
    default_beam_output = bpy.props.PointerProperty(type=BPY.Definition)
    def prereqs(self, context):
        self.mbdyn_path.assign(BPY.mbdyn_path)
        self.final_time.select, self.final_time.value = True, 10.0
        self.general_data.type = "General data"
        self.general_data.mandatory = True
        self.general_data_exists(context)
        self.method.type = "Method"
        self.nonlinear_solver.type = "Nonlinear solver"
        self.eigenanalysis.type = "Eigenanalysis"
        self.abort_after.type = "Abort after"
        self.linear_solver.type = "Linear solver"
        self.dummy_steps.type = "Dummy steps"
        self.output_data.type = "Output data"
        self.output_data.mandatory = True
        self.output_data_exists(context)
        self.real_time.type = "Real time"
        self.assembly.type = "Assembly"
        self.job_control.type = "Job control"
        self.job_control.mandatory = True
        self.job_control_exists(context)
        self.default_output.type = "Default output"
        self.default_output.mandatory = True
        self.default_output_exists(context)
        self.default_aerodynamic_output.type = "Default aerodynamic output"
        self.default_beam_output.type = "Default beam output"
    def assign(self, context):
        self.mbdyn_path.assign(self.entity.mbdyn_path)
        self.initial_time.assign(self.entity.initial_time)
        self.final_time.assign(self.entity.final_time)
        self.general_data.assign(self.entity.general_data)
        self.method.assign(self.entity.method)
        self.nonlinear_solver.assign(self.entity.nonlinear_solver)
        self.eigenanalysis.assign(self.entity.eigenanalysis)
        self.abort_after.assign(self.entity.abort_after)
        self.linear_solver.assign(self.entity.linear_solver)
        self.dummy_steps.assign(self.entity.dummy_steps)
        self.output_data.assign(self.entity.output_data)
        self.real_time.assign(self.entity.real_time)
        self.assembly.assign(self.entity.assembly)
        self.job_control.assign(self.entity.job_control)
        self.default_output.assign(self.entity.default_output)
        self.default_aerodynamic_output.assign(self.entity.default_aerodynamic_output)
        self.default_beam_output.assign(self.entity.default_beam_output)
    def store(self, context):
        self.entity.mbdyn_path = BPY.mbdyn_path = self.mbdyn_path.store()
        self.entity.initial_time = self.initial_time.store()
        self.entity.final_time = self.final_time.store()
        self.entity.general_data = self.general_data.store()
        self.entity.method = self.method.store()
        self.entity.nonlinear_solver = self.nonlinear_solver.store()
        self.entity.eigenanalysis = self.eigenanalysis.store()
        self.entity.abort_after = self.abort_after.store()
        self.entity.linear_solver = self.linear_solver.store()
        self.entity.dummy_steps = self.dummy_steps.store()
        self.entity.output_data = self.output_data.store()
        self.entity.real_time = self.real_time.store()
        self.entity.assembly = self.assembly.store()
        self.entity.job_control = self.job_control.store()
        self.entity.default_output = self.default_output.store()
        self.entity.default_aerodynamic_output = self.default_aerodynamic_output.store()
        self.entity.default_beam_output = self.default_beam_output.store()
    def pre_finished(self, context):
        exec("bpy.ops." + root_dot + "save('INVOKE_DEFAULT')")
    def draw(self, context):
        layout = self.layout
        self.mbdyn_path.draw(layout, "MBDyn path", "Set")
        self.initial_time.draw(layout, "Initial time")
        self.final_time.draw(layout, "Final time")
        self.general_data.draw(layout, "General data")
        self.method.draw(layout, "Method", "Set")
        self.nonlinear_solver.draw(layout, "Nonlinear solver", "Set")
        self.eigenanalysis.draw(layout, "Eigenanalysis", "Set")
        self.abort_after.draw(layout, "Abort after", "Set")
        self.linear_solver.draw(layout, "Linear solver", "Set")
        self.dummy_steps.draw(layout, "Dummy steps", "Set")
        self.output_data.draw(layout, "Output data", "Set")
        self.real_time.draw(layout, "Real time", "Set")
        self.assembly.draw(layout, "Assembly", "Set")
        self.job_control.draw(layout, "Job control", "Set")
        self.default_output.draw(layout, "Default output", "Set")
        self.default_aerodynamic_output.draw(layout, "Default aerodynamic output", "Set")
        self.default_beam_output.draw(layout, "Default beam output", "Set")
    def check(self, context):
        return (True in [x.check(context) for x in [self.mbdyn_path, self.initial_time, self.final_time, self.general_data, self.method, self.nonlinear_solver, self.eigenanalysis, self.abort_after, self.linear_solver, self.dummy_steps, self.output_data, self.real_time, self.assembly, self.default_output, self.default_aerodynamic_output, self.default_beam_output]])
    def create_entity(self):
        return InitialValue(self.name)

klasses[InitialValueOperator.bl_label] = InitialValueOperator

class Save(bpy.types.Operator, Base):
    bl_idname = root_dot + "save"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_label = "Save Blender File"
    filter_glob = bpy.props.StringProperty(
            default="*.blend",
            options={'HIDDEN'},
            )
    filepath = bpy.props.StringProperty()
    def invoke(self, context, event):
        if not context.blend_data.filepath:
            self.filepath = "untitled.blend"
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        self.filepath = context.blend_data.filepath
        return self.execute(context)
    def execute(self, context):
        directory = os.path.splitext(self.filepath)[0]
        if not os.path.exists(directory):
            os.mkdir(directory)
        database.simulator[context.scene.simulator_index].write_input_file(context, directory)
        bpy.ops.wm.save_mainfile(filepath=self.filepath)
        context.scene.dirty_simulator = False
        context.scene.clean_log = False
        return{'FINISHED'}
BPY.klasses.append(Save)

class Simulate(bpy.types.Operator, Base):
    bl_idname = root_dot + "simulate"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_label = "Run simulation"
    bl_description = "Run MBDyn for the input file"
    def modal(self, context, event):
        wm = context.window_manager
        poll = self.process.poll()
        if poll == None:
            output = subprocess.check_output(("tail", "-n", "1", self.out_file))
            if output and 2 < len(output.split()):
                percent = 100.*(1.-(self.t_final - float(output.split()[2]))/self.t_range)
                wm.progress_update(percent)
            return {'PASS_THROUGH'}
        self.f.seek(0)
        s = self.f.read().decode()
        self.f.close()
        if poll:
            self.report({'ERROR'}, s)
        else:
            context.scene.clean_log = True
            BPY.plot_data.clear()
            if s:
                self.report({'INFO'}, s)
        wm.event_timer_remove(self.timer)
        wm.progress_end()
        return {'FINISHED'}
    def execute(self, context):
        sim = database.simulator[context.scene.simulator_index]
        directory = os.path.splitext(context.blend_data.filepath)[0]
        command = [sim.mbdyn_path if sim.mbdyn_path is not None else "mbdyn", "-s", "-f", os.path.join(directory, context.scene.name + ".mbd")]
        print(" ".join(command))
        self.f = TemporaryFile()
        self.process = subprocess.Popen(command, stdout=self.f, stderr=self.f)
        self.out_file = os.path.join(directory, context.scene.name + ".out")
        self.t_final = sim.final_time if sim.final_time is not None else float("inf")
        self.t_range = self.t_final - (sim.initial_time if sim.initial_time is not None else 0.0)
        subprocess.call(("touch", self.out_file))
        wm = context.window_manager
        wm.progress_begin(0., 100.)
        self.timer = wm.event_timer_add(0.01, context.window)
        wm.modal_handler_add(self)
        return{'RUNNING_MODAL'}
BPY.klasses.append(Simulate)

class Animate(bpy.types.Operator, Base):
    bl_idname = root_dot + "animate"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_label = "Animate objects"
    bl_description = "Import each node's position and orientation into Blender keyframes starting at the next frame"
    steps = bpy.props.IntProperty(name="MBDyn steps between Blender keyframes", default=1, min=1)
    def invoke(self, context, event):
        scene = context.scene
        directory = os.path.splitext(context.blend_data.filepath)[0]
        for node in database.node:
            for data_path in "location rotation_euler".split():
                node.keyframe_insert(data_path)
        with open(os.path.join(directory, context.scene.name + ".mov")) as f:
            self.lines = f.readlines()
        self.marker = int(self.lines[0].split()[0])
        self.N = float(len(self.lines))
        for self.i, line in enumerate(self.lines[1:]):
            if int(line.split()[0]) == self.marker:
                break
        return context.window_manager.invoke_props_dialog(self)
    def execute(self, context):
        scene = context.scene
        frame_initial = scene.frame_current
        wm = context.window_manager
        wm.progress_begin(0., 100.)
        skip = self.steps - 1
        for n, line in enumerate(self.lines):
            if int(line.split()[0]) == self.marker:
                skip = (skip + 1) % self.steps
            if not skip:
                wm.progress_update(100.*float(n)/self.N)
                fields = line.split()
                node_index = int(fields[0])
                if node_index == self.marker:
                    scene.frame_current += 1
                fields = [float(field) for field in fields[1:13]]
                euler = Matrix([fields[3:6], fields[6:9], fields[9:12]]).to_euler()
                database.node[node_index].location = fields[:3]
                database.node[node_index].rotation_euler = euler[0], euler[1], euler[2]
                for data_path in "location rotation_euler".split():
                    database.node[node_index].keyframe_insert(data_path)
        scene.frame_current = frame_initial + 1
        wm.progress_end()
        return{'FINISHED'}
    def draw(self, context):
        layout = self.layout
        layout.label("File has " + str(int(self.N/(self.i+1))) + " timesteps.")
        layout.prop(self, "steps")
BPY.klasses.append(Animate)

bundle = Bundle(tree, Base, klasses, database.simulator)
