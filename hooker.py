bl_info = {
"name": "Object Track Hooker",
"author": "Sebastian Koenig",
"version": (1, 0),
"blender": (2, 7, 2),
"location": "",
"description": "",
"warning": "",
"wiki_url": "",
"tracker_url": "",
"category": "Movie Tracking"}

import bpy


def get_track_empties(context, tracks):
    # the selected empties are assumed to be the linked tracks
    # these ones will be the parents

    for e in context.selected_objects:
        if e.type=="EMPTY":
            tracks.append(e)
            e.empty_draw_size = 0.05
            e.layers = [False] + [True] + [False] * 18


def create_hook_empties(context, tracks, hooks):
    # create the actual hooks at the same position as the tracks

    for t in tracks:
        # create a new empty, assign name and location
        h = bpy.data.objects.new("CTRL_" + t.name, None)
        h.location = t.matrix_world.to_translation()
        h.empty_draw_size = 0.025
        h.empty_draw_type = "CUBE"

        # link it to the scene
        bpy.context.scene.objects.link(h)

        # add the new empty to the list of parents
        hooks.append(h)

        # make the hook empty a child of the parent
        bpy.ops.object.select_all(action='DESELECT')
        t.select = True
        h.select = True
        bpy.context.scene.objects.active = t
        bpy.ops.object.parent_set()


def get_location(hooks):
    coords=[]
    for h in hooks:
        coords.append(h.location*h.matrix_world)
    return coords


def create_object(context, name, hooks, cleanobject):
    from bpy_extras.io_utils import unpack_list

    # get all locations of the hooks in the list
    coords=get_location(hooks)
    print(coords)

    # create the vertices of the cleanplate mesh
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(coords))
    me.vertices.foreach_set("co", unpack_list(coords))

    # create the object which is using the mesh
    ob = bpy.data.objects.new(name, me)
    ob.location = (0,0,0)

    # link it to the scene and make it active
    bpy.context.scene.objects.link(ob)
    bpy.context.scene.objects.active=ob

    # go into edit mode, select all vertices and create the face
    if not context.object.mode=="EDIT":
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode="OBJECT")

    cleanobject.append(ob)



def hook_em_up(hooks, ob):
    # create an yet unassigned hook modifier for each hook in the list
    modlist=[]
    for h in hooks:
        modname="Hook_" + h.name
        modlist.append(modname)
        mod = ob.modifiers.new(name=modname, type="HOOK")
        mod.object=h

    # now for each vertex go to edit mode, select the vertex and assign the modifier
    verts = ob.data.vertices
    for i in range(len(verts)):
        # Deselect Everything in Edit Mode
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

        ob.data.vertices[i].select=True
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.object.hook_assign(modifier=modlist[i])

    bpy.ops.object.mode_set(mode = 'OBJECT')



class VIEW3D_OT_track_hooker(bpy.types.Operator):
    bl_idname = "object.track_hooker"
    bl_label = "John Lee Hooker"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'VIEW_3D'

    def execute(self, context):
        hooks=[]
        tracks=[]
        cleanobject=[]
        name="canvas"

        get_track_empties(context, tracks)
        create_hook_empties(context, tracks, hooks)

        create_object(context, name, hooks, cleanobject)
        print(cleanobject)

        ob = bpy.data.objects.get(cleanobject[0].name)
        print(ob)
        bpy.context.scene.objects.active = ob

        hook_em_up(hooks, ob)

        return {'FINISHED'}

########## REGISTER ############

def register():
    bpy.utils.register_class(VIEW3D_OT_track_hooker)



def unregister():

    bpy.utils.unregister_class(VIEW3D_OT_track_hooker)

if __name__ == "__main__":
    register()


