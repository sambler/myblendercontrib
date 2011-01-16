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

"""
  TODO:
      LATER:
          Coordinate reference euclidean and polar...
          Guides... (separate panel?)
          Wiki Page: http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/3D_interaction
          Blender SVN upload...

      ISSUES:
          

      QUESTIONS:
          cc_orthoCenter()
              ?Will precision improve if all six possible results are averaged?

  --- pre 0.4.1 -----------------------------------------------------------------------------------
  2011-01-09 - Support for Blender 2.56b
  --- pre 0.4 -----------------------------------------------------------------------------------
  2010-11-15 - Support for Blender 2.55b
  2010-10-28 - Added Cursor Location to the panel
  2010-10-10 - Refactored drawButton into utility class seminumerical.GUI
  2010-10-06 - Desaturated color of SL-cursor
  2010-10-02 - SL is now drawn as a dimmed replica of 3D-cursor 
  2010-10-02 - Four point sphere.
  2010-09-27 - Some cleanup and refactoring.
               Gathered all properties in a single structure (CursorControlData).
               Updates due to refactoring of the seminumerical module
  2010-09-15 - Default value of view3d_cursor_linex_choice is now -1
               Improved some operator descriptions.
               Changed bl_addon_info.name
  --- pre 0.3 -----------------------------------------------------------------------------------
  2010-09-15 - Closest point on 3-point sphere
               Fixed bug in cc_closestP2F. It now works as intended on quad faces.
               Changed 'circum center' to the more generic 'closest point on cylinder axis'
               SL is nolonger destroyed by cursor_to_linex
               Changed some icons in the UI
  --- pre 0.2.1 -----------------------------------------------------------------------------------
  2010-09-14 - Support for Blender 2.54b
  --- pre 0.2.0 -----------------------------------------------------------------------------------
  2010-09-14 - Fixed bug in cursor_to_face
  2010-09-13 - Triangle circumcenter (3-point circle center)
               View now updates when enable/disable draw is clicked
               Expand / contract SL properties.
  2010-09-12 - Fixed enable/disable buttons
               Move to closest vertex/line/edge/plane/face
               UI redesigned
  2010-09-11 - Local view now works like a charm
  --- pre 0.1.0 -----------------------------------------------------------------------------------
  2010-09-06 - Force update callback was interfering with undo.
               Thankfully the verts, edge and face select-count updates as it should,
               so I was able to read get the necessary information from there.
               Forced update is now done inside the operators where mesh data is accessed.
  2010-09-05 - Force update for edit mode is now working.
               Thanks to Buerbaum Martin (Pontiac). I peeked a bit at his code for registering a callback...
"""

# Blender Add-Ons menu registration (in User Prefs)
bl_addon_info = {
    'name': 'Cursor Control',
    'author': 'Morgan Mörtsell (Seminumerical)',
    'version': (0, 4, 1),
    'blender': (2, 5, 6),
    'api': 34074,
    'location': 'View3D > Properties > Cursor',
    'description': 'Control the Cursor',
    'warning': '', # used for warning icon and text in addons panel
    'wiki_url': '',
    'tracker_url': '',
    'category': '3D View'}



import bpy
from mathutils import Vector, Matrix
import bgl
from mathutils import geometry
from seminumerical import *
import math

PHI = 1.61803398874989484820
PHI_INV = 1/PHI


# Precision for display of float values.
PRECISION = 4

class CursorControlData(bpy.types.IDPropertyGroup):
    # SL Location
    savedLocation = bpy.props.FloatVectorProperty(name="",description="Saved Location",precision=PRECISION)
    # Define property for the draw setting.
    savedLocationDraw = bpy.props.BoolProperty(description="Draw SL cursor in 3D view",default=1)
    # Define property for the expand SL setting.
    savedLocationExpand = bpy.props.BoolProperty(description="Expand SL properties in UI",default=1)
    cursorLocationExpand = bpy.props.BoolProperty(description="Expand cursor property in UI",default=1)
    # Property for linex result select...
    linexChoice = bpy.props.IntProperty(name="",default=-1)

    # UI Utils
    def hideLinexChoice(self):
        self.linexChoice = -1

    def cycleLinexCoice(self,limit):
        qc = self.linexChoice + 1
        if qc<0:
            qc = 1
        if qc>=limit:
            qc = 0
        self.linexChoice = qc


