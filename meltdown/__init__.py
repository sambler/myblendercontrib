#  (c) 2014 by Piotr Adamowicz (MadMinstrel)

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

bl_info = {
    "name": "Meltdown",
    "author": "Piotr Adamowicz",
    "version": (0, 2),
    "blender": (2, 7, 1),
    "location": "Properties Editor -> Render Panel",
    "description": "Improved baking UI",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/MadMinstrel/meltdown/issues",
    "category": "Baking"}

import code
import os
import bpy
from bpy.props import *
from bpy.utils import register_class, unregister_class

class BakePair(bpy.types.PropertyGroup):
    activated = bpy.props.BoolProperty(name = "Activated", description="Pair on/off", default = True)
    lowpoly = bpy.props.StringProperty(name="", description="Lowpoly mesh", default="")
    cage = bpy.props.StringProperty(name="", description="Cage mesh", default="")
    highpoly = bpy.props.StringProperty(name="", description="Highpoly mesh", default="")
    hp_obj_vs_group = EnumProperty(name="Object vs Group", description="", default="OBJ", items = [('OBJ', '', 'Object', 'MESH_CUBE', 0), ('GRP', '', 'Group', 'GROUP', 1)])
    extrusion_vs_cage = EnumProperty(name="Extrusion vs Cage", description="", default="EXT", items = [('EXT', '', 'Extrusion', 'OUTLINER_DATA_META', 0), ('CAGE', '', 'Cage', 'OUTLINER_OB_LATTICE', 1)])
    extrusion = bpy.props.FloatProperty(name="Extrusion", description="", default=0.5, min=0.0)
    use_hipoly = bpy.props.BoolProperty(name="Use Hipoly", default = True)
    no_materials = bpy.props.BoolProperty(name="No Materials", default = False)
register_class(BakePair)

