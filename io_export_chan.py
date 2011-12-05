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
bl_info = {
    "name": "Export animation to nuke (.chan)",
    "author": "Michael Krupa",
    "version": (1, 0),
    "blender": (2, 6, 0),
    "api": 36079,
    "location": "File > Export > Nuke (.chan)",
    "description": "Export object's animation to nuke",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/Import-Export/Nuke",
    "tracker_url": "http://projects.blender.org/tracker/?"\
        "func=detail&atid=467&aid=28368&group_id=153",
    "category": "Import-Export"}

""" This script is an exporter to the nuke's .chan files.
It takes the currently active object and writes it's transformation data
into a text file with .chan extension."""

import bpy
from mathutils import Matrix
from mathutils import Euler
from math import radians
from math import degrees
from math import atan
from math import atan2
from math import tan


def save_chan(context, filepath, y_up, rot_ord):
    #check if we have anything selected, if not, end with no action
    if not bpy.context.active_object:
        return {'FINISHED'}

    #get the active object
    obj = bpy.context.active_object

    #get the range of an animation
    f_start = bpy.context.scene.frame_start
    f_end = bpy.context.scene.frame_end

    #get the resolution (needed by nuke)
    res_x = bpy.context.scene.render.resolution_x
    res_y = bpy.context.scene.render.resolution_y
    res_ratio = res_y / res_x

    #prepare the correcting matrix
    rot_mat = Matrix.Rotation(radians(-90), 4, "X").to_4x4()

    f = open(filepath, 'w')
    #iterate the frames
    for a in range(f_start, f_end, 1):
        #reset the new line of a chan file
        export_string = []

        #set the current frame
        bpy.context.scene.frame_set(a)

        #get the objects world matrix
        mat = obj.matrix_world

        #if the setting is proper use the rotation matrix
        #to flip the Z and Y axis
        if y_up:
            mat = rot_mat * mat

        #create the first component of a new line, the frame number
        export_string.append("%i\t" % a)

        #create transform component
        t = mat.to_translation()
        export_string.append("%f\t%f\t%f\t" % t[:])

        #create rotation component
        r = mat.to_euler(rot_ord)

        #export_string += "%f\t%f\t%f\t" % (r[0], r[1], r[2])
        export_string.append("%f\t%f\t%f\t" % (degrees(r[0]),
                                           degrees(r[1]),
                                           degrees(r[2])))

        #if we have a camera, add the focal length
        if obj.type == 'CAMERA':
            #I've found via the experiments that this is a blenders 
            #default sensor size (in mm)
            sensor_x = 32.0
            #the vertical sensor size we get by multiplying the sensor_x by
            #resolution ratio
            sensor_y = sensor_x * res_ratio
            cam_lens = obj.data.lens
            #calculate the vertical field of view
            #we know the vertical size of (virtual) sensor, the focal length
            #of the camera so all we need to do is to feed this data to
            #atan2 function whitch returns the degree (in radians) of 
            #an angle formed by a triangle with two legs of a given lengths
            vfov = degrees(atan2(sensor_y / 2, cam_lens))*2
            export_string.append("%f\n" % vfov)

        #when all is set and done write the new line
        f.write("".join(export_string))

    #after the whole loop close the file
    f.close()

    return {'FINISHED'}


from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty


class ExportChan(bpy.types.Operator, ExportHelper):
    '''Export the animation to .chan file, readable by nuke and houdini.
    The exporter uses frames from the frames range'''
    bl_idname = "export.export_chan"
    bl_label = "Export chan file"
    filename_ext = ".chan"
    filter_glob = StringProperty(default="*.chan", options={'HIDDEN'})
    y_up = BoolProperty(name="Make Y up",
                       description="Switch the Y and Z axis",
                       default=True)
    rot_ord = EnumProperty(items=(('XYZ', "XYZ", "XYZ"),
                               ('XZY', "XZY", "XZY"),
                               ('YXZ', "YXZ", "YXZ"),
                               ('YZX', "YZX", "YZX"),
                               ('ZXY', "ZXY", "ZXY"),
                               ('ZYX', "ZYX", "ZYX"),
                               ),
                        name="Rotation order",
                        description="Choose the export rotation order",
                        default='XYZ')
    settings = {"y_up": y_up, "rot_ord": rot_ord}

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        return save_chan(context, self.filepath, self.y_up, self.rot_ord)


def menu_func_export(self, context):
    self.layout.operator(ExportChan.bl_idname, text="Nuke (.chan)")


def register():
    bpy.utils.register_class(ExportChan)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportChan)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
