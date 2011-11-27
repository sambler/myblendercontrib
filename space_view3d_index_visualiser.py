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
    'name': 'Index Visualiser',
    'author': 'Bartius Crouch',
    'version': (2, 6, 12),
    'blender': (2, 6, 0),
    'api': 42181,
    'location': 'View3D > Properties panel > Mesh Display tab',
    'warning': '', # used for warning icon and text in addons panel
    'description': 'Display the indices of vertices, edges and faces '\
        'in the 3d-view',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/'\
        'Scripts/3D_interaction/Index_Visualiser',
    'tracker_url': 'http://projects.blender.org/tracker/index.php?'\
        'func=detail&aid=21557',
    'category': '3D View'}


"""
Display the indices of vertices, edges and faces in the 3d-view.

How to use:
- Select a mesh and go into editmode
- Display the properties panel (N-key)
- Go to the Mesh Display tab, it helps to fold the tabs above it
- Press the 'Visualise indices button'

"""

import bgl
import blf
import bpy
import mathutils


# calculate locations and store them as ID property in the mesh
def calc_callback(self, context):
    # polling
    if context.mode != "EDIT_MESH":
        return
    
    # get screen information
    mid_x = context.region.width/2.0
    mid_y = context.region.height/2.0
    width = context.region.width
    height = context.region.height
    
    # get matrices
    view_mat = context.space_data.region_3d.perspective_matrix
    ob_mat = context.active_object.matrix_world
    total_mat = view_mat * ob_mat
    
    # calculate location info
    texts = []
    locs = []
    me = context.active_object.data
    if bpy.context.scene.live_mode:
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
    if bpy.context.scene.display_vert_index:
        for v in me.vertices:
            if not v.hide and \
            (v.select or not bpy.context.scene.display_sel_only):
                locs.append([1.0, 1.0, 1.0, v.index, v.co.to_4d()])
    if bpy.context.scene.display_edge_index:
        for ed in me.edges:
            if not ed.hide and \
            (ed.select or not bpy.context.scene.display_sel_only):
                v1, v2 = ed.vertices
                v1 = me.vertices[v1].co.copy()
                v2 = me.vertices[v2].co.copy()
                loc = v1 + ((v2-v1)/2.0)
                locs.append([1.0, 1.0, 0.0, ed.index, loc.to_4d()])
    if bpy.context.scene.display_face_index:
        for f in me.faces:
            if not f.hide and \
            (f.select or not bpy.context.scene.display_sel_only):
                locs.append([1.0, 0.0, 0.5, f.index, f.center.to_4d()])
                
    for loc in locs:
        vec = total_mat * loc[4] # order is important
        # dehomogenise
        vec = mathutils.Vector((vec[0]/vec[3],vec[1]/vec[3],vec[2]/vec[3]))
        x = int(mid_x + vec[0]*width/2.0)
        y = int(mid_y + vec[1]*height/2.0)
        texts+=[loc[0], loc[1], loc[2], loc[3], x, y, 0]

    # store as ID property in mesh
    context.scene["IndexVisualiser"] = texts


# draw in 3d-view
def draw_callback(self, context):
    # polling
    if context.mode != "EDIT_MESH":
        return
    # retrieving ID property data
    try:
        texts = context.scene["IndexVisualiser"]
    except:
        return
    if not texts:
        return
    
    # draw
    blf.size(0, 13, 72)
    for i in range(0,len(texts),7):
        bgl.glColor3f(texts[i], texts[i+1], texts[i+2])
        blf.position(0, texts[i+4], texts[i+5], texts[i+6])
        blf.draw(0, str(int(texts[i+3])))