class BakePass(bpy.types.PropertyGroup):
    activated = bpy.props.BoolProperty(name = "Activated", default = True)
    pair_counter = bpy.props.IntProperty(name="Pair Counter", description="", default=0)
    pass_name = bpy.props.EnumProperty(name = "Pass", default = "NORMAL",
                                    items = (("COMBINED","Combined",""),
                                            #("Z","Depth",""),
                                            #("COLOR","Color",""),
                                            #("DIFFUSE","Diffuse",""),
                                            #("SPECULAR","Specular",""),
                                            ("SHADOW","Shadow",""),
                                            ("AO","Ambient Occlusion",""),
                                            #("REFLECTION","Reflection",""),
                                            ("NORMAL","Normal",""),
                                            #("VECTOR","Vector",""),
                                            #("REFRACTION","Refraction",""),
                                            #("OBJECT_INDEX","Object Index",""),
                                            ("UV","UV",""),
                                            #("MIST","Mist",""),
                                            ("EMIT","Emission",""),
                                            ("ENVIRONMENT","Environment",""),
                                            #("MATERIAL_INDEX","Material Index",""),
                                            ("DIFFUSE_DIRECT","DIffuse Direct",""),
                                            ("DIFFUSE_INDIRECT","Diffuse Indirect",""),
                                            ("DIFFUSE_COLOR","Diffuse Color",""),
                                            ("GLOSSY_DIRECT","Glossy Direct",""),
                                            ("GLOSSY_INDIRECT","Glossy Indirect",""),
                                            ("GLOSSY_COLOR","Glossy Color",""),
                                            ("TRANSMISSION_DIRECT","Transmission Direct",""),
                                            ("TRANSMISSION_INDIRECT","Transmission Indirect",""),
                                            ("TRANSMISSION_COLOR","Transmission Color",""),
                                            ("SUBSURFACE_DIRECT","Subsurface Direct",""),
                                            ("SUBSURFACE_INDIRECT","Subsurface Indirect",""),
                                            ("SUBSURFACE_COLOR","Subsurface Color","")))
    
    material_override = bpy.props.StringProperty(name="Material Override", description="", default="")
    ao_distance = bpy.props.FloatProperty(name="Distance", description="", default=10.0, min=0.0)
    samples = bpy.props.IntProperty(name="Samples", description="", default=1)
    suffix = bpy.props.StringProperty(name="Suffix", description="", default="")

    nm_space = bpy.props.EnumProperty(name = "Normal map space", default = "TANGENT",
                                    items = (("TANGENT","Tangent",""),
                                            ("OBJECT", "Object", "")))

    normal_r = EnumProperty(name="R", description="", default="POS_X", 
                                    items = (("POS_X", "X+", ""), 
                                            ("NEG_X", "X-", ""),
                                            ("POS_Y", "Y+", ""),
                                            ("NEG_Y", "Y-", ""),
                                            ("POS_Z", "Z+", ""),
                                            ("NEG_Z", "Z-", "")))
    normal_g = EnumProperty(name="G", description="", default="POS_Y", 
                                    items = (("POS_X", "X+", ""), 
                                            ("NEG_X", "X-", ""),
                                            ("POS_Y", "Y+", ""),
                                            ("NEG_Y", "Y-", ""),
                                            ("POS_Z", "Z+", ""),
                                            ("NEG_Z", "Z-", "")))
    normal_b = EnumProperty(name="B", description="", default="POS_Z", 
                                    items = (("POS_X", "X+", ""), 
                                            ("NEG_X", "X-", ""),
                                            ("POS_Y", "Y+", ""),
                                            ("NEG_Y", "Y-", ""),
                                            ("POS_Z", "Z+", ""),
                                            ("NEG_Z", "Z-", "")))
    def props(self):
        props = set()
        if self.pass_name == "COMBINED":
            props = {"samples"}
        if self.pass_name == "SHADOW":
            props = {"samples"}
        if self.pass_name == "AO":
            props = {"ao_distance", "samples"}
        if self.pass_name == "NORMAL":
            props = {"nm_space", "swizzle"}
        if self.pass_name == "DIFFUSE_DIRECT":
            props = {"samples"}
        if self.pass_name == "DIFFUSE_INDIRECT":
            props = {"samples"}
        if self.pass_name == "GLOSSY_DIRECT":
            props = {"samples"}
        if self.pass_name == "GLOSSY_INDIRECT":
            props = {"samples"}
        if self.pass_name == "TRANSMISSION_DIRECT":
            props = {"samples"}
        if self.pass_name == "TRANSMISSION_INDIRECT":
            props = {"samples"}
        if self.pass_name == "SUBSURFACE_DIRECT":
            props = {"samples"}
        if self.pass_name == "SUBSURFACE_INDIRECT":
            props = {"samples"}            
        return props
        
    def get_filepath(self, bj):
        path = bj.output 
        if path[-1:] != "/":
            path = path + "/"
        path = path + bj.name 
        if len(self.suffix)>0:
            path += "_" + self.suffix
        path += ".png"
        return path

    def get_filename(self, bj):
        name = bj.name 
        if len(self.suffix)>0:
            name += "_" + self.suffix
        name += ".png"
        return name        
    
register_class(BakePass)
                                            
    
class BakeJob(bpy.types.PropertyGroup):
    activated = bpy.props.BoolProperty(name = "Activated", default = True)
    expand = bpy.props.BoolProperty(name = "Expand", default = True)
    resolution_x = bpy.props.IntProperty(name="Resolution X", default = 1024)
    resolution_y = bpy.props.IntProperty(name="Resolution Y", default = 1024)
    
    margin = bpy.props.IntProperty(name="Margin", default = 16, min = 0)
    
    output = bpy.props.StringProperty(name = 'File path',
                            description = 'The path of the output image.',
                            default = '//textures/',
                            subtype = 'FILE_PATH')
    name = bpy.props.StringProperty(name = 'name',
                            description = '',
                            default = 'bake')
    
    bake_queue = bpy.props.CollectionProperty(type=BakePair)
    bake_pass_queue = bpy.props.CollectionProperty(type=BakePass)
    
register_class(BakeJob)

