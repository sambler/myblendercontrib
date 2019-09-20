import bpy
from vtools_multiLayerPainting import paintingLayers

#-- DEF CALLBACKS ---#


def cb_selectLayerSet(self, value):
    
    bpy.context.scene.mlpLayerTreeCollection.clear()
    bpy.context.scene.mlpLayerTreeCollection_ID = -1
    
    bpy.ops.vtoolpt.collectsetlayers()

def cb_selectPaintingLayer(self,value):
    
    lNode = paintingLayers.getLayerNodeById(bpy.context.scene.mlpLayerTreeCollection_ID)
    
    
    if lNode != None:
        
        cs = paintingLayers.getLayerColorSpace()
        if cs == "color":
            colorImage = lNode.node_tree.nodes["Color"].image
            bpy.context.tool_settings.image_paint.canvas = colorImage
        else:
            maskImage = lNode.node_tree.nodes["Mask"].image
            bpy.context.tool_settings.image_paint.canvas = maskImage
        
        if lNode.node_tree.nodes["Mask"].image != None:
            lNode.node_tree.nodes["PL_InputMaskOpacity"].outputs[0].default_value = 1
        else:
            lNode.node_tree.nodes["PL_InputMaskOpacity"].outputs[0].default_value = 0
    
    bpy.context.scene.mlpFilterLayerCollection.clear()
    bpy.context.scene.mlpFilterLayerCollection_ID = -1
    
    bpy.ops.vtoolpt.collectlayerfilter()
                

def cb_setLayerVisibilty(self, value):
    
    #lNode = paintingLayers.getLayerNodeById(bpy.context.scene.mlpLayerTreeCollection_ID)
    lNode = paintingLayers.getLayerNodeById(self.layerID)
    
    if self.visible == True:
        lNode.node_tree.nodes["PL_OpacityOffset"].inputs[0].default_value =  1
    else:
        lNode.node_tree.nodes["PL_OpacityOffset"].inputs[0].default_value =  0
        
    
def cb_renameLayerSet(self, value):
    
    lsNode = paintingLayers.getActiveLayerSetByName(self.layerSetName)
    if lsNode != None:
        lsNode.label = self.name


def cb_renamePaintingLayer(self, value):

    lNode = paintingLayers.getLayerNodeByName(self.layerName)
    if lNode != None:
        lNode.label = self.name

def cb_selectFilterLayer(self, value):
    
    return None

    
# --- FILTERS TREE ---------#

