bl_info = {
    "name": "Text from file",
    "description": "Set the text object content from a text file.",
    "author": "Chebhou",
    "version": (1,0),
    "blender": (2, 6, 3),
    "location": "3D View > Object > convert text object",
    #"warning": "",
    "wiki_url": "http://blender.stackexchange.com/a/26722/935",
    #"tracker_url": "",
    "category": "3D View"}

import bpy
from bpy.types import Operator  
from bpy.props import *  

def object_to_text():
    obj = bpy.context.active_object
    if obj.type == 'FONT':
       if None == bpy.data.texts.get(obj.name):
          bpy.data.texts.new(name = obj.name)

       text_file = bpy.data.texts[obj.name]
       text_file.clear()
       text = obj.data.body
       text_file.write(text)


def object_from_text():
    obj = bpy.context.active_object
    if obj.type == 'FONT':
       if None == bpy.data.texts.get(obj.name):
          bpy.data.texts.new(name = obj.name)

       text_file = bpy.data.texts[obj.name]
       #clear text_obj
       obj.data.body = text_file.as_string()

class   text_object(Operator):  

    """text file from&to text object"""        
    bl_idname = "object.from_to_text"  
    bl_label = "convert text object"     
    bl_options = {'REGISTER', 'UNDO'}    

    #parameters and variables
    convert = EnumProperty(
                name="Convert",
                description="Choose conversion",
                items=(('T2F', "object to file ", "convert text object to text file"),
                       ('F2T', "file  to object", "convert text file to text object")),
                default='T2F',
                )

    def execute(self, context): 
        if self.convert == 'T2F':
            object_to_text()
        else:
            object_from_text()

        self.report({'INFO'},"Conversion is Done")
        return {'FINISHED'}

    #get inputs 
    def invoke(self, context, event):
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

def addObject(self, context): 
    self.layout.operator(
    text_object.bl_idname,
    text = text_object.bl_label,
    icon = 'OUTLINER_DATA_FONT')

def register():
    bpy.utils.register_class(text_object)      
    bpy.types.VIEW3D_MT_object.append(addObject)

def unregister(): 
    bpy.types.VIEW3D_MT_object.remove(addObject)
    bpy.utils.unregister_class(text_object)

if __name__ == "__main__":  
    register()