class MeltdownSettings(bpy.types.PropertyGroup):
    bl_idname = __name__
    bake_job_queue = bpy.props.CollectionProperty(type=BakeJob)
    
register_class(MeltdownSettings)
bpy.types.Scene.meltdown_settings = PointerProperty(type = MeltdownSettings)

class MeltdownBakeOp(bpy.types.Operator):
    '''Meltdown'''

    bl_idname = "meltdown.bake"
    bl_label = "Meltdown"
    
    job = bpy.props.IntProperty()
    bakepass = bpy.props.IntProperty()
    pair = bpy.props.IntProperty()
    bake_all = bpy.props.BoolProperty()
    bake_target = bpy.props.StringProperty()
    
    def create_temp_node(self):
        #add an image node to the lowpoly model's material
        bake_mat = bpy.context.active_object.active_material
        
        if "MDtarget" not in bake_mat.node_tree.nodes:
            imgnode = bake_mat.node_tree.nodes.new(type = "ShaderNodeTexImage")
            imgnode.image = bpy.data.images[self.bake_target]
            imgnode.name = 'MDtarget'
            imgnode.label = 'MDtarget'
        else:
            imgnode = bake_mat.node_tree.nodes['MDtarget']
            imgnode.image = bpy.data.images[self.bake_target]
        
        bake_mat.node_tree.nodes.active = imgnode
    
    def cleanup_temp_node(self):
        bake_mat = bpy.context.active_object.active_material
        if "MDtarget" in bake_mat.node_tree.nodes:
            imgnode = bake_mat.node_tree.nodes['MDtarget']
            bake_mat.node_tree.nodes.remove(imgnode)
            
    def prepare_scene(self):
        mds = bpy.context.scene.meltdown_settings
        pair = mds.bake_job_queue[self.job].bake_queue[self.pair]
        
        # make selections
        bpy.ops.object.select_all(action='DESELECT')
        if pair.highpoly != "":
            if pair.hp_obj_vs_group == "GRP":
                for object in bpy.data.groups[pair.highpoly].objects:
                    object.select = True
            else:
                bpy.data.scenes[0].objects[pair.highpoly].select = True
        else:
            pair.use_hipoly = False
        
        bpy.data.scenes[0].objects[pair.lowpoly].select = True
        bpy.context.scene.objects.active = bpy.data.scenes[0].objects[pair.lowpoly]
        
    def create_render_target(self):
        mds = bpy.context.scene.meltdown_settings
        bakepass = mds.bake_job_queue[self.job].bake_pass_queue[self.bakepass]
        job = mds.bake_job_queue[self.job]
        
        if "MDtarget" not in bpy.data.images:
            bpy.ops.image.new(name="MDtarget", width= job.resolution_x, height = job.resolution_y, \
                                color=(0.0, 0.0, 0.0, 0.0), alpha=True, generated_type='BLANK', float=False)
        baketarget = bpy.data.images["MDtarget"]
        self.bake_target = "MDtarget"
        
        #assign file path to render target
        baketarget.filepath = bakepass.get_filepath(job)
        
    def cleanup_render_target(self):
        baketarget = bpy.data.images[self.bake_target]
        
        #save image
        baketarget.save()
        
        #unlink from image editors
        for wm in bpy.data.window_managers:
            for window in wm.windows:
                for area in window.screen.areas:
                    if area.type == "IMAGE_EDITOR":
                        area.spaces[0].image = None
        #remove image
        baketarget.user_clear()
        bpy.data.images.remove(baketarget)
    
    def bake_set(self):
        mds = bpy.context.scene.meltdown_settings
        pair = mds.bake_job_queue[self.job].bake_queue[self.pair]
        bakepass = mds.bake_job_queue[self.job].bake_pass_queue[self.bakepass]
        bj = mds.bake_job_queue[self.job]
        
        self.prepare_scene()
        
        no_materials = False
        #ensure lowpoly has material
        if len(bpy.data.scenes[0].objects[pair.lowpoly].data.materials) == 0 \
            or bpy.data.scenes[0].objects[pair.lowpoly].material_slots[0].material == None:
            no_materials = True
            temp_mat = bpy.data.materials.new("MeltdownTempMat")
            temp_mat.use_nodes = True
            bpy.data.scenes[0].objects[pair.lowpoly].data.materials.append(temp_mat)
            bpy.data.scenes[0].objects[pair.lowpoly].active_material = temp_mat
        
        self.create_temp_node()
        
        if pair.extrusion_vs_cage == "CAGE":
            pair_use_cage = True
        else:
            pair_use_cage = False
        
        clear = True
        if bakepass.pair_counter > 0:
            clear = False
        bakepass.pair_counter = bakepass.pair_counter + 1
        
        #bake
        bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type, filepath="", \
        width=bj.resolution_x, height=bj.resolution_y, margin=bj.margin, \
        use_selected_to_active=pair.use_hipoly, cage_extrusion=pair.extrusion, cage_object=pair.cage, \
        normal_space=bakepass.nm_space, \
        normal_r=bakepass.normal_r, normal_g=bakepass.normal_g, normal_b=bakepass.normal_b, \
        save_mode='INTERNAL', use_clear=clear, use_cage=pair_use_cage, \
        use_split_materials=False, use_automatic_name=False)
    
        # bake_mat.node_tree.nodes.remove(imgnode)
        self.cleanup_temp_node()
        
        if no_materials:
            bpy.data.scenes[0].objects[pair.lowpoly].data.materials.clear()
            bpy.ops.object.material_slot_remove()
            
    def bake_pass(self):
        mds = bpy.context.scene.meltdown_settings
        bakepass = mds.bake_job_queue[self.job].bake_pass_queue[self.bakepass]
        bj = mds.bake_job_queue[self.job]
        
        self.create_render_target()
        
        #copy pass settings to cycles settings
        bpy.data.scenes[0].cycles.bake_type = bakepass.pass_name
        bpy.data.scenes[0].cycles.samples = bakepass.samples
        bpy.data.worlds[0].light_settings.distance = bakepass.ao_distance
        
        #the pair counter is used to determine whether to clear the image
        #set it to 0 after each bake pass
        bakepass.pair_counter = 0
        
        for i_pair, pair in enumerate(bj.bake_queue):
            if pair.activated == True:
                self.pair = i_pair
                self.bake_set()
    
        self.cleanup_render_target()
            
    
    def execute(self, context):
        mds = context.scene.meltdown_settings

        for i_job, bj in enumerate(mds.bake_job_queue):
            if bj.activated == True:
                self.job = i_job
                
                #ensure save path exists
                if not os.path.exists(bpy.path.abspath(bj.output)):
                    os.makedirs(bpy.path.abspath(bj.output))
                
                for i_pass, bakepass in enumerate(bj.bake_pass_queue):
                    if bakepass.activated == True:
                        self.bakepass = i_pass
                        self.bake_pass()
        
        return {'FINISHED'}

