import bpy

# ----- UI -------#
class VTOOLS_UL_fieldAreaUI(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        
        col = layout.column(align=True)
        col.scale_x = 0.3
        col.label(text=str(item.fieldAreaID))
        
        box = layout.box()
        col = box.column(align=True)
        col.prop(item, "fieldAreaObject", text="", emboss=True, translate=False)
        col.prop(item, "fieldAreaBunker", text="", emboss=True, translate=False)
        col.prop(item, "fieldAreaMaterial", text="", emboss=True, translate=False)
        
         
class VTOOLS_CC_fieldAreaType(bpy.types.PropertyGroup):
       
    name = bpy.props.StringProperty(default='')
    fieldAreaID = bpy.props.IntProperty()
    fieldAreaObject = bpy.props.PointerProperty(name="", type=bpy.types.Object)
    fieldAreaBool = bpy.props.PointerProperty(name="", type=bpy.types.Object)
    fieldAreaBunker = bpy.props.PointerProperty(name="", type=bpy.types.Object)
    fieldAreaBunkerBool = bpy.props.PointerProperty(name="", type=bpy.types.Object)
    fieldAreaMaterial = bpy.props.PointerProperty(name="", type=bpy.types.Material)
    

#---- OPERATORS --------#


class VTOOLS_OP_fieldAreaADD(bpy.types.Operator):
    bl_idname = "camperotools.fieldareaadd"
    bl_label = "Add Field Area"
    bl_description = "Add a new field area"
    bl_options = {'REGISTER', 'UNDO'}
    
    def addAreaLinesCollection(self):
        cId = bpy.data.collections.find("AREA_LINES")
        if cId == -1:
            gc = bpy.data.collections.new(name="AREA_LINES")
            bpy.context.scene.collection.children.link(gc) 
            
    def execute(self, context):
        
        for o in bpy.context.selected_objects:
        
            cl = bpy.context.scene.ct_fieldAreaCollection_ID
            nl = bpy.context.scene.ct_fieldAreaCollection.add()
            bpy.context.scene.ct_fieldAreaCollection_ID += 1
            
            nl.fieldAreaID = bpy.context.scene.ct_fieldAreaCollection_ID
            
            if len(bpy.context.selected_objects) != 0:
                nl.fieldAreaObject = o
            
        return {'FINISHED'}

class VTOOLS_OP_fieldAreaREMOVE(bpy.types.Operator):
    bl_idname = "camperotools.fieldarearemove"
    bl_label = "Remove Field Area"
    bl_description = "Remove selected field area"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        cl = bpy.context.scene.ct_fieldAreaCollection_ID
        bpy.context.scene.ct_fieldAreaCollection.remove(bpy.context.scene.ct_fieldAreaCollection_ID)
        bpy.context.scene.ct_fieldAreaCollection_ID -= 1
        
        if len(bpy.context.scene.ct_fieldAreaCollection) > 0 and bpy.context.scene.ct_fieldAreaCollection_ID == -1:
            bpy.context.scene.ct_fieldAreaCollection_ID = 0
        
        cont = 0
        for item in bpy.context.scene.ct_fieldAreaCollection:
            item.fieldAreaID = cont
            cont += 1
            
            
        return {'FINISHED'} 

class VTOOLS_OP_fieldAreaMOVE(bpy.types.Operator):
    bl_idname = "camperotools.fieldareamove"
    bl_label = "Move Field Area"
    bl_description = "Move selected field area"
    bl_options = {'REGISTER', 'UNDO'}
    
    UP = bpy.props.BoolProperty()
    
    def execute(self, context):
        
        
        af = cl = bpy.context.scene.ct_fieldAreaCollection 
        cl = bpy.context.scene.ct_fieldAreaCollection_ID
    
        if cl != -1:
            ci = af[cl]

            if self.UP == True:
                if cl > 0:      
                    upArea = af[cl - 1].fieldAreaObject
                    af[cl -1].fieldAreaObject = af[cl].fieldAreaObject
                    af[cl].fieldAreaObject = upArea
                    
                    bpy.context.scene.ct_fieldAreaCollection_ID -= 1
        
                    if len(bpy.context.scene.ct_fieldAreaCollection) > 0 and bpy.context.scene.ct_fieldAreaCollection_ID == -1:
                        bpy.context.scene.ct_fieldAreaCollection_ID = 0
                    
            else:
                if cl < len(af)-1:      
                    cArea = af[cl].fieldAreaObject
                    af[cl].fieldAreaObject = af[cl+1].fieldAreaObject
                    af[cl+1].fieldAreaObject = cArea
                    
                    bpy.context.scene.ct_fieldAreaCollection_ID += 1
                
            
            
        return {'FINISHED'}  
    
def register():
    
    bpy.utils.register_class(VTOOLS_UL_fieldAreaUI)
    bpy.utils.register_class(VTOOLS_CC_fieldAreaType)
    bpy.utils.register_class(VTOOLS_OP_fieldAreaADD)
    bpy.utils.register_class(VTOOLS_OP_fieldAreaREMOVE)
    bpy.utils.register_class(VTOOLS_OP_fieldAreaMOVE)
    
    bpy.types.Scene.ct_fieldAreaCollection_ID = bpy.props.IntProperty(default = -1)
    bpy.types.Scene.ct_fieldAreaCollection = bpy.props.CollectionProperty(type=VTOOLS_CC_fieldAreaType)
    

    return {'FINISHED'}

def unregister():
    
    bpy.utils.unregister_class(VTOOLS_UL_fieldAreaUI)
    bpy.utils.unregister_class(VTOOLS_CC_fieldAreaType)
    bpy.utils.unregister_class(VTOOLS_OP_fieldAreaADD)
    bpy.utils.unregister_class(VTOOLS_OP_fieldAreaREMOVE)
    bpy.utils.unregister_class(VTOOLS_OP_fieldAreaMOVE)
    
    
    del bpy.types.Scene.ct_fieldAreaCollection_ID
    del bpy.types.Scene.ct_fieldAreaCollection
    

     
    return {'FINISHED'}