class VIEW3D_OT_cursor_to_origin(bpy.types.Operator):
    '''Move to world origin.'''
    bl_idname = "view3d.cursor_to_origin"
    bl_label = "Move to world origin."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        CursorAccess.setCursor([0,0,0])
        return {'FINISHED'}


class VIEW3D_OT_cursor_to_active_object_center(bpy.types.Operator):
    '''Move to active object origin.'''
    bl_idname = "view3d.cursor_to_active_object_center"
    bl_label = "Move to active object origin."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        CursorAccess.setCursor(context.active_object.location)
        return {'FINISHED'}


#class VIEW3D_OT_cursor_to_nearest_object(bpy.types.Operator):
    #'''Move to center of nearest object.'''
    #bl_idname = "view3d.cursor_to_nearest_object"
    #bl_label = "Move to center of nearest object."
    #bl_options = {'REGISTER'}

    #def modal(self, context, event):
        #return {'FINISHED'}

    #def execute(self, context):
        #CursorAccess.setCursor(context.active_object.location)
        #return {'FINISHED'}


#class VIEW3D_OT_cursor_to_selection_midpoint(bpy.types.Operator):
    #'''Move to active objects median.'''
    #bl_idname = "view3d.cursor_to_selection_midpoint"
    #bl_label = "Move to active objects median."
    #bl_options = {'REGISTER'}

    #def modal(self, context, event):
        #return {'FINISHED'}

    #def execute(self, context):
        #location = Vector((0,0,0))
        #n = 0
        #for obj in context.selected_objects:
            #location = location + obj.location
            #n += 1
        #if (n==0):
            #return {'CANCELLED'}
        #location = location / n
        #CursorAccess.setCursor(location)
        #return {'FINISHED'}


class VIEW3D_OT_cursor_SL_save(bpy.types.Operator):
    '''Save cursor location.'''
    bl_idname = "view3d.cursor_SL_save"
    bl_label = "Save cursor location."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.savedLocation = CursorAccess.getCursor()
        # This is a workaround to trigger a callback
        CursorAccess.setCursor(cc.savedLocation)
        return {'FINISHED'}


class VIEW3D_OT_cursor_SL_swap(bpy.types.Operator):
    '''Swap cursor location.'''
    bl_idname = "view3d.cursor_SL_swap"
    bl_label = "Swap cursor location."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        location = CursorAccess.getCursor().copy()
        cc = context.scene.cursor_control
        CursorAccess.setCursor(cc.savedLocation)
        cc.savedLocation = location
        return {'FINISHED'}


class VIEW3D_OT_cursor_SL_recall(bpy.types.Operator):
    '''Recall cursor location.'''
    bl_idname = "view3d.cursor_SL_recall"
    bl_label = "Recall cursor location."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        CursorAccess.setCursor(cc.savedLocation)
        return {'FINISHED'}


