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

      IDEAS:
          More saved locations... add, remove, lock, caption

      LATER:
          Wiki Page: http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/3D_interaction
          Blender SVN upload...

      ISSUES:
          Bugs:
          Mites:
            * History back button does not light up on first cursor move.
              It does light up on the second, or when mouse enters the tool-area
            * Switching between local and global view triggers new cursor position in history trace.
            * Each consecutive click on the linex operator triggers new cursor position in history trace.
                 (2011-01-16) Was not able to fix this because of some strange script behaviour
                              while trying to clear linexChoice from addHistoryLocation

      QUESTIONS:


  2011-01-16 - Small cleanup
               Step length added to Control panel
               Added move_to_SL to Control, and reworked SL_recall for Memory panel
               More changes due to refactoring in the seminumerical module
  2011-01-13 - Changes due to refactoring in the seminumerical module
               Changes due to bugfix in seminumerical module
               Bugfix: Mirror now correctly ignores additional vertices when a face is selected.
               Improved history tracker with back and forward buttons.
               Split addon into three panels (Control, Memory and History)
  2011-01-12 - Some buttons are now hidden in edit mode.
               Changed some icons
               Changed some operator names
               Refactored setCursor into the CursorControl class.
               A working version of the move-to-with-offset feature
               Changed the workings of move to center of cylinder and sphere.
               Changed the workings of move to perimeter of cylinder and sphere.
               Basic history tracker with undo working
  --- pre 0.4.1 -----------------------------------------------------------------------------------
  2011-01-09 - Support for Blender 2.56a
  --- pre 0.4 -----------------------------------------------------------------------------------
  2010-11-15 - Support for Blender 2.55b
  2010-10-28 - Added Cursor Location to the panel
  2010-10-10 - Refactored drawButton into utility class seminumerical.GUI
  2010-10-06 - Desaturated color of SL-cursor
  2010-10-02 - SL is now drawn as a dimmed replica of 3D-cursor 
               Four point sphere.
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
    'version': (0, 5, 0),
    'blender': (2, 5, 6),
    'api': 34074,
    'location': 'View3D > Properties > Cursor',
    'description': 'Control the Cursor',
    'warning': '', # used for warning icon and text in addons panel
    'wiki_url': 'http://blenderpythonscripts.wordpress.com/',
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
    savedLocationDraw = bpy.props.BoolProperty(description="Draw SL cursor in 3D view",default=1)
    savedLocation = bpy.props.FloatVectorProperty(name="",description="Saved Location",precision=PRECISION)
    # Step length properties
    stepLengthEnable = bpy.props.BoolProperty(name="Use step length",description="Use step length",default=0)
    stepLengthMode = bpy.props.EnumProperty(items=[
        ("Mode", "Mode", "Mode"),
        ("Absolute", "Absolute", "Absolute"),
        ("Proportional", "Proportional", "Proportional")],
        default="Proportional")
    stepLengthValue = bpy.props.FloatProperty(name="",precision=PRECISION,default=PHI)
    # Property for linex result select...
    linexChoice = bpy.props.IntProperty(name="",default=-1)
    # History tracker
    historyDraw = bpy.props.BoolProperty(description="Draw history trace in 3D view",default=1)
    historyDepth = 144
    historyWindow = 12
    historyPosition = [-1] # Integer must be in a list or else it can not be written to
    historyLocation = []
    #historySuppression = [False] # Boolean must be in a list or else it can not be written to

    def hideLinexChoice(self):
        self.linexChoice = -1

    def cycleLinexCoice(self,limit):
        qc = self.linexChoice + 1
        if qc<0:
            qc = 1
        if qc>=limit:
            qc = 0
        self.linexChoice = qc
  
    def setCursor(self,v):
        if self.stepLengthEnable:
            c = CursorAccess.getCursor()
            if((Vector(c)-Vector(v)).length>0):
                if self.stepLengthMode=='Absolute':
                    v = (Vector(v)-Vector(c)).normalize()*self.stepLengthValue + Vector(c)
                if self.stepLengthMode=='Proportional':
                    v = (Vector(v)-Vector(c))*self.stepLengthValue + Vector(c)
        CursorAccess.setCursor(Vector(v))

    def addHistoryLocation(self, l):
        if(self.historyPosition[0]==-1):
            self.historyLocation.append(l.copy())
            self.historyPosition[0]=0
            return
        if(l==self.historyLocation[self.historyPosition[0]]):
            return
        #if self.historySuppression[0]:
            #self.historyPosition[0] = self.historyPosition[0] - 1
        #else:
            #self.hideLinexChoice()
        while(len(self.historyLocation)>self.historyPosition[0]+1):
            self.historyLocation.pop(self.historyPosition[0]+1)
        #self.historySuppression[0] = False
        self.historyLocation.append(l.copy())
        if(len(self.historyLocation)>self.historyDepth):
            self.historyLocation.pop(0)
        self.historyPosition[0] = len(self.historyLocation)-1
        #print (self.historyLocation)

    #def enableHistorySuppression(self):
        #self.historySuppression[0] = True

    def previousLocation(self):
        if(self.historyPosition[0]<=0):
            return
        self.historyPosition[0] = self.historyPosition[0] - 1
        CursorAccess.setCursor(self.historyLocation[self.historyPosition[0]].copy())

    def nextLocation(self):
        if(self.historyPosition[0]<0):
            return
        if(self.historyPosition[0]+1==len(self.historyLocation)):
            return
        self.historyPosition[0] = self.historyPosition[0] + 1
        CursorAccess.setCursor(self.historyLocation[self.historyPosition[0]].copy())



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
        cc.setCursor([0,0,0])
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
        cc.setCursor(context.active_object.location)
        return {'FINISHED'}



