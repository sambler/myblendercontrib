import bpy
from vtools_multiLayerPainting import createNodes
from vtools_multiLayerPainting import paintingLayers


#-- DEF ---

def addLayerSetTree(pNewSet):
    newSet = bpy.context.scene.mlpLayerSetsCollection.add()
    newSet.layerSetName = pNewSet.name
    newSet.name = pNewSet.label
    
    bpy.context.scene.mlpLayerSetsCollection_ID = len(bpy.context.scene.mlpLayerSetsCollection) - 1


def isLayerSet(pNode):
    
    res = False
    if pNode != None:
        if pNode.type == "GROUP" and pNode.node_tree != None:
            if pNode.node_tree.name.find("MTLayerSet") != -1:
                res = True
            
    return res

def getSelectedLayerSetNode():
    
    layerSetNode = None
    
    if bpy.context.scene.mlpLayerSetsCollection_ID != -1:
       mainTree = bpy.context.object.active_material.node_tree
       lsName = bpy.context.scene.mlpLayerSetsCollection[bpy.context.scene.mlpLayerSetsCollection_ID].layerSetName
       
       layerSetNode = mainTree.nodes[lsName]
       
    return layerSetNode
       
    
# --- CLASSES --------

class VTOOLS_OP_CollectPaintingSets(bpy.types.Operator):
    bl_idname = "vtoolpt.collectpaintingsets"
    bl_label = "Collect Painting Sets"
    bl_description = "Collect Scene Painting Sets"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.ed.undo_push()
        createNodes.init()
        
        mainTree = bpy.context.object.active_material.node_tree
        
        bpy.context.scene.mlpLayerSetsCollection.clear()
        bpy.context.scene.mlpLayerSetsCollection_ID = -1
    
        for n in mainTree.nodes:
            if isLayerSet(n) == True:
                addLayerSetTree(n)
        
        bpy.context.scene.mlpLayerSetsCollection_ID = len(bpy.context.scene.mlpLayerSetsCollection) - 1
        bpy.context.scene.vt_mpPaintActiveMaterial = bpy.context.object.active_material.name
        
        return {'FINISHED'}
    

class VTOOLS_OP_DeletePaintingSet(bpy.types.Operator):
    bl_idname = "vtoolpt.deletepaintingset"
    bl_label = "Delete Painting Set"
    bl_description = "Delete selected painting set"
    bl_options = {'REGISTER', 'UNDO'}
    
    def deletePaintingLayers(self):
        
        bpy.context.scene.mlpLayerTreeCollection_ID = 0
        
        while len(bpy.context.scene.mlpLayerTreeCollection) > 0:
            bpy.context.scene.mlpLayerTreeCollection_ID = 0
            bpy.ops.vtoolpt.deletepaintinglayer()
            
        bpy.context.scene.mlpLayerTreeCollection_ID = -1
        
    def deleteLayerSet(self):
        
        mainTree = bpy.context.object.active_material.node_tree
        
        self.deletePaintingLayers()
        lsn = getSelectedLayerSetNode()
        
        if lsn != None:
            currentSelected = bpy.context.scene.mlpLayerSetsCollection_ID
            bpy.data.node_groups.remove(lsn.node_tree)
            mainTree.nodes.remove(lsn) 
            bpy.context.scene.mlpLayerSetsCollection.remove(bpy.context.scene.mlpLayerSetsCollection_ID)
            
            if currentSelected == 0 and len(bpy.context.scene.mlpLayerSetsCollection) > 0:
                    bpy.context.scene.mlpLayerSetsCollection_ID = 0
            else: 
                bpy.context.scene.mlpLayerSetsCollection_ID = currentSelected -1    
        
        return {'FINISHED'}
            
    def execute(self, context):
        bpy.ops.ed.undo_push()
        self.deleteLayerSet()
        return {'FINISHED'}
        
class VTOOLS_OP_AddPaintingSet(bpy.types.Operator):
    bl_idname = "vtoolpt.createpaintingset"
    bl_label = "Add Painting Set"
    bl_description = "Add a new painting set"
    bl_options = {'REGISTER', 'UNDO'}
    
    def addLayerSet(self,pName):
        
        newLayerSet = None
        
        if bpy.data.node_groups.find(pName) == -1:
            bpy.ops.vtoolpt.collectpaintingsets()  
        
        mainTree = bpy.context.object.active_material.node_tree
        newLayerSet = bpy.context.object.active_material.node_tree
        newLayerSet = mainTree.nodes.new(type="ShaderNodeGroup")
        newLayerSet.node_tree = bpy.data.node_groups[pName].copy()   
        newLayerSet.name = "layerSet"
        newLayerSet.label = "layerSet"
        
        return newLayerSet
   
    def execute(self, context):
        bpy.ops.ed.undo_push()
        newSet = self.addLayerSet(bpy.context.scene.vt_layerSetNodeType)
        addLayerSetTree(newSet)
        newSet.location[0] = 200*len(bpy.context.scene.mlpLayerSetsCollection)
        
        return {'FINISHED'}

class VTOOLS_OP_DuplicatePaintingSet(bpy.types.Operator):
    bl_idname = "vtoolpt.duplicatepaintingset"
    bl_label = "Duplicate Painting Set"
    bl_description = "Duplicate the selected painting set"
    bl_options = {'REGISTER', 'UNDO'}
    
    def duplicateLayerSet(self,pLayerSetNode):
        
        newLayerSet = None
        
        if pLayerSetNode != None:
        
            mainTree = bpy.context.object.active_material.node_tree
            newLayerSet = mainTree.nodes.new(type="ShaderNodeGroup")
            newLayerSet.node_tree = bpy.data.node_groups[pLayerSetNode.node_tree.name].copy()   
            newLayerSet.name = "layerSet"
            newLayerSet.label = "Copy_" + pLayerSetNode.label
        
        return newLayerSet
    
    def makeSetUnique(self, pLayerSetNode):
        
        for n in pLayerSetNode.node_tree.nodes:
            if n.type == "GROUP":
                if n.node_tree.name.find(bpy.context.scene.vt_paintLayerNodeType) != -1:
                    n.node_tree = bpy.data.node_groups[n.node_tree.name].copy()   
   
   
    def execute(self, context):
        bpy.ops.ed.undo_push()
        layerSetNode = getSelectedLayerSetNode()
        
        if layerSetNode != None:
            newSet = self.duplicateLayerSet(layerSetNode)
            addLayerSetTree(newSet)
            newSet.location[0] = 200*len(bpy.context.scene.mlpLayerSetsCollection)
            self.makeSetUnique(newSet)
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(VTOOLS_OP_AddPaintingSet)
    bpy.utils.register_class(VTOOLS_OP_DeletePaintingSet)
    bpy.utils.register_class(VTOOLS_OP_CollectPaintingSets)
    bpy.utils.register_class(VTOOLS_OP_DuplicatePaintingSet)
    return {'FINISHED'}
    

def unregister():
   bpy.utils.unregister_class(VTOOLS_OP_AddPaintingSet)
   bpy.utils.unregister_class(VTOOLS_OP_DeletePaintingSet)
   bpy.utils.unregister_class(VTOOLS_OP_CollectPaintingSets)
   bpy.utils.unregister_class(VTOOLS_OP_DuplicatePaintingSet)
   return {'FINISHED'}
    

classes = (
    
    VTOOLS_OP_AddPaintingSet,
)
