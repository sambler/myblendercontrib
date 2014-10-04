bl_info = {
    "name": "Blendermada Client",
    "author": "Sergey Ozerov, <ozzyrov@gmail.com>",
    "version": (0, 1, 2),
    "blender": (2, 70, 0),
    "location": "Properties > Material > Blendermada Client",
    "description": "Browse and download materials from online CC0 database.",
    "warning": "Alpha version",
    "wiki_url": "http://blendermada.com/addon.html",
    "tracker_url": "https://github.com/TrueCryer/blendermada",
    "category": "Material",
}


import bpy
from bpy.props import *

from urllib import request
import json
import os
import pickle
import time
from datetime import datetime


ENGINE_MAPPING = {
    'BLENDER_RENDER': 'internal',
    'BLENDER_GAME': 'internal',
    'CYCLES': 'cycles',
}


###############################################
###############################################
###############################################


def get_cache_path():
    path = os.path.join('~', '.blendermada')
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        os.mkdir(path)
    path = os.path.join(path, 'cache')
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def dump_data(data, filepath):
    with open(filepath, 'wb+') as f:
        pickle.dump(data, f)

def load_data(filepath):
    with open(filepath, 'rb+') as f:
        data = pickle.load(f)
    return data

def file_expired(filepath, seconds_to_live):
    if os.path.exists(filepath):
        if time.mktime(datetime.now().timetuple()) - os.path.getmtime(filepath) < seconds_to_live:
            return False
    return True


###############################################
###############################################
###############################################


def get_engine():
    engine = bpy.context.scene.render.engine
    try:
        return ENGINE_MAPPING[engine]
    except:
        return ''

def get_materials(category):
    engine = get_engine()
    filepath = os.path.join(get_cache_path(), '%s-cat-%s' % (engine, category))
    if file_expired(filepath, 300):
        r = request.urlopen('http://blendermada.com/api/materials/category/%s.json' % (category,))
        ans = json.loads(str(r.read(), 'UTF-8'))
        dump_data(ans, filepath)
    return load_data(filepath)

def get_categories():
    filepath = os.path.join(get_cache_path(), 'categories')
    if file_expired(filepath, 300):
        r = request.urlopen('http://blendermada.com/api/materials/index.json')
        ans = json.loads(str(r.read(), 'UTF-8'))
        dump_data(ans, filepath)
    return load_data(filepath)

def get_material_detail(pk, slug):
    filepath = os.path.join(get_cache_path(), 'mat-%s-%s' % (pk, slug))
    if file_expired(filepath, 300):
        r = request.urlopen('http://blendermada.com/api/materials/material/%s-%s.json' % (pk, slug))
        ans = json.loads(str(r.read(), 'UTF-8'))
        dump_data(ans, filepath)
    return load_data(filepath)

def get_image(url):
    filepath = os.path.join(get_cache_path(), 'images')
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    filepath = os.path.join(filepath, url.split('/')[-1])
    if file_expired(filepath, 300):
        r = request.urlopen(url)
        with open(filepath, 'wb+') as f:
            f.write(r.read())
    return filepath

def get_library(url):
    filepath = os.path.join(get_cache_path(), 'files')
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    filepath = os.path.join(filepath, url.split('/')[-1])
    if file_expired(filepath, 300):
        r = request.urlopen(url)
        with open(filepath, 'wb+') as f:
            f.write(r.read())
    return filepath


###############################################
###############################################
###############################################


def update_categories(context):
    context.scene.bmd_category_list.clear()
    for i in get_categories():
        a = context.scene.bmd_category_list.add()
        a.slug = i['slug']
        a.name = i['name']
    update_materials(None, context)

def update_materials(self, context):
    context.scene.bmd_material_list.clear()
    for i in get_materials(category=context.scene.bmd_category_list[context.scene.bmd_category_list_idx].slug):
        a = context.scene.bmd_material_list.add()
        a.pk = i['pk']
        a.slug = i['slug']
        a.name = i['name']
    context.scene.bmd_material_list_idx = 0
    update_active_material(self, context)

def update_active_material(self, context):
    mat = get_material_detail(
        context.scene.bmd_material_list[context.scene.bmd_material_list_idx].pk,
        context.scene.bmd_material_list[context.scene.bmd_material_list_idx].slug,
    )
    context.scene.bmd_material_active.pk = mat['pk']
    context.scene.bmd_material_active.slug = mat['slug']
    context.scene.bmd_material_active.name = mat['name']
    context.scene.bmd_material_active.description = mat['description']
    context.scene.bmd_material_active.storage_name = mat['storage_name']
    context.scene.bmd_material_active.image_url = 'http://blendermada.com' + mat['image']
    context.scene.bmd_material_active.library_url = 'http://blendermada.com' + mat['storage']