#class VIEW3D_OT_cursor_to_nearest_object(bpy.types.Operator):
    #'''Move to center of nearest object.'''
    #bl_idname = "view3d.cursor_to_nearest_object"
    #bl_label = "Move to center of nearest object."
    #bl_options = {'REGISTER'}

    #def modal(self, context, event):
        #return {'FINISHED'}

    #def execute(self, context):
        #cc.setCursor(context.active_object.location)
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
        #cc.setCursor(location)
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



class VIEW3D_OT_cursor_previous(bpy.types.Operator):
    '''Previous cursor location.'''
    bl_idname = "view3d.cursor_previous"
    bl_label = "Previous cursor location."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        cc.previousLocation()
        return {'FINISHED'}



class VIEW3D_OT_cursor_next(bpy.types.Operator):
    '''Next cursor location.'''
    bl_idname = "view3d.cursor_next"
    bl_label = "Next cursor location."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        cc.nextLocation()
        return {'FINISHED'}



class VIEW3D_OT_cursor_to_SL(bpy.types.Operator):
    '''Move to saved location.'''
    bl_idname = "view3d.cursor_to_SL"
    bl_label = "Move to saved location."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        cc.setCursor(cc.savedLocation)
        return {'FINISHED'}



class VIEW3D_OT_cursor_to_SL_mirror(bpy.types.Operator):
    '''Mirror cursor around SL or selection.'''
    bl_idname = "view3d.cursor_to_SL_mirror"
    bl_label = "Mirror cursor around SL or selection."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def mirror(self, cc, p):
        v = p - Vector(CursorAccess.getCursor())
        cc.setCursor(p + v)

    def execute(self, context):
        BlenderFake.forceUpdate()
        obj = context.active_object
        cc = context.scene.cursor_control
        cc.hideLinexChoice()
        
        if obj==None or obj.data.total_vert_sel==0:
            self.mirror(cc, Vector(cc.savedLocation))
            return {'FINISHED'}

        mat = obj.matrix_world

        if obj.data.total_vert_sel==1:
            sf = [f for f in obj.data.vertices if f.select == 1]
            self.mirror(cc, Vector(sf[0].co)*mat)
            return {'FINISHED'}

        mati = mat.copy().invert()      
        c = Vector(CursorAccess.getCursor())*mati

        if obj.data.total_vert_sel==2:
            sf = [f for f in obj.data.vertices if f.select == 1]
            p = G3.closestP2L(c, Vector(sf[0].co), Vector(sf[1].co))
            self.mirror(cc, p*mat)
            return {'FINISHED'}
            
        if obj.data.total_vert_sel==3:
            sf = [f for f in obj.data.vertices if f.select == 1]
            v0 = Vector(sf[0].co)
            v1 = Vector(sf[1].co)
            v2 = Vector(sf[2].co)
            normal = (v1-v0).cross(v2-v0)
            normal.normalize();            
            p = G3.closestP2S(c, v0, normal)
            self.mirror(cc, p*mat)
            return {'FINISHED'}
              
        if obj.data.total_face_sel==1:
            sf = [f for f in obj.data.faces if f.select == 1]
            v0 = Vector(obj.data.vertices[sf[0].vertices[0]].co)
            v1 = Vector(obj.data.vertices[sf[0].vertices[1]].co)
            v2 = Vector(obj.data.vertices[sf[0].vertices[2]].co)
            normal = (v1-v0).cross(v2-v0)
            normal.normalize();            
            p = G3.closestP2S(c, v0, normal)
            self.mirror(cc, p*mat)
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
        cc.setCursor(v*mat)
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
            cc.setCursor(q)
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
        cc.setCursor(q*mat)
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
            cc.setCursor(q)
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
        cc.setCursor(q*mat)
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
            cc.setCursor(q)
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
        cc.setCursor(q*mat)
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
            cc.setCursor(q*mat)
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

        cc.setCursor(q*mat)
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
        cc.setCursor(location*mat)
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
            #cc.enableHistorySuppression()
            cc.cycleLinexCoice(2)
            q = qq[cc.linexChoice]

        #q = geometry.intersect_line_line (e1v1, e1v2, e2v1, e2v2)[qc] * mat
        #i2 = geometry.intersect_line_line (e2v1, e2v2, e1v1, e1v2)[0] * mat
        cc.setCursor(q*mat)
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
        if(q==None):
            return {'CANCELLED'}
        cc.setCursor(q*mat)
        return {'FINISHED'}     


