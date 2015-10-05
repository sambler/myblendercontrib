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
    from .common import FORMAT, method_types, nonlinear_solver_types

problem_types = ["General data"] + method_types + nonlinear_solver_types + ["Eigenanalysis", "Abort after", "Linear solver", "Dummy steps", "Output data", "Real time"]

control_types = ["Assembly", "Job control", "Default output", "Default aerodynamic output", "Default beam output", "Default scale", "Rigid body kinematics"]

problem_tree = ["Problem",
    ["General data",
    "Method", method_types,
    "Nonlinear solver", nonlinear_solver_types,
    "Eigenanalysis",
    "Abort after",
    "Linear solver",
    "Dummy steps",
    "Output data",
     "Real time"
    ]]

control_tree = ["Control", control_types]

types = problem_types + control_types

tree = ["Definition", problem_tree + control_tree]

klasses = dict()

class Base(Operator):
    bl_label = "Definitions"
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return True
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.definition_uilist = bpy.props.CollectionProperty(type = ListItem)
        bpy.types.Scene.definition_index = bpy.props.IntProperty(default=-1)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.definition_uilist
        del bpy.types.Scene.definition_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.definition_index, context.scene.definition_uilist
    def set_index(self, context, value):
        context.scene.definition_index = value

for t in types:
    class Tester(Base):
        bl_label = t
        @classmethod
        def poll(cls, context):
            return False
        def create_entity(self):
            return Entity(self.name)
    klasses[t] = Tester

class GeneralProblem(Entity):
    def write(self, f):
        f.write("\tstrategy: " + self.strategy)
        if self.strategy == "factor":
            f.write(", " + ", ".join([BPY.FORMAT(v) for v in (self.reduction_factor, self.steps_before_reduction,
                self.raise_factor, self.steps_before_raise, self.factor_min_iterations)])
                + (", " + FORMAT(self.factor_max_iterations) if self.set_factor_max_iterations else ""))
        elif self.strategy == "change":
            f.write(", " + self.time_step_pattern_drive.string())
        if self.strategy != "no change":
            f.write(";\n\tmin time step: " + FORMAT(self.min_time_step) +
            ";\n\tmax time step: " + ("unlimited" if self.unlimited else FORMAT(self.max_time_step)))
        f.write(";\n\ttime step: " + FORMAT(self.time_step))
        if self.set_residual_tolerance:
            f.write(";\n\ttolerance: " + FORMAT(self.residual_tolerance))
            if self.set_residual_test:
                f.write(", test, " + self.residual_test + (", scale" if self.scale_residual_test else ""))
            if self.set_solution_tolerance:
                f.write(", " + FORMAT(self.solution_tolerance) +
                    (", test, " + self.solution_test if self.set_solution_test else ""))
        f.write(";\n\tmax iterations: " + (FORMAT(self.max_iterations) if self.max_iterations else "null") +
            (", at most" if self.at_most else "") +
            (";\n\tmodify residual test" if self.modify_residual_test else ""))
        if self.set_threads:
            f.write(";\n\tthreads: " + self.auto_disable +
                (", " + self.assembly_solver if self.set_assembly_solver else "") + ", " + FORMAT(self.threads))
        f.write(";\n\tderivatives tolerance: " + FORMAT(self.derivatives_tolerance) +
            ";\n\tderivatives max iterations: " + FORMAT(self.derivatives_max_iterations) +
            ";\n\tderivatives coefficient: " + FORMAT(self.derivatives_coefficient) + ";\n")

class GeneralProblemOperator(Base):
    bl_label = "General data"
    strategy = bpy.props.EnumProperty(items=[
        ("no change", "No change", ""),
        ("factor", "Factor", ""),
        ("change", "Change", ""),
        ], name="Strategy", default="no change")
    reduction_factor = bpy.props.PointerProperty(type = BPY.Float)
    steps_before_reduction = bpy.props.IntProperty(name="Steps before reduction", default=0, min=0)
    raise_factor = bpy.props.FloatProperty(name="Raise factor", default=0.0, min=0.0, precision=6)
    steps_before_raise = bpy.props.IntProperty(name="Steps before raise", default=0, min=0)
    factor_min_iterations = bpy.props.IntProperty(name="Min iterations", default=0, min=0)
    set_factor_max_iterations = bpy.props.BoolProperty(name="Set max iterations")
    factor_max_iterations = bpy.props.IntProperty(name="Max iterations", min=0)
    time_step_pattern_drive = bpy.props.PointerProperty(type=BPY.Drive)
    min_time_step = bpy.props.FloatProperty(name="Min time step", default=0.0, min=0.0, precision=6)
    unlimited = bpy.props.BoolProperty(name="Unlimited")
    max_time_step = bpy.props.FloatProperty(name="Max time step", default=0.0, min=0.0, precision=6)
    time_step = bpy.props.FloatProperty(name="Initial time step", default=1e-3, min=0.0, precision=6)
    set_residual_tolerance = bpy.props.BoolProperty(name="Set residual tolerance", default=True)
    residual_tolerance = bpy.props.FloatProperty(name="Residual tolerance", default=1e-6, min=0.0, precision=6)
    set_residual_test = bpy.props.BoolProperty(name="Set residual test")
    residual_test = bpy.props.EnumProperty(items=[
        ("none", "None", ""),
        ("norm", "Norm", ""),
        ("minmax", "Min max", ""),
        ], name="Residual test", default="norm")
    scale_residual_test = bpy.props.BoolProperty(name="Scale residual test")
    set_solution_tolerance = bpy.props.BoolProperty(name="Set solution tolerance")
    solution_tolerance = bpy.props.FloatProperty(name="Solution tolerance", default=0.0, min=0.0, precision=6)
    set_solution_test = bpy.props.BoolProperty(name="Set solution test")
    solution_test = bpy.props.EnumProperty(items=[
        ("none", "None", ""),
        ("norm", "Norm", ""),
        ("minmax", "Min max", ""),
        ], name="Residual test", default="norm")
    max_iterations = bpy.props.IntProperty(name="Max iterations", default=10, min=0)
    at_most = bpy.props.BoolProperty(name="At most")
    modify_residual_test = bpy.props.BoolProperty(name="Modify residual test")
    set_threads = bpy.props.BoolProperty(name="Set auto or disable")
    auto_disable = bpy.props.EnumProperty(items=[
        ("auto", "Auto", ""),
        ("disable", "Disable", ""),
        ], name="Auto or disable", default="auto")
    set_assembly_solver = bpy.props.BoolProperty(name="Only assembly or solver")
    assembly_solver = bpy.props.EnumProperty(items=[
        ("assembly", "Assembly", ""),
        ("solver", "Solver", ""),
        ], name="Assembly or solver", default="solver")
    threads = bpy.props.IntProperty(name="Threads", default=1, min=1)
    derivatives_tolerance = bpy.props.FloatProperty(name="Derivatives tolerance", default=2.0, min=0.0, precision=6)
    derivatives_max_iterations = bpy.props.IntProperty(name="Derivatives max iterations", default=1, min=0)
    derivatives_coefficient = bpy.props.FloatProperty(name="Derivatives coefficient", default=1e-3, min=0.0, precision=6)
    def prereqs(self, context):
        self.reduction_factor.mandatory = True
    def assign(self, context):
        self.strategy = self.entity.strategy
        self.reduction_factor.assign(self.entity.reduction_factor)
        self.steps_before_reduction = self.entity.steps_before_reduction
        self.raise_factor = self.entity.raise_factor
        self.steps_before_raise = self.entity.steps_before_raise
        self.factor_min_iterations = self.entity.factor_min_iterations
        self.set_factor_max_iterations = self.entity.set_factor_max_iterations
        self.factor_max_iterations = self.entity.factor_max_iterations
        self.min_time_step = self.entity.min_time_step
        self.unlimited = self.entity.unlimited
        self.max_time_step = self.entity.max_time_step
        self.time_step = self.entity.time_step
        self.set_residual_tolerance = self.entity.set_residual_tolerance
        self.residual_tolerance = self.entity.residual_tolerance
        self.set_residual_test = self.entity.set_residual_test
        self.residual_test = self.entity.residual_test
        self.scale_residual_test = self.entity.scale_residual_test
        self.set_solution_tolerance = self.entity.set_solution_tolerance
        self.solution_tolerance = self.entity.solution_tolerance
        self.set_solution_test = self.entity.set_solution_test
        self.solution_test = self.entity.solution_test
        self.max_iterations = self.entity.max_iterations
        self.at_most = self.entity.at_most
        self.modify_residual_test = self.entity.modify_residual_test
        self.set_threads = self.entity.set_threads
        self.auto_disable = self.entity.auto_disable
        self.set_assembly_solver = self.entity.set_assembly_solver
        self.assembly_solver = self.entity.assembly_solver
        self.threads = self.entity.threads
        self.derivatives_tolerance = self.entity.derivatives_tolerance
        self.derivatives_max_iterations = self.entity.derivatives_max_iterations
        self.derivatives_coefficient = self.entity.derivatives_coefficient
        self.time_step_pattern_drive.assign(self.entity.time_step_pattern_drive)
    def store(self, context):
        self.entity.strategy = self.strategy
        self.entity.reduction_factor = self.reduction_factor.store()
        self.entity.steps_before_reduction = self.steps_before_reduction
        self.entity.raise_factor = self.raise_factor
        self.entity.steps_before_raise = self.steps_before_raise
        self.entity.factor_min_iterations = self.factor_min_iterations
        self.entity.set_factor_max_iterations = self.set_factor_max_iterations
        self.entity.factor_max_iterations = self.factor_max_iterations
        self.entity.min_time_step = self.min_time_step
        self.entity.unlimited = self.unlimited
        self.entity.max_time_step = self.max_time_step
        self.entity.time_step = self.time_step
        self.entity.set_residual_tolerance = self.set_residual_tolerance
        self.entity.residual_tolerance = self.residual_tolerance
        self.entity.set_residual_test = self.set_residual_test
        self.entity.residual_test = self.residual_test
        self.entity.scale_residual_test = self.scale_residual_test
        self.entity.set_solution_tolerance = self.set_solution_tolerance
        self.entity.solution_tolerance = self.solution_tolerance
        self.entity.set_solution_test = self.set_solution_test
        self.entity.solution_test = self.solution_test
        self.entity.max_iterations = self.max_iterations
        self.entity.at_most = self.at_most
        self.entity.modify_residual_test = self.modify_residual_test
        self.entity.set_threads = self.set_threads
        self.entity.auto_disable = self.auto_disable
        self.entity.set_assembly_solver = self.set_assembly_solver
        self.entity.assembly_solver = self.assembly_solver
        self.entity.threads = self.threads
        self.entity.derivatives_tolerance = self.derivatives_tolerance
        self.entity.derivatives_max_iterations = self.derivatives_max_iterations
        self.entity.derivatives_coefficient = self.derivatives_coefficient
        self.entity.time_step_pattern_drive = self.time_step_pattern_drive.store()
    def draw(self, context):
        self.basis = (self.strategy, self.set_factor_max_iterations, self.unlimited, self.set_residual_tolerance, self.set_residual_test, self.set_solution_tolerance, self.set_solution_test, self.set_threads, self.set_assembly_solver)
        layout = self.layout
        layout.prop(self, "strategy")
        if self.strategy == "factor":
            self.reduction_factor.draw(layout, "Reduction factor")
            layout.prop(self, "steps_before_reduction")
            layout.prop(self, "raise_factor")
            layout.prop(self, "steps_before_raise")
            layout.prop(self, "factor_min_iterations")
            row = layout.row()
            row.prop(self, "set_factor_max_iterations")
            if self.set_factor_max_iterations:
                row.prop(self, "factor_max_iterations")
        elif self.strategy == "change":
            self.time_step_pattern_drive.draw(layout, "Time step pattern")
        if self.strategy != "no change":
            layout.prop(self, "min_time_step")
            row = layout.row()
            row.prop(self, "unlimited")
            if not self.unlimited:
                row.prop(self, "max_time_step")
        layout.prop(self, "time_step")
        row = layout.row()
        row.prop(self, "set_residual_tolerance")
        if self.set_residual_tolerance:
            row.prop(self, "residual_tolerance")
            row = layout.row()
            row.prop(self, "set_residual_test")
            if self.set_residual_test:
                row.prop(self, "residual_test")
                row.prop(self, "scale_residual_test")
            row = layout.row()
            row.prop(self, "set_solution_tolerance")
            if self.set_solution_tolerance:
                row.prop(self, "solution_tolerance")
                row = layout.row()
                row.prop(self, "set_solution_test")
                if self.set_solution_test:
                    row.prop(self, "solution_test")
        row = layout.row()
        row.prop(self, "max_iterations")
        row.prop(self, "at_most")
        layout.prop(self, "modify_residual_test")
        row = layout.row()
        row.prop(self, "set_threads")
        if self.set_threads:
            row.prop(self, "auto_disable")
            row.prop(self, "threads")
        row = layout.row()
        row.prop(self, "set_assembly_solver")
        if self.set_assembly_solver:
            row.prop(self, "assembly_solver")
        layout.prop(self, "derivatives_tolerance")
        layout.prop(self, "derivatives_max_iterations")
        layout.prop(self, "derivatives_coefficient")
    def check(self, context):
        self.time_step_pattern_drive.mandatory = self.strategy == "change"
        return (True in [x.check(context) for x in [self.reduction_factor]]) or self.time_step_pattern_drive.check(context) or (self.basis != (self.strategy, self.set_factor_max_iterations, self.unlimited, self.set_residual_tolerance, self.set_residual_test, self.set_solution_tolerance, self.set_solution_test, self.set_threads, self.set_assembly_solver))
    def create_entity(self):
        return GeneralProblem(self.name)