class VIEW3D_OT_cursor_to_SL_mirror(bpy.types.Operator):
    '''Mirror cursor around SL or selection.'''
    bl_idname = "view3d.cursor_to_SL_mirror"
    bl_label = "Mirror cursor around SL or selection."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def mirror(self, p):
        v = p - Vector(CursorAccess.getCursor())
        CursorAccess.setCursor(p + v)

    def execute(self, context):
        BlenderFake.forceUpdate()
        obj = context.active_object
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        
        if obj==None or obj.data.total_vert_sel==0:
            self.mirror(Vector(cc.savedLocation))
            return {'FINISHED'}

        mat = obj.matrix_world

        if obj.data.total_vert_sel==1:
            sf = [f for f in obj.data.vertices if f.select == 1]
            self.mirror(Vector(sf[0].co)*mat)
            return {'FINISHED'}

        mati = mat.copy().invert()      
        c = Vector(CursorAccess.getCursor())*mati

        if obj.data.total_vert_sel==2:
            sf = [f for f in obj.data.vertices if f.select == 1]
            p = G3.closestP2L(c, Vector(sf[0].co), Vector(sf[1].co))
            self.mirror(p*mat)
            return {'FINISHED'}
            
        if obj.data.total_vert_sel==3 or obj.data.total_face_sel==1:
            sf = [f for f in obj.data.vertices if f.select == 1]
            v0 = Vector(sf[0].co)
            v1 = Vector(sf[1].co)
            v2 = Vector(sf[2].co)
            normal = (v1-v0).cross(v2-v0)
            normal.normalize();            
            p = G3.closestP2S(c, v0, normal)
            self.mirror(p*mat)
            return {'FINISHED'}
              
        return {'CANCELLED'}


class VIEW3D_OT_cursor_to_vertex(bpy.types.Operator):
    '''Move to closest vertex.'''
    bl_idname = "view3d.cursor_to_vertex"
    bl_label = "Move to closest vertex."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        BlenderFake.forceUpdate()
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        obj = context.active_object
        mat = obj.matrix_world
        mati = mat.copy().invert()
        vs = obj.data.vertices
        c = Vector(CursorAccess.getCursor())*mati
        v = None
        d = -1
        for vv in vs:
            if not vv.select:
                continue
            w = Vector(vv.co)
            dd = G3.distanceP2P(c, w)
            if d<0 or dd<d:
                v = w
                d = dd
        if v==None:
            return
        CursorAccess.setCursor(v*mat)
        return {'FINISHED'}


class VIEW3D_OT_cursor_to_line(bpy.types.Operator):
    '''Move to closest point on line.'''
    bl_idname = "view3d.cursor_to_line"
    bl_label = "Move to closest point on line."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        BlenderFake.forceUpdate()
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        obj = bpy.context.active_object
        mat = obj.matrix_world
        if obj.data.total_vert_sel==2:
            sf = [f for f in obj.data.vertices if f.select == 1]
            p = CursorAccess.getCursor()
            v0 = sf[0].co*mat
            v1 = sf[1].co*mat
            q = G3.closestP2L(p, v0, v1)
            CursorAccess.setCursor(q)
            return {'FINISHED'}
        if obj.data.total_edge_sel<2:
            return {'CANCELLED'}
        mati = mat.copy().invert()
        c = Vector(CursorAccess.getCursor())*mati
        q = None
        d = -1
        for ee in obj.data.edges:
            if not ee.select:
                continue
            e1 = Vector(obj.data.vertices[ee.vertices[0]].co)
            e2 = Vector(obj.data.vertices[ee.vertices[1]].co)
            qq = G3.closestP2L(c, e1, e2)
            dd = G3.distanceP2P(c, qq)
            if d<0 or dd<d:
                q = qq
                d = dd
        if q==None:
            return {'CANCELLED'}
        CursorAccess.setCursor(q*mat)
        return {'FINISHED'}


