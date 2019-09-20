import bpy


def create_layerSetType():
    
    # create a group
    mt_node = bpy.data.node_groups.new('MTLayerSet', 'ShaderNodeTree')
    
    '''
    #Frame Fiist Layer
    mt_initFrame = mt_node.nodes.new('NodeFrame')
    mt_initFrame.name = "MLP_FirstLayer"
    mt_initFrame.label = "First Layer"
    mt_initFrame.location[0] = -400
    '''
    
    #----- OUTPUT-----------------
    
    # create group input
    mt_paintSetInput = mt_node.nodes.new('NodeGroupInput')
    mt_paintSetInput.name = "PL_PaintingSetInput"
    mt_paintSetInput.label = 'Painting Set Inputs'
    
    #inputs below
    n_colorSetBelow = mt_node.inputs.new('NodeSocketColor','Color')
    n_alphaSetBelow = mt_node.inputs.new('NodeSocketColor','Alpha')
    
    mt_paintSetInput.location = (-500,0)

    n_colorSetBelow.default_value = [1,1,1,1]
    n_alphaSetBelow.default_value = [1,1,1,1]
    
    # create group output
    mt_colorOutput = mt_node.nodes.new('NodeGroupOutput')
    mt_colorOutput.name = "PL_LayerSetOutput"
    mt_colorOutput.label = 'Painting Set Outputs'
    
    mt_colorOutput.location = (500,0)
    
    #outputs
    n_colorOutput = mt_node.outputs.new('NodeSocketColor','Color')
    n_alphaOutput = mt_node.outputs.new('NodeSocketColor','Alpha')
    n_bakeOutput = mt_node.outputs.new('NodeSocketShader','Bake')
    
    n_colorOutput.default_value = [0,0,0,0]
    n_alphaOutput.default_value = [0,0,0,0]
    
    #bakeShader = mt_node.nodes.new("ShaderNodeBsdfDiffuse")
    bakeShader = mt_node.nodes.new("ShaderNodeEmission")
    bakeShader.name = "MTBakeShader"
    bakeShader.location[1] = 200
    

    #-- LINKS
    #mt_node.links.new(bakeShader.outputs["BSDF"], mt_colorOutput.inputs["Bake"])
    mt_node.links.new(bakeShader.outputs["Emission"], mt_colorOutput.inputs["Bake"])
    
    return mt_node.name

