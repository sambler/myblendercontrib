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
    'name': 'Bridge',
    'author': 'Bartius Crouch',
    'version': (1, 4, 7),
    'blender': (2, 5, 7),
    'api': 34674,
    'location': 'View3D > Ctrl+F > Bridge',
    'warning': '',
    'description': 'Bridge two, or loft several, loops of vertices.',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/'\
        'Scripts/Modeling/Bridge',
    'tracker_url': 'http://projects.blender.org/tracker/index.php?'\
        'func=detail&aid=23889',
    'category': 'Mesh'}

"""
Bridge

How to use:
- Select a mesh and go into editmode
- Select two or more edge-loops
- Press Ctrl+F
- Select the Bridge or Loft option
"""


import bpy
import mathutils


# gather initial data
def initialise(interpolation):
    global_undo = bpy.context.user_preferences.edit.use_global_undo
    bpy.context.user_preferences.edit.use_global_undo = False
    bpy.ops.object.mode_set(mode = 'OBJECT')
    mesh = bpy.context.active_object.data
    old_selected_faces = [face.index for face in mesh.faces if face.select and not face.hide]
    
    smooth = False
    if mesh.faces:
        if sum([face.use_smooth for face in mesh.faces])/len(mesh.faces) >= 0.5:
            smooth = True

    if interpolation == 'cubic':
        # dictionary with the edge-key as key
        # and a list of connected valid faces as value
        face_blacklist = [face.index for face in mesh.faces if face.select or face.hide]
        edge_faces = dict([[edge.key, []] for edge in mesh.edges if not edge.hide])
        for face in mesh.faces:
            if face.index in face_blacklist:
                continue
            for key in face.edge_keys:
                edge_faces[key].append(face)
        # dictionary with the edge-key as key and edge as value
        edgekey_to_edge = dict([[edge.key, edge] for edge in mesh.edges if edge.select and not edge.hide])
    else:
        edge_faces = False
        edgekey_to_edge = False
    
    return global_undo, mesh, old_selected_faces, smooth, edge_faces, edgekey_to_edge


# clean up and set settings back to original state
def terminate(global_undo):
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.context.user_preferences.edit.use_global_undo = global_undo


# return a list of 2 non-connected loops (vertex indices), or False
def get_selection(mesh):
    # create list of internal edges, which should be skipped
    eks_of_selected_faces = [item for sublist in [face.edge_keys for face in mesh.faces if face.select and not face.hide] for item in sublist]
    edge_count = {}
    for ek in eks_of_selected_faces:
        if ek in edge_count:
            edge_count[ek] += 1
        else:
            edge_count[ek] = 1
    internal_edges = [ek for ek in edge_count if edge_count[ek]>1]
    
    selected_edges = [edge.key for edge in mesh.edges if edge.select and not edge.hide and edge.key not in internal_edges]
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
            else:
                extended = False
                for connection_index, connecting_vertex in enumerate(vert_connections[loop[-1]]):
                    if connecting_vertex not in loop:
                        vert_connections[loop[-1]].pop(connection_index)
                        if len(vert_connections[loop[-1]]) == 0:
                            del vert_connections[loop[-1]]
                        # remove connection both ways
                        if connecting_vertex in vert_connections:
                            if len(vert_connections[connecting_vertex]) == 1:
                                del vert_connections[connecting_vertex]
                            else:
                                vert_connections[connecting_vertex].remove(loop[-1])
                        loop.append(connecting_vertex)
                        extended = True
                        break
                if not extended:
                    # found one end of the loop, continue with next
                    if sides_left == True:
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
                else:
                    vert_connections[loop[-1]].remove(loop[-1])
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