class VIEW3D_OT_cursor_to_edge(bpy.types.Operator):
    '''Move to closest point on edge.'''
    bl_idname = "view3d.cursor_to_edge"
    bl_label = "Move to closest point on edge."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        BlenderFake.forceUpdate()
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        obj = bpy.context.active_object
        mat = obj.matrix_world
        if obj.data.total_vert_sel==2:
            sf = [f for f in obj.data.vertices if f.select == 1]
            p = CursorAccess.getCursor()
            v0 = sf[0].co*mat
            v1 = sf[1].co*mat
            q = G3.closestP2E(p, v0, v1)
            CursorAccess.setCursor(q)
            return {'FINISHED'}
        if obj.data.total_edge_sel<2:
            return {'CANCELLED'}
        mati = mat.copy().invert()
        c = Vector(CursorAccess.getCursor())*mati
        q = None
        d = -1
        for ee in obj.data.edges:
            if not ee.select:
                continue
            e1 = Vector(obj.data.vertices[ee.vertices[0]].co)
            e2 = Vector(obj.data.vertices[ee.vertices[1]].co)
            qq = G3.closestP2E(c, e1, e2)
            dd = G3.distanceP2P(c, qq)
            if d<0 or dd<d:
                q = qq
                d = dd
        if q==None:
            return {'CANCELLED'}
        CursorAccess.setCursor(q*mat)
        return {'FINISHED'}


class VIEW3D_OT_cursor_to_plane(bpy.types.Operator):
    '''Move to closest point on a plane.'''
    bl_idname = "view3d.cursor_to_plane"
    bl_label = "Move to closest point on a plane"
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        BlenderFake.forceUpdate()
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        obj = bpy.context.active_object
        mesh = obj.data.vertices
        mat = obj.matrix_world
        if obj.data.total_vert_sel==3:
            sf = [f for f in obj.data.vertices if f.select == 1]
            v0 = Vector(sf[0].co)
            v1 = Vector(sf[1].co)
            v2 = Vector(sf[2].co)
            normal = (v1-v0).cross(v2-v0)
            normal.normalize();
            p = CursorAccess.getCursor()
            n = normal*mat-obj.location
            v = v0*mat
            k = - (p-v).dot(n) / n.dot(n)
            q = p+n*k
            CursorAccess.setCursor(q)
            return {'FINISHED'}

        mati = mat.copy().invert()
        c = Vector(CursorAccess.getCursor())*mati
        q = None
        d = -1
        for ff in obj.data.faces:
            if not ff.select:
                continue
            qq = G3.closestP2S(c, Vector(obj.data.vertices[ff.vertices[0]].co), ff.normal)
            dd = G3.distanceP2P(c, qq)
            if d<0 or dd<d:
                q = qq
                d = dd
        if q==None:
            return {'CANCELLED'}
        CursorAccess.setCursor(q*mat)
        return {'FINISHED'}


class VIEW3D_OT_cursor_to_face(bpy.types.Operator):
    '''Move to closest point on a face.'''
    bl_idname = "view3d.cursor_to_face"
    bl_label = "Move to closest point on a face"
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        BlenderFake.forceUpdate()
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        obj = bpy.context.active_object
        mesh = obj.data.vertices
        mat = obj.matrix_world
        mati = mat.copy().invert()
        c = Vector(CursorAccess.getCursor())*mati
        if obj.data.total_vert_sel==3:
            sf = [f for f in obj.data.vertices if f.select == 1]
            v0 = Vector(sf[0].co)
            v1 = Vector(sf[1].co)
            v2 = Vector(sf[2].co)
            fv = [v0, v1, v2]
            normal = (v1-v0).cross(v2-v0)
            normal.normalize();
            q = G3.closestP2F(c, fv, normal)
            CursorAccess.setCursor(q*mat)
            return {'FINISHED'}

        #visual = True

        qqq = []
        q = None
        d = -1
        for ff in obj.data.faces:
            if not ff.select:
                continue
            fv=[]
            for vi in ff.vertices:
                fv.append(Vector(obj.data.vertices[vi].co))
            qq = G3.closestP2F(c, fv, ff.normal)
            #if visual:
                #qqq.append(qq)
            dd = G3.distanceP2P(c, qq)
            if d<0 or dd<d:
                q = qq
                d = dd
        if q==None:
            return {'CANCELLED'}

        #if visual:
            #ci = MeshEditor.addVertex(c)
            #for qq in qqq:
                #qqi = MeshEditor.addVertex(qq)
                #MeshEditor.addEdge(ci, qqi)

        CursorAccess.setCursor(q*mat)
        return {'FINISHED'}


