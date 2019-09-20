import bpy
from vtools_multiLayerPainting import paintingLayers

#-- TYPES --

filterTypes = [
    ["RGB Curves","ShaderNodeRGBCurve", "Color", "Color"], 
    ["Hue/Saturation","ShaderNodeHueSaturation", "Color", "Color"],
    ["ColorRamp","ShaderNodeValToRGB", "Fac", "Color"],
    ["Gamma","ShaderNodeGamma","Color","Color"],
    ["Invert","ShaderNodeInvert","Color","Color"],
    ["Bright/Contrast","ShaderNodeBrightContrast","Color","Color"],
    ["RGB to BW","ShaderNodeRGBToBW","Color", "Val"],
    ]

    
    
#-- DEF ---

def getFilterNodeSelected():
    
    filterNode = None
    layerNode = paintingLayers.getLayerNodeSelected()
    filterId = bpy.context.scene.mlpFilterLayerCollection_ID

    if filterId != -1 and filterId < len(bpy.context.scene.mlpFilterLayerCollection):
        if layerNode != None:
            filterIdName = bpy.context.scene.mlpFilterLayerCollection[filterId].filterLayerName
            filterNode = layerNode.node_tree.nodes[filterIdName]
        
    return filterNode

def getFilterNodeSelectedById(pId):
    
    filterNode = None
    layerNode = paintingLayers.getLayerNodeSelected()
    filterId = pId

    if filterId != -1 and filterId < len(bpy.context.scene.mlpFilterLayerCollection):
        if layerNode != None:
            filterIdName = bpy.context.scene.mlpFilterLayerCollection[filterId].filterLayerName
            filterNode = layerNode.node_tree.nodes[filterIdName]
    
    return filterNode




def isFilterNode(pNode):
    
    res = False
    if pNode != None:
        if pNode.name.find("MLPFilterNode") != -1:
            res = True
    return res

def addFilterToTree(pFilterNode):
        
        filterSlot = bpy.context.scene.mlpFilterLayerCollection.add()
        filterSlot.name = pFilterNode.label
        filterSlot.filterLayerName = pFilterNode.name
        
        newFilterId = len(bpy.context.scene.mlpFilterLayerCollection) - 1
        targetFilterId = bpy.context.scene.mlpFilterLayerCollection_ID + 1
        
        if targetFilterId > newFilterId:
            targetFilterId = newFilterId
            
        bpy.context.scene.mlpFilterLayerCollection.move(newFilterId,targetFilterId)
        bpy.context.scene.mlpFilterLayerCollection_ID = targetFilterId
        
def getFilterNodeType(pFilterNode):
    
    res = None
    
    if isFilterNode(pFilterNode):
        for ft in filterTypes:
            if ft[1] == pFilterNode.bl_idname:
                res = ft
    
    return res
                
def getNextFilterNode(pFilterNode, pFilterType):
    
    toNode = None
    toSocket = None
    fl = pFilterNode.outputs[pFilterType[3]].links
    
    if len(fl) > 0:
        toNode = fl[0].to_node
        toSocket = fl[0].to_socket.name
        
    return toNode

def getPrevFilterNode(pFilterNode, pFilterType):
    
    fromNode = None
    fromSocket = None
    fl = pFilterNode.inputs[pFilterType[2]].links
    
    if len(fl) > 0:
        fromNode = fl[0].from_node
        fromSocket = fl[0].from_socket.name
        
    return fromNode

def getFirstFilterNode():
    
    layerNode = paintingLayers.getLayerNodeSelected()
    firstFilterNode = None
    
    if layerNode != None:
        filtersInitNode = layerNode.node_tree.nodes["PL_filtersColorInput"]
        firstFilterNode = filtersInitNode.outputs[0].links[0].to_node
        
        if isFilterNode(firstFilterNode) == False:
            firstFilterNode = None
    
    
    return firstFilterNode
     
def getFilterInputName(pFilterNode):
    
    input = None
    fSelType = getFilterNodeType(pFilterNode)
    if fSelType != None:
        input = fSelType[2]
    
    return input

def getFilterOutputName(pFilterNode):
    
    output = None
    fSelType = getFilterNodeType(pFilterNode)
    if fSelType != None:
        output = fSelType[3]
    
    return output

        
# --- CLASSES --------

