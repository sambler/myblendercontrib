# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation, either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

from math import radians

import bpy
from mathutils import *


class DirectXExporter:
    def __init__(self, Config, context):
        self.Config = Config
        self.context = context

        self.File = File(self.Config.filepath)

        self.Log("Setting up coordinate system...")
        # SystemMatrix converts from right-handed, z-up to left-handed, y-up
        self.SystemMatrix = (Matrix.Scale(-1, 4, Vector((0, 0, 1))) *
            Matrix.Rotation(radians(-90), 4, 'X'))
        self.Log("Done")

        self.Log("Generating object lists for export...")
        if self.Config.SelectedOnly:
            ExportList = list(self.context.selected_objects)
        else:
            ExportList = list(self.context.scene.objects)

        # ExportMap maps Blender objects to ExportObjects
        self.ExportMap = {} # XXX Do we keep ExportMap around in self?  Or should it be local?
        for Object in ExportList:
            if Object.type == 'EMPTY':
                self.ExportMap[Object] = EmptyExportObject(self.Config, self, Object)
            elif Object.type == 'MESH':
                self.ExportMap[Object] = MeshExportObject(self.Config, self,
                    Object)
            elif Object.type == 'ARMATURE':
                self.ExportMap[Object] = ArmatureExportObject(self.Config, self,
                    Object)

        # Find the objects who do not have a parent or whose parent we are
        # not exporting
        self.RootExportList = [Object for Object in self.ExportMap.values()
            if Object.BlenderObject.parent not in ExportList]
        self.RootExportList = Util.SortByNameField(self.RootExportList)
        
        self.ExportList = Util.SortByNameField(self.ExportMap.values())

        # Determine each object's children from the pool of ExportObjects
        for Object in self.ExportMap.values():
            Children = Object.BlenderObject.children
            Object.Children = []
            for Child in Children:
                if Child in self.ExportMap:
                    Object.Children.append(self.ExportMap[Child])
        self.Log("Done")
        
        if self.Config.ExportAnimation:
            AnimationGenerators = self.__GatherAnimationGenerators()
            
            if self.Config.ExportActionsAsSets:
                self.AnimationWriter = SplitSetAnimationWriter(self.Config,
                    self, AnimationGenerators)
            else:
                self.AnimationWriter = JoinedSetAnimationWriter(self.Config,
                    self, AnimationGenerators)

    # "Public" Interface

    def Export(self):
        self.Log("Exporting to {}".format(self.File.FilePath),
            MessageVerbose=False)

        self.Log("Opening file...")
        self.File.Open()
        self.Log("Done")

        self.Log("Writing header...")
        self.__WriteHeader()
        self.Log("Done")

        self.Log("Opening Root frame...")
        self.__OpenRootFrame()
        self.Log("Done")

        self.Log("Writing objects...")
        for Object in self.RootExportList:
            Object.Write()
        self.Log("Done")

        self.Log("Closing Root frame...")
        self.__CloseRootFrame()
        self.Log("Done")
        
        if self.AnimationWriter is not None:
            self.AnimationWriter.WriteAnimationSets()

        self.File.Close()

    def Log(self, String, MessageVerbose=True):
        if self.Config.Verbose is True or MessageVerbose == False:
            print(String)

    # "Private" Methods

    def __WriteHeader(self):
        self.File.Write("xof 0303txt 0032\n\n")

        if self.Config.IncludeFrameRate:
            self.File.Write("template AnimTicksPerSecond {\n\
  <9E415A43-7BA6-4a73-8743-B73D47E88476>\n\
  DWORD AnimTicksPerSecond;\n\
}\n\n")
        if self.Config.ExportSkinWeights:
            self.File.Write("template XSkinMeshHeader {\n\
  <3cf169ce-ff7c-44ab-93c0-f78f62d172e2>\n\
  WORD nMaxSkinWeightsPerVertex;\n\
  WORD nMaxSkinWeightsPerFace;\n\
  WORD nBones;\n\
}\n\n\
template SkinWeights {\n\
  <6f0d123b-bad2-4167-a0d0-80224f25fabb>\n\
  STRING transformNodeName;\n\
  DWORD nWeights;\n\
  array DWORD vertexIndices[nWeights];\n\
  array float weights[nWeights];\n\
  Matrix4x4 matrixOffset;\n\
}\n\n")

    # Start the Root frame and write its transform matrix
    def __OpenRootFrame(self):
        self.File.Write("Frame Root {\n")
        self.File.Indent()

        self.File.Write("FrameTransformMatrix {\n")
        self.File.Indent()
        Util.WriteMatrix(self.File, self.SystemMatrix)
        self.File.Unindent()
        self.File.Write("}\n")

    def __CloseRootFrame(self):
        self.File.Unindent()
        self.File.Write("} // End of Root\n")
    
    def __GatherAnimationGenerators(self):
        Generators = []
        
        if not self.Config.ExportActionsAsSets:
            for Object in self.ExportList:
                if Object.BlenderObject.type == 'ARMATURE':
                    Generators.append(ArmatureAnimationGenerator(self.Config, 
                        None, Object))
                else:
                    Generators.append(GenericAnimationGenerator(self.Config,
                        None, Object))
        else:
            ActionlessObjects = []
            
            for Object in self.ExportList:
                if Object.BlenderObject.animation_data is None:
                    ActionlessObjects.append(Object)
                    continue
                else:
                    if Object.BlenderObject.animation_data.action is None:
                        ActionlessObjects.append(Object)
                        continue
                
                if Object.BlenderObject.type == 'ARMATURE':
                    Generators.append(ArmatureAnimationGenerator(self.Config,
                        Util.SafeName(Object.BlenderObject.animation_data.action.name),
                        Object))
                else:
                    Generators.append(GenericAnimationGenerator(self.Config,
                        Util.SafeName(Object.BlenderObject.animation_data.action.name),
                        Object))
            
            if self.Config.AttachToFirstArmature:
                FirstArmature = None
                for Object in self.ExportList:
                    if Object.BlenderObject.type == 'ARMATURE':
                        FirstArmature = Object
                        break
                    
                if FirstArmature is not None:
                    UsedActions = [BlenderObject.animation_data.action
                        for BlenderObject in bpy.data.objects
                        if BlenderObject.animation_data is not None]
                    FreeActions = [Action for Action in bpy.data.actions
                        if Action not in UsedActions]
                    
                    if FirstArmature in ActionlessObjects and len(FreeActions):
                        ActionlessObjects.remove(FirstArmature)
                    
                    OldAction = None
                    NoData = False
                    if FirstArmature.BlenderObject.animation_data is not None:
                        OldAction = FirstArmature.BlenderObject.animation_data.action
                    else:
                        NoData = True
                        FirstArmature.BlenderObject.animation_data_create()
                    
                    for Action in FreeActions:
                        FirstArmature.BlenderObject.animation_data.action = Action
                        
                        Generators.append(ArmatureAnimationGenerator(self.Config,
                            Util.SafeName(Action.name), FirstArmature))
                    
                    FirstArmature.BlenderObject.animation_data.action = OldAction
                    if NoData:
                        FirstArmature.BlenderObject.animation_data_clear()
            
            if len(ActionlessObjects):
                Generators.append(GroupAnimationGenerator(self.Config,
                    "Default_Action", ActionlessObjects))

        return Generators        


