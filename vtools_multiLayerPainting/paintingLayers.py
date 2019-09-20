import bpy
from vtools_multiLayerPainting import createNodes

# ---------- GLOBAL DEFS -------

def getActiveLayerSet(pGetNodeTree):
    
    setNode = None
    
    obj = bpy.context.object
    
    if obj != None:
        if obj.active_material != None:
            mainTree = bpy.context.object.active_material.node_tree
            setName = ""
            
            if bpy.context.scene.mlpLayerSetsCollection_ID != -1:
                setName = bpy.context.scene.mlpLayerSetsCollection[bpy.context.scene.mlpLayerSetsCollection_ID].layerSetName
            
            setNodeId = mainTree.nodes.find(setName)
            if setNodeId != -1:
                setNode = mainTree.nodes[setNodeId]
            else:
                setNode = bpy.context.object.active_material
            
            if pGetNodeTree == True:
                setNode = setNode.node_tree

    return setNode

def getActiveLayerSetByName(pSetName):
    
    setNode = None
    mainTree = bpy.context.object.active_material.node_tree
    
    if bpy.context.scene.mlpLayerSetsCollection_ID != -1:

        setNodeId = mainTree.nodes.find(pSetName)
        if setNodeId != -1:
            setNode = mainTree.nodes[setNodeId]
 
    return setNode
    
def getLayerNodeSelected():
    
    layerNode = None
    alId = bpy.context.scene.mlpLayerTreeCollection_ID
    
    if alId != -1 and len(bpy.context.scene.mlpLayerTreeCollection) > 0:
        layerNodeName = bpy.context.scene.mlpLayerTreeCollection[alId].layerName
        mainTree = getActiveLayerSet(True)
        layerId = mainTree.nodes.find(layerNodeName)
        if layerId != -1:
            layerNode = mainTree.nodes[layerId]
    
    return layerNode

def getLayerNodeById(pId):
    
    layerNode = None
    lastLayerId =  len(bpy.context.scene.mlpLayerTreeCollection) - 1
    
    if pId > -1 and pId <= lastLayerId:
        layerNodeName = bpy.context.scene.mlpLayerTreeCollection[pId].layerName
        mainTree = getActiveLayerSet(True) 
        layerId = mainTree.nodes.find(layerNodeName)
        if layerId != -1:
            layerNode = mainTree.nodes[layerId]
    
    return layerNode

def getLayerNodeByName(pName):
    
    layerNode = None
    
    mainTree = getActiveLayerSet(True)
    layerId = mainTree.nodes.find(pName)
    if layerId != -1:
        layerNode = mainTree.nodes[layerId]
            
    return layerNode
    
     
def getLayerFromSelected(pDistance):
    layerNode = None
    alId = bpy.context.scene.mlpLayerTreeCollection_ID
    lastLayerId =  len(bpy.context.scene.mlpLayerTreeCollection) - 1
    targetLayer = bpy.context.scene.mlpLayerTreeCollection_ID + pDistance
    
    if targetLayer >= 0 and targetLayer <= lastLayerId:
        layerNodeName = bpy.context.scene.mlpLayerTreeCollection[targetLayer].layerName
        mainTree = getActiveLayerSet(True)
        layerId = mainTree.nodes.find(layerNodeName)
        if layerId != -1:
            layerNode = mainTree.nodes[layerId]
    
    return layerNode
    
def getLayerOverSelected():
    
    layerNode = None
    alId = bpy.context.scene.mlpLayerTreeCollection_ID
    lastLayerId =  len(bpy.context.scene.mlpLayerTreeCollection) - 1
    
    if alId != -1 and alId < lastLayerId:
        layerNodeName = bpy.context.scene.mlpLayerTreeCollection[alId + 1].layerName
        mainTree = getActiveLayerSet(True)
        layerId = mainTree.nodes.find(layerNodeName)
        if layerId != -1:
            layerNode = mainTree.nodes[layerId]
    
    return layerNode