# match up loops in pairs, used for multi-input bridging
def match_loops(mesh, loops):
    # calculate average loop normals and centers
    normals = []
    centers = []
    for vertices, circular in loops:
        normal = mathutils.Vector([0, 0, 0])
        center = mathutils.Vector([0, 0, 0])
        for vertex in vertices:
            normal += mesh.vertices[vertex].normal
            center += mesh.vertices[vertex].co
        normals.append(normal / len(vertices) / 10)
        centers.append(center / len(vertices))
    
    # possible matches if loop normals are faced towards the center of the other loop
    matches = dict([[i, []] for i in range(len(loops))])
    matches_amount = 0
    for i in range(len(loops) + 1):
        for j in range(i+1, len(loops)):
            if (centers[i] - centers[j]).length > (centers[i] - (centers[j] + normals[j])).length and \
            (centers[j] - centers[i]).length > (centers[j] - (centers[i] + normals[i])).length:
                matches_amount += 1
                matches[i].append([(centers[i] - centers[j]).length, i, j])
                matches[j].append([(centers[i] - centers[j]).length, j, i])
    # if no loops face each other, just make matches between all the loops
    if matches_amount == 0:
        for i in range(len(loops) + 1):
            for j in range(i+1, len(loops)):
                matches[i].append([(centers[i] - centers[j]).length, i, j])
                matches[j].append([(centers[i] - centers[j]).length, j, i])
    for key, value in matches.items():
        value.sort()

    # make matches based on distance between centers and number of vertices in loops
    new_order = []
    for loop_index in range(len(loops)):
        if loop_index in new_order:
            continue
        loop_matches = matches[loop_index]
        if not loop_matches:
            continue
        shortest_distance = loop_matches[0][0]
        shortest_distance *= 1.1
        loop_matches = [[abs(len(loops[loop_index][0])-len(loops[loop[2]][0])), loop[0], loop[1], loop[2]] for loop in loop_matches if loop[0] < shortest_distance]
        loop_matches.sort()
        for match in loop_matches:
            if match[3] not in new_order:
                new_order += [loop_index, match[3]]
                break
    
    # reorder loops based on matches
    if len(new_order) >= 2:
        loops = [loops[i] for i in new_order]
    
    return loops


