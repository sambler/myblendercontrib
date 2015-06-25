# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# PEP8 compliant (https://www.python.org/dev/peps/pep-0008)

# ----------------------------------------------------------
# File: measureit_tools.py
# support routines for OpenGL
# Author: Antonio Vazquez (antonioya)
#
# ----------------------------------------------------------
# noinspection PyUnresolvedReferences
import bpy
# noinspection PyUnresolvedReferences
import bgl
# noinspection PyUnresolvedReferences
import blf
import math
# noinspection PyUnresolvedReferences
import mathutils
# noinspection PyUnresolvedReferences
import bmesh
# noinspection PyUnresolvedReferences
from bpy_extras import view3d_utils


# -------------------------------------------------------------
# Handle all draw routines (OpenGL main entry point)
#
# -------------------------------------------------------------
def draw_main(context):
    region = bpy.context.region
    rv3d = bpy.context.space_data.region_3d
    scene = bpy.context.scene
    # Get visible layers
    layers = []
    for x in range(0, 20):
        if bpy.context.scene.layers[x] is True:
            layers.extend([x])

    bgl.glEnable(bgl.GL_BLEND)
    # Display selected or all
    if scene.measureit_gl_ghost is False:
        objlist = context.selected_objects
    else:
        objlist = context.scene.objects
    # ---------------------------------------
    # Generate all OpenGL calls
    # ---------------------------------------
    for myobj in objlist:
        if myobj.hide is False:
            if 'MeasureGenerator' in myobj:
                # verify visible layer
                for x in range(0, 20):
                    if myobj.layers[x] is True:
                        if x in layers:
                            op = myobj.MeasureGenerator[0]
                            draw_segments(context, myobj, op, region, rv3d)
                        break

    # -----------------------
    # restore opengl defaults
    # -----------------------
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


