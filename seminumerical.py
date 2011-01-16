# -*- coding: utf-8 -*-
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

'''
    Common stuff for my addons...


  --- pre shipment with Cursor Contol 0.4.1 -----------------------------------------------------------------------------------
    2011-01-09 - Support for Blender 2.56a

  --- pre shipment with Cursor Contol 0.4.0 -----------------------------------------------------------------------------------
    2010-11-15 - Support for Blender 2.55b
    2010-10-10 - Refactored drawButton into utility class GUI
    2010-09-27 - Some refactoring
                 Bundled methods in classes
                 Renamed some methods



    TODO:
        Make up nifty version handling... or require all addons to update when this module changes...


'''


import bpy
from mathutils import Vector, Matrix
from mathutils import geometry

      

class BlenderFake:

    @classmethod
    def forceUpdate(cls):
        if bpy.context.mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')

    @classmethod
    def forceRedraw(cls):
        CursorAccess.setCursor(CursorAccess.getCursor())



class CursorAccess:

    @classmethod
    def findSpace(cls):
        area = None
        for area in bpy.data.window_managers[0].windows[0].screen.areas:
            if area.type == 'VIEW_3D':
                break
        if area.type != 'VIEW_3D':
            return None
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                break
        if space.type != 'VIEW_3D':
            return None
        return space

    @classmethod
    def setCursor(cls,coordinates):
        spc = cls.findSpace()
        spc.cursor_location = coordinates

    @classmethod
    def getCursor(cls):
        spc = cls.findSpace()
        return spc.cursor_location



# Modify mesh data
class MeshEditor:

    @classmethod
    def addVertex(cls, v):
        toggle = False
        if bpy.context.mode == 'EDIT_MESH':
            toggle = True
        if toggle:
            bpy.ops.object.editmode_toggle()
        mesh = bpy.context.active_object.data
        mesh.add_geometry (1, 0, 0)
        vi = len (mesh.vertices) - 1
        mesh.vertices[vi].co = v
        mesh.update()
        if toggle:
            bpy.ops.object.editmode_toggle()
        return vi
        
    @classmethod
    def addEdge(cls, vi1, vi2):
        toggle = False
        if bpy.context.mode == 'EDIT_MESH':
            toggle = True
        if toggle:
            bpy.ops.object.editmode_toggle()
        mesh = bpy.context.active_object.data
        mesh.add_geometry (0, 1, 0)
        ei = len (mesh.edges) - 1
        e = mesh.edges[ei]
        e.vertices[0] = vi1;
        e.vertices[1] = vi2;
        mesh.update()
        if toggle:
            bpy.ops.object.editmode_toggle()
        return ei



class GUI:

    @classmethod
    def drawButton(cls, enabled, layout, iconName, operator, frame=True):
        col = layout.column()
        col.enabled = enabled
        bt = col.operator(operator,
            text='',
            icon=iconName,
            emboss=frame)