class VTOOLS_OP_MoveLayerFilter(bpy.types.Operator):
    bl_idname = "vtoolpt.movelayerfilter"
    bl_label = "move Filter"
    bl_description = "Move Fitler"
    bl_options = {'REGISTER', 'UNDO'}
    
    direction = bpy.props.StringProperty()
    
    def moveUP(self):
        
        layerNode = paintingLayers.getLayerNodeSelected()
        filterNode = getFilterNodeSelected()
        selOutputName = getFilterOutputName(filterNode)
        selInputName = getFilterInputName(filterNode)
        
        numFilters = len(bpy.context.scene.mlpFilterLayerCollection)
        fsId = bpy.context.scene.mlpFilterLayerCollection_ID
        
        if fsId < numFilters-1:
            
            if layerNode != None:
            
                prevFilter = getFilterNodeSelectedById(fsId-1)
                prevOutputName = ""
                
                if prevFilter != None:
                    prevOutputName = getFilterOutputName(prevFilter)
                else:
                    prevFilter = layerNode.node_tree.nodes["PL_filtersColorInput"]
                    prevOutputName = "Output"
                
                nextFilter = getFilterNodeSelectedById(fsId+1)
                nextInputName = ""
                nextOutputName = ""
                 
                if nextFilter != None:
                    nextInputName = getFilterInputName(nextFilter)
                    nextOutputName = getFilterOutputName(nextFilter)
                else:
                    nextFilter = layerNode.node_tree.nodes["PL_filtersColorOutput"]
                    nextInputName = "Input"
                    prevOutputName = "Output"
                    
                
                upperFilter = getFilterNodeSelectedById(fsId+2)
                upperInputName = ""
                
                if upperFilter != None:
                    upperInputName = getFilterInputName(upperFilter)
                else:
                    upperFilter = layerNode.node_tree.nodes["PL_filtersColorOutput"]
                    upperInputName = "Input"
                     
                paintingLayers.removeNodeLinks(layerNode.node_tree, filterNode, selOutputName)
                paintingLayers.removeNodeLinks(layerNode.node_tree, prevFilter, prevOutputName)
                
                layerNode.node_tree.links.new(prevFilter.outputs[prevOutputName], nextFilter.inputs[nextInputName])
                layerNode.node_tree.links.new(nextFilter.outputs[nextOutputName], filterNode.inputs[selInputName])
                layerNode.node_tree.links.new(filterNode.outputs[selOutputName], upperFilter.inputs[upperInputName])
                
            bpy.ops.vtoolpt.collectlayerfilter()
            bpy.context.scene.mlpFilterLayerCollection_ID = fsId + 1
        
        
                
        return {'FINISHED'}
    
    def moveDN(self):
        
        layerNode = paintingLayers.getLayerNodeSelected()
        filterNode = getFilterNodeSelected()
        selOutputName = getFilterOutputName(filterNode)
        selInputName = getFilterInputName(filterNode)
        
        numFilters = len(bpy.context.scene.mlpFilterLayerCollection)
        fsId = bpy.context.scene.mlpFilterLayerCollection_ID
        
        if fsId > 0:
            
            if layerNode != None:
            
                prevFilter = getFilterNodeSelectedById(fsId-1)
                prevInputName = ""
                prevOutputName = ""
                
                if prevFilter != None:
                    prevInputName = getFilterInputName(prevFilter)
                    prevOutputName = getFilterOutputName(prevFilter)
                else:
                    prevFilter = layerNode.node_tree.nodes["PL_filtersColorInput"]
                    prevInputName = "Input"
                    prevOutputName = "Output"
                
                nextFilter = getFilterNodeSelectedById(fsId+1)
                nextInputName = ""
                nextOutputName = ""
                 
                if nextFilter != None:
                    nextInputName = getFilterInputName(nextFilter)
                    nextOutputName = getFilterOutputName(nextFilter)
                else:
                    nextFilter = layerNode.node_tree.nodes["PL_filtersColorOutput"]
                    nextInputName = "Input"
                    nextOutputName = "Output"
                    
                
                lowerFilter = getFilterNodeSelectedById(fsId-2)
                lowerOutputName = ""
                
                if lowerFilter != None:
                    lowerOutputName = getFilterOutputName(lowerFilter)
                else:
                    lowerFilter = layerNode.node_tree.nodes["PL_filtersColorInput"]
                    lowerOutputName = "Output"
                    
                
                #paintingLayers.removeNodeLinks(layerNode.node_tree, filterNode, selOutputName)
                #paintingLayers.removeNodeLinks(layerNode.node_tree, prevFilter, prevOutputName)
                
                
                layerNode.node_tree.links.new(filterNode.inputs[selInputName], lowerFilter.outputs[lowerOutputName])
                layerNode.node_tree.links.new(filterNode.outputs[selOutputName], prevFilter.inputs[prevInputName])
                layerNode.node_tree.links.new(prevFilter.outputs[prevOutputName], nextFilter.inputs[nextInputName])
                
                
            bpy.ops.vtoolpt.collectlayerfilter()
            bpy.context.scene.mlpFilterLayerCollection_ID = fsId - 1
        
        return {'FINISHED'}
        
    def execute(self, context):
        
        bpy.ops.ed.undo_push()
        if self.direction == "UP":
            self.moveUP()
        else:
            self.moveDN()
            
        return {'FINISHED'}
    
    
    