class VIEW3D_OT_cursor_to_vertex_median(bpy.types.Operator):
    '''Move to median of vertices.'''
    bl_idname = "view3d.cursor_to_vertex_median"
    bl_label = "Move to median of vertices."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        BlenderFake.forceUpdate()
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        obj = context.active_object
        mat = obj.matrix_world
        vs = obj.data.vertices
        selv = [v for v in vs if v.select == 1]
        location = Vector((0,0,0))
        for v in selv:
            location = location + v.co
        n = len(selv)
        if (n==0):
            return {'CANCELLED'}
        location = location / n
        CursorAccess.setCursor(location*mat)
        return {'FINISHED'}


class VIEW3D_OT_cursor_to_linex(bpy.types.Operator):
    '''Alternate between closest encounter points of two lines.'''
    bl_idname = "view3d.cursor_to_linex"
    bl_label = "Alternate between to closest encounter points of two lines."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        BlenderFake.forceUpdate()
        obj = bpy.context.active_object
        mat = obj.matrix_world

        se = [e for e in obj.data.edges if (e.select == 1)]
        e1v1 = obj.data.vertices[se[0].vertices[0]].co
        e1v2 = obj.data.vertices[se[0].vertices[1]].co
        e2v1 = obj.data.vertices[se[1].vertices[0]].co
        e2v2 = obj.data.vertices[se[1].vertices[1]].co

        qq = geometry.intersect_line_line (e1v1, e1v2, e2v1, e2v2)

        q = None
        if len(qq)==0:
            #print ("lx 0")
            return {'CANCELLED'}

        if len(qq)==1:
            #print ("lx 1")
            q = qq[0]
        
        if len(qq)==2:
            cc = context.scene.cursor_control
            cc.cycleLinexCoice(2)
            q = qq[cc.linexChoice]

        #q = geometry.intersect_line_line (e1v1, e1v2, e2v1, e2v2)[qc] * mat
        #i2 = geometry.intersect_line_line (e2v1, e2v2, e1v1, e1v2)[0] * mat
        CursorAccess.setCursor(q*mat)
        return {'FINISHED'}


class VIEW3D_OT_cursor_to_cylinderaxis(bpy.types.Operator):
    '''Move to closest point on cylinder axis.'''
    bl_idname = "view3d.cursor_to_cylinderaxis"
    bl_label = "Move to closest point on cylinder axis."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        BlenderFake.forceUpdate()
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        obj = bpy.context.active_object
        mesh = obj.data.vertices
        mat = obj.matrix_world
        mati = mat.copy().invert()
        c = Vector(CursorAccess.getCursor())*mati

        sf = [f for f in obj.data.vertices if f.select == 1]
        v0 = Vector(sf[0].co)
        v1 = Vector(sf[1].co)
        v2 = Vector(sf[2].co)
        fv = [v0, v1, v2]
        q = G3.closestP2CylinderAxis(c, fv)
        CursorAccess.setCursor(q*mat)
        return {'FINISHED'}     


