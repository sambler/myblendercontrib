bl_info = {
    "name": "Multikey",
    "author": "Tal Hershkovich ",
    "version": (0, 3),
    "blender": (2, 80, 0),
    "location": "3DView",
    "description": "Edit Multiply Keyframes by adjusting their value or randomizing it",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Animation/Multikey",
    "category": "Animation"}

import bpy
import random

def store_handles(key):
    #storing the distance between the handles bezier to the key value
    handle_r = key.handle_right[1] - key.co[1]
    handle_l = key.handle_left[1] - key.co[1]
    
    return handle_r, handle_l

def apply_handles(key, handle_r, handle_l):
    if bpy.context.scene.handletype == True:
         key.handle_right[1] = key.co[1] + handle_r
         key.handle_left[1] = key.co[1] + handle_l
    else:
        key.handle_right_type = "AUTO_CLAMPED"
        key.handle_left_type = "AUTO_CLAMPED"
                
def check_selected_bones(obj):
    if  bpy.context.scene.selectedbones == True:
            bonelist = []
            for knochen in obj.pose.bones:
                if knochen.bone.select == True:
                    bonelist.append(knochen)
    else:
        bonelist = obj.pose.bones
    return bonelist

def check_fcurve(function):
    #checking the selected fcurve and applying the function to it
    objects = bpy.context.selected_objects
    
    for obj in objects:
    
        if obj.animation_data.action is not None:
            action = obj.animation_data.action
            for fcu in action.fcurves:
                if obj.type == 'ARMATURE':
                    bonelist = check_selected_bones(obj) 
                    for bone in bonelist:
                        #find the fcurve of the bone
                        if fcu.data_path.rfind(bone.name) == 12 and fcu.data_path[12 + len(bone.name)] == '"':
                            function(fcu)                           
                else:
                    function(fcu)
        
def add_value(key, value):
    if key.select_control_point == True:
            #store handle values in relative to the keyframe value
            handle_r, handle_l = store_handles(key)              
            
            key.co[1] += value
            apply_handles(key, handle_r, handle_l)
                
#calculate the difference between current value and the fcurve value                
def add_diff(fcu, current_value, index):    
    value = current_value[index] - fcu.evaluate(bpy.context.scene.frame_current)
    if value != 0:
        for key in fcu.keyframe_points:
            add_value(key, value)
        fcu.update()
        
def scale_value(fcu):
    value_list = []
    scale = bpy.context.scene.scalevalues
    for key in fcu.keyframe_points: 
        if key.select_control_point == True: 
            value_list.append(key.co[1])
    if len(value_list)>1:
        #the average value with the scale property added to it
        avg_value = sum(value_list) / len(value_list)
        for key in fcu.keyframe_points:
            if key.select_control_point == True:
                #store handle_type 
                handle_r, handle_l = store_handles(key)
                #add the value of the distance from the average * scale factor
                key.co[1] = avg_value + ((key.co[1] - avg_value)*scale)
                key = apply_handles(key, handle_r, handle_l)
        fcu.update()
    
def random_value(fcu):
    value_list = []
    threshold = bpy.context.scene.threshold                        
    for key in fcu.keyframe_points: 
        if key.select_control_point == True: 
            value_list.append(key.co[1])
            
    if len(value_list) > 0:
        value = max(value_list)- min(value_list)
        for key in fcu.keyframe_points:
            add_value(key, value * random.uniform(-threshold, threshold))
        fcu.update()
                                
                                    