def create_paintLayerType():
    
    # create a group
    mt_node = bpy.data.node_groups.new('MTPaintLayer', 'ShaderNodeTree')
    
    #------- INPUTS --------------#
    
    #frame inputs
    
    mt_inputsFrame = mt_node.nodes.new('NodeFrame')
    mt_inputsFrame.label = "Inputs"
    mt_inputsFrame.name = "PL_FrameInputs"
    
    # create group inputs
    mt_colorInputs = mt_node.nodes.new('NodeGroupInput')
    
    mt_colorInputs.label = 'layer Inputs'
    mt_colorInputs.name = "PL_LayerInput"
    
    mt_colorInputs.parent = mt_inputsFrame
    
    #opacity
    n_layerOpacity = mt_node.inputs.new('NodeSocketFloat','Opacity')
    n_layerOpacity.min_value = 0
    n_layerOpacity.max_value = 1
    n_layerOpacity.default_value = 1
    
    #global filter
    n_layerGlobalOpacity = mt_node.inputs.new('NodeSocketFloat','Global Filter')
    n_layerGlobalOpacity.min_value = 0
    n_layerGlobalOpacity.max_value = 1
    n_layerGlobalOpacity.default_value = 0
    
    #inputs below
    n_colorBelow = mt_node.inputs.new('NodeSocketColor','colorBelow')
    n_alphaBelow = mt_node.inputs.new('NodeSocketColor','alphaBelow')

    n_colorBelow.default_value = [0,0,0,0]
    n_alphaBelow.default_value = [0,0,0,0]

    #node color and alpha
    #n_color = mt_node.inputs.new('NodeSocketColor','Color')
    #n_colorAlpha = mt_node.inputs.new('NodeSocketColor','ColorAlpha')

    #node mask

    #n_mask = mt_node.inputs.new('NodeSocketColor','Mask')
    #n_mask.default_value = [1,1,1,1]
    
    #---inputs values
    
    mt_inLayerOpacity = mt_node.nodes.new('ShaderNodeValue')
    mt_inLayerOpacity.name = "PL_globalFilterValue"
    mt_inLayerOpacity.label = "Global Filter"
    mt_inLayerOpacity.outputs[0].default_value = 0
    mt_inLayerOpacity.parent = mt_inputsFrame
    
    mt_inMaskOpacity = mt_node.nodes.new('ShaderNodeValue')
    mt_inMaskOpacity.name = "PL_InputMaskOpacity"
    mt_inMaskOpacity.label = "Mask Opacity"
    mt_inMaskOpacity.outputs[0].default_value = 0
    mt_inMaskOpacity.parent = mt_inputsFrame
    
    #locations
    mt_colorInputs.location = (0,0)
    mt_inLayerOpacity.location = (0,-160)
    mt_inMaskOpacity.location = (0,-260)
    
    
    #---------- FILTERS -------------------
    
    #frame
    mt_filterFrame = mt_node.nodes.new('NodeFrame')
    mt_filterFrame.name = "PL_FrameClippingMaskFilters"
    mt_filterFrame.label = "Clipping Mask Filters"
    
    #reroutes
    mt_filterRerouteIN = mt_node.nodes.new('NodeReroute')
    mt_filterRerouteIN.name = "PL_filtersColorInput"
    mt_filterRerouteIN.label = "Filters Input"
    mt_filterRerouteIN.parent = mt_filterFrame
    
    mt_filterRerouteOUT = mt_node.nodes.new('NodeReroute')
    mt_filterRerouteOUT.name = "PL_filtersColorOutput"
    mt_filterRerouteOUT.label = "Filters Output"
    mt_filterRerouteOUT.parent = mt_filterFrame

    
    #global filter layer
    
    mt_globalFilter = mt_node.nodes.new('ShaderNodeMixRGB')
    mt_globalFilter.name = "PL_globalFilterSwitcher"
    mt_globalFilter.label = "Global Filter Switcher"
    mt_globalFilter.inputs["Fac"].default_value = 0
    mt_globalFilter.use_clamp = True
    
    mt_globalFilter.parent = mt_filterFrame
    
    #locations
    mt_filterRerouteIN.location = (200,0)
    mt_filterRerouteOUT.location = (400,0)
    mt_globalFilter.location = (-100, 0)
    mt_filterFrame.location = (300, 500)
    
    #---------- LAYER SYSTEM -------------------
    
    #frame
    mt_systemFrame = mt_node.nodes.new('NodeFrame')
    mt_systemFrame.name = "PL_FrameLayerSystem"
    mt_systemFrame.label = "Layer System"
    
    #opacity offset
    mt_opacityOffset = mt_node.nodes.new('ShaderNodeMath')
    mt_opacityOffset.name = "PL_OpacityOffset"
    mt_opacityOffset.label = "Opacity Offset"
    mt_opacityOffset.operation = "MULTIPLY"
    mt_opacityOffset.inputs[0].default_value = 1
    mt_opacityOffset.inputs[1].default_value = 1
    mt_opacityOffset.use_clamp = True
    mt_opacityOffset.parent = mt_systemFrame
    
    
    #layer opacity
    mt_layerOpacity = mt_node.nodes.new('ShaderNodeMixRGB')
    mt_layerOpacity.name = "PL_LayerOpacity"
    mt_layerOpacity.label = "Layer Opacity"
    mt_layerOpacity.blend_type = "MIX"
    mt_layerOpacity.use_clamp = True
    
    mt_layerOpacity.parent = mt_systemFrame
    
    #mask switcher
    mt_maskSwitcher = mt_node.nodes.new('ShaderNodeMixRGB')
    mt_maskSwitcher.name = "PL_LayerMask"
    mt_maskSwitcher.label = "Layer Max"
    mt_maskSwitcher.blend_type = "MULTIPLY"
    mt_maskSwitcher.inputs["Color1"].default_value = [0,0,0,1]
    mt_maskSwitcher.inputs["Color2"].default_value = [0,0,0,1]
    mt_maskSwitcher.use_clamp = True
    mt_maskSwitcher.parent = mt_systemFrame
    
    #invert mask texture
    mt_invertMaskTexture = mt_node.nodes.new("ShaderNodeInvert")
    mt_invertMaskTexture.label = "PL_invertMaskTexture"
    mt_invertMaskTexture.name = "Invert Mask Texture"
    mt_invertMaskTexture.parent = mt_systemFrame
    
    #Desaturate max
    mt_desatureMaskTexture = mt_node.nodes.new("ShaderNodeHueSaturation")
    mt_desatureMaskTexture.label = "PL_desatureMaskTexture"
    mt_desatureMaskTexture.name = "Desature Max Texture"
    mt_desatureMaskTexture.parent = mt_systemFrame
    mt_desatureMaskTexture.inputs["Saturation"].default_value = 0
    
    #masks adition
    mt_masksAdition = mt_node.nodes.new('ShaderNodeMixRGB')
    mt_masksAdition.name = "PL_MaskAddition"
    mt_masksAdition.label = "Masks Adition"
    mt_masksAdition.blend_type = "ADD"
    mt_masksAdition.use_clamp = True
    mt_masksAdition.inputs["Fac"].default_value = 1
    mt_masksAdition.parent = mt_systemFrame
    

    #Global Filter Switcher    
    mt_globalFilterColorAlpha = mt_node.nodes.new('ShaderNodeMixRGB')
    mt_globalFilterColorAlpha.name = "PL_GlobalFilterAlphaColor"
    mt_globalFilterColorAlpha.label = "Global Filter Color Alpha"
    mt_globalFilterColorAlpha.blend_type = "MIX"
    mt_globalFilterColorAlpha.use_clamp = True
    mt_globalFilterColorAlpha.inputs["Fac"].default_value = 0
    mt_globalFilterColorAlpha.inputs["Color1"].default_value = [1,1,1,1]
    mt_globalFilterColorAlpha.inputs["Color2"].default_value = [1,1,1,1]
    mt_globalFilterColorAlpha.parent = mt_systemFrame
    
    
    #Global Layer Opacity 
    mt_globalOpacity = mt_node.nodes.new('ShaderNodeMixRGB')
    mt_globalOpacity.name = "PL_GlobalLayerOpacity"
    mt_globalOpacity.label = "Global Layer Opacity"
    mt_globalOpacity.blend_type = "MULTIPLY"
    mt_globalOpacity.use_clamp = True
    mt_globalOpacity.inputs["Fac"].default_value = 1
    mt_globalOpacity.inputs["Color1"].default_value = [1,1,1,1]
    mt_globalOpacity.inputs["Color2"].default_value = [1,1,1,1]
    mt_globalOpacity.parent = mt_systemFrame
    
    
    
    #locations
    mt_systemFrame.location = (400,0)
    mt_opacityOffset.location = (0,0)
    mt_layerOpacity.location = (160,0)
    mt_maskSwitcher.location = (0,-200)
    mt_masksAdition.location = (180,-400)
    mt_invertMaskTexture.location = (0, -400)
    mt_desatureMaskTexture.location = (-180, -400)
    mt_globalFilterColorAlpha.location = (-180,-200)
    mt_globalOpacity.location = (180,-200)
    
    
    #---------- BLEND MODE -------------------
    
    #frame
    mt_blendModeFrame = mt_node.nodes.new('NodeFrame')
    mt_blendModeFrame.name = "PL_FrameBlendMode"
    mt_blendModeFrame.label = "Blend Mode"
    
    #blend mode node
    mt_blendMode = mt_node.nodes.new('ShaderNodeMixRGB')
    mt_blendMode.name = "PL_BlendMode"
    mt_blendMode.label = "Blend Mode"
    mt_blendMode.blend_type = "MIX"
    mt_blendMode.use_clamp = True
    mt_blendMode.parent = mt_blendModeFrame
    
    #Blend Mode Extra Opacity 
    mt_blendOpacity = mt_node.nodes.new('ShaderNodeMixRGB')
    mt_blendOpacity.name = "PL_BlendModeOpacity"
    mt_blendOpacity.label = "Blend Opacity"
    mt_blendOpacity.blend_type = "MIX"
    mt_blendOpacity.use_clamp = True
    mt_blendOpacity.inputs["Fac"].default_value = 1
    mt_blendOpacity.inputs["Color1"].default_value = [0,0,0,1]
    mt_blendOpacity.inputs["Color2"].default_value = [0,0,0,1]
    mt_blendOpacity.parent = mt_blendModeFrame
    
    #locations
    mt_blendModeFrame.location = (1000,0)
    mt_blendOpacity.location[0] = mt_blendMode.location[0] + 180
    
    #---------- ALPHA OUT ADD -------------------
    
    #frame
    mt_alphaOutAddFrame = mt_node.nodes.new('NodeFrame')
    mt_alphaOutAddFrame.name = "PL_FrameAlphaAdd"
    mt_alphaOutAddFrame.label = "Alpha  Add"
    
    #blend mode node
    mt_alphaOutAdd = mt_node.nodes.new('ShaderNodeMixRGB')
    mt_alphaOutAdd.name = "PL_alphaOutAdd"
    mt_alphaOutAdd.label = "Alpha Add"
    mt_alphaOutAdd.blend_type = "ADD"
    mt_alphaOutAdd.use_clamp = True
    mt_alphaOutAdd.inputs["Fac"].default_value = 1
    mt_alphaOutAdd.parent = mt_alphaOutAddFrame
    
    #locations
    mt_alphaOutAddFrame.location = (1000,-300)
    
    #----- OUTPUT-----------------
    
    # create group output
    mt_colorOutput = mt_node.nodes.new('NodeGroupOutput')
    mt_colorOutput.name = "PL_LayerOutput"
    mt_colorOutput.label = 'Layer Output'
    
    #outputs
    n_colorOutput = mt_node.outputs.new('NodeSocketColor','Color')
    n_alphaOutput = mt_node.outputs.new('NodeSocketColor','Alpha')
    
    n_colorOutput.default_value = [0,0,0,0]
    n_alphaOutput.default_value = [0,0,0,0]
    
    #location 
    mt_colorOutput.location = (1300,0)
    
    
    #---- IMAGE TEXTURES -----#
    
    #frame
    mt_texturesFrame = mt_node.nodes.new('NodeFrame')
    mt_texturesFrame.name = "PL_textures"
    mt_texturesFrame.label = "Textures"
    
    
    #colorImage = createNewTextureImage()
    #maskImage = createNewTextureImage()
    
    colorTexture = mt_node.nodes.new("ShaderNodeTexImage")
    #colorTexture.image = colorImage
    colorTexture.label = "COLOR"
    colorTexture.name = "Color"
    

    maskTexture = mt_node.nodes.new("ShaderNodeTexImage")
    #maskTexture.image = maskImage
    maskTexture.label = "MASK"
    maskTexture.name = "Mask"
    
    
    
    #uv nodes
    colorUVNode = mt_node.nodes.new("ShaderNodeUVMap")
    maskUVNode = mt_node.nodes.new("ShaderNodeUVMap")
    colorUVNode.name = "colorUVNode"
    maskUVNode.name = "maskUVNode"
    
    #mapping node
    colorMapNode = mt_node.nodes.new("ShaderNodeMapping")
    colorMapNode.name = "colorMapNode"
    
    maskMapNode = mt_node.nodes.new("ShaderNodeMapping")
    maskMapNode.name = "maskMapNode"
   
    
    #frame link
    colorTexture.parent = mt_texturesFrame
    maskTexture.parent = mt_texturesFrame
    colorUVNode.parent = mt_texturesFrame
    maskUVNode.parent = mt_texturesFrame
    colorMapNode.parent = mt_texturesFrame
    maskMapNode.parent = mt_texturesFrame
    
    #node locations
    maskTexture.location = (600,0)
    colorMapNode.location = (0,-230)
    colorUVNode.location = (0,-530)
    maskMapNode.location = (600,-230)
    maskUVNode.location = (600,-530)
    mt_texturesFrame.location = (-400,-750)
    
    
            
    #---- INTERNAL LINKS ------
    
    #uv nodes links
    
    mt_node.links.new(colorMapNode.outputs["Vector"], colorTexture.inputs["Vector"])
    mt_node.links.new(colorUVNode.outputs["UV"], colorMapNode.inputs["Vector"])
    
    mt_node.links.new(maskMapNode.outputs["Vector"], maskTexture.inputs["Vector"])
    mt_node.links.new(maskUVNode.outputs["UV"], maskMapNode.inputs["Vector"])
    
    
    #reroutes
    #mt_node.links.new(mt_colorInputs.outputs['Color'], mt_filterRerouteIN.inputs[0])
    mt_node.links.new(mt_filterRerouteIN.outputs[0], mt_filterRerouteOUT.inputs[0])
    mt_node.links.new(mt_globalFilter.outputs['Color'], mt_filterRerouteIN.inputs[0])
    
    mt_node.links.new(colorTexture.outputs['Color'], mt_globalFilter.inputs["Color1"])
    mt_node.links.new(mt_colorInputs.outputs['colorBelow'], mt_globalFilter.inputs["Color2"])
    
    
    #layer opacity
    mt_node.links.new(mt_colorInputs.outputs['colorBelow'], mt_layerOpacity.inputs["Color1"])
    mt_node.links.new(mt_filterRerouteOUT.outputs[0], mt_layerOpacity.inputs["Color2"])
    
    #golbal filter input
    
    mt_node.links.new(mt_colorInputs.outputs['Global Filter'], mt_globalFilter.inputs["Fac"])
    
    #layer opacity
    #mt_node.links.new(mt_inLayerOpacity.outputs[0], mt_opacityOffset.inputs[1])
    #mt_node.links.new(mt_inLayerOpacity.outputs[0], mt_layerOpacity.inputs["Fac"])
    
    #mt_node.links.new(mt_colorInputs.outputs['Opacity'], mt_layerOpacity.inputs["Fac"])
    
    mt_node.links.new(mt_colorInputs.outputs['Opacity'], mt_opacityOffset.inputs[1])
    mt_node.links.new(mt_opacityOffset.outputs["Value"], mt_layerOpacity.inputs["Fac"])
    
    
    
    #layer mask
    mt_node.links.new(mt_globalFilterColorAlpha.outputs['Color'], mt_maskSwitcher.inputs["Color1"])
    mt_node.links.new(mt_invertMaskTexture.outputs['Color'], mt_maskSwitcher.inputs["Fac"])
    mt_node.links.new(mt_desatureMaskTexture.outputs['Color'], mt_invertMaskTexture.inputs["Color"])
    mt_node.links.new(maskTexture.outputs["Color"], mt_desatureMaskTexture.inputs["Color"])
    mt_node.links.new(maskTexture.outputs["Alpha"], mt_invertMaskTexture.inputs["Fac"])
    
    
    #masks
    mt_node.links.new(colorTexture.outputs["Alpha"], mt_masksAdition.inputs["Color1"])
    mt_node.links.new(maskTexture.outputs["Color"], mt_masksAdition.inputs["Color2"])
    #mt_node.links.new(mt_colorInputs.outputs['ColorAlpha'], mt_masksAdition.inputs["Color2"])
    
    mt_node.links.new(colorTexture.outputs['Alpha'], mt_globalFilterColorAlpha.inputs["Color1"])
    mt_node.links.new(mt_colorInputs.outputs['Global Filter'], mt_globalFilterColorAlpha.inputs["Fac"])
    
    #blend mode
    mt_node.links.new(mt_globalOpacity.outputs["Color"], mt_blendMode.inputs["Fac"])
    mt_node.links.new(mt_colorInputs.outputs['colorBelow'], mt_blendMode.inputs["Color1"])
    mt_node.links.new(mt_layerOpacity.outputs[0], mt_blendMode.inputs["Color2"])
    mt_node.links.new(mt_globalOpacity.outputs["Color"], mt_blendMode.inputs["Fac"])
    
    #alpha out
    mt_node.links.new(mt_masksAdition.outputs["Color"], mt_alphaOutAdd.inputs["Color1"])
    mt_node.links.new(mt_colorInputs.outputs['alphaBelow'], mt_alphaOutAdd.inputs["Color2"])
    
    #Global Opacity
    #mt_node.links.new(mt_colorInputs.outputs['Opacity'], mt_globalOpacity.inputs["Color2"])
    mt_node.links.new(mt_opacityOffset.outputs["Value"], mt_globalOpacity.inputs["Fac"])
    mt_node.links.new(mt_maskSwitcher.outputs['Color'], mt_globalOpacity.inputs["Color1"])
    
    #output
    mt_node.links.new(mt_opacityOffset.outputs['Value'], mt_blendOpacity.inputs["Fac"])
    mt_node.links.new(mt_blendOpacity.outputs["Color"], mt_colorOutput.inputs["Color"])
    mt_node.links.new(mt_blendMode.outputs["Color"], mt_blendOpacity.inputs["Color2"])
    mt_node.links.new(mt_colorInputs.outputs['colorBelow'], mt_blendOpacity.inputs["Color1"])
    mt_node.links.new(mt_alphaOutAdd.outputs[0], mt_colorOutput.inputs["Alpha"])
    
    return mt_node.name



