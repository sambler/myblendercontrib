import bpy
from vtools_multiLayerPainting import paintingLayers


def getMainOutputNode():
    
    outputNode = None
    
    mainTree = bpy.context.object.active_material.node_tree
    for n in mainTree.nodes:
        n.select = False
        if hasattr(n, "is_active_output"):
            if n.is_active_output == True:
                outputNode = n
    
    return outputNode
            
def setActiveOutput(pNewOutputNode):
    
    oldOutputNode = None
    mainTree = bpy.context.object.active_material.node_tree
    
    for n in mainTree.nodes:
        n.select = False
        if hasattr(n, "is_active_output"):
            if n.is_active_output == True:
                oldOutputNode = n
                n.is_active_output = False
            
    mainTree.nodes.active = None    
    
    pNewOutputNode.select = True
    mainTree.nodes.active = pNewOutputNode
    pNewOutputNode.is_active_output = True
    
    mainTree.nodes.active = pNewOutputNode
    
    return oldOutputNode


def bakeLayers(pLayerSet, pImageToBake):
    
    mainTree = bpy.context.object.active_material.node_tree
    
    #---CREATE BAKE NODES
    bakeOutput = mainTree.nodes.new("ShaderNodeOutputMaterial")
    bakeShader = mainTree.nodes.new("ShaderNodeBsdfDiffuse")
    bakeTexture = mainTree.nodes.new("ShaderNodeTexImage")
    

    #-- CONFIGURE    
    bakeShader.location[0] = 200
    bakeOutput.location[0] = 400
    
    bakeOutput.name = "MTBakeOutput"
    bakeShader.name = "MTBakeShader"
    bakeTexture.name = "MTBakeTexture"
    
    #--- BAKE IMAGE ---
    #bakeImage = bpy.data.images.new('MTBakeImageTarget',1024,1024)
    bakeTexture.image = pImageToBake
    
    #-------LINKS---------
    mainTree.links.new(pLayerSet.outputs["Bake"], bakeOutput.inputs["Surface"])
    #mainTree.links.new(mainTree.nodes["bowTexture"].outputs[0], bakeShader.inputs["Color"])
    
    #---SET OUTPUTS
    mainOutputNode = setActiveOutput(bakeOutput)
    bakeTexture.select = True
    mainTree.nodes.active = bakeTexture
    
    
    #-- BAKE
    runBaking()
    
    #--COME BACK
    setActiveOutput(mainOutputNode)
    
    mainTree.nodes.remove(node=bakeOutput)
    mainTree.nodes.remove(node=bakeShader)
    mainTree.nodes.remove(node=bakeTexture)
    
    return {'FINISHED'}

def configDiffuseRender():
    
    cs = bpy.context.scene
    
    cs.cycles.bake_type = "DIFFUSE"
    cs.render.bake.use_pass_direct = False
    cs.render.bake.use_pass_indirect = False    
    cs.render.bake.use_pass_color = True

def configEmitRender():
    
    cs = bpy.context.scene
    cs.cycles.bake_type = "EMIT"
    
        
def runBaking():
    
    co = bpy.context.object
    
    am = co.active_material # co.data.materials[co.active_material_index]
    am.use_nodes = True
    
    #create a new layer and set as active
    #node_tree.nodes.active = node
    
    cs = bpy.context.scene
    
    oldEngine = cs.render.engine 
    
    cs.render.engine = "CYCLES"
    #configDiffuseRender()
    configEmitRender()
    
    
    cs.render.bake.use_selected_to_active = False
    cs.render.use_bake_multires = False
    
    cs.cycles.samples = 1
    cs.cycles.use_square_sampes = False
    cs.cycles.diffuse_bounces = 1
    cs.cycles.glossy_bounces = 1
    cs.cycles.transparent_max_bounces = 1
    cs.cycles.transmission_bounces = 1
    cs.cycles.volume_bounces = 0
    
    #bpy.ops.object.bake(type='DIFFUSE')
    bpy.ops.object.bake(type='EMIT')
    
    cs.render.engine = oldEngine