class VTOOLS_UL_FilterlayerTree(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
            layout.prop(item, "name", text="", emboss=False, translate=False)
         
class VTOOLS_CC_FilterlayerCollection(bpy.types.PropertyGroup):
       
    name = bpy.props.StringProperty(default='')
    filterLayerID = bpy.props.IntProperty()
    filterLayerName = bpy.props.StringProperty(name="filterLayer", default="filterLayer")
        
# --- PAINTING LAYER TREE --- #

class VTOOLS_UL_layerTree(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        
        image = None
        selectedLayer = paintingLayers.getLayerNodeSelected()
        if selectedLayer != None:
            itemLayerNode = paintingLayers.getLayerNodeById(item.layerID)
            layerNode = paintingLayers.getLayerNodeByName(item.layerName)
            isSelectedLayer = selectedLayer.name == item.layerName
            cs = item.colorSpace
            
            colorEmboss = False
            maskEmboss = False
            

            if isSelectedLayer:
                if cs == "color":
                    layout.label(text="", icon="IMAGE")
                    colorEmboss = True
                else:
                    layout.label(text="", icon="IMAGE_ALPHA") 
                    maskEmboss = True
            else:
                layout.label(text="", icon="DOT") 
                
   
            row = layout.row(align=True)
            
            
            #row.operator(paintingLayers.VTOOLS_OP_DuplicatePaintingLayer.bl_idname, text="", icon='HIDE_OFF')
            
            
            imageColor = layerNode.node_tree.nodes["Color"].image
            imageMask = layerNode.node_tree.nodes["Mask"].image
            
            if imageColor != None:    
                opm = row.operator(paintingLayers.VTOOLS_OP_SelectLayerColorSpace.bl_idname, text="", icon_value=imageColor.preview.icon_id, emboss=colorEmboss)   
                opm.color = "color"
                opm.layerID = item.layerID
                #row.label(text="", icon_value=imageColor.preview.icon_id)
            else:
                #row.label(text="", icon="FILE") 
                opm = row.operator(paintingLayers.VTOOLS_OP_SelectLayerColorSpace.bl_idname, text="", icon="FILE", emboss=colorEmboss)   
                opm.color = "color"
                opm.layerID = item.layerID
                
            if imageMask != None:
                opm = row.operator(paintingLayers.VTOOLS_OP_SelectLayerColorSpace.bl_idname, text="", icon_value=imageMask.preview.icon_id, emboss=maskEmboss)   
                opm.color = "mask"
                opm.layerID = item.layerID
                #row.label(text="", icon_value=imageMask.preview.icon_id)
            else:
                #row.label(text="", icon="FILE") 
                opm = row.operator(paintingLayers.VTOOLS_OP_SelectLayerColorSpace.bl_idname, text="", icon="FILE", emboss=maskEmboss)   
                opm.color = "mask"
                opm.layerID = item.layerID
            
            row = layout.row(align=True)
            row.enabled = isSelectedLayer  
                
            if cs == "color":
                row.prop(layerNode.node_tree.nodes["Color"], "image", text="")
            else:
                row.prop(layerNode.node_tree.nodes["Mask"], "image", text="")
            
            row = layout.row(align=True)
            row.prop(item, "visible", text="", icon='HIDE_OFF', translate=False)
            

            

            

            
class VTOOLS_CC_layerTreeCollection(bpy.types.PropertyGroup):
       
    name = bpy.props.StringProperty(default='', update = cb_renamePaintingLayer)
    layerID = bpy.props.IntProperty()
    layerName = bpy.props.StringProperty(name="layerName", default="layerName")
    
    colorSpace = bpy.props.EnumProperty(
    items=(
        ("color", "Color Texture", 'color space',  'IMAGE', 1),
        ("mask", "Mask Texture", 'mask space',  'IMAGE_ALPHA', 2),
    ),
    name="colorSpaceEnum",
    default="color",
    update = cb_selectPaintingLayer
    )
    
    visible = bpy.props.BoolProperty(default=True, update=cb_setLayerVisibilty)
    


# --- LAYER SET TREE ---------#

class VTOOLS_UL_layerSetTree(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, translate=False)
        #layout.prop(item, "layerSetName", text="", emboss=False, translate=False)
        
            
class VTOOLS_CC_layerSetCollection(bpy.types.PropertyGroup):
       
    name = bpy.props.StringProperty(default='', update=cb_renameLayerSet)
    layerSetID = bpy.props.IntProperty()
    layerSetName = bpy.props.StringProperty(name="layerName", default="layerName")
    
# ----- REGISTER -------------#


def register():
    
    bpy.utils.register_class(VTOOLS_CC_layerTreeCollection)
    bpy.utils.register_class(VTOOLS_UL_layerTree)
    bpy.utils.register_class(VTOOLS_CC_layerSetCollection)
    bpy.utils.register_class(VTOOLS_UL_layerSetTree)
    bpy.utils.register_class(VTOOLS_UL_FilterlayerTree)
    bpy.utils.register_class(VTOOLS_CC_FilterlayerCollection)
    
    bpy.types.Scene.mlpLayerTreeCollection_ID = bpy.props.IntProperty(update=cb_selectPaintingLayer, default = -1)
    bpy.types.Scene.mlpLayerTreeCollection = bpy.props.CollectionProperty(type=VTOOLS_CC_layerTreeCollection)
    
    #bpy.context.scene.mlpLayerTreeCollection.clear()
    #bpy.context.scene.mlpLayerTreeCollection_ID = -1
    
    bpy.types.Scene.mlpLayerSetsCollection = bpy.props.CollectionProperty(type=VTOOLS_CC_layerSetCollection)
    bpy.types.Scene.mlpLayerSetsCollection_ID = bpy.props.IntProperty(update=cb_selectLayerSet, default = -1) #bpy.props.StringProperty(update = callback_editFilter)
    
    #bpy.context.scene.mlpLayerSetsCollection.clear()
    #bpy.context.scene.mlpLayerSetsCollection_ID = -1
    
    bpy.types.Scene.mlpFilterLayerCollection = bpy.props.CollectionProperty(type=VTOOLS_CC_FilterlayerCollection)
    bpy.types.Scene.mlpFilterLayerCollection_ID = bpy.props.IntProperty(update=cb_selectFilterLayer, default = -1) #bpy.props.StringProperty(update = callback_editFilter)
    
    #bpy.context.scene.mlpFilterLayerCollection.clear()
    #bpy.context.scene.mlpFilterLayerCollection_ID = -1
    

    return {'FINISHED'}

def unregister():
    
    bpy.utils.unregister_class(VTOOLS_CC_layerTreeCollection)
    bpy.utils.unregister_class(VTOOLS_UL_layerTree)
    bpy.utils.unregister_class(VTOOLS_CC_layerSetCollection)
    bpy.utils.unregister_class(VTOOLS_UL_layerSetTree)
    bpy.utils.unregister_class(VTOOLS_UL_FilterlayerTree)
    bpy.utils.unregister_class(VTOOLS_CC_FilterlayerCollection)
    
    del bpy.types.Scene.mlpLayerTreeCollection_ID
    del bpy.types.Scene.mlpLayerTreeCollection
    
    del bpy.types.Scene.mlpLayerSetsCollection_ID
    del bpy.types.Scene.mlpLayerSetsCollection
    
    del bpy.types.Scene.mlpFilterLayerCollection_ID
    del bpy.types.Scene.mlpFilterLayerCollection
     
    return {'FINISHED'}

classes = (
    
    VTOOLS_CC_layerTreeCollection,
    VTOOLS_UL_layerTree,

)


# ---------------------------------- #