def newTextureImage(pName = "layerPaintImage", pWidth = 1024, pHeight = 1024, pColor = (0.0,0.0,0.0,0.0), pAlpha = True, pFloat=False):
    
  
    #unusedImageName = getFirstUnusedImageName(pName)
    #imageProperties = [unusedImageName , pWidth, pHeight, pColor, pAlpha, pDepth]
    img = bpy.ops.image.new(name = "layer")
    textureImage = bpy.data.images["layer"]
    textureImage.user_clear()     
    return textureImage

def createNewTextureImage():
    imageName = bpy.props.StringProperty(name="Name")
    imageWidth = bpy.props.IntProperty(name="Width", default=1024)
    imageHeight = bpy.props.IntProperty(name="Height", default=1024)
    imageColor = bpy.props.FloatVectorProperty(name="Image color", subtype='COLOR', size = 4, default=(0.0, 0.0, 0.0,0.0),min=0.0, max=1.0, description="color picker")
    imageDepth = bpy.props.BoolProperty(name="32 Bit Float Image", default = False) 
    isEmpty = bpy.props.BoolProperty(name="empty layer", default=False)
    connectToShaderNode = bpy.props.BoolProperty(name="Connected to Shader", default=False)
    shaderConnectionSlot = bpy.props.StringProperty(name = "Shader connection slot", default="Color")
    
    textureImage = newTextureImage(pName = imageName, pWidth = 1024, pHeight = 1024, pColor = (0.0, 0.0, 0.0,0.0), pAlpha = True, pFloat=32)
    
    return textureImage


