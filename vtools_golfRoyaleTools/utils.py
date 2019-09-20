import bpy
from vtools_golfRoyaleTools import gameField

def cb_updateSplineAreaDetail(self,value):
    
    cAreaLinesId = bpy.data.collections.find("AREA_LINES")
    if cAreaLinesId != -1:
        oc = bpy.data.collections[cAreaLinesId].objects
        for obj in oc:
            obj.data.resolution_u = bpy.context.scene.ct_splineAreaDetail


def duplicateObject(pObj):
        
    obj = pObj.copy()
    bpy.context.scene.collection.objects.link(obj)
    obj.data = obj.data.copy()
    
    return obj
    
class VTOOLS_OP_ApplyFieldModifiers(bpy.types.Operator):
    bl_idname = "camperotools.applyfieldmodifiers"
    bl_label = "Apply field modifiers"
    bl_description = "Apply field modifiers"
    bl_options = {'REGISTER', 'UNDO'}
    
    def createExportCollection(self):
        
        cID = bpy.data.collections.find("AREA_TOEXPORT")
        if cID == -1:
            gc = bpy.data.collections.new(name="AREA_TOEXPORT")
            bpy.context.scene.collection.children.link(gc)
    
    def duplicateAndApply(self):
        cAreaLinesId = bpy.data.collections.find("AREA_INGAME")
        if cAreaLinesId != -1:
            oc = bpy.data.collections[cAreaLinesId].objects
            for obj in oc:
                no = duplicateObject(obj)
                gameField.moveObjectToCollection(no,"AREA_TOEXPORT")
                
                no.select_set(state = True)
                bpy.context.view_layer.objects.active = no
                
                for m in no.modifiers:
                    if m.name != "wrap":
                        
                        try:
                            bpy.ops.object.modifier_apply(apply_as='DATA',modifier=m.name)
                        except:
                            no.modifiers.remove(m)
                            #obj_name = getattr(obj, "name", "NO NAME")
                            #collect_names.append(obj_name)
                            #message_b = True
                            pass
                
                
                no.select_set(state = False)                        
                  
    def execute(self, context):
        
        self.createExportCollection()
        self.duplicateAndApply()
            
        return {'FINISHED'}  

def register():
    
    bpy.utils.register_class(VTOOLS_OP_ApplyFieldModifiers)
    
    bpy.types.Scene.ct_splineAreaDetail = bpy.props.IntProperty(default = 8, min = 1, max = 64, update=cb_updateSplineAreaDetail)
    
    
    return {'FINISHED'}

def unregister():
    
    bpy.utils.unregister_class(VTOOLS_OP_ApplyFieldModifiers)
    
    del bpy.types.Scene.ct_splineAreaDetail 
     
    return {'FINISHED'}