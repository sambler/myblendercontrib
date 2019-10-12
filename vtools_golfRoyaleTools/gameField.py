import bpy


def cb_updateFieldDetail(self, value):
    bpy.context.scene.ct_fieldBaseLP.modifiers["Detail"].levels = bpy.context.scene.ct_fieldDetail
    
    cInGameId = bpy.data.collections.find("AREA_INGAME")
    if cInGameId != -1:
        oc = bpy.data.collections[cInGameId].objects
        for obj in oc:
            obj.modifiers["Detail"].levels = bpy.context.scene.ct_fieldDetail
    

def moveObjectToCollection(pObj, pCollectionName):
        
    if bpy.data.collections.find(pCollectionName) != -1:
        for c in pObj.users_collection:
            c.objects.unlink(pObj)
        
        bpy.data.collections[pCollectionName].objects.link(pObj)                  



def collectionHide_set(pCollectionName, pState):
    
    cId = bpy.data.collections.find(pCollectionName)
    if cId != -1:
        c = bpy.data.collections[cId]
        c.hide_viewport = pState
        """
        oldCName = bpy.context.view_layer.active_layer_collection.name
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[pCollectionName]
        bpy.context.collection.hide_viewport = pState
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[oldCName]
        """    
    
    
class VTOOLS_OP_fielGenerate(bpy.types.Operator):
    bl_idname = "camperotools.fieldgenerate"
    bl_label = "Generate"
    bl_description = "Generate in game field"
    bl_options = {'REGISTER', 'UNDO'}
    
    def createBaseCollection(self):
        
        cIBaseLP = bpy.data.collections.find("AREA_BASE_LP")
        if cIBaseLP == -1:
            gc = bpy.data.collections.new(name="AREA_BASE_LP")
            bpy.context.scene.collection.children.link(gc)
            
            
        cId = bpy.data.collections.find("AREA_LINES")
        if cId == -1:
            gc = bpy.data.collections.new(name="AREA_LINES")
            bpy.context.scene.collection.children.link(gc)
            

    def moveAreaLines(self):
        
        for area in bpy.context.scene.ct_fieldAreaCollection:
            area.fieldAreaObject.data.resolution_u = bpy.context.scene.ct_splineAreaDetail
            moveObjectToCollection(area.fieldAreaObject,"AREA_LINES")
            
            if area.fieldAreaBunker != None:
                 moveObjectToCollection(area.fieldAreaBunker,"AREA_LINES")
    
    def createChunksBool(self, pBoxSize, pNumX, pNumY):
        
        cId = bpy.data.collections.find("AREA_CHUNKSBOOL")
        if cId == -1:
            gc = bpy.data.collections.new(name="AREA_CHUNKSBOOL")
            bpy.context.scene.collection.children.link(gc)
        
        for i in range(0,pNumX):
            j = 0
            for j in range(0,pNumY):
                bpy.ops.mesh.primitive_cube_add(enter_editmode=False, location=(i*pBoxSize*-1,j*pBoxSize,0))
                nc = bpy.data.objects[bpy.context.object.name]
                nc.display_type = "WIRE"
                nc.name = "chunkBool.000"
                nc.scale[0] = (pBoxSize/2)
                nc.scale[1] = (pBoxSize/2)
                nc.scale[2] = (pBoxSize/2)
                bpy.ops.object.transform_apply(location=False, rotation = False, scale = True)
                moveObjectToCollection(nc, "AREA_CHUNKSBOOL")
                
                """
                nc.scale[0] += 0.00001
                nc.scale[1] += 0.00001
                nc.scale[2] += 1
                """
                
                mod = nc.modifiers.new(name="subDetail", type="SUBSURF")
                mod.levels = 2
                mod.render_levels = 2
                mod.subdivision_type = "SIMPLE"
                
                """
                mod = nc.modifiers.new(name="deform", type="SIMPLE_DEFORM")
                mod.deform_method = "TAPER"
                mod.deform_axis = "Z"
                mod.factor = 0.001
                """
                
        
                
    def createBaseLPObj(self):
        
        objHP = bpy.context.scene.ct_fieldBaseHP
        objLP = None
        
        if objHP != None:
            
            bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode = False, location=(0,0,0))
            objLP = bpy.data.objects[bpy.context.object.name] 
            objLP.name = "fieldLP.000"
            
            
            sizeX = (objHP.dimensions[0]/bpy.context.scene.ct_numPieces)/objLP.dimensions[0]
            objLP.scale[0] = sizeX
            objLP.scale[1] = sizeX
            
            bpy.context.view_layer.objects.active = objLP
            
            bpy.ops.object.transform_apply(location=False, rotation = False, scale = True)
    
            chunkSize = objLP.dimensions[0]
            chunkCountX = int(objHP.dimensions[0]/chunkSize)
            chunkCountY = int(objHP.dimensions[1]/chunkSize)
            
            
            #CREATE CHUNKS BOOLEANS
            self.createChunksBool(chunkSize, chunkCountX, chunkCountY)
            
            #ADD MODIFIERS
            
            mod_chunksX = objLP.modifiers.new(name="ChunksX", type="ARRAY")
            mod_chunksX.count = chunkCountX
            mod_chunksX.relative_offset_displace[0] = -1
            mod_chunksX.use_merge_vertices = True
            
            mod_chunksY = objLP.modifiers.new(name="ChunksY", type="ARRAY")
            mod_chunksY.count = chunkCountY
            mod_chunksY.relative_offset_displace[0] = 0
            mod_chunksY.relative_offset_displace[1] = 1
            mod_chunksY.use_merge_vertices = True
            
            mod_subdivision = objLP.modifiers.new(name="Detail", type="SUBSURF")
            mod_subdivision.subdivision_type = "SIMPLE"
            mod_subdivision.levels = bpy.context.scene.ct_fieldDetail
            
            #BOOLEANAS
            
            mod_boolInt = objLP.modifiers.new(name="Intersect", type="BOOLEAN")
            mod_boolInt.operation = "INTERSECT"
            mod_boolDif = objLP.modifiers.new(name="Diference", type="BOOLEAN")
            mod_boolDif.operation = "DIFFERENCE"
            mod_boolBunkerDif = objLP.modifiers.new(name="DiferenceBunker", type="BOOLEAN")
            mod_boolBunkerDif.operation = "DIFFERENCE"
            
            #WRAP HP
            
            mod_wrap = objLP.modifiers.new(name="wrap", type="SHRINKWRAP")
            mod_wrap.target = objHP
            mod_wrap.wrap_method = "PROJECT"
            mod_wrap.use_negative_direction = True
            mod_wrap.use_positive_direction = True
            mod_wrap.use_project_z = True
            
            #SET LP MESH
            bpy.context.scene.ct_fieldBaseLP = None
            bpy.context.scene.ct_fieldBaseLP = objLP
            
            #SHOW WIREFRAME
            objLP.show_wire = True
            objLP.show_all_edges = True
            
        return objLP
            
    def execute(self, context):
        
        collectionHide_set("AREA_CHUNKSBOOL", False)
        collectionHide_set("AREA_BASE_LP", False)
        
        self.createBaseCollection()
        baseLPMesh = self.createBaseLPObj()  
        moveObjectToCollection(baseLPMesh, "AREA_BASE_LP")
        self.moveAreaLines()
                
        af = bpy.context.scene.ct_fieldAreaCollection
        cl = bpy.context.scene.ct_fieldAreaCollection_ID
            
        return {'FINISHED'}


