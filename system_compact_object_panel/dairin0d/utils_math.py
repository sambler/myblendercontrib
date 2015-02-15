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

from mathutils import Color, Vector, Matrix, Quaternion, Euler

import math

def lerp(v0, v1, t):
    return v0 * (1.0 - t) + v1 * t

def clamp(v, v_min, v_max):
    return (v_min if (v < v_min) else (v if v < v_max else v_max))
    #return min(max(v, v_min), v_max)

def round_step(x, s=1.0):
    #return math.floor(x * s + 0.5) / s
    return math.floor(x / s + 0.5) * s

twoPi = 2.0 * math.pi
def clamp_angle(ang):
    # Attention! In Python the behaviour is:
    # -359.0 % 180.0 == 1.0
    # -359.0 % -180.0 == -179.0
    ang = (ang % twoPi)
    return ((ang - twoPi) if (ang > math.pi) else ang)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!! TODO: check if Blender has a correct implementation now !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def angle_axis_to_quat(angle, axis):
    w = math.cos(angle / 2.0)
    xyz = axis.normalized() * math.sin(angle / 2.0)
    return Quaternion((w, xyz.x, xyz.y, xyz.z))

def angle_signed(n, v0, v1, fallback=None):
    angle = v0.angle(v1, fallback)
    if (angle != fallback) and (angle > 0):
        angle *= math.copysign(1.0, v0.cross(v1).dot(n))
    return angle

def snap_pixel_vector(v, d=0.5): # to have 2d-stable 3d drawings
    return Vector((round(v.x)+d, round(v.y)+d))

def matrix_LRS(L, R, S):
    m = R.to_matrix()
    m.col[0] *= S[0]
    m.col[1] *= S[1]
    m.col[2] *= S[2]
    m.resize_4x4()
    m.translation = L
    return m

def matrix_compose(*args):
    size = len(args)
    m = Matrix.Identity(size)
    axes = m.col # m.row
    
    if size == 2:
        for i in (0, 1):
            c = args[i]
            if isinstance(c, Vector):
                axes[i] = c.to_2d()
            elif hasattr(c, "__iter__"):
                axes[i] = Vector(c).to_2d()
            else:
                axes[i][i] = c
    else:
        for i in (0, 1, 2):
            c = args[i]
            if isinstance(c, Vector):
                axes[i][:3] = c.to_3d()
            elif hasattr(c, "__iter__"):
                axes[i][:3] = Vector(c).to_3d()
            else:
                axes[i][i] = c
        
        if size == 4:
            c = args[3]
            if isinstance(c, Vector):
                m.translation = c.to_3d()
            elif hasattr(c, "__iter__"):
                m.translation = Vector(c).to_3d()
    
    return m

def matrix_decompose(m, res_size=None):
    size = len(m)
    axes = m.col # m.row
    if res_size is None:
        res_size = size
    
    if res_size == 2:
        return (axes[0].to_2d(), axes[1].to_2d())
    else:
        x = axes[0].to_3d()
        y = axes[1].to_3d()
        z = (axes[2].to_3d() if size > 2 else Vector())
        if res_size == 3:
            return (x, y, z)
        
        t = (m.translation.to_3d() if size == 4 else Vector())
        if res_size == 4:
            return (x, y, z, t)
