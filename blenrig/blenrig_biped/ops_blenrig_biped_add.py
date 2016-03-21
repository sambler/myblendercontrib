import bpy
import os

class Operator_BlenRig5_Add_Biped(bpy.types.Operator):    
    
    bl_idname = "blenrig5.add_biped_rig"   
    bl_label = "BlenRig 5 Add Biped Rig"   
    bl_description = "Generates BlenRig 5 biped rig"    
    bl_options = {'REGISTER', 'UNDO',}     


    @classmethod
    def poll(cls, context):                            #method called by blender to check if the operator can be run
        return bpy.context.scene != None
       
    def import_blenrig_biped(self, context):
        CURRENT_DIR = os.path.dirname(__file__)        
        filepath =  os.path.join(CURRENT_DIR, "blenrig_biped.blend")
        group_name = "blenrig_biped"       
        scene = bpy.context.scene 

        # append all groups from the .blend file
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            ## all groups
            # data_to.groups = data_from.groups

            # only append a single group we already know the name of
            data_to.groups = [group_name]

        # add the group instance to the scene
        for group in data_to.groups:
            for ob in group.objects:
                scene.objects.link(ob)
        #assign  layers
                if ob.type == 'MESH':
                    ob.layers = [(x in [19]) for x in range(20)]  
                    if 'BlenRig_mdef_cage' in ob.name:
                        ob.layers = [(x in [11]) for x in range(20)]   
                    if 'BlenRig_proxy_model' in ob.name:
                        ob.layers = [(x in [1]) for x in range(20)]    
                if ob.type == 'LATTICE':
                    ob.layers = [(x in [12]) for x in range(20)]      
                if ob.type == 'ARMATURE':
                    ob.layers = [(x in [10]) for x in range(20)] 
                    if 'biped_blenrig' in ob.name:
                        bpy.context.scene.layers[10] = True 
                        bpy.context.scene.objects.active = ob
                        bpy.ops.object.mode_set(mode='POSE')                 

    def execute(self, context):
        self.import_blenrig_biped(context)
        return{'FINISHED'}  