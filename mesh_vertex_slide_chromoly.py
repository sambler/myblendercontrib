# -*- coding: utf-8 -*-

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

# Modified by JMR to make it work on blender 2.57
# Modified by Ideasman42 to work on blender 2.63

bl_info = {
    'name': 'Vertex Slide Chromoly',
    'author': 'chromoly, JMR',
    'version': (0, 2),
    'blender': (2, 5, 7),
    'api': 39104,
    'location': 'Search > vertex slide',
    'description': 'Interactive Vertex Slide',
    'warning': 'Tool Shelf functions may cause errors.',
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/" \
        "Scripts/Modeling/Vertex_Slide",
    "tracker_url": "https://projects.blender.org/tracker/index.php?"\
        "func=detail&aid=27487&group_id=153&atid=468",
    'category': 'Mesh'}

import math
import sys
import time
#from functools import reduce
#from collections import OrderedDict, Counter

import bpy
from bpy.props import *
import mathutils as Math
from mathutils import Euler, Matrix, Quaternion, Vector
#import geometry as Geo
import bgl
from bgl import glEnable, glDisable, glBegin, glEnd, glColor4f, glVertex2f, \
                GL_BLEND, GL_LINES, glRectf
import blf
import bmesh

'''
from va.mesh import PyMesh  #, path_vertices_list

from va.view import convert_world_to_window, convert_window_to_world, \
                    MouseCoordinate
from va.gl import draw_circle, draw_arrow
from va.utils import InputExpression, print_event
'''

MIN_NUMBER = 1E-8
GRID_MIN_PX = 6.0

print_event_modal = False

### Copy from Modules #########################################################
class Vert():
    # &#31777;&#26131;&#29256;
    def __init__(self):
        self.index = 0
        self.select = False
        self.hide = False
        self.co = Vector()
        self.verts = []
        self.worco = None  # type:Vector. ob.matrix_world * self.co
        self.winco = None  # type:Vector. convert_world_to_window()
        self.viewco = None  # type:Vector viewmat * self.worco

    def _get_selected(self):
        return self.select and not self.hide
    def _set_selected(self, val):
        if not self.hide:
            self.select = val
    is_selected = property(_get_selected, _set_selected)

class PyMesh():
    # &#31777;&#26131;&#29256;
    def __init__(self, bm):
        verts = [Vert() for i in range(len(bm.verts))]
        for i, v in enumerate(bm.verts):
            vert = verts[i]
            vert.index = v.index
            vert.select = v.select
            vert.hide = v.hide
            vert.co = v.co.copy()
        for edge in bm.edges:
            v1, v2 = edge.verts
            i1, i2 = v1.index, v2.index
            verts[i1].verts.append(verts[i2])
            verts[i2].verts.append(verts[i1])
        self.verts = verts

    def calc_world_coordinate(self, matrix_world):
        for vert in self.verts:
            vert.worco = matrix_world * vert.co

def convert_world_to_window(vec, persmat, sx, sy):
    '''vec: sequence
    return Vector
    '''
    #v = vec.copy().resize4D()
    v = Vector([vec[0], vec[1], vec[2], 1.0])
    v = persmat * v
    if v[3] != 0.0:
        v /= v[3]
    x = sx / 2 + v[0] * sx / 2
    y = sy / 2 + v[1] * sy / 2
    return Vector([x, y, v[2]])


def convert_window_to_world(vec, persmat, sx, sy):
    '''vec: sequence
    return Vector
    '''
    invpmat = persmat.copy()
    invpmat.invert()
    v1 = Math.Vector([float(vec[0]) * 2 / sx, float(vec[1]) * 2 / sy, vec[2]])
    v2 = v1 - Math.Vector([1., 1., 0.])
    v2.resize_4d()
    v3 = invpmat * v2
    if v3[3] != 0.0:
        v3 /= v3[3]
    v3.resize_3d()
    return v3