class VTOOLS_OP_cutFieldByAreas(bpy.types.Operator):
    bl_idname = "camperotools.cutfieldbyareas"
    bl_label = "Cut field in Areas"
    bl_description = "Cut game field in selected areas"
    bl_options = {'REGISTER', 'UNDO'}
    
    def setCollections(self):
        
        ac = None
        gc = None
        cBoolId = bpy.data.collections.find("AREA_BOOL")
        if cBoolId != -1:
            oc = bpy.data.collections[cBoolId].objects
            for obj in oc:
                bpy.data.objects.remove(obj)
        else:
            #create collcetion 
            ac = bpy.data.collections.new(name="AREA_BOOL")
            bpy.context.scene.collection.children.link(ac)     
        
        cInGameId = bpy.data.collections.find("AREA_INGAME")
        if cInGameId != -1:
            oc = bpy.data.collections[cInGameId].objects
            for obj in oc:
                bpy.data.objects.remove(obj)
        else:    
            #create collection
            gc = bpy.data.collections.new(name="AREA_INGAME")
            bpy.context.scene.collection.children.link(gc)     
        
        
        if ac != None:
            ac.hide_viewport = False
            ac.hide_select = False
        
        if gc != None:
            gc.hide_viewport = False
            gc.hide_select = False
    
                    
    def createBoolMesh(self, pArea):
        
        obj = pArea
        boolArea = None
        
        boolArea = obj.copy()
        bpy.context.scene.collection.objects.link(boolArea)
        boolArea.data = obj.data.copy()
        boolArea.name = "boolArea.000"
        
        boolArea.data.extrude = 200
        boolArea.data.dimensions = "2D"
        boolArea.data.fill_mode = "BOTH"
        
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = boolArea
        boolArea.select_set(state=True)
        bpy.ops.object.convert(target="MESH")
        
        moveObjectToCollection(boolArea, "AREA_BOOL")
        #boolArea.hide_set(state=True)
        
        return boolArea
    
        
    def createBooleanAreas(self):

        booleanList = []
        
        for area in bpy.context.scene.ct_fieldAreaCollection:
            
            area.fieldAreaBool = self.createBoolMesh(area.fieldAreaObject)
            #booleanList.append(boolArea)
            
            if area.fieldAreaBunker != None:
                area.fieldAreaBunkerBool = self.createBoolMesh(area.fieldAreaBunker)
        
        return booleanList
    
    def setMaterials(self,pMeshArea, pAreaData):
        
        numMat = len(pMeshArea.material_slots)
        
        if pAreaData.fieldAreaMaterial != None:
            pMeshArea.data.materials.clear()
            pMeshArea.data.materials.append(pAreaData.fieldAreaMaterial)    
        
    def setBooleans(self, pBoolList):
        
        areas = bpy.context.scene.ct_fieldAreaCollection
        #numBool = len(pBoolList)
        numBool = len(areas)
        
        for i in range(0,numBool):
            meshArea = bpy.context.scene.ct_fieldBaseLP.copy()
            meshArea.data = bpy.context.scene.ct_fieldBaseLP.data.copy()
            meshArea.name = "meshArea.000"
            bpy.context.scene.collection.objects.link(meshArea)
            moveObjectToCollection(meshArea, "AREA_INGAME")
            
            boolArea = areas[i].fieldAreaBool
            
                
            if i == 0:
                meshArea.modifiers["Diference"].object = boolArea         
            else:
                if i == (numBool-1):
                    meshArea.modifiers["Intersect"].object = boolArea    
                else:
                    meshArea.modifiers["Intersect"].object = areas[i-1].fieldAreaBool
                    meshArea.modifiers["Diference"].object = boolArea
            
            if areas[i].fieldAreaBunkerBool != None:
                    
                    #areas[i].fieldAreaBunkerBool.hide_set(state=True)
                    boolBunker = areas[i].fieldAreaBunkerBool
                    moveObjectToCollection(boolBunker, "AREA_BOOL")
                    #boolBunker.hide_set(state=True)
                     
                    meshAreaBunker = bpy.context.scene.ct_fieldBaseLP.copy()
                    meshAreaBunker.data = bpy.context.scene.ct_fieldBaseLP.data.copy()
                    meshAreaBunker.name = "meshAreaBunker.000"
                    bpy.context.scene.collection.objects.link(meshAreaBunker)
                    moveObjectToCollection(meshAreaBunker, "AREA_INGAME")
                    
                    meshAreaBunker.modifiers["Intersect"].object = boolBunker
                    meshArea.modifiers["DiferenceBunker"].object = boolBunker
                    
                    
        
            self.setMaterials(meshArea, areas[i])
                
    def execute(self, context):
        
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection
        self.setCollections()
        lpBase = bpy.context.scene.ct_fieldBaseLP
        boolList = self.createBooleanAreas()
        self.setBooleans(boolList)
        #lpBase.hide_select = True
        #moveObjectToCollection(lpBase, "AREA_INGAME")
        #lpBase.hide_set(state=True)
        
        collectionHide_set("AREA_LINES", True)
        collectionHide_set("AREA_BOOL", True)
        collectionHide_set("AREA_BASE_LP", True)
        collectionHide_set("AREA_CHUNKSBOOL", True)
        collectionHide_set("AREA_INGAME", False)
            
        return {'FINISHED'}
    

