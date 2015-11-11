# bc_scene_utils.py
import bpy
import bmesh
import os


def enumerate_objects_starting_with(find_term):
    return (c for c in bpy.data.objects if c.name.startswith(find_term))


def select_starting(find_term):
    objs = enumerate_objects_starting_with(find_term)
    for o in objs:
        o.select = True


def select_starting2(find_term, type_object):

    shortname = {
        # easy to extend..
        'CU': 'CURVE',
        'M': 'MESH'
    }.get(type_object)

    if shortname:
        type_object = shortname

    objs = enumerate_objects_starting_with(find_term)
    for o in objs:
        if not o.type == type_object:
            continue
        o.select = True


def distance_check():
    obj = bpy.context.edit_object
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)

    verts = [v.co for v in bm.verts if v.select]
    if not len(verts) == 2:
        return 'select 2 only'
    else:
        dist = (verts[0] - verts[1]).length
        return str(dist)


def align_view_to_3dcursor():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            ctx = bpy.context.copy()
            ctx['area'] = area
            ctx['region'] = area.regions[-1]
            bpy.ops.view3d.view_center_cursor(ctx)


def parent_selected_to_new_empty():
    context = bpy.context
    scene = context.scene
    objects = bpy.data.objects

    selected_objects = context.selected_objects.copy()

    if not selected_objects:
        return

    mt = objects.new('parent_empty', None)
    scene.objects.link(mt)

    for o in selected_objects:
        o.parent = mt

    return mt


def add_mesh_2_json(kind):
    temp_root = os.path.dirname(__file__)

    file_by_name = {
        'zup': 'mesh2json.py',
        'yup': 'mesh2json2.py'
    }.get(kind)

    fp = os.path.join(temp_root, 'fast_ops', file_by_name)
    with open(fp) as ofile:
        fullstr = ''.join(ofile)
        nf = bpy.data.texts.new(file_by_name)
        nf.from_string(fullstr)
