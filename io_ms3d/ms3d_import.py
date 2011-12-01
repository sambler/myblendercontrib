# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


###############################################################################
#234567890123456789012345678901234567890123456789012345678901234567890123456789
#--------1---------2---------3---------4---------5---------6---------7---------
# <pep8 compliant>


# ##### BEGIN COPYRIGHT BLOCK #####
#
# initial script copyright (c)2011 Alexander Nussbaumer
#
# ##### END COPYRIGHT BLOCK #####


# To support reload properly, try to access a package var, if it's there, reload everything
if ("bpy" in locals()):
    import imp
    #if "ms3d_export" in locals():
    #    imp.reload(ms3d_export)
    #if "ms3d_import" in locals():
    #    imp.reload(ms3d_import)
    if "ms3d_spec" in locals():
        imp.reload(ms3d_spec)
    if "ms3d_utils" in locals():
        imp.reload(ms3d_utils)
    #print("MS3D-add-on Reloaded")

else:
    #from . import ms3d_export
    #from . import ms3d_import
    from . import ms3d_spec
    from . import ms3d_utils
    #print("MS3D-add-on Imported")


#import python stuff
import io
import sys
import time
import os
import math
import mathutils

#import blender stuff
import bpy
import bpy_extras.io_utils
from bpy_extras.image_utils import load_image

from bpy.props import *


#
# DEBUG
#
def DEBUG_print(s):
    if(ms3d_utils._DEBUG):
        print("ms3d_import.{0}".format(s))
    pass


###############################################################################
def prop(name):
    return "ms3d_{0}".format(name)


###############################################################################
def hashStr(obj):
    return str(hash(obj))


PROP_NAME_HASH = "import_hash"