def setupLayerSetNode():
    
    layerSetGroupId = bpy.data.node_groups.find('MTLayerSet')
    
    if layerSetGroupId < 0:
        layerSetNodeTypeName = create_layerSetType()
    else:
        bpy.data.node_groups[layerSetGroupId].name += "_OLD"
        layerSetNodeTypeName = create_layerSetType()
        layerSetNodeTypeName = bpy.data.node_groups[layerSetGroupId].name
        
    bpy.context.scene.vt_layerSetNodeType = layerSetNodeTypeName
    
def setupPaintLayerNode():
    
    paintLayerGroupId = bpy.data.node_groups.find('MTPaintLayer')
    
    if paintLayerGroupId < 0:
        layerNodeTypeName = create_paintLayerType()
    else:
        bpy.data.node_groups[paintLayerGroupId].name += "_OLD"
        layerNodeTypeName = create_paintLayerType()
        layerNodeTypeName = bpy.data.node_groups[paintLayerGroupId].name
        
    bpy.context.scene.vt_paintLayerNodeType = layerNodeTypeName

def setupPaintingSpace():
    
    return {'FINISHED'}
    
def init():    
    
    bpy.context.scene.mlpLayerTreeCollection.clear()
    bpy.context.scene.mlpLayerTreeCollection_ID = -1
    
    bpy.context.scene.mlpLayerSetsCollection.clear()
    bpy.context.scene.mlpLayerSetsCollection_ID = -1
    
    bpy.context.scene.mlpFilterLayerCollection.clear()
    bpy.context.scene.mlpFilterLayerCollection_ID = -1
    
    bpy.context.tool_settings.image_paint.mode = "IMAGE"
    bpy.context.scene.vt_layerSetNodeType = ""
    
    setupLayerSetNode()
    setupPaintLayerNode()
    setupPaintingSpace()
    
    return {'FINISHED'}
    
def register():
    
    bpy.types.Scene.vt_layerSetNodeType = bpy.props.StringProperty(default = "")
    bpy.types.Scene.vt_paintLayerNodeType = bpy.props.StringProperty(default = "")  
    bpy.types.Scene.vt_mpPaintActiveMaterial = bpy.props.StringProperty(default = "")  
        
    
    return {'FINISHED'}

def unregister():
    
    del bpy.types.Scene.vt_layerSetNodeType
    del bpy.types.Scene.vt_paintLayerNodeType
    del bpy.types.Scene.vt_mpPaintActiveMaterial
    
    
    return {'FINISHED'}
    
    
classes = ( )