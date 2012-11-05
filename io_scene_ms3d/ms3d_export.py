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

# <pep8 compliant>

###############################################################################
#234567890123456789012345678901234567890123456789012345678901234567890123456789
#--------1---------2---------3---------4---------5---------6---------7---------


# ##### BEGIN COPYRIGHT BLOCK #####
#
# initial script copyright (c)2011,2012 Alexander Nussbaumer
#
# ##### END COPYRIGHT BLOCK #####


#import python stuff
import io
from math import (
        radians,
        )
from mathutils import (
        Vector,
        )
from os import (
        path,
        )
from sys import (
        exc_info,
        )
from time import (
        time,
        )


# To support reload properly, try to access a package var,
# if it's there, reload everything
if ('bpy' in locals()):
    import imp
    if 'io_scene_ms3d.ms3d_strings' in locals():
        imp.reload(io_scene_ms3d.ms3d_strings)
    if 'io_scene_ms3d.ms3d_spec' in locals():
        imp.reload(io_scene_ms3d.ms3d_spec)
    if 'io_scene_ms3d.ms3d_utils' in locals():
        imp.reload(io_scene_ms3d.ms3d_utils)
    if 'io_scene_ms3d.ms3d_ui' in locals():
        imp.reload(io_scene_ms3d.ms3d_ui)
    pass
else:
    from io_scene_ms3d.ms3d_strings import (
            ms3d_str,
            )
    from io_scene_ms3d.ms3d_spec import (
            Ms3dSpec,
            Ms3dModel,
            Ms3dModelEx,
            Ms3dVertex,
            Ms3dVertexEx2,
            Ms3dTriangle,
            Ms3dGroup,
            Ms3dMaterial,
            Ms3dJoint,
            Ms3dJointEx,
            Ms3dRotationKeyframe,
            Ms3dTranslationKeyframe,
            Ms3dComment,
            Ms3dCommentEx,
            )
    from io_scene_ms3d.ms3d_utils import (
            select_all,
            enable_pose_mode,
            enable_edit_mode,
            pre_setup_environment,
            post_setup_environment,
            )
    from io_scene_ms3d.ms3d_ui import (
            Ms3dUi,
            )
    pass


#import blender stuff
from bpy import (
        context,
        ops,
        )
import bmesh


