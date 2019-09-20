from . import mst_blender
import bpy

bl_info = {
    "name": "Minimum Spanning Tree (MST)",
    "description": "Addon for creating minimum spanning trees",
    "category": "Add Curve",
    "author": "Patrick Herbers",
    "blender": (2, 80, 0),
}

def menu_draw(self, context):
    layout = self.layout
    layout.menu("VIEW3D_MT_minimum_spanning_tree",
                text="Minimum Spanning Tree",
                icon="PARTICLES")

class VIEW3D_MT_minimum_spanning_tree(bpy.types.Menu):
    # Define the "Single Vert" menu
    bl_idname = "VIEW3D_MT_minimum_spanning_tree"
    bl_label = "Minimum Spanning Tree"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("object.add_minimum_spanning_tree")
        layout.operator("object.add_mst_dendrites")

def register():
    registerclasses()
    # Add menu entry
    bpy.types.VIEW3D_MT_mesh_add.append(menu_draw)

def unregister():
    unregisterclasses()
    # Remove menu entry
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_draw)

classes = (
    mst_blender.OBJECT_OT_dendritedelete,
    mst_blender.OBJECT_OT_dendriteadd,
    mst_blender.OBJECT_OT_mstadd,
    VIEW3D_MT_minimum_spanning_tree
)

registerclasses, unregisterclasses = bpy.utils.register_classes_factory(classes)