class VIEW3D_OT_cursor_to_spherecenter(bpy.types.Operator):
    '''Move to center of cylinder or sphere.'''
    bl_idname = "view3d.cursor_to_spherecenter"
    bl_label = "Move to center of cylinder or sphere."
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
            q = G3.closestP2CylinderAxis(c, fv)
            #q = G3.centerOfSphere(fv)
            if(q==None):
                return {'CANCELLED'}
            cc.setCursor(q*mat)
            return {'FINISHED'}
        if obj.data.total_vert_sel==4:
            sf = [f for f in obj.data.vertices if f.select == 1]
            v0 = Vector(sf[0].co)
            v1 = Vector(sf[1].co)
            v2 = Vector(sf[2].co)
            v3 = Vector(sf[3].co)
            fv = [v0, v1, v2, v3]
            q = G3.centerOfSphere(fv)
            if(q==None):
                return {'CANCELLED'}
            cc.setCursor(q*mat)
            return {'FINISHED'}
        return {'CANCELLED'}



class VIEW3D_OT_cursor_to_perimeter(bpy.types.Operator):
    '''Move to perimeter of cylinder or sphere.'''
    bl_idname = "view3d.cursor_to_perimeter"
    bl_label = "Move to perimeter of cylinder or sphere."
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
            q = G3.closestP2Cylinder(c, fv)
            if(q==None):
                return {'CANCELLED'}
            #q = G3.centerOfSphere(fv)
            cc.setCursor(q*mat)
            return {'FINISHED'}
        if obj.data.total_vert_sel==4:
            sf = [f for f in obj.data.vertices if f.select == 1]
            v0 = Vector(sf[0].co)
            v1 = Vector(sf[1].co)
            v2 = Vector(sf[2].co)
            v3 = Vector(sf[3].co)
            fv = [v0, v1, v2, v3]
            q = G3.closestP2Sphere(c, fv)
            if(q==None):
                return {'CANCELLED'}
            cc.setCursor(q*mat)
            return {'FINISHED'}
        return {'CANCELLED'}



