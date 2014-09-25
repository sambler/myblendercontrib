import bpy
mat = bpy.data.materials["Yellow"]
mat.name = "tmp"
mat.user_clear()
with bpy.data.libraries.load("D:\\RED\\Scripting\\matlib\\matlibvx1.blend") as (data_from, data_to):
 data_to.materials = ["Yellow"]
mat = bpy.data.materials["Yellow"]
mat.use_fake_user=True
bpy.ops.wm.save_mainfile(filepath="D:\\Blender258\\2.58\\scripts\\addons\\matlib\\materials.blend", check_existing=False, compress=True)