# -------------------------------------------------------------
# Draw segments
#
# rgb: Color
# fsize: Font size
# -------------------------------------------------------------
def draw_segments(context, myobj, op, region, rv3d):
    if op.measureit_num > 0:
        a_code = "\u00b0"
        scale = bpy.context.scene.unit_settings.scale_length
        scene = bpy.context.scene
        pr = scene.measureit_gl_precision
        fmt = "%1." + str(pr) + "f"
        ovr = scene.measureit_ovr
        ovrcolor = scene.measureit_ovr_color
        ovrfsize = scene.measureit_ovr_font
        ovrline = scene.measureit_ovr_width
        units = scene.measureit_units
        # --------------------
        # Scene Scale
        # --------------------
        if scene.measureit_scale is True:
            prs = scene.measureit_scale_precision
            fmts = "%1." + str(prs) + "f"
            pos_x, pos_y = get_scale_txt_location(context)
            tx_dsp = fmts % scene.measureit_scale_factor
            tx_scale = scene.measureit_gl_scaletxt + " 1:" + tx_dsp
            draw_text(pos_x, pos_y,
                      tx_scale, scene.measureit_scale_color, scene.measureit_scale_font)
        # --------------------
        # Loop
        # --------------------
        for idx in range(0, op.measureit_num):
            ms = op.measureit_segments[idx]
            if ovr is False:
                fsize = ms.glfont_size
            else:
                fsize = ovrfsize
            # ------------------------------
            # only active and visible
            # ------------------------------
            if ms.glview is True and ms.glfree is False:
                # noinspection PyBroadException
                try:
                    if ovr is False:
                        rgb = ms.glcolor
                    else:
                        rgb = ovrcolor
                    # ----------------------
                    # Segment or Label
                    # ----------------------
                    if ms.gltype == 1 or ms.gltype == 2:
                        obverts = get_mesh_vertices(myobj)

                        if ms.glpointa <= len(obverts) and ms.glpointb <= len(obverts):
                            a_p1 = get_point(obverts[ms.glpointa].co, myobj)
                            b_p1 = get_point(obverts[ms.glpointb].co, myobj)
                    # ----------------------
                    # Vertex to Vertex (link)
                    # ----------------------
                    if ms.gltype == 3:
                        obverts = get_mesh_vertices(myobj)
                        linkverts = bpy.data.objects[ms.gllink].data.vertices
                        a_p1 = get_point(obverts[ms.glpointa].co, myobj)
                        b_p1 = get_point(linkverts[ms.glpointb].co, bpy.data.objects[ms.gllink])
                    # ----------------------
                    # Vertex to Object (link)
                    # ----------------------
                    if ms.gltype == 4:
                        obverts = get_mesh_vertices(myobj)
                        a_p1 = get_point(obverts[ms.glpointa].co, myobj)
                        b_p1 = get_location(bpy.data.objects[ms.gllink])
                    # ----------------------
                    # Object to Vertex (link)
                    # ----------------------
                    if ms.gltype == 5:
                        linkverts = bpy.data.objects[ms.gllink].data.vertices
                        a_p1 = get_location(myobj)
                        b_p1 = get_point(linkverts[ms.glpointa].co, bpy.data.objects[ms.gllink])
                    # ----------------------
                    # Object to Object (link)
                    # ----------------------
                    if ms.gltype == 8:
                        a_p1 = get_location(myobj)
                        b_p1 = get_location(bpy.data.objects[ms.gllink])
                    # ----------------------
                    # Vertex to origin
                    # ----------------------
                    if ms.gltype == 6:
                        obverts = get_mesh_vertices(myobj)
                        a_p1 = (0, 0, 0)
                        b_p1 = get_point(obverts[ms.glpointa].co, myobj)
                    # ----------------------
                    # Object to origin
                    # ----------------------
                    if ms.gltype == 7:
                        a_p1 = (0, 0, 0)
                        b_p1 = get_location(myobj)
                    # ----------------------
                    # Angle
                    # ----------------------
                    if ms.gltype == 9:
                        obverts = get_mesh_vertices(myobj)
                        if ms.glpointa <= len(obverts) and ms.glpointb <= len(obverts) and ms.glpointc <= len(obverts):
                            an_p1 = get_point(obverts[ms.glpointa].co, myobj)
                            an_p2 = get_point(obverts[ms.glpointb].co, myobj)
                            an_p3 = get_point(obverts[ms.glpointc].co, myobj)

                            ang_1 = mathutils.Vector((an_p1[0] - an_p2[0], an_p1[1] - an_p2[1], an_p1[2] - an_p2[2]))
                            ang_2 = mathutils.Vector((an_p3[0] - an_p2[0], an_p3[1] - an_p2[1], an_p3[2] - an_p2[2]))

                            ang_3 = ang_1 + ang_2  # Result vector

                        a_p1 = (an_p2[0], an_p2[1], an_p2[2])
                        b_p1 = (0, 0, 0)

                    # Calculate distance
                    dist, distloc = distance(a_p1, b_p1, ms.glocx, ms.glocy, ms.glocz)
                    # ------------------------------------
                    # get normal vector
                    # ------------------------------------
                    if ms.gldefault is True:
                        if ms.gltype != 9:
                            loc = get_location(myobj)
                            midpoint3d = interpolate3d(a_p1, b_p1, math.fabs(dist / 2))
                            vn = mathutils.Vector((midpoint3d[0] - loc[0],
                                                   midpoint3d[1] - loc[1],
                                                   midpoint3d[2] - loc[2]))
                        else:
                            vn = ang_3  # if angle, vector is angle position
                    else:
                        vn = mathutils.Vector((ms.glnormalx, ms.glnormaly, ms.glnormalz))

                    vn.normalize()
                    # ------------------------------------
                    # position vector
                    # ------------------------------------
                    vi = vn * ms.glspace
                    s = (14 / 200)
                    if s > ms.glspace:
                        s = ms.glspace / 5
                    vi2 = vn * (ms.glspace + s)
                    # ------------------------------------
                    # apply vector
                    # ------------------------------------
                    v1 = (a_p1[0] + vi[0], a_p1[1] + vi[1], a_p1[2] + vi[2])
                    v2 = (b_p1[0] + vi[0], b_p1[1] + vi[1], b_p1[2] + vi[2])

                    # Segment extreme
                    v11 = (a_p1[0] + vi2[0], a_p1[1] + vi2[1], a_p1[2] + vi2[2])
                    v22 = (b_p1[0] + vi2[0], b_p1[1] + vi2[1], b_p1[2] + vi2[2])

                    # Labeling
                    v11a = (a_p1[0] + vi2[0], a_p1[1] + vi2[1], a_p1[2] + vi2[2] + s / 30)
                    v11b = (a_p1[0] + vi2[0], a_p1[1] + vi2[1], a_p1[2] + vi2[2] - s / 40)
                    # ------------------------------------
                    # converting to screen coordinates
                    # ------------------------------------
                    screen_point_ap1 = view3d_utils.location_3d_to_region_2d(region, rv3d, a_p1)
                    screen_point_bp1 = view3d_utils.location_3d_to_region_2d(region, rv3d, b_p1)

                    screen_point_v1 = view3d_utils.location_3d_to_region_2d(region, rv3d, v1)
                    screen_point_v2 = view3d_utils.location_3d_to_region_2d(region, rv3d, v2)
                    screen_point_v11 = view3d_utils.location_3d_to_region_2d(region, rv3d, v11)
                    screen_point_v22 = view3d_utils.location_3d_to_region_2d(region, rv3d, v22)
                    screen_point_v11a = view3d_utils.location_3d_to_region_2d(region, rv3d, v11a)
                    screen_point_v11b = view3d_utils.location_3d_to_region_2d(region, rv3d, v11b)
                    # ------------------------------------
                    # colour + line setup
                    # ------------------------------------
                    bgl.glEnable(bgl.GL_BLEND)
                    if ovr is False:
                        bgl.glLineWidth(ms.glwidth)
                    else:
                        bgl.glLineWidth(ovrline)

                    bgl.glColor4f(rgb[0], rgb[1], rgb[2], rgb[3])

                    # ------------------------------------
                    # Text (distance)
                    # ------------------------------------
                    # noinspection PyBroadException
                    if ms.gltype != 2 and ms.gltype != 9:
                        # noinspection PyBroadException
                        try:
                            midpoint3d = interpolate3d(v1, v2, math.fabs(dist / 2))
                            gap3d = (midpoint3d[0], midpoint3d[1], midpoint3d[2] + s / 2)
                            txtpoint2d = view3d_utils.location_3d_to_region_2d(region, rv3d, gap3d)
                            # Scale
                            if scene.measureit_scale is True:
                                dist = dist * scene.measureit_scale_factor
                                distloc = distloc * scene.measureit_scale_factor

                            # decide dist to use
                            if dist == distloc:
                                locflag = False
                                usedist = dist
                            else:
                                usedist = distloc
                                locflag = True
                            # Apply scene scale
                            usedist *= scale
                            # ------------------------
                            # Units automatic
                            # ------------------------
                            if units == "1":
                                # Units
                                if bpy.context.scene.unit_settings.system == "IMPERIAL":
                                    feet = usedist * 3.2808399
                                    inches = (feet * 12) % 12
                                    if feet >= 1.0:
                                        tx_dist = fmt % feet + " ft"
                                    else:
                                        tx_dist = fmt % inches + " in"
                                elif bpy.context.scene.unit_settings.system == "METRIC":
                                    if usedist >= 1.0:
                                        tx_dist = fmt % usedist + " m"
                                    else:
                                        if usedist >= 0.01:
                                            d_cm = usedist * 100
                                            tx_dist = fmt % d_cm + " cm"
                                        else:
                                            d_mm = usedist * 1000
                                            tx_dist = fmt % d_mm + " mm"
                                else:
                                    tx_dist = fmt % usedist
                            # ------------------------
                            # Units meters
                            # ------------------------
                            elif units == "2":
                                tx_dist = fmt % usedist + " m"
                            # ------------------------
                            # Units centimeters
                            # ------------------------
                            elif units == "3":
                                d_cm = usedist * 100
                                tx_dist = fmt % d_cm + " cm"
                            # ------------------------
                            # Units milimiters
                            # ------------------------
                            elif units == "4":
                                d_mm = usedist * 1000
                                tx_dist = fmt % d_mm + " mm"
                            # ------------------------
                            # Units feet
                            # ------------------------
                            elif units == "5":
                                feet = usedist * 3.2808399
                                tx_dist = fmt % feet + " ft"
                            # ------------------------
                            # Units inches
                            # ------------------------
                            elif units == "6":
                                inches = usedist * 39.3700787
                                tx_dist = fmt % inches + " in"
                            # ------------------------
                            # Default
                            # ------------------------
                            else:
                                tx_dist = fmt % usedist

                            # -----------------------------------
                            # Draw text
                            # -----------------------------------
                            if scene.measureit_gl_show_d is True:
                                msg = tx_dist + " "
                            else:
                                msg = " "
                            if scene.measureit_gl_show_n is True:
                                msg += ms.gltxt
                            if scene.measureit_gl_show_d is True or scene.measureit_gl_show_n is True:
                                draw_text(txtpoint2d[0], txtpoint2d[1], msg, rgb, fsize)

                            # ------------------------------
                            # if axis loc, show a indicator
                            # ------------------------------
                            if locflag is True and ms.glocwarning is True:
                                txtpoint2d = view3d_utils.location_3d_to_region_2d(region, rv3d, (v2[0], v2[1], v2[2]))
                                txt = "["
                                if ms.glocx is True:
                                    txt += "X"
                                if ms.glocy is True:
                                    txt += "Y"
                                if ms.glocz is True:
                                    txt += "Z"
                                txt += "]"
                                draw_text(txtpoint2d[0], txtpoint2d[1], txt, rgb, fsize-1)

                        except:
                            pass
                    # ------------------------------------
                    # Text (label) and Angles
                    # ------------------------------------
                    # noinspection PyBroadException
                    if ms.gltype == 2 or ms.gltype == 9:
                        # noinspection PyBroadException
                        try:
                            if ms.gltype == 2:
                                tx_dist = " " + ms.gltxt
                                right = False
                            else:  # Angles
                                ang = ang_1.angle(ang_2)
                                right = True
                                if bpy.context.scene.unit_settings.system_rotation == "DEGREES":
                                    ang = math.degrees(ang)

                                tx_dist = " " + fmt % ang
                                # Add degree symbol
                                if bpy.context.scene.unit_settings.system_rotation == "DEGREES":
                                    tx_dist += a_code

                                if scene.measureit_gl_show_n is True:
                                    tx_dist += " " + ms.gltxt

                            gap3d = (v11[0], v11[1], v11[2])
                            txtpoint2d = view3d_utils.location_3d_to_region_2d(region, rv3d, gap3d)
                            draw_text(txtpoint2d[0], txtpoint2d[1], tx_dist, rgb, fsize, right)
                        except:
                            pass
                    # ------------------------------------
                    # Draw lines
                    # ------------------------------------
                    if ms.gltype == 1:  # Segment
                        draw_line(screen_point_ap1, screen_point_v11)
                        draw_line(screen_point_bp1, screen_point_v22)
                        draw_line(screen_point_v1, screen_point_v2)

                    if ms.gltype == 2:  # Label
                        draw_line(screen_point_ap1, screen_point_v11)
                        draw_line(screen_point_v11a, screen_point_v11b)

                    if ms.gltype == 3 or ms.gltype == 4 or ms.gltype == 5 or ms.gltype == 8 \
                            or ms.gltype == 6 or ms.gltype == 7:  # Origin and Links
                        draw_line(screen_point_ap1, screen_point_bp1)

                    if ms.gltype == 9:  # Angle
                        dist, distloc = distance(an_p1, an_p2)
                        mp1 = interpolate3d(an_p1, an_p2, math.fabs(dist / 1.1))

                        dist, distloc = distance(an_p3, an_p2)
                        mp2 = interpolate3d(an_p3, an_p2, math.fabs(dist / 1.1))

                        screen_point_an_p1 = view3d_utils.location_3d_to_region_2d(region, rv3d, mp1)
                        screen_point_an_p2 = view3d_utils.location_3d_to_region_2d(region, rv3d, an_p2)
                        screen_point_an_p3 = view3d_utils.location_3d_to_region_2d(region, rv3d, mp2)

                        draw_line(screen_point_an_p1, screen_point_an_p2)
                        draw_line(screen_point_an_p2, screen_point_an_p3)
                        draw_line(screen_point_an_p1, screen_point_an_p3)

                except:
                    # if error, disable segment
                    ms.glfree = True

    return