###############################################################################
class Ms3dExporter():
    """ Load a MilkShape3D MS3D File """

    def __init__(self, options):
        self.options = options
        pass

    # create a empty ms3d ms3d_model
    # fill ms3d_model with blender content
    # writer ms3d file
    def write(self, blender_context):
        """convert bender content to ms3d content and write it to file"""

        t1 = time()
        t2 = None

        try:
            # setup environment
            pre_setup_environment(self, blender_context)

            # create an empty ms3d template
            ms3d_model = Ms3dModel()

            # inject blender data to ms3d file
            self.from_blender(blender_context, ms3d_model)

            t2 = time()

            self.file = None
            try:
                # write ms3d file to disk
                self.file = io.FileIO(self.options.filepath, "wb")

                ms3d_model.write(self.file)
                self.file.flush()
            finally:
                if self.file is not None:
                    self.file.close()

            # if option is set, this time will enlargs the io time
            if (self.options.prop_verbose):
                ms3d_model.print_internal()

            post_setup_environment(self, blender_context)
            # restore active object
            context.scene.objects.active = self.active_object

            if ((not context.scene.objects.active)
                    and (context.selected_objects)):
                context.scene.objects.active \
                        = context.selected_objects[0]

            # restore pre operator undo state
            context.user_preferences.edit.use_global_undo = self.undo

            is_valid, statistics = ms3d_model.is_valid()
            print()
            print("##########################################################")
            print("Blender -> MS3D : [{0}]".format(self.filepath_splitted[1]))
            print(statistics)
            print("##########################################################")

        except Exception:
            type, value, traceback = exc_info()
            print("write - exception in try block\n  type: '{0}'\n"
                    "  value: '{1}'".format(type, value, traceback))

            if t2 is None:
                t2 = time()

            raise

        else:
            pass

        t3 = time()
        print(ms3d_str['SUMMARY_EXPORT'].format(
                (t3 - t1), (t2 - t1), (t3 - t2)))

        return {"FINISHED"}


    ###########################################################################
    def from_blender(self, blender_context, ms3d_model):
        blender_mesh_objects = []

        ##EXPORT_ACTIVE_ONLY:
        ##if self.options.prop_selected:
        ##    source = blender_context.selected_objects
        ##else:
        ##    source = blender_context.blend_data.objects
        ##
        ## temporary, handle only the active object, for easy handling
        source = (blender_context.active_object, )
        ##

        for blender_object in source:
            if blender_object and blender_object.type == 'MESH' \
                    and blender_object.is_visible(blender_context.scene):
                blender_mesh_objects.append(blender_object)

        blender_to_ms3d_bones = {}

        self.create_animation(blender_context, ms3d_model, blender_mesh_objects, blender_to_ms3d_bones)
        self.create_geometry(blender_context, ms3d_model, blender_mesh_objects, blender_to_ms3d_bones)


    ###########################################################################
    def create_geometry(self, blender_context, ms3d_model, blender_mesh_objects, blender_to_ms3d_bones):
        blender_scene = blender_context.scene

        blender_to_ms3d_vertices = {}
        blender_to_ms3d_triangles = {}
        blender_to_ms3d_groups = {}
        blender_to_ms3d_materials = {}

        for blender_mesh_object in blender_mesh_objects:
            blender_mesh = blender_mesh_object.data

            ##########################
            # prepare ms3d groups if available
            # works only for exporting active object
            ##EXPORT_ACTIVE_ONLY:
            for ms3d_local_group_index, blender_ms3d_group in enumerate(blender_mesh.ms3d.groups):
                ms3d_group = Ms3dGroup()
                ms3d_group.__index = len(ms3d_model._groups)
                ms3d_group.name = blender_ms3d_group.name
                ms3d_group.flags = Ms3dUi.flags_to_ms3d(blender_ms3d_group.flags)
                if blender_ms3d_group.comment:
                    ms3d_group._comment_object = Ms3dCommentEx()
                    ms3d_group._comment_object.comment = blender_ms3d_group.comment
                    ms3d_group._comment_object.index = len(ms3d_model._groups)
                ms3d_group.material_index = None # to mark as not setted
                ms3d_model._groups.append(ms3d_group)
                blender_to_ms3d_groups[blender_ms3d_group.id] = ms3d_group

            ##########################
            # i have to use BMesh, because there are several custom data stored.
            # BMesh doesn't support quads_convert_to_tris()
            # so, i use that very ugly way:
            # create a complete copy of mesh and bend object data
            # to be able to apply operations to it.

            # get a temporary mesh with applied modifiers
            if self.options.prop_apply_modifier:
                blender_mesh_temp = blender_mesh_object.to_mesh(blender_scene,
                        self.options.prop_apply_modifier,
                        self.options.prop_apply_modifier_mode)
            else:
                blender_mesh_temp = blender_mesh_object.data.copy()

            # assign temporary mesh as new object data
            blender_mesh_object.data = blender_mesh_temp

            # convert to tris
            enable_edit_mode(True)
            select_all(True)
            if ops.mesh.quads_convert_to_tris.poll():
                ops.mesh.quads_convert_to_tris()
            enable_edit_mode(False)

            enable_edit_mode(True)
            bm = bmesh.from_edit_mesh(blender_mesh_temp)

            layer_texture = bm.faces.layers.tex.get(
                    ms3d_str['OBJECT_LAYER_TEXTURE'])
            if layer_texture is None:
                layer_texture = bm.faces.layers.tex.new(
                        ms3d_str['OBJECT_LAYER_TEXTURE'])

            layer_smoothing_group = bm.faces.layers.int.get(
                    ms3d_str['OBJECT_LAYER_SMOOTHING_GROUP'])
            if layer_smoothing_group is None:
                layer_smoothing_group = bm.faces.layers.int.new(
                        ms3d_str['OBJECT_LAYER_SMOOTHING_GROUP'])

            layer_group = bm.faces.layers.int.get(
                    ms3d_str['OBJECT_LAYER_GROUP'])
            if layer_group is None:
                layer_group = bm.faces.layers.int.new(
                        ms3d_str['OBJECT_LAYER_GROUP'])

            layer_uv = bm.loops.layers.uv.get(ms3d_str['OBJECT_LAYER_UV'])
            if layer_uv is None:
                if bm.loops.layers.uv:
                    layer_uv = bm.loops.layers.uv[0]
                else:
                    layer_uv = bm.loops.layers.uv.new(ms3d_str['OBJECT_LAYER_UV'])

            layer_deform = bm.verts.layers.deform.active

            ##########################
            # handle vertices
            for bmv in bm.verts:
                item = blender_to_ms3d_vertices.get(bmv)
                if item is None:
                    index = len(ms3d_model._vertices)
                    ms3d_vertex = Ms3dVertex()
                    ms3d_vertex.__index = index
                    ms3d_vertex._vertex = (self.matrix_scaled_coordination_system \
                            * (bmv.co + blender_mesh_object.location))[:]

                    if layer_deform:
                        blender_vertex_group_ids = bmv[layer_deform]
                        if blender_vertex_group_ids:
                            temp_weight = 0
                            count = 0
                            for blender_index, blender_weight in blender_vertex_group_ids.items():
                                ms3d_joint = blender_to_ms3d_bones.get(
                                        blender_mesh_object.vertex_groups[blender_index].name)
                                if ms3d_joint:
                                    if count == 0:
                                        ms3d_vertex.bone_id = ms3d_joint.__index
                                        temp_weight = blender_weight
                                    elif count == 1:
                                        ms3d_vertex._vertex_ex_object.bone_ids[0] = ms3d_joint.__index
                                        ms3d_vertex._vertex_ex_object.weights[0] = temp_weight * 100
                                        ms3d_vertex._vertex_ex_object.weights[1] = blender_weight * 100
                                    elif count == 2:
                                        ms3d_vertex._vertex_ex_object.bone_ids[1] = ms3d_joint.__index
                                        ms3d_vertex._vertex_ex_object.weights[2] = blender_weight * 100
                                    #elif count == 3:
                                    #    ms3d_vertex._vertex_ex_object.bone_ids[2] = ms3d_joint.__index

                                # only first three weights will be supported
                                count+= 1
                                if count > 3:
                                    break

                    ms3d_model._vertices.append(ms3d_vertex)
                    blender_to_ms3d_vertices[bmv] = ms3d_vertex

            ##########################
            # handle faces / tris
            for bmf in bm.faces:
                item = blender_to_ms3d_triangles.get(bmf)
                if item is None:
                    index = len(ms3d_model._triangles)
                    ms3d_triangle = Ms3dTriangle()
                    ms3d_triangle.__index = index
                    bmv0 = bmf.verts[0]
                    bmv1 = bmf.verts[1]
                    bmv2 = bmf.verts[2]
                    ms3d_vertex0 = blender_to_ms3d_vertices[bmv0]
                    ms3d_vertex1 = blender_to_ms3d_vertices[bmv1]
                    ms3d_vertex2 = blender_to_ms3d_vertices[bmv2]
                    ms3d_vertex0.reference_count += 1
                    ms3d_vertex1.reference_count += 1
                    ms3d_vertex2.reference_count += 1
                    ms3d_triangle._vertex_indices = (
                            ms3d_vertex0.__index,
                            ms3d_vertex1.__index,
                            ms3d_vertex2.__index,
                            )
                    ms3d_triangle._vertex_normals = (
                            (self.matrix_coordination_system * bmv0.normal)[:],
                            (self.matrix_coordination_system * bmv1.normal)[:],
                            (self.matrix_coordination_system * bmv2.normal)[:],
                            )
                    ms3d_triangle._s = (
                            bmf.loops[0][layer_uv].uv.x,
                            bmf.loops[1][layer_uv].uv.x,
                            bmf.loops[2][layer_uv].uv.x,
                            )
                    ms3d_triangle._t = (
                            1.0 - bmf.loops[0][layer_uv].uv.y,
                            1.0 - bmf.loops[1][layer_uv].uv.y,
                            1.0 - bmf.loops[2][layer_uv].uv.y,
                            )

                    ms3d_triangle.smoothing_group = bmf[layer_smoothing_group]
                    ms3d_model._triangles.append(ms3d_triangle)

                    ms3d_material = self.get_ms3d_material_add_if(blender_mesh, ms3d_model,
                            blender_to_ms3d_materials, bmf.material_index)
                    ms3d_group = blender_to_ms3d_groups.get(bmf[layer_group])

                    ##EXPORT_ACTIVE_ONLY:
                    if ms3d_group is not None:
                        if ms3d_material is None:
                            ms3d_group.material_index = Ms3dSpec.DEFAULT_GROUP_MATERIAL_INDEX
                        else:
                            if ms3d_group.material_index is None:
                                ms3d_group.material_index = ms3d_material.__index
                            else:
                                if ms3d_group.material_index != ms3d_material.__index:
                                    ms3d_group = self.get_ms3d_group_by_material_add_if(ms3d_model, ms3d_material)
                    else:
                        if ms3d_material is not None:
                            ms3d_group = self.get_ms3d_group_by_material_add_if(ms3d_model, ms3d_material)
                        else:
                            ms3d_group = self.get_ms3d_group_default_material_add_if(ms3d_model)

                    if ms3d_group is not None:
                        ms3d_group._triangle_indices.append(ms3d_triangle.__index)
                        ms3d_triangle.group_index = ms3d_group.__index

                    blender_to_ms3d_triangles[bmf] = ms3d_triangle

            if bm is not None:
                bm.free()

            enable_edit_mode(False)

            ##########################
            # restore original object data
            blender_mesh_object.data = blender_mesh

            ##########################
            # remove the temporary data
            if blender_mesh_temp is not None:
                blender_mesh_temp.user_clear()
                blender_context.blend_data.meshes.remove(blender_mesh_temp)

            # DEBUG:
            #print("DEBUG: blender_mesh_object: {}".format(blender_mesh_object))


    ###########################################################################
    def create_animation(self, blender_context, ms3d_model, blender_mesh_objects, blender_to_ms3d_bones):
        ##########################
        # setup scene
        blender_scene = blender_context.scene
        ms3d_model.animation_fps = blender_scene.render.fps * blender_scene.render.fps_base
        ms3d_model.number_total_frames = (blender_scene.frame_end - blender_scene.frame_start) + 1
        ms3d_model.current_time = (blender_scene.frame_current - blender_scene.frame_start)\
                / (blender_scene.render.fps * blender_scene.render.fps_base)

        #return
        ### not ready yet
        for blender_mesh_object in blender_mesh_objects:
            blender_bones = None
            for blender_modifier in blender_mesh_object.modifiers:
                if blender_modifier.type == 'ARMATURE' and blender_modifier.object.pose:
                    blender_bones = blender_modifier.object.pose.bones
                    break

            for blender_bone_oject in blender_bones:
                ms3d_joint = Ms3dJoint()
                ms3d_joint.__index = len(ms3d_model._joints)

                blender_ms3d_joint = blender_bone_oject.bone.ms3d
                blender_bone = blender_bone_oject

                if blender_ms3d_joint.name:
                    ms3d_joint.name = blender_ms3d_joint.name
                else:
                    ms3d_joint.name = blender_bone.name

                if blender_bone.parent:
                    if blender_ms3d_joint.name:
                        ms3d_joint.parent_name = blender_bone.parent.bone.ms3d.name
                    else:
                        ms3d_joint.parent_name = blender_bone.parent.name

                    ms3d_joint_vector = (blender_bone.head - blender_bone.parent.head) * self.matrix_scaled_coordination_system
                    ms3d_joint_euler = blender_bone.matrix.to_euler('XZY')
                else:
                    ms3d_joint_vector = blender_bone.head * self.matrix_scaled_coordination_system
                    ms3d_joint_euler = blender_bone.matrix.to_euler('XZY')
                ms3d_joint._position = ms3d_joint_vector
                #ms3d_joint._rotation = ms3d_joint_euler

                ms3d_joint.flags = Ms3dUi.flags_to_ms3d(blender_ms3d_joint.flags)
                if blender_ms3d_joint.comment:
                    ms3d_joint._comment_object = Ms3dCommentEx()
                    ms3d_joint._comment_object.comment = blender_ms3d_joint.comment
                    ms3d_joint._comment_object.index = ms3d_joint.__index


                ms3d_model._joints.append(ms3d_joint)
                blender_to_ms3d_bones[blender_bone.name] = ms3d_joint


    ###########################################################################
    def get_ms3d_group_default_material_add_if(self, ms3d_model):
        markerName = "MaterialGroupDefault"
        markerComment = "group without material"

        for ms3d_group in ms3d_model._groups:
            if ms3d_group.material_index == Ms3dSpec.DEFAULT_GROUP_MATERIAL_INDEX \
                    and ms3d_group.name == markerName \
                    and ms3d_group._comment_object \
                    and ms3d_group._comment_object.comment == markerComment:
                return ms3d_group

        ms3d_group = Ms3dGroup()
        ms3d_group.__index = len(ms3d_model._groups)
        ms3d_group.name = markerName
        ms3d_group._comment_object = Ms3dCommentEx()
        ms3d_group._comment_object.comment = markerComment
        ms3d_group._comment_object.index = len(ms3d_model._groups)
        ms3d_group.material_index = Ms3dSpec.DEFAULT_GROUP_MATERIAL_INDEX

        ms3d_model._groups.append(ms3d_group)

        return ms3d_group


    ###########################################################################
    def get_ms3d_group_by_material_add_if(self, ms3d_model, ms3d_material):
        if ms3d_material.__index < 0 or ms3d_material.__index >= len(ms3d_model.materials):
            return None

        markerName = "MaterialGroup." + ms3d_material.__index
        markerComment = "material group conflict dissolver (" + ms3d_material.name + ")"

        for ms3d_group in ms3d_model._groups:
            if ms3d_group.name == markerName and ms3d_group._comment_object and ms3d_group._comment_object.comment == markerComment:
                return ms3d_group

        ms3d_group = Ms3dGroup()
        ms3d_group.__index = len(ms3d_model._groups)
        ms3d_group.name = markerName
        ms3d_group._comment_object = Ms3dCommentEx()
        ms3d_group._comment_object.comment = markerComment
        ms3d_group._comment_object.index = len(ms3d_model._groups)
        ms3d_group.material_index = ms3d_material_index

        ms3d_model._groups.append(ms3d_group)

        return ms3d_group


    ###########################################################################
    def get_ms3d_material_add_if(self, blender_mesh, ms3d_model, blender_to_ms3d_materials, blender_index):
        if blender_index < 0 or blender_index >= len(blender_mesh.materials):
            return None

        blender_material = blender_mesh.materials[blender_index]
        ms3d_material = blender_to_ms3d_materials.get(blender_material)
        if ms3d_material is None:
            ms3d_material = Ms3dMaterial()
            ms3d_material.__index = len(ms3d_model.materials)

            blender_ms3d_material = blender_material.ms3d

            if blender_ms3d_material.name:
                ms3d_material.name = blender_ms3d_material.name
            else:
                ms3d_material.name = blender_material.name

            ms3d_material._ambient = blender_ms3d_material.ambient
            ms3d_material._diffuse = blender_ms3d_material.diffuse
            ms3d_material._specular = blender_ms3d_material.specular
            ms3d_material._emissive = blender_ms3d_material.emissive
            ms3d_material.shininess = blender_ms3d_material.shininess
            ms3d_material.transparency = blender_ms3d_material.transparency
            ms3d_material.mode = Ms3dUi.texture_mode_to_ms3d(blender_ms3d_material.mode)
            ms3d_material.texture = blender_ms3d_material.texture
            ms3d_material.alphamap = blender_ms3d_material.alphamap
            if blender_ms3d_material.comment:
                ms3d_material._comment_object = Ms3dCommentEx()
                ms3d_material._comment_object.comment = blender_ms3d_material.comment
                ms3d_material._comment_object.index = ms3d_material.__index

            ms3d_model.materials.append(ms3d_material)

            blender_to_ms3d_materials[blender_material] = ms3d_material

        return ms3d_material


###############################################################################
#234567890123456789012345678901234567890123456789012345678901234567890123456789
#--------1---------2---------3---------4---------5---------6---------7---------
# ##### END OF FILE #####