def getLayerDownSelected():
    
    layerNode = None
    alId = bpy.context.scene.mlpLayerTreeCollection_ID
    
    if alId > 0:
        layerNodeName = bpy.context.scene.mlpLayerTreeCollection[alId - 1].layerName
        mainTree = getActiveLayerSet(True)
        layerId = mainTree.nodes.find(layerNodeName)
        if layerId != -1:
            layerNode = mainTree.nodes[layerId]
    
    return layerNode

def getLayerDownByNode(pNode):
    
    nodeDn = None
    
    if pNode != None:
        links = pNode.inputs["colorBelow"].links 

    if  len(links) > 0: 
        nodeDn = links[0].from_node 

        if isMLPLayerNode(nodeDn) == False:
            nodeDn = None
            
    return nodeDn

def getLayerColorSpace():
    
    res = "color"
    lc = bpy.context.scene.mlpLayerTreeCollection
    alId = bpy.context.scene.mlpLayerTreeCollection_ID
    
    if alId != -1 and len(lc) > 0:
        res = lc[alId].colorSpace

    return res

def setLayerColorSpace(pColorSpace):
    lc = bpy.context.scene.mlpLayerTreeCollection
    alId = bpy.context.scene.mlpLayerTreeCollection_ID
    
    if alId != -1 and len(lc) > 0:
        lc[alId].colorSpace = pColorSpace
    
def getLayerSelectedFromTree():
    res = None
    lc = bpy.context.scene.mlpLayerTreeCollection
    alId = bpy.context.scene.mlpLayerTreeCollection_ID
    
    if alId != -1:
        res = lc[alId]

    return res
    
       
def removeNodeLinks(pContextTree, pNode, pOutput):
    
    if pNode != None:
        while len(pNode.outputs[pOutput].links) > 0:
            pContextTree.links.remove(pNode.outputs[pOutput].links[0])
    
def connectLayerNodes(pLayerDn, pLayerUp):
                
    mainTree = getActiveLayerSet(True)
    done = False
    
    if pLayerDn != None and  pLayerUp != None:
        removeNodeLinks(mainTree, pLayerDn, "Color")
        removeNodeLinks(mainTree, pLayerDn, "Alpha")
        
        mainTree.links.new(pLayerDn.outputs["Color"], pLayerUp.inputs["colorBelow"])
        mainTree.links.new(pLayerDn.outputs["Alpha"], pLayerUp.inputs["alphaBelow"])
        done = True 
        
    return done

def isFirstLayer(pLayerNode):
    
    isFirst = False
    if pLayerNode.name.find("paintLayer") != -1:
        bl = pLayerNode.inputs["colorBelow"].links
        if len(bl) > 0:
            if isMLPLayerNode(bl[0].from_node) == False:
                isFirst = True
        else:
            isFirst = True
    
    return isFirst


def addLayerTree(pNewLayer):
        targetLayerItemId = bpy.context.scene.mlpLayerTreeCollection_ID + 1
        uiLayer = bpy.context.scene.mlpLayerTreeCollection.add()
        uiLayer.layerName = pNewLayer.name
        uiLayer.name = pNewLayer.label
          
        #MOVE layer tree
        newLayerItemId = len(bpy.context.scene.mlpLayerTreeCollection) -1
        bpy.context.scene.mlpLayerTreeCollection.move(newLayerItemId,targetLayerItemId)
        bpy.context.scene.mlpLayerTreeCollection_ID = targetLayerItemId
        
def isMLPLayerNode(pNode):
    
    res = False
    if pNode.type == "GROUP":
        if pNode.node_tree.name.find(bpy.context.scene.vt_paintLayerNodeType) != -1:
            res = True
    
    return res


    
def getFirstLayer():
    als = getActiveLayerSet(False)
    mainTree = als.node_tree
    firstLayer = None
    
    #fId = mainTree.nodes.find("MLP_FirstLayer")
    #if fId != -1:
    #parentFrame = mainTree.nodes[fId]
    
    for n in mainTree.nodes:
        if isFirstLayer(n) == True:
            firstLayer = n
    
    return firstLayer
        