def setupLayersForBake(pNumLayers):
    
    tmpBakeNodes = []
    als = paintingLayers.getActiveLayerSet(False)
    firstLayerId = bpy.context.scene.mlpLayerTreeCollection_ID
    slId = firstLayerId
    
    firstLayer = paintingLayers.getLayerNodeById(firstLayerId)
    
    for i in range(pNumLayers):
        
        lId = firstLayerId - i
        tmp_n = paintingLayers.getLayerNodeById(lId)
        
        if tmp_n != None:
            tmp_bake = als.node_tree.nodes.new(type="ShaderNodeGroup")
            tmp_bake.node_tree = tmp_n.node_tree
            tmp_bake.inputs["Opacity"].default_value = tmp_n.inputs["Opacity"].default_value
            tmp_bake.inputs["Global Filter"].default_value = tmp_n.inputs["Global Filter"].default_value
            
            tmpBakeNodes.append(tmp_bake)
            tmp_bake.location = (200*i*-1, 400)
        else:
            break
    
    numBakingNodes = len(tmpBakeNodes)
    bakeNodes = tmpBakeNodes[::-1]
    print("BAKE NODES ", tmpBakeNodes, " -- ", bakeNodes)
    
    for i in range(numBakingNodes):
        n1 = bakeNodes[i]
        
        if i+1 < numBakingNodes:
            n2 = bakeNodes[i+1]
        else:
            break
        
        paintingLayers.connectLayerNodes(n1,n2)
        
        
    return bakeNodes    

def deleteBakeLayerNodes(pLayerSet,pLayerList):
    
    for l in pLayerList:
        pLayerSet.node_tree.nodes.remove(l)
        
    return {'FINISHED'}

def deleteBakedLayers(pLayerSet, pNumLayers):
    
    currentSelectedId = bpy.context.scene.mlpLayerTreeCollection_ID
    
    for i in range(pNumLayers):
        bpy.context.scene.mlpLayerTreeCollection_ID = bpy.context.scene.mlpLayerTreeCollection_ID - 1
        bpy.ops.vtoolpt.deletepaintinglayer()
        
    #bpy.context.scene.mlpLayerTreeCollection_ID = currentSelectedId - pNumLayers
    
#--- CLASSES -----------

class VTOOLS_OP_mergeLayers(bpy.types.Operator):
    bl_idname = "vtoolpt.mergelayers"
    bl_label = "Merge Layers"
    bl_description = "1 - Create a new layer, 2 - Create an image within for baking, 3 - Push Merge Layers button, it will merge all layers below the one just created"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        bpy.ops.ed.undo_push()
        bakeLayerNodes = setupLayersForBake(bpy.context.scene.mlpNumLayersToBake)
        imageToBake = paintingLayers.connectLayerToBake(bakeLayerNodes[len(bakeLayerNodes)-1])
        
        layerSet = paintingLayers.getActiveLayerSet(False)
        
        if imageToBake != None:
            bakedImage = bakeLayers(layerSet, imageToBake)
        
        deleteBakeLayerNodes(layerSet,bakeLayerNodes)
        
        '''
        if bpy.context.scene.mlpDeleteBakedLayers == True:
            deleteBakedLayers(layerSet, len(bakeLayerNodes)-1)
        '''
        
        return {'FINISHED'}
    

#--------- REGISTER --------------
    
def register():
    
    bpy.utils.register_class(VTOOLS_OP_mergeLayers)
    
    bpy.types.Scene.mlpNumLayersToBake = bpy.props.IntProperty(default=2, min = 2)
    bpy.types.Scene.mlpDeleteBakedLayers = bpy.props.BoolProperty(default=False)
    
    return {'FINISHED'}
    
    
def unregister():
    bpy.utils.unregister_class(VTOOLS_OP_mergeLayers)
    
    del bpy.types.Scene.mlpNumLayersToBake
    del bpy.types.Scene.mlpDeleteBakedLayers   
    
    return {'FINISHED'}