###############################################
###############################################
###############################################


class BMDCategoryPG(bpy.types.PropertyGroup):
    slug = StringProperty()
    name = StringProperty()

bpy.utils.register_class(BMDCategoryPG)
bpy.types.Scene.bmd_category_list = CollectionProperty(type=BMDCategoryPG)
bpy.types.Scene.bmd_category_list_idx = IntProperty(update=update_materials)
bpy.types.Scene.bmd_category_active = PointerProperty(type=BMDCategoryPG)


class BMDMaterialListPG(bpy.types.PropertyGroup):
    pk   = IntProperty()
    slug = StringProperty()
    name = StringProperty()

bpy.utils.register_class(BMDMaterialListPG)
bpy.types.Scene.bmd_material_list = CollectionProperty(type=BMDMaterialListPG)
bpy.types.Scene.bmd_material_list_idx = IntProperty(update=update_active_material)


class BMDMaterialDetailPG(bpy.types.PropertyGroup):
    pk   = IntProperty()
    slug = StringProperty()
    name = StringProperty()
    description = StringProperty()
    storage_name = StringProperty()
    image_url = StringProperty()
    library_url = StringProperty()

bpy.utils.register_class(BMDMaterialDetailPG)
bpy.types.Scene.bmd_material_active = PointerProperty(type=BMDMaterialDetailPG)


###############################################
###############################################
###############################################


def material_imported(context):
    name = context.scene.bmd_material_active.storage_name
    if name in bpy.data.materials.keys():
        return True
    return False


###############################################
###############################################
###############################################


class BMDPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Blendermada Client"
    bl_idname = "BlendermadaClientPanel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        layout.operator('bmd.update')
        layout.label('Category')
        layout.template_list('BMDCategoryList', '', context.scene, 'bmd_category_list', context.scene, 'bmd_category_list_idx', rows=3)
        layout.label('Material')
        layout.template_list('BMDMaterialList', '', context.scene, 'bmd_material_list', context.scene, 'bmd_material_list_idx', rows=7)
        layout.label('Material Detail')
        layout.label(context.scene.bmd_material_active.name)
        layout.label(context.scene.bmd_material_active.description)
        layout.operator('bmd.import')


class BMDMaterialList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.name)


class BMDCategoryList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.name)


class BMDImport(bpy.types.Operator):
    bl_idname = "bmd.import"
    bl_label = "Import"

    def execute(self, context):
        if material_imported(context):
            self.report(
                {'WARNING'},
                'Material with name \'%s\' already exists here. Please, rename it to import new one.' % (
                    context.scene.bmd_material_active.storage_name,
                )
            )
            return {'CANCELLED'}
        else:
            storage = get_library(context.scene.bmd_material_active.library_url)
            directory = '%s/Material/' % (storage,)
            filename = context.scene.bmd_material_active.storage_name
            if bpy.app.version < (2, 72):
                bpy.ops.wm.link_append(
                    filepath=('%s%s' % (directory, filename)),
                    directory=directory,
                    filename=filename,
                    relative_path=True,
                    link=False,
                )
            else:
                bpy.ops.wm.append(
                    filepath=('%s%s' % (directory, filename)),
                    directory=directory,
                    filename=filename,
                )
            if not material_imported(context): # some error while importing
                self.report(
                    {'WARNING'},
                    'Material cannot be imported. Maybe library has been damaged. Please, report about it to Blendermada administrator.',
                )
                return {'CANCELLED'}
            else:
                ao = bpy.context.active_object
                ao.material_slots[ao.active_material_index].material = bpy.data.materials[context.scene.bmd_material_active.storage_name]
                self.report({'INFO'}, 'Material was imported succesfully.')
                return {'FINISHED'}


class BMDUpdate(bpy.types.Operator):
    bl_idname = 'bmd.update'
    bl_label = 'Update'
    def execute(self, context):
        update_categories(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BMDPanel)
    bpy.utils.register_class(BMDImport)
    bpy.utils.register_class(BMDMaterialList)
    bpy.utils.register_class(BMDCategoryList)
    bpy.utils.register_class(BMDUpdate)


def unregister():
    bpy.utils.unregister_class(BMDPanel)
    bpy.utils.unregister_class(BMDImport)
    bpy.utils.unregister_class(BMDMaterialList)
    bpy.utils.unregister_class(BMDCategoryList)
    bpy.utils.unregister_class(BMDUpdate)


if __name__ == '__main__':
    register()
