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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

#----------------------------------------------------------
# File: main_panel.py
# Main panel for different Archimesh general actions
# Author: Antonio Vazquez (antonioya)
#
#----------------------------------------------------------
import bpy
import math
from tools import *

#-----------------------------------------------------
# Verify if boolean already exist
#-----------------------------------------------------
def isBoolean(myObject,childObject):
    flag = False
    for mod in myObject.modifiers:
            if mod.type == 'BOOLEAN':
                if mod.object == childObject:
                    flag = True
                    break
    return flag        
#------------------------------------------------------
# Button: Action to link windows and doors
#------------------------------------------------------
class holeAction(bpy.types.Operator):
    bl_idname = "object.archimesh_cut_holes"
    bl_label = "Auto Holes"
    bl_description = "Enable windows and doors holes for any selected object"
    bl_category = 'Archimesh'

    #------------------------------
    # Execute
    #------------------------------
    def execute(self, context):
        scene = context.scene
        listObj = []
        #---------------------------------------------------------------------
        # Save the list of selected objects because the select flag is missed
        # only can be windows or doors
        #---------------------------------------------------------------------
        for obj in bpy.context.scene.objects:
            try:
                if obj["archimesh.hole_enable"] == True:
                    if obj.select == True or scene.archimesh_select_only == False:
                        listObj.extend([obj])   
            except:
                continue
        #---------------------------
        # Get the baseboard object  
        #---------------------------
        myBaseBoard = None
        for child in context.object.children:
            try:
                if child["archimesh.room_baseboard"] == True:
                    myBaseBoard = child 
            except:
                continue                
        #-----------------------------
        # Now apply Wall holes
        #-----------------------------
        for obj in listObj:
            parentObj = context.object
            # Parent the empty to the room (the parent of frame)
            if obj.parent != None:
                bpy.ops.object.select_all(action='DESELECT')
                parentObj.select = True
                obj.parent.select = True # parent of object
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)                    
            #---------------------------------------
            # Add the modifier to controller
            # and the scale to use the same thickness
            #---------------------------------------
            for child in obj.parent.children:
                try:
                    if child["archimesh.ctrl_hole"] == True:
                        # apply scale
                        t = parentObj.RoomGenerator[0].wall_width
                        if t > 0:
                            child.scale.y = (t  + 0.35) / (child.dimensions.y/child.scale.y) # Add some gap
                        else:
                            child.scale.y = 1     
                        # add boolean modifier
                        if isBoolean(context.object,child) == False:
                            set_modifier_boolean(context.object,child)
                except:
                    x = 1 # dummy            
        #---------------------------------------
        # Now add the modifiers to baseboard
        #---------------------------------------
        if myBaseBoard != None:
            for obj in bpy.context.scene.objects:
                try:
                    if obj["archimesh.ctrl_base"] == True:
                        if obj.select == True or scene.archimesh_select_only == False:
                            # add boolean modifier
                            if isBoolean(myBaseBoard,obj) == False:
                                set_modifier_boolean(myBaseBoard,obj)
                except:
                    x = 1 # dummy            
                    
        return {'FINISHED'}