class ExportObject:
    def __init__(self, Config, Exporter, BlenderObject):
        self.Config = Config
        self.Exporter = Exporter
        self.BlenderObject = BlenderObject

        self.name = self.BlenderObject.name # Simple alias
        self.SafeName = Util.SafeName(self.BlenderObject.name)
        self.Children = []

    def __repr__(self):
        return "[ExportObject: {}]".format(self.BlenderObject.name)

    # "Public" Interface

    def Write(self):
        self._OpenFrame()

        self._WriteChildren()

        self._CloseFrame()

    # "Protected" Interface

    def _OpenFrame(self):
        self.Exporter.File.Write("Frame {} {{\n".format(self.SafeName))
        self.Exporter.File.Indent()

        self.Exporter.File.Write("FrameTransformMatrix {\n")
        self.Exporter.File.Indent()
        Util.WriteMatrix(self.Exporter.File, self.BlenderObject.matrix_local)
        self.Exporter.File.Unindent()
        self.Exporter.File.Write("}\n")

    def _CloseFrame(self):
        self.Exporter.File.Unindent()
        self.Exporter.File.Write("}} // End of {}\n".format(self.SafeName))

    def _WriteChildren(self):
        for Child in Util.SortByNameField(self.Children):
            Child.Write()


class EmptyExportObject(ExportObject):
    def __init__(self, Config, Exporter, BlenderObject):
        ExportObject.__init__(self, Config, Exporter, BlenderObject)

    def __repr__(self):
        return "[EmptyExportObject: {}]".format(self.name)
    

