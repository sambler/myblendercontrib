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
# Copyright Josh Wedlake 2010
# Thanks to Martin Ellison for vertex group code
# <pep8-80 compliant>
bl_addon_info = {
    'name': 'Mesh: Full Fat Smoothie Maker',
    'author': 'Josh Wedlake',
    'version': '0.1',
    'blender': (2, 5, 3),
    'location': 'ToolShelf Search',
    'description': 'Multiple Smooth Algorithms',
    'url': 'http://tube.freefac.org',
    'category': 'Mesh'}

import bpy
from bpy.ops import *
import math

    
class Smoothie(bpy.types.Operator):
    '''advance smoothing algorithms'''
    bl_idname = "mesh.smoothie_maker"
    bl_label = "Full Fat Smoothie Maker"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    
    smooth_amount = bpy.props.FloatProperty(name="Smooth Amount", description="amount of smoothing to apply",default=0.1,min=0,max=10,step=0.01,precision=3)
    smooth_iterations = bpy.props.IntProperty(name="Iterations", description="number of times to repeat smoothing",default=1,min=1,max=100,step=1)
    smooth_algorithm=bpy.props.EnumProperty(items=[('ALGO','Smoothing Algorithm','Smoothing algorithm to use'),('AVE','Quick Neighbour Average (looses shape)','Mean of Neighbours'),('NPV','Neighbour-Point Vectors (treats edges as rigid)','Average Length along Neighbour-Point Vectors'),('PNA','Neighbour-Plane Perp Vector Average (good for sharp corners)','Point on a perpendicular to the plane formed by neighbour points'),('HNPV','Half Neighbour-Point Vectors (keeps shape, spreads vertices evenly)','Half-Length along Neighbour-Point Vectors'),('NNA','Neighbour Normal Average','Neighbour Normal Average')],default='HNPV')
    X_in=bpy.props.FloatProperty(name="X in",description="Use X coordinate in input",default=1,min=0,max=1,step=0.1,precision=2)
    Y_in=bpy.props.FloatProperty(name="Y in",description="Use Y coordinate in input",default=1,min=0,max=1,step=0.1,precision=2)
    Z_in=bpy.props.FloatProperty(name="Z in",description="Use Z coordinate in input",default=1,min=0,max=1,step=0.1,precision=2)
    X_out=bpy.props.FloatProperty(name="X out",description="Use X coordinate in output",default=1,min=0,max=1,step=0.1,precision=2)
    Y_out=bpy.props.FloatProperty(name="Y out",description="Use Y coordinate in output",default=1,min=0,max=1,step=0.1,precision=2)
    Z_out=bpy.props.FloatProperty(name="Z out",description="Use Z coordinate in output",default=1,min=0,max=1,step=0.1,precision=2)
    exclude_unselected=bpy.props.BoolProperty(name="Ignore Unselected Neighbours",description="determines whether unselected neighbours are ignored as non-existant in the algorithm",default=False)
    non_manifold_mode=bpy.props.EnumProperty(items=[('NMH','Non-Manifold Edge Handling','Non-Manifold Edge Handling'),('NMP','Fully Processed','Non-Manifolds are Processed'),('NMI','Considered Non-Existant (Ignored)','Non-Manifolds are taken as Non-Existant (Ignored)'),('NMU','Considered but Unchanged','Non-Manifolds Considered but Unchanged')],default='NMU')
    normal_compensation_algorithm=bpy.props.EnumProperty(items=[('NALGO','Normal Compensation Algorithm to Use','Normal Compensation Algorithm to Use'),('RAW','Raw Differences (lazy)','Project on Normal by Change Amount'),('NPV','Differences Projected on Normal (similar to Alt+S)','Differences Projected on Normal'),('ANP','Differences Projected on Averaged Neighbour Normals (removes smaller detail)','Differences Projected on Averaged Neighbour Normals')],default='NPV')
    normal_compensation_direction=bpy.props.EnumProperty(items=[('NCOMP','Allow Compensation to...','Allow Compensation to...'),('-1','Shrink Only','Shrink Only'),('0','Shrink and Expand','Shrink and Expand'),('+1','Expand Only','Expand Only')],default='0')
    normal_compensation=bpy.props.FloatProperty(name="Post Compensate For Shrinking",description="adjusts each calculated point for shrinkage",min=0,max=1,step=0.1,default=1)
    remove_doubles=bpy.props.FloatProperty(name="Remove Doubles Each Iteration", description="threshold for a remove doubles each iteration",default=0,min=0,max=1,step=0.001,precision=3)
    selection_growth = bpy.props.IntProperty(name="Selection Growth/Shrink Each Iteration", description="number of times to grow or shrink the selection after each iteration",default=0,min=-10,max=10,step=1)
    dialog_width = 400
    
    def build_vertex_group_enum(self,context):
        vertex_group_list=[]
        vertex_group_list.append(('VGID','Vertex Group Mask','Vertex Group to Mask Smoothing'))
        vertex_group_list.append(('-1','(Do not use vertex groups)','no group'))
        obj = context.active_object
        for index,vg in enumerate(obj.vertex_groups):
            vertex_group_list.append((str(index), vg.name, vg.name))
        context.active_object.EnumProperty(attr="smoothie_vertex_group_mask",items=vertex_group_list,default='-1')
        
    def build_transform_orientations_enum(self,context):
        orientations_list=[]
        orientations_list.append(('PRIMARY','Primary (X)','Primary (X) Axis For Smoothing'))
        orientations_list.append(('W_X','World X','World X'))
        orientations_list.append(('W_Y','World Y','World Y'))
        orientations_list.append(('W_Z','World Z','World Z'))
        orientations_list.append(('L_X','Local X','Local X'))
        orientations_list.append(('L_Y','Local Y','Local Y'))
        orientations_list.append(('L_Z','Local Z','local Z'))
        for orientation_index in range(0,len(context.scene.orientations)):
            mx=context.scene.orientations[orientation_index].matrix[0]
            my=context.scene.orientations[orientation_index].matrix[1]
            mz=context.scene.orientations[orientation_index].matrix[2]
            name=context.scene.orientations[orientation_index].name
            nx=name+' X ('+str(round(mx[0],2))+','+str(round(mx[1],2))+','+str(round(mx[2],2))+')'
            ny=name+' Y ('+str(round(my[0],2))+','+str(round(my[1],2))+','+str(round(my[2],2))+')'
            nz=name+' Z ('+str(round(mz[0],2))+','+str(round(mz[1],2))+','+str(round(mz[2],2))+')'
            orientations_list.append(('S_X_'+str(orientation_index),nx,nx))
            orientations_list.append(('S_Y_'+str(orientation_index),ny,ny))
            orientations_list.append(('S_Z_'+str(orientation_index),nz,nz))
        ol_Y=orientations_list[:]
        ol_Y[0]=('SECONDARY','Secondary (Y)','Secondary (Y) Axis For Smoothing')
        ol_Y.append(('A','Auto Secondary','Automatically Generate Second Axis'))
        context.active_object.EnumProperty(attr="smoothie_X_in",items=orientations_list,default='W_X')
        context.active_object.EnumProperty(attr="smoothie_Y_in",items=ol_Y,default='A')
    
    def get_transform_matrix(self,context,or_X,or_Y):
        import mathutils
        vx=self.get_transform_vector(context,or_X)
        vy=self.get_transform_vector(context,or_Y)
        if vy.length==0:
            if or_X[2]=='X':
                or_Y=or_X[:2]+'Y'+or_X[3:]
            elif or_X[2]=='Y':
                or_Y=or_X[:2]+'Z'+or_X[3:]
            elif or_X[2]=='Z':
                or_Y=or_X[:2]+'X'+or_X[3:]
            vy=self.get_transform_vector(context,or_Y)
        if vx.angle(vy)==0:
            #the vectors are useless...
            return -1
            #parent function needs to turn off input/output for Y/Z
        else:
            vz=vx.copy().cross(vy)
            vy=vz.copy().cross(vx)
            return mathutils.Matrix(vx.normalize(),vy.normalize(),vz.normalize())

        
    def get_transform_vector(self,context,ori):
        import mathutils
        if ori=='W_X':
            v=context.active_object.matrix_world.copy().to_3x3()[0]
        elif ori=='W_Y':
            v=context.active_object.matrix_world.copy().to_3x3()[1]
        elif ori=='W_Z':
            v=context.active_object.matrix_world.copy().to_3x3()[2]
        elif ori=='L_X':
            v=mathutils.Vector((1,0,0))
        elif ori=='L_Y':
            v=mathutils.Vector((0,1,0))
        elif ori=='L_Z':
            v=mathutils.Vector((0,0,1))
        elif ori[:4]=='S_X_':
            or_index=int(ori[4:])
            v=context.scene.orientations[or_index].matrix.copy().to_3x3()[0]*context.active_object.matrix_world.copy().to_3x3()
        elif ori[:4]=='S_Y_':
            or_index=int(ori[4:])
            v=context.scene.orientations[or_index].matrix.copy().to_3x3()[1]*context.active_object.matrix_world.copy().to_3x3()
        elif ori[:4]=='S_Z_':
            or_index=int(ori[4:])
            v=context.scene.orientations[or_index].matrix.copy().to_3x3()[2]*context.active_object.matrix_world.copy().to_3x3()
        else:
            v=mathutils.Vector((0,0,0))
        return v

    def get_vert_selection(self,obdat):
        verts_selected=set()
        for index,ivert in enumerate(obdat.verts):
            if ivert.select==True:
                verts_selected.add(index)
        return verts_selected
    
    def set_vert_selection(self,obdat,selection_set): 
        for index,ivert in enumerate(obdat.verts):
            if index in selection_set:
                ivert.select=True
            else:
                ivert.select=False

    def get_non_manifold_vert_selection(self,obdat,selection_set):
        import bpy
        bpy.ops.object.editmode_toggle()
        if obdat.total_vert_sel>0:
            bpy.ops.mesh.select_all()
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.object.editmode_toggle()
        non_manifold_set=self.get_vert_selection(obdat)
        bpy.ops.object.editmode_toggle()
        if bpy.context.active_object.data.total_vert_sel>0:
            bpy.ops.mesh.select_all()
        bpy.ops.object.editmode_toggle()
        self.set_vert_selection(obdat,selection_set)
        return non_manifold_set

    def set_co(self,obdat,vert_index,new_vector,XYZ_out,matrix_out,matrix_in):
        existing_pt=self.get_co(obdat,vert_index,matrix_in)
        new_vector.x=(new_vector.x*XYZ_out[0])+(existing_pt[0]*(1-XYZ_out[0]))
        new_vector.y=(new_vector.y*XYZ_out[1])+(existing_pt[1]*(1-XYZ_out[1]))
        new_vector.z=(new_vector.z*XYZ_out[2])+(existing_pt[2]*(1-XYZ_out[2]))
        new_vector=matrix_out*new_vector
        obdat.verts[vert_index].co=new_vector
    
    def get_co(self,obdat,vert_index,matrix_in):
        vert_co=obdat.verts[vert_index].co.copy()
        vert_co=matrix_in*vert_co
        return vert_co
    
    def get_no(self,obdat,vert_index,matrix_in):
        vert_no=obdat.verts[vert_index].normal.copy()
        vert_no=matrix_in*vert_no
        return vert_no

    def build_neighbours(self,obdat,vert_index,exclude_unselected,selection_set):
        neighbour_set=set()
        for edge in obdat.edges:
            if vert_index in edge.verts:
                if exclude_unselected:
                    neighbour_set|=(set(edge.verts)&selection_set)
                else:
                    neighbour_set|=set(edge.verts)
        neighbour_set.remove(vert_index)
        return neighbour_set

    def build_neighbours_dictionary(self,obdat,exclude_unselected,selection_set):
        selection_list=list(selection_set)
        neighbours_dictionary=dict()
        for each_vertex in selection_list:
            neighbours_dictionary[each_vertex]=self.build_neighbours(obdat,each_vertex,exclude_unselected,selection_set)
        return neighbours_dictionary
        
    def average_vector_list(self,vector_list):
        import mathutils
        vector_sum=mathutils.Vector()
        for each_vector in vector_list:
            vector_sum+=each_vector
        return vector_sum/len(vector_list)
    
    def average_vector_list_length(self,vector_list):
        vector_length_sum=0
        for each_vector in vector_list:
            vector_length_sum+=each_vector.length
        return vector_length_sum/len(vector_list)
    
    def update_vertices_from_dictionary(self,obdat,selection_set,vert_dict,XYZ_out,matrix_out,matrix_in):
        selection_list=list(selection_set)
        for each_vertex in selection_list:
            self.set_co(obdat,each_vertex,vert_dict[each_vertex],XYZ_out,matrix_out,matrix_in)
    
    def apply_smooth_amount(self,obdat,vert_dict,smooth_amount,matrix_in):
        vert_list=list(vert_dict.keys())
        for each_vert in vert_list:
            existing_co=self.get_co(obdat,each_vert,matrix_in)
            vert_dict[each_vert]=(vert_dict[each_vert]*smooth_amount)+(existing_co*(1-smooth_amount))
        return vert_dict

    def apply_vertex_group_amount(self,obdat,vert_dict,group_index,matrix_in):
        vert_list=list(vert_dict.keys())
        for each_vert in vert_list:
            existing_co=self.get_co(obdat,each_vert,matrix_in)
            weight_amount=0
            for group_search_index in range(0,len(obdat.verts[each_vert].groups)):
                if obdat.verts[each_vert].groups[group_search_index].group==group_index:
                    weight_amount=obdat.verts[each_vert].groups[group_search_index].weight
                    break
            vert_dict[each_vert]=(vert_dict[each_vert]*weight_amount)+(existing_co*(1-weight_amount))
        return vert_dict
    
    def build_vertex_dictionary(self,obdat,selection_list,matrix_in):
        vert_dict=dict()        
        for each_vertex in selection_list:
            vert_dict[each_vertex]=self.get_co(obdat,each_vertex,matrix_in)
        return vert_dict
    
    def get_average_neighbour_normal(self,obdat,vert_index,neighbour_dictionary,selection_set,matrix_in):
        import mathutils
        vector_sum=mathutils.Vector()
        neighbour_list=list(neighbour_dictionary[vert_index])
        for neighbour in neighbour_list:
            vector_sum+=self.get_no(obdat,neighbour,matrix_in)
        return vector_sum/len(neighbour_list)

    def set_direction(self,direction_vector,vector_to_set):
        import math
        if vector_to_set.length>0 and direction_vector.length>0:
            if vector_to_set.angle(direction_vector)>math.radians(90) or vector_to_set.angle(direction_vector)<-math.radians(90):
                vector_to_set=-vector_to_set
        return vector_to_set.normalize()
    
    def get_length_multiplier(self,direction_vector,vector_to_test):
        import math
        if vector_to_test.length>0 and direction_vector.length>0:
            if vector_to_test.angle(direction_vector)>math.radians(90) or vector_to_test.angle(direction_vector)<-math.radians(90):
                return 1
            else:
                return -1
        return 0
    
    def get_normal_multiplier(self,direction_vector,vector_to_test,normal_compensation_direction):
        import math
        if vector_to_test.length>0 and direction_vector.length>0:
            if vector_to_test.angle(direction_vector)>math.radians(90) or vector_to_test.angle(direction_vector)<-math.radians(90):
                if normal_compensation_direction=='0' or normal_compensation_direction=='+1':
                    return 1
                else:
                    return 0
            else:
                if normal_compensation_direction=='0' or normal_compensation_direction=='-1':
                    return -1
                else:
                    return 0
        return 0

    def normal_compensate_points(self,obdat,vert_dict_old,normal_compensation_algorithm,normalize_amount,neighbour_dictionary,selection_set,normal_compensation_direction,matrix_in):
        vertex_list=list(vert_dict_old.keys())
        vert_dict_new=dict()
        if normal_compensation_algorithm=='RAW':
            for each_vertex in vertex_list:
                current_vertex=self.get_co(obdat,each_vertex,matrix_in)
                #get the normal of the current vertex position
                vert_normal=self.get_no(obdat,each_vertex,matrix_in)
                #get the vector between the current and the old position
                vector_current_to_old=current_vertex-vert_dict_old[each_vertex]
                #normalize the normal and multiply by distance between the old and new
                change_vector=vert_normal.normalize()*(vector_current_to_old.length*self.get_normal_multiplier(vert_normal,vector_current_to_old,normal_compensation_direction))
                #add it to the existing point
                vert_dict_new[each_vertex]=current_vertex+(change_vector*normalize_amount)
        elif normal_compensation_algorithm=='NPV':
            for each_vertex in vertex_list:
                current_vertex=self.get_co(obdat,each_vertex,matrix_in)
                #get the normal of the current vertex position
                vert_normal=self.get_no(obdat,each_vertex,matrix_in)
                vert_normal=vert_normal.normalize()
                #get the vector between the current and the old position
                vector_current_to_old=current_vertex-vert_dict_old[each_vertex]
                #project the 2nd vector in the first vector
                projected_vector=vector_current_to_old.project(vert_normal)
                #normalize the normal and multiply by projection length
                change_vector=vert_normal.normalize()*(projected_vector.length*self.get_normal_multiplier(vert_normal,vector_current_to_old,normal_compensation_direction))
                #add it to the existing point
                vert_dict_new[each_vertex]=current_vertex+(change_vector*normalize_amount)
        elif normal_compensation_algorithm=='ANP':
            for each_vertex in vertex_list:
                current_vertex=self.get_co(obdat,each_vertex,matrix_in)
                #get the normal of the current vertex's neighbours
                vert_normal=self.get_average_neighbour_normal(obdat,each_vertex,neighbour_dictionary,selection_set,matrix_in)
                vert_normal=vert_normal.normalize()
                #get the vector between the current and the old position
                vector_current_to_old=current_vertex-vert_dict_old[each_vertex]
                #project the 2nd vector in the first vector
                projected_vector=vector_current_to_old.project(vert_normal)
                #normalize the normal and multiply by projection length
                change_vector=vert_normal.normalize()*(projected_vector.length*self.get_normal_multiplier(vert_normal,vector_current_to_old,normal_compensation_direction))
                #add it to the existing point
                vert_dict_new[each_vertex]=current_vertex+(change_vector*normalize_amount) 
        return vert_dict_new
    
    def method_AVE(self,obdat,vert_index,matrix_in,neighbour_dictionary,selection_set):
        neighbour_list=list(neighbour_dictionary[vert_index])
        neighbour_points=[]
        for each_neighbour in neighbour_list:
            neighbour_points.append(self.get_co(obdat,each_neighbour,matrix_in))
        return self.average_vector_list(neighbour_points)

    def method_NNA(self,obdat,vert_index,matrix_in,neighbour_dictionary,selection_set):
        neighbour_list=list(neighbour_dictionary[vert_index])
        neighbour_points=[]
        neighbour_normals=[]
        current_vertex=self.get_co(obdat,vert_index,matrix_in)
        for each_neighbour in neighbour_list:
            neighbour_point=(self.get_co(obdat,each_neighbour,matrix_in))
            neighbour_normal=(self.get_no(obdat,each_neighbour,matrix_in)).normalize()
            dist_from_current=(current_vertex-neighbour_point).length
            neighbour_points.append(neighbour_point+(neighbour_normal*dist_from_current))
        return self.average_vector_list(neighbour_points)

    def method_NPV(self,obdat,vert_index,matrix_in,neighbour_dictionary,selection_set):
        neighbour_list=list(neighbour_dictionary[vert_index])
        this_point=self.get_co(obdat,vert_index,matrix_in)
        #make a list of neighbour point vectors
        neighbour_to_point_vectors=[]
        neighbour_points=[]
        for neighbour_index in neighbour_list:
            neighbour_point=self.get_co(obdat,neighbour_index,matrix_in)
            neighbour_points.append(neighbour_point)
            neighbour_to_point_vectors.append(this_point-neighbour_point)
        #find average length
        average_length=self.average_vector_list_length(neighbour_to_point_vectors)
        #normalize each neighbour_to_point_vectors
        for index in range(0,len(neighbour_to_point_vectors)):
            neighbour_to_point_vectors[index]=neighbour_points[index]+(neighbour_to_point_vectors[index].normalize()*average_length)
        return self.average_vector_list(neighbour_to_point_vectors)

    def method_HNPV(self,obdat,vert_index,matrix_in,neighbour_dictionary,selection_set):
        neighbour_list=list(neighbour_dictionary[vert_index])
        this_point=self.get_co(obdat,vert_index,matrix_in)
        #make a list of neighbour point vectors
        halfway_points=[]
        neighbour_points=[]
        for neighbour_index in neighbour_list:
            halfway_points.append((self.get_co(obdat,neighbour_index,matrix_in)+this_point)/2)
        #return the average of the halfway points
        return self.average_vector_list(halfway_points)
    
    def method_PNA(self,obdat,vert_index,matrix_in,neighbour_dictionary,selection_set):
        import math
        current_vertex=self.get_co(obdat,vert_index,matrix_in)
        #find neighbours
        neighbour_list=list(neighbour_dictionary[vert_index])
        #find average point of all neighbours
        neighbour_points=[]
        for each_neighbour in neighbour_list:
            neighbour_points.append(self.get_co(obdat,each_neighbour,matrix_in))
        average_point=self.average_vector_list(neighbour_points)
        #form av>neighbour vector cross pairs results
        number_of_neighbours=len(neighbour_points)
        cross_results=[]
        for index in range(0,number_of_neighbours):
            v1=(neighbour_points[index])-average_point
            if index!=number_of_neighbours-1:
                v2=neighbour_points[index+1]-average_point
            else:
                v2=neighbour_points[0]-average_point
            cross_results.append(v2.cross(v1))
            #normalise and set the direction for the cross result
            cross_results[index]=self.set_direction(current_vertex-average_point,cross_results[index])
        #check there are no points too close together
        if cross_results[index].length>0 and (self.get_no(obdat,vert_index,matrix_in)).length>0:
             #average the cross pairs
            average_cross_result=self.average_vector_list(cross_results)
            #multiply the average cross result by the length of the vector between the av and current
            #return average_point+(average_cross_result*(((current_vertex-average_point).project(average_cross_result)).length))
            return average_point+(average_cross_result*((current_vertex-average_point).length))
        else:
            return self.get_co(obdat,vert_index,matrix_in)
            
    def invoke(self, context, event):
        self.build_vertex_group_enum(context)
        self.build_transform_orientations_enum(context)
        context.active_object.smoothie_X_in='W_X'
        context.active_object.smoothie_Y_in='A'
        context.active_object.smoothie_vertex_group_mask='-1'
        wm = context.manager
        wm.invoke_props_dialog(self, self.dialog_width)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        import bpy
        import mathutils
        
        normal_compensation=self.properties.normal_compensation
        bpy.context.tool_settings.mesh_selection_mode=[True,False,False]
        obdat=bpy.context.active_object.data
        if context.mode=='EDIT_MESH':
            bpy.ops.object.editmode_toggle()
        #test for vertex group
        group_index_for_mask=int(context.active_object.smoothie_vertex_group_mask)
        
        #XYZ in and out processing        
        X_in=self.properties.X_in
        Y_in=self.properties.Y_in
        Z_in=self.properties.Z_in
        XYZ_out=[]
        XYZ_out.append(self.properties.X_out)
        XYZ_out.append(self.properties.Y_out)
        XYZ_out.append(self.properties.Z_out)
        if X_in<1:
            XYZ_out[0]=0
            self.properties.X_out=0
        if Y_in<1:
            XYZ_out[1]=0
            self.properties.Y_out=0
        if Z_in<1:
            XYZ_out[2]=0
            self.properties.Z_out=0
        print(X_in,Y_in,Z_in,XYZ_out)
        XYZ_in_matrix=mathutils.Matrix((X_in,0,0),(0,Y_in,0),(0,0,Z_in))
        
        #get the transform matrix
        matrix_calc=self.get_transform_matrix(context,context.active_object.smoothie_X_in,context.active_object.smoothie_Y_in)
        if matrix_calc==-1:
            print ('Cannot use two colinear axes!')
            return {'CANCELLED'}
        matrix_calc=matrix_calc.rotation_part()
        matrix_in=XYZ_in_matrix*matrix_calc.copy()
        matrix_out=matrix_calc.copy().invert()
        #create a selection set
        selection_set=self.get_vert_selection(obdat)
        if self.properties.non_manifold_mode=='NMI':      
            selection_set-=self.get_non_manifold_vert_selection(obdat,selection_set)
        selection_changed=0
        neighbours_dictionary=self.build_neighbours_dictionary(obdat,self.properties.exclude_unselected,selection_set)
        for iter_run in range(0,self.properties.smooth_iterations):
            #code body here
            #run method to build dictionary
            vert_dict=dict()
            selection_list=list(selection_set)
            for each_vert in selection_list:
                if self.properties.smooth_algorithm=='AVE':
                    vert_dict[each_vert]=self.method_AVE(obdat,each_vert,matrix_in,neighbours_dictionary,selection_set)
                elif self.properties.smooth_algorithm=='NPV':
                    vert_dict[each_vert]=self.method_NPV(obdat,each_vert,matrix_in,neighbours_dictionary,selection_set)
                elif self.properties.smooth_algorithm=='PNA':
                    vert_dict[each_vert]=self.method_PNA(obdat,each_vert,matrix_in,neighbours_dictionary,selection_set)
                elif self.properties.smooth_algorithm=='HNPV':
                    vert_dict[each_vert]=self.method_HNPV(obdat,each_vert,matrix_in,neighbours_dictionary,selection_set)
                elif self.properties.smooth_algorithm=='NNA':
                    vert_dict[each_vert]=self.method_NNA(obdat,each_vert,matrix_in,neighbours_dictionary,selection_set)
            #adjust the result
            vert_dict=self.apply_smooth_amount(obdat,vert_dict,self.properties.smooth_amount,matrix_calc)
            if group_index_for_mask!=-1:
                vert_dict=self.apply_vertex_group_amount(obdat,vert_dict,group_index_for_mask,matrix_calc)
            #create a selection set for NMU - if non manifolds are untouched
            if self.properties.non_manifold_mode=='NMU':
                apply_selection_set=selection_set-self.get_non_manifold_vert_selection(obdat,selection_set)
            else:
                apply_selection_set=selection_set
            if normal_compensation!=0:
                #build the existing point and normal dictionary...
                vert_dict_old=self.build_vertex_dictionary(obdat,selection_list,matrix_in)
                #update the real points
                self.update_vertices_from_dictionary(obdat,apply_selection_set,vert_dict,XYZ_out,matrix_out,matrix_calc)
                #build a new vert_dict based on normal compensation...
                vert_dict=self.normal_compensate_points(obdat,vert_dict_old,self.properties.normal_compensation_algorithm,normal_compensation,neighbours_dictionary,selection_set,self.properties.normal_compensation_direction,matrix_in)
                #apply the mask
                if group_index_for_mask!=-1:
                    vert_dict=self.apply_vertex_group_amount(obdat,vert_dict,group_index_for_mask,matrix_calc)
                #update the points
                self.update_vertices_from_dictionary(obdat,apply_selection_set,vert_dict,XYZ_out,matrix_out,matrix_calc)
            else:
                self.update_vertices_from_dictionary(obdat,apply_selection_set,vert_dict,XYZ_out,matrix_out,matrix_calc)
            if self.properties.remove_doubles>0:
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.remove_doubles(limit=self.properties.remove_doubles)
                bpy.ops.object.editmode_toggle()
                selection_changed=1
            if self.properties.selection_growth>0:
                bpy.ops.object.editmode_toggle()
                for temp in range(0,self.properties.selection_growth):
                    bpy.ops.mesh.select_more()
                bpy.ops.object.editmode_toggle()
                selection_changed=1
            elif self.properties.selection_growth<0:
                bpy.ops.object.editmode_toggle()
                for temp in range(0,-self.properties.selection_growth):
                    bpy.ops.mesh.select_less()
                bpy.ops.object.editmode_toggle()
                selection_changed=1
            if selection_changed==1:
                #rebuild the selection
                selection_set=self.get_vert_selection(obdat)
                if self.properties.non_manifold_mode=='NMI':      
                    selection_set-=self.get_non_manifold_vert_selection(obdat,selection_set)
                neighbours_dictionary=self.build_neighbours_dictionary(obdat,self.properties.exclude_unselected,selection_set)
                selection_changed=0
        bpy.ops.object.editmode_toggle()


        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        props = self.properties
        
        row = layout.row()
        split = row.split(percentage=0.5)
        colL = split.column()
        colR = split.column() 
        colL.prop(props, "smooth_amount")
        colR.prop(props, "smooth_iterations")
        
        layout.prop(props, "smooth_algorithm")
        
        row = layout.row()
        split = row.split(percentage=0.7)
        colL = split.column()
        colR = split.column()
        colL.prop(context.active_object, "smoothie_X_in", text="Primary (X) Axis")
        colR.prop(props, "X_in")
        colL.prop(context.active_object, "smoothie_Y_in", text="Secondary (Y) Axis")
        colR.prop(props, "Y_in")
        colL.label(text="Tertiary Axis (X cross Y)")
        colR.prop(props, "Z_in")
        colL.label(text="Primary Axis Out")
        colR.prop(props, "X_out")
        colL.label(text="Secondary Axis Out")
        colR.prop(props, "Y_out")
        colL.label(text="Tertiary Axis Out")
        colR.prop(props, "Z_out")
        
        layout.prop(props, "exclude_unselected")
        layout.prop(props, "non_manifold_mode")
        layout.prop(props, "normal_compensation_algorithm")
        layout.prop(props, "normal_compensation_direction")
        layout.prop(props, "normal_compensation")
        layout.prop(props, "remove_doubles")
        layout.prop(props, "selection_growth")
        
        layout.prop(context.active_object, "smoothie_vertex_group_mask", text="Vertex Group Mask")



specials_classes = [Smoothie]

classes=list(set(specials_classes))

def gen(c):
    def menu_func(self, context):
        self.layout.operator(c.bl_idname, c.bl_label)
    return(menu_func)

def register():
    #register = bpy.types.register
    #for c in classes:
    #        register(c)
    for c in specials_classes:
        bpy.types.VIEW3D_MT_edit_mesh_specials.append(gen(c))

def unregister():
    #unregister = bpy.types.unregister
    #for c in classes:
    #        unregister(c)
    for c in specials_classes:
        bpy.types.VIEW3D_MT_edit_mesh_specials.remove(gen(c)) 

if __name__ == "__main__":
    unregister()
    register()