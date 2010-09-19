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


"""
Bridge

How to use:
- Select a mesh and go into editmode
- Select two or more edge-loops
- Press Ctrl+F
- Select the Bridge option
"""


bl_addon_info = {
    'name': 'Bridge',
    'author': 'Bartius Crouch',
    'version': (1,1,0),
    'blender': (2,5,4),
    'api': 31878,
    'location': 'View3D > Ctrl+F > Bridge',
    'warning': '', # used for warning icon and text in addons panel
    'description': 'Connect two or more loops of vertices.',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:Py/'\
         'Scripts/',
    'tracker_url': 'https://projects.blender.org/tracker/index.php?'\
	    'func=detail&aid=23889&group_id=153&atid=467',
    'category': 'Mesh'}


import bpy
import mathutils


# gather initial data
def initialise():
    global_undo = bpy.context.user_preferences.edit.use_global_undo
    bpy.context.user_preferences.edit.use_global_undo = False
    bpy.ops.object.mode_set(mode = 'OBJECT')
    mesh = bpy.context.active_object.data
    return global_undo, mesh


# clean up and set settings back to original state
def terminate(global_undo):
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.context.user_preferences.edit.use_global_undo = global_undo


# return a list of 2 non-connected loops (vertex indices), or False
def get_selection(mesh):
    selected_edges = [edge.key for edge in mesh.edges if edge.select and not edge.hide]
    vert_connections = {}
    loops = []
    # dict with vertex index as key, list of connected vertices as value
    for key in selected_edges:
        for i in range(2):
            if key[i] not in vert_connections:
                vert_connections[key[i]] = [key[1-i]]
            else:
                if len(vert_connections[key[i]]) == 2:
                    return False
                vert_connections[key[i]].append(key[1-i])

    while len(vert_connections) > 0:
        loop = [iter(vert_connections.keys()).__next__()]
        growing = True
        sides_left = True
        
        while growing:
            # no more connection data for current vertex
            if loop[-1] not in vert_connections:
                if sides_left == True:
                    loop.reverse()
                    sides_left = False
                else:
                    growing = False
            # test first possible connection
            elif vert_connections[loop[-1]][-1] not in loop:
                new_vert = vert_connections[loop[-1]].pop()
                if len(vert_connections[loop[-1]]) == 0:
                    del vert_connections[loop[-1]]
                if new_vert in vert_connections:
                    # remove connection both ways
                    if loop[-1] in vert_connections[new_vert]:
                        if len(vert_connections[new_vert]) == 1:
                            del vert_connections[new_vert]
                        else:
                            vert_connections[new_vert].remove(loop[-1])
                loop.append(new_vert)
            # test second possible connection
            elif len(vert_connections[loop[-1]]) > 1:
                if vert_connections[loop[-1]][-2] not in loop:
                    new_vert = vert_connections[loop[-1]].pop(-2)
                    if len(vert_connections[loop[-1]]) == 0:
                        del vert_connections[loop[-1]]
                    if new_vert in vert_connections:
                        # remove connection both ways
                        if loop[-1] in vert_connections[new_vert]:
                            if len(vert_connections[new_vert]) == 1:
                                del vert_connections[new_vert]
                            else:
                                vert_connections[new_vert].remove(loop[-1])
                    loop.append(new_vert)
            # found one end of the loop, continue with next
            elif sides_left == True:
                loop.reverse()
                sides_left = False
            # found both ends of the loop, stop growing
            elif sides_left == False:
                growing = False

        # check for circular
        if loop[0] in vert_connections:
            if loop[-1] in vert_connections[loop[0]]:
                # is circular
                if len(vert_connections[loop[0]]) == 1:
                    del vert_connections[loop[0]]
                else:
                    vert_connections[loop[0]].remove(loop[-1])
                if len(vert_connections[loop[-1]]) == 1:
                    del vert_connections[loop[-1]]
                loop = [loop, True]
            else:
                # not circular
                loop = [loop, False]
        else:
            # not circular
            loop = [loop, False]
        
        loops.append(loop)
    
    if len(loops) < 2:
        # can't bridge if there is only 1 loop (or none)
        return False
    else:
        return loops


# sort loops, so they are connected in the correct order when lofting
def sort_loops(mesh, loops, loft_loop):
    # simplify loops to single points, and prepare for pathfinding
    x, y, z = [[sum([mesh.vertices[i].co[j] for i in loop[0]]) / len(loop[0]) for loop in loops] for j in range(3)]
    nodes = [mathutils.Vector([x[i], y[i], z[i]]) for i in range(len(loops))]
    
    active_node = 0
    open = [i for i in range(1, len(loops))]
    path = [[0,0]]
    # connect node to path, that is shortest to active_node
    while len(open) > 0:
        distances = [(nodes[active_node] - nodes[i]).length for i in open]
        active_node = open[distances.index(min(distances))]
        open.remove(active_node)
        path.append([active_node, min(distances)])
    # check if we didn't start in the middle of the path
    for i in range(2, len(path)):
        if (nodes[path[i][0]]-nodes[0]).length < path[i][1]:
            temp = path[:i]
            path.reverse()
            path = path[:-i] + temp
            break
    
    # reorder loops
    loops = [loops[i[0]] for i in path]
    # if requested, duplicate first loop at last position, so loft can loop
    if loft_loop:
        loops = loops + [loops[0]]
    return loops