class MeshExportObject(ExportObject):
    def __init__(self, Config, Exporter, BlenderObject):
        ExportObject.__init__(self, Config, Exporter, BlenderObject)

    def __repr__(self):
        return "[MeshExportObject: {}]".format(self.name)

    # "Public" Interface

    def Write(self):
        self._OpenFrame()

        if self.Config.ExportMeshes:
            # Generate the export mesh
            Mesh = None
            if self.Config.ApplyModifiers:
                DeactivatedModifierList = []
                
                if self.Config.ExportSkinWeights:
                    DeactivatedModifierList = [Modifier
                        for Modifier in self.BlenderObject.modifiers
                        if Modifier.type == 'ARMATURE' and Modifier.show_viewport]
                
                for Modifier in DeactivatedModifierList:
                    Modifier.show_viewport = False
                        
                Mesh = self.BlenderObject.to_mesh(self.Exporter.context.scene,
                    True, 'PREVIEW')
                
                for Modifier in DeactivatedModifierList:
                    Modifier.show_viewport = True   
            else:
                Mesh = self.BlenderObject.to_mesh(self.Exporter.context.scene,
                    False, 'PREVIEW')
                    
            self.__WriteMesh(Mesh)
            bpy.data.meshes.remove(Mesh)

        self._WriteChildren()

        self._CloseFrame()

    # "Protected"
    
    class _MeshEnumerator:
        def __init__(self, Mesh):
            self.Mesh = Mesh
            
            self.vertices = None 
            self.polygons = None
            
            self.VertexIndexes = None # self.vertices[x] == Mesh.vertices[self.VertexIndexes[x]]
            self.PolygonVertexIndexes = None # Mesh.vertices[Mesh.polygons[x].vertices[y]] == self.vertices[self.PolygonVertexIndexes[x][y]]
    
    class _OneToOneMeshEnumerator(_MeshEnumerator):
        def __init__(self, Mesh):
            MeshExportObject._MeshEnumerator.__init__(self, Mesh)
            
            self.vertices = Mesh.vertices
            self.polygons = Mesh.polygons # Needed? XXX
            
            self.VertexIndexes = tuple(range(0, len(self.vertices))) # Needed?
            self.PolygonVertexIndexes = tuple(tuple(Polygon.vertices)
                for Polygon in Mesh.polygons)

    class _UnrolledFacesMeshEnumerator(_MeshEnumerator):
        def __init__(self, Mesh):
            MeshExportObject._MeshEnumerator.__init__(self, Mesh)
            
            self.vertices = tuple()
            for Polygon in Mesh.polygons:
                self.vertices += tuple(Mesh.vertices[VertexIndex]
                    for VertexIndex in Polygon.vertices)
            
            self.polygons = Mesh.polygons
            
            self.VertexIndexes = tuple()
            for Polygon in Mesh.polygons:
                self.VertexIndexes += tuple(Polygon.vertices)
            
            self.PolygonVertexIndexes = []
            Index = 0
            for Polygon in Mesh.polygons:
                self.PolygonVertexIndexes.append(tuple(range(Index, 
                    Index + len(Polygon.vertices))))
                Index += len(Polygon.vertices)
            
    # "Private" Methods

    def __WriteMesh(self, Mesh):
        self.Exporter.File.Write("Mesh {{ // {} mesh\n".format(self.SafeName))
        self.Exporter.File.Indent()
        
        MeshEnumerator = None
        if (self.Config.ExportUVCoordinates and Mesh.uv_textures):
            MeshEnumerator = MeshExportObject._UnrolledFacesMeshEnumerator(Mesh)
        else:
            MeshEnumerator = MeshExportObject._OneToOneMeshEnumerator(Mesh)
        
        # Write vertex positions
        VertexCount = len(MeshEnumerator.vertices)
        self.Exporter.File.Write("{};\n".format(VertexCount))
        for Index, Vertex in enumerate(MeshEnumerator.vertices):
            Position = Vertex.co
            self.Exporter.File.Write("{:9f};{:9f};{:9f};".format(
                        Position[0], Position[1], Position[2]))
            
            if Index == VertexCount - 1:
                self.Exporter.File.Write(";\n", Indent=False)
            else:
                self.Exporter.File.Write(",\n", Indent=False)
        
        # Write face definitions
        PolygonCount = len(MeshEnumerator.polygons)
        self.Exporter.File.Write("{};\n".format(PolygonCount))
        for Index, PolygonVertexIndexes in enumerate(MeshEnumerator.PolygonVertexIndexes):
            self.Exporter.File.Write("{};".format(len(PolygonVertexIndexes)))
            
            PolygonVertexIndexes = PolygonVertexIndexes[::-1]
            
            for VertexIndex in PolygonVertexIndexes:
                self.Exporter.File.Write("{};".format(VertexIndex), Indent=False)
            
            if Index == PolygonCount - 1:
                self.Exporter.File.Write(";\n", Indent=False)
            else:
                self.Exporter.File.Write(",\n", Indent=False)
            
        if self.Config.ExportNormals:
            self.__WriteMeshNormals(Mesh)
            
        if self.Config.ExportUVCoordinates:
            self.__WriteMeshUVCoordinates(Mesh)

        if self.Config.ExportMaterials:
            self.__WriteMeshMaterials(Mesh)
        
        #if self.Config.ExportVertexColor:
        #    self.__WriteMeshVertexColors(Mesh)
        
        if self.Config.ExportSkinWeights:
            self.__WriteMeshSkinWeights(Mesh, MeshEnumerator=MeshEnumerator)

        self.Exporter.File.Unindent()
        self.Exporter.File.Write("}} // End of {} mesh\n".format(self.SafeName))

    def __WriteMeshNormals(self, Mesh, MeshEnumerator=None):
        class _NormalsMeshEnumerator(MeshExportObject._MeshEnumerator):
            def __init__(self, Mesh):
                MeshExportObject._MeshEnumerator(Mesh)
                
                self.polygons = None
                self.VertexIndexes = None
                
                self.vertices = []
                self.PolygonVertexIndexes = []
                
                Index = 0
                for Polygon in Mesh.polygons:
                    if not Polygon.use_smooth:
                        self.vertices.append(Polygon)
                        self.PolygonVertexIndexes.append(tuple(len(Polygon.vertices) * [Index]))
                        Index += 1
                    else:
                        for Vertex in Polygon.vertices:
                            self.vertices.append(Vertex)
                        self.PolygonVertexIndexes.append(tuple(range(Index, Index + len(Polygon.vertices))))
                        Index += len(Polygon.vertices)            
        
        if MeshEnumerator is None:
            MeshEnumerator = _NormalsMeshEnumerator(Mesh)
        
        self.Exporter.File.Write("MeshNormals {{ // {} normals\n".format(
            self.SafeName))
        self.Exporter.File.Indent()
        
        NormalCount = len(MeshEnumerator.vertices)
        self.Exporter.File.Write("{};\n".format(NormalCount))
        
        # Write mesh normals.
        for Index, Vertex in enumerate(MeshEnumerator.vertices):
            Normal = Vertex.normal
            self.Exporter.File.Write("{:9f};{:9f};{:9f};".format(Normal[0],
                Normal[1], Normal[2]))
            
            if Index == NormalCount - 1:
                self.Exporter.File.Write(";\n", Indent=False)
            else:
                self.Exporter.File.Write(",\n", Indent=False)
        
        # Write face definitions.
        FaceCount = len(MeshEnumerator.PolygonVertexIndexes)
        self.Exporter.File.Write("{};\n".format(FaceCount))
        for Index, Polygon in enumerate(MeshEnumerator.PolygonVertexIndexes):
            self.Exporter.File.Write("{};".format(len(Polygon)))
            
            # Reverse the winding order
            for VertexIndex in Polygon[::-1]:
                self.Exporter.File.Write("{};".format(VertexIndex), Indent=False)
            
            if Index == FaceCount - 1:
                self.Exporter.File.Write(";\n", Indent=False)
            else:
                self.Exporter.File.Write(",\n", Indent=False)

        self.Exporter.File.Unindent()
        self.Exporter.File.Write("}} // End of {} normals\n".format(
            self.SafeName))
     
    def __WriteMeshUVCoordinates(self, Mesh):
        if not Mesh.uv_textures:
            return
        
        self.Exporter.File.Write("MeshTextureCoords {{ // {} UV coordinates\n".
            format(self.SafeName))
        self.Exporter.File.Indent()
        
        UVCoordinates = Mesh.uv_layers.active.data
        
        VertexCount = 0
        for Polygon in Mesh.polygons:
            VertexCount += len(Polygon.vertices)
        
        Index = 0
        self.Exporter.File.Write("{};\n".format(VertexCount))
        for Polygon in Mesh.polygons:
            Vertices = []
            for Vertex in [UVCoordinates[Vertex] for Vertex in
                Polygon.loop_indices]:
                Vertices.append(tuple(Vertex.uv))
            for Vertex in Vertices:
                self.Exporter.File.Write("{:9f};{:9f};".format(Vertex[0],
                    Vertex[1]))
                Index += 1
                if Index == VertexCount:
                    self.Exporter.File.Write(";\n", Indent=False)
                else:
                    self.Exporter.File.Write(",\n", Indent=False)
                    
        self.Exporter.File.Unindent()
        self.Exporter.File.Write("}} // End of {} UV coordinates\n".format(
            self.SafeName))

    def __WriteMeshMaterials(self, Mesh):
        def WriteMaterial(Exporter, Material):
            def GetMaterialTextureFileName(Material):
                if Material:
                    # Create a list of Textures that have type 'IMAGE'
                    ImageTextures = [Material.texture_slots[TextureSlot].texture
                        for TextureSlot in Material.texture_slots.keys()
                        if Material.texture_slots[TextureSlot].texture.type ==
                        'IMAGE']
                    # Refine to only image file names if applicable
                    ImageFiles = [bpy.path.basename(Texture.image.filepath)
                        for Texture in ImageTextures
                        if getattr(Texture.image, "source", "") == 'FILE']
                    if ImageFiles:
                        return ImageFiles[0]
                return None
            
            Exporter.File.Write("Material {} {{\n".format(
                Util.SafeName(Material.name)))
            Exporter.File.Indent()
            
            Diffuse = list(Vector(Material.diffuse_color) *
                Material.diffuse_intensity)
            Diffuse.append(Material.alpha)
            # Map Blender's range of 1 - 511 to 0 - 1000
            Specularity = 1000 * (Material.specular_hardness - 1.0) / 510.0
            Specular = list(Vector(Material.specular_color) *
                Material.specular_intensity)
            
            Exporter.File.Write("{:9f};{:9f};{:9f};{:9f};;\n".format(Diffuse[0],
                Diffuse[1], Diffuse[2], Diffuse[3]))
            Exporter.File.Write(" {:9f};\n".format(Specularity))
            Exporter.File.Write("{:9f};{:9f};{:9f};;\n".format(Specular[0],
                Specular[1], Specular[2]))
            Exporter.File.Write(" 0.000000; 0.000000; 0.000000;;\n")
            
            TextureFileName = GetMaterialTextureFileName(Material)
            if TextureFileName:
                Exporter.File.Write("TextureFilename {{\"{}\";}}\n".format(
                    TextureFileName))
            
            Exporter.File.Unindent()
            Exporter.File.Write("}\n");
        
        Materials = Mesh.materials
        # Do not write materials if there are none
        if not Materials.keys():
            return
        
        self.Exporter.File.Write("MeshMaterialList {{ // {} material list\n".
            format(self.SafeName))
        self.Exporter.File.Indent()
        
        self.Exporter.File.Write("{};\n".format(len(Materials)))
        self.Exporter.File.Write("{};\n".format(len(Mesh.polygons)))
        for Index, Polygon in enumerate(Mesh.polygons):
            self.Exporter.File.Write("{}".format(Polygon.material_index))
            if Index == len(Mesh.polygons) - 1:
                self.Exporter.File.Write(";;\n", Indent=False)
            else:
                self.Exporter.File.Write(",\n", Indent=False)
        
        for Material in Materials:
            WriteMaterial(self.Exporter, Material)
        
        self.Exporter.File.Unindent()
        self.Exporter.File.Write("}} // End of {} material list\n".format(
            self.SafeName))
    
    def __WriteMeshVertexColors(self, Mesh):
        pass
    
    def __WriteMeshSkinWeights(self, Mesh, MeshEnumerator=None):
        class _BoneVertexGroup:
                def __init__(self, BlenderObject, ArmatureObject, BoneName):
                    self.BoneName = BoneName
                    self.SafeName = Util.SafeName(ArmatureObject.name) + "_" + \
                        Util.SafeName(BoneName)
                    
                    self.Indexes = []
                    self.Weights = []
                    
                    # BoneMatrix transforms mesh vertices into the space of the bone.
                    # Here are the final transformations in order:
                    #  - Object Space to World Space
                    #  - World Space to Armature Space
                    #  - Armature Space to Bone Space
                    # This way, when BoneMatrix is transformed by the bone's Frame matrix, the vertices will be in their final world position.
                    
                    self.BoneMatrix = ArmatureObject.data.bones[BoneName].matrix_local.inverted()
                    self.BoneMatrix *= ArmatureObject.matrix_world.inverted()
                    self.BoneMatrix *= BlenderObject.matrix_world
                
                def AddVertex(self, Index, Weight):
                    self.Indexes.append(Index)
                    self.Weights.append(Weight)
        
        if MeshEnumerator is None:
            MeshEnumerator = MeshExportObject._OneToOneMeshEnumerator(Mesh)
        
        ArmatureModifierList = [Modifier 
            for Modifier in self.BlenderObject.modifiers
            if Modifier.type == 'ARMATURE' and Modifier.show_viewport]
        
        if not ArmatureModifierList:
            return
        
        ArmatureObjects = [Modifier.object for Modifier in ArmatureModifierList]
        
        for ArmatureObject in ArmatureObjects:
            PoseBoneNames = [Bone.name for Bone in ArmatureObject.pose.bones]
            VertexGroupNames = [Group.name for Group
                in self.BlenderObject.vertex_groups]
            UsedBoneNames = set(PoseBoneNames).intersection(VertexGroupNames)
            
            BoneVertexGroups = [_BoneVertexGroup(self.BlenderObject, ArmatureObject, BoneName)
                for BoneName in UsedBoneNames]
            
            GroupIndexToBoneVertexGroups = {Group.index : BoneVertexGroup
                for Group in self.BlenderObject.vertex_groups
                for BoneVertexGroup in BoneVertexGroups
                if Group.name == BoneVertexGroup.BoneName}
            
            MaximumInfluences = 0
            
            for Index, Vertex in enumerate(MeshEnumerator.vertices):
                VertexWeightTotal = 0.0
                VertexInfluences = 0
                
                # Sum up the weights of groups that correspond to armature bones.
                for VertexGroup in Vertex.groups:
                    BoneVertexGroup = GroupIndexToBoneVertexGroups.get(VertexGroup.group)
                    if BoneVertexGroup is not None:
                        VertexWeightTotal += VertexGroup.group
                        VertexInfluences += 1
                
                if VertexInfluences > MaximumInfluences:
                    MaximumInfluences = VertexInfluences
                
                # Add the vertex to the bone vertex groups it belongs to, normalizing each bone's weight.
                for VertexGroup in Vertex.groups:
                    BoneVertexGroup = GroupIndexToBoneVertexGroups.get(VertexGroup.group)
                    if BoneVertexGroup is not None:
                        Weight = VertexGroup.weight / VertexWeightTotal
                        BoneVertexGroup.AddVertex(Index, Weight)
            
            self.Exporter.File.Write("XSkinMeshHeader {\n")
            self.Exporter.File.Indent()
            self.Exporter.File.Write("{};\n".format(MaximumInfluences))
            self.Exporter.File.Write("{};\n".format(3 * MaximumInfluences))
            self.Exporter.File.Write("{};\n".format(len(BoneVertexGroups)))
            self.Exporter.File.Unindent()
            self.Exporter.File.Write("}\n")
            
            for BoneVertexGroup in BoneVertexGroups:
                self.Exporter.File.Write("SkinWeights {\n")
                self.Exporter.File.Indent()
                self.Exporter.File.Write("\"{}\";\n".format(BoneVertexGroup.SafeName))
                
                GroupVertexCount = len(BoneVertexGroup.Indexes)
                self.Exporter.File.Write("{};\n".format(GroupVertexCount))
                
                # Write the indexes of the vertices this bone affects.
                for Index, VertexIndex in enumerate(BoneVertexGroup.Indexes):
                    self.Exporter.File.Write("{}".format(VertexIndex))
                    
                    if Index == GroupVertexCount - 1:
                        self.Exporter.File.Write(";\n", Indent=False)
                    else:
                        self.Exporter.File.Write(",\n", Indent=False)
                
                # Write the weights of the affected vertices.
                for Index, VertexWeight in enumerate(BoneVertexGroup.Weights):
                    self.Exporter.File.Write("{:9f}".format(VertexWeight))
                    
                    if Index == GroupVertexCount - 1:
                        self.Exporter.File.Write(";\n", Indent=False)
                    else:
                        self.Exporter.File.Write(",\n", Indent=False)
                
                # Write the bone's matrix.
                Util.WriteMatrix(self.Exporter.File, BoneVertexGroup.BoneMatrix)
            
                self.Exporter.File.Unindent()
                self.Exporter.File.Write("}} // End of {} skin weights\n".format(BoneVertexGroup.SafeName))
            
            
