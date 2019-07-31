import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import bgl

from .utils import get_shelf_collection_by_index
class BookGenShelfOutline:
    draw_handler = None
    batch = None

    def __init__(self):
        self.shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        col_ref = bpy.context.preferences.themes[0].view_3d.face_select
        self.outline_color = (col_ref[0], col_ref[1], col_ref[2], 0.1)
        self.batch = None 

    def update(self, verts, faces, context):
        indices = []
        for f in faces:
            indices.append((f[0], f[1], f[2]))
            indices.append((f[0], f[2], f[3]))

        self.batch = batch_for_shader(self.shader, "TRIS", {"pos": verts}, indices=indices)

    def enable_outline(self, verts, faces, context):
        if self.draw_handler is None:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_outline, (self,context), 'WINDOW', 'POST_VIEW')
        self.update(verts, faces, context)

    def disable_outline(self):
        if self.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')
            self.draw_handler = None


    def draw_outline(self, op, context):
        if self.batch is None:
            return
        self.shader.bind()
        bgl.glEnable(bgl.GL_BLEND)
        self.shader.uniform_float("color", self.outline_color)
        self.batch.draw(self.shader)
        bgl.glDisable(bgl.GL_BLEND)