# -------------------------------------------------------------
# Create OpenGL text
#
# right: Align to right
# -------------------------------------------------------------
def draw_text(x_pos, y_pos, display_text, rgb, fsize, right=False):
    gap = 12
    font_id = 0
    blf.size(font_id, fsize, 72)

    text_width, text_height = blf.dimensions(font_id, display_text)
    if right is True:
        newx = x_pos - text_width - gap
    else:
        newx = x_pos
    blf.position(font_id, newx, y_pos, 0)
    bgl.glColor4f(rgb[0], rgb[1], rgb[2], rgb[3])
    blf.draw(font_id, display_text)
    return


# -------------------------------------------------------------
# Draw an OpenGL line
#
# -------------------------------------------------------------
def draw_line(v1, v2):
    # noinspection PyBroadException
    try:
        if v1 is not None and v2 is not None:
            bgl.glBegin(bgl.GL_LINES)
            bgl.glVertex2f(*v1)
            bgl.glVertex2f(*v2)
            bgl.glEnd()
    except:
        pass


# --------------------------------------------------------------------
# Distance between 2 points in 3D space
# v1: first point
# v2: second point
# locx/y/z: Use this axis
# return: distance
# --------------------------------------------------------------------
def distance(v1, v2, locx=True, locy=True, locz=True):
    x = math.sqrt((v2[0] - v1[0]) ** 2 + (v2[1] - v1[1]) ** 2 + (v2[2] - v1[2]) ** 2)

    # If axis is not used, make equal both (no distance)
    v1b = [v1[0], v1[1], v1[2]]
    v2b = [v2[0], v2[1], v2[2]]
    if locx is False:
        v1b[0] = 0
        v2b[0] = 0
    if locy is False:
        v1b[1] = 0
        v2b[1] = 0
    if locz is False:
        v1b[2] = 0
        v2b[2] = 0

    xloc = math.sqrt((v2b[0] - v1b[0]) ** 2 + (v2b[1] - v1b[1]) ** 2 + (v2b[2] - v1b[2]) ** 2)

    return x, xloc