class ArmatureExportObject(ExportObject):
    def __init__(self, Config, Exporter, BlenderObject):
        ExportObject.__init__(self, Config, Exporter, BlenderObject)

    def __repr__(self):
        return "[ArmatureExportObject: {}]".format(self.name)
    
    # "Public" Interface

    def Write(self):
        self._OpenFrame()
        
        if self.Config.ExportArmatureBones:
            Armature = self.BlenderObject.data
            RootBones = [Bone for Bone in Armature.bones if Bone.parent is None]
            self.__WriteBones(RootBones)

        self._WriteChildren()

        self._CloseFrame()
    
    # "Private" Methods
    
    def __WriteBones(self, Bones):
        for Bone in Bones:
            BoneMatrix = Matrix()
            
            if self.Config.ExportRestBone:
                if Bone.parent:
                    BoneMatrix = Bone.parent.matrix_local.inverted()
                BoneMatrix *= Bone.matrix_local
            else:
                PoseBone = self.BlenderObject.pose.bones[Bone.name]
                if Bone.parent:
                    BoneMatrix = PoseBone.parent.matrix.inverted()
                BoneMatrix *= PoseBone.matrix
            
            BoneSafeName = self.SafeName + "_" + \
                Util.SafeName(Bone.name)
            self.__OpenBoneFrame(BoneSafeName, BoneMatrix)
            
            self.__WriteBoneChildren(Bone)
            
            self.__CloseBoneFrame(BoneSafeName)
            
    
    def __OpenBoneFrame(self, BoneSafeName, BoneMatrix):
        self.Exporter.File.Write("Frame {} {{\n".format(BoneSafeName))
        self.Exporter.File.Indent()

        self.Exporter.File.Write("FrameTransformMatrix {\n")
        self.Exporter.File.Indent()
        Util.WriteMatrix(self.Exporter.File, BoneMatrix)
        self.Exporter.File.Unindent()
        self.Exporter.File.Write("}\n")
    
    def __CloseBoneFrame(self, BoneSafeName):
        self.Exporter.File.Unindent()
        self.Exporter.File.Write("}} // End of {}\n".format(BoneSafeName))
    
    def __WriteBoneChildren(self, Bone):
        self.__WriteBones(Util.SortByNameField(Bone.children))


