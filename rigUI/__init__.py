bl_info = {
    "name": "Rig UI",
    "author": "Christophe Seux",
    "version": (0, 1),
    "blender": (2, 77, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Rigging"}

if "bpy" in locals():
    import imp
    imp.reload(operators)
    imp.reload(panels)

else:
    from . import operators
    from . import panels

import bpy

def menu_func(self, context):
    self.layout.operator("rigui.ui_draw",icon ='MOD_ARMATURE')


def register():
    bpy.types.Armature.UI = bpy.props.PointerProperty(type= bpy.types.PropertyGroup)
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_HT_header.append(menu_func)



def unregister():
    del bpy.types.Armature.UI
    bpy.types.VIEW3D_HT_header.remove(menu_func)

    bpy.utils.unregister_module(__name__)
