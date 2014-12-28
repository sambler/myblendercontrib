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

import bpy
from motion_graphics_utils import *
from motion_graphics_create_object_utils import *
from motion_graphics_constraint_utils import *
from motion_graphics_driver_utils import *
from motion_graphics_animation_utils import *
from motion_graphics_material_and_node_utils import *
from motion_graphics_names import *

class MotionGraphicsObject():
	
	def __init__(self, object):
		self.__object = object
		
	def generateVelocityProperties(self):
		(startFrame, endFrame) = getFrameBoundaries()
		obj = self.__object
		
		self.cleanVelocityProperties()
		
		for frame in range(startFrame, endFrame):
			self.createVelocityAnimation(frame)
	
	def cleanVelocityProperties(self):
		self.createVelocityProperties()
		self.clearVelocityAnimation()
	def createVelocityProperties(self):
		obj = self.__object
		setCustomProperty(obj, PropNames.xLocVelocity, value = 0.0, description = "Location change on the X-axis for every frame.")
		setCustomProperty(obj, PropNames.yLocVelocity, value = 0.0, description = "Location change on the Y-axis for every frame.")
		setCustomProperty(obj, PropNames.zLocVelocity, value = 0.0, description = "Location change on the Z-axis for every frame.")
	def clearVelocityAnimation(self):
		obj = self.__object
		clearAnimation(obj, PropPaths.xLocVelocity)
		clearAnimation(obj, PropPaths.yLocVelocity)
		clearAnimation(obj, PropPaths.zLocVelocity)
		
	def createVelocityAnimation(self, frame):
		self.setVelocityValues(frame)
		self.setVelocityKeyframe(frame)
	def setVelocityValues(self, frame):
		obj = self.__object
		obj[PropNames.xLocVelocity] = getChangeInFrame(obj, frame, "location", index = 0)
		obj[PropNames.yLocVelocity] = getChangeInFrame(obj, frame, "location", index = 1)
		obj[PropNames.zLocVelocity] = getChangeInFrame(obj, frame, "location", index = 2)
	def setVelocityKeyframe(self, frame):
		obj = self.__object
		obj.keyframe_insert(data_path = PropPaths.xLocVelocity, frame = frame)
		obj.keyframe_insert(data_path = PropPaths.yLocVelocity, frame = frame)
		obj.keyframe_insert(data_path = PropPaths.zLocVelocity, frame = frame)
		
	
	def linkXLocVelocityToShear(self):
		obj = self.__object
		if isTextObject(obj):
			curveObject = bpy.data.curves[obj.data.name]
			driver = newDriver(curveObject, "shear")
			linkFloatPropertyToDriver(driver, "xVel", obj, PropPaths.xLocVelocity)
			driver.expression = "-xVel"
			
	def getShearDriver(self):
		obj = self.__object.data
		if hasDriverData(obj):
			drivers = obj.animation_data.drivers
			for driver in drivers:
				if driver.data_path == "shear":
					return driver
		return None
		
	def createAnimatedLattice(self):
		obj = self.__object
		(startFrame, endFrame) = getFrameBoundaries()
		oldFrame = bpy.context.scene.frame_current
		lattice = newLattice()
		for frame in range(startFrame, endFrame):
			bpy.context.scene.frame_set(frame)
			setLatticeAsBoundingBox(lattice, obj)
			lattice.keyframe_insert(data_path = "location", frame = frame)
			lattice.keyframe_insert(data_path = "rotation_euler", frame = frame)
			lattice.keyframe_insert(data_path = "scale", frame = frame)
		bpy.context.scene.frame_set(oldFrame)
		
		
	def getObject(self):
		return self.__object