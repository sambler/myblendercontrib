# ====================== BEGIN GPL LICENSE BLOCK ======================
#    This file is part of the  bookGen-addon for generating books in Blender
#    Copyright (c) 2014 Oliver Weissbarth
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ======================= END GPL LICENSE BLOCK ========================

import bpy
import bmesh
from mathutils import Vector, Euler, Matrix

from math import radians, degrees, atan

from .utils import get_bookgen_collection 
from .data.verts import get_verts
from .data.faces import get_faces
from .data.uvs import get_uvs
from .data.creases import get_creases

from .profiling import Profiler

class Book:

    def __init__(self, cover_height, cover_thickness, cover_depth, page_height, page_depth, page_thickness, spine_curl, hinge_inset, hinge_width, book_width, lean, lean_angle, subsurf, material):
        self.height = cover_height
        self.width = page_thickness + 2 * cover_thickness
        self.depth = cover_depth
        self.lean_angle = lean_angle
        self.lean = lean
        self.page_thickness = page_thickness
        self.page_height = page_height
        self.page_depth = page_depth
        self.cover_depth = cover_depth
        self.cover_height = cover_height
        self.cover_thickness = cover_thickness
        self.hinge_inset = hinge_inset
        self.hinge_width = hinge_width
        self.spine_curl = spine_curl
        self.subsurf = subsurf
        self.material = material
        self.location =  Vector([0,0,0])
        self.rotation =  Vector([0,0,0])


        self.verts = get_verts(page_thickness, page_height, cover_depth, cover_height, cover_thickness, page_depth, hinge_inset, hinge_width, spine_curl)
        self.faces = get_faces()
   
    def to_object(self):
        def index_to_vert(face):
            lst = []
            for i in face:
                lst.append(vert_ob[i])
            return tuple(lst)

        mesh = bpy.data.meshes.new("book")

        self.creases = get_creases()
        self.uvs = get_uvs(self.page_thickness, self.page_height, self.cover_depth, self.cover_height, self.cover_thickness, self.page_depth, self.hinge_inset, self.hinge_width, self.spine_curl)


        self.obj = bpy.data.objects.new("book", mesh)

        bm = bmesh.new()
        bm.from_mesh(mesh)
        vert_ob = []
        for vert in self.verts:
            vert_ob.append(bm.verts.new(vert))

        bm.verts.index_update()
        bm.verts.ensure_lookup_table()

        cl = bm.edges.layers.crease.verify()
        for c in self.creases:
            e = bm.edges.new((bm.verts[c[0]], bm.verts[c[1]]))
            e[cl] = 1.0

        for face in self.faces:
            f = bm.faces.new(index_to_vert(face))
            f.smooth = True

        bm.faces.index_update()
        bm.edges.ensure_lookup_table()

        uv_layer = bm.loops.layers.uv.verify()
        for (f, uvs) in zip(bm.faces, self.uvs):
            for (l, uv) in zip(f.loops, uvs):
                loop_uv = l[uv_layer]
                loop_uv.uv.x = uv[0]
                loop_uv.uv.y = uv[1]

        bm.normal_update()
        bm.to_mesh(mesh)
        bm.free()

        # calculate auto smooth angle based on spine
        center = self.verts[-1]
        side = self.verts[-5]
        curl = abs(center[1] - side[1])
        width = abs(center[0] - side[0])
        spine_angle = atan(width/curl)*2
        normal_angle = radians(180) - spine_angle + radians(1) # add 1 deg to account for fp
        mesh.use_auto_smooth = True
        mesh.auto_smooth_angle = normal_angle

        if(self.subsurf):
            self.obj.modifiers.new("subd", type='SUBSURF')
            self.obj.modifiers['subd'].levels = 1


        if(self.material):
            if self.obj.data.materials:
                self.obj.data.materials[0] = self.material
            else:
                self.obj.data.materials.append(self.material)
        
        self.obj.matrix_world = Matrix.Translation(self.location) @ self.rotation.to_4x4()

        return self.obj


    def get_geometry(self):
        transformed_verts = map(lambda v: self.rotation @ Vector(v) + self.location, self.verts)
        return transformed_verts, self.faces