def get_DPBU_dx_unit_pow(region, rv3d):
    '''&#30011;&#38754;&#20013;&#24515;p&#12392;&#12289;&#12381;&#12371;&#12363;&#12425;BlenderUnit&#20998;&#12384;&#12369;&#30011;&#38754;&#12392;&#24179;&#34892;&#12395;&#31227;&#21205;&#12375;&#12383;q&#12434;
    &#12381;&#12428;&#12382;&#12428;window&#24231;&#27161;&#12395;&#22793;&#25563;(p,q&#12399;&#20849;&#12395;world&#24231;&#27161;)
    '''
    sx = region.width
    sy = region.height
    persmat = rv3d.perspective_matrix
    viewmat = rv3d.view_matrix
    viewinvmat = viewmat.copy()
    viewinvmat.invert()
    viewloc = rv3d.view_location

    p = viewloc
    if sx >= sy:
        q = viewloc + Vector(viewinvmat[0][:3])
    else:
        q = viewloc + Vector(viewinvmat[1][:3])
    dp = convert_world_to_window(p, persmat, sx, sy)
    dq = convert_world_to_window(q, persmat, sx, sy)
    l = math.sqrt((dp[0] - dq[0]) ** 2 + (dp[1] - dq[1]) ** 2)
    dot_per_blender_unit = dx = l

    #unit = 1.0
    unit_pow = 0
    if dx < GRID_MIN_PX:
        while dx < GRID_MIN_PX:
            dx *= 10
            unit_pow += 1
    else:
        while dx > GRID_MIN_PX * 10:
            dx /= 10
            unit_pow -= 1
    return dot_per_blender_unit, dx, unit_pow


class MouseCoordinate:
    '''
    origin, current, shift&#12363;&#12425;relative&#12434;&#27714;&#12417;&#12427;&#12290;
    relative&#12434;origin -> lock&#12398;&#12505;&#12463;&#12488;&#12523;&#12395;&#27491;&#23556;&#24433;&#12290;
    &#12473;&#12490;&#12483;&#12503;&#12434;&#12434;&#35336;&#31639;&#12375;&#12390;dist&#12395;&#20516;&#12434;&#20837;&#12428;&#12427;&#12290;
    '''
    shift = None  # *0.1. type:Vector. relative&#12395;&#24433;&#38911;&#12290;
    lock = None  # lock direction. type:Vector. relative&#12395;&#24433;&#38911;&#12290;
    snap = False  # type:Bool
    origin = Vector()  # R&#12461;&#12540;&#12391;&#22793;&#26356;
    current = Vector()  # (event.mouse_region_x, event.mouse_region_y, 0)
    relative = Vector()  # shift&#12434;&#32771;&#24942;
    dpbu = 1.0  # update&#26178;&#12395;&#21487;&#33021;&#12394;&#12425;&#20877;&#21462;&#24471;
    unit_pow = 1.0 # update&#26178;&#12395;&#21487;&#33021;&#12394;&#12425;&#20877;&#21462;&#24471;
    dist = 0.0  # relativesnap&#12434;&#32771;&#24942;
    dpf= 200 # dot per fac
    fac = 0.0

    def __init__(self, context=None, event=None, recalcDPBU=True, dpf=200):
        if event:
            self.origin = Vector((event.mouse_region_x, event.mouse_region_y, \
                                  0.0))
        self.dpf = dpf
        self.update(context, event, recalcDPBU)

    def update(self, context=None, event=None, recalcDPBU=False):
        shift = self.shift
        snap = self.snap
        lock = self.lock
        origin = self.origin

        if event:
            current = Vector((event.mouse_region_x, event.mouse_region_y, 0.0))
        else:
            current = self.current
        if shift:
            relative = shift - origin + (current - shift) * 0.1
        else:
            relative = current - origin
        if lock:
            origin_lock = lock - origin
            if origin_lock.length >= MIN_NUMBER:
                if relative.length >= MIN_NUMBER:
                    relative = relative.project(origin_lock)
            else:
                self.lock = None
        if context and recalcDPBU:
            dpbu, dx, unit_pow = get_DPBU_dx_unit_pow(context.region, context.region_data)
        else:
            dpbu, unit_pow = self.dpbu, self.unit_pow

        dist = relative.length / dpbu
        fac = relative.length / self.dpf
        if lock:
            if relative.dot(origin_lock) < 0.0:
                dist = -dist
                fac = -fac
        if snap:
            grid = 10 ** unit_pow
            gridf = 0.1
            if shift:
                grid /= 10
                gridf /= 10
            dist = grid * math.floor(0.5 + dist / grid)
            fac = gridf * math.floor(0.5 + fac / gridf)

        self.current = current
        self.relative = relative
        self.dpbu = dpbu
        self.unit_pow = unit_pow
        self.dist = dist
        self.fac = fac

    def draw_origin(self, radius=5):
        draw_circle(self.origin[0], self.origin[1], radius, 16)

    def draw_relative(self, radius=5):
        #if self.shift:
        draw_circle(self.origin[0] + self.relative[0], \
                    self.origin[1] + self.relative[1], radius, 16)

    def draw_lock_arrow(self, length=10, angle=math.radians(110)):
        if self.lock is not None:
            lock = self.lock.copy().resize2D()
            origin = self.origin.copy().resize2D()
            vec = (origin - lock).normalize()
            vec *= 20
            vecn = lock + vec
            draw_arrow(vecn[0], vecn[1], lock[0], lock[1], \
                       headlength=length, headangle=angle, headonly=True)