class VTOOLS_OP_CollectLayerFilter(bpy.types.Operator):
    bl_idname = "vtoolpt.collectlayerfilter"
    bl_label = "Collect Layer Filter"
    bl_description = "Collect Fitlers from Selected Layer"
    
    
    def execute(self, context):
        
        layerNode = paintingLayers.getLayerNodeSelected()
        fNode = getFirstFilterNode()
        
        bpy.context.scene.mlpFilterLayerCollection.clear()
        bpy.context.scene.mlpFilterLayerCollection_ID = -1
        
        cont = 0
        while isFilterNode(fNode) == True and fNode != None: 
            fNode.location = (300*cont, 500)
            addFilterToTree(fNode)
            fSelType = getFilterNodeType(fNode)
            fNode = getNextFilterNode(fNode, fSelType)
            cont = cont + 1
            
        return {'FINISHED'}
    

class VTOOLS_OP_DeleteLayerFilter(bpy.types.Operator):
    bl_idname = "vtoolpt.deletelayerfilter"
    bl_label = "Delete Layer Filter"
    bl_description = "Delete Selected Filter from layer"
    bl_options = {'REGISTER', 'UNDO'}
    
    def deleteFilterFromTree(self):
        
        fsId = bpy.context.scene.mlpFilterLayerCollection_ID
        
        if fsId != -1:
            bpy.context.scene.mlpFilterLayerCollection.remove(fsId)
            bpy.context.scene.mlpFilterLayerCollection_ID = fsId - 1
            
            #select layer
            if len(bpy.context.scene.mlpFilterLayerCollection) > 0 and bpy.context.scene.mlpFilterLayerCollection_ID  == -1:
                bpy.context.scene.mlpFilterLayerCollection_ID = 0
                
        return {'FINISHED'}
    
    def deleteFilterNode(sefl):
        
        layerNode = paintingLayers.getLayerNodeSelected()
        filterNode = getFilterNodeSelected()
        filterType = getFilterNodeType(filterNode)
        layerNode.node_tree.nodes.remove(filterNode)
        
        
    def bridgeFilterNodes(self):
        
        layerNode = paintingLayers.getLayerNodeSelected()
        filterNode = getFilterNodeSelected()
        fSelType = getFilterNodeType(filterNode)
        
        fNext = getNextFilterNode(filterNode, fSelType)
        fNextType = getFilterNodeType(fNext)
        nextSocket = None
        
        if fNextType != None:
            nextSocket = fNext.inputs[fNextType[2]]    
        else:
            nextSocket = layerNode.node_tree.nodes["PL_filtersColorOutput"].inputs[0]
            
        
        fPrev = getPrevFilterNode(filterNode, fSelType)
        fPrevType = getFilterNodeType(fPrev)
        
        if fPrevType != None:
            prevSocket = fPrev.outputs[fPrevType[3]]
        else:
            prevSocket = layerNode.node_tree.nodes["PL_filtersColorInput"].outputs[0]
        
        
        layerNode.node_tree.links.new(prevSocket,nextSocket)
        
            
    def execute(self, context):
        
        bpy.ops.ed.undo_push()
        self.bridgeFilterNodes()
        self.deleteFilterNode()
        self.deleteFilterFromTree()
        
        return {'FINISHED'}
        
