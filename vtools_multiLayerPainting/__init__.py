bl_info = {
    "name": "vtools - Multi Layer Painting",
    "author": "Antonio Mendoza",
    "location": "View3D > Sidebar > View Tab > Tool",
    "version": (0, 1, 2),
    "blender": (2, 80, 0),
    "description": "Tools for Multi Layering Painting",
    "category": "3D View"  
}


if "bpy" in locals():
    import importlib    
    importlib.reload(createNodes)
    importlib.reload(paintingLayers)
    importlib.reload(paintingSet)
    importlib.reload(uiLayerTree)
    importlib.reload(layerFilters)
    importlib.reload(mergeLayers)
    
else:
      
    from vtools_multiLayerPainting import createNodes
    from vtools_multiLayerPainting import paintingLayers
    from vtools_multiLayerPainting import paintingSet
    from vtools_multiLayerPainting import uiLayerTree
    from vtools_multiLayerPainting import layerFilters
    from vtools_multiLayerPainting import mergeLayers
    
    #remove when releasingp
    import importlib
    importlib.reload(createNodes)  
    importlib.reload(paintingLayers) 
    importlib.reload(paintingSet) 
    importlib.reload(uiLayerTree) 
    importlib.reload(layerFilters)
    importlib.reload(mergeLayers)
    
import bpy 


class VTOOLS_PT_PaintingSets(bpy.types.Panel):
    bl_label = "Painting Sets"
    bl_parent_id = "VTOOLS_PT_MultiLayerPainting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_options = {'DEFAULT_CLOSED'}
    

    def draw(self, context):
        
        layout = self.layout
        
        if bpy.context.scene.vt_mpPaintActiveMaterial == bpy.context.object.active_material.name:
            if context.object.active_material != None:
             
                row = layout.row()
                col = row.column(align=True)
                col.template_list('VTOOLS_UL_layerSetTree', "layerSetID ", context.scene, "mlpLayerSetsCollection", context.scene, "mlpLayerSetsCollection_ID", rows=2)
                
                
                col = row.column(align=True)  
                col.operator(paintingSet.VTOOLS_OP_CollectPaintingSets.bl_idname, text="",icon='FILE_REFRESH')
                
                if bpy.context.scene.vt_layerSetNodeType != "":
                    col.operator(paintingSet.VTOOLS_OP_AddPaintingSet.bl_idname, text="",icon='ADD')
                    col.operator(paintingSet.VTOOLS_OP_DeletePaintingSet.bl_idname, text="",icon='REMOVE')
                    col.operator(paintingSet.VTOOLS_OP_DuplicatePaintingSet.bl_idname, text="",icon='DUPLICATE')
            
            else:
                layout.label(text="No material found in active object")
        else:
            layout.operator(paintingSet.VTOOLS_OP_CollectPaintingSets.bl_idname, text="Update",icon='FILE_REFRESH')
            