class Animation:
    def __init__(self, SafeName):
        self.SafeName = SafeName
        
        self.RotationKeys = []
        self.ScaleKeys = []
        self.PositionKeys = []
        
    # "Public" Interface
    
    def GetKeyCount(self):
        return len(self.RotationKeys)


class AnimationGenerator:
    def __init__(self, Config, SafeName, ExportObject):
        self.Config = Config
        self.SafeName = SafeName
        self.ExportObject = ExportObject
        
        self.Animations = []


class GenericAnimationGenerator(AnimationGenerator):
    def __init__(self, Config, SafeName, ExportObject):
        AnimationGenerator.__init__(self, Config, SafeName, ExportObject)
        
        self._GenerateKeys()
    
    # "Protected" Interface
    
    def _GenerateKeys(self):
        Scene = bpy.context.scene # Convenience alias
        BlenderCurrentFrame = Scene.frame_current
        
        CurrentAnimation = Animation(self.ExportObject.SafeName)
        BlenderObject = self.ExportObject.BlenderObject
        
        for Frame in range(Scene.frame_start, Scene.frame_end + 1):
            Scene.frame_set(Frame)
            
            Rotation = BlenderObject.rotation_euler.to_quaternion()
            Scale = BlenderObject.matrix_local.to_scale()
            Position = BlenderObject.matrix_local.to_translation()
            
            CurrentAnimation.RotationKeys.append(Rotation)
            CurrentAnimation.ScaleKeys.append(Scale)
            CurrentAnimation.PositionKeys.append(Position)
        
        self.Animations.append(CurrentAnimation)
        Scene.frame_set(BlenderCurrentFrame)
        