def draw_circle(x, y, radius, subdivide):
    '''e = Euler([0, 0, math.radians(360 / subdivide)])
    m = e.to_matrix()
    v = Vector([0, radius, 0])
    bgl.glBegin(bgl.GL_LINE_LOOP)
    for i in range(subdivide):
        bgl.glVertex2f(x + v[0], y + v[1])
        v = m * v
    bgl.glEnd()
    '''
    bgl.glBegin(bgl.GL_LINE_LOOP)
    r = 0.0
    dr = math.pi * 2 / subdivide
    for i in range(subdivide):
        bgl.glVertex2f(x + radius * math.cos(r), y + radius * math.sin(r))
        r += dr
    bgl.glEnd()


def draw_arrow(nockx, nocky, headx, heady, headlength=10, \
               headangle=math.radians(70), headonly=False):
    '''
    nockx, nocky: &#31560;
    headx, heady: &#37827;
    '''
    if nockx == headx and nocky == heady or headonly and headlength == 0:
        return
    angle = max(min(math.pi / 2, headangle / 2), 0)  # &#31622;&#12392;&#12398;&#35282;&#24230;
    length = headlength / math.cos(angle)
    vn = Vector((nockx, nocky))
    vh = Vector((headx, heady))
    if headonly:
        vh = vh + (vh - vn).normalize() * headlength
        headx, heady = vh
    bgl.glBegin(bgl.GL_LINES)
    # shaft
    if not headonly:
        bgl.glVertex2f(nockx, nocky)
        bgl.glVertex2f(headx, heady)
    # head
    if headlength:
        vec = (vn - vh).normalize() * length
        vec.resize3D()
        q = Quaternion((0, 0, 0, -1))
        q.angle = angle
        v = q * vec
        bgl.glVertex2f(headx, heady)
        bgl.glVertex2f(headx + v[0], heady + v[1])
        q.angle = -angle
        v = q * vec
        bgl.glVertex2f(headx, heady)
        bgl.glVertex2f(headx + v[0], heady + v[1])
    bgl.glEnd()


