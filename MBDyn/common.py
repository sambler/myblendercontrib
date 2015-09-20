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
    imp.reload(sqrt)
    imp.reload(bmesh)
else:
    import bpy
    from math import sqrt
    import bmesh

FORMAT = "{:.6g}".format

def safe_name(name):
    return "_".join("_".join(name.split(".")).split())

class Type(str):
    def __new__(cls, data='', N=None):
        return super(Type, cls).__new__(cls, data)
    def __init__(self, data='', N=None):
        self.N = N

aerodynamic_types = [
    Type("Aerodynamic body", 1),
    Type("Aerodynamic beam2", 2),
    "Aerodynamic beam3",
    "Generic aerodynamic force",
    "Induced velocity"]
beam_types = [
    Type("Beam segment", 2),
    "Three node beam"]
force_types = [
    "Abstract force",
    Type("Structural force", 1),
    Type("Structural internal force", 2),
    Type("Structural couple", 1),
    Type("Structural internal couple", 2)]
genel_types = [
    "Swashplate"]
joint_types = [
    Type("Axial rotation", 2),
    Type("Clamp", 1),
    Type("Distance", 2),
    Type("Deformable displacement joint", 2),
    Type("Deformable hinge", 2),
    Type("Deformable joint", 2),
    Type("Inline", 2),
    Type("Inplane", 2),
    Type("Revolute hinge", 2),
    Type("Rod", 2),
    Type("Spherical hinge", 2),
    Type("Total joint", 2),
    Type("Viscous body", 1)]
environment_types = [
    "Air properties",
    "Gravity"]
node_types = [
    Type("Rigid offset", 2),
    Type("Dummy node", 2),
    "Feedback node"]

rigid_body_types = ["Body"]

structural_static_types = aerodynamic_types + joint_types + ["Rotor"] + beam_types + force_types

structural_dynamic_types = rigid_body_types

method_types = [
    "Crank Nicolson",
    "ms",
    "Hope",
    "Third order",
    "bdf",
    "Implicit Euler"]

nonlinear_solver_types = [
    "Newton Raphston",
    "Line search",
    "Matrix free"]

class Common:
    def write_vector(self, f, v, end=""):
        f.write(", ".join([FORMAT(round(x, 6) if round(x, 6) != -0. else 0) for x in v]) + end)
    def write_matrix(self, f, m, pad=""):
        f.write(",\n".join([pad + ", ".join(FORMAT(round(x, 6) if round(x, 6) != -0. else 0) for x in r) for r in m]))

def subsurf(obj):
    subsurf = [m for m in obj.modifiers if m.type == 'SUBSURF']
    subsurf = subsurf[0] if subsurf else obj.modifiers.new("Subsurf", 'SUBSURF')
    subsurf.levels = 3

def Ellipsoid(obj, mass, mat):
    def v_or_1(value):
        return value if isinstance(value, (int, float)) else 1.0
    diag, scale = 3*[1.0], 1.0
    if mat is not None:
        if mat.subtype != "eye":
            diag = [v_or_1(mat.floats[4*i]) for i in range(3)]
        scale = v_or_1(mat.scale)
    s = [0.5*sqrt(x*scale/v_or_1(mass)) for x in diag]
    bm = bmesh.new()
    for v in [(x*s[0],y*s[1],z*s[2]) for z in [-1., 1.] for y in [-1., 1.] for x in [-1., 1.]]:
        bm.verts.new(v)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for f in [(1,0,2,3),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)]:
        bm.faces.new([bm.verts[i] for i in f])
    crease = bm.edges.layers.crease.new()
    for e in bm.edges:
        e[crease] = 0.184
    bm.to_mesh(obj.data)
    subsurf(obj)
    bm.free()

def Sphere(obj):
    bm = bmesh.new()
    for v in [(x, y, z) for z in [-0.5, 0.5] for y in [-0.5, 0.5] for x in [-0.5, 0.5]]:
        bm.verts.new(v)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for f in [(1,0,2,3),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)]:
        bm.faces.new([bm.verts[i] for i in f])
    bm.to_mesh(obj.data)
    subsurf(obj)
    bm.free()

def RhombicPyramid(obj):
    bm = bmesh.new()
    for v in [(.333,0.,0.),(0.,.666,0.),(-.333,0.,0.),(0.,-.666,0.),(0.,0.,1.)]:
        bm.verts.new(v)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for f in [(3,2,1,0),(0,1,4),(1,2,4),(2,3,4),(3,0,4)]:
        bm.faces.new([bm.verts[i] for i in f])
    crease = bm.edges.layers.crease.new()
    for e in bm.edges:
        e[crease] = 1.0
    bm.to_mesh(obj.data)
    subsurf(obj)
    bm.free()

def Teardrop(obj):
    bm = bmesh.new()
    for v in [(x, y, -.5) for y in [-.5, .5] for x in [-.5, .5]] + [(0.,0.,0.)]:
        bm.verts.new(v)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for q in [(2,3,1,0),(0,1,4),(1,3,4),(3,2,4),(2,0,4)]:
        bm.faces.new([bm.verts[i] for i in q])
    crease = bm.edges.layers.crease.new()
    for i in range(4,8):
        bm.edges[i][crease] = 1.0
    bm.to_mesh(obj.data)
    bm.free()
    subsurf(obj)

def Cylinder(obj):
    bm = bmesh.new()
    scale = .5
    for z in [-1., 1.]:
        for y in [-1., 1.]:
            for x in [-1., 1.]:
                bm.verts.new((scale*x,scale*y,scale*z))
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for q in [(1,0,2,3),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)]:
        bm.faces.new([bm.verts[i] for i in q])
    crease = bm.edges.layers.crease.new()
    for v0, v1 in ([(0,1),(0,2),(2,3),(3,1),(4,5),(4,6),(6,7),(7,5)]):
        bm.edges.get((bm.verts[v0], bm.verts[v1]))[crease] = 1.0
    bm.to_mesh(obj.data)
    bm.free()
    subsurf(obj)

def RectangularCuboid(obj):
    bm = bmesh.new()
    for v in [(x, y, z) for z in [-0.2, 0.2] for y in [-0.1, 0.1] for x in [-0.3, 0.3]]:
        bm.verts.new(v)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for f in [(1,0,2,3),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)]:
        bm.faces.new([bm.verts[i] for i in f])
    crease = bm.edges.layers.crease.new()
    for e in bm.edges:
        e[crease] = 1.0
    bm.to_mesh(obj.data)
    subsurf(obj)
    bm.free()