#class VIEW3D_OT_cursor_offset_from_radius(bpy.types.Operator):
    #'''Calculate offset from radius.'''
    #bl_idname = "view3d.cursor_offset_from_radius"
    #bl_label = "Calculate offset from radius."
    #bl_options = {'REGISTER'}

    #def modal(self, context, event):
        #return {'FINISHED'}

    #def execute(self, context):
        #BlenderFake.forceUpdate()
        #cc = context.scene.cursor_control
        #cc.hideLinexChoice()
        #obj = bpy.context.active_object
        #mesh = obj.data.vertices
        #mat = obj.matrix_world
        #mati = mat.copy().invert()
        #c = Vector(CursorAccess.getCursor())*mati

        #if obj.data.total_vert_sel==3:
            #sf = [f for f in obj.data.vertices if f.select == 1]
            #v0 = Vector(sf[0].co)
            #v1 = Vector(sf[1].co)
            #v2 = Vector(sf[2].co)
            #fv = [v0, v1, v2]
            #q = G3.centerOfSphere(fv)
            #d = (v0-q).length
            #cc.stepLengthValue = d
            #return {'FINISHED'}
        #if obj.data.total_vert_sel==4:
            #sf = [f for f in obj.data.vertices if f.select == 1]
            #v0 = Vector(sf[0].co)
            #v1 = Vector(sf[1].co)
            #v2 = Vector(sf[2].co)
            #v3 = Vector(sf[3].co)
            #fv = [v0, v1, v2, v3]
            #q = G3.centerOfSphere(fv)
            #d = (v0-q).length
            #cc.stepLengthValue = d
            #return {'FINISHED'}
        #return {'CANCELLED'}



class VIEW3D_OT_cursor_draw_enable(bpy.types.Operator):
    '''Show cursor memory.'''
    bl_idname = "view3d.cursor_draw_enable"
    bl_label = "Show cursor memory."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.savedLocationDraw = True
        BlenderFake.forceRedraw()
        return {'FINISHED'}



class VIEW3D_OT_cursor_draw_disable(bpy.types.Operator):
    '''Hide cursor memory.'''
    bl_idname = "view3d.cursor_draw_disable"
    bl_label = "Hide cursor memory."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.savedLocationDraw = False
        BlenderFake.forceRedraw()
        return {'FINISHED'}



class VIEW3D_OT_cursor_history_enable(bpy.types.Operator):
    '''Show cursor trace.'''
    bl_idname = "view3d.cursor_history_enable"
    bl_label = "Show cursor trace."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.historyDraw = True
        BlenderFake.forceRedraw()
        return {'FINISHED'}



class VIEW3D_OT_cursor_history_disable(bpy.types.Operator):
    '''Hide cursor trace.'''
    bl_idname = "view3d.cursor_history_disable"
    bl_label = "Hide cursor trace."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.historyDraw = False
        BlenderFake.forceRedraw()
        return {'FINISHED'}



class VIEW3D_OT_cursor_stepval_phinv(bpy.types.Operator):
    '''Set step value to 1/Phi.'''
    bl_idname = "view3d.cursor_stepval_phinv"
    bl_label = "Set step value to 1/Phi."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.stepLengthValue = PHI_INV
        BlenderFake.forceRedraw()
        return {'FINISHED'}



class VIEW3D_OT_cursor_stepval_phi(bpy.types.Operator):
    '''Set step value to Phi.'''
    bl_idname = "view3d.cursor_stepval_phi"
    bl_label = "Set step value to Phi."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.stepLengthValue = PHI
        BlenderFake.forceRedraw()
        return {'FINISHED'}



class VIEW3D_OT_cursor_stepval_phi2(bpy.types.Operator):
    '''Set step value to Phi².'''
    bl_idname = "view3d.cursor_stepval_phi2"
    bl_label = "Set step value to Phi²."
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_control
        cc.stepLengthValue = PHI*PHI
        BlenderFake.forceRedraw()
        return {'FINISHED'}



