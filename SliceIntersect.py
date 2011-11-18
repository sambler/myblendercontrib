# parts based on Keith (Wahooney) Boshoff, cursor to intersection script and
# Paul Bourke's Shortest Line Between 2 lines
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****


import bpy
import sys
from mathutils import Vector


__author__ = ['zeffii']
__version__ = '0.1'
__bpydoc__ = """
             """


bl_addon_info = {
    'name': 'Mesh: Slice Intersect',
    'author': 'zeffii',
    'version': '0.1',
    'blender': (2, 5, 4),
    'location': 'View3D > EditMode > Specials',
    'wiki_url': '',
    'category': 'Mesh'}
       
    

##function lifted from 3dview_spacebar_menu
def LineLineIntersect (p1, p2, p3, p4):
    # based on Paul Bourke's Shortest Line Between 2 lines
    
    min = 0.0000001
    v1 = p1 - p3 #Vector((p1.x - p3.x, p1.y - p3.y, p1.z - p3.z))
    v2 = p4 - p3 #Vector((p4.x - p3.x, p4.y - p3.y, p4.z - p3.z))
    
    if abs(v2.x) < min and abs(v2.y) < min and abs(v2.z) < min:
        return None
    
    v3 = p2 - p1
    
    if abs(v3.x) < min and abs(v3.y) < min and abs(v3.z) < min:
        return None
    
    d1 = v1.dot(v2)
    d2 = v2.dot(v3)
    d3 = v1.dot(v3)
    d4 = v2.dot(v2)
    d5 = v3.dot(v3)
    d = d5 * d4 - d2 * d2
    
    if abs(d) < min:
        return None
    
    n = d1 * d2 - d3 * d4
    mua = n / d
    mub = (d1 + d2 * (mua)) / d4

    #modified for clarity, and to use some neat Vector functionality.    
    return [p1 + mua * v3 , p3  + mub * v2] 
            
            

##function partially lifted from 3dview_spacebar_menu
def checkEdges(Edge, obj):
    
    p1 = Vector((Edge[0][0]))
    p2 = Vector((Edge[0][1]))
    p3 = Vector((Edge[1][0]))
    p4 = Vector((Edge[1][1]))

    line = LineLineIntersect(p1, p2, p3, p4)
    
    if line == None: return None
        
    tm = obj.matrix_world.copy()
    point = ((line[0] + line[1]) / 2)
    point = tm * point
   
    return point


def makeGeometry(point,outer_points):
        
    # print("start cutting")
    # print("intersection point: " + str(point))    
        
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='EDGE') # removes edges + verts
  
    (vert_count, edge_count) = getVertEdgeCount()
    vert_count = len(vert_count)
    edge_count = len(edge_count)
    
    '''
    print("vert count is now: " + str(vert_count))
    print("Edge count is now: " + str(edge_count))

    print(outer_points[0][0])
    print(outer_points[0][1])
    print(outer_points[1][0])
    print(outer_points[1][1])
    
    '''
    
    bpy.ops.object.mode_set(mode='OBJECT') # to be sure.
    o = bpy.context.active_object
    
    va = Vector((outer_points[0][0]))
    vb = point
    vc = Vector((outer_points[0][1]))
    vd = Vector((outer_points[1][0]))
    ve = Vector((outer_points[1][1]))

    o.data.vertices.add(5)
    o.data.vertices[vert_count].co = va 
    o.data.vertices[vert_count+1].co = vb 
    o.data.vertices[vert_count+2].co = vc
    o.data.vertices[vert_count+3].co = vd
    o.data.vertices[vert_count+4].co = ve

    oe = o.data.edges
    
    oe.add(4)  
    oe[edge_count].vertices = [vert_count,vert_count+1]
    oe[edge_count+1].vertices = [vert_count+2,vert_count+1]
    oe[edge_count+2].vertices = [vert_count+3,vert_count+1]
    oe[edge_count+3].vertices = [vert_count+4,vert_count+1]


def runCleanUp():
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.remove_doubles(limit=0.0001)
    
    #unselect all
    bpy.ops.mesh.select_all(action='TOGGLE')    

def getMeshMatrix(obj):
            
    is_editmode = (obj.mode == 'EDIT')
    if is_editmode:
       bpy.ops.object.mode_set(mode='OBJECT')

    edges = []
    mesh = obj.data
    verts = mesh.vertices

    for e in mesh.edges:
        if e.select:
            edges.append(e)

    meshMatrix = []

    edgenum = 0
    for edge_to_test in edges:
        p1 = verts[edge_to_test.vertices[0]].co 
        p2 = verts[edge_to_test.vertices[1]].co
        meshMatrix.append([(p1.x,p1.y,p1.z),(p2.x,p2.y,p2.z)])
        edgenum += 1

    return meshMatrix


def getVertEdgeCount():
    
    bpy.ops.object.mode_set(mode='OBJECT')

    vert_count = bpy.context.active_object.data.vertices
    edge_count = bpy.context.active_object.data.edges

    return (vert_count, edge_count)

def selectNewGeometry():
    
    # potentially this is where i maybe go back to edit mode and select
    # the newly added edges.
        
    return


def initScript(context, self):
    
    obj = bpy.context.active_object

    meshMatrix = getMeshMatrix(obj)
    (vert_count, edge_count) = getVertEdgeCount()

    ## force edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    vSel = bpy.context.active_object.data.total_vert_sel
    xv = len(vert_count)
    xe = len(edge_count)


    if len(meshMatrix) != 2:
        print(str(len(meshMatrix)) +" select, make sure (only) 2 are selected")
    else:
        
        ''' debug prints
        print("begin--------------------")
        print("the object has " + str(xv) + " verts")
        print("currently " + str(vSel) + " verts are selected")
        print("the object has " + str(xe) + " edges")
        print("currently " + str(len(meshMatrix)) + " edges are selected")
        print("--------------------end")
        '''
        
        if checkEdges(meshMatrix, obj) == None:
            print("lines dont intersect")
        else: 
            makeGeometry(checkEdges(meshMatrix, obj),meshMatrix)
            runCleanUp()
            # selectNewGeometry()
            

    
class SliceIntersectingEdges(bpy.types.Operator):
    '''Finds visible intersection, existing or projected through extrapolation, creates new edges'''
    
    bl_idname = "Slice at Intersection"
    bl_label = "Slice Intersect"

    @classmethod
    def poll(self, context):
        obj = context.active_object
        return obj != None and obj.type == 'MESH'

    def execute(self, context):
        initScript(context, self)
        return {'FINISHED'}


menu_func = (lambda self,
            context: self.layout.operator(SliceIntersectingEdges.bl_idname,
            text="Slice at Edge Intersection"))

def register():
    bpy.types.VIEW3D_MT_edit_mesh_specials.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)

if __name__ == "__main__":
    register()