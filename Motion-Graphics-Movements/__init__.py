'''
Copyright (C) 2014 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys, os, bpy
sys.path.append(os.path.dirname(__file__))
from motion_graphics_utils import *
from motion_graphics_create_object_utils import *
from motion_graphics_constraint_utils import *
from motion_graphics_driver_utils import *
from motion_graphics_animation_utils import *
from motion_graphics_material_and_node_utils import *
from motion_graphics_MotionGraphicsObject import *
from motion_graphics_names import *

bl_info = {
	"name":        "Motion Graphics Movements",
	"description": "",
	"author":      "Jacques Lucke",
	"version":     (0, 0, 1),
	"blender":     (2, 7, 2),
	"location":    "View 3D > Tool Shelf",
	"category":    "Animation",
	"warning":	   "pre alpha"
	}	
	
# interface
##################################

class MotionGraphicsMovementsPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Animation"
	bl_label = "Motion Graphics Movements"
	bl_context = "objectmode"
	
	def draw(self, context):
		layout = self.layout
		layout.operator("motion_graphics.generate_velocity_properties")
		layout.operator("motion_graphics.link_xloc_velocity_to_shear")
		layout.operator("motion_graphics.create_animated_lattice")
		

# operators
##################################		
		
class GenerateVelocityProperties(bpy.types.Operator):
	bl_idname = "motion_graphics.generate_velocity_properties"
	bl_label = "Generate Velocity Properties"
	bl_description = "Generates animated custom properties with the velocity of the object"
	
	def execute(self, context):
		object = MotionGraphicsObject(getActive())
		object.generateVelocityProperties()
		return{"FINISHED"}
		
class LinkXLocVelocityToShear(bpy.types.Operator):
	bl_idname = "motion_graphics.link_xloc_velocity_to_shear"
	bl_label = "Link X Location Velocity to Shear"
	bl_description = "Creates a shear animation based on the velocity (only works on texts)."
	
	def execute(self, context):
		object = MotionGraphicsObject(getActive())
		object.linkXLocVelocityToShear()
		return{"FINISHED"}
		
class CreateAnimatedLattice(bpy.types.Operator):
	bl_idname = "motion_graphics.create_animated_lattice"
	bl_label = "Create Lattice"
	bl_description = "Create a lattice object as bounding box."
	
	def execute(self, context):
		object = MotionGraphicsObject(getActive())
		object.createAnimatedLattice()
		return{"FINISHED"}
	
	
# register
##################################

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
