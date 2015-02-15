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

#__all__ = ("module1", "module2", etc.) # in case we want to not export something

import bpy
import bgl

from mathutils import Color, Vector, Matrix, Quaternion, Euler

from bpy_extras.view3d_utils import (
    region_2d_to_location_3d,
    location_3d_to_region_2d,
    region_2d_to_vector_3d,
    region_2d_to_origin_3d,
)

import math

from .utils_math import matrix_LRS, angle_signed, snap_pixel_vector, lerp
from .utils_ui import calc_region_rect

class SmartView3D:
    def __init__(self, context=None):
        if context is None:
            context = bpy.context
        self.userprefs = bpy.context.user_preferences
        self.window = context.window # expected type: Window
        self.area = context.area # expected type: Area
        self.region = context.region # expected type: Region
        self.space_data = context.space_data # expected type: SpaceView3D
        self.region_data = context.region_data # expected type: RegionView3D
        self.use_camera_axes = False
        self.use_viewpoint =  False
        self.bypass_camera_lock = False
    
    def __get(self):
        return self.space_data.lock_cursor
    def __set(self, value):
        self.space_data.lock_cursor = value
    lock_cursor = property(__get, __set)
    
    def __get(self):
        return self.space_data.lock_object
    def __set(self, value):
        self.space_data.lock_object = value
    lock_object = property(__get, __set)
    
    def __get(self):
        return self.space_data.lock_bone
    def __set(self, value):
        self.space_data.lock_bone = value
    lock_bone_name = property(__get, __set)
    
    def __get(self):
        v3d = self.space_data
        obj = v3d.lock_object
        if obj and (obj.type == 'ARMATURE') and v3d.lock_bone:
            try:
                if obj.mode == 'EDIT':
                    return obj.data.edit_bones[v3d.lock_bone]
                else:
                    return obj.data.bones[v3d.lock_bone]
            except:
                pass
        return None
    def __set(self, value):
        self.space_data.lock_bone = (value.name if value else "")
    lock_bone = property(__get, __set)
    
    def __get(self):
        return self.space_data.lock_camera or self.bypass_camera_lock
    def __set(self, value):
        self.space_data.lock_camera = value
    lock_camera = property(__get, __set)
    
    def __get(self):
        return self.userprefs.view.use_camera_lock_parent
    def __set(self, value):
        self.userprefs.view.use_camera_lock_parent = value
    lock_camera_parent = property(__get, __set)
    
    def __get(self):
        return self.space_data.region_3d
    region_3d = property(__get)
    
    def __get(self):
        return self.region_data == self.space_data.region_3d
    is_region_3d = property(__get)
    
    # 0: bottom left (Front Ortho)
    # 1: top left (Top Ortho)
    # 2: bottom right (Right Ortho)
    # 3: top right (User Persp)
    def __get(self):
        return getattr(self.space_data, "region_quadviews")
    quadviews = property(__get)
    
    def __get(self):
        return bool(self.quadviews)
    quadview_enabled = property(__get)
    
    def __get(self):
        return self.region_data.lock_rotation
    def __set(self, value):
        self.region_data.lock_rotation = value
    quadview_lock = property(__get, __set)
    
    def __get(self):
        return self.region_data.show_sync_view
    def __set(self, value):
        self.region_data.show_sync_view = value
    quadview_sync = property(__get, __set)
    
    def __get(self):
        return Vector(self.region_data.view_camera_offset)
    def __set(self, value):
        self.region_data.view_camera_offset = value
    camera_offset = property(__get, __set)
    
    def __get(self):
        value = self.camera_offset
        value = Vector((value.x * self.region.width, value.y * self.region.height))
        return value * self.camera_zoom_scale
    def __set(self, value):
        value = value * (1.0 / self.camera_zoom_scale)
        value = Vector((value.x / self.region.width, value.y / self.region.height))
        self.camera_offset = value
    camera_offset_pixels = property(__get, __set)
    
    def __get(self):
        return self.region_data.view_camera_zoom
    def __set(self, value):
        self.region_data.view_camera_zoom = value
    camera_zoom = property(__get, __set)
    
    # See source\blender\blenkernel\intern\screen.c
    def __get(self):
        # BKE_screen_view3d_zoom_to_fac magic formula
        value = math.pow(math.sqrt(2.0) + self.camera_zoom / 50.0, 2.0) / 4.0
        return value * 2 # using Blender's formula, at 0 the result is 0.5
    def __set(self, value):
        value *= 0.5
        # BKE_screen_view3d_zoom_from_fac magic formula
        self.camera_zoom = (math.sqrt(4.0 * value) - math.sqrt(2.0)) * 50.0
    camera_zoom_scale = property(__get, __set)
    
    def __get(self):
        return self.space_data.camera
    def __set(self, value):
        self.space_data.camera = value
    camera = property(__get, __set)
    
    def __get(self):
        if self.is_camera and (self.camera.type == 'CAMERA'):
            return self.camera.data.lens
        else:
            return self.space_data.lens
    def __set(self, value):
        if self.is_camera and (self.camera.type == 'CAMERA'):
            if self.lock_camera:
                self.camera.data.lens = value
        else:
            self.space_data.lens = value
    lens = property(__get, __set)
    
    def __get(self):
        if self.is_camera and (self.camera.type == 'CAMERA'):
            return self.camera.data.clip_start
        else:
            return self.space_data.clip_start
    def __set(self, value):
        if self.is_camera and (self.camera.type == 'CAMERA'):
            if self.lock_camera:
                self.camera.data.clip_start = value
        else:
            self.space_data.clip_start = value
    clip_start = property(__get, __set)
    
    def __get(self):
        if self.is_camera and (self.camera.type == 'CAMERA'):
            return self.camera.data.clip_end
        else:
            return self.space_data.clip_end
    def __set(self, value):
        if self.is_camera and (self.camera.type == 'CAMERA'):
            if self.lock_camera:
                self.camera.data.clip_end = value
        else:
            self.space_data.clip_end = value
    clip_end = property(__get, __set)
    
    def __get(self):
        return ((self.region_data.view_perspective == 'CAMERA') and bool(self.space_data.camera))
    def __set(self, value):
        if value and self.space_data.camera:
            self.region_data.view_perspective = 'CAMERA'
        elif self.region_data.is_perspective:
            self.region_data.view_perspective = 'PERSP'
        else:
            self.region_data.view_perspective = 'ORTHO'
    is_camera = property(__get, __set)
    
    def __get(self):
        return self.lock_camera or not self.is_camera
    can_move = property(__get)
    
    def __get(self):
        if self.is_camera:
            if (self.camera.type == 'CAMERA'):
                return self.camera.data.type != 'ORTHO'
            else:
                return True
        else:
            return self.region_data.is_perspective
    def __set(self, value):
        if self.is_camera:
            if self.lock_camera:
                if (self.camera.type == 'CAMERA'):
                    cam_data = self.camera.data
                    old_value = (cam_data.type != 'ORTHO')
                    if value != old_value:
                        if cam_data.type == 'ORTHO':
                            cam_data.type = 'PERSP'
                        else:
                            cam_data.type = 'ORTHO'
        elif self.is_region_3d or not self.quadview_lock:
            self.region_data.is_perspective = value
            if value:
                self.region_data.view_perspective = 'PERSP'
            else:
                self.region_data.view_perspective = 'ORTHO'
    is_perspective = property(__get, __set)
    
    def __get(self):
        return self.region_data.view_distance
    def __set(self, value):
        if self.quadview_sync and (not self.is_region_3d):
            quadviews = self.quadviews
            quadviews[0].view_distance = value
            quadviews[0].update()
            quadviews[1].view_distance = value
            quadviews[1].update()
            quadviews[2].view_distance = value
            quadviews[2].update()
        else:
            self.region_data.view_distance = value
            self.region_data.update()
    raw_distance = property(__get, __set)
    
    def __get(self):
        return self.region_data.view_location.copy()
    def __set(self, value):
        if self.quadview_sync and (not self.is_region_3d):
            quadviews = self.quadviews
            quadviews[0].view_location = value.copy()
            quadviews[0].update()
            quadviews[1].view_location = value.copy()
            quadviews[1].update()
            quadviews[2].view_location = value.copy()
            quadviews[2].update()
        else:
            self.region_data.view_location = value.copy()
            self.region_data.update()
    raw_location = property(__get, __set)
    
    def __get(self):
        value = self.region_data.view_rotation.copy()
        if not self.use_camera_axes:
            value = value * Quaternion((1, 0, 0), -math.pi*0.5)
        return value
    def __set(self, value):
        if not self.use_camera_axes:
            value = value * Quaternion((1, 0, 0), math.pi*0.5)
        if self.is_region_3d or (not self.quadview_lock):
            self.region_data.view_rotation = value.copy()
            self.region_data.update()
    raw_rotation = property(__get, __set)
    
    def __get(self):
        return (self.viewpoint if self.use_viewpoint else self.focus)
    def __set(self, value):
        if self.use_viewpoint:
            self.viewpoint = value
        else:
            self.focus = value
    pivot = property(__get, __set)
    
    def __get(self):
        if self.is_camera and (self.camera.type == 'CAMERA') and (self.camera.data.type == 'ORTHO'):
            return self.camera.data.ortho_scale
        else:
            return self.raw_distance
    def __set(self, value):
        pivot = self.pivot
        value = max(value, 1e-12) # just to be sure that it's never zero or negative
        if self.is_camera and (self.camera.type == 'CAMERA') and (self.camera.data.type == 'ORTHO'):
            if self.lock_camera:
                self.camera.data.ortho_scale = value
        else:
            self.raw_distance = value
        self.pivot = pivot
    distance = property(__get, __set)
    
    def __set_cam_matrix(self, m):
        cam = self.space_data.camera
        if self.lock_camera_parent:
            max_parent = cam
            while True:
                if (max_parent.parent is None) or (max_parent.parent_type == 'VERTEX'):
                    break # 'VERTEX' isn't a rigidbody-type transform
                max_parent = max_parent.parent
            cm_inv = cam.matrix_world.inverted()
            pm = cm_inv * max_parent.matrix_world
            max_parent.matrix_world = m * pm
        else:
            cam.matrix_world = m
    
    def __get(self):
        v3d = self.space_data
        rv3d = self.region_data
        if self.is_camera:
            m = v3d.camera.matrix_world
            return m.translation + self.forward * rv3d.view_distance
        elif v3d.lock_object:
            obj = self.lock_object
            bone = self.lock_bone
            m = obj.matrix_world
            if bone:
                m = m * (bone.matrix if obj.mode == 'EDIT' else bone.matrix_local)
            return m.translation.copy()
        elif v3d.lock_cursor:
            return v3d.cursor_location.copy()
        else:
            return self.raw_location
    def __set(self, value):
        v3d = self.space_data
        rv3d = self.region_data
        if self.is_camera:
            if self.lock_camera:
                m = v3d.camera.matrix_world.copy()
                m.translation = value - self.forward * rv3d.view_distance
                self.__set_cam_matrix(m)
        elif v3d.lock_object:
            pass
        elif v3d.lock_cursor:
            pass
        else:
            self.raw_location = value
    focus = property(__get, __set)
    
    # Camera (and viewport): -Z is forward, Y is up, X is right
    def __get(self):
        v3d = self.space_data
        rv3d = self.region_data
        if self.is_camera:
            value = v3d.camera.matrix_world.to_quaternion()
            if not self.use_camera_axes:
                value = value * Quaternion((1, 0, 0), -math.pi*0.5)
        else:
            value = self.raw_rotation
        return value
    def __set(self, value):
        v3d = self.space_data
        rv3d = self.region_data
        pivot = self.pivot
        if self.is_camera:
            if not self.use_camera_axes:
                value = value * Quaternion((1, 0, 0), math.pi*0.5)
            if self.lock_camera:
                LRS = v3d.camera.matrix_world.decompose()
                m = matrix_LRS(LRS[0], value, LRS[2])
                forward = -m.col[2].to_3d().normalized() # in camera axes, forward is -Z
                m.translation = self.focus - forward * rv3d.view_distance
                self.__set_cam_matrix(m)
        else:
            self.raw_rotation = value
        self.pivot = pivot
    rotation = property(__get, __set)
    
    def __get(self): # in object axes
        world_x = Vector((1, 0, 0))
        world_z = Vector((0, 0, 1))
        
        x = self.right # right
        y = self.forward # forward
        z = self.up # up
        
        if abs(y.z) > (1 - 1e-12): # sufficiently close to vertical
            roll = 0.0
            xdir = x.copy()
        else:
            xdir = y.cross(world_z)
            rollPos = angle_signed(-y, x, xdir, 0.0)
            rollNeg = angle_signed(-y, x, -xdir, 0.0)
            if abs(rollNeg) < abs(rollPos):
                roll = rollNeg
                xdir = -xdir
            else:
                roll = rollPos
        xdir = Vector((xdir.x, xdir.y, 0)).normalized()
        
        yaw = angle_signed(-world_z, xdir, world_x, 0.0)
        
        zdir = xdir.cross(y).normalized()
        pitch = angle_signed(-xdir, zdir, world_z, 0.0)
        
        return Euler((pitch, roll, yaw), 'YXZ')
    def __set(self, value): # in object axes
        rot_x = Quaternion((1, 0, 0), value.x)
        rot_y = Quaternion((0, 1, 0), value.y)
        rot_z = Quaternion((0, 0, 1), value.z)
        rot = rot_z * rot_x * rot_y
        if self.use_camera_axes:
            rot = rot * Quaternion((1, 0, 0), math.pi*0.5)
        self.rotation = rot
    turntable_euler = property(__get, __set)
    
    def __get(self):
        v3d = self.space_data
        rv3d = self.region_data
        if self.is_camera:
            return v3d.camera.matrix_world.translation.copy()
        else:
            return self.focus - self.forward * rv3d.view_distance
    def __set(self, value):
        self.focus = self.focus + (value - self.viewpoint)
    viewpoint = property(__get, __set)
    
    def __get(self, viewpoint=False):
        m = self.rotation.to_matrix()
        m.resize_4x4()
        m.translation = (self.viewpoint if viewpoint else self.focus)
        return m
    def __set(self, m, viewpoint=False):
        if viewpoint:
            self.viewpoint = m.translation.copy()
        else:
            self.focus = m.translation.copy()
        self.rotation = m.to_quaternion()
    matrix = property(__get, __set)
    
    def __get_axis(self, x, y, z):
        rot = self.rotation
        if self.use_camera_axes:
            rot = rot * Quaternion((1, 0, 0), -math.pi*0.5)
        return (rot * Vector((x, y, z))).normalized()
    forward = property(lambda self: self.__get_axis(0, 1, 0))
    back = property(lambda self: self.__get_axis(0, -1, 0))
    up = property(lambda self: self.__get_axis(0, 0, 1))
    down = property(lambda self: self.__get_axis(0, 0, -1))
    left = property(lambda self: self.__get_axis(-1, 0, 0))
    right = property(lambda self: self.__get_axis(1, 0, 0))
    
    def project(self, pos, align=False): # 0,0 means region's bottom left corner
        region = self.region
        rv3d = self.region_data
        xy = location_3d_to_region_2d(region, rv3d, pos.copy())
        if align:
            xy = snap_pixel_vector(xy)
        return xy
    
    def unproject(self, xy, pos=None, align=False): # 0,0 means region's bottom left corner
        if align:
            xy = snap_pixel_vector(xy)
        if pos is None:
            pos = self.focus
        elif isinstance(pos, (int, float)):
            pos = self.zbuf_range[2] + self.forward * pos
        region = self.region
        rv3d = self.region_data
        return region_2d_to_location_3d(region, rv3d, xy.copy(), pos.copy())
    
    def ray(self, xy): # 0,0 means region's bottom left corner
        region = self.region
        rv3d = self.region_data
        
        view_dir = self.forward
        near, far, origin = self.zbuf_range
        near = origin + view_dir * near
        far = origin + view_dir * far
        
        # Just to be sure (sometimes scene.ray_cast sayid that ray start/end aren't 3D)
        a = region_2d_to_location_3d(region, rv3d, Vector(xy).to_2d(), near).to_3d()
        b = region_2d_to_location_3d(region, rv3d, Vector(xy).to_2d(), far).to_3d()
        return a, b
    
    @staticmethod
    def read_zbuffer(xy, wh=(1, 1)): # xy is in window coordinates!
        if isinstance(wh, (int, float)):
            wh = (wh, wh)
        elif len(wh) < 2:
            wh = (wh[0], wh[0])
        x, y, w, h = int(xy[0]), int(xy[1]), int(wh[0]), int(wh[1])
        zbuf = bgl.Buffer(bgl.GL_FLOAT, [w*h])
        bgl.glReadPixels(x, y, w, h, bgl.GL_DEPTH_COMPONENT, bgl.GL_FLOAT, zbuf)
        return zbuf
    
    def zbuf_to_depth(self, zbuf):
        near, far, origin = self.zbuf_range
        depth_linear = zbuf*far + (1.0 - zbuf)*near
        if self.is_perspective:
            return (far * near) / (zbuf*near + (1.0 - zbuf)*far)
        else:
            return zbuf*far + (1.0 - zbuf)*near
    
    def depth(self, xy, region_coords=True):
        if region_coords: # convert to window coords
            xy = xy + Vector((self.region.x, self.region.y))
        return self.zbuf_to_depth(self.read_zbuffer(xy)[0])
    
    def __get(self):
        rv3d = self.region_data
        if rv3d.is_perspective or (rv3d.view_perspective == 'CAMERA'):
            return (self.clip_start, self.clip_end, self.viewpoint)
        return (-self.clip_end*0.5, self.clip_end*0.5, self.focus)
    zbuf_range = property(__get)
    
    def z_distance(self, pos, clamp_near=None, clamp_far=None):
        if clamp_far is None:
            clamp_far = clamp_near
        
        near, far, origin = self.zbuf_range
        dist = (pos - origin).dot(self.forward)
        
        if self.is_perspective:
            if clamp_near is not None:
                dist = max(dist, near * (1.0 + clamp_near))
            if clamp_far is not None:
                dist = min(dist, far * (1.0 - clamp_far))
        else:
            if clamp_near is not None:
                dist = max(dist, lerp(near, far, clamp_near))
            if clamp_far is not None:
                dist = min(dist, lerp(far, near, clamp_far))
        
        return dist
    
    def region_rect(self, overlap=True):
        return calc_region_rect(self.area, self.region, overlap)
    
    def __get(self):
        region_center = Vector((self.region.width, self.region.height)) * 0.5
        if self.is_camera and (not self.is_perspective):
            return region_center # Somewhy Blender behaves like this
        return region_center - self.camera_offset_pixels
    focus_projected = property(__get)
    
    del __get
    del __set