def getNextNodeLayer(pCurrentNode):
    
    #pCurrentNode.outputs["colorOutput"].links[i].to_node
    
    nextNode = None
    links = pCurrentNode.outputs["Color"].links
    for l in links:
        tmpNext = l.to_node
        if tmpNext != None:
            if isMLPLayerNode(tmpNext):
                nextNode = tmpNext
    
    return nextNode
        

def configureLastLayer():
    
    mainTree = getActiveLayerSet(True)
    
    if mainTree != None:
        outputNodeId = mainTree.nodes.find("PL_LayerSetOutput")
        shaderNodeId = mainTree.nodes.find("MTBakeShader")
        
        if outputNodeId != -1 and shaderNodeId != -1:
            outputNode = mainTree.nodes[outputNodeId]
            shaderNode = mainTree.nodes[shaderNodeId]
            
            lId = len(bpy.context.scene.mlpLayerTreeCollection) - 1
            lastLayer = getLayerNodeById(lId)
            
            if lastLayer != None:
                removeNodeLinks(mainTree,lastLayer, "Color")
                removeNodeLinks(mainTree,lastLayer, "Alpha")
                
                mainTree.links.new(lastLayer.outputs["Color"], outputNode.inputs["Color"])
                #mainTree.links.new(lastLayer.outputs["Color"], shaderNode.inputs["Color"])
                mainTree.links.new(lastLayer.outputs["Alpha"], outputNode.inputs["Alpha"])


def configureFirstLayer():
    
    mainTree = getActiveLayerSet(True)
    
    if mainTree != None:
        inputNodeId = mainTree.nodes.find("PL_PaintingSetInput")
        
        if inputNodeId != -1:
            inputNode = mainTree.nodes[inputNodeId]
            firstLayer = getLayerNodeById(0)
            
            if firstLayer != None and inputNode != None:
                removeNodeLinks(mainTree,inputNode, "Color")
                removeNodeLinks(mainTree,inputNode, "Alpha")
                
                mainTree.links.new(inputNode.outputs["Color"], firstLayer.inputs["colorBelow"])
                mainTree.links.new(inputNode.outputs["Alpha"], firstLayer.inputs["alphaBelow"])
                        

def  orderLayerNodes():
    
    numLayers = len(bpy.context.scene.mlpLayerTreeCollection)
    for i in range(0,numLayers):
        tmpLayer = getLayerNodeById(i)
        tmpLayer.location = (300*i,-300)

def updateLayersID():
    
    cont = 0
    for l in bpy.context.scene.mlpLayerTreeCollection:
        l.layerID = cont
        cont += 1
    
    
def updateLayerNodes():
    
    configureLastLayer()
    configureFirstLayer()
    orderLayerNodes()
    
    bpy.ops.vtoolpt.collectlayerfilter()
    
    updateLayersID()
    
    return {'FINISHED'}

def setAllLayersVisibility():
    
    cont = 0
    for l in bpy.context.scene.mlpLayerTreeCollection:
        lNode = getLayerNodeById(l.layerID)
        if lNode.node_tree.nodes["PL_OpacityOffset"].inputs[0].default_value == 0:
            l.visible = False
        else:
            l.visible = True

def copyLayerVisibility(pOrigId, pDestId):
    
    lc = bpy.context.scene.mlpLayerTreeCollection
    numLayers = len(lc)
    
    if pOrigId > -1 and pOrigId < numLayers and pDestId > -1 and pDestId < numLayers:
        lOrig = lc[pOrigId]
        lDest = lc[pDestId]
        
        lDest.visible = lOrig.visible
        