klasses[GeneralProblemOperator.bl_label] = GeneralProblemOperator

class CrankNicolson(Entity):
    def write(self, f, tab=True):
        f.write(("\t" if tab else "") + "method: crank nicolson;\n")

class CrankNicolsonOperator(Base):
    bl_label = "Crank Nicolson"
    def create_entity(self):
        return CrankNicolson(self.name)

klasses[CrankNicolsonOperator.bl_label] = CrankNicolsonOperator

class MS(Entity):
    def write(self, f, tab=True):
        f.write(("\t" if tab else "") + "method: ms, " + ", ".join([drive.string() for drive in [self.differential_radius_drive, self.algebraic_radius_drive] if link is not None]) + ";\n")

class MSHopeOperator(Base):
    differential_radius_drive = bpy.props.PointerProperty(type = BPY.Drive)
    algebraic_radius_drive = bpy.props.PointerProperty(type = BPY.Drive)
    def prereqs(self, context):
        self.differential_radius_drive.mandatory = True
    def assign(self, context):
        self.differential_radius_drive.assign(self.entity.differential_radius_drive)
        self.algebraic_radius_drive.assign(self.entity.algebraic_radius_drive)
    def store(self, context):
        self.entity.differential_radius_drive = self.differential_radius_drive.store()
        self.entity.algebraic_radius_drive = self.algebraic_radius_drive.store()
    def draw(self, context):
        self.differential_radius_drive.draw(self.layout, "Differential radius drive")
        self.algebraic_radius_drive.draw(self.layout, "Algebraic radius drive")
    def check(self, context):
        return self.differential_radius_drive.check(context) or self.algebraic_radius_drive.check(context)

class MSOperator(MSHopeOperator):
    bl_label = "ms"
    def create_entity(self):
        return MS(self.name)

klasses[MSOperator.bl_label] = MSOperator

class Hope(Entity):
    def write(self, f, tab=True):
        f.write(("\t" if tab else "") + "method: hope, " + ", ".join([drive.string() for drive in [self.differential_radius_drive, self.algebraic_radius_drive] if link is not None]) + ";\n")

class HopeOperator(MSHopeOperator):
    bl_label = "Hope"
    def create_entity(self):
        return Hope(self.name)

klasses[HopeOperator.bl_label] = HopeOperator

class ThirdOrder(Entity):
    def write(self, f, tab=True):
        f.write(("\t" if tab else "") + "method: third order, " + (self.differential_radius_drive.string() if self.differential_radius_drive else "ad hoc") + ";\n")

class ThirdOrderOperator(Base):
    bl_label = "Third order"
    differential_radius_drive = bpy.props.PointerProperty(type = BPY.Drive)
    def assign(self, context):
        self.differential_radius_drive.assign(self.entity.differential_radius_drive)
    def store(self, context):
        self.entity.differential_radius_drive = self.differential_radius_drive.store()
    def draw(self, context):
        self.differential_radius_drive.draw(self.layout, "Differential radius drive")
    def check(self, context):
        return self.differential_radius_drive.check(context)
    def create_entity(self):
        return ThirdOrder(self.name)

klasses[ThirdOrderOperator.bl_label] = ThirdOrderOperator

class BDF(Entity):
    def write(self, f, tab=True):
        f.write(("\t" if tab else "") + "method: bdf" + (", order, " + FORMAT(self.order) if self.set_order else "") + ";\n")

class BDFOperator(Base):
    bl_label = "bdf"
    set_order = bpy.props.BoolProperty(name="Set order")
    order = bpy.props.IntProperty(name="Order", default=1, min=1, max=2)
    def assign(self, context):
        self.set_order = self.entity.set_order
        self.order = self.entity.order
    def store(self, context):
        self.entity.set_order = self.set_order
        self.entity.order = self.order
    def draw(self, context):
        self.basis = self.set_order
        layout = self.layout
        row = layout.row()
        row.prop(self, "set_order")
        if self.set_order:
            row.prop(self, "order")
    def check(self, context):
        return self.basis != self.set_order
    def create_entity(self):
        return BDF(self.name)

klasses[BDFOperator.bl_label] = BDFOperator

class ImplicitEuler(Entity):
    def write(self, f, tab=True):
        f.write(("\t" if tab else "") + "method: implicit euler;\n")

class ImplicitEulerOperator(Base):
    bl_label = "Implicit Euler"
    def create_entity(self):
        return ImplicitEuler(self.name)

klasses[ImplicitEulerOperator.bl_label] = ImplicitEulerOperator

class NewtonRaphston(Entity):
    def write(self, f):
        f.write("\tnonlinear solver: newton raphson, " + self.true_or_modified)
        if self.true_or_modified == "modified":
            f.write(", " + FORMAT(self.iterations) +
                (", keep jacobian matrix" if self.keep_jacobian_matrix else "") +
                (", honor element requests" if self.honor_element_requests else ""))
        f.write(";\n")

class NewtonRaphstonOperator(Base):
    bl_label = "Newton Raphston"
    true_or_modified = bpy.props.EnumProperty(items=[
        ("true", "True", ""),
        ("modified", "Modified", ""),
        ], name="True or modified", default="true")
    iterations = bpy.props.IntProperty(name="Iterations", default=0, min=0)
    keep_jacobian_matrix = bpy.props.BoolProperty(name="Keep jacobian matrix")
    honor_element_requests = bpy.props.BoolProperty(name="Honor element requests")
    def assign(self, context):
        self.true_or_modified = self.entity.true_or_modified
        self.iterations = self.entity.iterations
        self.keep_jacobian_matrix = self.entity.keep_jacobian_matrix
        self.honor_element_requests = self.entity.honor_element_requests
    def store(self, context):
        self.entity.true_or_modified = self.true_or_modified
        self.entity.iterations = self.iterations
        self.entity.keep_jacobian_matrix = self.keep_jacobian_matrix
        self.entity.honor_element_requests = self.honor_element_requests
    def draw(self, context):
        self.basis = self.true_or_modified
        layout = self.layout
        row = layout.row()
        row.prop(self, "true_or_modified")
        if self.true_or_modified == "modified":
            row.prop(self, "iterations")
            row = layout.row()
            row.prop(self, "keep_jacobian_matrix")
            row.prop(self, "honor_element_requests")
    def check(self, context):
        return self.basis != self.true_or_modified
    def create_entity(self):
        return NewtonRaphston(self.name)

klasses[NewtonRaphstonOperator.bl_label] = NewtonRaphstonOperator