class GroupAnimationGenerator(AnimationGenerator):
    def __init__(self, Config, SafeName, ExportObjects):
        AnimationGenerator.__init__(self, Config, SafeName, None)
        self.ExportObjects = ExportObjects
        
        self._GenerateKeys()
    
    # "Protected" Interface
    
    def _GenerateKeys(self):
        for Object in self.ExportObjects:
            if Object.BlenderObject.type == 'ARMATURE':
                TemporaryGenerator = ArmatureAnimationGenerator(self.Config,
                    None, Object)
                self.Animations += TemporaryGenerator.Animations
            else:
                TemporaryGenerator = GenericAnimationGenerator(self.Config,
                    None, Object)
                self.Animations += TemporaryGenerator.Animations


class ArmatureAnimationGenerator(GenericAnimationGenerator):
    def __init__(self, Config, SafeName, ArmatureExportObject):
        GenericAnimationGenerator.__init__(self, Config, SafeName, ArmatureExportObject)
        
        if self.Config.ExportArmatureBones:
            self._GenerateBoneKeys()
        
    # "Protected" Interface
    
    def _GenerateBoneKeys(self):
        from itertools import zip_longest as zip
        
        Scene = bpy.context.scene # Convenience alias
        BlenderCurrentFrame = Scene.frame_current
        
        ArmatureObject = self.ExportObject.BlenderObject
        ArmatureSafeName = self.ExportObject.SafeName
        
        BoneAnimations = [Animation(ArmatureSafeName + "_" + Util.SafeName(Bone.name))
            for Bone in ArmatureObject.pose.bones]
        
        for Frame in range(Scene.frame_start, Scene.frame_end + 1):
            Scene.frame_set(Frame)
            
            for Bone, BoneAnimation in zip(ArmatureObject.pose.bones, BoneAnimations):
                Rotation = ArmatureObject.data.bones[Bone.name].matrix.to_quaternion() * \
                    Bone.rotation_quaternion
                
                PoseMatrix = Matrix()
                if Bone.parent:
                    PoseMatrix = Bone.parent.matrix.inverted()
                PoseMatrix *= Bone.matrix
                
                Scale = PoseMatrix.to_scale()
                Position = PoseMatrix.to_translation()
                
                BoneAnimation.RotationKeys.append(Rotation)
                BoneAnimation.ScaleKeys.append(Scale)
                BoneAnimation.PositionKeys.append(Position)
        
        self.Animations += BoneAnimations
        Scene.frame_set(BlenderCurrentFrame)