class MeltdownPanel(bpy.types.Panel):
    bl_label = "Meltdown bake tools"
    bl_idname = "OBJECT_PT_meltdown"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        edit = context.user_preferences.edit
        wm = context.window_manager
        mds = context.scene.meltdown_settings
        
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("meltdown.bake", text='Meltdown', icon = "RADIO")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.separator()
        
        for job_i, bj in enumerate(mds.bake_job_queue):
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            
            if bj.expand == False: 
                row.prop(bj, "expand", icon="TRIA_RIGHT", icon_only=True, text=bj.name, emboss=False)
                
                if bj.activated:
                    row.prop(bj, "activated", icon_only=True, icon = "RESTRICT_RENDER_OFF", emboss = False)
                else:
                    row.prop(bj, "activated", icon_only=True, icon = "RESTRICT_RENDER_ON", emboss = False)
                    
                rem = row.operator("meltdown.rem_job", text = "", icon = "X")
                rem.job_index = job_i  
            else:
                row.prop(bj, "expand", icon="TRIA_DOWN", icon_only=True, text=bj.name, emboss=False)
                
                if bj.activated:
                    row.prop(bj, "activated", icon_only=True, icon = "RESTRICT_RENDER_OFF", emboss = False)
                else:
                    row.prop(bj, "activated", icon_only=True, icon = "RESTRICT_RENDER_ON", emboss = False)

                rem = row.operator("meltdown.rem_job", text = "", icon = "X")
                rem.job_index = job_i            
                
                row = layout.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(bj, 'resolution_x', text="X")
                row.prop(bj, 'resolution_y', text="Y")
                
                row = layout.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(bj, 'margin', text="Margin")
                
                row = layout.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(bj, 'output', text="Path")
                
                row = layout.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(bj, 'name', text="Name")
            
                for pair_i, pair in enumerate(bj.bake_queue):
                    row = layout.row(align=True)
                    row.alignment = 'EXPAND'
                    box = row.box().column(align=True)
                    
                    subrow = box.row(align=True)
                    subrow.prop_search(pair, "lowpoly", bpy.context.scene, "objects")
                        
                    subrow = box.row(align=True)
                    subrow.prop(pair, 'hp_obj_vs_group', expand=True)
                    if pair.hp_obj_vs_group == 'OBJ':
                        subrow.prop_search(pair, "highpoly", bpy.context.scene, "objects")
                    else:
                        subrow.prop_search(pair, "highpoly", bpy.data, "groups")
                    subrow = box.row(align=True)
                    
                    subrow.prop(pair, 'extrusion_vs_cage', expand=True)
                    if pair.extrusion_vs_cage == "EXT":
                        subrow.prop(pair, 'extrusion', expand=True)
                    else:
                        subrow.prop_search(pair, "cage", bpy.context.scene, "objects")
                    
                    col = row.column()
                    row = col.row()
                    rem = row.operator("meltdown.rem_pair", text = "", icon = "X")
                    rem.pair_index = pair_i
                    rem.job_index = job_i
                    
                    row = col.row()
                    if pair.activated:
                        row.prop(pair, "activated", icon_only=True, icon = "RESTRICT_RENDER_OFF", emboss = False)
                    else:
                        row.prop(pair, "activated", icon_only=True, icon = "RESTRICT_RENDER_ON", emboss = False)
                        
                row = layout.row(align=True)
                row.alignment = 'EXPAND'
                addpair = row.operator("meltdown.add_pair", icon = "DISCLOSURE_TRI_RIGHT")
                addpair.job_index = job_i
                
                for pass_i, bakepass in enumerate(bj.bake_pass_queue):
                    row = layout.row(align=True)
                    row.alignment = 'EXPAND'
                    box = row.box().column(align=True)
                    
                    # box = layout.box().column(align=True)
                    subrow = box.row(align=True)
                    subrow.alignment = 'EXPAND'
                    subrow.label(text=bakepass.get_filepath(bj = bj))
                    
                    # rem = row.operator("meltdown.rem_pass", text = "", icon = "X")
                    # rem.pass_index = pass_i
                    # rem.job_index = job_i
                    
                    subrow = box.row(align=True)
                    subrow.alignment = 'EXPAND'
                    subrow.prop(bakepass, 'pass_name')
                                
                    subrow = box.row(align=True)
                    subrow.alignment = 'EXPAND'
                    subrow.prop(bakepass, 'suffix')
                    
                    if len(bakepass.props())>0:
                        subrow = box.row(align=True)
                        subrow.alignment = 'EXPAND'
                        subrow.separator()

                        if "ao_distance" in bakepass.props():
                            subrow = box.row(align=True)
                            subrow.alignment = 'EXPAND'
                            subrow.prop(bakepass, 'ao_distance', text = "AO Distance")
                            
                        if "nm_space" in bakepass.props():
                            subrow = box.row(align=True)
                            subrow.alignment = 'EXPAND'
                            subrow.prop(bakepass, 'nm_space', text = "type")

                        if "swizzle" in bakepass.props():
                            subrow = box.row(align=True)
                            subrow.alignment = 'EXPAND'
                            subrow.label(text="Swizzle")
                            subrow.prop(bakepass, 'normal_r', text = "")
                            subrow.prop(bakepass, 'normal_g', text = "")
                            subrow.prop(bakepass, 'normal_b', text = "")
                            
                        if "samples" in bakepass.props():
                            subrow = box.row(align=True)
                            subrow.alignment = 'EXPAND'
                            subrow.prop(bakepass, 'samples', text = "Samples")    
                
                    col = row.column()
                    row = col.row()
                    rem = row.operator("meltdown.rem_pass", text = "", icon = "X")
                    rem.pass_index = pass_i
                    rem.job_index = job_i
                    
                    row = col.row()
                    if bakepass.activated:
                        row.prop(bakepass, "activated", icon_only=True, icon = "RESTRICT_RENDER_OFF", emboss = False)
                    else:
                        row.prop(bakepass, "activated", icon_only=True, icon = "RESTRICT_RENDER_ON", emboss = False)

                row = layout.row(align=True)
                row.alignment = 'EXPAND'
                addpass = row.operator("meltdown.add_pass", icon = "DISCLOSURE_TRI_RIGHT")
                addpass.job_index = job_i
                
                row = layout.row(align=True)
                row.alignment = 'EXPAND'
                row.separator()
            
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("meltdown.add_job", icon = "ZOOMIN")

