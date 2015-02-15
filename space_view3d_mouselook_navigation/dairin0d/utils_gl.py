#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

# <pep8 compliant>

import bgl

import math

#============================================================================#

# TODO: update to match the current API!
# TODO: implement all the OpenGL features (+other conveniences)
# TODO: documentation

'''
Speed tips:
* Static methods are faster than instance/class methods
  Seems like argument passing is a relatively expensive operation
* Closure dictionary lookup with constant key is faster:
    # non-arguments are assumed to be closure-bound objects
    def f(enum): g(enum)
    f(GL_BLEND) # bgl.GL_BLEND is even slower
    def f(enum): g(enums[enum])
    f('BLEND') # faster
'''

# Convention:
# UPPER_CASE is for enabled/disabled capabilities and constants
# CamelCase is for parameters/functions
# lower_case is for extra functionality

# Alternative:
# NAME/Name for set
# NAME_/Name_ for get
# or: get_Name, set_Name to not conflict with properties

class GLStateRestorator:
    def __init__(self, *args, **kwargs):
        _previous = {}
        for k in args:
            _previous[k] = getattr(cgl, k)
        for k, v in kwargs.items():
            _previous[k] = getattr(cgl, k)
            setattr(cgl, k, v)
        self._previous = _previous
    
    def restore(self):
        for k, v in self._previous.items():
            setattr(cgl, k, v)
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.restore()

def make_RenderBatch():
    # implementations:
    # None (same as mode, or compatible), LINES, TRIANGLES
    # also: VBO? DISPLAY_LIST?
    _gl_modes = {
        'POINTS':bgl.GL_POINTS,
        'LINES':bgl.GL_LINES,
        'LINE_STRIP':bgl.GL_LINE_STRIP,
        'LINE_LOOP':bgl.GL_LINE_LOOP,
        'TRIANGLES':bgl.GL_TRIANGLES,
        'TRIANGLE_STRIP':bgl.GL_TRIANGLE_STRIP,
        'TRIANGLE_FAN':bgl.GL_TRIANGLE_FAN,
        'QUADS':bgl.GL_QUADS,
        'QUAD_STRIP':bgl.GL_QUAD_STRIP,
        'POLYGON':bgl.GL_POLYGON,
        # CONVEX ?
    }
    _begin = bgl.glBegin
    _end = bgl.glEnd
    _vertex = bgl.glVertex4d
    
    class RenderBatch:
        def __init__(self, mode, implementation=None):
            self.mode = _gl_modes[mode]
        
        def begin(self):
            _begin(self.mode)
        
        def end(self):
            _end()
        
        def __enter__(self):
            self.begin()
            return self
        
        def __exit__(self, type, value, traceback):
            self.end()
        
        def vertex(self, x, y, z=0.0, w = 1.0):
            _vertex(x, y, z, w)
        
        def sequence(self, seq):
            for v in seq:
                self.vertex(*v)
        
        @staticmethod
        def circle(self, center, extents, resolution=2.0,
                   start=0.0, end=2.0*math.pi,
                   skip_start=0, skip_end=0, align=False):
            x0, y0 = center
            
            if isinstance(extents, (int, float)):
                xs = extents
                ys = extents
            else:
                xs, ys = extents
            
            sector = end - start
            
            if isinstance(resolution, int):
                n = resolution
            else:
                n = (abs(sector) * max(xs, ys)) / resolution
            
            modf = math.modf
            
            for i in range(skip_start, n - skip_end + 1):
                angle = start + (sector * i / n)
                nx = math.sin(angle)
                ny = math.cos(angle)
                x = x0 + nx * xs
                y = y0 + ny * ys
                if align:
                    yield modf(x)[1], modf(y)[1]
                else:
                    yield x, y
    
    return RenderBatch

RenderBatch = make_RenderBatch()
del make_RenderBatch

