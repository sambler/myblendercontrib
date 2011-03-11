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


bl_info = {
    'name': 'Display Keys Status for Screencasting',
    'author': 'Paulo Gomes, Bartius Crouch',
    'version': (1, 0),
    'blender': (2, 5, 6),
    'api': 35457,
    'location': 'View3D > Properties panel > Display tab',
    'warning': '',
    'description': 'Display keys pressed in the 3d-view, '\
        'useful for screencasts.',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.5/'\
        'Py/Scripts/3D_interaction/Screencast_Key_Status_Tool',
    'tracker_url': 'http://projects.blender.org/tracker/index.php?'\
        'func=detail&aid=21612',
    'category': '3D View'}


import bgl
import blf
import bpy
import time


def draw_callback_px(self, context):
    wm = context.window_manager
    if wm.display_keys:
        # draw text in the 3d-view
        blf.size(0, wm.display_font_size, 72)
        r, g, b = wm.display_color
        bgl.glColor3f(r, g, b)
        final = 0
        
        # only display key-presses of last 2 seconds
        for i in range(len(self.key)):
            if time.time()-self.time[i] < 2:
                blf.position(0, wm.display_pos_x,
                    wm.display_pos_y + wm.display_font_size*i, 0)
                blf.draw(0, self.key[i])
                final = i
            else:
                break

        # get rid of statuses that aren't displayed anymore
        self.key = self.key[:final+1]
        self.time = self.time[:final+1]
    else:
        return


class ScreencastKeysStatus(bpy.types.Operator):
    bl_idname = "view3d.screencast_keys"
    bl_label = "Screencast Key Status Tool"
    bl_description = "Display keys pressed in the 3D-view"
    
    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        # keys that shouldn't show up in the 3d-view
        mouse_keys = ['MOUSEMOVE','MIDDLEMOUSE','LEFTMOUSE',
         'RIGHTMOUSE', 'WHEELDOWNMOUSE','WHEELUPMOUSE']
        ignore_keys = ['LEFT_SHIFT', 'RIGHT_SHIFT', 'LEFT_ALT',
         'RIGHT_ALT', 'LEFT_CTRL', 'RIGHT_CTRL', 'TIMER']
        if not context.window_manager.display_mouse:
            ignore_keys.extend(mouse_keys)

        if event.value == 'PRESS':
            # add key-press to display-list
            sc_keys = []
            
            if event.ctrl:
                sc_keys.append("Ctrl ")
            if event.alt:
                sc_keys.append("Alt ")
            if event.shift:
                sc_keys.append("Shift ")
            
            if event.type not in ignore_keys:
                sc_keys.append(event.type)
                self.key.insert(0, "+ ".join(map(str, sc_keys)))
                self.time.insert(0, time.time())
        
        if not context.window_manager.display_keys:
            # stop script
            context.region.callback_remove(self._handle)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            if context.window_manager.display_keys == False:
                # operator is called for the first time, start everything
                context.window_manager.display_keys = True
                context.window_manager.modal_handler_add(self)
                self._handle = context.region.callback_add(draw_callback_px,
                    (self, context), 'POST_PIXEL')
                self.key = []
                self.time = []
                return {'RUNNING_MODAL'}
            else:
                # operator is called again, stop displaying
                context.window_manager.display_keys = False
                self.key = []
                self.time = []
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "View3D not found, can't run operator")
            return {'CANCELLED'}


# properties used by the script
def init_properties():
    bpy.types.WindowManager.display_keys = bpy.props.BoolProperty(
        default=False)
    bpy.types.WindowManager.display_mouse = bpy.props.BoolProperty(
        name="Mouse",
        description="Display mouse events",
        default=False)
    bpy.types.WindowManager.display_font_size = bpy.props.IntProperty(
        name="Size",
        description="Fontsize",
        default=20)
    bpy.types.WindowManager.display_pos_x = bpy.props.IntProperty(
        name="Pos X",
        description="Position of the font in x axis",
        default=15)
    bpy.types.WindowManager.display_pos_y = bpy.props.IntProperty(
        name="Pos Y",
        description="Position of the font in y axis",
        default=60)
    bpy.types.WindowManager.display_color = bpy.props.FloatVectorProperty(
        name="Colour",
        description="Font colour",
        default=(1.0, 1.0, 1.0),
        min=0,
        max=1,
        subtype='COLOR')


# removal of properties when script is disabled
def clear_properties():
    props = ["display_keys", "display_mouse", "display_font_size",
     "display_pos_x", "display_pos_y"]
    for p in props:
        if bpy.context.window_manager.get(p) != None:
            del bpy.context.window_manager[p]
        try:
            x = getattr(bpy.types.WindowManager, p)
            del x
        except:
            pass


# defining the panel
class OBJECT_PT_keys_status(bpy.types.Panel):
    bl_label = "Display Keys Status"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        col = self.layout.column(align=False)
        if not context.window_manager.display_keys:
            col.operator("view3d.screencast_keys", text="Start display",
                icon='PLAY')
        else:
            col.operator("view3d.screencast_keys", text="Stop display",
                icon='PAUSE')
        
        col = self.layout.column(align=True)
        row = col.row(align=True)
        row.prop(context.window_manager, "display_pos_x")
        row.prop(context.window_manager, "display_pos_y")
        row = col.row(align=True)
        row.prop(context.window_manager, "display_font_size")
        row.prop(context.window_manager, "display_mouse")
        
        row = self.layout.row()
        row.prop(context.window_manager, "display_color")


classes = [ScreencastKeysStatus,
    OBJECT_PT_keys_status]


def register():
    init_properties()
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    clear_properties()


if __name__ == "__main__":
    register()