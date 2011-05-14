#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you may redistribute it, and/or
# modify it, under the terms of the GNU General Public License
# as published by the Free Software Foundation - either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, write to:
#
#	the Free Software Foundation Inc.
#	51 Franklin Street, Fifth Floor
#	Boston, MA 02110-1301, USA
#
# or go online at: http://www.gnu.org/licenses/ to view license options.
#
# ***** END GPL LICENCE BLOCK *****
#

bl_info = {
    "name": "Columns",
    "author": "Jim Bates, jambay",
    "version": (0, 1),
    "blender": (2, 5, 7),
    "api": 36339,
    "location": "View3D > Add > Mesh > Columns",
    "description": "Add architectural column(s).",
    "warning": "WIP - Initial implementation; updates pending and API not final for Blender",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"
}

"""

Create a column for use as an architectural element in a scene. Basically a glorified cylinder/cube.

A column consists of three elements; base, shaft, and capital. They can be square or round, straight or tapered. The base and capital are optional.

The shaft may be fluted and twisted.

Only one column is created, at the current 3D cursor, expecting the user to duplicate and place as needed.

This script is based on features from add_mesh_gears.

"""

# Version History
# v0.01 2011/05/13	Initial implementation.


import bpy
import mathutils
from math import *
from bpy.props import *

# A very simple "bridge" tool.
# Connects two equally long vertex rows with faces.
# Returns a list of the new faces (list of  lists)
#
# vertIdx1 ... First vertex list (list of vertex indices).
# vertIdx2 ... Second vertex list (list of vertex indices).
# closed ... Creates a loop (first & last are closed).
# flipped ... Invert the normal of the face(s).
#
# Note: You can set vertIdx1 to a single vertex index to create
#       a fan/star of faces.
# Note: If both vertex idx list are the same length they have
#       to have at least 2 vertices.
def createFaces(vertIdx1, vertIdx2, closed=False, flipped=False):
    faces = []

    if not vertIdx1 or not vertIdx2:
        return None

    if len(vertIdx1) < 2 and len(vertIdx2) < 2:
        return None

    fan = False
    if (len(vertIdx1) != len(vertIdx2)):
        if (len(vertIdx1) == 1 and len(vertIdx2) > 1):
            fan = True
        else:
            return None

    total = len(vertIdx2)

    if closed:
        # Bridge the start with the end.
        if flipped:
            face = [
                vertIdx1[0],
                vertIdx2[0],
                vertIdx2[total - 1]]
            if not fan:
                face.append(vertIdx1[total - 1])
            faces.append(face)

        else:
            face = [vertIdx2[0], vertIdx1[0]]
            if not fan:
                face.append(vertIdx1[total - 1])
            face.append(vertIdx2[total - 1])
            faces.append(face)

    # Bridge the rest of the faces.
    for num in range(total - 1):
        if flipped:
            if fan:
                face = [vertIdx2[num], vertIdx1[0], vertIdx2[num + 1]]
            else:
                face = [vertIdx2[num], vertIdx1[num],
                    vertIdx1[num + 1], vertIdx2[num + 1]]
            faces.append(face)
        else:
            if fan:
                face = [vertIdx1[0], vertIdx2[num], vertIdx2[num + 1]]
            else:
                face = [vertIdx1[num], vertIdx2[num],
                    vertIdx2[num + 1], vertIdx1[num + 1]]
            faces.append(face)

    return faces