#------------------------------------------------------
# Button: Action to create room from grease pencil 
#------------------------------------------------------
class pencilAction(bpy.types.Operator):
    bl_idname = "object.archimesh_pencil_room"
    bl_label = "Room from Draw"
    bl_description = "Create a room base on grease pencil strokes (draw from top view (7 key))"
    bl_category = 'Archimesh'

    #------------------------------
    # Execute
    #------------------------------
    def execute(self, context):
        # Enable for debugging code
        debugMODE = False

        scene = context.scene

        # define error margin 
        xRange = 0.01
        yRange = 0.01
        
        if debugMODE == True:
            print("======================================================================")
            print("==                                                                  ==")
            print("==  Grease pencil strokes analysis                                  ==")
            print("==                                                                  ==")
            print("======================================================================")
        
        #-----------------------------------
        # Get grease pencil points
        #-----------------------------------
        try:
            
            try:
                pencil = bpy.context.object.grease_pencil.layers.active 
            except:    
                pencil = bpy.context.scene.grease_pencil.layers.active
                
            if pencil.active_frame != None:
                for i, stroke in enumerate(pencil.active_frame.strokes):
                    stroke_points = pencil.active_frame.strokes[i].points
                    allPoints = [ (point.co.x, point.co.y) 
                                    for point in stroke_points ]
                    
                    myPoints = []
                    idx = 0
                    x = 0
                    y = 0
                    orientation = None
                    old_orientation = None
                    
                    for point in allPoints:
                        if idx == 0:
                            x = point[0]
                            y = point[1]
                        else:    
                            if (x - xRange) <= point[0] <= (x + xRange):
                                orientation = "V"
                                
                            if (y - yRange) <= point[1] <= (y + yRange):
                                orientation = "H"
                                
                            if old_orientation == orientation:
                                x = point[0]
                                y = point[1]
                            else:                                     
                                myPoints.extend([(x,y)])
                                x = point[0]
                                y = point[1]
                                old_orientation = orientation
            
                        idx += 1
                    # Last point
                    myPoints.extend([(x,y)])
                    
                    if debugMODE == True:
                        print("\nPoints\n====================")
                        i = 0 
                        for p in myPoints:
                            print(str(i) + ":" + str(p))
                            i += 1
                    #-----------------------------------
                    # Calculate distance between points
                    #-----------------------------------
                    if debugMODE == True:
                        print("\nDistance\n====================")
                    i = len(myPoints)
                    distList = []
                    for e in range(1,i):
                        d = math.sqrt(((myPoints[e][0] - myPoints[e-1][0]) ** 2) + ((myPoints[e][1] - myPoints[e-1][1]) ** 2))
                        distList.extend([(d)])
                        
                        if debugMODE == True:
                            print(str(e-1) + ":" + str(d))
                    #-----------------------------------
                    # Calculate angle of walls
                    # clamped to right angles
                    #-----------------------------------
                    if debugMODE == True:
                        print("\nAngle\n====================")
                        
                    i = len(myPoints)
                    angleList = []
                    for e in range(1,i):
                        sinV = (myPoints[e][1] - myPoints[e-1][1]) / math.sqrt(((myPoints[e][0] - myPoints[e-1][0]) ** 2) + ((myPoints[e][1] - myPoints[e-1][1]) ** 2))
                        a = math.asin(sinV)            
                        # Clamp to 90 or 0 degrees
                        if math.fabs(a) > math.pi / 4:
                            b = math.pi / 2
                        else:
                            b = 0    
                        
                        angleList.extend([(b)])
                        # Reverse de distance using angles (inverse angle to axis) for Vertical lines
                        if a < 0.0 and b != 0:
                            distList[e-1] = distList[e-1] * -1 # reverse distance
                            
                        # Reverse de distance for horizontal lines
                        if b == 0:
                            if myPoints[e-1][0] > myPoints[e][0]:
                                distList[e-1] = distList[e-1] * -1 # reverse distance
                        
                        if debugMODE == True:
                            print(str(e-1) + ":" + str((a * 180) / math.pi) + "...:" + str((b * 180) / math.pi) + "--->" + str(distList[e-1])) 

                    #---------------------------------------
                    # Verify duplications and reduce noise
                    #---------------------------------------
                    if len(angleList) >= 1:
                        clearAngles = []
                        clearDistan = []
                        i = len(angleList)
                        oldAngle = angleList[0]
                        oldDist = 0
                        for e in range(0,i):
                            if oldAngle != angleList[e]:
                                clearAngles.extend([(oldAngle)])
                                clearDistan.extend([(oldDist)])    
                                oldAngle = angleList[e]
                                oldDist = distList[e]
                            else:
                                oldDist += distList[e]
                        # last 
                        clearAngles.extend([(oldAngle)])
                        clearDistan.extend([(oldDist)])    

            #----------------------------
            # Create the room 
            #----------------------------
            if len(myPoints) > 1 and len(clearAngles) > 0:
                # Move cursor
                bpy.context.scene.cursor_location.x = myPoints[0][0]
                bpy.context.scene.cursor_location.y = myPoints[0][1]
                bpy.context.scene.cursor_location.z = 0 # always on grid floor
                
                # Add room mesh
                bpy.ops.mesh.archimesh_room()
                myRoom = context.object
                myData = myRoom.RoomGenerator[0]
                # Number of walls
                myData.wall_num = len(myPoints) - 1
                myData.ceiling = scene.archimesh_ceiling
                myData.floor = scene.archimesh_floor
                myData.merge = scene.archimesh_merge
                
                i = len(myPoints)
                for e in range(0,i-1):
                    if clearAngles[e] == math.pi / 2: 
                        if clearDistan[e] > 0:
                            myData.walls[e].w = round(math.fabs(clearDistan[e]),2)
                            myData.walls[e].r = (math.fabs(clearAngles[e]) * 180) / math.pi # from radians
                        else:
                            myData.walls[e].w = round(math.fabs(clearDistan[e]),2)
                            myData.walls[e].r = (math.fabs(clearAngles[e]) * 180 * -1) / math.pi # from radians
                                
                    else:
                        myData.walls[e].w = round(clearDistan[e],2)
                        myData.walls[e].r = (math.fabs(clearAngles[e]) * 180) / math.pi # from radians
                            
                # Remove Grease pencil
                if pencil is not None:
                    for frame in pencil.frames:
                        pencil.frames.remove(frame)

                self.report({'INFO'}, "Archimesh: Room created from grease pencil strokes")
            else:
                self.report({'WARNING'}, "Archimesh: Not enough grease pencil strokes for creating room.")
                
            return {'FINISHED'}
        except:
            self.report({'WARNING'}, "Archimesh: No grease pencil strokes. Do strokes in top view before creating room")
            return {'CANCELLED'}