class CGL:
    def __call__(self, *args, **kwargs):
        return GLStateRestorator(*args, **kwargs)
    
    def batch(self, mode):
        return RenderBatch(mode)
    
    @staticmethod
    def read_zbuffer(xy, wh=(1, 1), centered=False, src=None):
        if isinstance(wh, (int, float)):
            wh = (wh, wh)
        elif len(wh) < 2:
            wh = (wh[0], wh[0])
        
        x, y, w, h = int(xy[0]), int(xy[1]), int(wh[0]), int(wh[1])
        
        if centered:
            x -= w // 2
            y -= h // 2
        
        buf_size = w*h
        
        if src is None:
            # xy is in window coordinates!
            zbuf = bgl.Buffer(bgl.GL_FLOAT, [buf_size])
            bgl.glReadPixels(x, y, w, h, bgl.GL_DEPTH_COMPONENT, bgl.GL_FLOAT, zbuf)
        else:
            src, w0, h0 = src
            template = [0.0] * buf_size
            for dy in range(h):
                y0 = min(max(y + dy, 0), h0-1)
                for dx in range(w):
                    x0 = min(max(x + dx, 0), w0-1)
                    i0 = x0 + y0 * w0
                    i1 = dx + dy * w
                    template[i1] = src[i0]
            zbuf = bgl.Buffer(bgl.GL_FLOAT, [buf_size], template)
        
        return zbuf
    
    @staticmethod
    def matrix_to_buffer(m, dtype=bgl.GL_FLOAT):
        return bgl.Buffer(dtype, 16, [m[i][j] for i in range(4) for j in range(4)])
    
    @staticmethod
    def polygon_stipple_from_list(L, zeros=False, tile=True):
        if isinstance(L, str):
            L = L.strip("\n").split("\n")
            if not isinstance(zeros, str):
                zeros = " "
        
        L_rows = len(L)
        if L_rows == 0:
            return [[0]*4]*32
        
        rows = []
        for i in range(32):
            if i >= L_rows:
                if tile:
                    rows.append(rows[i % L_rows])
                else:
                    rows.append([0, 0, 0, 0])
                continue
            
            L_col = L[i]
            L_cols = len(L_col)
            
            cols = [0, 0, 0, 0]
            j = 0
            for col in range(4):
                for shift in range(8):
                    if j >= L_cols:
                        if tile:
                            value = L_col[j % L_cols]
                        else:
                            value = zeros
                    else:
                        value = L_col[j]
                    
                    if value != zeros:
                        cols[col] |= 1 << (7 - shift)
                        #cols[col] |= 1 << shift
                    j += 1
            
            rows.append(cols)
        
        return list(reversed(rows))
        #return rows
    
    def CallList(self, id):
        pass

cgl = CGL()

