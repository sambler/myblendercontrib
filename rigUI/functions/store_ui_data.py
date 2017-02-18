import bpy
from mathutils import Vector

def store_ui_data(objects,canevas,rig):
    gamma = 1/2.2

    worldCanevasPoints = [canevas.matrix_world * Vector((p.co[0],p.co[1],0)) for p in canevas.data.splines[0].points]

    canevasX = [p[0] for p in worldCanevasPoints]
    canevasY = [p[1] for p in worldCanevasPoints]

    for ob in objects :

        data = ob.to_mesh(bpy.context.scene,False,'PREVIEW')

        points = []
        faces = []
        edges = []

        for p in data.vertices :
            point  = ob.matrix_world * Vector((p.co[0],p.co[1],0))

            x = (point[0]-min(canevasX)) / (max(canevasX)-min(canevasX))

            y = (point[1]-min(canevasY)) / (max(canevasY)-min(canevasY))

            points.append((round(x,5),round(y,5)))

        for f in data.polygons :
            faces.append(f.vertices)

        if not faces :
            for e in data.edges :
                edges.append(e.vertices)


        colors = ob.data.materials[0].node_tree.nodes['Emission'].inputs['Color'].default_value
        color = (round(pow(colors[0],gamma),4),round(pow(colors[1],gamma),4),round(pow(colors[2],gamma),4))

        index = round(ob.matrix_world[2][3]-canevas.matrix_world[2][3],5)


        rig.data.UI[ob.name] = {'points':points, 'faces':faces, 'edges' : edges,'color':color,'index' : index}
