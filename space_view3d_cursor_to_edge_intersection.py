# cursor_to_edge_intersection.py Copyright (C) 2009-2010, Keith (Wahooney) Boshoff
# parts based on Paul Bourke's Shortest Line Between 2 lines
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

bl_addon_info = {
    'name': '3D View: Cursor to Edge Intersection',
    'author': 'Keith (Wahooney) Boshoff',
    'version': '1.0',
    'blender': (2, 5, 3),
    'location': 'Snap',
    'description': 'adds Snap cursor to edge intersect to cursor tools',
    'url': '',
    'category': '3D View'}

from mathutils import Vector, Matrix
import math
import bpy

def abs(val):
    if val > 0:
        return val
    return -val

def LineLineIntersect (p1, p2, p3, p4):
    # based on Paul Bourke's Shortest Line Between 2 lines
    
    min = 0.0000001
    
    v1 = Vector((p1.x - p3.x, p1.y - p3.y, p1.z - p3.z))
    v2 = Vector((p4.x - p3.x, p4.y - p3.y, p4.z - p3.z))
    
    if abs(v2.x) < min and abs(v2.y) < min and abs(v2.z)  < min:
        return None
        
    v3 = Vector((p2.x - p1.x, p2.y - p1.y, p2.z - p1.z))
    
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

    return [Vector((p1.x + mua * v3.x, p1.y + mua * v3.y, p1.z + mua * v3.z)), 
        Vector((p3.x + mub * v2.x, p3.y + mub * v2.y, p3.z + mub * v2.z))]

def edgeIntersect(context, operator):
    
    obj = context.active_object
    
    if (obj.type != "MESH"):
        operator.report({'ERROR'}, "Object must be a mesh")
        return None
    
    edges = [];
    mesh = obj.data
    verts = mesh.verts

    is_editmode = (obj.mode == 'EDIT')
    if is_editmode:
        bpy.ops.object.mode_set(mode='OBJECT')
    
    for e in mesh.edges:
        if e.select:
            edges.append(e)

    if is_editmode:
        bpy.ops.object.mode_set(mode='EDIT')
            
    if len(edges) != 2:
        operator.report({'ERROR'}, "Operator requires exactly 2 edges to be selected.")
        return
        
    line = LineLineIntersect(verts[edges[0].verts[0]].co, verts[edges[0].verts[1]].co, verts[edges[1].verts[0]].co, verts[edges[1].verts[1]].co)

    if (line == None):
        operator.report({'ERROR'}, "Selected edges are parallel.")
        return

    tm = obj.matrix_world.copy()
    point = ((line[0] + line[1]) / 2)
    point = tm * point

    context.scene.cursor_location = point
            
    return point
    
class CursorToEdgeIntersection(bpy.types.Operator):
    '''Finds the mid-point of the shortest distance between two edges, the point may not lie
    between the edges as the edges are projected beyond their bounds'''
    
    bl_idname = "view3d.snap_cursor_to_edge_intersection"
    bl_label = "Cursor to Edge Intersection"

    @staticmethod
    def poll(context):
        obj = context.active_object
        return obj != None and obj.type == 'MESH'

    def execute(self, context):
        edgeIntersect(context, self)
        return {'FINISHED'}


menu_func = (lambda self,
            context: self.layout.operator(CursorToEdgeIntersection.bl_idname,
            text="Cursor to Edge intersection"))

def register():
    bpy.types.VIEW3D_MT_snap.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_snap.append(menu_func)

if __name__ == "__main__":
    register()