class LineSearch(Entity):
    def write(self, f):
        f.write("\tnonlinear solver: line search, " + self.true_or_modified)
        if self.true_or_modified == "modified":
            f.write(", " + FORMAT(self.iterations) +
                (", keep jacobian matrix" if self.keep_jacobian_matrix else "") +
                (", honor element requests" if self.honor_element_requests else ""))
        f.write(
            (",\n\t\ttolerance x, " + FORMAT(self.tolerance_x) if self.set_tolerance_x else "") +
            (",\n\t\ttolerance min, " + FORMAT(self.tolerance_min) if self.set_tolerance_min else "") +
            (",\n\t\tmax iterations, " + FORMAT(self.max_line_search_iterations) if self.set_max_line_search_iterations else "") +
            (",\n\t\talpha, " + FORMAT(self.alpha) if self.set_alpha else ""))
        if self.set_lambda_min:
            f.write(",\n\t\tlambda min, " + FORMAT(self.lambda_min) +
                ", relative, " + ("yes" if self.relative else "no"))
        f.write((",\n\t\tlambda factor min, " + FORMAT(self.lambda_factor_min) if self.set_lambda_factor_min else "") +
            (",\n\t\tmax step, " + FORMAT(self.max_step) if self.set_max_step else "") +
            (",\n\t\tzero gradient, continue, yes" if self.zero_gradient_continue else ""))
        if self.divergence_check:
            f.write(",\n\t\tdivergence check, yes" +
                (", factor, " + FORMAT(self.divergence_check_factor) if self.set_divergence_check_factor else ""))
        f.write(",\n\t\talgorithm, " + self.cubic_or_factor)
        if self.scale_newton_step:
            f.write(",\n\t\tscale newton step, yes" +
                (", min scale, " + FORMAT(self.min_scale_newton_step) if self.set_min_scale_newton_step else ""))
        f.write(",\n\t\tprint convergence info, " + ("yes" if self.print_convergence_info else "no") +
            ", verbose, " + ("yes" if self.verbose else "no") +
            ", abort at lambda min, " + ("yes" if self.abort_at_lambda_min else "no") +
            ";\n")
class LineSearchOperator(Base):
    bl_label = "Line search"
    true_or_modified = bpy.props.EnumProperty(items=[
        ("true", "True", ""),
        ("modified", "Modified", ""),
        ], name="True or modified", default="true")
    iterations = bpy.props.IntProperty(name="Iterations", default=0, min=0)
    keep_jacobian_matrix = bpy.props.BoolProperty(name="Keep jacobian matrix")
    honor_element_requests = bpy.props.BoolProperty(name="Honor element requests")
    set_tolerance_x = bpy.props.BoolProperty(name="Set tolerance x")
    tolerance_x = bpy.props.FloatProperty(name="Tolerance x", default=0.0, min=0.0, precision=6)
    set_tolerance_min = bpy.props.BoolProperty(name="Set tolerance min")
    tolerance_min = bpy.props.FloatProperty(name="Tolerance min", default=0.0, min=0.0, precision=6)
    set_max_line_search_iterations = bpy.props.BoolProperty(name="Set max iterations")
    max_line_search_iterations = bpy.props.IntProperty(name="Max iterations", default=0, min=0)
    set_alpha = bpy.props.BoolProperty(name="Set alpha")
    alpha = bpy.props.FloatProperty(name="Alpha", default=0.0, min=0.0, precision=6)
    set_lambda_min = bpy.props.BoolProperty(name="Set lambda min")
    lambda_min = bpy.props.FloatProperty(name="Lambda min", default=0.0, min=0.0, precision=6)
    relative = bpy.props.BoolProperty(name="Relative")
    set_lambda_factor_min = bpy.props.BoolProperty(name="Set lambda factor min")
    lambda_factor_min = bpy.props.FloatProperty(name="Lambda factor min", default=0.0, min=0.0, precision=6)
    set_max_step = bpy.props.BoolProperty(name="Set max step")
    max_step = bpy.props.IntProperty(name="Max step", default=0, min=0)
    zero_gradient_continue = bpy.props.BoolProperty(name="Zero gradient continue")
    divergence_check = bpy.props.BoolProperty(name="Divergence check")
    set_divergence_check_factor = bpy.props.BoolProperty(name="Set divergence check factor")
    divergence_check_factor = bpy.props.FloatProperty(name="Divergence check factor", default=0.0, min=0.0, precision=6)
    cubic_or_factor = bpy.props.EnumProperty(items=[
        ("cubic", "Cubic", ""),
        ("factor", "Factor", ""),
        ], name="Cubic or factor", default="cubic")
    scale_newton_step = bpy.props.BoolProperty(name="Scale Newton step")
    set_min_scale_newton_step = bpy.props.BoolProperty(name="Set min scale Newton step")
    min_scale_newton_step = bpy.props.FloatProperty(name="Min scale Newton step", default=0.0, min=0.0, precision=6)
    print_convergence_info = bpy.props.BoolProperty(name="Print convergence info")
    verbose = bpy.props.BoolProperty(name="Verbose")
    abort_at_lambda_min = bpy.props.BoolProperty(name="Abort at lambda min")
    def assign(self, context):
        self.true_or_modified = self.entity.true_or_modified
        self.iterations = self.entity.iterations
        self.keep_jacobian_matrix = self.entity.keep_jacobian_matrix
        self.honor_element_requests = self.entity.honor_element_requests
        self.set_tolerance_x = self.entity.set_tolerance_x
        self.tolerance_x = self.entity.tolerance_x
        self.set_tolerance_min = self.entity.set_tolerance_min
        self.tolerance_min = self.entity.tolerance_min
        self.set_max_line_search_iterations = self.entity.set_max_line_search_iterations
        self.max_line_search_iterations = self.entity.max_line_search_iterations
        self.set_alpha = self.entity.set_alpha
        self.alpha = self.entity.alpha
        self.set_lambda_min = self.entity.set_lambda_min
        self.lambda_min = self.entity.lambda_min
        self.relative = self.entity.relative
        self.set_lambda_factor_min = self.entity.set_lambda_factor_min
        self.lambda_factor_min = self.entity.lambda_factor_min
        self.set_max_step = self.entity.set_max_step
        self.max_step = self.entity.max_step
        self.zero_gradient_continue = self.entity.zero_gradient_continue
        self.divergence_check = self.entity.divergence_check
        self.set_divergence_check_factor = self.entity.set_divergence_check_factor
        self.divergence_check_factor = self.entity.divergence_check_factor
        self.cubic_or_factor = self.entity.cubic_or_factor
        self.scale_newton_step = self.entity.scale_newton_step
        self.set_min_scale_newton_step = self.entity.set_min_scale_newton_step
        self.min_scale_newton_step = self.entity.min_scale_newton_step
        self.print_convergence_info = self.entity.print_convergence_info
        self.verbose = self.entity.verbose
        self.abort_at_lambda_min = self.entity.abort_at_lambda_min
    def store(self, context):
        self.entity.true_or_modified = self.true_or_modified
        self.entity.iterations = self.iterations
        self.entity.keep_jacobian_matrix = self.keep_jacobian_matrix
        self.entity.honor_element_requests = self.honor_element_requests
        self.entity.set_tolerance_x = self.set_tolerance_x
        self.entity.tolerance_x = self.tolerance_x
        self.entity.set_tolerance_min = self.set_tolerance_min
        self.entity.tolerance_min = self.tolerance_min
        self.entity.set_max_line_search_iterations = self.set_max_line_search_iterations
        self.entity.max_line_search_iterations = self.max_line_search_iterations
        self.entity.set_alpha = self.set_alpha
        self.entity.alpha = self.alpha
        self.entity.set_lambda_min = self.set_lambda_min
        self.entity.lambda_min = self.lambda_min
        self.entity.relative = self.relative
        self.entity.set_lambda_factor_min = self.set_lambda_factor_min
        self.entity.lambda_factor_min = self.lambda_factor_min
        self.entity.set_max_step = self.set_max_step
        self.entity.max_step = self.max_step
        self.entity.zero_gradient_continue = self.zero_gradient_continue
        self.entity.divergence_check = self.divergence_check
        self.entity.set_divergence_check_factor = self.set_divergence_check_factor
        self.entity.divergence_check_factor = self.divergence_check_factor
        self.entity.cubic_or_factor = self.cubic_or_factor
        self.entity.scale_newton_step = self.scale_newton_step
        self.entity.set_min_scale_newton_step = self.set_min_scale_newton_step
        self.entity.min_scale_newton_step = self.min_scale_newton_step
        self.entity.print_convergence_info = self.print_convergence_info
        self.entity.verbose = self.verbose
        self.entity.abort_at_lambda_min = self.abort_at_lambda_min
    def draw(self, context):
        self.basis = (self.true_or_modified, self.set_tolerance_x, self.set_tolerance_min, self.set_max_line_search_iterations, self.set_alpha, self.set_lambda_min, self.set_lambda_factor_min, self.set_max_step, self.divergence_check, self.set_divergence_check_factor, self.scale_newton_step, self.set_min_scale_newton_step)
        layout = self.layout
        row = layout.row()
        row.prop(self, "true_or_modified")
        if self.true_or_modified == "modified":
            row.prop(self, "iterations")
            row.prop(self, "keep_jacobian_matrix")
            row.prop(self, "honor_element_requests")
        row = layout.row()
        row.prop(self, "set_tolerance_x")
        if self.set_tolerance_x:
            row.prop(self, "tolerance_x")
        row = layout.row()
        row.prop(self, "set_tolerance_min")
        if self.set_tolerance_min:
            row.prop(self, "tolerance_min")
        row = layout.row()
        row.prop(self, "set_max_line_search_iterations")
        if self.set_max_line_search_iterations:
            row.prop(self, "max_line_search_iterations")
        row = layout.row()
        row.prop(self, "set_alpha")
        if self.set_alpha:
            row.prop(self, "alpha")
        row = layout.row()
        row.prop(self, "set_lambda_min")
        if self.set_lambda_min:
            row.prop(self, "lambda_min")
            row.prop(self, "relative")
        row = layout.row()
        row.prop(self, "set_lambda_factor_min")
        if self.set_lambda_factor_min:
            row.prop(self, "lambda_factor_min")
        row = layout.row()
        row.prop(self, "set_max_step")
        if self.set_max_step:
            row.prop(self, "max_step")
        layout.prop(self, "zero_gradient_continue")
        row = layout.row()
        row.prop(self, "divergence_check")
        if self.divergence_check:
            row.prop(self, "set_divergence_check_factor")
            if self.set_divergence_check_factor:
                row.prop(self, "divergence_check_factor")
        layout.prop(self, "cubic_or_factor")
        row = layout.row()
        row.prop(self, "scale_newton_step")
        if self.scale_newton_step:
            row.prop(self, "set_min_scale_newton_step")
            if self.set_min_scale_newton_step:
                row.prop(self, "min_scale_newton_step")
        for s in "print_convergence_info verbose abort_at_lambda_min".split():
            layout.prop(self, s)
    def check(self, context):
        return self.basis != (self.true_or_modified, self.set_tolerance_x, self.set_tolerance_min, self.set_max_line_search_iterations, self.set_alpha, self.set_lambda_min, self.set_lambda_factor_min, self.set_max_step, self.divergence_check, self.set_divergence_check_factor, self.scale_newton_step, self.set_min_scale_newton_step)
    def create_entity(self):
        return LineSearch(self.name)

klasses[LineSearchOperator.bl_label] = LineSearchOperator