def evaluate_value(self, context):
    
    for obj in bpy.context.selected_objects:
        
        if obj.animation_data.action is not None:
            action = obj.animation_data.action
            
            for fcu in action.fcurves:     
                index = fcu.array_index
                if obj.type == 'ARMATURE':
                    transformations = ["rotation_quaternion","rotation_euler", "location", "scale"]
                    
                    #add value to the whole armature keyframes
                    if fcu.data_path[0:18] in transformations:
                        current_value = getattr(obj, fcu.data_path)
                        add_diff(fcu, current_value, index)     
                    
                    #add value to bones
                    bonelist = check_selected_bones(obj)
                    for bone in bonelist:
                        
                        #find the fcurve of the bone
                        if fcu.data_path.rfind(bone.name) == 12 and fcu.data_path[12 + len(bone.name)] == '"': 
                            transform = fcu.data_path[15 + len(bone.name):]
                            if transform in transformations:
                                current_value = getattr(obj.pose.bones[bone.name], transform)
                                #calculate the difference between current value and the fcurve value 
                                add_diff(fcu, current_value, index)
                                
             
                else:
                    transform = fcu.data_path
                    current_value = getattr(obj, transform)
                    
                    add_diff(fcu, current_value, index)
                                                    
class RANDOMIZE_OT_RandomizeKeys(bpy.types.Operator):
    """Create Random Keys"""
    bl_label = "Randomize keyframes"
    bl_idname = "fcurves.randomizekeys"
    bl_options = {'REGISTER', 'UNDO'}  
    
    bpy.types.Scene.threshold = bpy.props.FloatProperty(name="Threshold", description="Threshold of keyframes", default=0.1, min=0.0, max = 1.0)
      
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.animation_data
      
    def execute(self, context):
        check_fcurve(random_value)
        return {'FINISHED'} 
    
class SCALE_OT_ScaleValues(bpy.types.Operator):
    """Scale Keyframe Values"""
    bl_label = "Scale Keyframes Values"
    bl_idname = "fcurves.scalevalues"
    bl_options = {'REGISTER', 'UNDO'}  
    
    bpy.types.Scene.scalevalues = bpy.props.FloatProperty(name="Scale Factor", description="Scale percentage of the average value", default=1.0)
      
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.animation_data
      
    def execute(self, context):
        check_fcurve(scale_value)
        return {'FINISHED'} 
                                   
class MULTIKEY_OT_Multikey(bpy.types.Operator):
    """Edit all selected keyframes"""
    bl_label = "Edit Selected Keyframes"
    bl_idname = "fcurves.multikey"
    bl_options = {'REGISTER', 'UNDO'}  
    
    bpy.types.Scene.selectedbones = bpy.props.BoolProperty(name="Affect only selected bones", description="Affect only selected bones", default=True, options={'HIDDEN'})
    
    bpy.types.Scene.handletype = bpy.props.BoolProperty(name="Keep handle types", description="Keep handle types", default=False, options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.animation_data and bpy.context.scene.tool_settings.use_keyframe_insert_auto == False
      
    def execute(self, context):
        evaluate_value(self, context)
        return {'FINISHED'} 
    
class MultikeyPanel(bpy.types.Panel):
    """Add random value to selected keyframes"""
    bl_label = "Multikey"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category= 'Tool'
    
    def draw(self, context): 
        layout = self.layout
        layout.prop(context.scene, 'selectedbones')
        layout.prop(context.scene, 'handletype') 
        layout.separator()
        layout.label(text="Edit all selected keyframes")
        layout.operator("fcurves.multikey")
        layout.separator()
        layout.label(text="Scale Keyframe Values")
        layout.operator("fcurves.scalevalues")
        layout.prop(context.scene, 'scalevalues')
        layout.separator()
        layout.label(text="Randomize selected keyframes")
        layout.operator("fcurves.randomizekeys")
        layout.prop(context.scene, 'threshold', slider = True)       

classes = (MultikeyPanel, MULTIKEY_OT_Multikey, RANDOMIZE_OT_RandomizeKeys, SCALE_OT_ScaleValues)

register, unregister = bpy.utils.register_classes_factory(classes)

'''def register():
    bpy.utils.register_class(Multikey)
    bpy.utils.register_class(ScaleValues)
    bpy.utils.register_class(RandomizeKeys)
    bpy.utils.register_class(Multikey_Panel)

def unregister():
    bpy.utils.unregister_class(Multikey)
    bpy.utils.unregister_class(ScaleValues)
    bpy.utils.unregister_class(RandomizeKeys)
    bpy.utils.unregister_class(Multikey_Panel)'''

if __name__ == "__main__":
    register()                               