class AnimationSet:
    def __init__(self, SafeName, AnimationGenerators):
        self.SafeName = SafeName
        self.AnimationGenerators = AnimationGenerators


class AnimationWriter:
    def __init__(self, Config, Exporter, AnimationGenerators):
        self.Config = Config
        self.Exporter = Exporter
        self.AnimationGenerators = AnimationGenerators
        
        self.AnimationSets = []
        
    # "Public" Interface
    
    def WriteAnimationSets(self):
        if self.Config.IncludeFrameRate:
            self.__WriteFrameRate()
            
        for Set in self.AnimationSets:
            self.Exporter.File.Write("AnimationSet {} {{\n".format(Set.SafeName))
            self.Exporter.File.Indent()
            
            for Generator in Set.AnimationGenerators:
                for CurrentAnimation in Generator.Animations:
                    self.Exporter.File.Write("Animation {\n")
                    self.Exporter.File.Indent()
                    self.Exporter.File.Write("{{{}}}\n".format(CurrentAnimation.SafeName))
                    
                    KeyCount = CurrentAnimation.GetKeyCount()
                    
                    self.Exporter.File.Write("AnimationKey { // Rotation\n");
                    self.Exporter.File.Indent()
                    self.Exporter.File.Write("0;\n")
                    self.Exporter.File.Write("{};\n".format(KeyCount))
                    
                    for Frame, Key in enumerate(CurrentAnimation.RotationKeys):
                        self.Exporter.File.Write("{};4;{:9f},{:9f},{:9f},{:9f};;".format(
                            Frame, -Key[0], Key[1], Key[2], Key[3]))
                        
                        if Frame == KeyCount - 1:
                            self.Exporter.File.Write(";\n", Indent=False)
                        else:
                            self.Exporter.File.Write(",\n", Indent=False)
                    
                    self.Exporter.File.Unindent()
                    self.Exporter.File.Write("}\n")
                    
                    self.Exporter.File.Write("AnimationKey { // Scale\n");
                    self.Exporter.File.Indent()
                    self.Exporter.File.Write("1;\n")
                    self.Exporter.File.Write("{};\n".format(KeyCount))
                    
                    for Frame, Key in enumerate(CurrentAnimation.ScaleKeys):
                        self.Exporter.File.Write("{};3;{:9f},{:9f},{:9f};;".format(
                            Frame, Key[0], Key[1], Key[2]))
                        
                        if Frame == KeyCount - 1:
                            self.Exporter.File.Write(";\n", Indent=False)
                        else:
                            self.Exporter.File.Write(",\n", Indent=False)
                    
                    self.Exporter.File.Unindent()
                    self.Exporter.File.Write("}\n")
                    
                    self.Exporter.File.Write("AnimationKey { // Position\n");
                    self.Exporter.File.Indent()
                    self.Exporter.File.Write("1;\n")
                    self.Exporter.File.Write("{};\n".format(KeyCount))
                    
                    for Frame, Key in enumerate(CurrentAnimation.PositionKeys):
                        self.Exporter.File.Write("{};3;{:9f},{:9f},{:9f};;".format(
                            Frame, Key[0], Key[1], Key[2]))
                        
                        if Frame == KeyCount - 1:
                            self.Exporter.File.Write(";\n", Indent=False)
                        else:
                            self.Exporter.File.Write(",\n", Indent=False)
                    
                    self.Exporter.File.Unindent()
                    self.Exporter.File.Write("}\n")
                    
                    self.Exporter.File.Unindent()
                    self.Exporter.File.Write("}\n")
                    
            self.Exporter.File.Unindent()
            self.Exporter.File.Write("}} // End of AnimationSet {}\n".format(
                Set.SafeName))
    
    # "Private" Methods
    
    def __WriteFrameRate(self):
        Scene = bpy.context.scene # Convenience alias
        FrameRate = int(Scene.render.fps / Scene.render.fps_base)
        
        self.Exporter.File.Write("AnimTicksPerSecond {\n");
        self.Exporter.File.Indent()
        self.Exporter.File.Write("{};\n".format(FrameRate))
        self.Exporter.File.Unindent()
        self.Exporter.File.Write("}\n")


