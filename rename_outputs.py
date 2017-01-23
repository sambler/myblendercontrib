bl_info = {
    "name": "Rename outputs",
    "author": "Tal Hershkovich ",
    "version": (0, 1),
    "blender": (2, 72, 0),
    "location": "View3D > Tool Shelf > Render > Rename Outputs",
    "description": "replace strings of outputs in render output and compositing output nodes",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Render/Rename_Outputs",
    "category": "Render"}

import bpy
   
def replace_outputs(self, context):
    old_str = bpy.context.scene.old_string
    new_str = bpy.context.scene.new_string
    for scene in bpy.data.scenes:
        
        if scene.use_nodes:
            
            for node in scene.node_tree.nodes:
                if node.type == 'OUTPUT_FILE':
                    node.base_path = node.base_path.replace(old_str, new_str)          
                    node.file_slots[0].path = node.file_slots[0].path.replace(old_str, new_str)
                
        scene.render.filepath = scene.render.filepath.replace(old_str, new_str)
        
class Rename_Output(bpy.types.Operator):
    """Rename a string in all your render and compositing outputs"""
    bl_label = "Rename outputs"
    bl_idname = "rename.outputs"
    bl_options = {'REGISTER', 'UNDO'}  
    
    bpy.types.Scene.old_string = bpy.props.StringProperty(name="Old String", description="The string that you want to be replaced")
    
    bpy.types.Scene.new_string = bpy.props.StringProperty(name="New String", description="The string that you want to be replaced")
        
    def execute(self, context):
        replace_outputs(self, context)
        return {'FINISHED'} 
    
class Rename_Output_Panel(bpy.types.Panel):
    """Add random value to selected keyframes"""
    bl_label = "Rename Outputs"
    bl_idname = "renameoutputs.panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Render"
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Rename Outputs")
        layout.operator("rename.outputs")
        layout.prop(context.scene, 'old_string')
        layout.prop(context.scene, 'new_string')        

def register():
    bpy.utils.register_class(Rename_Output)
    bpy.utils.register_class(Rename_Output_Panel)

def unregister():
    bpy.utils.unregister_class(Rename_Output)
    bpy.utils.unregister_class(Rename_Output_Panel)

if __name__ == "__main__":
    register()                                  