class VIEW3D_OT_cursor_to_sphere(bpy.types.Operator):
    '''Move to closest point on surface of sphere.'''
    bl_idname = "view3d.cursor_to_sphere"
    bl_label = "Move to closest point on surface of sphere."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        BlenderFake.forceUpdate()
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        obj = bpy.context.active_object
        mesh = obj.data.vertices
        mat = obj.matrix_world
        mati = mat.copy().invert()
        c = Vector(CursorAccess.getCursor())*mati

        if obj.data.total_vert_sel==3:
            sf = [f for f in obj.data.vertices if f.select == 1]
            v0 = Vector(sf[0].co)
            v1 = Vector(sf[1].co)
            v2 = Vector(sf[2].co)
            fv = [v0, v1, v2]
            q = G3.closestP2Sphere(c, fv)
            CursorAccess.setCursor(q*mat)
            return {'FINISHED'}
        if obj.data.total_vert_sel==4:
            sf = [f for f in obj.data.vertices if f.select == 1]
            v0 = Vector(sf[0].co)
            v1 = Vector(sf[1].co)
            v2 = Vector(sf[2].co)
            v3 = Vector(sf[3].co)
            fv = [v0, v1, v2, v3]
            q = G3.closestP2Sphere4(c, fv)
            CursorAccess.setCursor(q*mat)
            return {'FINISHED'}
        return {'CANCELLED'}



class VIEW3D_OT_cursor_draw_enable(bpy.types.Operator):
    '''Enable SL draw.'''
    bl_idname = "view3d.cursor_draw_enable"
    bl_label = "Enable SL draw."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.savedLocationDraw = True
        BlenderFake.forceRedraw()
        return {'FINISHED'}


class VIEW3D_OT_cursor_draw_disable(bpy.types.Operator):
    '''Disable SL draw.'''
    bl_idname = "view3d.cursor_draw_disable"
    bl_label = "Disable SL draw."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.savedLocationDraw = False
        BlenderFake.forceRedraw()
        return {'FINISHED'}


class VIEW3D_OT_cursor_SL_expand(bpy.types.Operator):
    '''Expand SL properties.'''
    bl_idname = "view3d.cursor_SL_expand"
    bl_label = "Expand SL properties."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.savedLocationExpand = True
        return {'FINISHED'}


class VIEW3D_OT_cursor_SL_contract(bpy.types.Operator):
    '''Contract SL properties.'''
    bl_idname = "view3d.cursor_SL_contract"
    bl_label = "Contract SL properties."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.savedLocationExpand = False
        return {'FINISHED'}


class VIEW3D_OT_cursor_CL_expand(bpy.types.Operator):
    '''Expand SL properties.'''
    bl_idname = "view3d.cursor_CL_expand"
    bl_label = "Expand SL properties."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.cursorLocationExpand = True
        return {'FINISHED'}


class VIEW3D_OT_cursor_CL_contract(bpy.types.Operator):
    '''Contract SL properties.'''
    bl_idname = "view3d.cursor_CL_contract"
    bl_label = "Contract SL properties."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.cursorLocationExpand = False
        return {'FINISHED'}