###############################################################################
# registered entry point import
class ImportMS3D(
    bpy.types.Operator,
    bpy_extras.io_utils.ImportHelper
    ):
    """
    Load a MilkShape3D MS3D File
    """

    #DEBUG_print("ImportMS3D")

    bl_idname = "io_ms3d.ms3d_import"
    bl_label = "Import MS3D"
    bl_description = "Import from a MS3D file format (.ms3d)"
    bl_options = {"PRESET"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "TOOL" #"WINDOW"

    filename_ext = ms3d_utils.FILE_EXT
    filter_glob = bpy.props.StringProperty(
        default = ms3d_utils.FILE_FILTER,
        options = {"HIDDEN"}
        )

    filepath = bpy.props.StringProperty(subtype = "FILE_PATH")

    prop_debug = bpy.props.BoolProperty(
        name = ms3d_utils.PROP_NAME_DEBUG,
        description = ms3d_utils.PROP_DESC_DEBUG,
        default = ms3d_utils.PROP_DEFAULT_DEBUG,
        options = ms3d_utils.PROP_OPT_DEBUG,
        )

    prop_verbose = bpy.props.BoolProperty(
        name = ms3d_utils.PROP_NAME_VERBOSE,
        description = ms3d_utils.PROP_DESC_VERBOSE,
        default = ms3d_utils.PROP_DEFAULT_VERBOSE,
        options = ms3d_utils.PROP_OPT_VERBOSE,
        )

    prop_coordinate_system = EnumProperty(
        name = ms3d_utils.PROP_NAME_COORDINATESYSTEM,
        description = ms3d_utils.PROP_DESC_COORDINATESYSTEM,
        items = ms3d_utils.PROP_ITEMS_COORDINATESYSTEM,
        default = ms3d_utils.PROP_DEFAULT_COORDINATESYSTEM_IMP,
        options = ms3d_utils.PROP_OPT_COORDINATESYSTEM,
        )

    prop_scale = FloatProperty(
        name = ms3d_utils.PROP_NAME_SCALE,
        description = ms3d_utils.PROP_DESC_SCALE,
        default = ms3d_utils.PROP_DEFAULT_SCALE,
        min = ms3d_utils.PROP_MIN_SCALE,
        max = ms3d_utils.PROP_MAX_SCALE,
        soft_min = ms3d_utils.PROP_SMIN_SCALE,
        soft_max = ms3d_utils.PROP_SMAX_SCALE,
        options = ms3d_utils.PROP_OPT_SCALE,
        )

    prop_unit_mm = bpy.props.BoolProperty(
        name = ms3d_utils.PROP_NAME_UNIT_MM,
        description = ms3d_utils.PROP_DESC_UNIT_MM,
        default = ms3d_utils.PROP_DEFAULT_UNIT_MM,
        options = ms3d_utils.PROP_OPT_UNIT_MM,
        )

    prop_objects = EnumProperty(
        name = ms3d_utils.PROP_NAME_OBJECTS_IMP,
        description = ms3d_utils.PROP_DESC_OBJECTS_IMP,
        items = ms3d_utils.PROP_ITEMS_OBJECTS_IMP,
        default = ms3d_utils.PROP_DEFAULT_OBJECTS_IMP,
        options = ms3d_utils.PROP_OPT_OBJECTS_IMP,
        )

    prop_animation = bpy.props.BoolProperty(
        name = ms3d_utils.PROP_NAME_ANIMATION,
        description = ms3d_utils.PROP_DESC_ANIMATION,
        default = ms3d_utils.PROP_DEFAULT_ANIMATION,
        options = ms3d_utils.PROP_OPT_ANIMATION,
        )

    #prop_layer_geometry = bpy.props.BoolVectorProperty(
    #    name = ms3d_utils.PROP_NAME_LAYER_GEOMETRY,
    #    description = ms3d_utils.PROP_DESC_LAYER_GEOMETRY,
    #    default = ms3d_utils.PROP_DEFAULT_LAYER_GEOMETRY,
    #    options = ms3d_utils.PROP_OPT_LAYER_GEOMETRY,
    #    subtype = ms3d_utils.PROP_STYPE_LAYER_GEOMETRY,
    #    size = ms3d_utils.PROP_SIZE_LAYER_GEOMETRY,
    #    )

    #prop_layer_armature = bpy.props.BoolVectorProperty(
    #    name = ms3d_utils.PROP_NAME_LAYER_ARMARTURE,
    #    description = ms3d_utils.PROP_DESC_LAYER_ARMARTURE,
    #    default = ms3d_utils.PROP_DEFAULT_LAYER_ARMARTURE,
    #    options = ms3d_utils.PROP_OPT_LAYER_ARMARTURE,
    #    subtype = ms3d_utils.PROP_STYPE_LAYER_ARMARTURE,
    #    size = ms3d_utils.PROP_SIZE_LAYER_ARMARTURE,
    #    )

    prop_reuse = EnumProperty(
        name = ms3d_utils.PROP_NAME_REUSE,
        description = ms3d_utils.PROP_DESC_REUSE,
        items = ms3d_utils.PROP_ITEMS_REUSE,
        default = ms3d_utils.PROP_DEFAULT_REUSE,
        options = ms3d_utils.PROP_OPT_REUSE,
        )


    # draw the option panel
    def draw(self, context):
        layout = self.layout
        ms3d_utils.SetupMenuImport(self, layout)

    # entrypoint for MS3D -> blender
    def execute(self, blenderContext):
        """
        start executing
        """
        #DEBUG_print("ImportMS3D.execute")
        return self.ReadMs3d(blenderContext)

    def invoke(self, blenderContext, event):
        #DEBUG_print("ImportMS3D.invoke")
        blenderContext.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    # create empty blender ms3dTemplate
    # read ms3d file
    # fill blender with ms3dTemplate content
    def ReadMs3d(self, blenderContext):
        """
        read ms3d file and convert ms3d content to bender content
        """
        #DEBUG_print("ReadMs3d")

        t1 = time.time()

        try:
            # setup environment
            ms3d_utils.PreSetupEnvironment(self)

            # inject dictionaries
            # handle internal ms3d names to external blender names
            # to prevent potential name collisions on multiple imports
            # with same names but different content
            self.dict_armatures = {}
            self.dict_bones = {}
            self.dict_groups = {}
            self.dict_images = {}
            self.dict_materials = {}
            self.dict_meshes = {}
            self.dict_objects = {}
            self.dict_textures = {}

            #DEBUG_print("ReadMs3d - entering try block")

            # create an empty ms3d template
            ms3dTemplate = ms3d_spec.ms3d_file_t(self.filepath_splitted[1])

            #DEBUG_print("ReadMs3d - empty ms3d template created")

            # open ms3d file
            #DEBUG_print(self.filepath)
            self.file = io.FileIO(self.properties.filepath, "r")
            #DEBUG_print("ReadMs3d - file opend to read")

            # read and inject ms3d data disk to blender
            #DEBUG_print("ReadMs3d - read & parse file")
            ms3dTemplate.read(self.file)
            #DEBUG_print("ReadMs3d - file readed and parsed")

            # close ms3d file
            self.file.close()
            #DEBUG_print("ReadMs3d - file closed")

            # inject ms3d data to blender
            self.BlenderFromMs3d(blenderContext, ms3dTemplate)
            #DEBUG_print("ReadMs3d - data injected")

            # finalize/restore environment
            ms3d_utils.PostSetupEnvironment(self, self.prop_unit_mm)

        except:
            for i in range(len(sys.exc_info())):
                print("ReadMs3d - exception in try block '{0}'".format(sys.exc_info()[i]))

            raise

        else:
            #DEBUG_print("ReadMs3d - passed try block")
            pass

        t2 = time.time()
        print("elapsed time: {0:.4}s".format(t2 - t1))

        return {"FINISHED"}


    ###########################################################################
    def BlenderFromMs3d(self, blenderContext, ms3dTemplate):
        #DEBUG_print("BlenderFromMs3d")

        isValid, statistics = ms3dTemplate.isValid()

        if (self.prop_verbose):
            ms3dTemplate.print_internal()

        if (isValid):
            #DEBUG_print("BlenderFromMs3d 2")
            if (ms3d_utils.PROP_ITEM_OBJECT_JOINT in self.prop_objects):
                bones = self.CreateArmature(blenderContext, ms3dTemplate)
                pass

            for ms3dGroup in ms3dTemplate.groups:
                blenderMesh = self.CreateMesh(blenderContext, ms3dTemplate, ms3dGroup)

                # apply material if available
                if (ms3d_utils.PROP_ITEM_OBJECT_MATERIAL in self.prop_objects) and (ms3dGroup.materialIndex >= 0):
                    blenderMaterial = self.CreateMaterial(blenderContext, ms3dTemplate.materials[ms3dGroup.materialIndex], blenderMesh.uv_textures[0])
                    blenderMesh.materials.append(blenderMaterial)

                # apply smoothing groups
                if (ms3d_utils.PROP_ITEM_OBJECT_SMOOTHGROUPS in self.prop_objects):
                    self.GenerateSmoothGroups(blenderContext, ms3dTemplate, ms3dGroup, blenderMesh.faces)

                # apply tris to quads
                if (ms3d_utils.PROP_ITEM_OBJECT_TRI_TO_QUAD in self.prop_objects):
                    ms3d_utils.EnableEditMode(True)

                    # remove double vertices
                    ms3d_utils.SelectAll(True) # mesh

                    # convert tris to quads
                    if bpy.ops.mesh.tris_convert_to_quads.poll():
                        bpy.ops.mesh.tris_convert_to_quads()

                    ms3d_utils.EnableEditMode(False)

                self.PostSetupMesh()


            # put all objects to group
            if (ms3d_utils.PROP_ITEM_OBJECT_GROUP in self.prop_objects):
                blenderGroup, setupGroup = self.GetGroup(ms3dTemplate)
                if setupGroup:
                    for item in self.dict_objects.values():
                        blenderGroup.objects.link(item)


            print()
            print("######################################################################")
            print("MS3D -> Blender : [{0}]".format(self.filepath_splitted[1]))
            print(statistics)
            print("######################################################################")

        #DEBUG_print("BlenderFromMs3d #finished")


    ###########################################################################
    def CreateArmature(self, blenderContext, ms3dTemplate):
        """
        known issues: roll angle of the bones may be different as in ms3d
        """
        if (ms3dTemplate.nNumJoints <= 0):
            return None

        blenderScene = blenderContext.scene

        blenderArmature, setupArmature = self.GetArmature(ms3dTemplate)
        if setupArmature:
            blenderArmature.draw_type = "STICK"
            blenderArmature.show_axes = True
            blenderArmature.use_auto_ik = True

        blenderObject, setupObject = self.GetObject(ms3dTemplate, blenderArmature)
        if setupObject:
            blenderObject.location = blenderContext.scene.cursor_location
            blenderObject.show_x_ray = True
            blenderScene.objects.link(blenderObject)

        blenderScene.objects.active = blenderObject

        ms3d_utils.EnableEditMode(True)

        blenderBones = blenderArmature.edit_bones

        bones = {}
        bones_parentName = None
        for iBone, ms3dJoint in enumerate(ms3dTemplate.joints):
            #DEBUG_print(ms3dJoint.name)

            blenderBone = blenderBones.new(ms3dJoint.name)
            bones[ms3dJoint.name] = (blenderBone, ms3dJoint)

            blenderBones.active = blenderBone

            mathVector = mathutils.Vector(ms3dJoint.position)
            mathVector = mathVector * self.matrixViewport

            if (iBone == 0):
                blenderBone.tail = mathVector
                blenderBone.head = blenderBone.tail + mathutils.Vector((-1.0, 0.0, 0.0))
                bones_parentName = ms3dJoint.name

            else:
                # some models have more than one initial bone (with no parent)
                # no idea how to handle correctly
                if (not ms3dJoint.parentName) or (len(ms3dJoint.parentName) <= 0):
                    blenderBoneParent = bones[bones_parentName][0]
                else:
                    blenderBoneParent = bones[ms3dJoint.parentName][0]

                blenderBone.parent = blenderBoneParent

                #DEBUG_print("blenderBone.parent_recursive={0}:{1}".format(blenderBone.name, [key.name for key in blenderBone.parent_recursive]))

                matrixRotation = mathutils.Matrix()
                for blenderBoneParent in blenderBone.parent_recursive:
                    key = blenderBoneParent.name

                    # correct rotaion axis
                    rotationAxis = mathutils.Vector((-bones[key][1].rotation[0], -bones[key][1].rotation[1], -bones[key][1].rotation[2]))
                    rotationAxis = rotationAxis * self.matrixSwapAxis

                    rotation = mathutils.Euler(rotationAxis, "XZY")

                    matrixRotation = matrixRotation * rotation.to_matrix().to_4x4()

                #matrixRotation[3][0] = matrixRotation[3][1] = matrixRotation[3][2] = 0.0

                blenderBone.tail = blenderBone.parent.tail + (mathVector * matrixRotation)

                #blenderBoneParent.align_roll(mathutils.Vector((0.0, 0.0, 1.0)))


            blenderBone.use_local_location = True
            blenderBone.use_connect = True
            blenderBone.select = True

        ms3d_utils.EnableEditMode(False)

        #ms3d_utils.EnablePoseMode(True)
        #for iBone, ms3dJoint in enumerate(ms3dTemplate.joints):
        #    print(ms3dJoint.name)

        #    blenderBone = blenderObject.pose.bones[iBone]
        #    blenderBones.active = blenderBone

        #    mathRotation = mathutils.Vector(ms3dJoint.rotation) * self.matrixSwapAxis
        #    matrixRotationX = mathutils.Matrix.Rotation(mathRotation[0], 4, "X")
        #    matrixRotationY = mathutils.Matrix.Rotation(mathRotation[1], 4, "Y")
        #    matrixRotationZ = mathutils.Matrix.Rotation(mathRotation[2], 4, "Z")
        #    matrixRotation = matrixRotationX * matrixRotationY * matrixRotationZ
        #    mathVectorUp = mathutils.Vector([0.0, 0.0, 1.0])
        #    mathVectorUp = mathVectorUp * matrixRotation

        #ms3d_utils.EnablePoseMode(False)

        return bones


    ###########################################################################
    def CreateImageTexture(self, ms3dMaterial, alphamap, allow_create = True):
        blenderImage, setupImage = self.GetImage(ms3dMaterial, alphamap, allow_create = allow_create)
        if setupImage:
            pass
    
        blenderTexture, setupTexture = self.GetTexture(ms3dMaterial, alphamap, blenderImage, allow_create = allow_create)
        if setupTexture:
            blenderTexture.image = blenderImage
        
            if (alphamap):
                blenderTexture.use_preview_alpha = True

        return blenderTexture


    ###########################################################################
    def CreateMaterial(self, blenderContext, ms3dMaterial, blenderUvLayer):
        blenderMaterial, setupMaterial = self.GetMaterial(ms3dMaterial)
        if setupMaterial:
            blenderMaterial[prop(PROP_NAME_HASH)] = hashStr(ms3dMaterial)
            blenderMaterial[prop(ms3d_spec.PROP_NAME_MODE)] = ms3dMaterial.mode
            blenderMaterial.ambient = ((ms3dMaterial._ambient[0] + ms3dMaterial._ambient[1] + ms3dMaterial._ambient[2]) / 3.0) * ms3dMaterial._ambient[3]
            #blenderMaterial.ambient = ms3dMaterial._ambient[3]

            blenderMaterial.diffuse_color[0] = ms3dMaterial._diffuse[0]
            blenderMaterial.diffuse_color[1] = ms3dMaterial._diffuse[1]
            blenderMaterial.diffuse_color[2] = ms3dMaterial._diffuse[2]
            blenderMaterial.diffuse_intensity = ms3dMaterial._diffuse[3]

            blenderMaterial.specular_color[0] = ms3dMaterial._specular[0]
            blenderMaterial.specular_color[1] = ms3dMaterial._specular[1]
            blenderMaterial.specular_color[2] = ms3dMaterial._specular[2]
            blenderMaterial.specular_intensity = ms3dMaterial._specular[3]

            blenderMaterial.emit = ((ms3dMaterial._emissive[0] + ms3dMaterial._emissive[1] + ms3dMaterial._emissive[2]) / 3.0) * ms3dMaterial._emissive[3]
            #blenderMaterial.emit = ms3dMaterial._emissive[3]

            blenderMaterial.specular_hardness = ms3dMaterial.shininess

            if (ms3dMaterial.transparency):
                blenderMaterial.use_transparency = True
                blenderMaterial.alpha = ms3dMaterial.transparency
                blenderMaterial.specular_alpha = blenderMaterial.alpha

            if (blenderMaterial.game_settings):
                blenderMaterial.game_settings.use_backface_culling = False
                blenderMaterial.game_settings.alpha_blend = "ALPHA"

            # diffuse texture
            if (ms3dMaterial.texture) and (len(ms3dMaterial.texture) > 0):
                blenderMaterial[prop(ms3d_spec.PROP_NAME_TEXTURE)] = ms3dMaterial.texture
                blenderTexture = self.CreateImageTexture(ms3dMaterial, False)

                blenderTextureSlot = blenderMaterial.texture_slots.add()
                blenderTextureSlot.texture = blenderTexture
                blenderTextureSlot.texture_coords = "UV"
                blenderTextureSlot.uv_layer = blenderUvLayer.name
                blenderTextureSlot.use_map_color_diffuse = True
                blenderTextureSlot.use_map_alpha = False

                # apply image also to uv's
                for blenderTextureFace in blenderUvLayer.data:
                    blenderTextureFace.image = blenderTexture.image

            # alpha texture
            if (ms3dMaterial.alphamap) and (len(ms3dMaterial.alphamap) > 0):
                blenderMaterial[prop(ms3d_spec.PROP_NAME_ALPHAMAP)] = ms3dMaterial.alphamap
                blenderMaterial.alpha = 0
                blenderMaterial.specular_alpha = 0

                blenderTexture = self.CreateImageTexture(ms3dMaterial, True)

                blenderTextureSlot = blenderMaterial.texture_slots.add()
                blenderTextureSlot.texture = blenderTexture
                blenderTextureSlot.texture_coords = "UV"
                blenderTextureSlot.uv_layer = blenderUvLayer.name
                blenderTextureSlot.use_map_color_diffuse = False
                blenderTextureSlot.use_map_alpha = True
                blenderTextureSlot.use_rgb_to_intensity = True

        else:
            if (ms3dMaterial.texture) and (len(ms3dMaterial.texture) > 0):
                blenderTexture = self.CreateImageTexture(ms3dMaterial, False, allow_create = False)

                # apply image also to uv's
                if blenderTexture:
                    for blenderTextureFace in blenderUvLayer.data:
                        blenderTextureFace.image = blenderTexture.image

        return blenderMaterial


    ###########################################################################
    def CreateMesh(self, blenderContext, ms3dTemplate, ms3dGroup):
        vertices = []
        edges = []
        faces = []

        #DEBUG_print("CreateMesh 2")
        for ms3dVertex in ms3dTemplate.vertices:
            mathVector = mathutils.Vector(ms3dVertex.vertex)
            mathVector = mathVector * self.matrixViewport
            vertices.append(mathVector)

        for i in ms3dGroup.triangleIndices:
            #DEBUG_print("CreateMesh 3a index={0}, triangle={1}".format(i, ms3dTemplate.triangles[i]))
            faces.append(ms3dTemplate.triangles[i].vertexIndices)

        blenderScene = blenderContext.scene

        blenderMesh, setupMesh = self.GetMesh(ms3dGroup)

        blenderObject, setupObject = self.GetObject(ms3dGroup, blenderMesh)
        blenderObject.location = blenderScene.cursor_location
        blenderScene.objects.link(blenderObject)

        # setup mesh
        #DEBUG_print("from_pydata:\nvertices={0}\nedges={1}\nfaces={2}".format(vertices, edges, faces))

        blenderMesh.from_pydata(vertices, edges, faces)
        if (not edges) or (len(edges) <= 0):
            blenderMesh.update(calc_edges = True)

        ##DEBUG_print("blenderMesh:")
        #for v in blenderMesh.vertices:
        #    #DEBUG_print("vertices={0}".format(v.co))
        #    pass
        #for e in blenderMesh.edges:
        #    #DEBUG_print("edges={0}".format((e.vertices[0], e.vertices[1])))
        #    pass
        #for f in blenderMesh.faces:
        #    #DEBUG_print("faces={0}".format((f.vertices_raw[0], f.vertices_raw[1], f.vertices_raw[2])))
        #    pass

        # make new object as active and only selected object
        ms3d_utils.SelectAll(False) # object

        blenderObject.select = True
        bpy.context.scene.objects.active = blenderObject

        # handle UVs
        # add UVs
        if (not blenderMesh.uv_textures) and bpy.ops.mesh.uv_texture_add.poll():
            bpy.ops.mesh.uv_texture_add()

        # convert ms3d-ST to blender-UV
        for i, blenderUv in enumerate(blenderMesh.uv_textures[0].data):
            blenderUv.uv1[0], blenderUv.uv1[1] = ms3dTemplate.triangles[ms3dGroup.triangleIndices[i]].s[0], (1.0 - ms3dTemplate.triangles[ms3dGroup.triangleIndices[i]].t[0])
            blenderUv.uv2[0], blenderUv.uv2[1] = ms3dTemplate.triangles[ms3dGroup.triangleIndices[i]].s[1], (1.0 - ms3dTemplate.triangles[ms3dGroup.triangleIndices[i]].t[1])
            blenderUv.uv3[0], blenderUv.uv3[1] = ms3dTemplate.triangles[ms3dGroup.triangleIndices[i]].s[2], (1.0 - ms3dTemplate.triangles[ms3dGroup.triangleIndices[i]].t[2])


        # remove double and deserted vertices
        ms3d_utils.EnableEditMode(True)

    
        if (ms3d_utils.PROP_ITEM_OBJECT_JOINT in self.prop_objects):
            #bpy.ops.object.modifier_add(type = "ARMATURE")
            pass

        # remove double vertices
        ms3d_utils.SelectAll(True) # mesh
        if bpy.ops.mesh.remove_doubles.poll():
            bpy.ops.mesh.remove_doubles(limit = 0.0001)

        # remove deserted vertices
        ms3d_utils.SelectAll(False) # mesh
        if bpy.ops.mesh.select_by_number_vertices.poll():
            bpy.ops.mesh.select_by_number_vertices(type = "OTHER")
        if bpy.ops.mesh.delete.poll():
            bpy.ops.mesh.delete(type = "VERT")

        ms3d_utils.EnableEditMode(False)

        return blenderMesh


    ###########################################################################
    def GenerateSmoothGroups(self, blenderContext, ms3dTemplate, ms3dGroup, blenderFaces):
        """
        split faces of a smoothingGroup.
        it will preserve the UVs and materials.

        SIDE-EFFECT: it will change the order of faces!
        """
        #DEBUG_print("GenerateSmoothGroups")

        # smooth mesh to see its smoothed region
        if bpy.ops.object.shade_smooth.poll():
            bpy.ops.object.shade_smooth()


        nFaces = len(blenderFaces)

        # collect smoothgroups and its faces
        smoothGroupFaceIndices = {}
        for iTriangle, ms3dTriangleIndex in enumerate(ms3dGroup.triangleIndices):
            smoothGroupKey = ms3dTemplate.triangles[ms3dTriangleIndex].smoothingGroup

            if (smoothGroupKey == 0):
                continue

            if (smoothGroupKey not in smoothGroupFaceIndices):
                smoothGroupFaceIndices[smoothGroupKey] = []

            smoothGroupFaceIndices[smoothGroupKey].append(iTriangle)

        nKeys = len(smoothGroupFaceIndices)

        #DEBUG_print("GenerateSmoothGroups number of smoothGroups={0}".format(nKeys))
        #DEBUG_print("GenerateSmoothGroups smoothGroupFaceIndices={0}".format(smoothGroupFaceIndices))

        # handle smoothgroups, if more than one is available
        if (nKeys <= 1):
            return

        # enable edit-mode
        ms3d_utils.EnableEditMode(True)

        for smoothGroupKey in smoothGroupFaceIndices:
            # deselect all "faces"
            ms3d_utils.SelectAll(False) # mesh

            # enable object-mode (important for face.select = value)
            ms3d_utils.EnableEditMode(False)

            # select faces of current smoothgroup
            for faceIndex in smoothGroupFaceIndices[smoothGroupKey]:
                blenderFaces[faceIndex].select = True

            # enable edit-mode again
            ms3d_utils.EnableEditMode(True)

            #debug = []
            #for f in blenderFaces:
            #    debug.append((f.vertices_raw[0],f.vertices_raw[1],f.vertices_raw[2]))
            ##DEBUG_print("blenderFaces before split = {0}".format(debug))

            ## split selected faces
            ## WARNING: it will reorder the faces!
            ## after that it is impossible to use the dictionary for the next outstanding smoothgroups with that logic anymore
            #if bpy.ops.mesh.split.poll():
            #    bpy.ops.mesh.split()

            #debug = []
            #for f in blenderFaces:
            #    debug.append((f.vertices_raw[0],f.vertices_raw[1],f.vertices_raw[2]))
            ##DEBUG_print("blenderFaces after split = {0}".format(debug))

            # SPLIT WORKAROUND part 1
            # duplicate selected faces
            if bpy.ops.mesh.duplicate.poll():
                bpy.ops.mesh.duplicate()


        ## SPLIT WORKAROUND START part 2
        # cleanup old faces
        #
        ms3d_utils.SelectAll(False) # mesh

        # enable object-mode (important for face.select = value)
        ms3d_utils.EnableEditMode(False)

        # select all old faces
        for faceIndex in range(nFaces):
            blenderFaces[faceIndex].select = True
            pass

        # enable edit-mode again
        ms3d_utils.EnableEditMode(True)

        # delete old faces and its vertices
        if bpy.ops.mesh.delete.poll():
            bpy.ops.mesh.delete(type = "VERT")
        #
        ## SPLIT WORKAROUND END part 2


        # enable object-mode
        ms3d_utils.EnableEditMode(False)

        pass


    ###########################################################################
    def PostSetupMesh(self):
        ms3d_utils.EnableEditMode(True)
        ms3d_utils.SelectAll(True) # mesh
        ms3d_utils.EnableEditMode(False)


    ###########################################################################
    def GetAction(self, nameAction):
        # already available
        blenderAction = self.dict_actions.get(nameAction)
        if (blenderAction):
            return blenderAction, False

        # create new
        blenderAction = bpy.data.actions.new(nameAction)
        self.dict_actions[nameAction] = blenderAction
        if blenderAction:
            blenderAction[prop(ms3d_spec.PROP_NAME_NAME)] = nameAction
        return blenderAction, True


    ###########################################################################
    def GetArmature(self, ms3dObject):
        nameArmature = ms3dObject.name

        # already available
        blenderArmature = self.dict_armatures.get(nameArmature)
        if (blenderArmature):
            return blenderArmature, False

        # create new
        blenderArmature = bpy.data.armatures.new(nameArmature)
        self.dict_armatures[nameArmature] = blenderArmature
        if blenderArmature:
            blenderArmature[prop(ms3d_spec.PROP_NAME_NAME)] = nameArmature
        return blenderArmature, True


    ###########################################################################
    def GetBone(self, ms3dJoint):
        nameBone = ms3dJoint.name

        # already available
        blenderBone = self.dict_bones.get(nameBone)
        if (blenderBone):
            return blenderBone, False

        # create new
        blenderBone = bpy.data.armatures.new(nameBone)
        self.dict_bones[nameBone] = blenderArmature
        if blenderBone:
            blenderBone[prop(ms3d_spec.PROP_NAME_NAME)] = nameBone
        return blenderBone, True


    ###########################################################################
    def GetGroup(self, ms3dObject):
        nameGroup = ms3dObject.name

        # already available
        blenderGroup = self.dict_groups.get(nameGroup)
        if (blenderGroup):
            return blenderGroup, False

        # create new
        blenderGroup = bpy.data.groups.new(nameGroup)
        self.dict_groups[nameGroup] = blenderGroup
        if blenderGroup:
            blenderGroup[prop(ms3d_spec.PROP_NAME_NAME)] = nameGroup
        return blenderGroup, True


    ###########################################################################
    def GetImage(self, ms3dMaterial, alphamap, allow_create = True):
        if alphamap:
            nameImageRaw = ms3dMaterial.alphamap
            propName = ms3d_spec.PROP_NAME_ALPHAMAP
        else:
            nameImageRaw = ms3dMaterial.texture
            propName = ms3d_spec.PROP_NAME_TEXTURE

        nameImage = os.path.split(nameImageRaw)[1]
        nameDirectory = self.filepath_splitted[0]

        # already available
        blenderImage = self.dict_images.get(nameImage)
        if (blenderImage):
            return blenderImage, False

        # OPTIONAL: try to find an existing one, that fits
        if (self.prop_reuse == ms3d_utils.PROP_ITEM_REUSE_MATCH_VALUES):
            testBlenderImage = bpy.data.images.get(nameImage, None)
            if (testBlenderImage):
                # take a closer look to its content
                if (
                    (not testBlenderImage.library)
                    and (os.path.split(testBlenderImage.filepath)[1] == nameImage)
                ):
                    return testBlenderImage, False

        #elif (self.prop_reuse == ms3d_utils.PROP_ITEM_REUSE_MATCH_HASH):
        #    # irrespecting its real content
        #    # take materials, that have the same "ms3d_import_hash" custom property (of an previous import)
        #    propKey = prop(PROP_NAME_HASH)
        #    hexHash = hex(hash(nameImage))
        #    for testBlenderImage in bpy.data.images:
        #        if (testBlenderImage) and (not testBlenderImage.library) and (propKey in testBlenderImage) and (testBlenderImage[propKey] == hexHash):
        #            return testBlenderImage, False

        if not allow_create:
            return None, False

        # create new
        blenderImage = load_image(nameImage, nameDirectory) #bpy.data.images.new(nameImage)
        self.dict_images[nameImage] = blenderImage
        if blenderImage:
            blenderImage[prop(ms3d_spec.PROP_NAME_NAME)] = ms3dMaterial.name
            blenderImage[prop(propName)] = nameImageRaw
        return blenderImage, True


    ###########################################################################
    def GetTexture(self, ms3dMaterial, alphamap, blenderImage, allow_create = True):
        if alphamap:
            nameTextureRaw = ms3dMaterial.alphamap
            propName = ms3d_spec.PROP_NAME_ALPHAMAP
        else:
            nameTextureRaw = ms3dMaterial.texture
            propName = ms3d_spec.PROP_NAME_TEXTURE

        nameTexture = os.path.split(nameTextureRaw)[1]

        # already available
        blenderTexture = self.dict_textures.get(nameTexture)
        if (blenderTexture):
            return blenderTexture, False

        # OPTIONAL: try to find an existing one, that fits
        if self.prop_reuse == ms3d_utils.PROP_ITEM_REUSE_MATCH_VALUES:
            testBlenderTexture = bpy.data.textures.get(nameTexture, None)
            if (testBlenderTexture):
                # take a closer look to its content
                if (
                    (not testBlenderTexture.library)
                    and (testBlenderTexture.type == "IMAGE")
                    and (testBlenderTexture.image)
                    and (blenderImage)
                    and (testBlenderTexture.image.filepath == blenderImage.filepath)
                ):
                    return testBlenderTexture, False

        #elif self.prop_reuse == ms3d_utils.PROP_ITEM_REUSE_MATCH_HASH:
        #    # irrespecting its real content
        #    # take materials, that have the same "ms3d_import_hash" custom property (of an previous import)
        #    propKey = prop(PROP_NAME_HASH)
        #    hexHash = hex(hash(nameTexture))
        #    for testBlenderTexture in bpy.data.textures:
        #        if (testBlenderTexture) and (not testBlenderTexture.library) and (propKey in testBlenderTexture) and (testBlenderTexture[propKey] == hexHash):
        #            return testBlenderTexture, False

        if not allow_create:
            return None, False

        # create new
        blenderTexture = bpy.data.textures.new(name = nameTexture, type = "IMAGE")
        self.dict_textures[nameTexture] = blenderTexture
        if blenderTexture:
            blenderTexture[prop(ms3d_spec.PROP_NAME_NAME)] = ms3dMaterial.name
            blenderTexture[prop(propName)] = nameTextureRaw
        return blenderTexture, True


    ###########################################################################
    def GetMaterial(self, ms3dMaterial):
        nameMaterial = ms3dMaterial.name
        
        # already available
        blenderMaterial = self.dict_materials.get(nameMaterial)
        if (blenderMaterial):
            return blenderMaterial, False

        # OPTIONAL: try to find an existing one, that fits
        if self.prop_reuse == ms3d_utils.PROP_ITEM_REUSE_MATCH_VALUES:
            # irrespecting non tested real content
            # take materials, that have similar values
            epsilon = 0.00001
            for testBlenderMaterial in bpy.data.materials:
                # take a closer look to its content
                if (
                    (testBlenderMaterial)
                    and (not testBlenderMaterial.library)
                    and (epsilon > abs(testBlenderMaterial.ambient - ((ms3dMaterial._ambient[0] + ms3dMaterial._ambient[1] + ms3dMaterial._ambient[2]) / 3.0) * ms3dMaterial._ambient[3]))
                    and (epsilon > abs(testBlenderMaterial.diffuse_color[0] - ms3dMaterial._diffuse[0]))
                    and (epsilon > abs(testBlenderMaterial.diffuse_color[1] - ms3dMaterial._diffuse[1]))
                    and (epsilon > abs(testBlenderMaterial.diffuse_color[2] - ms3dMaterial._diffuse[2]))
                    and (epsilon > abs(testBlenderMaterial.diffuse_intensity - ms3dMaterial._diffuse[3]))
                    and (epsilon > abs(testBlenderMaterial.specular_color[0] - ms3dMaterial._specular[0]))
                    and (epsilon > abs(testBlenderMaterial.specular_color[1] - ms3dMaterial._specular[1]))
                    and (epsilon > abs(testBlenderMaterial.specular_color[2] - ms3dMaterial._specular[2]))
                    and (epsilon > abs(testBlenderMaterial.specular_intensity - ms3dMaterial._specular[3]))
                    and (epsilon > abs(testBlenderMaterial.emit - ((ms3dMaterial._emissive[0] + ms3dMaterial._emissive[1] + ms3dMaterial._emissive[2]) / 3.0) * ms3dMaterial._emissive[3]))
                ):
                    #DEBUG_print("passed test color")

                    # diffuse texture
                    fitTexture = False
                    testTexture = False
                    if (ms3dMaterial.texture) and (len(ms3dMaterial.texture) > 0):
                        testTexture = True
                        #DEBUG_print("test texture")

                        if (testBlenderMaterial.texture_slots):
                            nameTexture = os.path.split(ms3dMaterial.texture)[1]

                            for blenderTextureSlot in testBlenderMaterial.texture_slots:
                                if (
                                    (blenderTextureSlot)
                                    and (blenderTextureSlot.use_map_color_diffuse)
                                    and (blenderTextureSlot.texture)
                                    and (blenderTextureSlot.texture.type == "IMAGE")
                                    and
                                    (
                                        (
                                            (blenderTextureSlot.texture.image)
                                            and (blenderTextureSlot.texture.image.filepath)
                                            and (os.path.split(blenderTextureSlot.texture.image.filepath)[1] == nameTexture)
                                        )
                                        or
                                        (
                                            (not blenderTextureSlot.texture.image)
                                            and (blenderTextureSlot.texture.name == nameTexture)
                                        )
                                    )
                                ):
                                    fitTexture = True
                                    #DEBUG_print("passed test texture")
                                    break;

                    fitAlpha = False
                    testAlpha = False
                    # alpha texture
                    if (ms3dMaterial.alphamap) and (len(ms3dMaterial.alphamap) > 0):
                        testAlpha = True
                        #DEBUG_print("test alpha")

                        if (testBlenderMaterial.texture_slots):
                            nameAlpha = os.path.split(ms3dMaterial.alphamap)[1]

                            for blenderTextureSlot in testBlenderMaterial.texture_slots:
                                if (
                                    (blenderTextureSlot)
                                    and (blenderTextureSlot.use_map_alpha)
                                    and (blenderTextureSlot.texture)
                                    and (blenderTextureSlot.texture.type == "IMAGE")
                                    and
                                    (
                                        (
                                            (blenderTextureSlot.texture.image)
                                            and (blenderTextureSlot.texture.image.filepath)
                                            and (os.path.split(blenderTextureSlot.texture.image.filepath)[1] == nameAlpha)
                                        )
                                        or
                                        (
                                            (not blenderTextureSlot.texture.image)
                                            and (blenderTextureSlot.texture.name == nameAlpha)
                                            )
                                    )
                                ):
                                    fitAlpha = True
                                    #DEBUG_print("passed test alpha")
                                    break;

                    if ((testTexture and fitTexture) or (not testTexture)) and ((testAlpha and fitAlpha) or (not testAlpha)):
                        return testBlenderMaterial, False

        #elif self.prop_reuse == ms3d_utils.PROP_ITEM_REUSE_MATCH_HASH:
        #    # irrespecting its real content
        #    # take materials, that have the same "ms3d_import_hash" custom property (of an previous import)
        #    propKey = prop(PROP_NAME_HASH)
        #    hexHash = hex(hash(ms3dMaterial))
        #    for testBlenderMaterial in bpy.data.materials:
        #        if (testBlenderMaterial) and (not testBlenderMaterial.library) and (propKey in testBlenderMaterial) and (testBlenderMaterial[propKey] == hexHash):
        #            return testBlenderMaterial, False

        # create new
        blenderMaterial = bpy.data.materials.new(nameMaterial)
        self.dict_materials[nameMaterial] = blenderMaterial
        if blenderMaterial:
            blenderMaterial[prop(ms3d_spec.PROP_NAME_NAME)] = nameMaterial
        return blenderMaterial, True


    ###########################################################################
    def GetMesh(self, ms3dGroup):
        nameMesh = ms3dGroup.name

        # already available
        blenderMesh = self.dict_meshes.get(nameMesh)
        if (blenderMesh):
            return blenderMesh, False

        # create new
        blenderMesh = bpy.data.meshes.new(nameMesh)
        self.dict_meshes[nameMesh] = blenderMesh
        if blenderMesh:
            blenderMesh[prop(ms3d_spec.PROP_NAME_NAME)] = nameMesh
        return blenderMesh, True


    ###########################################################################
    def GetObject(self, ms3dObject, objectData):
        nameObject = ms3dObject.name

        # already available
        blenderObject = self.dict_objects.get(nameObject)
        if (blenderObject):
            return blenderObject, False

        # create new
        blenderObject = bpy.data.objects.new(nameObject, objectData)
        self.dict_objects[nameObject] = blenderObject
        if blenderObject:
            blenderObject[prop(ms3d_spec.PROP_NAME_NAME)] = nameObject
        return blenderObject, True


###############################################################################
#234567890123456789012345678901234567890123456789012345678901234567890123456789
#--------1---------2---------3---------4---------5---------6---------7---------
# ##### END OF FILE #####