class MatrixFree(Entity):
    def write(self, f):
        f.write("\tmatrix free: " + self.bicgstab_or_gmres +
            (",\n\t\ttolerance, " + FORMAT(self.tolerance) if self.set_tolerance else "") +
            (",\n\t\tsteps, " + FORMAT(self.steps) if self.set_steps else "") +
            (",\n\t\ttau, " + FORMAT(self.tau) if self.set_tau else "") +
            (",\n\t\teta, " + FORMAT(self.eta) if self.set_eta else ""))
        if self.preconditioner:
            f.write(",\n\t\tpreconditioner, full jacobian matrix" +
                (", steps, " + FORMAT(self.preconditioner_steps) if self.set_preconditioner_steps else "") +
                (", honor element requests" if self.honor_element_requests else ""))
        f.write(";\n")

class MatrixFreeOperator(Base):
    bl_label = "Matrix free"
    set_nonlinear_solver_data = bpy.props.BoolProperty(name="Set nonlinear solver data")
    bicgstab_or_gmres = bpy.props.EnumProperty(items=[
        ("bicgstab", "bicgstab", ""),
        ("gmres", "gmres", ""),
        ], name="bicgstab or gmres", default="bicgstab")
    set_tolerance = bpy.props.BoolProperty(name="Set tolerance")
    tolerance = bpy.props.FloatProperty(name="Tolerance", default=0.0, min=0.0, precision=6)
    set_steps = bpy.props.BoolProperty(name="Set steps")
    steps = bpy.props.IntProperty(name="Steps", default=0, min=0)
    set_tau = bpy.props.BoolProperty(name="Set tau")
    tau = bpy.props.FloatProperty(name="Tau", default=0.0, min=0.0, precision=6)
    set_eta = bpy.props.BoolProperty(name="Set eta")
    eta = bpy.props.FloatProperty(name="Eta", default=0.0, min=0.0, precision=6)
    preconditioner = bpy.props.BoolProperty(name="Preconditioner")
    set_preconditioner_steps = bpy.props.BoolProperty(name="Set preconditioner steps")
    preconditioner_steps = bpy.props.IntProperty(name="Preconditioner", default=0, min=0)
    honor_element_requests = bpy.props.BoolProperty(name="Honor element requests")
    def assign(self, context):
        self.bicgstab_or_gmres = self.entity.bicgstab_or_gmres
        self.set_tolerance = self.entity.set_tolerance
        self.tolerance = self.entity.tolerance
        self.set_steps = self.entity.set_steps
        self.steps = self.entity.steps
        self.set_tau = self.entity.set_tau
        self.tau = self.entity.tau
        self.set_eta = self.entity.set_eta
        self.eta = self.entity.eta
        self.preconditioner = self.entity.preconditioner
        self.set_preconditioner_steps = self.entity.set_preconditioner_steps
        self.preconditioner_steps = self.entity.preconditioner_steps
        self.honor_element_requests = self.entity.honor_element_requests
    def store(self, context):
        self.entity.bicgstab_or_gmres = self.bicgstab_or_gmres
        self.entity.set_tolerance = self.set_tolerance
        self.entity.tolerance = self.tolerance
        self.entity.set_steps = self.set_steps
        self.entity.steps = self.steps
        self.entity.set_tau = self.set_tau
        self.entity.tau = self.tau
        self.entity.set_eta = self.set_eta
        self.entity.eta = self.eta
        self.entity.preconditioner = self.preconditioner
        self.entity.set_preconditioner_steps = self.set_preconditioner_steps
        self.entity.preconditioner_steps = self.preconditioner_steps
        self.entity.honor_element_requests = self.honor_element_requests
    def draw(self, context):
        self.basis = (self.set_tolerance, self.set_steps, self.set_tau, self.set_eta, self.preconditioner, self.set_preconditioner_steps)
        layout = self.layout
        layout.prop(self, "bicgstab_or_gmres")
        row = layout.row()
        row.prop(self, "set_tolerance")
        if self.set_tolerance:
            row.prop(self, "tolerance")
        row = layout.row()
        row.prop(self, "set_steps")
        if self.set_steps:
            row.prop(self, "steps")
        row = layout.row()
        row.prop(self, "set_tau")
        if self.set_tau:
            row.prop(self, "tau")
        row = layout.row()
        row.prop(self, "set_eta")
        if self.set_eta:
            row.prop(self, "eta")
        row = layout.row()
        row.prop(self, "preconditioner")
        if self.preconditioner:
            row = layout.row()
            row.prop(self, "set_preconditioner_steps")
            if self.set_preconditioner_steps:
                row.prop(self, "preconditioner_steps")
            layout.prop(self, "honor_element_requests")
    def check(self, context):
        return self.basis != (self.set_tolerance, self.set_steps, self.set_tau, self.set_eta, self.preconditioner, self.set_preconditioner_steps)
    def create_entity(self):
        return MatrixFree(self.name)

klasses[MatrixFreeOperator.bl_label] = MatrixFreeOperator

class Eigenanalysis(Entity):
    def write(self, f):
        f.write("\teigenanalysis: list, " + FORMAT(self.num_times) + ", " + ", ".join([FORMAT(v) for v in self.when]) +
            (",\n\t\toutput full matrices" if self.output_full_matrices else "") +
            (",\n\t\toutput sparce matrices" if self.output_sparce_matrices else "") +
            (",\n\t\toutput eigenvectors" if self.output_eigenvectors else "") +
            (",\n\t\toutput geometry" if self.output_geometry else "") +
            (",\n\t\tparameter, " + FORMAT(self.parameter) if self.set_parameter else "") +
            (",\n\t\tlower frequency limit, " + FORMAT(self.lower_frequency_limit) if self.set_lower_frequency_limit else "") +
            (",\n\t\tupper frequency limit, " + FORMAT(self.upper_frequency_limit) if self.set_upper_frequency_limit else ""))
        if self.method == "use lapack":
            f.write(",\n\t\tuse lapack" + (", balance, " + self.balance if self.set_balance else ""))
        else:
            f.write(",\n\t\t" + self.method + ", " + ", ".join([FORMAT(v) for v in [self.nev, self.ncv, self.tol]]))
        f.write(";\n")

class EigenanalysisOperator(Base):
    bl_label = "Eigenanalysis"
    num_times = bpy.props.IntProperty(name="Number of times", default=1, min=1, max=50)
    when = bpy.props.CollectionProperty(name="When", type = BPY.Float)
    output_full_matrices = bpy.props.BoolProperty(name="Output full matrices")
    output_sparce_matrices = bpy.props.BoolProperty(name="Output sparce matrices")
    output_eigenvectors = bpy.props.BoolProperty(name="Output eigenvectors")
    output_geometry = bpy.props.BoolProperty(name="Output geometry")
    set_parameter = bpy.props.BoolProperty(name="Set parameter")
    parameter = bpy.props.FloatProperty(name="Parameter", default=1.0, min=0.0, precision=6)
    set_lower_frequency_limit = bpy.props.BoolProperty(name="Set lower frequency limit")
    lower_frequency_limit = bpy.props.FloatProperty(name="Lower frequency limit", default=0.0, min=0.0, precision=6)
    set_upper_frequency_limit = bpy.props.BoolProperty(name="Set upper frequency limit")
    upper_frequency_limit = bpy.props.FloatProperty(name="Upper frequency limit", default=0.0, min=0.0, precision=6)
    method = bpy.props.EnumProperty(items=[
        ("use lapack", "lapack", ""),
        ("use arpack", "arpack", ""),
        ("use jdqz", "jdqz", ""),
        ], name="Method", default="use lapack")
    set_balance = bpy.props.BoolProperty(name="Set balance")
    balance = bpy.props.EnumProperty(items=[
        ("no", "No", ""),
        ("scale", "Scale", ""),
        ("permute", "Permute", ""),
        ("all", "All", ""),
        ], name="Balance", default="no")
    nev = bpy.props.IntProperty(name="Number of eigenvalues", default=1, min=1)
    ncv = bpy.props.IntProperty(name="Number of Arnoldi vectors", default=1, min=1)
    tol = bpy.props.FloatProperty(name="Tolerance", default=0.0, min=0.0, precision=6)
    def prereqs(self, context):
        self.when.clear()
        for i in range(50):
            self.when.add().mandatory = True
    def assign(self, context):
        self.num_times = self.entity.num_times
        for i, value in enumerate(self.entity.when):
            self.when[i].value = value
        self.output_full_matrices = self.entity.output_full_matrices
        self.output_sparce_matrices = self.entity.output_sparce_matrices
        self.output_eigenvectors = self.entity.output_eigenvectors
        self.output_geometry = self.entity.output_geometry
        self.set_parameter = self.entity.set_parameter
        self.parameter = self.entity.parameter
        self.set_lower_frequency_limit = self.entity.set_lower_frequency_limit
        self.lower_frequency_limit = self.entity.lower_frequency_limit
        self.set_upper_frequency_limit = self.entity.set_upper_frequency_limit
        self.upper_frequency_limit = self.entity.upper_frequency_limit
        self.method = self.entity.method
        self.set_balance = self.entity.set_balance
        self.balance = self.entity.balance
        self.nev = self.entity.nev
        self.ncv = self.entity.ncv
        self.tol = self.entity.tol
    def store(self, context):
        self.entity.num_times = self.num_times
        self.entity.when = [t.value for t in self.when[:self.num_times]] if self.when else [0.0]
        self.entity.output_full_matrices = self.output_full_matrices
        self.entity.output_sparce_matrices = self.output_sparce_matrices
        self.entity.output_eigenvectors = self.output_eigenvectors
        self.entity.output_geometry = self.output_geometry
        self.entity.set_parameter = self.set_parameter
        self.entity.parameter = self.parameter
        self.entity.set_lower_frequency_limit = self.set_lower_frequency_limit
        self.entity.lower_frequency_limit = self.lower_frequency_limit
        self.entity.set_upper_frequency_limit = self.set_upper_frequency_limit
        self.entity.upper_frequency_limit = self.upper_frequency_limit
        self.entity.method = self.method
        self.entity.set_balance = self.set_balance
        self.entity.balance = self.balance
        self.entity.nev = self.nev
        self.entity.ncv = self.ncv
        self.entity.tol = self.tol
    def draw(self, context):
        self.basis = (self.num_times, self.set_parameter, self.set_lower_frequency_limit, self.set_upper_frequency_limit, self.method, self.set_balance)
        layout = self.layout
        layout.prop(self, "num_times")
        for i in range(self.num_times):
            layout.prop(self.when[i], "value", text="")
        layout.prop(self, "output_full_matrices")
        layout.prop(self, "output_sparce_matrices")
        layout.prop(self, "output_eigenvectors")
        layout.prop(self, "output_geometry")
        row = layout.row()
        row.prop(self, "set_parameter")
        if self.set_parameter:
            row.prop(self, "parameter")
        row = layout.row()
        row.prop(self, "set_lower_frequency_limit")
        if self.set_lower_frequency_limit:
            row.prop(self, "lower_frequency_limit")
        row = layout.row()
        row.prop(self, "set_upper_frequency_limit")
        if self.set_upper_frequency_limit:
            row.prop(self, "upper_frequency_limit")
        layout.prop(self, "method")
        if self.method == "use lapack":
            row = layout.row()
            row.prop(self, "set_balance")
            if self.set_balance:
                row.prop(self, "balance")
        else:
            layout.prop(self, "nev")
            layout.prop(self, "ncv")
            layout.prop(self, "tol")
    def check(self, context):
        return self.basis != (self.num_times, self.set_parameter, self.set_lower_frequency_limit, self.set_upper_frequency_limit, self.method, self.set_balance)
    def create_entity(self):
        return Eigenanalysis(self.name)