# Calculate the vertex coordinates for a single
# section of a gear tooth.
# Returns 4 lists of vertex coords (list of tuples):
#  *-*---*---*	(1.) verts_inner_base
#  | |   |   |
#  *-*---*---*	(2.) verts_outer_base
#    |   |   |
#    *---*---*	(3.) verts_middle_tooth
#     \  |  /
#      *-*-*	(4.) verts_tip_tooth
#
# a
# t
# d
# radius
# Ad
# De
# base
# p_angle
# rack
# crown
def add_tooth(a, t, d, radius, Ad, De, base, p_angle, rack=0, crown=0.0):
    A = [a, a + t / 4, a + t / 2, a + 3 * t / 4]
    C = [cos(i) for i in A]
    S = [sin(i) for i in A]

    Ra = radius + Ad
    Rd = radius - De
    Rb = Rd - base

    # Pressure angle calc
    O = Ad * tan(p_angle)
    if Ra: # prevent div 0 error - useless parameter...
        p_angle = atan(O / Ra)

    if radius < 0:
        p_angle = -p_angle

    if rack:
        S = [sin(t / 4) * I for I in range(-2, 3)]
        Sp = [0, sin(-t / 4 + p_angle), 0, sin(t / 4 - p_angle)]

        verts_inner_base = [(Rb, radius * S[I], d) for I in range(4)]
        verts_outer_base = [(Rd, radius * S[I], d) for I in range(4)]
        verts_middle_tooth = [(radius, radius * S[I], d) for I in range(1, 4)]
        verts_tip_tooth = [(Ra, radius * Sp[I], d) for I in range(1, 4)]

    else:
        Cp = [
            0,
            cos(a + t / 4 + p_angle),
            cos(a + t / 2),
            cos(a + 3 * t / 4 - p_angle)]
        Sp = [0,
            sin(a + t / 4 + p_angle),
            sin(a + t / 2),
            sin(a + 3 * t / 4 - p_angle)]

        verts_inner_base = [(Rb * C[I], Rb * S[I], d)
            for I in range(4)]
        verts_outer_base = [(Rd * C[I], Rd * S[I], d)
            for I in range(4)]
        verts_middle_tooth = [(radius * C[I], radius * S[I], d + crown / 3)
            for I in range(1, 4)]
        verts_tip_tooth = [(Ra * Cp[I], Ra * Sp[I], d + crown)
            for I in range(1, 4)]

    return (verts_inner_base, verts_outer_base, verts_middle_tooth, verts_tip_tooth)


# Create column geometry.
# Returns:
# * A list of vertices
# * A list of faces
# * A list (group) of vertices of the tip
# * A list (group) of vertices of the valley
#
#     radius	area of the column, negative for flutes (else extrusions).
#     sectors	surfaces (faces) on column, 1 = square, increase to smooth, max 360, 180 is plenty.
#     segNum	number of segments (rows - vertical blocks) for column. Use +1 to complete row (2 is working min).
#     flutes	make curfs, gouges, gear like indents... true/false.
# Ad ... Addendum, extent of tooth above radius.
# De ... Dedendum, extent of tooth below radius.
# width ... Width, thickness of flute.
# crown ... Inward pointing extend of crown teeth.
#
# @todo: Fix teethNum. Some numbers are not possible yet.
# @todo: Create start & end geoemetry (closing faces)
def add_column(radius, sectors, segNum, flutes, Ad, De, p_angle, width, skew, crown):

    numFlutes = 0
    isFluted = False

    t = 2 * pi / sectors # sectors == 1 makes a square

    verts = []
    faces = []
    vgroup_top = []  # Vertex group of top/tip? vertices.
    vgroup_valley = []  # Vertex group of valley vertices

    #width = width / 2.0

    edgeloop_prev = []
    for Row in range(segNum):
        edgeloop = []

        for faceCnt in range(sectors):
            a = faceCnt * t

            s = Row * skew
            d = Row * width

            if flutes and not numFlutes % sectors: # making "flutes", and due a flute?
                numFlutes + 1
                isFluted = True

                verts1, verts2, verts3, verts4 = add_tooth(a + s, t, d,
                    radius, Ad, De, 0, 0, 0, crown)

                # Remove various unneeded verts (if we are "inside" the tooth)
                del(verts2[2])  # Central vertex in the base of the tooth.
                del(verts3[1])  # Central vertex in the middle of the tooth.

            else: # column surface for section...
                isFluted = False
                verts1, verts2, verts3, verts4 = add_tooth(a + s, t, d,
                    radius - De, 0.0, 0.0, 0, p_angle)

                # Ignore other verts than the "other base".
                verts1 = verts3 = verts4 = []

            vertsIdx2 = list(range(len(verts), len(verts) + len(verts2)))
            verts.extend(verts2)
            vertsIdx3 = list(range(len(verts), len(verts) + len(verts3)))
            verts.extend(verts3)
            vertsIdx4 = list(range(len(verts), len(verts) + len(verts4)))
            verts.extend(verts4)

            if isFluted:
                verts_current = []
                verts_current.extend(vertsIdx2[:2])
                verts_current.append(vertsIdx3[0])
                verts_current.extend(vertsIdx4)
                verts_current.append(vertsIdx3[-1])
                verts_current.append(vertsIdx2[-1])

                # Valley = first 2 vertices of outer base:
                vgroup_valley.extend(vertsIdx2[:1])
                # Top/tip vertices:
                vgroup_top.extend(vertsIdx4)

            else: # Flat
                verts_current = vertsIdx2
                vgroup_valley.extend(vertsIdx2) # Valley - all of them

            edgeloop.extend(verts_current)

        # Create faces between rings/rows.
        if edgeloop_prev:
            faces_row = createFaces(edgeloop, edgeloop_prev, closed=True)
            faces.extend(faces_row)

        # Remember last ring/row of vertices for next ring/row iteration.
        edgeloop_prev = edgeloop

    return verts, faces, vgroup_top, vgroup_valley