def connectLayerToBake(pNode):
    
    mainTree = getActiveLayerSet(True)
    shaderNode = mainTree.nodes["MTBakeShader"]
    imageToBake = None
    
    al = pNode #getLayerNodeSelected()
    #alDown = getLayerDownByNode(al)
    
    if al != None:
        imageToBake = al.node_tree.nodes["Color"].image
        mainTree.links.new(al.outputs["Color"], shaderNode.inputs["Color"])
    
    return imageToBake
        
            
# ---------- OPERATORS -------

    
class VTOOLS_OP_CollectLayersFromSet(bpy.types.Operator):
    bl_idname = "vtoolpt.collectsetlayers"
    bl_label = "Collect Set Layers"
    bl_description = "Collect and Configure Set Layers"
    bl_options = {'REGISTER', 'UNDO'}
    
        
    def execute(self, context):
        
        bpy.ops.ed.undo_push()
        firstLayer = getFirstLayer()
        if firstLayer != None:
            addLayerTree(firstLayer)
            nextLayer = getNextNodeLayer(firstLayer)
            while nextLayer != None:
                addLayerTree(nextLayer)
                nextLayer = getNextNodeLayer(nextLayer)
            
        updateLayerNodes()
        setAllLayersVisibility()
        
        return {'FINISHED'}
        
class VTOOLS_OP_DeletePaintingLayer(bpy.types.Operator):
    bl_idname = "vtoolpt.deletepaintinglayer"
    bl_label = "Delete Layer"
    bl_description = "Delete selected painting layer"
    bl_options = {'REGISTER', 'UNDO'}
        
    def deleteLayerImages(self,pActiveLayer):
        
        colorImage = pActiveLayer.node_tree.nodes["Color"].image
        maskImage = pActiveLayer.node_tree.nodes["Mask"].image
        
        if colorImage != None:
            if colorImage.users == 1:  
                bpy.data.images.remove(colorImage)
        
        if maskImage != None:
            if maskImage.users == 1:  
                bpy.data.images.remove(maskImage)
            
        return {'FINISHED'}
        
    def deleteLayerNode(self,pActiveLayer):
        
        mainTree = getActiveLayerSet(True)    
        bpy.data.node_groups.remove(pActiveLayer.node_tree)
        mainTree.nodes.remove(pActiveLayer) 
         
        return {'FINISHED'}
    
    def deleteLayerFromTree(self):
        
        currentSelected = bpy.context.scene.mlpLayerTreeCollection_ID
        
        if currentSelected != -1:
            bpy.context.scene.mlpLayerTreeCollection.remove(bpy.context.scene.mlpLayerTreeCollection_ID)
            bpy.context.scene.mlpLayerTreeCollection_ID = currentSelected - 1
            
            #select layer
            if len(bpy.context.scene.mlpLayerTreeCollection) > 0 and bpy.context.scene.mlpLayerTreeCollection_ID  == -1:
                bpy.context.scene.mlpLayerTreeCollection_ID = 0
                
        return {'FINISHED'}
    
    def bridgeLayers(self,pActiveLayer, pDownActiveLayer, pOverActiveLayer):
        
        if pDownActiveLayer != None and pOverActiveLayer != None:
            connectLayerNodes(pDownActiveLayer, pOverActiveLayer)
            
        return {'FINISHED'}
    
    def execute(self, context):
        
        bpy.ops.ed.undo_push()
        al = getLayerNodeSelected()
        
        if al != None:
            
            alOver = getLayerOverSelected()
            alDown = getLayerDownSelected()  
        
            self.deleteLayerImages(al)
            self.deleteLayerNode(al) 
            self.bridgeLayers(al, alDown, alOver)
        
        self.deleteLayerFromTree()
        updateLayerNodes()  
        
        return {'FINISHED'}


            