class VTOOLS_PT_LayerTree(bpy.types.Panel):
    bl_label = "Painting Layers"
    bl_parent_id = "VTOOLS_PT_MultiLayerPainting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_options = {'DEFAULT_CLOSED'}
    

    def draw(self, context):
        layout = self.layout
        
        if bpy.context.scene.vt_mpPaintActiveMaterial == bpy.context.object.active_material.name:
            
            paintingSetId = bpy.context.scene.mlpLayerSetsCollection_ID > -1

            if paintingSetId == True and context.object.active_material != None:
                
                layout.operator("image.save_all_modified", text="Save All Images", icon='FILE_TICK')
                
                row = layout.row()
                col = row.column(align=True)
                col.template_list('VTOOLS_UL_layerTree', "layerID ", context.scene, "mlpLayerTreeCollection", context.scene, "mlpLayerTreeCollection_ID", rows=4)
                  
                col = row.column(align=True)
                col.operator(paintingLayers.VTOOLS_OP_AddPaintingLayer.bl_idname, text="",icon='ADD')
                col.operator(paintingLayers.VTOOLS_OP_DeletePaintingLayer.bl_idname, text="", icon='REMOVE')
                col.operator(paintingLayers.VTOOLS_OP_DuplicatePaintingLayer.bl_idname, text="", icon='DUPLICATE')

                col.separator()
                
                col.operator(paintingLayers.VTOOLS_OP_MovePaintingLayerDown.bl_idname, text="", icon='TRIA_UP')
                col.operator(paintingLayers.VTOOLS_OP_MovePaintingLayerUp.bl_idname, text="", icon='TRIA_DOWN')
                
                layerNode = paintingLayers.getLayerNodeSelected()
                
                if layerNode != None:
                    
                    activeImage = None
                    cs = paintingLayers.getLayerColorSpace()
                    selectedLayer = paintingLayers.getLayerSelectedFromTree()
                
                              
                    if cs == "color":
                        activeImage = layerNode.node_tree.nodes["Color"].image
                        layout.template_ID(layerNode.node_tree.nodes["Color"], "image", new="image.new", open="image.open")
                    else:
                        activeImage = layerNode.node_tree.nodes["Mask"].image
                        layout.template_ID(layerNode.node_tree.nodes["Mask"], "image", new="image.new", open="image.open")
                    
                    layout.prop(selectedLayer,"colorSpace", text=" ", toggle=True, expand=True)
                    layout.separator()    
                    layout.label(text="Layer Properties")

                    col = layout.column(align=True)
                    col.prop(layerNode.node_tree.nodes["PL_BlendMode"], "blend_type", text="")
                    col.prop(layerNode.inputs["Opacity"], "default_value", text="Opacity", slider=True)
                    col.prop(layerNode.inputs["Global Filter"], "default_value", text="Global Filter Layer", slider=True)
                    
                    ps = context.tool_settings.image_paint
                    if ps.canvas != activeImage:
                        ps.canvas = activeImage
            else:
                layout.label(text="No Painting Set selected")
        else:
            layout.operator(paintingSet.VTOOLS_OP_CollectPaintingSets.bl_idname, text="Update",icon='FILE_REFRESH')
            
          
class VTOOLS_PT_MergeProperties(bpy.types.Panel):
    bl_label = "Merge Layers"
    bl_parent_id = "VTOOLS_PT_MultiLayerPainting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}
    

    def draw(self, context):
        layout = self.layout
        layerNode = paintingLayers.getLayerNodeSelected()
        
        if layerNode != None:
            #layout.prop(context.scene,"mlpDeleteBakedLayers", text="Delete Baked Layers")
            col = layout.column(align=True)
            col.prop(context.scene, "mlpNumLayersToBake", text="Num Layeys Below")
            col.operator(mergeLayers.VTOOLS_OP_mergeLayers.bl_idname, text="Merge Layers", icon='TRIA_UP')
        else:
            layout.label(text="No layer selected")  
                        
class VTOOLS_PT_LayerFiltersProperties(bpy.types.Panel):
    bl_label = "Layer Filters"
    bl_parent_id = "VTOOLS_PT_MultiLayerPainting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layerNode = paintingLayers.getLayerNodeSelected()
        filterNode = layerFilters.getFilterNodeSelected()
        
        if layerNode != None:
            
            row = layout.row()
            
            col = row.column()
            col.template_list('VTOOLS_UL_FilterlayerTree', "filterLayerID", context.scene, "mlpFilterLayerCollection", context.scene, "mlpFilterLayerCollection_ID", rows=2)
            
            
            col = row.column(align=True)
            #col.operator(layerFilters.VTOOLS_OP_AddLayerFilter.bl_idname, text="",icon='ADD')
            col.menu(layerFilters.VTOOLS_MT_FiltersMenu.bl_idname, text="",icon='ADD')
            col.operator(layerFilters.VTOOLS_OP_DeleteLayerFilter.bl_idname, text="", icon='REMOVE')
            
            col.separator()
            
            opDN = col.operator(layerFilters.VTOOLS_OP_MoveLayerFilter.bl_idname, text="", icon='TRIA_UP')
            opDN.direction = "DOWN"
            
            opUP = col.operator(layerFilters.VTOOLS_OP_MoveLayerFilter.bl_idname, text="", icon='TRIA_DOWN')
            opUP.direction = "UP"
            
            
            if filterNode != None:
                
                for i in filterNode.inputs:
                    if len(i.links) == 0:
                        layout.prop(i,"default_value", text=i.name)
                    
                layout.separator()
                
                if hasattr(filterNode, "draw_buttons_ext"):
                    filterNode.draw_buttons_ext(context, layout)
                elif hasattr(filterNode, "draw_buttons"):
                    filterNode.draw_buttons(context, layout)
        else:
            layout.label(text="No layer selected")  
                