# calculate faces (list of lists, vertex indices) that need to be added
def calculate_faces(mesh, loops, mode, reverse):
    faces = []
    loop1, loop2 = [i[0] for i in loops]
    loop1_circular, loop2_circular = [i[1] for i in loops]
    circular = loop1_circular or loop2_circular
    circle_full = False
    
    # if circular, rotate loops so they are aligned
    if circular:
        # make sure loop1 is the circular one (or both are circular)
        if loop2_circular and not loop1_circular:
            loop1_circular, loop2_circular = True, False
            loop1, loop2 = loop2, loop1

        # match start vertex of loop1 with loop2
        distance_to_start1 = [(mathutils.Vector(mesh.vertices[loop1[i]].co) - mathutils.Vector(mesh.vertices[loop2[0]].co)).length for i in range(len(loop1))]
        start1 = distance_to_start1.index(min(distance_to_start1))
        loop1 = loop1[start1:] + loop1[:start1]
        # if loop2 is also circular, check if loop2 also has to be shifted
        if loop2_circular:
            distance_to_start2 = [(mathutils.Vector(mesh.vertices[loop1[0]].co) - mathutils.Vector(mesh.vertices[loop2[i]].co)).length for i in range(len(loop2))]
            start2 = distance_to_start2.index(min(distance_to_start2))
            if min(distance_to_start2) < min(distance_to_start1):
                loop2 = loop2[start2:] + loop2[:start2]
        # make sure loop1 is the longest one
        if len(loop2) > len(loop1):
            loop1, loop2 = loop2, loop1
            loop1_circular, loop2_circular = loop2_circular, loop1_circular
        # have both loops face the same way
        second_to_first, second_to_second, second_to_last = [(mathutils.Vector(mesh.vertices[loop1[1]].co) - mathutils.Vector(mesh.vertices[loop2[i]].co)).length for i in [0, 1, -1]]
        last_to_first, last_to_second = [(mathutils.Vector(mesh.vertices[loop1[-1]].co) - mathutils.Vector(mesh.vertices[loop2[i]].co)).length for i in [0, 1]]
        if (min(last_to_first, last_to_second) < min(second_to_first, second_to_second)) or \
        (loop2_circular and second_to_last < min(second_to_first, second_to_second)):
            if loop1_circular:
                loop1.reverse()
                loop1 = [loop1[-1]] + loop1[:-1]
            else:
                # set the circular loop to loop1 again
                loop2.reverse()
                loop2 = [loop2[-1]] + loop2[:-1]
                loop1_circular, loop2_circular = True, False
                loop1, loop2 = loop2, loop1
    
    # both loops have same length
    if len(loop1) == len(loop2):
        if not circular: # circular loops are already aligned correctly
            # have both loops face the same way
            length1 = sum([(mathutils.Vector(mesh.vertices[loop1[i]].co) - mathutils.Vector(mesh.vertices[loop2[i]].co)).length for i in range(len(loop1))])
            loop1.reverse()
            length2 = sum([(mathutils.Vector(mesh.vertices[loop1[i]].co) - mathutils.Vector(mesh.vertices[loop2[i]].co)).length for i in range(len(loop1))])
            if length1 < length2:
                loop1.reverse()
        
        # manual override
        if reverse:
            loop1.reverse()
        
        for i in range(len(loop1) - 1):
            faces.append([loop1[i], loop1[i+1], loop2[i+1], loop2[i]])
    
    # loops of different lengths
    else:
        # make loop1 longest loop
        if len(loop2) > len(loop1):
            loop1, loop2 = loop2, loop1
            loop1_circular, loop2_circular = loop2_circular, loop1_circular
        if not circular: # circular loops are already aligned correctly
            # have both loops face the same way
            lengths1 = [(mathutils.Vector(mesh.vertices[loop1[i]].co) - mathutils.Vector(mesh.vertices[loop2[i]].co)).length for i in [-1, 0]]
            loop1.reverse()
            lengths2 = [(mathutils.Vector(mesh.vertices[loop1[i]].co) - mathutils.Vector(mesh.vertices[loop2[i]].co)).length for i in [-1, 0]]
            if sum(lengths1) < sum(lengths2):
                loop1.reverse()
                lengths2 = lengths1
            # start of loop (index) should give shortest edge
            if lengths2[1] > lengths2[0]:
                loop1.reverse()
                loop2.reverse()
        
        # manual override
        if reverse:
            loop1.reverse()
        
        # shortest distance doesn't always give correct start vertex
        if loop1_circular and not loop2_circular:
            shifting = 1
            while shifting:
                if len(loop1) - shifting < len(loop2):
                    shifting = False
                    break
                to_last, to_first = [(mathutils.Vector(mesh.vertices[loop1[-1]].co) - mathutils.Vector(mesh.vertices[loop2[i]].co)).length for i in [-1, 0]]
                if to_first < to_last:
                    loop1 = [loop1[-1]] + loop1[:-1]
                    shifting += 1
                else:
                    shifting = False
                    break

        # basic shortest side first
        if mode == 'basic':
            for i in range(len(loop1) -1):
                if i >= len(loop2) - 1:
                    # triangles
                    faces.append([loop1[i], loop1[i+1], loop2[-1], loop1[i]])
                else:
                    # quads
                    faces.append([loop1[i], loop1[i+1], loop2[i+1], loop2[i]])
        
        # shortest edge algorithm
        else: # mode == 'shortest'
            prev_vert2 = 0
            for i in range(len(loop1) -1):
                if prev_vert2 == len(loop2) - 1 and not loop2_circular:
                    # force triangles, reached end of loop2
                    tri, quad = 0, 1
                elif prev_vert2 == len(loop2) - 1 and loop2_circular:
                    # at end of loop2, but circular, so check with first vertex
                    tri, quad = [(mathutils.Vector(mesh.vertices[loop1[i+1]].co) - mathutils.Vector(mesh.vertices[loop2[j]].co)).length for j in [prev_vert2, 0]]
                    circle_full = 2
                elif len(loop1) - 1 - i == len(loop2) - 1 - prev_vert2 and not circle_full:
                    # force quads, otherwise won't make it to end of loop2
                    tri, quad = 1, 0
                else:
                    # calculate if tri or quad gives shortest edge
                    tri, quad = [(mathutils.Vector(mesh.vertices[loop1[i+1]].co) - mathutils.Vector(mesh.vertices[loop2[j]].co)).length for j in range(prev_vert2, prev_vert2+2)]
                
                # triangle
                if tri < quad:
                    faces.append([loop1[i], loop1[i+1], loop2[prev_vert2], loop1[i]])
                    if circle_full == 2:
                        circle_full = False
                # quad
                elif not circle_full:
                    faces.append([loop1[i], loop1[i+1], loop2[prev_vert2+1], loop2[prev_vert2]])
                    prev_vert2 += 1
                # quad to first vertex of loop2
                else:
                    faces.append([loop1[i], loop1[i+1], loop2[0], loop2[prev_vert2]])
                    prev_vert2 = 0
                    circle_full = True
    
    # final face for circular loops
    if loop1_circular and loop2_circular:
        if circle_full:
            faces.append([loop1[-1], loop1[0], loop2[0], loop2[0]])
        else:
            faces.append([loop1[-1], loop1[0], loop2[0], loop2[-1]])
    
    return faces


