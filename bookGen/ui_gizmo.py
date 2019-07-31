import gpu

import bpy
import gpu
import bgl
from gpu_extras.batch import batch_for_shader

import mathutils
from mathutils import Vector, Matrix

from .data.gizmo_verts import bookstand_verts_start, bookstand_verts_end
from .utils import vector_scale
import logging

from .utils import bookGen_directory

class BookGenShelfGizmo():

    log = logging.getLogger("bookGen.gizmo")


    def __init__(self, start, end, nrm, height, depth, args):
        self.height = height
        self.depth = depth

        with open(bookGen_directory+"/shaders/dotted_line.vert") as fp:
            vertex_shader = fp.read()

        with open(bookGen_directory+"/shaders/dotted_line.frag") as fp:
            fragment_shader = fp.read()

        self.bookstand_shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        self.line_shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
        self.bookstand_batch = None
        self.line_batch = None

        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, args, 'WINDOW', 'POST_VIEW')

        color_ref = bpy.context.preferences.themes[0].user_interface.gizmo_primary
        self.bookstand_color = [color_ref[0], color_ref[1],color_ref[2], 0.6]


        self.args = args




    def draw(self, op, context):
        if self.bookstand_batch is None or self.line_batch is None:
            return

        self.bookstand_shader.bind()
        bgl.glEnable(bgl.GL_BLEND)
        self.bookstand_shader.uniform_float("color", self.bookstand_color)
        self.bookstand_batch.draw(self.bookstand_shader)
        bgl.glDisable(bgl.GL_BLEND)


        bgl.glLineWidth(3)
        matrix = bpy.context.region_data.perspective_matrix
        self.line_shader.bind()
        self.line_shader.uniform_float("u_ViewProjectionMatrix", matrix)
        self.line_shader.uniform_float("u_Scale", 100)
        self.line_batch.draw(self.line_shader)


    def update(self, start, end, nrm):
        dir = end - start
        width = dir.length
        dir.normalize()
        rotationMatrix = Matrix([dir, dir.cross(nrm), nrm]).transposed()
        verts_start= []
        for v in bookstand_verts_start:
            scaled = vector_scale(v, [1, self.depth, self.height])
            rotated = rotationMatrix @ scaled 
            verts_start.append(rotated + start)
        verts_end = []
        for v in bookstand_verts_end:
            scaled = vector_scale(v, [1, self.depth, self.height])
            offset = scaled + Vector((width, 0, 0))
            rotated = rotationMatrix @ offset
            verts_end.append(rotated + start)

        bookstand_verts = verts_start + verts_end

        self.bookstand_batch = batch_for_shader(self.bookstand_shader, 'TRIS', {"pos": bookstand_verts})

        offset = nrm * 0.0001 + start

        lines = [rotationMatrix@Vector((0, self.depth/2, 0))+offset, rotationMatrix@Vector((width, self.depth/2, 0))+offset,\
             rotationMatrix@Vector((0, -self.depth/2, 0))+offset, rotationMatrix@Vector((width, -self.depth/2, 0))+offset]

        arc_length = [0, width, 0, width]

        self.line_batch = batch_for_shader(self.line_shader, "LINES", {"pos": lines, "arcLength": arc_length})

        if self.draw_handler is None:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, self.args, 'WINDOW', 'POST_VIEW')



    def remove(self):
        self.log.debug("removing draw handler")
        if self.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')
            self.draw_handler = None