klasses[EigenanalysisOperator.bl_label] = EigenanalysisOperator

class AbortAfter(Entity):
    def write(self, f):
        f.write("\tabort after: " + self.abort_after + ";\n")

class AbortAfterOperator(Base):
    bl_label = "Abort after"
    abort_after = bpy.props.EnumProperty(items=[
        ("input", "input", ""),
        ("assembly", "assembly", ""),
        ("derivatives", "derivatives", ""),
        ("dummy steps", "dummy steps", ""),
        ], name="Abort after", default="input")
    def assign(self, context):
        self.abort_after = self.entity.abort_after
    def store(self, context):
        self.entity.abort_after = self.abort_after
    def draw(self, context):
        self.layout.prop(self, "abort_after")
    def create_entity(self):
        return AbortAfter(self.name)

klasses[AbortAfterOperator.bl_label] = AbortAfterOperator

class LinearSolver(Entity):
    def write(self, f):
        f.write("\tlinear solver: " + self.linear_solver)
        if self.linear_solver in "umfpack klu y12 superlu watson".split():
            f.write(",\n\t\t" + self.map_cc_dir if self.set_map_cc_dir else "")
        if self.linear_solver == "naive":
            f.write(",\n\t\t" + self.colamd_mmdata if self.set_colamd_mmdata else "")
        elif self.linear_solver == "superlu":
            f.write(",\n\t\tmmdata" if self.set_mmdata else "")
        if self.linear_solver in "naive taucs watson".split():
            f.write(",\n\t\tmultithread, " + FORMAT(self.threads) if self.set_multithread else "")
        if self.linear_solver == "y12":
            f.write(",\n\t\tworkspace size, " + FORMAT(self.workspace_size) if self.set_workspace_size else "")
        if self.linear_solver in "naive umfpack klu y12 lapack superlu watson".split():
            f.write(",\n\t\tpivot factor, " + FORMAT(self.pivot_factor) if self.set_pivot_factor else "")
        if self.linear_solver == "umfpack":
            f.write(",\n\t\tdrop tolerance, " + FORMAT(self.drop_tolerance) if self.set_drop_tolerance else "" +
                (",\n\t\tblock size, " + FORMAT(self.block_size) if self.set_block_size else ""))
        if self.linear_solver == "umfpack":
            f.write(",\n\t\tscale, " + FORMAT(self.scale) if self.set_scale else "")
        f.write(";\n")

class LinearSolverOperator(Base):
    bl_label = "Linear solver"
    linear_solver = bpy.props.EnumProperty(items=[
        ("naive", "naive", ""),
        ("umfpack", "umfpack", ""),
        ("klu", "klu", ""),
        ("y12", "y12", ""),
        ("lapack", "lapack", ""),
        ("superlu", "superlu", ""),
        ("taucs", "taucs", ""),
        ("watson", "watson", ""),
        ], name="Linear solver", default="naive")
    set_map_cc_dir = bpy.props.BoolProperty(name="Set map, cc, or dir")
    map_cc_dir = bpy.props.EnumProperty(items=[
        ("map", "map", ""),
        ("cc", "cc", ""),
        ("dir", "dir", ""),
        ], name="map cc dir", default="map")
    set_colamd_mmdata = bpy.props.BoolProperty(name="Set colamd or mmdata")
    colamd_mmdata = bpy.props.EnumProperty(items=[
        ("colamd", "colamd", ""),
        ("mmdata", "mmdata", ""),
        ], name="colamd mmdata", default="colamd")
    mmdata = bpy.props.BoolProperty(name="mmdata")
    set_multithread = bpy.props.BoolProperty(name="Set multithread")
    multithread = bpy.props.IntProperty(name="Multithread", default=1, min=1)
    set_workspace_size = bpy.props.BoolProperty(name="Set workspace size")
    workspace_size = bpy.props.IntProperty(name="Workspace size", default=0, min=0)
    set_pivot_factor = bpy.props.BoolProperty(name="Set pivot factor")
    pivot_factor = bpy.props.FloatProperty(name="Pivot factor", default=1.0, min=0.0, precision=6)
    set_drop_tolerance = bpy.props.BoolProperty(name="Set drop tolerance")
    drop_tolerance = bpy.props.FloatProperty(name="Drop tolerance", default=1.0, min=0.0, precision=6)
    set_block_size = bpy.props.BoolProperty(name="Set block size")
    block_size = bpy.props.IntProperty(name="Block size", default=32, min=0)
    set_scale = bpy.props.BoolProperty(name="Set scale")
    scale = bpy.props.EnumProperty(items=[
        ("no", "no", ""),
        ("always", "always", ""),
        ("once", "once", ""),
        ("max", "max", ""),
        ("sum", "sum", ""),
        ], name="Scale", default="no")
    def assign(self, context):
        self.linear_solver = self.entity.linear_solver
        self.set_map_cc_dir = self.entity.set_map_cc_dir
        self.map_cc_dir = self.entity.map_cc_dir
        self.set_colamd_mmdata = self.entity.set_colamd_mmdata
        self.colamd_mmdata = self.entity.colamd_mmdata
        self.mmdata = self.entity.mmdata
        self.set_multithread = self.entity.set_multithread
        self.multithread = self.entity.multithread
        self.set_workspace_size = self.entity.set_workspace_size
        self.workspace_size = self.entity.workspace_size
        self.set_pivot_factor = self.entity.set_pivot_factor
        self.pivot_factor = self.entity.pivot_factor
        self.set_drop_tolerance = self.entity.set_drop_tolerance
        self.drop_tolerance = self.entity.drop_tolerance
        self.set_block_size = self.entity.set_block_size
        self.block_size = self.entity.block_size
        self.set_scale = self.entity.set_scale
        self.scale = self.entity.scale
    def store(self, context):
        self.entity.linear_solver = self.linear_solver
        self.entity.set_map_cc_dir = self.set_map_cc_dir
        self.entity.map_cc_dir = self.map_cc_dir
        self.entity.set_colamd_mmdata = self.set_colamd_mmdata
        self.entity.colamd_mmdata = self.colamd_mmdata
        self.entity.mmdata = self.mmdata
        self.entity.set_multithread = self.set_multithread
        self.entity.multithread = self.multithread
        self.entity.set_workspace_size = self.set_workspace_size
        self.entity.workspace_size = self.workspace_size
        self.entity.set_pivot_factor = self.set_pivot_factor
        self.entity.pivot_factor = self.pivot_factor
        self.entity.set_drop_tolerance = self.set_drop_tolerance
        self.entity.drop_tolerance = self.drop_tolerance
        self.entity.set_block_size = self.set_block_size
        self.entity.block_size = self.block_size
        self.entity.set_scale = self.set_scale
        self.entity.scale = self.scale
    def draw(self, context):
        self.basis = (self.linear_solver, self.set_map_cc_dir, self.set_colamd_mmdata, self.set_multithread, self.set_workspace_size, self.set_pivot_factor, self.set_drop_tolerance, self.set_block_size, self.set_scale)
        layout = self.layout
        layout.prop(self, "linear_solver")
        if self.linear_solver in "umfpack klu y12 superlu watson".split():
            row = layout.row()
            row.prop(self, "set_map_cc_dir")
            if self.set_map_cc_dir:
                row.prop(self, "map_cc_dir")
        if self.linear_solver == "naive":
            row = layout.row()
            row.prop(self, "set_colamd_mmdata")
            if self.set_colamd_mmdata:
                row.prop(self, "colamd_mmdata")
        elif self.linear_solver == "superlu":
            row.prop(self, "mmdata")
        if self.linear_solver in "naive taucs watson".split():
            row = layout.row()
            row.prop(self, "set_multithread")
            if self.set_multithread:
                row.prop(self, "multithread")
        if self.linear_solver == "y12":
            row = layout.row()
            row.prop(self, "set_workspace_size")
            if self.set_workspace_size:
                row.prop(self, "workspace_size")
        if self.linear_solver in "naive umfpack klu y12 lapack superlu watson".split():
            row = layout.row()
            row.prop(self, "set_pivot_factor")
            if self.set_pivot_factor:
                row.prop(self, "pivot_factor")
        if self.linear_solver == "umfpack":
            row = layout.row()
            row.prop(self, "set_drop_tolerance")
            if self.set_drop_tolerance:
                row.prop(self, "drop_tolerance")
            row = layout.row()
            row.prop(self, "set_block_size")
            if self.set_block_size:
                row.prop(self, "block_size")
        if self.linear_solver == "umfpack":
            row = layout.row()
            row.prop(self, "set_scale")
            if self.set_scale:
                row.prop(self, "scale")
    def check(self, context):
        return self.basis != (self.linear_solver, self.set_map_cc_dir, self.set_colamd_mmdata, self.set_multithread, self.set_workspace_size, self.set_pivot_factor, self.set_drop_tolerance, self.set_block_size, self.set_scale)
    def create_entity(self):
        return LinearSolver(self.name)

klasses[LinearSolverOperator.bl_label] = LinearSolverOperator

class DummySteps(Entity):
    def write(self, f):
        f.write("\tdummy_steps_tolerance: " + FORMAT(self.dummy_steps_tolerance) +
        ";\n\tdummy_steps_max_iterations: " + FORMAT(self.dummy_steps_max_iterations) +
        ";\n\tdummy_steps_number: " + FORMAT(self.dummy_steps_number) +
        ";\n\tdummy_steps_ratio: " + FORMAT(self.dummy_steps_ratio) +
        ";\n\tdummy steps ")
        self.dummy_steps_method.write(f, tab=False) 
        