class VIEW3D_OT_cursor_stepval_vvdist(bpy.types.Operator):
    '''Set step value to distance vertex-vertex.'''
    bl_idname = "view3d.cursor_stepval_vvdist"
    bl_label = "Set step value to distance vertex-vertex."
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
        q = (v0-v1).length
        cc.stepLengthValue = q

        BlenderFake.forceRedraw()
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

    def draw(self, context):
        layout = self.layout
        sce = context.scene

        tvs = 0
        tes = 0
        tfs = 0
        edit_mode = False
        obj = context.active_object
        if (context.mode == 'EDIT_MESH'):
            if (obj and obj.type=='MESH' and obj.data):
                tvs = obj.data.total_vert_sel

                tes = obj.data.total_edge_sel
                tfs = obj.data.total_face_sel
                edit_mode = True

        # Mesh data elements
        if(edit_mode):
            row = layout.row()
            GUI.drawIconButton(tvs>=1          , row, 'STICKY_UVS_DISABLE', "view3d.cursor_to_vertex")
            GUI.drawIconButton(tvs==2 or tes>=1, row, 'MESH_DATA'         , "view3d.cursor_to_line")
            GUI.drawIconButton(tvs==2 or tes>=1, row, 'OUTLINER_OB_MESH'  , "view3d.cursor_to_edge")
            GUI.drawIconButton(tvs==3 or tfs>=1, row, 'SNAP_FACE'         , "view3d.cursor_to_plane")
            GUI.drawIconButton(tvs==3 or tfs>=1, row, 'FACESEL'           , "view3d.cursor_to_face")

        # Geometry from mesh
        if(edit_mode):
            row = layout.row()
            GUI.drawIconButton(tvs<=3 or tfs==1 , row, 'MOD_MIRROR'  , "view3d.cursor_to_SL_mirror")
            GUI.drawIconButton(tes==2, row, 'PARTICLE_TIP', "view3d.cursor_to_linex")
            GUI.drawIconButton(tvs>1 , row, 'ROTATECENTER', "view3d.cursor_to_vertex_median")  #EDITMODE_HLT
            GUI.drawIconButton(tvs==3 or tvs==4, row, 'FORCE_FORCE'  , "view3d.cursor_to_spherecenter")
            GUI.drawIconButton(tvs==3 or tvs==4, row, 'MATERIAL'  , "view3d.cursor_to_perimeter")

        # Objects
        #row = layout.row()

        #GUI.drawIconButton(context.active_object!=None    , row, 'ROTATE'          , "view3d.cursor_to_active_object_center")
        #GUI.drawIconButton(len(context.selected_objects)>1, row, 'ROTATECOLLECTION', "view3d.cursor_to_selection_midpoint")
        #GUI.drawIconButton(len(context.selected_objects)>1, row, 'ROTATECENTER'    , "view3d.cursor_to_selection_midpoint")

        # References World Origin, Object Origin, SL and CL
        row = layout.row()
        GUI.drawIconButton(True                       , row, 'WORLD_DATA'    , "view3d.cursor_to_origin")
        GUI.drawIconButton(context.active_object!=None, row, 'ROTACTIVE'       , "view3d.cursor_to_active_object_center")
        GUI.drawIconButton(True                       , row, 'CURSOR'        , "view3d.cursor_to_SL")
        #GUI.drawIconButton(True, row, 'GRID'          , "view3d.cursor_SL_recall")
        #GUI.drawIconButton(True, row, 'SNAP_INCREMENT', "view3d.cursor_SL_recall")
        #row.label("("+str(cc.linexChoice)+")")
        cc = context.scene.cursor_control
        if cc.linexChoice>=0:
            col = row.column()
            col.enabled = False
            col.prop(cc, "linexChoice")

        # Limit/Clamping Properties
        row = layout.row()
        row.prop(cc, "stepLengthEnable")
        if (cc.stepLengthEnable):
            row = layout.row()
            row.prop(cc, "stepLengthMode")
            row.prop(cc, "stepLengthValue")
            row = layout.row()
            GUI.drawTextButton(True, row, '1/Phi'      , "view3d.cursor_stepval_phinv")
            GUI.drawTextButton(True, row, 'Phi'      , "view3d.cursor_stepval_phi")
            GUI.drawTextButton(True, row, 'Phi²'      , "view3d.cursor_stepval_phi2")
            GUI.drawIconButton(tvs==2, row, 'EDGESEL'      , "view3d.cursor_stepval_vvdist")
        