class VTOOLS_PT_LayerProperties(bpy.types.Panel):
    bl_label = "Image Transform"
    bl_parent_id = "VTOOLS_PT_MultiLayerPainting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
               
        layerNode = paintingLayers.getLayerNodeSelected()
        colorSpace = paintingLayers.getLayerColorSpace()
    
        if layerNode != None:
            
            if colorSpace == "color":
                colorTextureNode = layerNode.node_tree.nodes["Color"]
                
                
                layout.separator()
                
                row = layout.row(align=True)
                row.label(text="", icon="IMAGE")
                row.label(text="Transform:")
                
                
                layout.prop(layerNode.node_tree.nodes["colorMapNode"], "scale", text="Scale")
                layout.prop(layerNode.node_tree.nodes["colorMapNode"], "rotation", text="Rotation")
                layout.prop(layerNode.node_tree.nodes["colorMapNode"], "translation", text="Location")
                
                layout.separator()
                layout.label(text="UV Map:")
                if hasattr(layerNode.node_tree.nodes["colorUVNode"], "draw_buttons_ext"):
                    layerNode.node_tree.nodes["colorUVNode"].draw_buttons_ext(context, layout)
                    
                
            else:
                maskTextureNode = layerNode.node_tree.nodes["Mask"]
                
                layout.separator()
                
                row = layout.row(align=True)
                row.label(text="", icon="IMAGE_ALPHA")
                row.label(text="Transform:")
                
                layout.prop(layerNode.node_tree.nodes["maskMapNode"], "scale", text="Scale")
                layout.prop(layerNode.node_tree.nodes["maskMapNode"], "rotation", text="Rotation")
                layout.prop(layerNode.node_tree.nodes["maskMapNode"], "translation", text="Location")
                
                layout.separator()
                layout.label(text="UV Map:")
                if hasattr(layerNode.node_tree.nodes["maskUVNode"], "draw_buttons_ext"):
                    layerNode.node_tree.nodes["maskUVNode"].draw_buttons_ext(context, layout)
                       
        else:
            layout.label(text="No layer selected")
            
        
                         
        
class VTOOLS_PT_MultiLayerPainting(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Layer Painting"
    bl_category = 'Tool'
    bl_options = {'DEFAULT_CLOSED'}       
        
    @classmethod
    def poll(cls, context):
        
        return (context.mode == 'PAINT_TEXTURE')
        #return (context.object)
    
    def draw(self,context):
        layout = self.layout
        
        
# -- REGISTRATION -- #        

modules = (

    createNodes,
    paintingLayers,
    paintingSet,
    uiLayerTree,
    layerFilters,
    mergeLayers
) 

classes = (VTOOLS_PT_MultiLayerPainting, VTOOLS_PT_PaintingSets, VTOOLS_PT_LayerTree, VTOOLS_PT_LayerFiltersProperties, VTOOLS_PT_LayerProperties, VTOOLS_PT_MergeProperties, )

def register():
    
    from bpy.utils import register_class
    
    #classes
    for cls in classes:
        register_class(cls)
    
    #submodules
    for mod in modules:
        mod.register()
    
    #createNodes.init()
    
def unregister():
    from bpy.utils import unregister_class
    
    #clases     
    for cls in classes:
        unregister_class(cls)
        
    #submodules
    for mod in modules:
        mod.unregister()
    
    
if __name__ == '__main__':
    register()
    
               
