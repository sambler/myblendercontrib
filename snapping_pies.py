bl_info = {
    "name": "Snapping Pies",
    "author": "Sebastian Koenig",
    "version": (0, 1),
    "blender": (2, 71, 6),
    "description": "Custom Pie Menus",
    "category": "3D View",}



import bpy
from bpy.types import Menu


###### FUNTIONS ##########

def origin_to_selection(context):
    context = bpy.context

    if context.object.mode == "EDIT":
        saved_location = context.scene.cursor_location.copy()
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        context.scene.cursor_location = saved_location


def origin_to_geometry(context):
    context = bpy.context

    if context.object.mode == "EDIT":
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        bpy.ops.object.mode_set(mode="EDIT")


########### CUSTOM OPERATORS ###############

class VIEW3D_OT_origin_to_selected(bpy.types.Operator):
    bl_idname="object.origin_to_selected"
    bl_label="Origin to Selection"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'VIEW_3D')

    def execute(self, context):
        origin_to_selection(context)
        return {'FINISHED'}


class VIEW3D_OT_origin_to_geometry(bpy.types.Operator):
    bl_idname="object.origin_to_geometry"
    bl_label="Origin to Geometry"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'VIEW_3D')

    def execute(self, context):
        origin_to_geometry(context)
        return {'FINISHED'}


#Menu Snap Target
class VIEW3D_OT_SnapTargetMenu(Menu):
    bl_idname = "snap.targetmenu"
    bl_label = "Snap Target Menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.snaptargetvariable", text="Active").variable='ACTIVE'
        layout.operator("object.snaptargetvariable", text="Median").variable='MEDIAN'
        layout.operator("object.snaptargetvariable", text="Center").variable='CENTER'
        layout.operator("object.snaptargetvariable", text="Closest").variable='CLOSEST'



class VIEW3D_OT_SnapTargetVariable(bpy.types.Operator):
    bl_idname = "object.snaptargetvariable"
    bl_label = "Snap Target Variable"
    variable = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.tool_settings.snap_target=self.variable
        return {'FINISHED'}


#Menu Snap Element
class VIEW3D_OT_SnapElementMenu(Menu):
    bl_idname = "snap.snapelementmenu"
    bl_label = "Snap Element"
    #settings = bpy.context.scene.tool_settings

    def draw(self, context):
        layout = self.layout
        layout.operator("object.snapelementvariable", text="Vertex").variable='VERTEX'
        layout.operator("object.snapelementvariable", text="Edge").variable='EDGE'
        layout.operator("object.snapelementvariable", text="Face").variable='FACE'
        layout.operator("object.snapelementvariable", text="Increment").variable='INCREMENT'
        #layout.operator("object.snapelementvariable", text="Volume").variable='VOLUME'


class VIEW3D_OT_SnapElementVariable(bpy.types.Operator):
    bl_idname = "object.snapelementvariable"
    bl_label = "Snap Element Variable"
    variable = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.tool_settings.snap_element=self.variable
        return {'FINISHED'}


################### PIES #####################

class VIEW3D_PIE_origin(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Origin"
    bl_idname = "object.snapping_pie"

    def draw(self, context):
        context = bpy.context
        layout = self.layout
        tool_settings = context.scene.tool_settings

        pie = layout.menu_pie()

        pie.operator("view3d.snap_selected_to_cursor", icon="CURSOR")
        pie.operator("view3d.snap_cursor_to_selected", icon="CLIPUV_HLT")

        # set origin to selection in Edit Mode, set origin to cursor in Object mode
        if context.object.mode == "EDIT":
            pie.operator("object.origin_to_selected", icon="OUTLINER_OB_EMPTY")
        else:
            pie.operator("object.origin_set",icon="EMPTY_DATA", text="Origin to Cursor").type="ORIGIN_CURSOR"


        #op = pie.operator("wm.context_set_enum", text="Edge Snapping", icon="SNAP_EDGE")
        #op.data_path="tool_settings.snap_element"
        #op.value="EDGE"


        if context.object.mode == "OBJECT":
            pie.operator("object.origin_set",icon="MESH_CUBE", text="Origin to Geometry").type="ORIGIN_GEOMETRY"
        else:
            pie.operator("object.origin_to_geometry", icon="MESH_CUBE")

        pie.operator("view3d.snap_cursor_to_center", icon="CURSOR")


        if tool_settings.snap_element=="VERTEX":
            pie.menu("snap.snapelementmenu", text="Snap Element", icon="SNAP_VERTEX")
        elif tool_settings.snap_element=="EDGE":
            pie.menu("snap.snapelementmenu", text="Snap Element", icon="SNAP_EDGE")
        elif tool_settings.snap_element=="FACE":
            pie.menu("snap.snapelementmenu", text="Snap Element", icon="SNAP_FACE")
        elif tool_settings.snap_element=="VOLUME":
            pie.menu("snap.snapelementmenu", text="Snap Element", icon="SNAP_VOLUME")
        elif tool_settings.snap_element=="INCREMENT":
            pie.menu("snap.snapelementmenu", text="Snap Element", icon="SNAP_INCREMENT")

        if tool_settings.use_snap:
            pie.prop(context.scene.tool_settings, "use_snap", text="Use Snap(ON)")
        else:
            pie.prop(context.scene.tool_settings, "use_snap", text="Use Snap(OFF)")

        pie.menu("snap.targetmenu", text="Snap Target", icon='SNAP_SURFACE')



########## REGISTER ############

def register():
    bpy.utils.register_class(VIEW3D_PIE_origin)
    bpy.utils.register_class(VIEW3D_OT_origin_to_selected)
    bpy.utils.register_class(VIEW3D_OT_origin_to_geometry)
    bpy.utils.register_class(VIEW3D_OT_SnapTargetMenu)
    bpy.utils.register_class(VIEW3D_OT_SnapTargetVariable)
    bpy.utils.register_class(VIEW3D_OT_SnapElementVariable)
    bpy.utils.register_class(VIEW3D_OT_SnapElementMenu)


    wm = bpy.context.window_manager
    

    km = wm.keyconfigs.addon.keymaps.new(name = 'Object Mode')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'S', 'PRESS', shift=True).properties.name = "object.snapping_pie"

    km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'S', 'PRESS',shift=True).properties.name = "object.snapping_pie"




def unregister():

    bpy.utils.unregister_class(VIEW3D_PIE_origin)
    bpy.utils.unregister_class(VIEW3D_OT_origin_to_selected)
    bpy.utils.unregister_class(VIEW3D_OT_origin_to_geometry)
    bpy.utils.unregister_class(VIEW3D_OT_SnapTargetMenu)
    bpy.utils.unregister_class(VIEW3D_OT_SnapTargetVariable)
    bpy.utils.unregister_class(VIEW3D_OT_SnapElementVariable)
    bpy.utils.unregister_class(VIEW3D_OT_SnapElementMenu)


if __name__ == "__main__":
    register()
    #bpy.ops.wm.call_menu_pie(name="mesh.mesh_operators")
