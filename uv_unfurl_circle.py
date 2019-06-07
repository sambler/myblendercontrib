bl_info = {
    "name": "UV Unfurl Circle",
    "author": "batFINGER",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > UV > Circle Unfurl",
    "description": "Select circle center vertex, to unfurl UV",
    "warning": "",
    "wiki_url": "",
    "category": "UV",
}

# from https://blender.stackexchange.com/a/142078/935

import bpy
import bmesh
from mathutils import Vector, Matrix

def main(obj, up=Vector((0, 0, 1)), to=Vector((0, 1))):

    from math import pi
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    uv_layer = bm.loops.layers.uv.verify()
    v = bm.select_history.active
    if not isinstance(v, bmesh.types.BMVert):
        print("Not a vert")
        return False

    tris = [t for t in v.link_faces if len(t.edges) == 3]
    n = v.normal
    T = Matrix.Translation(-v.co)
    R = n.rotation_difference(up).to_matrix().to_4x4()

    # calc perimeter

    p = sum(e.calc_length() for f in tris for e in f.edges
            if not any(v in e.verts for x in e.verts))

    for f in tris:
        f.select = True
        e = next(e for e in f.edges if v not in e.verts)
        e.select = True
        ec = sum([v.co for v in e.verts], Vector()) / 2
        fu = R @ (T @ ec)
        fx = to.xy.angle_signed(fu.xy)

        for l in f.loops:
            luv = l[uv_layer]
            y = 0

            if l.vert is v:
                x,y = fx, (ec - v.co).length
            else:
                u = R @ (T @ l.vert.co)
                x = to.xy.angle_signed(u.xy)
                if abs(fx - x) >= 1.5 * pi:
                    x -= 2 * pi if x > 0 else -2 * pi
            luv.uv = (x + pi) / (2 * pi), y / p

    bmesh.update_edit_mesh(me)


class UV_OT_circle_unfurl(bpy.types.Operator):
    """Circle Unfurl
    Select circle fan center vertex
    Unfurl perimeter to U = 0
    """
    bl_idname = "uv.circle_unfurl"
    bl_label = "UV Circle Unfurl"

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        main(context.edit_object)
        return {'FINISHED'}

def draw(self, context):
    ''' menu item '''
    self.layout.operator("uv.circle_unfurl")

def register():
    bpy.utils.register_class(UV_OT_circle_unfurl)
    bpy.types.VIEW3D_MT_uv_map.append(draw)


def unregister():
    bpy.types.VIEW3D_MT_uv_map.remove(draw)
    bpy.utils.unregister_class(UV_OT_circle_unfurl)


if __name__ == "__main__":
    register()