class VTOOLS_OP_AddPaintingLayer(bpy.types.Operator):
    bl_idname = "vtoolpt.addpaintinglayer"
    bl_label = "Add Layer"
    bl_description = "Add a new painting layer"
    bl_options = {'REGISTER', 'UNDO'}
    
    def addLayer(self,pNodeType):
        newLayer = None
        als = getActiveLayerSet(False)
        
        if bpy.data.node_groups.find(pNodeType) == -1:
            createNodes.setupPaintLayerNode()
          
        mainTree = als.node_tree
        newLayer = mainTree.nodes.new(type="ShaderNodeGroup")
        newLayer.node_tree = bpy.data.node_groups[pNodeType].copy()   
        newLayer.name = als.name+".paintLayer"
        newLayer.label = "paintLayer"
        
        newLayer.location.x = bpy.context.scene.mlpLayerTreeCollection_ID*200
    
        return newLayer
    
    def bridgeLayers(self, pActiveLayer, pLayerOverActive, pNewLayer):
        
        if pActiveLayer != None:
            connectLayerNodes(pActiveLayer, pNewLayer)
            
        if pLayerOverActive != None:
            connectLayerNodes(pNewLayer, pLayerOverActive)
            
        return {'FINISHED'}
            
    def execute(self, context):
        
        al = getLayerNodeSelected()
        alOver = getLayerOverSelected() 
        newLayer = self.addLayer(bpy.context.scene.vt_paintLayerNodeType)
        addLayerTree(newLayer)
        self.bridgeLayers(al, alOver, newLayer)
        
        bpy.ops.ed.undo_push()
        updateLayerNodes()  
        
        return {'FINISHED'}
        

class VTOOLS_OP_MovePaintingLayerUp(bpy.types.Operator):
    bl_idname = "vtoolpt.movepaintinglayerup"
    bl_label = "Move Layer Up"
    bl_description = "Move the selected layer Up"
    bl_options = {'REGISTER', 'UNDO'}
    
    def moveLayerUp(self, pActiveLayer, pLayerOver):
        
        if pLayerOver != None:
            alId = bpy.context.scene.mlpLayerTreeCollection_ID
            bpy.context.scene.mlpLayerTreeCollection.move(alId,alId+1)
            bpy.context.scene.mlpLayerTreeCollection_ID += 1
            
    
    def bridgeLayers(self, pActiveLayer, pLayerDownActive, pLayerOverActive):
            
        if pLayerOverActive != None:
            connectLayerNodes(pLayerOverActive, pActiveLayer)
            
            if pLayerDownActive != None:
                connectLayerNodes(pLayerDownActive, pLayerOverActive)
        
            upperLayer = getLayerFromSelected(+2)
        
            if upperLayer != None:
                connectLayerNodes(pActiveLayer, upperLayer)
        
    def execute(self, context):
        
        bpy.ops.ed.undo_push()
        al = getLayerNodeSelected()
        
        if al != None:            
            alOver = getLayerOverSelected()
            alDown = getLayerDownSelected()  
            self.bridgeLayers(al, alDown, alOver)
            self.moveLayerUp(al, alOver)
            
            updateLayerNodes()  
        
        return {'FINISHED'}
    
class VTOOLS_OP_MovePaintingLayerDown(bpy.types.Operator):
    bl_idname = "vtoolpt.movepaintinglayerdown"
    bl_label = "Move Layer Down"
    bl_description = "Move the selected layer Down"
    bl_options = {'REGISTER', 'UNDO'}
    
    def moveLayerDown(self, pActiveLayer, pLayerOver):
        
        if pLayerOver != None:
            alId = bpy.context.scene.mlpLayerTreeCollection_ID
            bpy.context.scene.mlpLayerTreeCollection.move(alId,alId-1)
            bpy.context.scene.mlpLayerTreeCollection_ID -= 1
            
    
    def bridgeLayers(self, pActiveLayer, pLayerDownActive, pLayerOverActive):
            
        if pLayerDownActive != None:
            connectLayerNodes(pActiveLayer, pLayerDownActive)
            
            if pLayerOverActive != None:
                connectLayerNodes(pLayerDownActive, pLayerOverActive)
        
            downerLayer = getLayerFromSelected(-2)
        
            if downerLayer != None:
                connectLayerNodes(downerLayer, pActiveLayer)
        
    def execute(self, context):
        
        bpy.ops.ed.undo_push()
        al = getLayerNodeSelected()
        
        if al != None:            
            alOver = getLayerOverSelected()
            alDown = getLayerDownSelected()  
            self.bridgeLayers(al, alDown, alOver)
            self.moveLayerDown(al, alDown)
            
            updateLayerNodes()
        
        return {'FINISHED'}
    
    
