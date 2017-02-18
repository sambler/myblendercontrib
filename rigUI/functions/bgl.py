import bpy
import bgl

from mathutils import Vector
from mathutils.geometry import intersect_line_line_2d
from math import fmod



def draw_polyline_2d_loop(context, points,faces,edges,scale, offset, color):
    region = context.region
    rv3d = context.space_data.region_3d
    bgl.glColor4f(*color)  #black or white?

    for face in faces :
        bgl.glBegin(bgl.GL_TRIANGLES)
        for point in face :
            coord = points[point]

            #for coord in points:

            bgl.glVertex2f(scale*coord[0]+offset[0], scale*coord[1] + offset[1])

    bgl.glEnd()

    bgl.glLineWidth(1)
    for edge in edges :
        bgl.glBegin(bgl.GL_LINES)

        for point in edge :
            coord = points[point]

            #for coord in points:

            bgl.glVertex2f(scale*coord[0]+offset[0], scale*coord[1] + offset[1])

    bgl.glEnd()

    return


def outside_loop(loop, scale, offset):
    xs = [scale*v[0] + offset[0] for v in loop]
    ys = [scale*v[1] + offset[1]  for v in loop]
    maxx = max(xs)
    maxy = max(ys)
    bound = (1.1*maxx, 1.1*maxy)
    return bound


def point_inside_loop(loop, point, scale, offset):
    nverts = len(loop)
    #vectorize our two item tuple
    out = Vector(outside_loop(loop, scale, offset))
    pt = Vector(point)

    intersections = 0
    for i in range(0,nverts):
        a = scale*Vector(loop[i-1]) + Vector(offset)
        b = scale*Vector(loop[i]) + Vector(offset)
        if intersect_line_line_2d(pt,out,a,b):
            intersections += 1

    inside = False
    if fmod(intersections,2):
        inside = True

    return inside


def select_bone(mouse) :
    button_data = bpy.context.object.data.UI
    region = bpy.context.region
    rv3d = bpy.context.space_data.region_3d
    width = region.width
    height = region.height

    menu_width = (height)

    #origin of menu is bottom left corner
    menu_loc = (-height/2 + width/2,0)

    for key,value in button_data.items(): #each of those is a loop
        if not key.endswith(".display"):
            select = point_inside_loop(value['points'],mouse,menu_width, menu_loc)

            bone = bpy.context.object.pose.bones.get(key)

            if bone and select:
                bone.bone.select = not bone.bone.select


def draw_callback_px(self, context,adress):
    if context.space_data.as_pointer() == adress :
        #if context.object and context.object.type =='ARMATURE' and context.object.data.UI:
        button_data = context.object.data.UI

        region = context.region
        rv3d = context.space_data.region_3d
        width = region.width
        height = region.height

        menu_width = (height)
        menu_loc = (-height/2 + width/2,0) #for now


        #draw all the buttons
        indexButton= sorted([(value['index'], key) for key,value in button_data.items()])


        for value in indexButton: #each of those is a loop
            points = button_data[value[1]]['points']
            GColor = button_data[value[1]]['color']
            Color = (GColor[0],GColor[1],GColor[2])

            faces = button_data[value[1]]['faces']
            edges = button_data[value[1]]['edges']

            if not value[1].endswith('.display') :


                select = point_inside_loop(points,self.mouse,menu_width, menu_loc)

                bone = bpy.context.object.pose.bones.get(value[1])

                if bone and bone.bone.select == True :
                    color = (0.9,0.9,0.9,1)

                    if select :
                        color = (1,1,1,1)

                else :
                    color = (Color[0],Color[1],Color[2],1)

                    if select:
                        color = (Color[0]*1.2,Color[1]*1.2,Color[2]*1.2,1)


                draw_polyline_2d_loop(context, points, faces,edges,menu_width, menu_loc, color)
                #color = (1.0,1.0,1.0,1.0) # ADDED

            else :
                color = (Color[0],Color[1],Color[2],1)
                #color = (1,1,1,1)
                draw_polyline_2d_loop(context, points, faces,edges,menu_width, menu_loc, color)
