import bpy
import bgl
from bpy_extras.view3d_utils import location_3d_to_region_2d as world_to_screen
from mathutils import Vector

before = 10
after = 10

def curve_info(fc) :
    info = {}
    for key in fc.keyframe_points :
        info[key.co[0]] = {'left_handle':key.handle_left,
                                    'right_handle':key.handle_right,
                                        'value':key.co[1],'is_key' : True}
    return info

def draw_callback(self,context) :
    ob = context.object
    current_frame = context.scene.frame_current
    action = ob.animation_data.action
    
    loc_x = action.fcurves.find('location',0)
    loc_y = action.fcurves.find('location',1)
    loc_z = action.fcurves.find('location',2)
    
    loc_x_info = curve_info(loc_x)
    loc_y_info = curve_info(loc_y)
    loc_z_info = curve_info(loc_z)

    keyframe_info = {}
    
    for frame in range(current_frame-before,current_frame+after) :
        if frame < current_frame :
            alpha = (before - (current_frame - frame )) / before *2
        else :
            alpha = (after - (frame - current_frame ))/ after *2

        keyframe_info[frame] = {'value':{},'left_handle' : {},'right_handle':{},'is_key':False,'alpha' : alpha}
        
        if frame in loc_x_info :
            keyframe_info[frame]['left_handle']['x'] = loc_x_info[frame]['left_handle']
            keyframe_info[frame]['right_handle']['x'] = loc_x_info[frame]['right_handle']
            keyframe_info[frame]['value']['x'] = loc_x_info[frame]['value']
            keyframe_info[frame]['is_key'] = True
        
        if frame in loc_y_info :
            keyframe_info[frame]['left_handle']['y'] = loc_y_info[frame]['left_handle']
            keyframe_info[frame]['right_handle']['y'] = loc_y_info[frame]['right_handle']
            keyframe_info[frame]['value']['y'] = loc_y_info[frame]['value']
            keyframe_info[frame]['is_key'] = True
                    
        if frame in loc_z_info :
            keyframe_info[frame]['left_handle']['z'] = loc_z_info[frame]['left_handle']
            keyframe_info[frame]['right_handle']['z'] = loc_z_info[frame]['right_handle']
            keyframe_info[frame]['value']['z'] = loc_z_info[frame]['value']
            keyframe_info[frame]['is_key'] = True
            
        if not keyframe_info[frame]['value'].get('x') :
            keyframe_info[frame]['value']['x'] = loc_x.evaluate(frame)
            
        if not keyframe_info[frame]['value'].get('y') :
            keyframe_info[frame]['value']['y'] = loc_y.evaluate(frame)
            
        if not keyframe_info[frame]['value'].get('z') :
            keyframe_info[frame]['value']['z'] = loc_z.evaluate(frame)
            
    print(keyframe_info)
            
    
    #keys = set(x_key+y_key+z_key)
    
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_DEPTH_TEST)
    #bgl.glLineWidth(1)

    #bgl.glPointSize(3)
    #bgl.glBegin(bgl.GL_POINTS)
    
    ## movement line
    bgl.glLineWidth(1)
    
    bgl.glBegin(bgl.GL_LINE_STRIP)
    for frame,info in sorted(keyframe_info.items()) :
        alpha = info['alpha']
        co = (info['value']['x'],info['value']['y'],info['value']['z'])
        
        bgl.glColor4f(0,0,0,alpha)
        bgl.glVertex3f(*co)
        
    bgl.glEnd()

    for frame,info in keyframe_info.items() :
        alpha = info['alpha']
        co = (info['value']['x'],info['value']['y'],info['value']['z'])        
        
        if info['is_key'] :
            handle_co_L = (info['left_handle']['x'][1],info['left_handle']['y'][1],info['left_handle']['z'][1])
            handle_co_R = (info['right_handle']['x'][1],info['right_handle']['y'][1],info['right_handle']['z'][1])
                        
            ###  handle point
            bgl.glPointSize(5)
            bgl.glBegin(bgl.GL_POINTS)
            bgl.glColor4f(0,0.5,1,alpha)
            
            bgl.glVertex3f(*handle_co_L)
            bgl.glVertex3f(*handle_co_R)
            bgl.glEnd()
            
            # line handle R
            bgl.glLineWidth(2)
            bgl.glBegin(bgl.GL_LINE_STRIP)
            bgl.glVertex3f(*co)
            bgl.glVertex3f(*handle_co_R)
            bgl.glEnd()
            
            # line handle L
            bgl.glBegin(bgl.GL_LINE_STRIP)
            bgl.glVertex3f(*co)
            bgl.glVertex3f(*handle_co_L)
            bgl.glEnd()
            
            ##KEYFRAME
            bgl.glPointSize(6)
            bgl.glBegin(bgl.GL_POINTS)
            bgl.glColor4f(1,1,0,alpha)
            
            bgl.glVertex3f(*co)
            bgl.glEnd()
            
        else :
            bgl.glPointSize(3)
            bgl.glColor4f(0.6,0.6,0.6,alpha)
            bgl.glBegin(bgl.GL_POINTS)
            
            bgl.glVertex3f(*co)
            bgl.glEnd()
            
            
    bgl.glEnd()
    
    


class ViewCameraField(bpy.types.Operator):
    bl_idname = "motionpath.diplay"
    bl_label = "Add Camera Frustum"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Press escape to quit"

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_3d, 'WINDOW')

            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        args = (self,context)
        self._handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_callback, args, 'WINDOW', 'POST_VIEW')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
bpy.utils.register_class(ViewCameraField)