class VTOOLS_OP_DuplicatePaintingLayer(bpy.types.Operator):
    bl_idname = "vtoolpt.duplicatepaintinglayer"
    bl_label = "Duplicate Layer"
    bl_description = "Duplciate the selected layer"
    bl_options = {'REGISTER', 'UNDO'}
 
    def execute(self, context):
        
        bpy.ops.ed.undo_push()
        al = getLayerNodeSelected()
        
        if al != None:
            
            alId = bpy.context.scene.mlpLayerTreeCollection_ID
            
            bpy.ops.vtoolpt.addpaintinglayer()            
            newLayer = getLayerNodeSelected()
            
            if newLayer != None:
                newLayer.node_tree = bpy.data.node_groups[al.node_tree.name].copy()
                newLayer.inputs["Opacity"].default_value = al.inputs["Opacity"].default_value
                newLayer.inputs["Global Filter"].default_value = al.inputs["Global Filter"].default_value
                
                nlId = bpy.context.scene.mlpLayerTreeCollection_ID
                
                copyLayerVisibility(alId, nlId)
                
            updateLayerNodes()    
                    
        return {'FINISHED'}
    
class VTOOLS_OP_SelectLayerColorSpace(bpy.types.Operator):
    bl_idname = "vtoolpt.selectlayercolorspace"
    bl_label = "Select Layer Color Space"
    bl_description = "Select color texture or mask texture from layer"
    bl_options = {'REGISTER', 'UNDO'}
    
    color = bpy.props.StringProperty(default="color")
    layerID = bpy.props.IntProperty()
    
    def selectColor(self):
        
        return {'FINISHED'}
    
    def selectMask(self):
        
        return {'FINISHED'}
    
    def execute(self, context):
        
        bpy.ops.ed.undo_push()
        
        bpy.context.scene.mlpLayerTreeCollection_ID = self.layerID
        
        if self.color == "color":
            setLayerColorSpace("color")
        else:
            setLayerColorSpace("mask")
            
              
        return {'FINISHED'}
    
#--------- REGISTER --------------
    
def register():
    
    bpy.utils.register_class(VTOOLS_OP_AddPaintingLayer)
    bpy.utils.register_class(VTOOLS_OP_DeletePaintingLayer)
    bpy.utils.register_class(VTOOLS_OP_MovePaintingLayerUp)
    bpy.utils.register_class(VTOOLS_OP_MovePaintingLayerDown)
    bpy.utils.register_class(VTOOLS_OP_CollectLayersFromSet)
    bpy.utils.register_class(VTOOLS_OP_DuplicatePaintingLayer)
    bpy.utils.register_class(VTOOLS_OP_SelectLayerColorSpace)
    
    return {'FINISHED'}
    
    
def unregister():
    bpy.utils.unregister_class(VTOOLS_OP_AddPaintingLayer)
    bpy.utils.unregister_class(VTOOLS_OP_DeletePaintingLayer)
    bpy.utils.unregister_class(VTOOLS_OP_MovePaintingLayerUp)
    bpy.utils.unregister_class(VTOOLS_OP_MovePaintingLayerDown)
    bpy.utils.unregister_class(VTOOLS_OP_CollectLayersFromSet)
    bpy.utils.unregister_class(VTOOLS_OP_DuplicatePaintingLayer)
    bpy.utils.unregister_class(VTOOLS_OP_SelectLayerColorSpace)
    
    return {'FINISHED'}
    
   
classes = (VTOOLS_OP_AddPaintingLayer,VTOOLS_OP_DeletePaintingLayer,)
