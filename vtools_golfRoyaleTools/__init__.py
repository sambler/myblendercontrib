bl_info = {
    "name": "vtools - Golf Royale Tools",
    "author": "Antonio Mendoza",
    "location": "View3D > Sidebar > View Tab > Campero Tools",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "description": "Tools for Golf Royale game assets",
    "category": "3D View"  
}




if "bpy" in locals():
    import importlib    
    importlib.reload(fieldAreas)
    importlib.reload(gameField)
    importlib.reload(utils)
    
else:
      
    from vtools_golfRoyaleTools import fieldAreas
    from vtools_golfRoyaleTools import gameField
    from vtools_golfRoyaleTools import utils
    
    #remove when releasingp
    import importlib
    importlib.reload(fieldAreas)  
    importlib.reload(gameField)
    importlib.reload(utils) 

 
modules = (fieldAreas,gameField,utils) 
   
def getCollectionByName(pCollName):
    
    res = None
    
    if bpy.data.collections.find(pCollName) != -1:
        res = bpy.data.collections[pCollName]

    return res


import bpy        
        
class VTOOLS_PT_GolfRoyaleTools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Golf Royale"
    bl_category = 'Campero Tools '
    bl_options = {'DEFAULT_CLOSED'}       
        
    @classmethod
    def poll(cls, context):
        
        return (context.mode == 'OBJECT')
        #return (context.object)
    
    def draw(self,context):
        enabled = True
        layout = self.layout
        
        layout.prop(bpy.context.scene, "ct_fieldBaseHP")
        bm = bpy.context.scene.ct_fieldBaseHP
        
        if bm == None:    
            enabled = False
        
        layout.label(text="Field Areas:")
            
        row = layout.row()
        row.enabled = enabled
        
        col = row.column()
        row.template_list('VTOOLS_UL_fieldAreaUI', "fieldAreaID", context.scene, "ct_fieldAreaCollection", context.scene, "ct_fieldAreaCollection_ID", rows=4)
        
        col = row.column(align=True)
        col.operator(fieldAreas.VTOOLS_OP_fieldAreaADD.bl_idname, text="",icon='ADD')
        col.operator(fieldAreas.VTOOLS_OP_fieldAreaREMOVE.bl_idname, text="",icon='REMOVE')
        
        opUP = col.operator(fieldAreas.VTOOLS_OP_fieldAreaMOVE.bl_idname, text="",icon='TRIA_UP')
        opUP.UP = True
        opDN = col.operator(fieldAreas.VTOOLS_OP_fieldAreaMOVE.bl_idname, text="",icon='TRIA_DOWN')
        opDN.UP = False
        
        col = layout.column(align=True)
        col.prop(context.scene,"ct_numPieces", text="X Chunk Count")
        col.operator(gameField.VTOOLS_OP_fielGenerate.bl_idname, text="Generate Base",icon='ADD')
        col.operator(gameField.VTOOLS_OP_resetFieldGolf.bl_idname, text="Reset Base Field",icon='REMOVE')
        
        layout.label(text = "In Game Field:")
        col = layout.column(align=False)
        col.enabled = bpy.context.scene.ct_fieldBaseLP != None
        col.prop(bpy.context.scene, "ct_fieldBaseLP", text="")
        
        col = layout.column(align=True)
        col.prop(context.scene,"ct_fieldDetail", text="Mesh Detail")
        col.prop(context.scene,"ct_splineAreaDetail", text="Area Detail")
        
        col = layout.column()
        col.operator(gameField.VTOOLS_OP_cutFieldByAreas.bl_idname, text="Generate Game Field", icon="NODE")
        
        layout.separator()
        layout.label(text = "Export setup:")
        col = layout.column()
        col.operator(utils.VTOOLS_OP_ApplyFieldModifiers.bl_idname, text="Duplicate and Apply Modifiers",icon='MODIFIER')
        
        
# -- REGISTRATION -- #        

def register():
    
    from bpy.utils import register_class
    
    #CLASES
    bpy.utils.register_class(VTOOLS_PT_GolfRoyaleTools)
    #PROP
    bpy.types.Scene.ct_fieldBaseHP = bpy.props.PointerProperty(name="Base Mesh", type=bpy.types.Object)
    
    
    #submodules
    for mod in modules:
        mod.register()    
    
def unregister():
    from bpy.utils import unregister_class
    
    #CLASES
    bpy.utils.unregister_class(VTOOLS_PT_GolfRoyaleTools)
    
    #PROP
    del bpy.types.Scene.ct_fieldBaseHP
       
    #submodules
    for mod in modules:
        mod.unregister()
    
    
    
if __name__ == '__main__':
    register()
    