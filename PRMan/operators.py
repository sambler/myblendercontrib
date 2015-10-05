# ##### BEGIN MIT LICENSE BLOCK #####
#
# Copyright (c) 2015 Brian Savery
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#
# ##### END MIT LICENSE BLOCK #####

import bpy
import os
import subprocess
import bgl
import blf

from bpy.props import PointerProperty, StringProperty, BoolProperty, \
    EnumProperty, IntProperty, FloatProperty, FloatVectorProperty, \
    CollectionProperty

from .util import init_env
from .util import getattr_recursive
from .util import user_path
from .util import get_real_path
from .util import readOSO

from .shader_parameters import tex_source_path
from .shader_parameters import tex_optimised_path

from .export import export_archive
from .engine import RPass
from .export import debug
from . import engine

from bpy_extras.io_utils import ExportHelper

class Renderman_open_stats(bpy.types.Operator):
    bl_idname = 'rman.open_stats'
    bl_label = "Open Last Stats"
    bl_description = "Open Last stats file"

    def execute(self, context):
        scene = context.scene
        rm = scene.renderman
        output_dir = os.path.dirname(user_path(rm.path_rib_output, scene=scene))
        bpy.ops.wm.url_open(url="file://" + os.path.join(output_dir, 'stats.xml'))
        return {'FINISHED'}

class SHADING_OT_add_renderman_nodetree(bpy.types.Operator):

    ''''''
    bl_idname = "shading.add_renderman_nodetree"
    bl_label = "Add Renderman Nodetree"
    bl_description = "Add a renderman shader node tree linked to this material"

    idtype = StringProperty(name="ID Type", default="material")

    def execute(self, context):
        idtype = self.properties.idtype
        context_data = {'material': context.material, 'lamp': context.lamp}
        idblock = context_data[idtype]

        nt = bpy.data.node_groups.new(idblock.name,
                                      type='RendermanPatternGraph')
        nt.use_fake_user = True
        idblock.renderman.nodetree = nt.name

        if idtype == 'material':
            output = nt.nodes.new('RendermanOutputNode')
            default = nt.nodes.new('PxrDisneyBxdfNode')
            default.location = output.location
            default.location[0] -= 300
            nt.links.new(default.outputs[0], output.inputs[0])
        else:

            light_type = idblock.type
            light_shader = 'PxrStdAreaLightLightNode'
            if light_type == 'SUN':
                light_shader = 'PxrStdEnvDayLightLightNode'
            elif light_type == 'HEMI':
                light_shader = 'PxrStdEnvMapLightLightNode'
            elif light_type == 'AREA' or light_type == 'POINT':
                idblock.type = "AREA"
                context.lamp.size = 1.0
                context.lamp.size_y = 1.0
                
            else:
                idblock.type = "AREA"

            output = nt.nodes.new('RendermanOutputNode')
            default = nt.nodes.new(light_shader)
            default.location = output.location
            default.location[0] -= 300
            nt.links.new(default.outputs[0], output.inputs[1])

        return {'FINISHED'}


class refresh_osl_shader(bpy.types.Operator):
    bl_idname = "node.refresh_osl_shader"
    bl_label = "Refresh OSL Node"
    bl_description = "Refreshes the OSL node This takes a few seconds!!!"

    def invoke(self, context, event):
        context.node.RefreshNodes(context)
        return {'FINISHED'}


class StartInteractive(bpy.types.Operator):

    ''''''
    bl_idname = "lighting.start_interactive"
    bl_label = "Start/Stop Interactive Rendering"
    bl_description = "Start/Stop Interactive Rendering, \
        must have 'it' installed"
    rpass = None
    is_running = False

    def draw(self, context):
        w = context.region.width
        h = context.region.height

        # Draw text area that PRMan is running.
        pos_x = w / 2 - 100
        pos_y = 20
        blf.enable(0, blf.SHADOW)
        blf.shadow_offset(0, 1, -1)
        blf.shadow(0, 5, 0.0, 0.0, 0.0, 0.8)
        blf.size(0, 32, 36)
        blf.position(0, pos_x, pos_y, 0)
        bgl.glColor4f(1.0, 0.0, 0.0, 1.0)
        blf.draw(0, "%s" % ('PRMan Interactive Mode Running'))
        blf.disable(0, blf.SHADOW)

    def invoke(self, context, event=None):
        if engine.ipr is None:
            engine.ipr = RPass(context.scene, interactive=True)
            engine.ipr.start_interactive()
            engine.ipr_handle = bpy.types.SpaceView3D.draw_handler_add(
                self.draw, (context,), 'WINDOW', 'POST_PIXEL')
            bpy.app.handlers.scene_update_post.append(
                engine.ipr.issue_transform_edits)
            bpy.app.handlers.load_pre.append(self.invoke)
        else:
            bpy.types.SpaceView3D.draw_handler_remove(
                engine.ipr_handle, 'WINDOW')
            bpy.app.handlers.scene_update_post.remove(
                engine.ipr.issue_transform_edits)
            engine.ipr.end_interactive()
            engine.ipr = None
            if context:
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
        return {'FINISHED'}