class DummyStepsOperator(Base):
    bl_label = "Dummy steps"
    dummy_steps_tolerance = bpy.props.FloatProperty(name="Dummy steps tolerance", default=0.0, min=0.0, precision=6)
    dummy_steps_max_iterations = bpy.props.IntProperty(name="Dummy steps max iterations", default=0, min=0)
    dummy_steps_number = bpy.props.IntProperty(name="Dummy steps number", default=0, min=0)
    dummy_steps_ratio = bpy.props.FloatProperty(name="Dummy steps ratio", default=1.0, min=0.0, precision=6)
    dummy_steps_method = bpy.props.PointerProperty(type = BPY.Definition)
    def prereqs(self, context):
        self.dummy_steps_method.type = "Method"
        self.dummy_steps_method.mandatory = True
    def assign(self, context):
        self.dummy_steps_tolerance = self.entity.dummy_steps_tolerance
        self.dummy_steps_max_iterations = self.entity.dummy_steps_max_iterations
        self.dummy_steps_number = self.entity.dummy_steps_number
        self.dummy_steps_ratio = self.entity.dummy_steps_ratio
        self.dummy_steps_method.assign(self.entity.dummy_steps_method)
    def store(self, context):
        self.entity.dummy_steps_tolerance = self.dummy_steps_tolerance
        self.entity.dummy_steps_max_iterations = self.dummy_steps_max_iterations
        self.entity.dummy_steps_number = self.dummy_steps_number
        self.entity.dummy_steps_ratio = self.dummy_steps_ratio
        self.entity.dummy_steps_method = self.dummy_steps_method.store()
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "dummy_steps_tolerance")
        layout.prop(self, "dummy_steps_max_iterations")
        layout.prop(self, "dummy_steps_number")
        layout.prop(self, "dummy_steps_ratio")
        self.dummy_steps_method.draw(self.layout, "Dummy steps method")
    def check(self, context):
        return self.dummy_steps_method.check(context)
    def create_entity(self):
        return DummySteps(self.name)

klasses[DummyStepsOperator.bl_label] = DummyStepsOperator

class OutputData(Entity):
    def write(self, f):
        args = [
            (self.none, "none"),
            (self.iterations, "iterations"),
            (self.residual, "residual"),
            (self.solution, "solution"),
            (self.jacobian_matrix, "jacobian_matrix"),
            (self.messages, "messages"),
            (self.counter, "counter"),
            (self.bailout, "bailout"),
            (self.matrix_condition_number, "matrix condition number"),
            (self.solver_condition_number, "solver condition number")]
        if [arg for arg in args if arg[0]]:
            f.write("\toutput:\n\t\t" + ",\n\t\t".join([arg[1] for arg in args if arg[0]]) + ";\n")

class OutputDataOperator(Base):
    bl_label = "Output data"
    none = bpy.props.BoolProperty(name="None")
    iterations = bpy.props.BoolProperty(name="Iterations")
    residual = bpy.props.BoolProperty(name="Residual")
    solution = bpy.props.BoolProperty(name="Solution")
    jacobian_matrix = bpy.props.BoolProperty(name="Jacobian matrix")
    messages = bpy.props.BoolProperty(name="Messages")
    counter = bpy.props.BoolProperty(name="Counter")
    bailout = bpy.props.BoolProperty(name="Bailout")
    matrix_condition_number = bpy.props.BoolProperty(name="Matrix condition number")
    solver_condition_number = bpy.props.BoolProperty(name="Solver condition number")
    def assign(self, context):
        self.none = self.entity.none
        self.iterations = self.entity.iterations
        self.residual = self.entity.residual
        self.solution = self.entity.solution
        self.jacobian_matrix = self.entity.jacobian_matrix
        self.messages = self.entity.messages
        self.counter = self.entity.counter
        self.bailout = self.entity.bailout
        self.matrix_condition_number = self.entity.matrix_condition_number
        self.solver_condition_number = self.entity.solver_condition_number
    def store(self, context):
        self.entity.none = self.none
        self.entity.iterations = self.iterations
        self.entity.residual = self.residual
        self.entity.solution = self.solution
        self.entity.jacobian_matrix = self.jacobian_matrix
        self.entity.messages = self.messages
        self.entity.counter = self.counter
        self.entity.bailout = self.bailout
        self.entity.matrix_condition_number = self.matrix_condition_number
        self.entity.solver_condition_number = self.solver_condition_number
    def draw(self, context):
        layout = self.layout
        column_flow = layout.column_flow(2)
        column_flow.prop(self, "none")
        column_flow.prop(self, "iterations")
        column_flow.prop(self, "residual")
        column_flow.prop(self, "solution")
        column_flow.prop(self, "jacobian_matrix")
        column_flow.prop(self, "messages")
        column_flow.prop(self, "counter")
        column_flow.prop(self, "bailout")
        column_flow.prop(self, "matrix_condition_number")
        column_flow.prop(self, "solver_condition_number")
    def create_entity(self):
        return OutputData(self.name)

klasses[OutputDataOperator.bl_label] = OutputDataOperator

class RealTime(Entity):
    def write(self, f):
        f.write("\treal time: " + self.rtai_posix)
        if self.mode == "period":
            f.write(", mode, period, time step, " + FORMAT(self.time_step))
        elif self.mode == "semaphore":
            f.write(", mode, semaphore, " + FORMAT(self.semaphore))
        else:
            f.write(", mode, " + self.mode)
        f.write((",\n\t\treserve stack, " + FORMAT(self.stack_size) if self.set_reserve_stack else "") +
            (",\n\t\tallow nonroot" if self.allow_nonroot else "") +
            (",\n\t\tcpu map, " + FORMAT(self.cpu_map) if self.set_cpu_map else "") +
            (",\n\t\toutput, no" if self.disable_output else "") +
            (",\n\t\thard real time" if self.hard_real_time else "") +
            (",\n\t\treal time log" + (", file name, " + self.command_name if self.set_command_name else "") if self.real_time_log else "") +
            ";\n")

class RealTimeOperator(Base):
    bl_label = "Real time"
    rtai_posix = bpy.props.EnumProperty(items=[
        ("rtai", "RTAI", ""),
        ("posix", "POSIX", ""),
        ], name="RTAI or POSIX", default="rtai")
    mode = bpy.props.EnumProperty(items=[
        ("period", "Period", ""),
        ("semaphore", "Semaphore", ""),
        ("io", "IO", ""),
        ], name="Mode", default="period")
    time_step = bpy.props.FloatProperty(name="Time step", default=0.0, min=0.0, precision=6)
    set_reserve_stack = bpy.props.BoolProperty(name="Set reserve stack")
    stack_size = bpy.props.IntProperty(name="Stack size", default=1024, min=1024)
    allow_nonroot = bpy.props.BoolProperty(name="Allow nonroot")
    set_cpu_map = bpy.props.BoolProperty(name="Set cpu map")
    cpu_map = bpy.props.IntProperty(name="Cpu map", default=0, min=0)
    disable_output = bpy.props.BoolProperty(name="Disable output")
    hard_real_time = bpy.props.BoolProperty(name="Hard real time")
    real_time_log = bpy.props.BoolProperty(name="Real time log")
    set_command_name = bpy.props.BoolProperty(name="Set command name")
    command_name = bpy.props.StringProperty(name="Command name")
    def assign(self, context):
        self.rtai_posix = self.entity.rtai_posix
        self.mode = self.entity.mode
        self.time_step = self.entity.time_step
        self.set_reserve_stack = self.entity.set_reserve_stack
        self.stack_size = self.entity.stack_size
        self.allow_nonroot = self.entity.allow_nonroot
        self.set_cpu_map = self.entity.set_cpu_map
        self.cpu_map = self.entity.cpu_map
        self.disable_output = self.entity.disable_output
        self.hard_real_time = self.entity.hard_real_time
        self.real_time_log = self.entity.real_time_log
        self.set_command_name = self.entity.set_command_name
        self.command_name = self.entity.command_name
    def store(self, context):
        self.entity.rtai_posix = self.rtai_posix
        self.entity.mode = self.mode
        self.entity.time_step = self.time_step
        self.entity.set_reserve_stack = self.set_reserve_stack
        self.entity.stack_size = self.stack_size
        self.entity.allow_nonroot = self.allow_nonroot
        self.entity.set_cpu_map = self.set_cpu_map
        self.entity.cpu_map = self.cpu_map
        self.entity.disable_output = self.disable_output
        self.entity.hard_real_time = self.hard_real_time
        self.entity.real_time_log = self.real_time_log
        self.entity.set_command_name = self.set_command_name
        self.entity.command_name = self.command_name
    def draw(self, context):
        self.basis = (self.mode, self.set_reserve_stack, self.set_cpu_map, self.real_time_log, self.set_command_name)
        layout = self.layout
        layout.prop(self, "rtai_posix")
        row = layout.row()
        row.prop(self, "mode")
        if self.mode == "period":
            row.prop(self, "time_step")
        row = layout.row()
        row.prop(self, "set_reserve_stack")
        if self.set_reserve_stack:
            row.prop(self, "stack_size")
        layout.prop(self, "allow_nonroot")
        row = layout.row()
        row.prop(self, "set_cpu_map")
        if self.set_cpu_map:
            row.prop(self, "cpu_map")
        layout.prop(self, "disable_output")
        layout.prop(self, "hard_real_time")
        layout.prop(self, "real_time_log")
        if self.real_time_log:
            row = layout.row()
            row.prop(self, "set_command_name")
            if self.set_command_name:
                row.prop(self, "command_name")
    def check(self, context):
        return self.basis != (self.mode, self.set_reserve_stack, self.set_cpu_map, self.real_time_log, self.set_command_name)
    def create_entity(self):
        return RealTime(self.name)

klasses[RealTimeOperator.bl_label] = RealTimeOperator

class Assembly(Entity):
    def write(self, f):
        if self.skip_initial_joint_assembly:
            f.write("\tskip initial joint assembly;\n")
        if (self.rigid_bodies or self.gravity or self.forces or self.beams 
            or self.aerodynamic_elements or self.loadable_elements):
            f.write("\tuse: " +
                ("rigid bodies, " if self.rigid_bodies else "") +
                ("gravity, " if self.gravity else "") +
                ("forces, " if self.forces else "") +
                ("beams, " if self.beams else "") +
                ("aerodynamic elements, " if self.aerodynamic_elements else "") +
                ("loadable elements, " if self.loadable_elements else "") +
                " in assembly;\n")
        if self.set_initial_position_stiffness:
            f.write("\tinitial stiffness: " + FORMAT(self.initial_position_stiffness) +
                (", " + FORMAT(self.initial_velocity_stiffness) if self.set_initial_velocity_stiffness else "") +
                ";\n")
        f.write("\tomega rotates: " + ("yes;\n") if self.omega_rotates else "no;\n" +
            ("\ttolerance: " + FORMAT(self.tolerance) + ";\n" if self.set_tolerance else "") +
            ("\tmax iterations: " + FORMAT(self.max_iterations) + ";\n" if self.set_max_iterations else ""))