class VTOOLS_OP_AddLayerFilter(bpy.types.Operator):
    bl_idname = "vtoolpt.addlayerfilter"
    bl_label = "Add Layer Filter"
    bl_description = "Add a new Filter to the selected layer"
    bl_options = {'REGISTER', 'UNDO'}
    
    filterType = bpy.props.StringProperty()
    inputSocket = bpy.props.StringProperty()
    outputSocket = bpy.props.StringProperty()
    
    
    def bridgeFilterNodes(self, pNewFilter):
        
        layerNode = paintingLayers.getLayerNodeSelected()
        filterNode = getFilterNodeSelected()
        fSelType = getFilterNodeType(filterNode)
        
        fNext = getNextFilterNode(filterNode, fSelType)
        fNextType = getFilterNodeType(fNext)
        nextSocket = None
        
        if fNextType != None:
            nextSocket = fNext.inputs[fNextType[2]]    
        else:
            nextSocket = layerNode.node_tree.nodes["PL_filtersColorOutput"].inputs[0]
            
        
        fNewType = getFilterNodeType(pNewFilter)
        
        layerNode.node_tree.links.new(filterNode.outputs[fSelType[3]],pNewFilter.inputs[fNewType[2]])
        layerNode.node_tree.links.new(pNewFilter.outputs[fNewType[3]],nextSocket)
        
    def addFilterNode(self):
        
        layerNode = paintingLayers.getLayerNodeSelected()
        filterFrame = layerNode.node_tree.nodes["PL_FrameClippingMaskFilters"]
        
        filterNode = layerNode.node_tree.nodes.new(type=self.filterType)
        filterNode.parent = filterFrame
        filterNode.location = (100, 500)
        filterNode.label = filterNode.name
        filterNode.name = "MLPFilterNode" + filterNode.name
        
        colorTextureNode = layerNode.node_tree.nodes["Color"]
        filterInputNode = layerNode.node_tree.nodes["PL_filtersColorInput"]
        filterOutputNode = layerNode.node_tree.nodes["PL_filtersColorOutput"]
        
        if len(bpy.context.scene.mlpFilterLayerCollection) == 0:
            layerNode.node_tree.links.new(filterInputNode.outputs[0], filterNode.inputs[self.inputSocket])
            layerNode.node_tree.links.new(filterNode.outputs[self.outputSocket], filterOutputNode.inputs[0])
        else:
            self.bridgeFilterNodes(filterNode)
            
        return filterNode
    
        
    def execute(self, context):
        #bpy.ops.vtoolpt.filtersmenu()
        bpy.ops.ed.undo_push()
        filterNode = self.addFilterNode()
        addFilterToTree(filterNode)
        
        return {'FINISHED'}

class VTOOLS_MT_FiltersMenu(bpy.types.Menu):
    bl_idname = "vtoolpt.filtersmenu"
    bl_label = ""
    bl_description = "Add a filter to selected layer"
    

    #["",""],
    
        
    def draw(self,context):
        layout = self.layout
        #layout.operator_context = 'INVOKE_DEFAULT'
        for type in filterTypes:
            op = layout.operator(VTOOLS_OP_AddLayerFilter.bl_idname, text=type[0])
            op.filterType = type[1]
            op.inputSocket = type[2]
            op.outputSocket = type[3]



def register():
    bpy.utils.register_class(VTOOLS_OP_AddLayerFilter)
    bpy.utils.register_class(VTOOLS_OP_DeleteLayerFilter)
    bpy.utils.register_class(VTOOLS_OP_CollectLayerFilter)
    bpy.utils.register_class(VTOOLS_MT_FiltersMenu)
    bpy.utils.register_class(VTOOLS_OP_MoveLayerFilter)
    return {'FINISHED'}
    

def unregister():
   bpy.utils.unregister_class(VTOOLS_OP_AddLayerFilter)
   bpy.utils.unregister_class(VTOOLS_OP_DeleteLayerFilter)
   bpy.utils.unregister_class(VTOOLS_OP_CollectLayerFilter)
   bpy.utils.unregister_class(VTOOLS_MT_FiltersMenu)
   bpy.utils.unregister_class(VTOOLS_OP_MoveLayerFilter)
   return {'FINISHED'}
    