class VIEW3D_PT_cursor_SL(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Cursor Memory"
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
        if cc.savedLocationDraw:
            GUI.drawIconButton(True, layout, 'RESTRICT_VIEW_OFF', "view3d.cursor_draw_disable", False)
        else:
            GUI.drawIconButton(True, layout, 'RESTRICT_VIEW_ON' , "view3d.cursor_draw_enable", False)
        #layout.prop(sce, "cursor_control.savedLocationDraw")

    def draw(self, context):
        layout = self.layout
        sce = context.scene
        cc = context.scene.cursor_control

        row = layout.row()
        col = row.column()
        row2 = col.row()
        GUI.drawIconButton(True, row2, 'FORWARD', "view3d.cursor_SL_save")
        row2 = col.row()
        GUI.drawIconButton(True, row2, 'FILE_REFRESH', "view3d.cursor_SL_swap")
        row2 = col.row()
        GUI.drawIconButton(True, row2, 'BACK'        , "view3d.cursor_SL_recall")
        col = row.column()
        col.prop(cc, "savedLocation")

class VIEW3D_PT_cursor_history(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Cursor History"
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
        if cc.historyDraw:
            GUI.drawIconButton(True, layout, 'RESTRICT_VIEW_OFF', "view3d.cursor_history_disable", False)
        else:
            GUI.drawIconButton(True, layout, 'RESTRICT_VIEW_ON' , "view3d.cursor_history_enable", False)

    def draw(self, context):
        layout = self.layout
        sce = context.scene
        cc = context.scene.cursor_control

        row = layout.row()
        row.label("Navigation: ")
        GUI.drawIconButton(cc.historyPosition[0]>0, row, 'PLAY_REVERSE', "view3d.cursor_previous")
        #if(cc.historyPosition[0]<0):
            #row.label("  --  ")
        #else:
            #row.label("  "+str(cc.historyPosition[0])+"  ")
        GUI.drawIconButton(cc.historyPosition[0]<len(cc.historyLocation)-1, row, 'PLAY', "view3d.cursor_next")

        row = layout.row()
        col = row.column()
        col.prop(CursorAccess.findSpace(), "cursor_location")

        cc.addHistoryLocation(CursorAccess.getCursor())
  
                

  
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

    draw = 0
    if hasattr(cc, "historyDraw"):
        draw = cc.historyDraw

    if(draw):
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glShadeModel(bgl.GL_FLAT)
        alpha = 1-PHI_INV
        # History Trace
        if cc.historyPosition[0]<0:
            return
        bgl.glBegin(bgl.GL_LINE_STRIP)
        ccc = 0
        for iii in range(cc.historyWindow+1):
            ix_rel = iii - int(cc.historyWindow / 2)
            ix = cc.historyPosition[0] + ix_rel
            if(ix<0 or ix>=len(cc.historyLocation)):
                continue
            ppp = region3d_get_2d_coordinates(context, cc.historyLocation[ix])
            if(ix_rel<=0):
                bgl.glColor4f(0, 0, 0, alpha)
            else:
                bgl.glColor4f(1, 0, 0, alpha)
            bgl.glVertex2f(ppp[0], ppp[1])
            ccc = ccc + 1
        bgl.glEnd()

        
        
        

def register():
    # Register Cursor Control Structure
    bpy.types.Scene.cursor_control = bpy.props.PointerProperty(type=CursorControlData, name="")
        


def unregister():
    pass


if __name__ == "__main__":
    register()
