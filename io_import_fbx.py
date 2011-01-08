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

# <pep8 compliant>

bl_addon_info = {
    "name": "Import: Autodesk FBX",
    "author": "Campbell Barton",
    "version": (0, 0, 1),
    "blender": (2, 5, 6),
    "api": 32516,
    "location": "File > Import ",
    "description": "This script is WIP and not intended for general use yet!",
    "warning": "Work in progress",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}


def parse_fbx(path, fbx_data):
    DEBUG = False

    f = open(path, "rU")
    lines = f.readlines()

    # remove comments and \n
    lines = [l[:-1].rstrip() for l in lines if not l.lstrip().startswith(";")]

    # remove whitespace
    lines = [l for l in lines if l]

    # remove multiline float lists
    def unmultiline(i):
        lines[i - 1] = lines[i - 1] + lines.pop(i).lstrip()

    # Multiline floats, used for verts and matricies, this is harderto read so detect and make into 1 line.
    i = 0
    while i < len(lines):
        l = lines[i].strip()
        if l.startswith(","):
            unmultiline(i)
            i -= 1
        try:
            float(l.split(",", 1)[0])
            unmultiline(i)
            i -= 1
        except:
            pass

        i += 1

    CONTAINER = [None]

    def is_int(val):
        try:
            CONTAINER[0] = int(val)
            return True
        except:
            return False

    def is_int_array(val):
        try:
            CONTAINER[0] = tuple([int(v) for v in val.split(",")])
            return True
        except:
            return False

    def is_float(val):
        try:
            CONTAINER[0] = float(val)
            return True
        except:
            return False

    def is_float_array(val):
        try:
            CONTAINER[0] = tuple([float(v) for v in val.split(",")])
            return True
        except:
            return False

    def read_fbx(i, ls):
        if DEBUG:
            print("LINE:", lines[i])

        tag, val = lines[i].split(":", 1)
        tag = tag.lstrip()
        val = val.strip()

        if val == "":
            ls.append((tag, None, None))
        if val.endswith("{"):
            name = val[:-1].strip()  # remove the trailing {
            if name == "":
                name = None

            sub_ls = []
            ls.append((tag, name, sub_ls))

            i += 1
            while lines[i].strip() != "}":
                i = read_fbx(i, sub_ls)

        elif val.startswith('"') and val.endswith('"'):
            ls.append((tag, None, val[1:-1]))  # remove quotes
        elif is_int(val):
            ls.append((tag, None, CONTAINER[0]))
        elif is_float(val):
            ls.append((tag, None, CONTAINER[0]))
        elif is_int_array(val):
            ls.append((tag, None, CONTAINER[0]))
        elif is_float_array(val):
            ls.append((tag, None, CONTAINER[0]))
        elif tag == 'Property':
            ptag, ptype, punknown, pval = val.split(",", 3)
            ptag = ptag.strip().strip("\"")
            ptype = ptype.strip().strip("\"")
            punknown = punknown.strip().strip("\"")
            pval = pval.strip()

            if val.startswith('"') and val.endswith('"'):
                pval = pval[1:-1]
            elif is_int(pval):
                pval = CONTAINER[0]
            elif is_float(pval):
                pval = CONTAINER[0]
            elif is_int_array(pval):
                pval = CONTAINER[0]
            elif is_float_array(pval):
                pval = CONTAINER[0]

            ls.append((tag, None, (ptag, ptype, punknown, pval)))
        else:
            # IGNORING ('Property', None, '"Lcl Scaling", "Lcl Scaling", "A+",1.000000000000000,1.000000000000000,1.000000000000000')
            print("\tParser Skipping:", (tag, None, val))

        # name = .lstrip()[0]
        if DEBUG:
            print("TAG:", tag)
            print("VAL:", val)
        return i + 1

    i = 0
    while i < len(lines):
        i = read_fbx(i, fbx_data)


# Blender code starts here:
import bpy


def import_fbx(path):
    import math
    
    fbx_data = []
    parse_fbx(path, fbx_data)
    # Now lets get in the mesh data for fun.

    def tag_get_iter(data, tag):
        for tag_iter, name, value in data:
            if tag_iter == tag:
                yield (name, value)
    
    def tag_get_single(data, tag):
        for tag_iter, name, value in data:
            if tag_iter == tag:
                return (name, value)
        return (None, None)

    def tag_get_prop(data, prop):
        for tag_iter, name, value in data:
            if tag_iter == "Property":
                if value[0] == prop:
                    return value[3]
        return None

    scene = bpy.context.scene

    for tag1, name1, value1 in fbx_data:
        if tag1 == "Objects":
            for tag2, name2, value2 in value1:
                if tag2 == "Model":
                    '''
                    print("")
                    print(tag2)
                    print(name2)
                    print(value2)
                    '''

                    # check we import an object
                    obj = None

                    # we dont parse this part properly
                    # the name2 can be somtrhing like
                    # Model "Model::kimiko", "Mesh"
                    if name2.endswith(" \"Mesh\""):
                        fbx_name = tag2.lstrip("Model::")

                        verts = tag_get_single(value2, "Vertices")[1]
                        faces = tag_get_single(value2, "PolygonVertexIndex")[1]

                        # convert odd fbx verts and faces to a blender mesh.
                        if verts and faces:
                            me = bpy.data.meshes.new(name=fbx_name)
                            # get a list of floats as triples
                            blen_verts = [verts[i - 3:i] for i in range(3, len(verts) + 3, 3)]

                            # get weirdo face indicies
                            face = []
                            blen_faces = [face]
                            for f in faces:
                                if f < 0:
                                    face.append(int(-f) - 1)
                                    face = []
                                    blen_faces.append(face)
                                else:
                                    face.append(int(f))

                            if not blen_faces[-1]:
                                del blen_faces[-1]

                            me.from_pydata(blen_verts, [], blen_faces)
                            me.update()

                            obj = bpy.data.objects.new(fbx_name, me)
                            base = scene.objects.link(obj)

                    elif name2.endswith(" \"Camera\""):
                        fbx_name = tag2.lstrip("Model::")

                        camera = bpy.data.cameras.new(name=fbx_name)
                        
                        props = tag_get_single(value2, "Properties60")[1]
                        camera.angle = math.radians(tag_get_prop(props, "FieldOfView"))

                        obj = bpy.data.objects.new(fbx_name, camera)
                        base = scene.objects.link(obj)

                    # apply transformation
                    if obj:
                        props = tag_get_single(value2, "Properties60")[1]
                        
                        # Note, rotations is not correct!
                        loc = tag_get_prop(props, "Lcl Translation")
                        rot = tag_get_prop(props, "Lcl Rotation")
                        sca = tag_get_prop(props, "Lcl Scaling")

                        obj.location = loc
                        obj.rotation_euler = rot
                        obj.scale = sca

    return {'FINISHED'}


# Operator
from bpy.props import StringProperty
from io_utils import ImportHelper


class ImportFBX(bpy.types.Operator, ImportHelper):
    ''''''
    bl_idname = "import_scene.fbx"
    bl_label = "Import FBX"

    filename_ext = ".fbx"
    filter_glob = StringProperty(default="*.fbx", options={'HIDDEN'})

    def execute(self, context):
        return import_fbx(self.filepath)


# Registering / Unregister
def menu_func(self, context):
    self.layout.operator(ImportFBX.bl_idname, icon='PLUGIN')


def register():
    bpy.types.INFO_MT_file_import.append(menu_func)


def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func)


if __name__ == "__main__":
    register()


if __name__ == "__main__":
    import_fbx("/test.fbx")