# calculate lines (list of lists, vertex indices) that are used for bridging
def calculate_lines(mesh, loops, mode, twist, reverse):
    lines = []
    loop1, loop2 = [i[0] for i in loops]
    loop1_circular, loop2_circular = [i[1] for i in loops]
    circular = loop1_circular or loop2_circular
    circle_full = False
    
    # calculate loop centers
    centers = []
    for loop in [loop1, loop2]:
        center = mathutils.Vector([0,0,0])
        for vertex in loop:
            center += mesh.vertices[vertex].co
        center /= len(loop)
        centers.append(center)
    for i, loop in enumerate([loop1, loop2]):
        for vertex in loop:
            if mesh.vertices[vertex].co == centers[i]:
                # prevent zero-length vectors from appearing in angle comparisons
                centers[i] += mathutils.Vector([0.01, 0, 0])
                break
    center1, center2 = centers
    
    # calculate the normals of the virtual planes that the loops are on
    normals = []
    normal_plurity = False
    for i, loop in enumerate([loop1, loop2]):
        # covariance matrix
        mat = mathutils.Matrix(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
        x, y, z = centers[i]
        for loc in [mesh.vertices[vertex].co for vertex in loop]:
            mat[0][0] += (loc[0]-x)**2
            mat[0][1] += (loc[0]-x)*(loc[1]-y)
            mat[0][2] += (loc[0]-x)*(loc[2]-z)
            mat[1][0] += (loc[1]-y)*(loc[0]-x)
            mat[1][1] += (loc[1]-y)**2
            mat[1][2] += (loc[1]-y)*(loc[2]-z)
            mat[2][0] += (loc[2]-z)*(loc[0]-x)
            mat[2][1] += (loc[2]-z)*(loc[1]-y)
            mat[2][2] += (loc[2]-z)**2
        # plane normal
        normal = False
        if sum(mat[0]) < 1e-6 or sum(mat[1]) < 1e-6 or sum(mat[2]) < 1e-6:
            normal_plurity = True
        try:
            mat.invert()
        except:
            if sum(mat[0]) == 0:
                normal = mathutils.Vector([1.0, 0.0, 0.0])
            elif sum(mat[1]) == 0:
                normal = mathutils.Vector([0.0, 1.0, 0.0])
            elif sum(mat[2]) == 0:
                normal = mathutils.Vector([0.0, 0.0, 1.0])
        if not normal:
            itermax = 500
            iter = 0
            vec = mathutils.Vector([1.0, 1.0, 1.0])
            vec2 = (vec*mat)/(vec*mat).length
            while vec != vec2 and iter<itermax:
                iter+=1
                vec = vec2
                vec2 = (vec*mat)/(vec*mat).length
            normal = vec2
        normals.append(normal)
    # have plane normals face in the same direction (maximum angle is 90 degrees)
    if ((center1 + normals[0]) - center2).length < ((center1 - normals[0]) - center2).length:
        normals[0].negate()
    if ((center2 + normals[1]) - center1).length > ((center2 - normals[1]) - center1).length:
        normals[1].negate()
    
    # calculate rotation matrix, representing the difference between the plane normals
    axis = normals[0].cross(normals[1])
    axis = mathutils.Vector([loc if abs(loc) > 1e-8 else 0 for loc in axis])
    if axis.angle(mathutils.Vector([0, 0, 1]), 0) > 1.5707964:
        axis.negate()
    angle = normals[0].dot(normals[1])
    rotation_matrix = mathutils.Matrix.Rotation(angle, 4, axis)
    
    # if circular, rotate loops so they are aligned
    if circular:
        # make sure loop1 is the circular one (or both are circular)
        if loop2_circular and not loop1_circular:
            loop1_circular, loop2_circular = True, False
            loop1, loop2 = loop2, loop1
        
        # match start vertex of loop1 with loop2
        target_vector = mesh.vertices[loop2[0]].co - center2
        dif_angles = [[((mesh.vertices[vertex].co - center1) * rotation_matrix).angle(target_vector, 0), False, i] for i, vertex in enumerate(loop1)]
        dif_angles.sort()
        if len(loop1) != len(loop2):
            angle_limit = dif_angles[0][0] * 1.2 # 20% margin
            dif_angles = [[(mesh.vertices[loop2[0]].co - mesh.vertices[loop1[index]].co).length, angle, index] for angle, distance, index in dif_angles if angle <= angle_limit]
            dif_angles.sort()
        loop1 = loop1[dif_angles[0][2]:] + loop1[:dif_angles[0][2]]
    
    # have both loops face the same way
    if normal_plurity and not circular:
        second_to_first, second_to_second, second_to_last = [(mesh.vertices[loop1[1]].co - center1).angle(mesh.vertices[loop2[i]].co - center2) for i in [0, 1, -1]]
        last_to_first, last_to_second = [(mesh.vertices[loop1[-1]].co - center1).angle(mesh.vertices[loop2[i]].co - center2) for i in [0, 1]]
        if (min(last_to_first, last_to_second)*1.1 < min(second_to_first, second_to_second)) or \
        (loop2_circular and second_to_last*1.1 < min(second_to_first, second_to_second)):
            loop1.reverse()
            if circular:
                loop1 = [loop1[-1]] + loop1[:-1]
    else:
        angle = (mesh.vertices[loop1[0]].co - center1).cross(mesh.vertices[loop1[1]].co - center1).angle(normals[0])
        target_angle = (mesh.vertices[loop2[0]].co - center2).cross(mesh.vertices[loop2[1]].co - center2).angle(normals[1])
        limit = 1.5707964 # 0.5*pi, 90 degrees
        if not ((angle > limit and target_angle > limit) or (angle < limit and target_angle < limit)):
            loop1.reverse()
            if circular:
                loop1 = [loop1[-1]] + loop1[:-1]
    
    # both loops have the same length
    if len(loop1) == len(loop2):
        # manual override
        if twist:
            if abs(twist) < len(loop1):
                loop1 = loop1[twist:]+loop1[:twist]
        if reverse:
            loop1.reverse()
        
        lines.append([loop1[0], loop2[0]])
        for i in range(1, len(loop1)):
            lines.append([loop1[i], loop2[i]])
    
    # loops of different lengths
    else:
        # make loop1 longest loop
        if len(loop2) > len(loop1):
            loop1, loop2 = loop2, loop1
            loop1_circular, loop2_circular = loop2_circular, loop1_circular
        
        # manual override
        if twist:
            if abs(twist) < len(loop1):
                loop1 = loop1[twist:]+loop1[:twist]
        if reverse:
            loop1.reverse()
            
        # shortest angle difference doesn't always give correct start vertex
        if loop1_circular and not loop2_circular:
            shifting = 1
            while shifting:
                if len(loop1) - shifting < len(loop2):
                    shifting = False
                    break
                to_last, to_first = [((mesh.vertices[loop1[-1]].co - center1) * rotation_matrix).angle((mesh.vertices[loop2[i]].co - center2), 0) for i in [-1, 0]]
                if to_first < to_last:
                    loop1 = [loop1[-1]] + loop1[:-1]
                    shifting += 1
                else:
                    shifting = False
                    break
        
        # basic shortest side first
        if mode == 'basic':
            lines.append([loop1[0], loop2[0]])
            for i in range(1, len(loop1)):
                if i >= len(loop2) - 1:
                    # triangles
                    lines.append([loop1[i], loop2[-1]])
                else:
                    # quads
                    lines.append([loop1[i], loop2[i]])
        
        # shortest edge algorithm
        else: # mode == 'shortest'
            lines.append([loop1[0], loop2[0]])
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
                    lines.append([loop1[i+1], loop2[prev_vert2]])
                    if circle_full == 2:
                        circle_full = False
                # quad
                elif not circle_full:
                    lines.append([loop1[i+1], loop2[prev_vert2+1]])
                    prev_vert2 += 1
                # quad to first vertex of loop2
                else:
                    lines.append([loop1[i+1], loop2[0]])
                    prev_vert2 = 0
                    circle_full = True
    
    # final face for circular loops
    if loop1_circular and loop2_circular:
        lines.append([loop1[0], loop2[0]])
    
    return lines


# return dictionary with vertex index as key, and the normal vector as value
def calculate_virtual_vertex_normals(mesh, lines, loops, edge_faces, edgekey_to_edge):
    if not edge_faces: # interpolation isn't set to cubic
        return False
    
    # pity reduce() isn't one of the basic functions in python anymore
    def average_vector_dictionary(dic):
        for key, vectors in dic.items():
            #if type(vectors) == type([]) and len(vectors) > 1:
            if len(vectors) > 1:
                average = mathutils.Vector([0, 0, 0])
                for vector in vectors:
                    average += vector
                average /= len(vectors)
                dic[key] = [average]
        return dic
    
    # get all edges of the loop
    edges = [[edgekey_to_edge[tuple(sorted([loops[j][0][i], loops[j][0][i+1]]))] for i in range(len(loops[j][0])-1)] for j in [0,1]]
    edges = edges[0] + edges[1]
    for j in [0, 1]:
        if loops[j][1]: # circular
            edges.append(edgekey_to_edge[tuple(sorted([loops[j][0][0], loops[j][0][-1]]))])

    """ calculation based on face topology (assign edge-normals to vertices)
    
            edge_normal = face_normal x edge_vector
            vertex_normal = average(edge_normals)
    """
    vertex_normals = dict([(vertex, []) for vertex in loops[0][0]+loops[1][0]])
    for edge in edges:
        faces = edge_faces[edge.key] # valid faces connected to edge
        
        if faces:
            # get edge coordinates
            v1, v2 = [mesh.vertices[edge.key[i]].co for i in [0,1]]
            edge_vector = v1 - v2
            if edge_vector.length < 1e-4: # zero-length edge, vertices at same location
                continue
            edge_center = (v1 + v2) / 2
            
            # average the face coordinate values, if edge is connected to more than 1 valid face
            if len(faces) > 1:
                face_normal = mathutils.Vector([0, 0, 0])
                face_center = mathutils.Vector([0, 0, 0])
                for face in faces:
                    face_normal += face.normal
                    face_center += face.center
                face_normal /= len(faces)
                face_center /= len(faces)
            else:
                face_normal = faces[0].normal
                face_center = faces[0].center
            if face_normal.length < 1e-4: # faces with a surface of 0 have no face normal
                continue
            
            # calculate virtual edge normal
            edge_normal = edge_vector.cross(face_normal)
            edge_normal.length = 0.01
            if (face_center - (edge_center + edge_normal)).length > (face_center - (edge_center - edge_normal)).length:
                # make normal face the correct way
                edge_normal.negate()
            edge_normal.normalize()
            # add virtual edge normal as entry for both vertices it connects
            for vertex in edge.key:
                vertex_normals[vertex].append(edge_normal)
      
    """ calculation based on connection with other loop (vertex focused method) 
        - used for vertices that aren't connected to any valid faces
        
        plane_normal = edge_vector x connection_vector
        vertex_normal = plane_normal x edge_vector
    """
    vertices = [vertex for vertex, normal in vertex_normals.items() if not normal]
    
    if vertices:
        # edge vectors connected to vertices
        edge_vectors = dict([[vertex, []] for vertex in vertices])
        for edge in edges:
            for v in edge.key:
                if v in edge_vectors:
                    edge_vector = mesh.vertices[edge.key[0]].co - mesh.vertices[edge.key[1]].co
                    if edge_vector.length < 1e-4: # zero-length edge, vertices at same location
                        continue
                    edge_vectors[v].append(edge_vector)
    
        # connection vectors between vertices of both loops
        connection_vectors = dict([[vertex, []] for vertex in vertices])
        connections = dict([[vertex, []] for vertex in vertices])
        for v1, v2 in lines:
            if v1 in connection_vectors or v2 in connection_vectors:
                new_vector = mesh.vertices[v1].co - mesh.vertices[v2].co
                if new_vector.length < 1e-4: # zero-length connection vector, vertices in different loops at same location
                    continue
                if v1 in connection_vectors:
                    connection_vectors[v1].append(new_vector)
                    connections[v1].append(v2)
                if v2 in connection_vectors:
                    connection_vectors[v2].append(new_vector)
                    connections[v2].append(v1)
        connection_vectors = average_vector_dictionary(connection_vectors)
        connection_vectors = dict([[vertex, vector[0]] if vector else [vertex, []] for vertex, vector in connection_vectors.items()])
        
        for vertex, values in edge_vectors.items():
            # vertex normal doesn't matter, just assign a random vector to it
            if not connection_vectors[vertex]:
                vertex_normals[vertex] = [mathutils.Vector([1, 0, 0])]
                continue
            
            # calculate to what location the vertex is connected, used to determine what way to flip the normal
            connected_center = mathutils.Vector([0, 0, 0])
            for v in connections[vertex]:
                connected_center += mesh.vertices[v].co
            if len(connections[vertex]) > 1:
                connected_center /= len(connections[vertex])
            if len(connections[vertex]) == 0:
                # shouldn't be possible, but better safe than sorry
                vertex_normals[vertex] = [mathutils.Vector([1, 0, 0])]
                continue
                
            # can't do proper calculations, because of zero-length vector
            if not values:
                if (connected_center - (mesh.vertices[vertex].co + connection_vectors[vertex])).length < (connected_center - (mesh.vertices[vertex].co - connection_vectors[vertex])).length:
                    connection_vectors[vertex].negate()
                vertex_normals[vertex] = [connection_vectors[vertex].normalized()]
                continue
            
            # calculate vertex normals using edge-vectors, connection-vectors and the derived plane normal
            for edge_vector in values:
                plane_normal = edge_vector.cross(connection_vectors[vertex])
                vertex_normal = edge_vector.cross(plane_normal)
                vertex_normal.length = 0.1
                if (connected_center - (mesh.vertices[vertex].co + vertex_normal)).length < (connected_center - (mesh.vertices[vertex].co - vertex_normal)).length:
                # make normal face the correct way
                    vertex_normal.negate()
                vertex_normal.normalize()
                vertex_normals[vertex].append(vertex_normal)

    # average virtual vertex normals, based on all edges it's connected to
    vertex_normals = average_vector_dictionary(vertex_normals)
    vertex_normals = dict([[vertex, vector[0]] for vertex, vector in vertex_normals.items()])

    return vertex_normals


# calculate a cubic spline through the middle section of the 4 given coordinates
def calculate_cubic_spline(mesh, coordinates):
    result = []
    x = [0, 1, 2, 3]
    
    for j in range(3):
        a = []
        for i in coordinates:
            a.append(float(i[j]))
        h = []
        for i in range(3):
            h.append(x[i+1]-x[i])
        q = [False]
        for i in range(1,3):
            q.append(3.0/h[i]*(a[i+1]-a[i])-3.0/h[i-1]*(a[i]-a[i-1]))
        l = [1.0]
        u = [0.0]
        z = [0.0]
        for i in range(1,3):
            l.append(2.0*(x[i+1]-x[i-1])-h[i-1]*u[i-1])
            u.append(h[i]/l[i])
            z.append((q[i]-h[i-1]*z[i-1])/l[i])
        l.append(1.0)
        z.append(0.0)
        b = [False for i in range(3)]
        c = [False for i in range(4)]
        d = [False for i in range(3)]
        c[3] = 0.0
        for i in range(2,-1,-1):
            c[i] = z[i]-u[i]*c[i+1]
            b[i] = (a[i+1]-a[i])/h[i]-h[i]*(c[i+1]+2.0*c[i])/3.0
            d[i] = (c[i+1]-c[i])/(3.0*h[i])
        for i in range(3):
            result.append([a[i], b[i], c[i], d[i], x[i]])
    spline = [result[1], result[4], result[7]]

    return spline


# calculate number of segments needed
def calculate_segments(mesh, lines, loops, segments):
    # return if amount of segments is set by user
    if segments != 0:
        return segments
    
    # calculate average lengths
    average_edge_length = [(mesh.vertices[vertex].co - mesh.vertices[loop[0][i+1]].co).length for loop in loops for i, vertex in enumerate(loop[0][:-1])]
    average_edge_length += [(mesh.vertices[loop[0][-1]].co - mesh.vertices[loop[0][0]].co).length for loop in loops if loop[1]] # closing edges of circular loops
    average_edge_length = sum(average_edge_length) / len(average_edge_length)
    average_bridge_length = sum([(mesh.vertices[v1].co - mesh.vertices[v2].co).length for v1, v2 in lines]) / len(lines)

    segments = max(1, round(average_bridge_length / average_edge_length))
    return segments


# return a list with new vertex location vectors, a list with face vertex integers, and the highest vertex integer in the virtual mesh
def calculate_geometry(mesh, lines, vertex_normals, segments, interpolation, cubic_strength, min_width, max_vert_index):
    new_verts = []
    faces = []
    
    # calculate location based on interpolation method
    def get_location(line, segment, splines):
        v1 = mesh.vertices[lines[line][0]].co
        v2 = mesh.vertices[lines[line][1]].co
        if interpolation == 'linear':
            return v1 + (segment/segments) * (v2-v1)
        else: # interpolation == 'cubic'
            m = (segment/segments)
            ax,bx,cx,dx,tx = splines[line][0]
            x = ax+bx*m+cx*m**2+dx*m**3
            ay,by,cy,dy,ty = splines[line][1]
            y = ay+by*m+cy*m**2+dy*m**3
            az,bz,cz,dz,tz = splines[line][2]
            z = az+bz*m+cz*m**2+dz*m**3
            return mathutils.Vector([x,y,z])
        
    # no interpolation needed
    if segments == 1:
        for i, line in enumerate(lines):
            if i < len(lines)-1:
                faces.append([line[0], lines[i+1][0], lines[i+1][1], line[1]])
    # more than 1 segment, interpolate
    else:
        # calculate splines (if necessary), so they don't have to be recalculated all the time
        if interpolation == 'cubic':
            splines = []
            for line in lines:
                v1 = mesh.vertices[line[0]].co
                v2 = mesh.vertices[line[1]].co
                size = (v2-v1).length * cubic_strength
                splines.append(calculate_cubic_spline(mesh, [v1+size*vertex_normals[line[0]], v1, v2, v2+size*vertex_normals[line[1]]]))
        else:
            splines = False
        
        # create starting situation
        virtual_width = [(mathutils.Vector(mesh.vertices[lines[i][0]].co)-mathutils.Vector(mesh.vertices[lines[i+1][0]].co)).length for i in range(len(lines)-1)]
        new_verts = [get_location(0, seg, splines) for seg in range(1, segments)]
        first_line_indices = [i for i in range(max_vert_index+1, max_vert_index+segments)]
        
        prev_verts = new_verts[:] # vertex locations of verts on previous line
        prev_vert_indices = first_line_indices[:]
        max_vert_index += segments - 1 # highest vertex index in virtual mesh
        next_verts = [] # vertex locations of verts on current line
        next_vert_indices = []
        
        for i, line in enumerate(lines):
            if i < len(lines)-1:
                v1 = line[0]
                v2 = lines[i+1][0]
                end_face = True
                for seg in range(1, segments):
                    loc1 = prev_verts[seg-1]
                    loc2 = get_location(i+1, seg, splines)
                    if (loc1-loc2).length < (min_width/100)*virtual_width[i] and line[1]==lines[i+1][1]:
                        # triangle, no new vertex
                        faces.append([v1, v2, prev_vert_indices[seg-1], prev_vert_indices[seg-1]])
                        next_verts += prev_verts[seg-1:]
                        next_vert_indices += prev_vert_indices[seg-1:]
                        end_face = False
                        break
                    else:
                        if i == len(lines)-2 and lines[0] == lines[-1]:
                            # quad with first line, no new vertex
                            faces.append([v1, v2, first_line_indices[seg-1], prev_vert_indices[seg-1]])
                            v2 = first_line_indices[seg-1]
                            v1 = prev_vert_indices[seg-1]
                        else:
                            # quad, add new vertex
                            max_vert_index += 1
                            faces.append([v1, v2, max_vert_index, prev_vert_indices[seg-1]])
                            v2 = max_vert_index
                            v1 = prev_vert_indices[seg-1]
                            new_verts.append(loc2)
                            next_verts.append(loc2)
                            next_vert_indices.append(max_vert_index)
                if end_face:
                    faces.append([v1, v2, lines[i+1][1], line[1]])
                        
                prev_verts = next_verts[:]
                prev_vert_indices = next_vert_indices[:]
                next_verts = []
                next_vert_indices = []
    
    return new_verts, faces, max_vert_index


# add vertices to mesh
def create_vertices(mesh, vertices):
    start_index = len(mesh.vertices)
    mesh.vertices.add(len(vertices))
    for i in range(len(vertices)):
        mesh.vertices[start_index + i].co = vertices[i]


# add faces to mesh
def create_faces(mesh, faces, twist):
    # have the normal point the correct way
    if twist < 0:
        [face.reverse() for face in faces]
        faces = [face[2:]+face[:2] if face[0]==face[1] else face for face in faces]
    
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
    mesh.update(calc_edges = True) # calc_edges prevents memory-corruption


# add the newly created faces to the selection
def select_new_faces(mesh, amount, smooth):
    select_mode = [i for i in bpy.context.tool_settings.mesh_select_mode]
    bpy.context.tool_settings.mesh_select_mode = [False, False, True]
    for i in range(amount):
        mesh.faces[-(i+1)].select = True
        mesh.faces[-(i+1)].use_smooth = smooth
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.context.tool_settings.mesh_select_mode = select_mode


# update list of internal faces that are flagged for removal
def save_unused_faces(mesh, old_selected_faces, loops):
    # dictionary with vertex indices as keys and lists of selected faces using it as values
    vertex_to_face = dict([[i, []] for i in range(len(mesh.vertices))])
    [[vertex_to_face[vertex_index].append(face) for vertex_index in mesh.faces[face].vertices] for face in old_selected_faces]
    
    # group selected faces that are connected
    groups = []
    grouped_faces = []
    for face in old_selected_faces:
        if face in grouped_faces:
            continue
        grouped_faces.append(face)
        group = [face]
        new_faces = [face]
        while new_faces:
            grow_face = new_faces[0]
            for vertex in mesh.faces[grow_face].vertices:
                vertex_face_group = [face for face in vertex_to_face[vertex] if face not in grouped_faces]
                new_faces += vertex_face_group
                grouped_faces += vertex_face_group
                group += vertex_face_group
            new_faces.pop(0)
        groups.append(group)
    
    # dictionary with vertex indices as key and True/False as value, depending on whether they are in a loop that is used
    used_vertices = dict([[i, 0] for i in range(len(mesh.vertices))])
    for loop in loops:
        for vertex in loop[0]:
            used_vertices[vertex] = True
    
    # check if group is bridged, if not remove faces from list of internal faces
    for group in groups:
        used = False
        for face in group:
            if used:
                break
            for vertex in mesh.faces[face].vertices:
                if used_vertices[vertex]:
                    used = True
                    break
        if not used:
            for face in group:
                old_selected_faces.remove(face)


# remove old_selected_faces
def remove_internal_faces(mesh, old_selected_faces):
    select_mode = [i for i in bpy.context.tool_settings.mesh_select_mode]
    bpy.context.tool_settings.mesh_select_mode = [False, False, True]
    
    # hack to keep track of the current selection
    for edge in mesh.edges:
        if edge.select and not edge.hide:
            edge.bevel_weight = (edge.bevel_weight/3) + 0.2
        else:
            edge.bevel_weight = (edge.bevel_weight/3) + 0.6
    
    # remove faces
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')
    for face in old_selected_faces:
        mesh.faces[face].select = True
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.delete(type = 'FACE')
    
    # restore old selection, using hack
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.context.tool_settings.mesh_select_mode = [False, True, False]
    for edge in mesh.edges:
        if edge.bevel_weight < 0.6:
            edge.bevel_weight = (edge.bevel_weight-0.2) * 3
            edge.select = True
        else:
            edge.bevel_weight = (edge.bevel_weight-0.6) * 3
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.context.tool_settings.mesh_select_mode = select_mode
    

# have normals of selection face outside
def recalculate_normals():
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.normals_make_consistent()


# operator class
class bridge(bpy.types.Operator):
    bl_idname = 'mesh.bridge'
    bl_label = "Bridge / Loft"
    bl_description = "Bridge two, or loft several, loops of vertices"
    bl_options = {'REGISTER', 'UNDO'}

    mode = bpy.props.EnumProperty(items = (('basic', "Basic", "Fast algorithm"), ('shortest', "Shortest edge", "Slower algorithm with better vertex matching")),
                        name = "Mode",
                        description = "Algorithm used for bridging",
                        default = 'shortest')
    segments = bpy.props.IntProperty(name = "Segments",
                        description = "Number of segments used to bridge the gap",
                        default = 1,
                        min = 0,
                        soft_max = 20)
    min_width = bpy.props.IntProperty(name = "Minimum width",
                        description = "Segments with an edge smaller than this are merged (compared to base edge)",
                        default = 0,
                        min = 0,
                        max = 100,
                        subtype = 'PERCENTAGE')
    interpolation = bpy.props.EnumProperty(items = (('cubic', "Cubic", "Gives curved results"), ('linear', "Linear", "Basic, fast, straight interpolation")),
                        name = "Interpolation mode",
                        description = "Interpolation mode: algorithm used when creating segments",
                        default = 'cubic')
    cubic_strength = bpy.props.FloatProperty(name = "Strength",
                        description = "Higher strength results in more fluid curves",
                        default = 1.0,
                        soft_min = -3.0,
                        soft_max = 3.0)
    remove_faces = bpy.props.BoolProperty(name = "Remove faces",
                        description = "Remove faces that are internal after bridging",
                        default = True)
    twist = bpy.props.IntProperty(name = "Twist",
                        description = "Twist what vertices are connected to each other",
                        default = 0)
    reverse = bpy.props.BoolProperty(name = "Reverse",
                        description = "Manually override the direction in which the loops are bridged. Only use if the tool gives the wrong result.",
                        default = False)
    loft = bpy.props.BoolProperty(name = "Loft",
                        description = "Loft multiple loops, instead of considering them as a multi-input for bridging",
                        default = False)
    loft_loop = bpy.props.BoolProperty(name = "Loop",
                        description = "Connect the first and the last loop with each other",
                        default = False)
    
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')
    
    def draw(self, context):
        layout = self.layout
        #layout.prop(self, 'mode') # hidden by default, haven't found a case when 'Basic' mode was needed
        
        if self.loft:        
            row = layout.box().row(align = True)
            row.prop(self, 'loft_loop')
        
        box = layout.box()
        split = box.split(percentage = 0.7, align = True)
        split.prop(self, 'segments')
        row = split.row(align = True)
        if self.segments == 1:
            row.active = False
        row.prop(self, 'min_width', text="")
        split = box.split(percentage = 0.5)
        if self.segments == 1:
            split.active = False
        split.prop(self, 'interpolation', text="")
        row = split.row(align = True)
        if self.interpolation == 'cubic':
            row.prop(self, 'cubic_strength')
        row = box.row(align = True)
        row.prop(self, 'remove_faces')
        
        row = layout.box().row(align = True)
        row.prop(self, 'twist')
        row.prop(self, 'reverse')

    def execute(self, context):
        global_undo, mesh, old_selected_faces, smooth, edge_faces, edgekey_to_edge = initialise(self.interpolation)
        # get loops
        loops = get_selection(mesh)
        if loops:
            # reorder loops if there are more than 2
            if len(loops) > 2:
                if self.loft:
                    loops = sort_loops(mesh, loops, self.loft_loop)
                else:
                    loops = match_loops(mesh, loops)
            # calculate new geometry
            vertices = []
            faces = []
            max_vert_index = len(mesh.vertices)-1
            for i in range(1, len(loops)):
                if not self.loft and i%2 == 0:
                    continue
                lines = calculate_lines(mesh, loops[i-1:i+1], self.mode, self.twist, self.reverse)
                vertex_normals = calculate_virtual_vertex_normals(mesh, lines, loops[i-1:i+1], edge_faces, edgekey_to_edge) # only necessary for cubic interpolation
                segments = calculate_segments(mesh, lines, loops[i-1:i+1], self.segments)
                new_verts, new_faces, max_vert_index = calculate_geometry(mesh, lines, vertex_normals, segments, self.interpolation, self.cubic_strength, self.min_width, max_vert_index)
                if new_verts:
                    vertices += new_verts
                if new_faces:
                    faces += new_faces
            # make sure faces in loops that aren't used, aren't removed
            if self.remove_faces and old_selected_faces:
                save_unused_faces(mesh, old_selected_faces, loops)
            # create vertices
            if vertices:
                create_vertices(mesh, vertices)
            # create faces
            if faces:
                create_faces(mesh, faces, self.twist)
                select_new_faces(mesh, len(faces), smooth)
            # delete internal faces
            if self.remove_faces and old_selected_faces:
                remove_internal_faces(mesh, old_selected_faces)
            # make sure normals are facing outside
            recalculate_normals()
        
        terminate(global_undo)
        return{'FINISHED'}


# draw function for menu integration
def menu_func(self, context):
    self.layout.operator("mesh.bridge", text = "Bridge").loft = False
    self.layout.operator("mesh.bridge", text = "Loft").loft = True


# integrate operator in menu
def register():
    bpy.types.VIEW3D_MT_edit_mesh_faces.prepend(menu_func)


# remove operator from menu
def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_faces.remove(menu_func)


if __name__ == '__main__':
    bpy.ops.mesh.bridge()