#------------------------------------------------------------------
# Define panel class for main functions.
#------------------------------------------------------------------
class ArchimeshMainPanel(bpy.types.Panel):
    bl_idname      ="archimesh_main_panel"
    bl_label       ="Archimesh"
    bl_space_type  ='VIEW_3D'
    bl_region_type = "TOOLS"
    bl_category = 'Archimesh'

    #------------------------------
    # Draw UI
    #------------------------------
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        myObj = context.object
        #-------------------------------------------------------------------------
        # If the selected object didn't be created with the group 'RoomGenerator', 
        # this button is not created.
        #-------------------------------------------------------------------------
        try:
            if 'RoomGenerator' in myObj:
                box = layout.box()
                box.label("Room Tools",icon='MODIFIER')
                row = box.row(align=False)
                row.operator("object.archimesh_cut_holes", icon='GRID')
                row.prop(scene,"archimesh_select_only")
    
                # Export/Import
                row = box.row(align=False)
                row.operator("io_import.roomdata", text="Import",icon='COPYDOWN')
                row.operator("io_export.roomdata", text="Export",icon='PASTEDOWN')
        except:
            x = 1 # dummy line   
        
        # Grease pencil tools 
        box = layout.box()
        box.label("Pencil Tools",icon='MODIFIER')
        row = box.row(align=False)
        row.operator("object.archimesh_pencil_room", icon='GREASEPENCIL')
        row = box.row(align=False)
        row.prop(scene,"archimesh_ceiling")
        row.prop(scene,"archimesh_floor")
        row.prop(scene,"archimesh_merge")
        #-------------------------------------------------------------------------
        # If the selected object isn't a kitchen 
        # this button is not created.
        #-------------------------------------------------------------------------
        try:
            if myObj["archimesh.sku"] != None:
                box = layout.box()
                box.label("Kitchen Tools",icon='MODIFIER')
                # Export
                row = box.row(align=False)
                row.operator("io_export.kitchen_inventory", text="Export inventory",icon='PASTEDOWN')
        except:
            x = 1 # dummy line   
            
        #------------------------------
        # Elements Buttons
        #------------------------------
        box = layout.box()
        box.label("Elements", icon='GROUP')
        row = box.row()
        row.operator("mesh.archimesh_room")
        row.operator("mesh.archimesh_column")
        row = box.row()
        row.operator("mesh.archimesh_door")
        row.operator("mesh.archimesh_window")
        row = box.row()
        row.operator("mesh.archimesh_kitchen")
        row.operator("mesh.archimesh_shelves")
        row = box.row()
        row.operator("mesh.archimesh_stairs")
        row.operator("mesh.archimesh_roof")
        
        #------------------------------
        # Prop Buttons
        #------------------------------
        box = layout.box()
        box.label("Props",icon='LAMP_DATA')
        row = box.row()
        row.operator("mesh.archimesh_books")
        row.operator("mesh.archimesh_lamp")
        row = box.row()
        row.operator("mesh.archimesh_venetian")
        row.operator("mesh.archimesh_roller")
        row = box.row()
        row.operator("mesh.archimesh_japan")
            