class AssemblyOperator(Base):
    bl_label = "Assembly"
    skip_initial_joint_assembly = bpy.props.BoolProperty(name="Skip initial joint assembly")
    rigid_bodies = bpy.props.BoolProperty(name="Rigid bodies")
    gravity = bpy.props.BoolProperty(name="Gravity")
    forces = bpy.props.BoolProperty(name="Forces")
    beams = bpy.props.BoolProperty(name="Beams")
    aerodynamic_elements = bpy.props.BoolProperty(name="Aerodynamic elements")
    loadable_elements = bpy.props.BoolProperty(name="Loadable elements")
    set_initial_position_stiffness = bpy.props.BoolProperty(name="Set initial position stiffness")
    initial_position_stiffness = bpy.props.FloatProperty(name="Initial position stiffness", default=1.0, min=0.0, precision=6)
    set_initial_velocity_stiffness = bpy.props.BoolProperty(name="Set initial velocity stiffness")
    initial_velocity_stiffness = bpy.props.FloatProperty(name="Initial velocity stiffness", default=1.0, min=0.0, precision=6)
    omega_rotates = bpy.props.BoolProperty(name="Omega rotates")
    set_tolerance = bpy.props.BoolProperty(name="Set tolerance")
    tolerance = bpy.props.FloatProperty(name="Tolerance", default=0.0, min=0.0, precision=6)
    set_max_iterations = bpy.props.BoolProperty(name="Set max iterations")
    max_iterations = bpy.props.IntProperty(name="Max iterations", default=0, min=0)
    def assign(self, context):
        self.skip_initial_joint_assembly = self.entity.skip_initial_joint_assembly
        self.rigid_bodies = self.entity.rigid_bodies
        self.gravity = self.entity.gravity
        self.forces = self.entity.forces
        self.beams = self.entity.beams
        self.aerodynamic_elements = self.entity.aerodynamic_elements
        self.loadable_elements = self.entity.loadable_elements
        self.set_initial_position_stiffness = self.entity.set_initial_position_stiffness
        self.initial_position_stiffness = self.entity.initial_position_stiffness
        self.set_initial_velocity_stiffness = self.entity.set_initial_velocity_stiffness
        self.initial_velocity_stiffness = self.entity.initial_velocity_stiffness
        self.omega_rotates = self.entity.omega_rotates
        self.set_tolerance = self.entity.set_tolerance
        self.tolerance = self.entity.tolerance
        self.set_max_iterations = self.entity.set_max_iterations
        self.max_iterations = self.entity.max_iterations
    def store(self, context):
        self.entity.skip_initial_joint_assembly = self.skip_initial_joint_assembly
        self.entity.rigid_bodies = self.rigid_bodies
        self.entity.gravity = self.gravity
        self.entity.forces = self.forces
        self.entity.beams = self.beams
        self.entity.aerodynamic_elements = self.aerodynamic_elements
        self.entity.loadable_elements = self.loadable_elements
        self.entity.set_initial_position_stiffness = self.set_initial_position_stiffness
        self.entity.initial_position_stiffness = self.initial_position_stiffness
        self.entity.set_initial_velocity_stiffness = self.set_initial_velocity_stiffness
        self.entity.initial_velocity_stiffness = self.initial_velocity_stiffness
        self.entity.omega_rotates = self.omega_rotates
        self.entity.set_tolerance = self.set_tolerance
        self.entity.tolerance = self.tolerance
        self.entity.set_max_iterations = self.set_max_iterations
        self.entity.max_iterations = self.max_iterations
    def draw(self, context):
        self.basis = (self.set_initial_position_stiffness, self.set_initial_velocity_stiffness, self.set_tolerance, self.set_max_iterations)
        layout = self.layout
        layout.prop(self, "skip_initial_joint_assembly")
        layout.prop(self, "rigid_bodies")
        layout.prop(self, "gravity")
        layout.prop(self, "forces")
        layout.prop(self, "beams")
        layout.prop(self, "aerodynamic_elements")
        layout.prop(self, "loadable_elements")
        row = layout.row()
        row.prop(self, "set_initial_position_stiffness")
        if self.set_initial_position_stiffness:
            row.prop(self, "initial_position_stiffness")
            row = layout.row()
            row.prop(self, "set_initial_velocity_stiffness")
            if self.set_initial_velocity_stiffness:
                row.prop(self, "initial_velocity_stiffness")
        layout.prop(self, "omega_rotates")
        row = layout.row()
        row.prop(self, "set_tolerance")
        if self.set_tolerance:
            row.prop(self, "tolerance")
        row = layout.row()
        row.prop(self, "set_max_iterations")
        if self.set_max_iterations:
            row.prop(self, "max_iterations")
    def check(self, context):
        return self.basis != (self.set_initial_position_stiffness, self.set_initial_velocity_stiffness, self.set_tolerance, self.set_max_iterations)
    def create_entity(self):
        return Assembly(self.name)

klasses[AssemblyOperator.bl_label] = AssemblyOperator

class JobControl(Entity):
    def write(self, f):
        if self.simulation_title is not None:
            f.write("\ttitle: " + self.simulation_title + ";\n")
        if (self.dof_stats or self.dof_description or self.equation_description or 
            self.element_connection or self.node_connection):
            s = ("\tprint: " +
                ("dof stats, " if self.dof_stats else "") +
                ("dof description, " if self.dof_description else "") +
                ("equation description, " if self.equation_description else "") +
                ("element connection, " if self.element_connection else "") +
                ("node connection, " if self.node_connection else ""))
            f.write(s[:-2] + ";\n")
        if self.select_timeout is not None:
            f.write("\tselect timeout: " + BPY.FORMAT(self.select_timeout) + ";\n")
        else:
            f.write("\tselect timeout: forever;\n")
        f.write("\tdefault orientation: " + self.default_orientation + ";\n")
        f.write("\toutput meter: " + self.meter_drive.string() +
            ";\n\toutput precision: " + FORMAT(self.output_precision) + ";\n" +
            ("\tmodel: static;\n" if self.static_model else ""))

class JobControlOperator(Base):
    bl_label = "Job control"
    simulation_title = bpy.props.PointerProperty(type=BPY.Str)
    dof_stats = bpy.props.BoolProperty(name="Dof stats")
    dof_description = bpy.props.BoolProperty(name="Dof description")
    equation_description = bpy.props.BoolProperty(name="Equation description")
    element_connection = bpy.props.BoolProperty(name="Element connection")
    node_connection = bpy.props.BoolProperty(name="Node connection")
    select_timeout = bpy.props.PointerProperty(type=BPY.Float)
    meter_drive = bpy.props.PointerProperty(type = BPY.Drive)
    default_orientation = bpy.props.EnumProperty(items=[
        ("euler123", "Euler123", ""),
        ("euler313", "Euler313", ""),
        ("euler321", "Euler321", ""),
        ("orientation vector", "Orientation vector", ""),
        ("orientation matrix", "Orientation matrix", ""),
        ], name="Default orientation", default="orientation matrix")
    output_precision = bpy.props.IntProperty(name="Output precision", default=6, min=1)
    static_model = bpy.props.BoolProperty(name="Static model", description="Set model type to static")
    def prereqs(self, context):
        self.meter_drive.type = "Meter drive"
        self.meter_drive.mandatory = True
        self.meter_drive_exists(context)
    def assign(self, context):
        self.simulation_title.assign(self.entity.simulation_title)
        self.dof_stats = self.entity.dof_stats
        self.dof_description = self.entity.dof_description
        self.equation_description = self.entity.equation_description
        self.element_connection = self.entity.element_connection
        self.node_connection = self.entity.node_connection
        self.select_timeout.assign(self.entity.select_timeout)
        self.meter_drive.assign(self.entity.meter_drive)
        self.default_orientation = self.entity.default_orientation
        self.output_precision = self.entity.output_precision
        self.static_model = self.entity.static_model
    def store(self, context):
        self.entity.simulation_title = self.simulation_title.store()
        self.entity.dof_stats = self.dof_stats
        self.entity.dof_description = self.dof_description
        self.entity.equation_description = self.equation_description
        self.entity.element_connection = self.element_connection
        self.entity.node_connection = self.node_connection
        self.entity.select_timeout = self.select_timeout.store()
        self.entity.meter_drive = self.meter_drive.store()
        self.entity.output_precision = self.output_precision
        self.entity.default_orientation = self.default_orientation
        self.entity.output_precision = self.output_precision
        self.entity.static_model = self.static_model
    def draw(self, context):
        layout = self.layout
        self.simulation_title.draw(layout, "Simulation title", "Set")
        layout.label("Print:")
        for attribute in ["dof_stats", "dof_description", "equation_description", "element_connection", "node_connection"]:
            row = layout.split(.1)
            row.label()
            row.prop(self, attribute)
        self.select_timeout.draw(layout, "Select timeout", "Set")
        self.meter_drive.draw(self.layout, "Output meter drive", "Set")
        layout.prop(self, "default_orientation")
        layout.prop(self, "output_precision")
        layout.prop(self, "static_model")
    def check(self, context):
        return True in [x.check(context) for x in [self.simulation_title, self.select_timeout, self.meter_drive]]
    def create_entity(self):
        return JobControl(self.name)

klasses[JobControlOperator.bl_label] = JobControlOperator

class DefaultOutput(Entity):
    def write(self, f):
        args = [
            (self.none, "none"),
            (self.reference_frames, "reference frames"),
            (self.abstract_nodes, "abstract nodes"),
            (self.electric_nodes, "electric nodes"),
            (self.hydraulic_nodes, "hydraulic nodes"),
            (self.structural_nodes, "structural nodes"),
            (self.accelerations, "accelerations"),
            (self.aerodynamic_elements, "aerodynamic elements"),
            (self.air_properties, "air properties"),
            (self.beams, "beams"),
            (self.electric_elements, "electric elements"),
            (self.forces, "forces"),
            (self.genels, "genels"),
            (self.gravity, "gravity"),
            (self.hydraulic_elements, "hydraulic elements"),
            (self.joints, "joints"),
            (self.rigid_bodies, "rigid bodies"),
            (self.induced_velocity_elements, "induced velocity elements")]
        if [arg for arg in args if arg[0]]:
            f.write("\tdefault output:\n\t\t" + ",\n\t\t".join([arg[1] for arg in args if arg[0]]) + ";\n")