class MeltdownAddPairOp(bpy.types.Operator):
    '''add pair'''

    bl_idname = "meltdown.add_pair"
    bl_label = "Add Pair"
    
    job_index = bpy.props.IntProperty()
    def execute(self, context):
        bpy.data.scenes[0].meltdown_settings.bake_job_queue[self.job_index].bake_queue.add()
        
        return {'FINISHED'}

class MeltdownRemPairOp(bpy.types.Operator):
    '''delete pair'''

    bl_idname = "meltdown.rem_pair"
    bl_label = "Remove Pair"
    
    pair_index = bpy.props.IntProperty()
    job_index = bpy.props.IntProperty()
    def execute(self, context):
        bpy.data.scenes[0].meltdown_settings.bake_job_queue[self.job_index].bake_queue.remove(self.pair_index)
        
        return {'FINISHED'}
        
class MeltdownAddPassOp(bpy.types.Operator):
    '''add pass'''

    bl_idname = "meltdown.add_pass"
    bl_label = "Add Pass"
    
    job_index = bpy.props.IntProperty()
    def execute(self, context):
        bpy.data.scenes[0].meltdown_settings.bake_job_queue[self.job_index].bake_pass_queue.add()
        return {'FINISHED'}

class MeltdownRemPassOp(bpy.types.Operator):
    '''delete pass'''

    bl_idname = "meltdown.rem_pass"
    bl_label = "Remove Pass"
    
    pass_index = bpy.props.IntProperty()
    job_index = bpy.props.IntProperty()
    def execute(self, context):
        bpy.data.scenes[0].meltdown_settings.bake_job_queue[self.job_index].bake_pass_queue.remove(self.pass_index)
        return {'FINISHED'}

class MeltdownAddJobOp(bpy.types.Operator):
    '''add job'''

    bl_idname = "meltdown.add_job"
    bl_label = "Add Bake Job"
    
    def execute(self, context):
        bpy.data.scenes[0].meltdown_settings.bake_job_queue.add()
        return {'FINISHED'}

class MeltdownRemJobOp(bpy.types.Operator):
    '''delete job'''

    bl_idname = "meltdown.rem_job"
    bl_label = "Remove Bake Job"
    
    job_index = bpy.props.IntProperty()
    def execute(self, context):
        bpy.data.scenes[0].meltdown_settings.bake_job_queue.remove(self.job_index)
        return {'FINISHED'}
    
def register():
    bpy.utils.register_module(__name__)
    
    #bpy.data.scenes[0].bakejob_settings.bake_queue.add()
    
    
def unregister():
    print("Goodbye World!")
    

if __name__ == "__main__":
    register()