# add faces to mesh
def create_faces(mesh, faces):
    # eekadoodle prevention
    for i in range(len(faces)):
        if not faces[i][-1]:
            if faces[i][0] == faces[i][-1]:
                faces[i] = [faces[i][1], faces[i][2], faces[i][3], faces[i][1]]
            else:
                faces[i] = [faces[i][-1]] + faces[i][:-1]

    start_faces = len(mesh.faces)
    mesh.faces.add(len(faces))
    for i in range(len(faces)):
        mesh.faces[start_faces + i].vertices_raw = faces[i]
    mesh.update(calc_edges=True) # calc_edges prevents memory-corruption
    

# operator class
class bridge(bpy.types.Operator):
    bl_idname = 'mesh.bridge'
    bl_label = "Bridge"
    bl_description = "Connect two loops of vertices with faces"
    bl_options = {'REGISTER', 'UNDO'}

    option1_mode = bpy.props.EnumProperty(items = (('basic', "Basic", "Fast algorithm"), ('shortest', "Shortest edge", "Slower algorithm with better vertex matching")),
                        name = "Mode",
                        description = "Algorithm used for bridging",
                        default = 'shortest')
    option2_loft_loop = bpy.props.BoolProperty(name = "Loft: loop",
                        description = "When lofting, connect the first and the last loop with each other",
                        default = False)
    option3_reverse = bpy.props.BoolProperty(name = "Reverse",
                        description = "Manually override the direction in which the loops are bridged. Only use if the tool gives the wrong result.",
                        default = False)
    
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')

    def execute(self, context):
        global_undo, mesh = initialise()
        # get loops
        loops = get_selection(mesh)
        if loops:
            # order loops for lofting
            if len(loops) > 2:
                loops = sort_loops(mesh, loops, self.option2_loft_loop)
            # calculate faces
            faces = []
            for i in range(1, len(loops)):
                new_faces = calculate_faces(mesh, loops[i-1:i+1], self.option1_mode, self.option3_reverse)
                if new_faces:
                    faces += new_faces
            # create faces
            if faces:
                create_faces(mesh, faces)
        
        terminate(global_undo)
        return{'FINISHED'}


# draw function for menu integration
menu_func = (lambda self, context: self.layout.operator("mesh.bridge"))


# integrate operator in menu
def register():
    bpy.types.VIEW3D_MT_edit_mesh_faces.prepend(menu_func)


# remove operator from menu
def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_faces.remove(menu_func)


if __name__ == '__main__':
    bpy.ops.mesh.bridge(option1_mode='shortest')