class InputExpression:
    '''
    modal&#20869;&#12395;&#32068;&#12415;&#36796;&#12415;&#12289;&#12461;&#12540;&#12508;&#12540;&#12489;&#20837;&#21147;&#12434;&#25991;&#23383;&#21015;&#12392;&#12375;&#12390;&#26684;&#32013;&#12290;
    event: (type:Event)
    exp_strings: &#27083;&#25991; (type:str_list)
    caret: &#12450;&#12463;&#12486;&#12451;&#12502;&#12394;&#27083;&#25991;, &#12459;&#12540;&#12477;&#12523;&#20301;&#32622; (type:int_list)
    '''
    event_char = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                          'abcdefghijklmnopqrstuvwxyz'))

    event_char.update(zip(('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR',
                           'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE'),
                          '0123456789'))
    event_char.update({'NUMPAD_' + val: val for val in '0123456789'})
    event_char.update(zip(('NUMPAD_PERIOD', 'NUMPAD_SLASH', 'NUMPAD_ASTERIX',
                           'NUMPAD_MINUS', 'NUMPAD_PLUS'),
                          './*-+'))
    event_char.update({'SPACE': ' ',
                       'SEMI_COLON': ';', 'PERIOD': '.', 'COMMA': ',',
                       'QUOTE': "'", 'MINUS':'-', 'SLASH':'/',
                       'EQUAL':'=', 'LEFT_BRACKET':'[', 'RIGHT_BRACKET':']'})
    event_char_shift = dict(zip(('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR',
                                 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE'),
                                '''~!"#$%&'()'''))
    event_char_shift.update({'SEMI_COLON': '+', 'MINUS': '='})
    event_caret = {'LEFT_ARROW': -1, 'RIGHT_ARROW': 1,
                   'UP_ARROW': -999, 'DOWN_ARROW': 999,
                   'HOME': -999, 'END': 999}
    event_delete = {'DEL':'del', 'BACK_SPACE':'back_space'}

    def __init__(self, names=('Dist',)):
        self.exp_names = list(names)
        self.exp_strings = ['' for i in range(len(names))]
        self.caret = [0, 0]

    def input(self, event):
        exp_event = True  # &#12513;&#12477;&#12483;&#12489;&#12391;&#20966;&#29702;&#12375;&#12383;&#12392;&#12356;&#12358;&#20107;
        if event.value != 'PRESS':
            exp_event = False
            return exp_event

        i, caret = self.caret
        string = self.exp_strings[i]
        if event.type == 'X' and event.ctrl:  # all clear
            if event.shift:
                self.caret[:] = [0, 0]
                for i in range(len(self.exp_strings)):
                    self.exp_strings[i] = ''
            else:
                self.caret[1] = 0
                self.exp_strings[self.caret[0]] = ''
        elif event.type in self.event_char:
            if event.shift:
                char = self.event_char_shift.get(event.type, None)
            else:
                char = self.event_char[event.type]
            if char:
                self.exp_strings[i] = string[:caret] + char + string[caret:]
                self.caret[1] += 1
            else:
                exp_event = False
        elif event.type in self.event_caret:
            caret += self.event_caret[event.type]
            self.caret[1] = min(max(caret, 0), len(string))
        elif event.type in self.event_delete:
            deltype = self.event_delete[event.type]
            if deltype =='del':
                self.exp_strings[i] = string[:caret] + string[caret + 1:]
            elif deltype == 'back_space':
                self.exp_strings[i] = string[:max(0, caret - 1)] + \
                                      string[caret:]
                self.caret[1] =  max(0, caret - 1)
        elif event.type == 'TAB':
            if event.shift or event.ctrl:
                exp_event = False
            else:
                i += 1
                if i >= len(self.exp_strings):
                    i = 0
                self.caret[0] = i
                self.caret[1] = len(self.exp_strings[i])
        else:
            exp_event = False
        return exp_event

    def get_exp_value(self, index=0):
        val = None
        if self.exp_strings[index]:
            try:
                v = eval(self.exp_strings[index])
                if isinstance(v, (int, float)):
                    val = v
            except:
                pass
        return val

    def get_exp_values(self):
        vals = []
        for i in range(len(self.exp_strings)):
            vals.append(self.get_exp_value(i))
        return vals

    def draw_exp_strings(self, font_id, ofsx, ofsy, minwidth=40, \
                         petition=',  ', end=''):
        for i, string in enumerate(self.exp_strings):
            name = self.exp_names[i] + ' '
            text = name + string
            if len(self.exp_strings) > 1 and 0 < i < len(exp_strings) - 1:
                text = text + pertiton
            blf.position(font_id, ofsx, ofsy, 0)
            blf.draw(font_id, text)
            text_width, text_height = blf.dimensions(font_id, text)
            text_width = max(minwidth, text_width)
            # caret
            if i == self.caret[0]:
                t = name + string[:self.caret[1]]
                t_width, t_height = blf.dimensions(font_id, t)
                x = ofsx + t_width
                glRectf(x, ofsy - 4, x + 1, ofsy + 14)
            ofsx += text_width
            if end and i == len(self.exp_strings) - 1:
                blf.position(font_id, ofsx, ofsy, 0)
                blf.draw(font_id, end)
###############################################################################


class MESH_OT_vertex_slide(bpy.types.Operator):
    ''' Vertex slide '''
    bl_description = ''
    bl_idname = 'mesh.vertex_slide'
    bl_label = 'Vertex Slide'
    bl_options = {'REGISTER', 'UNDO'}

    dist = FloatProperty(name='Distance',
                         description='',
                         default=0.0,
                         min=-sys.float_info.max, max=sys.float_info.max,
                         soft_min=-sys.float_info.max,
                         soft_max=sys.float_info.max,
                         step=3, precision=2)#,
                         #subtype='DISTANCE', unit='LENGTH')

    isfactor = BoolProperty(name='Factor',
                             description='Dist consider as Factor',
                             default=False)

    mode = EnumProperty(items=(('vert', 'Vertex Slide', ''),
                               ('edge', 'Edge Slide', '')),
                               name='Mode',
                               description='',
                               default='vert')

    flip = IntProperty(name='Flip',
                       description='Direction. 0:center, -1or1:side',
                       default=0,
                       min=-1, max=1, soft_min=-1, soft_max=2)

    inputexpression = BoolProperty(name='Input chars',
                                   description='',
                                   default=False, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        actob = context.active_object
        return actob and actob.type == 'MESH' and actob.mode == 'EDIT'

    '''def check(context=None):
        # Check the operator settings.
        # Return type:	boolean
        return True
    '''

    def vertex_slide(self, context):
        mc_origin = self.mc.origin
        mc_relative = self.mc.relative
        mouseco = mc_origin + mc_relative
        mc_lock = self.mc.lock

        dist = self.dist
        edgelines = self.edgelines  # &#25551;&#30011;&#29992;
        translines = self.translines  # &#25551;&#30011;&#29992;
        pymesh = self.pymesh

        actob = context.active_object
        bm = bmesh.from_edit_mesh(actob.data)
        meverts = bm.verts
        matrix_world_inv = actob.matrix_world.copy()
        matrix_world_inv.invert()
        persmat = self.rv3d.perspective_matrix
        sx, sy = self.region.width, self.region.height

        mouse_init_worco = convert_window_to_world(mc_origin, persmat, sx, sy)
        mouse_worco = convert_window_to_world(mouseco, persmat, sx, sy)
        if mc_lock:
            mouse_middle_worco = convert_window_to_world(mc_lock, persmat, sx, sy)
            mouse_direction = mouse_middle_worco - mouse_init_worco
        else:
            mouse_direction = mouse_worco - mouse_init_worco  # (Relative)
        if mouse_direction.length < MIN_NUMBER:
            mouse_direction = Vector((1, 0, 0))
        edgelines[:] = []  # Clear
        translines[:] = []  # Clear
        for vert in (v for v in pymesh.verts if v.is_selected and v.verts):
            connected_vertices = [v for v in vert.verts if not v.hide]
            if not connected_vertices:
                continue
            for i in range(len(connected_vertices)):
                v = connected_vertices[i]
                if (v.worco - vert.worco).length < MIN_NUMBER:
                    connected_vertices.extend([vv for vv in v.verts if not vv.hide])
            angles = []
            zerolength = True
            for vertvert in connected_vertices:
                v = vertvert.worco - vert.worco
                if v.length >= MIN_NUMBER:
                    angles.append(mouse_direction.angle(v))
                    zerolength = False
                else:
                    angles.append(math.pi * 2)  # &#20778;&#20808;&#24230;&#26368;&#20302;
            if min(angles) == math.pi * 2:
                continue
            targetvert = connected_vertices[angles.index(min(angles))]
            transvec = targetvert.worco - vert.worco
            if self.isfactor:
                distance = dist if self.mc.lock else min(max(0, dist), 1)
            else:
                if not self.mc.lock:
                    distance = min(max(0, dist), transvec.length)
                    # dist = &#12392;&#12377;&#12427;&#12392;self.dist&#12398;&#20516;&#12434;&#32622;&#12365;&#25563;&#12360;&#12390;&#12375;&#12414;&#12358;
                else:
                    distance = dist
                transvec.normalize()
            if self.flip:
                newco = targetvert.worco - transvec * distance
            else:
                newco = vert.worco + transvec * distance
            # apply
            meverts[vert.index].co = matrix_world_inv * newco

            # edgelines
            if vert.winco:
                p1 = vert.winco
            else:
                p1 = vert.winco = convert_world_to_window(vert.worco, persmat, sx, sy)
            for vertvert in connected_vertices:
                if vertvert.winco:
                    p2 = vertvert.winco
                else:
                    p2 = vertvert.winco = convert_world_to_window(vertvert.worco, persmat, sx, sy)
                if vertvert == targetvert:
                    translines.append((p1, p2))
                else:
                    edgelines.append((p1, p2))

    def execute(self, context=None):
        #print('distance', self.dist, 'mode', self.mode, 'flip', self.flip)

        if self.mode == 'edge':
            #self.edge_slide(context)
            pass
        else:
            self.vertex_slide(context)
        return {'FINISHED'}

    def reset_vertices(self, context=None):
        pymesh = self.pymesh
        bm = bmesh.from_edit_mesh(context.active_object.data)
        for vert in bm.verts:
            vert.co = pymesh.verts[vert.index].co


    def draw_callback_px(self, context):
        # init
        font_id = 0
        #blf.position(font_id, 80, 30, 0)
        blf.size(font_id, 11, context.user_preferences.system.dpi)
        bgl.glColor4f(1.0, 1.0, 1.0, 1.0)

        ofsx = 70
        # draw Dist
        blf.position(font_id, ofsx, 50, 0)
        if self.isfactor:
            text_dist = '{0:>6.4f} x'.format(self.dist)
        else:
            text_dist = '{0:>6.4f}'.format(self.dist)
        blf.draw(font_id, text_dist)

        # draw Expression
        if self.inputexpression:
            text_width, text_height = blf.dimensions(font_id, text_dist)
            posx = max(ofsx + text_width + 15, 150)
            blf.position(font_id, posx, 50, 0)
            title = 'Exp: '
            if self.exp.get_exp_value(0):
                bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
            else:
                bgl.glColor4f(1.0, 0.5, 0.3, 1.0)
            blf.draw(font_id, title)
            text_width, text_height = blf.dimensions(font_id, title)
            posx += text_width
            bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
            self.exp.draw_exp_strings(font_id, posx, 50, end=' )')

        # draw Help
        textlist = ['{Tab}:InputString',
                    '{Del,BS}:ResetAll',
                    '{R}:ResetOrig',
                    '{M-Mouse}:Lock',
                    '{F}:Flip',
                    '{D}:Factor']
        blf.position(font_id, 70, 30, 0)
        blf.draw(font_id, ', '.join(textlist))

        bgl.glEnable(bgl.GL_BLEND)

        # draw mouseco_init
        self.mc.draw_origin(5)

        # draw mouseco_rerative
        self.mc.draw_relative(5)

        # draw mouseco_lock
        # mouseco_init&#12363;&#12425;&#12398;&#30690;&#21360;
        self.mc.draw_lock_arrow(8, math.radians(110))


        # draw edgelines
        bgl.glColor4f(0.8, 0.8, 0.8, 1.0)
        bgl.glBegin(bgl.GL_LINES)
        for p1, p2 in self.edgelines:
            bgl.glVertex2f(p1[0], p1[1])
            bgl.glVertex2f(p2[0], p2[1])
        if self.mc.lock:
            bgl.glColor4f(0.0, 0.0, 1.0, 1.0)
        else:
            bgl.glColor4f(1.0, 1.0, .0, 1.0)
        for p1, p2 in self.translines:
            bgl.glVertex2f(p1[0], p1[1])
            bgl.glVertex2f(p2[0], p2[1])
        bgl.glEnd()

        # restore opengl defaults
        bgl.glLineWidth(1)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
        blf.size(0, 11, context.user_preferences.system.dpi)

    def set_dist(self):
        if self.inputexpression:
            dist = self.exp.get_exp_value(0)
            if dist:
                self.dist = dist
            else:
                self.dist = self.mc.fac if self.isfactor else self.mc.dist
        else:
            self.dist = self.mc.fac if self.isfactor else self.mc.dist

    def modal(self, context=None, event=None):
        if print_event_modal:
            print_event(event)

        if self.inputexpression:  # eval&#12398;&#24335;&#12398;&#20837;&#21147;
            if event.value == 'PRESS':
                event_is_char = self.exp.input(event)
                if event_is_char:
                    self.set_dist()
                    '''
                    dist = self.exp.get_exp_value(0)
                    if dist:
                        self.dist = dist
                    else:
                        self.mc.update(context, event)
                    '''
                    self.execute(context)
                    context.area.tag_redraw()
                    return {'RUNNING_MODAL'}

        '''if self.exp.get_exp_value(0) is None or not self.inputexpression:
            obj_dist = self
        else:
            obj_dist = None
        '''
        mouseco = Vector((event.mouse_region_x, event.mouse_region_y, 0.0))
        if event.type in ('LEFT_SHIFT', 'RIGHT_SHIFT'):
            if event.value == 'PRESS':
                self.mc.shift = mouseco.copy()
            elif event.value == 'RELEASE':
                self.mc.shift = None
                self.mc.update(context, event)
                self.set_dist()
        elif event.type in ('LEFT_CTRL', 'RIGHT_CTRL'):
            if event.value == 'PRESS':
                self.mc.snap = True
            elif event.value == 'RELEASE':
                self.mc.snap = False
            self.mc.update(context, event)
            self.set_dist()
        elif event.type == 'MOUSEMOVE':
            # <Move Mouse>
            self.mc.update(context, event)
            self.set_dist()
        elif event.type in ('DEL', 'BACK_SPACE', 'R'):
            # <Reset>
            if event.value == 'PRESS':
                if self.mc.lock:
                    if event.type in ('DEL', 'BACK_SPACE'):
                        self.mc.lock = None
                    else:
                        self.mc.lock = self.mc.lock - self.mc.origin + mouseco
                if event.type in ('DEL', 'BACK_SPACE'):
                    self.flip = 0
                self.mc.origin = mouseco.copy()
                #self.mc.shift = None
                #self.mc.snap = False
                self.mc.update(context, event)
                self.set_dist()
        elif event.type == 'F':
            # <Flip>
            if event.value == 'PRESS':
                self.flip = abs(self.flip - 1)
        elif event.type == 'D':
            # <as Factor>
            if event.value == 'PRESS':
                self.isfactor = abs(self.isfactor - 1)
                self.set_dist()
        elif event.type == 'MIDDLEMOUSE':
            # <Lock Trans Axis>
            if event.value == 'PRESS':
                if self.mc.lock is None:
                    self.mc.lock = mouseco.copy()
                else:
                    self.mc.lock = None
        elif event.type == 'TAB':
            if event.value == 'PRESS':
                if self.inputexpression and (event.shift or event.ctrl):
                    self.inputexpression = False
                    self.mc.update(context, event)
                    self.set_dist()
                elif not self.inputexpression and not \
                                                  (event.shift or event.ctrl):
                    self.inputexpression = True
                    if self.exp.get_exp_value(0) is not None:
                        self.dist = self.exp.get_exp_value(0)
                    #self.mc.update(context, event)
        elif event.type in ('SPACE'):
            # <Toggle EDGE-SLIDE <-> VERT-SLIDE>
            # &#24037;&#20107;&#20013;
            '''if event.value == 'PRESS':
                self.mode = 'vert' if self.mode == 'edge' else 'edge'
            '''
            pass
        elif event.type in ('LEFTMOUSE', 'RET', 'NUMPAD_ENTER'):
            # <Finish>
            # self.execute(context)  # &#19981;&#35201;&#65311;
            context.region.callback_remove(self._handle)
            context.area.tag_redraw()
            return {'FINISHED'}
        elif event.type in ('RIGHTMOUSE', 'ESC'):
            # <Cancel>
            if event.value == 'PRESS':
                if self.inputexpression:  # shift = off
                    self.inputexpression = False
                    self.mc.update(context, event)
                    self.set_dist()
                else:
                    self.reset_vertices(context)
                    context.region.callback_remove(self._handle)
                    context.area.tag_redraw()
                    return {'CANCELLED'}
        if event.type in ('MOUSEMOVE', 'LEFT_SHIFT', 'RIGHT_SHIFT', \
                          'LEFT_CTRL', 'RIGHT_CTRL') or \
           event.value == 'PRESS':
            self.execute(context)
            context.area.tag_redraw()

        return {'RUNNING_MODAL'}  # PASS_THROUGH

    def invoke(self, context=None, event=None):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)
        self._handle = context.region.callback_add(self.__class__.draw_callback_px, (self, context), 'POST_PIXEL')
        # set mouse
        self.mc = MouseCoordinate(context, event, dpf=200)

        # set input expression
        self.exp = InputExpression(names=('eval(',))

        self.translines = []  # &#25551;&#30011;&#29992;&#12290;&#31227;&#21205;&#20013;&#12398;edge
        self.edgelines = []  # &#25551;&#30011;&#29992;&#12290;&#31227;&#21205;&#21487;&#33021;&#12394;edge
        # set region
        self.region = context.region
        self.v3d = context.space_data
        self.rv3d = context.region_data
        self.persmat = self.rv3d.perspective_matrix
        #self.viewmat = rv3d.view_matrix
        # set data
        bm = bmesh.from_edit_mesh(context.active_object.data)
        #self.paths = path_vertices_list(bm, select=True, hide=False)
        self.pymesh = PyMesh(bm)
        self.pymesh.calc_world_coordinate(context.active_object.matrix_world)

        context.area.tag_redraw()

        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(MESH_OT_vertex_slide)

def unregister():
    bpy.utils.unregister_class(MESH_OT_vertex_slide)

if __name__ == '__main__':
    register()