def fill_CGL():
    def Cap(name, doc=""):
        pname = name[3:]
        if hasattr(CGL, pname):
            return
        
        is_enabled = bgl.glIsEnabled
        enabler = bgl.glEnable
        disabler = bgl.glDisable
        
        state_id = getattr(bgl, name)
        
        class Descriptor:
            __doc__ = doc
            def __get__(self, instance, owner):
                return is_enabled(state_id)
            def __set__(self, instance, value):
                (enabler if value else disabler)(state_id)
        
        setattr(CGL, pname, Descriptor())
    ###############################################################
    
    def State(name, doc, *params):
        pname = name[2:].split(":")[0]
        if hasattr(CGL, pname):
            return
        
        name = name.replace(":", "")
        
        localvars = {"doc":doc, "Buf":bgl.Buffer}
        
        args_info = []
        for param in params:
            arg_type = param[0]
            arg_key = param[1]
            state_getter = (param[2] if len(param) > 2 else None)
            
            getter_specific = "{0}"
            setter_specific = "{0}"
            
            arg_id = len(args_info)
            
            if isinstance(arg_type, set):
                data_type = bgl.GL_INT
                data_size = 1
                state_getter = state_getter or bgl.glGetIntegerv
                
                enum = {}
                enum_inv = {}
                for enum_item in arg_type:
                    enum_value = getattr(bgl, "GL_" + enum_item)
                    enum[enum_item] = enum_value
                    enum_inv[enum_value] = enum_item
                
                localvars["_enum%s" % arg_id] = enum
                localvars["_enum_inv%s" % arg_id] = enum_inv
                
                getter_specific = "_enum_inv%s[{0}]" % arg_id
                setter_specific = "_enum%s[{0}]" % arg_id
            elif arg_type.startswith("int"):
                data_type = bgl.GL_INT
                data_size = eval(arg_type.split(":")[1])
                state_getter = state_getter or bgl.glGetIntegerv
            elif arg_type.startswith("float"):
                data_type = bgl.GL_FLOAT
                data_size = eval(arg_type.split(":")[1])
                state_getter = state_getter or bgl.glGetFloatv
            else:
                data_type = None
                data_size = None
                state_getter = None
            
            if data_size == 1:
                getter_specific = getter_specific.format("{0}[0]")
                setter_specific = setter_specific.format("{0}")
            else:
                getter_specific = getter_specific.format("{0}.to_list()")
                setter_specific = setter_specific.format("Buf(_type%s, %s, {0})" % (arg_id, data_size))
            
            state_id = (None if arg_key is None else getattr(bgl, arg_key))
            buf = bgl.Buffer(data_type, data_size)
            
            localvars["_getter%s" % arg_id] = state_getter
            localvars["_state_id%s" % arg_id] = state_id
            localvars["_buf%s" % arg_id] = buf
            localvars["_type%s" % arg_id] = data_type
            
            args_info.append((getter_specific, setter_specific))
        
        getter_lines = []
        setter_lines = []
        return_args = []
        setter_args = []
        any_specific = False
        for i in range(len(args_info)):
            getter_specific, setter_specific = args_info[i]
            
            if localvars["_state_id%s" % i] is None:
                getter_lines.append("   _getter{0}(_buf{0})".format(i))
            else:
                getter_lines.append("   _getter{0}(_state_id{0}, _buf{0})".format(i))
            
            return_args.append(getter_specific.format("_buf%s" % i))
            
            if setter_specific != "{0}":
                any_specific = True
            setter_args.append(setter_specific.format("value[%s]" % i))
        
        if len(args_info) == 1:
            setter_args = [args_info[0][1].format("value")]
        elif not any_specific:
            setter_args = ["*value"]
        
        localvars["_setter"] = getattr(bgl, name)
        
        get_body = "{0}\n   return {1}".format("\n".join(getter_lines), ", ".join(return_args))
        set_body = "{0}\n   _setter({1})".format("\n".join(setter_lines), ", ".join(setter_args))
        
        code = """
def make(**kwargs):
 locals().update(kwargs)
 class Descriptor:
  __doc__ = doc
  def __get__(self, instance, owner):\n{0}
  def __set__(self, instance, value):\n{1}
 return Descriptor
""".format(get_body, set_body)
        #print(code)
        exec(code, localvars, localvars)
        
        Descriptor = localvars["make"](**localvars)
        
        setattr(CGL, pname, Descriptor())
    ###############################################################
    
    def PolygonStipple():
        data_type = bgl.GL_BYTE
        data_size = [32, 4] # [32, 32] in Blender docs
        
        Buf = bgl.Buffer
        buf = Buf(data_type, data_size)
        
        setter = bgl.glPolygonStipple
        getter = bgl.glGetPolygonStipple
        
        class Descriptor:
            __doc__ = ""
            def __get__(self, instance, owner):
                getter(buf)
                return buf.to_list()
            def __set__(self, instance, value):
                setter(Buf(data_type, data_size, value))
        
        setattr(CGL, "PolygonStipple", Descriptor())
    ###############################################################
    
    Cap('GL_ALPHA_TEST')
    Cap('GL_AUTO_NORMAL')
    Cap('GL_BLEND')
    for i in range(6):
        Cap('GL_CLIP_PLANE%s' % i)
    #Cap('GL_COLOR_LOGIC_OP')
    Cap('GL_COLOR_MATERIAL')
    #Cap('GL_COLOR_TABLE')
    #Cap('GL_CONVOLUTION_1D')
    #Cap('GL_CONVOLUTION_2D')
    Cap('GL_CULL_FACE')
    Cap('GL_DEPTH_TEST')
    Cap('GL_DEPTH_WRITEMASK')
    Cap('GL_DITHER')
    Cap('GL_FOG')
    #Cap('GL_HISTOGRAM')
    #Cap('GL_INDEX_LOGIC_OP')
    for i in range(8):
        Cap('GL_LIGHT%s' % i)
    Cap('GL_LIGHTING')
    Cap('GL_LINE_SMOOTH')
    Cap('GL_LINE_STIPPLE')
    for i in (1, 2):
        Cap('GL_MAP%s_COLOR_4' % i)
        Cap('GL_MAP%s_INDEX' % i)
        Cap('GL_MAP%s_NORMAL' % i)
        for j in (1, 2, 3, 4):
            Cap('GL_MAP%s_TEXTURE_COORD_%s' % (i, j))
        for j in (3, 4):
            Cap('GL_MAP%s_VERTEX_%s' % (i, j))
    #Cap('GL_MINMAX')
    Cap('GL_NORMALIZE')
    Cap('GL_POINT_SMOOTH')
    Cap('GL_POLYGON_OFFSET_FILL')
    Cap('GL_POLYGON_OFFSET_LINE')
    Cap('GL_POLYGON_OFFSET_POINT')
    Cap('GL_POLYGON_SMOOTH')
    Cap('GL_POLYGON_STIPPLE')
    #Cap('GL_POST_COLOR_MATRIX_COLOR_TABLE')
    #Cap('GL_POST_CONVOLUTION_COLOR_TABLE')
    #Cap('GL_RESCALE_NORMAL')
    #Cap('GL_SEPARABLE_2D')
    Cap('GL_SCISSOR_TEST')
    Cap('GL_STENCIL_TEST')
    # currently 3D texture cap not defined in bgl
    for i in (1, 2):#(1, 2, 3):
        Cap('GL_TEXTURE_%sD' % i)
    for c in "QRST":
        Cap('GL_TEXTURE_GEN_%s' % c)
    
    State('glLineWidth', "", ("int:1", 'GL_LINE_WIDTH'))
    State('glShadeModel', "", ({'FLAT', 'SMOOTH'}, 'GL_SHADE_MODEL'))
    State('glColor:4fv', "", ("float:4", 'GL_CURRENT_COLOR')) # GL_COLOR ?
    State('glColor3:fv', "", ("float:3", 'GL_CURRENT_COLOR')) # GL_COLOR ?
    State('glBlendFunc', "", # Somewhy CONST modes aren't present in bgl %)
        ({'ZERO', 'ONE', 'SRC_COLOR', 'ONE_MINUS_SRC_COLOR', 'DST_COLOR', 'ONE_MINUS_DST_COLOR', 'SRC_ALPHA', 'ONE_MINUS_SRC_ALPHA', 'DST_ALPHA', 'ONE_MINUS_DST_ALPHA', 'SRC_ALPHA_SATURATE'}, 'GL_BLEND_SRC'),
        ({'ZERO', 'ONE', 'SRC_COLOR', 'ONE_MINUS_SRC_COLOR', 'DST_COLOR', 'ONE_MINUS_DST_COLOR', 'SRC_ALPHA', 'ONE_MINUS_SRC_ALPHA', 'DST_ALPHA', 'ONE_MINUS_DST_ALPHA'}, 'GL_BLEND_DST'))
    # added 2015-01-02
    State('glDepthFunc', "", ({'NEVER', 'LESS', 'EQUAL', 'LEQUAL', 'GREATER', 'NOTEQUAL', 'GEQUAL', 'ALWAYS'}, 'GL_DEPTH_FUNC'))
    State('glLineStipple', "", ("int:1", 'GL_LINE_STIPPLE_REPEAT'), ("int:1", 'GL_LINE_STIPPLE_PATTERN'))
    State('glPolygonStipple', "", ("int:32,4", None, bgl.glGetPolygonStipple)) # TODO: check if this actually works
    
    #PolygonStipple()

fill_CGL()
del fill_CGL
