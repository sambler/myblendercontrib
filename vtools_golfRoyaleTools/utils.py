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
        
        cID = bpy.data.collections.find("AREA_MESH")
        if cID == -1:
            gc = bpy.data.collections.new(name="AREA_MESH")
            bpy.context.scene.collection.children.link(gc)
            
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
                gameField.moveObjectToCollection(no,"AREA_MESH")
                
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
    
    def joinAreaMesh(self):
        
        bpy.ops.object.select_all(action='DESELECT')
        
        cId = bpy.data.collections.find("AREA_MESH")
        if cId != -1:
            oc = bpy.data.collections[cId].objects
            for obj in oc:
                obj.select_set(state=True)
                bpy.context.view_layer.objects.active = obj
            
        bpy.ops.object.join()
        bpy.context.scene.ct_fieldToExport = bpy.data.objects[bpy.context.object.name]   
                      
    def execute(self, context):
        
        gameField.collectionHide_set("AREA_MESH", False)
        
        self.createExportCollection()
        self.duplicateAndApply()
        self.joinAreaMesh()
        
        gameField.collectionHide_set("AREA_INGAME", True)
        
            
        return {'FINISHED'}  


class VTOOLS_OP_AddEditNormal(bpy.types.Operator):
    bl_idname = "camperotools.addeditnormal"
    bl_label = "Add Edit Normal Target"
    bl_description = "Add edit normal modifier"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    def createVertexGroup(self, pObj, pName):
        
        if pObj.vertex_groups.find(pName) == -1:
            pObj.vertex_groups.new(name=pName)
        
        
    def addEditModifier(self):
        
        vgname = "border"
        cAreaLinesId = bpy.data.collections.find("AREA_MESH")
        if cAreaLinesId != -1:
            oc = bpy.data.collections[cAreaLinesId].objects
            for obj in oc:
                obj.data.use_auto_smooth = True
                self.createVertexGroup(obj,vgname)
                mod = obj.modifiers.new(name="normalEdit", type="NORMAL_EDIT")
                mod.target = bpy.context.scene.ct_fieldNormalTarget
                mod.mode = "DIRECTIONAL"
                mod.vertex_group = vgname
                                     
                  
    def execute(self, context):
        
        self.addEditModifier()    
        return {'FINISHED'}  
    


def register():
    
    bpy.utils.register_class(VTOOLS_OP_ApplyFieldModifiers)
    bpy.utils.register_class(VTOOLS_OP_AddEditNormal)
    
    bpy.types.Scene.ct_splineAreaDetail = bpy.props.IntProperty(default = 8, min = 1, max = 64, update=cb_updateSplineAreaDetail)
    
    
    return {'FINISHED'}

def unregister():
    
    bpy.utils.unregister_class(VTOOLS_OP_ApplyFieldModifiers)
    bpy.utils.unregister_class(VTOOLS_OP_AddEditNormal)
    
    del bpy.types.Scene.ct_splineAreaDetail 
     
    return {'FINISHED'}