# --------------------------------------------------------------------
# Interpolate 2 points in 3D space
# v1: first point
# v2: second point
# d1: distance
# return: interpolate point
# --------------------------------------------------------------------
def interpolate3d(v1, v2, d1):
    # calculate vector
    v = (v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2])
    # calculate distance between points
    d0, dloc = distance(v1, v2)

    # calculate interpolate factor (distance from origin / distance total)
    # if d1 > d0, the point is projected in 3D space
    if d0 > 0:
        x = d1 / d0
    else:
        x = d1

    final = (v1[0] + (v[0] * x), v1[1] + (v[1] * x), v1[2] + (v[2] * x))
    return final


# --------------------------------------------------------------------
# Get point rotated and relative to parent
# v1: point
# mainobject
# --------------------------------------------------------------------
def get_point(v1, mainobject):
    # Using World Matrix
    vt = mathutils.Vector((v1[0], v1[1], v1[2], 1))
    m4 = mainobject.matrix_world
    vt2 = m4 * vt
    v2 = [vt2[0], vt2[1], vt2[2]]

    return v2


# --------------------------------------------------------------------
# Get location in world space
# v1: point
# mainobject
# --------------------------------------------------------------------
def get_location(mainobject):
    # Using World Matrix
    m4 = mainobject.matrix_world

    return [m4[0][3], m4[1][3], m4[2][3]]


# --------------------------------------------------------------------
# Get vertex data
# mainobject
# --------------------------------------------------------------------
def get_mesh_vertices(myobj):
    if myobj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(myobj.data)
        obverts = bm.verts
    else:
        obverts = myobj.data.vertices

    return obverts


# --------------------------------------------------------------------
# Get position for scale text
#
# --------------------------------------------------------------------
def get_scale_txt_location(context):
    scene = context.scene
    pos_x = int(context.region.width * scene.measureit_scale_pos_x / 100)
    pos_y = int(context.region.height * scene.measureit_scale_pos_y / 100)

    return pos_x, pos_y