class JoinedSetAnimationWriter(AnimationWriter):
    def __init__(self, Config, Exporter, AnimationGenerators):
        AnimationWriter.__init__(self, Config, Exporter, AnimationGenerators)
        
        self.AnimationSets = [AnimationSet("Global", self.AnimationGenerators)]


class SplitSetAnimationWriter(AnimationWriter):
    def __init__(self, Config, Exporter, AnimationGenerators):
        AnimationWriter.__init__(self, Config, Exporter, AnimationGenerators)
        
        self.AnimationSets = [AnimationSet(Generator.SafeName, [Generator])
            for Generator in AnimationGenerators]


class File:
    def __init__(self, FilePath):
        self.FilePath = FilePath
        self.File = None
        self.__Whitespace = 0

    def Open(self):
        if not self.File:
            self.File = open(self.FilePath, 'w')

    def Close(self):
        self.File.close()
        self.File = None

    def Write(self, String, Indent=True):
        if Indent:
            # Escape any formatting braces
            String = String.replace("{", "{{")
            String = String.replace("}", "}}")
            self.File.write(("{}" + String).format("  " * self.__Whitespace))
        else:
            self.File.write(String)

    def Indent(self, Levels=1):
        self.__Whitespace += Levels

    def Unindent(self, Levels=1):
        self.__Whitespace -= Levels
        if self.__Whitespace < 0:
            self.__Whitespace = 0


class Util:
    @staticmethod
    def SafeName(Name):
        # Replaces each character in OldSet with NewChar
        def ReplaceSet(String, OldSet, NewChar):
            for OldChar in OldSet:
                String = String.replace(OldChar, NewChar)
            return String

        import string

        NewName = ReplaceSet(Name, string.punctuation + " ", "_")
        if NewName[0].isdigit() or NewName in ["ARRAY", "DWORD", "UCHAR",
            "FLOAT", "ULONGLONG", "BINARY_RESOURCE", "SDWORD", "UNICODE",
            "CHAR", "STRING", "WORD", "CSTRING", "SWORD", "DOUBLE", "TEMPLATE"]:
            NewName = "_" + NewName
        return NewName

    @staticmethod
    def WriteMatrix(File, Matrix):
        File.Write("{:9f},{:9f},{:9f},{:9f},\n".format(Matrix[0][0],
            Matrix[1][0], Matrix[2][0], Matrix[3][0]))
        File.Write("{:9f},{:9f},{:9f},{:9f},\n".format(Matrix[0][1],
            Matrix[1][1], Matrix[2][1], Matrix[3][1]))
        File.Write("{:9f},{:9f},{:9f},{:9f},\n".format(Matrix[0][2],
            Matrix[1][2], Matrix[2][2], Matrix[3][2]))
        File.Write("{:9f},{:9f},{:9f},{:9f};;\n".format(Matrix[0][3],
            Matrix[1][3], Matrix[2][3], Matrix[3][3]))
    
    @staticmethod
    def SortByNameField(List):
        def SortKey(x):
            return x.name
        
        return sorted(List, key=SortKey)