class ExportRIBArchive(bpy.types.Operator, ExportHelper):

    ''''''
    bl_idname = "export_shape.rib"
    bl_label = "Export RIB Archive (.rib)"
    bl_description = "Export an object to an archived geometry file on disk"

    filename_ext = ".rib"
    filter_glob = StringProperty(default="*.rib", options={'HIDDEN'})

    archive_motion = BoolProperty(name='Export Motion Data',
                                  description='Exports a MotionBegin/End block for any sub-frame (motion blur) animation data',
                                  default=True)

    animated = BoolProperty(name='Animated Frame Sequence',
                            description='Exports a sequence of rib files for a frame range',
                            default=False)
    frame_start = IntProperty(
        name="Start Frame",
        description="The first frame of the sequence to export",
        default=1)
    frame_end = IntProperty(
        name="End Frame",
        description="The final frame of the sequence to export",
        default=1)

    @classmethod
    def poll(self, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        export_archive(context.scene, context.selected_objects,
                       **self.as_keywords(ignore=("check_existing",
                                                  "filter_glob")))

        return {'FINISHED'}




'''
class TEXT_OT_add_inline_rib(bpy.types.Operator):
    """
    This operator is only intended for when there are no
    blender text datablocks in the file. Just for convenience
    """
    bl_label = "Add New"
    bl_idname = "text.add_inline_rib"

    context = StringProperty(
                name="Context",
                description="Name of context member to find renderman pointer in",
                default="")
    collection = StringProperty(
                name="Collection",
                description="The collection to manipulate",
                default="")

    def execute(self, context):
        if len(bpy.data.texts) > 0:
            return {'CANCELLED'}
        bpy.data.texts.new(name="Inline RIB")

        id = getattr_recursive(context, self.properties.context)
        rm = id.renderman
        collection = getattr(rm, prop_coll)
'''


# Yuck, this should be built in to blender...
class COLLECTION_OT_add_remove(bpy.types.Operator):
    bl_label = "Add or Remove Paths"
    bl_idname = "collection.add_remove"

    action = EnumProperty(
        name="Action",
        description="Either add or remove properties",
        items=[('ADD', 'Add', ''),
               ('REMOVE', 'Remove', '')],
        default='ADD')
    context = StringProperty(
        name="Context",
        description="Name of context member to find renderman pointer in",
        default="")
    collection = StringProperty(
        name="Collection",
        description="The collection to manipulate",
        default="")
    collection_index = StringProperty(
        name="Index Property",
        description="The property used as a collection index",
        default="")
    defaultname = StringProperty(
        name="Default Name",
        description="Default name to give this collection item",
        default="")
    # BBM addition begin
    is_shader_param = BoolProperty(name='Is shader parameter', default=False)
    shader_type = StringProperty(
        name="shader type",
        default='surface')
    # BBM addition end

    def invoke(self, context, event):
        scene = context.scene
        # BBM modification
        if not self.properties.is_shader_param:
            id = getattr_recursive(context, self.properties.context)
            rm = id.renderman if hasattr(id, 'renderman') else id
        else:
            if context.active_object.name in bpy.data.lamps.keys():
                rm = bpy.data.lamps[context.active_object.name].renderman
            else:
                rm = context.active_object.active_material.renderman
            id = getattr(rm, '%s_shaders' % self.properties.shader_type)
            rm = getattr(id, self.properties.context)

        prop_coll = self.properties.collection
        coll_idx = self.properties.collection_index

        collection = getattr(rm, prop_coll)
        index = getattr(rm, coll_idx)

        # otherwise just add an empty one
        if self.properties.action == 'ADD':
            collection.add()

            index += 1
            setattr(rm, coll_idx, index)
            collection[-1].name = self.properties.defaultname
            # BBM addition begin
            # if coshader array, add the selected coshader
            if self.is_shader_param:
                coshader_name = getattr(rm, 'bl_hidden_%s_menu' % prop_coll)
                collection[-1].name = coshader_name
            # BBM addition end
        elif self.properties.action == 'REMOVE':
            collection.remove(index)
            setattr(rm, coll_idx, index - 1)

        return {'FINISHED'}

class OT_add_aov_list(bpy.types.Operator):
    bl_idname = 'renderman.add_aov_list'
    bl_label = 'Add aov list'
    
    def execute(self, context):
        scene = context.scene
        scene.renderman.aov_lists.add()
        active_layer = scene.render.layers.active
        # this sucks.  but can't find any other way to refer to render layer
        scene.renderman.aov_lists[-1].render_layer = active_layer.name
        return {'FINISHED'}


# Menus
export_archive_menu_func = (lambda self, context: self.layout.operator(
    ExportRIBArchive.bl_idname, text="RIB Archive (.rib)"))
compile_shader_menu_func = (lambda self, context: self.layout.operator(
    TEXT_OT_compile_shader.bl_idname))


def register():
    bpy.types.INFO_MT_file_export.append(export_archive_menu_func)
    bpy.types.TEXT_MT_text.append(compile_shader_menu_func)
    bpy.types.TEXT_MT_toolbox.append(compile_shader_menu_func)


def unregister():
    bpy.types.INFO_MT_file_export.remove(export_archive_menu_func)
    bpy.types.TEXT_MT_text.remove(compile_shader_menu_func)
    bpy.types.TEXT_MT_toolbox.remove(compile_shader_menu_func)