# operator
class IndexVisualiser(bpy.types.Operator):
    bl_idname = "view3d.index_visualiser"
    bl_label = "Index Visualiser"
    bl_description = "Toggle the visualisation of indices"
    
    @classmethod
    def poll(cls, context):
        return context.mode=="EDIT_MESH"
    
    def __del__(self):
        bpy.context.scene.display_indices = -1
        clear_properties(full=False)
    
    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        # removal of callbacks when operator is called again
        if context.scene.display_indices == -1:
            context.region.callback_remove(self.handle1)
            context.region.callback_remove(self.handle2)
            context.scene.display_indices = 0
            return {"CANCELLED"}
        
        return {"PASS_THROUGH"}
    
    def invoke(self, context, event):
        if context.area.type == "VIEW_3D":
            if context.scene.display_indices < 1:
                # operator is called for the first time, start everything
                context.scene.display_indices = 1
                context.window_manager.modal_handler_add(self)
                self.handle1 = context.region.callback_add(calc_callback,
                    (self, context), "POST_VIEW")
                self.handle2 = context.region.callback_add(draw_callback,
                    (self, context), "POST_PIXEL")
                return {"RUNNING_MODAL"}
            else:
                # operator is called again, stop displaying
                context.scene.display_indices = -1
                clear_properties(full=False)
                return {'RUNNING_MODAL'}
        else:
            self.report({"WARNING"}, "View3D not found, can't run operator")
            return {"CANCELLED"}


# properties used by the script
class InitProperties(bpy.types.Operator):
    bl_idname = "view3d.init_index_visualiser"
    bl_label = "init properties for index visualiser"
    
    def execute(self, context):
        bpy.types.Scene.display_indices = bpy.props.IntProperty(
            name="Display indices",
            default=0)
        context.scene.display_indices = 0
        bpy.types.Scene.display_sel_only = bpy.props.BoolProperty(
            name="Selected only",
            description="Only display indices of selected vertices/edges/faces",
            default=True)
        bpy.types.Scene.display_vert_index = bpy.props.BoolProperty(
            name="Vertices",
            description="Display vertex indices", default=True)
        bpy.types.Scene.display_edge_index = bpy.props.BoolProperty(
            name="Edges",
            description="Display edge indices")
        bpy.types.Scene.display_face_index = bpy.props.BoolProperty(
            name="Faces",
            description="Display face indices")
        bpy.types.Scene.live_mode = bpy.props.BoolProperty(
            name="Live",
            description="Toggle live update of the selection, can be slow",
            default=False)
        return {'FINISHED'}


# removal of ID-properties when script is disabled
def clear_properties(full=True):
    # can happen on reload
    if bpy.context.scene is None:
        return
    
    if "IndexVisualiser" in bpy.context.scene.keys():
        del bpy.context.scene["IndexVisualiser"]
    if full:
        props = ["display_indices", "display_sel_only", "display_vert_index",
        "display_edge_index", "display_face_index", "live_mode"]
        for p in props:
            if p in bpy.types.Scene.bl_rna.properties:
                exec("del bpy.types.Scene."+p)
            if p in bpy.context.scene.keys():
                del bpy.context.scene[p]


# defining the panel
def menu_func(self, context):
    self.layout.separator()
    col = self.layout.column(align=True)
    col.operator(IndexVisualiser.bl_idname, text="Visualise indices")
    row = col.row(align=True)
    row.active = (context.mode=="EDIT_MESH" and \
        context.scene.display_indices==1)
    row.prop(context.scene, "display_vert_index", toggle=True)
    row.prop(context.scene, "display_edge_index", toggle=True)
    row.prop(context.scene, "display_face_index", toggle=True)
    row = col.row(align=True)
    row.active = (context.mode=="EDIT_MESH" and \
        context.scene.display_indices==1)
    row.prop(context.scene, "display_sel_only")
    row.prop(context.scene, "live_mode", toggle=False)


def register():
    bpy.utils.register_class(IndexVisualiser)
    bpy.utils.register_class(InitProperties)
    bpy.ops.view3d.init_index_visualiser()
    bpy.types.VIEW3D_PT_view3d_meshdisplay.append(menu_func)


def unregister():
    bpy.utils.unregister_class(IndexVisualiser)
    bpy.utils.unregister_class(InitProperties)
    clear_properties()
    bpy.types.VIEW3D_PT_view3d_meshdisplay.remove(menu_func)


if __name__ == "__main__":
    register()
