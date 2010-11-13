'''
The files are licenced under a BSD licence.

Copyright (c) 2010, Florian Meyer
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    * Neither the name of the <ORGANIZATION> nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''


''' Usage Notes:

in Maya Mel:
cacheFile -pc2 1 -pcf "<insert filepath of source>" -f "<insert target filename w/o extension>" -dir "<insert directory path for target>" -format "OneFile";

'''


bl_addon_info = {
    "name": "Export Pointcache (.pc2)",
    "author": "Florian Meyer (tstscr)",
    "version": (1,0),
    "blender": (2, 5, 4),
    "api": 33047,
    "location": "File > Export",
    "description": "Export Mesh Pointcache to .pc2",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import/Export"}


import bpy
from bpy.props import *
import mathutils, math, struct
from os import remove
import time
from io_utils import ExportHelper

def getSampling(start, end, sampling):
    samples = [start - sampling
               + x * sampling
               for x in range(start, int((end-start)*1/sampling)+1)]
    return samples

def do_export(context, props, filepath):
    mat_x90 = mathutils.Matrix.Rotation(-math.pi/2, 4, 'X')
    ob = context.active_object
    sc = context.scene
    start = props.range_start
    end = props.range_end
    sampling = float(props.sampling)
    apply_modifiers = props.apply_modifiers
    me = ob.create_mesh(sc, apply_modifiers, 'PREVIEW')
    vertCount = len(me.vertices)
    sampletimes = getSampling(start, end, sampling)
    sampleCount = len(sampletimes)
    
    # Create the header
    headerFormat='<12ciiffi'
    headerStr = struct.pack(headerFormat, 'P','O','I','N','T','C','A','C','H','E','2','\0',
                            1, vertCount, start, sampling, sampleCount)

    file = open(filepath, "wb")
    file.write(headerStr)
    
    for frame in sampletimes:
        sc.frame_set(frame)
        me = ob.create_mesh(sc, apply_modifiers, 'PREVIEW')
        
        if len(me.vertices) != vertCount:
            file.close()
            try:
                remove(filepath)
            except:
                empty = open(filepath, 'w')
                empty.write('DUMMIFILE - export failed\n')
                empty.close()
            print('Export failed. Vertexcount of Object is not constant')
            return False
        
        if props.world_space:
            me.transform(ob.matrix_world)
        if props.rot_x90:
            me.transform(mat_x90)
        
        for v in me.vertices:
            thisVertex = struct.pack('<fff', float(v.co[0]),
                                             float(v.co[1]),
                                             float(v.co[2]))
            file.write(thisVertex)
    
    file.flush()
    file.close()
    return True


###### EXPORT OPERATOR #######
class Export_pc2(bpy.types.Operator, ExportHelper):
    '''Exports the active Object as a .pc2 Pointcache file.'''
    bl_idname = "export_pc2"
    bl_label = "Export Pointcache (.pc2)"

    filename_ext = ".pc2"
    
    rot_x90 = BoolProperty(name="Convert to Y-up",
                            description="Rotate 90 degrees around X to convert to y-up",
                            default=True)
    world_space = BoolProperty(name="Export into Worldspace",
                            description="Transform the Vertexcoordinates into Worldspace",
                            default=False)
    apply_modifiers = BoolProperty(name="Apply Modifiers",
                            description="Applies the Modifiers",
                            default=True)
    range_start = IntProperty(name='Start Frame',
                            description='First frame to use for Export',
                            default=1)
    range_end = IntProperty(name='End Frame',
                            description='Last frame to use for Export',
                            default=250)    
    sampling = EnumProperty(name='Sampling',
                            description='Sampling --> frames per sample (0.1 yields 10 samples per frame)',
                            items=[
                            ('0.01', '0.01', ''),
                            ('0.05', '0.05', ''),
                            ('0.1', '0.1', ''),
                            ('0.2', '0.2', ''),
                            ('0.25', '0.25', ''),
                            ('0.5', '0.5', ''),
                            ('1', '1', ''),
                            ('2', '2', ''),
                            ('3', '3', ''),
                            ('4', '4', ''),
                            ('5', '5', ''),
                            ('10', '10', '')],
                            default='1')
    
    @classmethod
    def poll(cls, context):
        return context.active_object.type in ['MESH', 'CURVE', 'SURFACE', 'FONT']

    def execute(self, context):
        start_time = time.time()
        print('\n_____START_____')
        props = self.properties
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        exported = do_export(context, props, filepath)
        
        if exported:
            print('finished export in %s seconds' %((time.time() - start_time)))
            print(filepath)
            
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        if True:
            # File selector
            wm.add_fileselect(self) # will run self.execute()
            return {'RUNNING_MODAL'}
        elif True:
            # search the enum
            wm.invoke_search_popup(self)
            return {'RUNNING_MODAL'}
        elif False:
            # Redo popup
            return wm.invoke_props_popup(self, event) #
        elif False:
            return self.execute(context)


### REGISTER ###

def menu_func(self, context):
    self.layout.operator(Export_pc2.bl_idname, text="Pointcache (.pc2)")


def register():
    bpy.types.INFO_MT_file_export.append(menu_func)
    #bpy.types.VIEW3D_PT_tools_objectmode.prepend(menu_func)

def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func)
    #bpy.types.VIEW3D_PT_tools_objectmode.remove(menu_func)
    
if __name__ == "__main__":
    register()