class AddColumn(bpy.types.Operator):
    '''Add a column mesh.'''
    bl_idname = "mesh.primitive_column"
    bl_label = "Add Column"
    bl_options = {'REGISTER', 'UNDO'}

    radius = FloatProperty(name="Radius",
        description="Radius of the column",
        min=0.01,
        max=100.0,
        default=0.5)
    column_segs = IntProperty(name="Segments",
        description="Number of segments (faces) in the column",
        min=1,
        max=360,
        default=10)
    column_blocks = IntProperty(name="Rows",
        description="Number of blocks in the column",
        min=1,
        max=100,
        default=2)
    row_height = FloatProperty(name="Row Height",
        description="Height of each block row",
        min=0.05,
        max=100.0,
        default=2)
    flutes = BoolProperty(name="Flutes",
         description="Channels on column",
         default = False)
    addendum = FloatProperty(name="Addendum",
        description="Addendum, extent of tooth above radius",
        min=0.01,
        max=100.0,
        default=0.1)
    dedendum = FloatProperty(name="Dedendum",
        description="Dedendum, extent of tooth below radius",
        min=0.0,
        max=100.0,
        default=0.0)
    angle = FloatProperty(name="Pressure Angle",
        description="Pressure angle, skewness of tooth tip (degrees)",
        min=0.0,
        max=45.0,
        default=20.0)
    skew = FloatProperty(name="Skew",
        description="Twist the column (degrees) - neg for left twist.",
        min=-180,
        max=180,
        default=0.00)
    crown = FloatProperty(name="Crest",
        description="Extend flutes at top of column.",
        min=0.0,
        max=100.0,
        default=0.0)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, 'radius')
        box.prop(self, 'column_segs')
        box.prop(self, 'column_blocks')
        box.prop(self, 'row_height')
        box.prop(self, 'flutes')
        box = layout.box()
        box.prop(self, 'addendum')
        box.prop(self, 'dedendum')
        box = layout.box()
        box.prop(self, 'angle')
        box.prop(self, 'skew')
        box.prop(self, 'crown')

    def execute(self, context):

        verts, faces, verts_tip, verts_valley = add_column(
            -self.radius, # use neg to get "flutes" based on "gear" function.
            self.column_segs, # "faces" on column, 1 = square.
            self.column_blocks + 1, # need extra to complete row :)
            self.flutes,
            self.addendum,
            self.dedendum,
            radians(self.angle),
            width=self.row_height,
            skew=radians(self.skew),
            crown=self.crown)

        scene = context.scene

        # Deselect all objects.
        bpy.ops.object.select_all(action='DESELECT')

        # Create new mesh
        mesh = bpy.data.meshes.new("Column")

        # Make a mesh from a list of verts/edges/faces.
        mesh.from_pydata(verts, [], faces)

        mesh.update()

        ob_new = bpy.data.objects.new("Column", mesh)
        scene.objects.link(ob_new)
# leave this out to prevent 'Tab key" going into edit mode :):):)
# Use rmb click to select and still modify.
        scene.objects.active = ob_new
        ob_new.select = True

        ob_new.location = tuple(context.scene.cursor_location)
        ob_new.rotation_quaternion = [1.0,0.0,0.0,0.0]

        # Create vertex groups from stored vertices.
        tipGroup = ob_new.vertex_groups.new('Tips')
        tipGroup.add(verts_tip, 1.0, 'ADD')

        valleyGroup = ob_new.vertex_groups.new('Valleys')
        valleyGroup.add(verts_valley, 1.0, 'ADD')

        return {'FINISHED'}


class INFO_MT_mesh_columns_add(bpy.types.Menu):
    # Define the "Columns" menu
    bl_idname = "INFO_MT_mesh_columns_add"
    bl_label = "Columns"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.primitive_column", text="Column")


# Define "Columns" menu
def menu_func(self, context):
    self.layout.menu("INFO_MT_mesh_columns_add", icon="PLUGIN")


def register():
    bpy.utils.register_module(__name__)

    # Add entry to the "Add Mesh" menu.
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    # Remove entry from the "Add Mesh" menu.
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