class VIEW3D_PT_cursor(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Cursor Control"
    bl_default_closed = True

    @classmethod
    def poll(self, context):
        # Display in object or edit mode.
        if (context.area.type == 'VIEW_3D' and
            (context.mode == 'EDIT_MESH'
            or context.mode == 'OBJECT')):
            return 1

        return 0

    def draw_header(self, context):
        layout = self.layout
        cc = context.scene.cursor_control
 
        #layout.prop(sce, "cursor_control.savedLocationDraw")
        if cc.savedLocationDraw:
            GUI.drawButton(True, layout, 'RESTRICT_VIEW_OFF', "view3d.cursor_draw_disable", False)
        else:
            GUI.drawButton(True, layout, 'RESTRICT_VIEW_ON' , "view3d.cursor_draw_enable", False)

    def draw(self, context):
        layout = self.layout
        sce = context.scene

        tvs = 0
        tes = 0
        tfs = 0
        obj = context.active_object
        if (context.mode == 'EDIT_MESH'):
            if (obj and obj.type=='MESH' and obj.data):
                tvs = obj.data.total_vert_sel
                tes = obj.data.total_edge_sel
                tfs = obj.data.total_face_sel

        # Mesh data elements
        row = layout.row()
        GUI.drawButton(tvs>=1          , row, 'STICKY_UVS_DISABLE', "view3d.cursor_to_vertex")
        GUI.drawButton(tvs==2 or tes>=1, row, 'MESH_DATA'         , "view3d.cursor_to_line")
        GUI.drawButton(tvs==2 or tes>=1, row, 'OUTLINER_OB_MESH'  , "view3d.cursor_to_edge")
        GUI.drawButton(tvs==3 or tfs>=1, row, 'SNAP_FACE'         , "view3d.cursor_to_plane")
        GUI.drawButton(tvs==3 or tfs>=1, row, 'FACESEL'           , "view3d.cursor_to_face")

        # Geometry from mesh
        row = layout.row()
        GUI.drawButton(tvs<=3 or tfs==1 , row, 'MOD_MIRROR'  , "view3d.cursor_to_SL_mirror")
        GUI.drawButton(tes==2, row, 'PARTICLE_TIP', "view3d.cursor_to_linex")
        GUI.drawButton(tvs>1 , row, 'ROTATECENTER', "view3d.cursor_to_vertex_median")  #EDITMODE_HLT
        GUI.drawButton(tvs==3, row, 'FORCE_MAGNETIC'  , "view3d.cursor_to_cylinderaxis")
        GUI.drawButton(tvs==3 or tvs==4, row, 'MESH_UVSPHERE'  , "view3d.cursor_to_sphere")

        # Objects
        #row = layout.row()
        #GUI.drawButton(context.active_object!=None    , row, 'ROTATE'          , "view3d.cursor_to_active_object_center")
        #GUI.drawButton(len(context.selected_objects)>1, row, 'ROTATECOLLECTION', "view3d.cursor_to_selection_midpoint")
        #GUI.drawButton(len(context.selected_objects)>1, row, 'ROTATECENTER'    , "view3d.cursor_to_selection_midpoint")

        # References World Origin, Object Origin, SL and CS
        row = layout.row()
        GUI.drawButton(True                       , row, 'WORLD_DATA'    , "view3d.cursor_to_origin")
        GUI.drawButton(context.active_object!=None, row, 'ROTACTIVE'       , "view3d.cursor_to_active_object_center")
        GUI.drawButton(True                       , row, 'CURSOR'        , "view3d.cursor_SL_recall")
        #GUI.drawButton(True, row, 'GRID'          , "view3d.cursor_SL_recall")
        #GUI.drawButton(True, row, 'SNAP_INCREMENT', "view3d.cursor_SL_recall")
        #row.label("("+str(cc.linexChoice)+")")
        cc = context.scene.cursor_control
        if cc.linexChoice>=0:
            col = row.column()
            col.enabled = False
            col.prop(cc, "linexChoice")

        # SL Properties
        row = layout.row()
        if cc.savedLocationExpand:
            GUI.drawButton(True   , row, 'DISCLOSURE_TRI_DOWN_VEC'        , "view3d.cursor_SL_contract", False)
            row.label("Saved Location (SL)")

            row = layout.row()
            col = row.column()
            row2 = col.row()
            GUI.drawButton(True, row2, 'FORWARD', "view3d.cursor_SL_save")
            row2 = col.row()
            GUI.drawButton(True, row2, 'FILE_REFRESH', "view3d.cursor_SL_swap")
                #icon='ARROW_LEFTRIGHT')
            col = row.column()
            col.prop(cc, "savedLocation")
        else:
            GUI.drawButton(True   , row, 'DISCLOSURE_TRI_RIGHT_VEC'        , "view3d.cursor_SL_expand", False)
            row.label("Saved Location (SL)")

        # CL Properties
        row = layout.row()
        if cc.cursorLocationExpand:
            GUI.drawButton(True   , row, 'DISCLOSURE_TRI_DOWN_VEC'        , "view3d.cursor_CL_contract", False)
            row.label("Cursor Location (CL)")

            row = layout.row()
            col = row.column()
            col.prop(CursorAccess.findSpace(), "cursor_location")
        else:
            GUI.drawButton(True   , row, 'DISCLOSURE_TRI_RIGHT_VEC'        , "view3d.cursor_CL_expand", False)
            row.label("Cursor Location (CL)")

        #row = layout.row()
        #row.label("Coordinate System (CS)")
  
                

  
class VIEW3D_PT_cursor_init(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Register callback"
    bl_default_closed = True

    @classmethod
    def poll(cls, context):
        print ("Cursor Control draw-callback registration...")
        sce = context.scene
        if context.area.type == 'VIEW_3D':
            for reg in context.area.regions:
                if reg.type == 'WINDOW':
                    # Register callback for SL-draw
                    reg.callback_add(
                        cursor_draw_SL,
                        (cls,context),
                        'POST_PIXEL')
                    print ("Cursor Control draw-callback registered")
                    # Unregister to prevent double registration...
                    bpy.types.unregister(VIEW3D_PT_cursor_init)
        else:
            print("View3D not found, cannot run operator")
        return 0

    def draw_header(self, context):
        pass

    def draw(self, context):
        pass

def cursor_draw_SL(cls,context):
    cc = context.scene.cursor_control

    draw = 0
    if hasattr(cc, "savedLocationDraw"):
        draw = cc.savedLocationDraw

    if(draw):
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glShadeModel(bgl.GL_FLAT)
        p1 = Vector(cc.savedLocation)
        location = region3d_get_2d_coordinates(context, p1)
        alpha = 1-PHI_INV
        # Circle
        color = ([0.33, 0.33, 0.33],
            [1, 1, 1],
            [0.33, 0.33, 0.33],
            [1, 1, 1],
            [0.33, 0.33, 0.33],
            [1, 1, 1],
            [0.33, 0.33, 0.33],
            [1, 1, 1],
            [0.33, 0.33, 0.33],
            [1, 1, 1],
            [0.33, 0.33, 0.33],
            [1, 1, 1],
            [0.33, 0.33, 0.33],
            [1, 1, 1])
        offset = ([-4.480736161291701, -8.939966636005579],
            [-0.158097634992133, -9.998750178787843],
            [4.195854066857877, -9.077158622037636],
            [7.718765411993642, -6.357724476147943],
            [9.71288060283854, -2.379065025383466],
            [9.783240669628, 2.070797430975971],
            [7.915909938224691, 6.110513059466902],
            [4.480736161291671, 8.939966636005593],
            [0.15809763499209872, 9.998750178787843],
            [-4.195854066857908, 9.077158622037622],
            [-7.718765411993573, 6.357724476148025],
            [-9.712880602838549, 2.379065025383433],
            [-9.783240669627993, -2.070797430976005],
            [-7.915909938224757, -6.110513059466818])
        bgl.glBegin(bgl.GL_LINE_LOOP)
        for i in range(14):
            bgl.glColor4f(color[i][0], color[i][1], color[i][2], alpha)
            bgl.glVertex2f(location[0]+offset[i][0], location[1]+offset[i][1])
        bgl.glEnd()

        # Crosshair
        offset2 = 20
        offset = 5
        bgl.glColor4f(0, 0, 0, alpha)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(location[0]-offset2, location[1])
        bgl.glVertex2f(location[0]- offset, location[1])
        bgl.glEnd()
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(location[0]+ offset, location[1])
        bgl.glVertex2f(location[0]+offset2, location[1])
        bgl.glEnd()
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(location[0], location[1]-offset2)
        bgl.glVertex2f(location[0], location[1]- offset)
        bgl.glEnd()
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(location[0], location[1]+ offset)
        bgl.glVertex2f(location[0], location[1]+offset2)
        bgl.glEnd()

        
        
        

def register():
    # Register Cursor Control Structure
    bpy.types.Scene.cursor_control = bpy.props.PointerProperty(type=CursorControlData, name="")
        


def unregister():
    pass


if __name__ == "__main__":
    register()