class VTOOLS_OP_resetFieldGolf(bpy.types.Operator):
    bl_idname = "camperotools.resetfieldgolf"
    bl_label = "Reset Field Golf"
    bl_description = "Reset Field Golf"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        objLP = bpy.context.scene.ct_fieldBaseLP 
        
        if objLP != None:
            bpy.data.objects.remove(objLP)
            
        cBoolId = bpy.data.collections.find("AREA_BOOL")
        if cBoolId != -1:
            oc = bpy.data.collections[cBoolId].objects
            for obj in oc:
                bpy.data.objects.remove(obj)
                
        cInGameId = bpy.data.collections.find("AREA_INGAME")
        if cInGameId != -1:
            oc = bpy.data.collections[cInGameId].objects
            for obj in oc:
                bpy.data.objects.remove(obj)
                
        cInGameId = bpy.data.collections.find("AREA_CHUNKSBOOL")
        if cInGameId != -1:
            oc = bpy.data.collections[cInGameId].objects
            for obj in oc:
                bpy.data.objects.remove(obj)
        
        cId = bpy.data.collections.find("AREA_MESH")
        if cId != -1:
            oc = bpy.data.collections[cId].objects
            for obj in oc:
                bpy.data.objects.remove(obj)
                
        cId = bpy.data.collections.find("AREA_TOEXPORT")
        if cId != -1:
            oc = bpy.data.collections[cId].objects
            for obj in oc:
                bpy.data.objects.remove(obj)       
        
        collectionHide_set("AREA_MESH", True)
        collectionHide_set("AREA_TOEXPORT", True)
        collectionHide_set("AREA_INGAME", True)
        collectionHide_set("AREA_BOOL", True)        
        collectionHide_set("AREA_LINES", False)
        collectionHide_set("AREA_BASE_LP", False)
        collectionHide_set("AREA_LINES", False)
            
        return {'FINISHED'}
    
