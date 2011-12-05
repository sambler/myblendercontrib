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
    "name": "Import animation from chan file (.chan)",
    "author": "Michael Krupa",
    "version": (1, 0),
    "blender": (2, 6, 0),
    "api": 36079,
    "location": "File > Import > Nuke (.chan)",
    "description": "Import object's animation from nuke",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/Import-Export/Nuke",
    "tracker_url": "http://projects.blender.org/tracker/index.php?"\
        "func=detail&atid=467&aid=28368&group_id=153",
    "category": "Import-Export"}

""" This script is an importer for the nuke's .chan files"""

import bpy
from mathutils import Matrix
from mathutils import Euler
from mathutils import Vector
from math import radians
from math import degrees
from math import atan
from math import tan


def read_chan(context, filepath, Zup, rot_ord):
    #check if we have anything selected, if not, finish without doing anything.
    if not bpy.context.active_object:
        return {'FINISHED'}

    #get the active object
    obj = bpy.context.active_object

    #get the resolution (needed to calculate the camera lens)
    res_x = bpy.context.scene.render.resolution_x
    res_y = bpy.context.scene.render.resolution_y
    res_ratio = res_y / res_x

    #prepare the correcting matrix
    rot_mat = Matrix.Rotation(radians(90), 4, "X").to_4x4()

    #read the file
    f = open(filepath, 'r')

    #iterate throug the files lines
    for line in f.readlines():
        #reset the target objects matrix
        #(the one from whitch one we'll extract the final transforms)
        m_trans_mat = Matrix()
        m_trans_mat.to_4x4()

        #strip the line
        data = line.split()

        #test if the line is not commented out
        if data[0] != "#":

            #set the frame number basing on the chan file
            bpy.context.scene.frame_set(int(data[0]))

            #read the translation values from the first three columns of line
            v_transl = Vector([float(data[1]), float(data[2]), float(data[3])])
            translation_mat = Matrix.Translation(v_transl)
            translation_mat.to_4x4()

            #read the rotations, and set the rotation order basing on the order
            #set during the export (it's not being saved in the chan file
            #you have to keep it noted somewhere
            #the actual objects rotation order doesn't matter since the
            #rotations are being extracted from the matrix afterwards
            e_rot = Euler([radians(float(data[4])),
                            radians(float(data[5])),
                            radians(float(data[6]))])
            e_rot.order = rot_ord
            mrot_mat = e_rot.to_matrix()
            mrot_mat.resize_4x4()

            #merge the rotation and translation
            m_trans_mat = translation_mat * mrot_mat

            #correct the world space
            #(nuke's and blenders scene spaces are different)
            if Zup:
                m_trans_mat = rot_mat * m_trans_mat

            #break the matrix into a set of the coordinates
            trns = m_trans_mat.decompose()

            #set the location and the location's keyframe
            obj.location = trns[0]
            obj.keyframe_insert('location')

            #convert the rotation to euler angles (or not)
            #basing on the objects rotation mode
            if obj.rotation_mode != "QUATERNION":
                obj.rotation_euler = trns[1].to_euler(obj.rotation_mode)
                obj.keyframe_insert('rotation_euler')
            else:
                obj.rotation_euler = trns[1]
                obj.keyframe_insert('rotation_quaternion')

            #if the target object is camera test for the vfov data. If present,
            #calculate the horizontal angle and set the keyframe on camera lens
            if obj.data.type == "PERSP":
                if len(data) > 7:
                    v_fov = float(data[7])
                    lenslen = (res_ratio/2)  / (tan(radians(v_fov/2)))
                    h_fov = (atan( .5 / lenslen ) * 2)
                    print(h_fov)
                    obj.data.angle = h_fov
                    obj.data.keyframe_insert('lens')
    f.close()

    return {'FINISHED'}


from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty


class ImportChan(bpy.types.Operator, ImportHelper):
    '''Import animation from .chan file, exported from nuke or houdini.
    The importer uses frame numbers from the file.'''
    bl_idname = "import_scene.import_chan"
    bl_label = "Import chan file"

    filename_ext = ".chan"

    filter_glob = StringProperty(default="*.chan", options={'HIDDEN'})

    Zup = BoolProperty(name="Make Z up",
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
                        description="Choose the rotation order with whitch \
                        the chan file has been exported",
                        default='XYZ')

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        return read_chan(context, self.filepath, self.Zup, self.rot_ord)


def menu_func_import(self, context):
    self.layout.operator(ImportChan.bl_idname, text="Nuke (.chan)")


def register():
    bpy.utils.register_class(ImportChan)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportChan)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
    bpy.ops.import_scene.import_chan('INVOKE_DEFAULT')