# 3D Geometry
class G3:

    @classmethod
    def distanceP2P(cls, p1, p2):
        return (p1-p2).length

    @classmethod
    def closestP2L(cls, p, l1, l2):
        vA = p - l1
        vL = l2- l1
        vL.normalize()
        return vL * (vL.dot(vA)) + l1

    @classmethod
    def closestP2E(cls, p, e1, e2):
        q = G3.closestP2L(p, e1, e2)
        de = G3.distanceP2P(e1, e2)
        d1 = G3.distanceP2P(q, e1)
        d2 = G3.distanceP2P(q, e2)
        if d1>de and d1>d2:
            q = e2
        if d2>de and d2>d1:
            q = e1
        return q

    @classmethod
    def heightP2S(cls, p, sO, sN):
        return (p-sO).dot(sN) / sN.dot(sN)

    @classmethod
    def closestP2S(cls, p, sO, sN):
        k = - G3.heightP2S(p, sO, sN)
        q = p+sN*k
        return q

    @classmethod
    def closestP2F(cls, p, fv, sN):
        q = G3.closestP2S(p, fv[0], sN)
        #pi = MeshEditor.addVertex(p)
        #qi = MeshEditor.addVertex(q)
        #MeshEditor.addEdge(pi, qi)
        #print ([d0,d1,d2])
        
        if len(fv)==3:
            h = G3.closestP2L(fv[0], fv[1], fv[2])
            d = (fv[0]-h).dot(q-h)
            if d<=0:
                return G3.closestP2E(q, fv[1], fv[2])
            h = G3.closestP2L(fv[1], fv[2], fv[0])
            d = (fv[1]-h).dot(q-h)
            if d<=0:
                return G3.closestP2E(q, fv[2], fv[0])
            h = G3.closestP2L(fv[2], fv[0], fv[1])
            d = (fv[2]-h).dot(q-h)
            if d<=0:
                return G3.closestP2E(q, fv[0], fv[1])
            return q
        if len(fv)==4:
            h = G3.closestP2L(fv[0], fv[1], fv[2])
            d = (fv[0]-h).dot(q-h)
            if d<=0:
                return G3.closestP2E(q, fv[1], fv[2])
            h = G3.closestP2L(fv[1], fv[2], fv[3])
            d = (fv[1]-h).dot(q-h)
            if d<=0:
                return G3.closestP2E(q, fv[2], fv[3])
            h = G3.closestP2L(fv[2], fv[3], fv[0])
            d = (fv[2]-h).dot(q-h)
            if d<=0:
                return G3.closestP2E(q, fv[3], fv[0])
            h = G3.closestP2L(fv[3], fv[0], fv[1])
            d = (fv[3]-h).dot(q-h)
            if d<=0:
                return G3.closestP2E(q, fv[0], fv[1])
            return q

    @classmethod
    def medianTriangle(cls, vv):
        m0 = (vv[1]+vv[2])/2
        m1 = (vv[0]+vv[2])/2
        m2 = (vv[0]+vv[1])/2
        return [m0, m1, m2]

    @classmethod
    def orthoCenter(cls, fv):
        h0 = G3.closestP2L(fv[0], fv[1], fv[2])
        h1 = G3.closestP2L(fv[1], fv[0], fv[2])
        #h2 = G3.closestP2L(fm[2], fm[0], fm[1])
        return geometry.intersect_line_line (fv[0], h0, fv[1], h1)[0]

    @classmethod
    def circumCenter(cls, fv):
        fm = G3.medianTriangle(fv)
        return G3.orthoCenter(fm)

    @classmethod
    def ThreePnormal(cls, fv):
        return (fv[1]-fv[0]).cross(fv[2]-fv[0]).normalize()

    @classmethod
    def closestP2CylinderAxis(cls, p, fv):
        n = G3.ThreePnormal(fv)
        c = G3.circumCenter(fv)
        return G3.closestP2L(p, c, c+n)

    @classmethod
    def closestP2Sphere(cls, p, fv):
        #print ("G3.closestP2Sphere")
        c = G3.circumCenter(fv)
        pc = p-c
        if pc.length == 0:
            pc = pc + Vector((1,0,0))
        return c + (pc.normalize() * G3.distanceP2P(c, fv[0]))

    @classmethod
    def closestP2Sphere4(cls, p, fv4):
        #print ("G3.closestP2Sphere")
        fv = [fv4[0],fv4[1],fv4[2]]
        c1 = G3.circumCenter(fv)
        n1 = G3.ThreePnormal(fv)
        fv = [fv4[1],fv4[2],fv4[3]]
        c2 = G3.circumCenter(fv)
        n2 = G3.ThreePnormal(fv)
        d1 = c1+n1
        d2 = c2+n2
        c = geometry.intersect_line_line (c1, d1, c2, d2)[0]
        pc = p-c
        if pc.length == 0:
            pc = pc + Vector((1,0,0))
        return c + (pc.normalize() * G3.distanceP2P(c, fv[0]))



# Converts 3D coordinates in a 3DRegion
# into 2D screen coordinates for that region.
# Borrowed from Buerbaum Martin (Pontiac)
def region3d_get_2d_coordinates(context, loc_3d):
    # Get screen information
    mid_x = context.region.width / 2.0
    mid_y = context.region.height / 2.0
    width = context.region.width
    height = context.region.height

    # Get matrices
    view_mat = context.space_data.region_3d.perspective_matrix
    total_mat = view_mat

    # order is important
    vec = Vector((loc_3d[0], loc_3d[1], loc_3d[2], 1.0)) * total_mat

    # dehomogenise
    vec = Vector((
        vec[0] / vec[3],
        vec[1] / vec[3],
        vec[2] / vec[3]))

    x = int(mid_x + vec[0] * width / 2.0)
    y = int(mid_y + vec[1] * height / 2.0)
    z = vec[2]

    return Vector((x, y, z))