class DefaultOutputOperator(Base):
    bl_label = "Default output"
    none = bpy.props.BoolProperty(name="None")
    reference_frames = bpy.props.BoolProperty(name="Reference frames", default=True)
    abstract_nodes = bpy.props.BoolProperty(name="Abstract nodes", default=True)
    electric_nodes = bpy.props.BoolProperty(name="Electric nodes", default=True)
    hydraulic_nodes = bpy.props.BoolProperty(name="Hydraulic nodes", default=True)
    structural_nodes = bpy.props.BoolProperty(name="Structural nodes", default=True)
    accelerations = bpy.props.BoolProperty(name="Accelerations", default=True)
    aerodynamic_elements = bpy.props.BoolProperty(name="Aerodynamic elements", default=True)
    air_properties = bpy.props.BoolProperty(name="Air properties", default=True)
    beams = bpy.props.BoolProperty(name="beams", default=True)
    electric_elements = bpy.props.BoolProperty(name="Electric elements", default=True)
    forces = bpy.props.BoolProperty(name="Forces", default=True)
    genels = bpy.props.BoolProperty(name="Genels", default=True)
    gravity = bpy.props.BoolProperty(name="Gravity", default=True)
    hydraulic_elements = bpy.props.BoolProperty(name="Hydraulic elements", default=True)
    joints = bpy.props.BoolProperty(name="Joints", default=True)
    rigid_bodies = bpy.props.BoolProperty(name="Rigid bodies", default=True)
    induced_velocity_elements = bpy.props.BoolProperty(name="Induced velocity elements", default=True)
    def assign(self, context):
        self.none = self.entity.none
        self.reference_frames = self.entity.reference_frames
        self.abstract_nodes = self.entity.abstract_nodes
        self.electric_nodes = self.entity.electric_nodes
        self.hydraulic_nodes = self.entity.hydraulic_nodes
        self.structural_nodes = self.entity.structural_nodes
        self.accelerations = self.entity.accelerations
        self.aerodynamic_elements = self.entity.aerodynamic_elements
        self.air_properties = self.entity.air_properties
        self.beams = self.entity.beams
        self.electric_elements = self.entity.electric_elements
        self.forces = self.entity.forces
        self.genels = self.entity.genels
        self.gravity = self.entity.gravity
        self.hydraulic_elements = self.entity.hydraulic_elements
        self.joints = self.entity.joints
        self.rigid_bodies = self.entity.rigid_bodies
        self.induced_velocity_elements = self.entity.induced_velocity_elements
    def store(self, context):
        self.entity.none = self.none
        self.entity.reference_frames = self.reference_frames
        self.entity.abstract_nodes = self.abstract_nodes
        self.entity.electric_nodes = self.electric_nodes
        self.entity.hydraulic_nodes = self.hydraulic_nodes
        self.entity.structural_nodes = self.structural_nodes
        self.entity.accelerations = self.accelerations
        self.entity.aerodynamic_elements = self.aerodynamic_elements
        self.entity.air_properties = self.air_properties
        self.entity.beams = self.beams
        self.entity.electric_elements = self.electric_elements
        self.entity.forces = self.forces
        self.entity.genels = self.genels
        self.entity.gravity = self.gravity
        self.entity.hydraulic_elements = self.hydraulic_elements
        self.entity.joints = self.joints
        self.entity.rigid_bodies = self.rigid_bodies
        self.entity.induced_velocity_elements = self.induced_velocity_elements
    def draw(self, context):
        layout = self.layout
        column_flow = layout.column_flow(2)
        column_flow.prop(self, "none")
        column_flow.prop(self, "reference_frames")
        column_flow.prop(self, "abstract_nodes")
        column_flow.prop(self, "electric_nodes")
        column_flow.prop(self, "hydraulic_nodes")
        column_flow.prop(self, "structural_nodes")
        column_flow.prop(self, "accelerations")
        column_flow.prop(self, "aerodynamic_elements")
        column_flow.prop(self, "air_properties")
        column_flow.prop(self, "beams")
        column_flow.prop(self, "electric_elements")
        column_flow.prop(self, "forces")
        column_flow.prop(self, "genels")
        column_flow.prop(self, "gravity")
        column_flow.prop(self, "hydraulic_elements")
        column_flow.prop(self, "joints")
        column_flow.prop(self, "rigid_bodies")
        column_flow.prop(self, "induced_velocity_elements")
    def create_entity(self):
        return DefaultOutput(self.name)

klasses[DefaultOutputOperator.bl_label] = DefaultOutputOperator

class DefaultAerodynamicOutput(Entity):
    def write(self, f):
        args = [
            (self.position, "position"),
            (self.velocity, "velocity"),
            (self.angular_velocity, "angular velocity"),
            (self.force, "force"),
            (self.moment, "moment"),
            (self.orientation, "orientation")]
        if [arg for arg in args if arg[0]]:
            f.write("\tdefault aerodynamic output:\n\t\t" + ",\n\t\t".join([arg[1] for arg in args if arg[0]]))
        if self.orientation:
            f.write(", " + self.orientation_description)
        f.write(";\n")
class DefaultAerodynamicOutputOperator(Base):
    bl_label = "Default aerodynamic output"
    position = bpy.props.BoolProperty(name="Position")
    orientation = bpy.props.BoolProperty(name="Orientation")
    orientation_description = bpy.props.EnumProperty(items=[
        ("euler123", "Euler123", ""),
        ("euler313", "Euler313", ""),
        ("euler321", "Euler321", ""),
        ("orientation vector", "Orientation vector", ""),
        ("orientation matrix", "Orientation matrix", ""),
        ], name="Default orientation", default="orientation matrix")
    velocity = bpy.props.BoolProperty(name="Velocity")
    angular_velocity = bpy.props.BoolProperty(name="Angular velocity")
    force = bpy.props.BoolProperty(name="Force")
    moment = bpy.props.BoolProperty(name="Moment")
    def assign(self, context):
        self.position = self.entity.position
        self.orientation = self.entity.orientation
        self.orientation_description = self.entity.orientation_description
        self.velocity = self.entity.velocity
        self.angular_velocity = self.entity.angular_velocity
        self.force = self.entity.force
        self.moment = self.entity.moment
    def store(self, context):
        self.entity.position = self.position
        self.entity.orientation = self.orientation
        self.entity.orientation_description = self.orientation_description
        self.entity.velocity = self.velocity
        self.entity.angular_velocity = self.angular_velocity
        self.entity.force = self.force
        self.entity.moment = self.moment
    def draw(self, context):
        self.basis = self.orientation
        layout = self.layout
        row = layout.row()
        row.prop(self, "position")
        row.prop(self, "orientation")
        if self.orientation:
            row.prop(self, "orientation_description")
        column_flow = layout.column_flow(2)
        column_flow.prop(self, "velocity")
        column_flow.prop(self, "angular_velocity")
        column_flow.prop(self, "force")
        column_flow.prop(self, "moment")
    def check(self, context):
        return self.basis != self.orientation
    def create_entity(self):
        return DefaultAerodynamicOutput(self.name)

klasses[DefaultAerodynamicOutputOperator.bl_label] = DefaultAerodynamicOutputOperator

class DefaultBeamOutput(Entity):
    def write(self, f):
        args = [
            (self.position, "position"),
            (self.force, "force"),
            (self.moment, "moment"),
            (self.linear_strain, "linear strain"),
            (self.angular_strain, "angular strain"),
            (self.linear_strain_rate, "linear strain rate"),
            (self.angular_strain_rate, "angular strain rate"),
            (self.orientation, "orientation")]
        if [arg for arg in args if arg[0]]:
            f.write("\tdefault beam output:\n\t\t" + ",\n\t\t".join([arg[1] for arg in args if arg[0]]))
        if self.orientation:
            f.write(", " + self.orientation_description)
        f.write(";\n")

class DefaultBeamOutputOperator(Base):
    bl_label = "Default beam output"
    position = bpy.props.BoolProperty(name="Position")
    orientation = bpy.props.BoolProperty(name="Orientation")
    orientation_description = bpy.props.EnumProperty(items=[
        ("euler123", "Euler123", ""),
        ("euler313", "Euler313", ""),
        ("euler321", "Euler321", ""),
        ("orientation vector", "Orientation vector", ""),
        ("orientation matrix", "Orientation matrix", ""),
        ], name="Default orientation", default="orientation matrix")
    force = bpy.props.BoolProperty(name="Force")
    moment = bpy.props.BoolProperty(name="Moment")
    linear_strain = bpy.props.BoolProperty(name="Linear strain")
    angular_strain = bpy.props.BoolProperty(name="Angular strain")
    linear_strain_rate = bpy.props.BoolProperty(name="Linear strain rate")
    angular_strain_rate = bpy.props.BoolProperty(name="Angular strain rate")
    def assign(self, context):
        self.position = self.entity.position
        self.orientation = self.entity.orientation
        self.orientation_description = self.entity.orientation_description
        self.force = self.entity.force
        self.moment = self.entity.moment
        self.linear_strain = self.entity.linear_strain
        self.angular_strain = self.entity.angular_strain
        self.linear_strain_rate = self.entity.linear_strain_rate
        self.angular_strain_rate = self.entity.angular_strain_rate
    def store(self, context):
        self.entity.position = self.position
        self.entity.orientation = self.orientation
        self.entity.orientation_description = self.orientation_description
        self.entity.force = self.force
        self.entity.moment = self.moment
        self.entity.linear_strain = self.linear_strain
        self.entity.angular_strain = self.angular_strain
        self.entity.linear_strain_rate = self.linear_strain_rate
        self.entity.angular_strain_rate = self.angular_strain_rate
    def draw(self, context):
        self.basis = self.orientation
        layout = self.layout
        row = layout.row()
        row.prop(self, "position")
        row.prop(self, "orientation")
        if self.orientation:
            row.prop(self, "orientation_description")
        column_flow = layout.column_flow(2)
        column_flow.prop(self, "force")
        column_flow.prop(self, "moment")
        column_flow.prop(self, "linear_strain")
        column_flow.prop(self, "angular_strain")
        column_flow.prop(self, "linear_strain_rate")
        column_flow.prop(self, "angular_strain_rate")
    def check(self, context):
        return self.basis != self.orientation
    def create_entity(self):
        return DefaultBeamOutput(self.name)

klasses[DefaultBeamOutputOperator.bl_label] = DefaultBeamOutputOperator

bundle = Bundle(tree, Base, klasses, database.definition)
