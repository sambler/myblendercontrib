import bpy

from ..functions import store_ui_data
from ..functions import draw_callback_px
from ..functions import select_bone


class StoreUIData(bpy.types.Operator):
    bl_label = "Store UI Data"
    bl_idname = "rigui.store_ui_data"
    #bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        canevas=None
        objects = bpy.context.selected_objects
        rig = bpy.context.object

        for ob in objects :
            if ob.name.endswith('canevas.display') :
                canevas = ob

        if rig.type == 'ARMATURE' and canevas:
            objects.remove(rig)
            store_ui_data(objects,canevas,rig)

        else :
            self.report({'INFO'},'active object not rig or canevas not found')

        return {'FINISHED'}

class UIDraw(bpy.types.Operator):
    bl_idname = "rigui.ui_draw"
    bl_label = "Rig UI Draw"


    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            self.mouse = (event.mouse_region_x, event.mouse_region_y)

        elif event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
            select_bone((event.mouse_region_x, event.mouse_region_y))

            #bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            #return {'FINISHED'}

        elif event.type in {'ESC',}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            adress = context.space_data.as_pointer()
            #context.window_manager.modal_handler_add(self)
            args = (self, context,adress)

            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'

            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            self.mouse = (0,0)

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
