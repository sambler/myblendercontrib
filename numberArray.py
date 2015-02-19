
# based on original code from
# http://blender.stackexchange.com/questions/25939/is-it-possible-to-create-an-incremental-array
# made into addon by Shane Ambler

bl_info = {
    "name": "Number Array",
    "author": "Stacker",
    "version": (1, 0),
    "blender": (2, 70, 0),
    "location": "3DView > Add > Curve > Number Array",
    "description": "Add an array of text number objects.",
    "warning": "",
    "wiki_url": "https://github.com/sambler/myblendercontrib/blob/master/numberArray.py",
    "tracker_url": "https://github.com/sambler/myblendercontrib/issues",
    "category": "Add Curve"}

import bpy,math

from bpy.props import IntProperty,FloatProperty,EnumProperty,BoolProperty

class NumberArray(bpy.types.Operator):
    """ Creates an array of text elements"""
    bl_idname = "curve.number_array"
    bl_label = "Number Array"
    bl_options = {'REGISTER', 'UNDO'}

    start = IntProperty(name="Start",description="Start value",min=0, max=100,default=1 )
    count = IntProperty(name="Count",description="Number of items to create",min=1, max=100, default=12  )
    offset = FloatProperty(name="Offset",description="Distance",min=0.01, max=100.0, default=1.0 )
    rotate  = BoolProperty(name="Circular",description="Rotate Elements",default=False)

    all_fonts = []
    for afont in bpy.data.fonts:
        all_fonts.append(( afont.name, afont.name,""))
    if len(all_fonts) == 0:
        all_fonts.append(("Bfont","Bfont",""))

    font = EnumProperty( name="Fonts",items=all_fonts,default="Bfont" )

    def execute(self, context):
        x = -self.offset
        y = 0.0
        angle = 2*math.pi+math.pi/4
        angle_step = 2 * math.pi / self.count
        angle = angle - angle_step
        pos = self.start
        end = self.count + self.start
        print(self.font)
        if len(bpy.data.fonts) == 0:
            # if no fonts exist we add and delete a text objet to initiate it
            bpy.ops.object.text_add()
            context.scene.objects.unlink(bpy.data.objects['Text'])
            bpy.data.objects.remove(bpy.data.objects['Text'])

        font_obj = bpy.data.fonts[ self.font ]

        while pos < end:
            if self.rotate:
                cs = math.cos( angle ) * self.offset
                si = math.sin( angle ) * self.offset
                x = cs - si
                y = si + cs
            else:
                x = x + self.offset
            angle = angle - angle_step

            bpy.ops.object.text_add(location=(x, y, 0))
            ob=bpy.context.object
            ob.data.body = str(pos)
            ob.data.font = font_obj
            pos = pos + 1
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(NumberArray.bl_idname, icon='MESH_CUBE')

def register():
    bpy.utils.register_class(NumberArray)
    bpy.types.INFO_MT_curve_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(NumberArray)
    bpy.types.INFO_MT_curve_add.remove(menu_func)

if __name__ == "__main__":
    register()

