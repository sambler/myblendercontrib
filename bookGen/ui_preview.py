import gpu

import bpy
import gpu
import bgl
from gpu_extras.batch import batch_for_shader

import mathutils
from mathutils import Vector, Matrix

from .utils import vector_scale
import logging

from .utils import bookGen_directory

class BookGenShelfPreview():

    log = logging.getLogger("bookGen.preview")


    def __init__(self):
        with open(bookGen_directory+"/shaders/simple_flat.vert") as fp:
            vertex_shader = fp.read()

        with open(bookGen_directory+"/shaders/simple_flat.frag") as fp:
            fragment_shader = fp.read()
        
        
        self.shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
        
        self.batch = None

        self.draw_handler = None
        self.color = [0.8, 0.8, 0.8]



    def draw(self, op, context):
        if self.batch is None:
            return

        view_projection_matrix = bpy.context.region_data.perspective_matrix
        normal_matrix = bpy.context.region_data.view_matrix.inverted().transposed()

        self.shader.bind()
        bgl.glEnable(bgl.GL_DEPTH_TEST)
        bgl.glDepthFunc(bgl.GL_LESS)
        self.shader.uniform_float("color", self.color)
        self.shader.uniform_float("modelviewprojection_mat", view_projection_matrix)
        self.shader.uniform_float("normal_mat", normal_matrix)
        self.batch.draw(self.shader)
        bgl.glDisable(bgl.GL_DEPTH_TEST)


    def update(self, verts, faces, context):

        normals = []
        vertices = []
        for f in faces:
            vertices += [verts[f[0]], verts[f[1]], verts[f[2]], verts[f[0]], verts[f[2]], verts[f[3]]]
            a = Vector(verts[f[1]]) - Vector(verts[f[0]])
            b = Vector(verts[f[2]]) - Vector(verts[f[0]])
            nrm = (a.cross(b)).normalized()
            normals += [nrm] * 6

        self.batch = batch_for_shader(self.shader, "TRIS", {"pos": vertices, "nrm": normals})

        if self.draw_handler is None:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, (self, context), 'WINDOW', 'POST_VIEW')



    def remove(self):
        self.log.debug("removing draw handler")
        if self.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')
            self.draw_handler = None