class VTOOLS_OP_chunkFieldGolf(bpy.types.Operator):
    bl_idname = "camperotools.chunkfieldgolf"
    bl_label = "Chunk Field Golf"
    bl_description = "Chunk Field Golf"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        collectionHide_set("AREA_TOEXPORT", False)
        
                
        baseExportMesh = bpy.context.scene.ct_fieldToExport
        
        """
        
        if baseExportMesh != None:
            
            mod = baseExportMesh.modifiers.new(name="solid", type="SOLIDIFY")
            mod.thickness = 10
            mod.use_rim = True
        """
                
        cId= bpy.data.collections.find("AREA_CHUNKSBOOL")
        if cId != -1:
            oc = bpy.data.collections[cId].objects
            for obj in oc:
                chunk = baseExportMesh.copy()
                chunk.data = baseExportMesh.data.copy()
                bpy.context.scene.collection.objects.link(chunk)
                chunk.name = "fieldChunk.000"
                chunk.modifiers.new
                chunk.show_wire = False
                
                chunk.select_set(state = True)
                bpy.context.view_layer.objects.active = chunk
                
                for m in chunk.modifiers:
                    try:
                        bpy.ops.object.modifier_apply(apply_as='DATA',modifier=m.name)
                    except:
                        chunk.modifiers.remove(m)
                        pass
                
                #mod = chunk.modifiers.new(name="Triangulate", type="TRIANGULATE")
                
                mod = chunk.modifiers.new(name="Intersect", type="BOOLEAN")
                mod.operation = "INTERSECT"
                mod.object = obj
                
                moveObjectToCollection(chunk, "AREA_TOEXPORT")
            
            collectionHide_set("AREA_INGAME", True)
            collectionHide_set("AREA_MESH", True)
            collectionHide_set("AREA_CHUNKSBOOL", True)
                
                        
        return {'FINISHED'}
    
    
def register():
    
    bpy.types.Scene.ct_numPieces = bpy.props.IntProperty(default = 4, min = 1, max = 1000)
    bpy.types.Scene.ct_fieldDetail = bpy.props.IntProperty(default = 1, min = 1, max = 10, update=cb_updateFieldDetail)
    
    bpy.types.Scene.ct_fieldBaseLP = bpy.props.PointerProperty(name="InGame Field Mesh", type=bpy.types.Object)
    bpy.types.Scene.ct_fieldToExport = bpy.props.PointerProperty(name="Field to Export", type=bpy.types.Object)
    
    
    bpy.utils.register_class(VTOOLS_OP_fielGenerate)
    bpy.utils.register_class(VTOOLS_OP_cutFieldByAreas)
    bpy.utils.register_class(VTOOLS_OP_resetFieldGolf)
    bpy.utils.register_class(VTOOLS_OP_chunkFieldGolf)
    
    return {'FINISHED'}

def unregister():
    
    del bpy.types.Scene.ct_fieldDetail
    del bpy.types.Scene.ct_numPieces

    del bpy.types.Scene.ct_fieldBaseLP
    del bpy.types.Scene.ct_fieldToExport
    
    bpy.utils.unregister_class(VTOOLS_OP_fielGenerate)
    bpy.utils.unregister_class(VTOOLS_OP_cutFieldByAreas)
    bpy.utils.unregister_class(VTOOLS_OP_resetFieldGolf)
    bpy.utils.unregister_class(VTOOLS_OP_chunkFieldGolf)
    
    return {'FINISHED'}