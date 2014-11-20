# ##### BEGIN GPL LICENSE BLOCK #####

# Blendermada client.
# Add-on for Blender 3D to access content from http://blendermada.com
# Copyright (C) 2014  Sergey Ozerov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>


bl_info = {
    "name": "Blendermada Client",
    "author": "Sergey Ozerov, <ozzyrov@gmail.com>",
    "version": (0, 9, 1),
    "blender": (2, 70, 0),
    "location": "Properties > Material > Blendermada Client",
    "description": "Browse and download materials from online CC0 database.",
    "warning": "Beta version",
    "wiki_url": "http://blendermada.com/addon.html",
    "tracker_url": "https://github.com/TrueCryer/blendermada",
    "category": "Material",
}


import bpy
import bgl
from bpy.props import *


from urllib import request, parse
import json
import os
import pickle
import time
from datetime import datetime


ENGINE_MAPPING = {
    'BLENDER_RENDER': 'int',
    'BLENDER_GAME': 'int',
    'CYCLES': 'cyc',
}


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
        now = time.mktime(datetime.now().timetuple())
        filetime = os.path.getmtime(filepath)
        if now - filetime < seconds_to_live:
            return False
    return True


###############################################
###############################################


def get_engine():
    engine = bpy.context.scene.render.engine
    try:
        return ENGINE_MAPPING[engine]
    except:
        return ''


def bmd_urlopen(url, **kwargs):
    full_url = parse.urljoin('http://blendermada.com/', url)
    params = parse.urlencode(kwargs)
    return request.urlopen('%s?%s' % (full_url, params))


def get_image(url):
    filepath = os.path.join(get_cache_path(), 'images')
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    filepath = os.path.join(filepath, url.split('/')[-1])
    if file_expired(filepath, 300):
        r = bmd_urlopen(url)
        with open(filepath, 'wb+') as f:
            f.write(r.read())
    return filepath


def get_library(url):
    filepath = os.path.join(get_cache_path(), 'files')
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    filepath = os.path.join(filepath, url.split('/')[-1])
    if file_expired(filepath, 300):
        r = bmd_urlopen(url)
        with open(filepath, 'wb+') as f:
            f.write(r.read())
    return filepath


###############################################
###############################################


class BlendermadaClient(object):

    def __init__(self):
        self.materials = list()
        self.categories = [{'id': 0, 'slug': 'all', 'name': 'All'}]

    def update(self):
        engine = get_engine()
        r = bmd_urlopen('/api/materials/full.json', engine=engine)
        data = json.loads(str(r.read(), 'UTF-8'))
        self.materials = data['materials']
        self.materials.sort(key=lambda x: x['name'])
        self.categories = data['categories']
        self.categories.sort(key=lambda x: x['id'])
        self.categories.insert(0, {'id': 0, 'slug': 'all', 'name': 'All'})
        bpy.context.scene.bmd_category_active = 'All'

    def get_categories(self):
        return self.categories.copy()

    def get_materials(self, category='All'):
        if category == 'All':
            return self.materials.copy()
        else:
            return [
                mat for mat in self.materials if mat['category'] == category
            ]

    def get_material_detail(self, id):
        return [mat for mat in self.materials if mat['id'] == id][0]


bmd_client = BlendermadaClient()


###############################################
###############################################


class Preview(object):

    def __init__(self):
        self.activated = False
        self.x = 10
        self.y = 10
        self.width = 256
        self.height = 256
        self.move = False
        self.glImage = None
        self.bindcode = None

    def load_image(self, image_url):
        self.glImage = bpy.data.images.load(get_image(image_url))
        self.glImage.gl_load(bgl.GL_NEAREST, bgl.GL_NEAREST)
        self.bindcode = self.glImage.bindcode

    def unload_image(self):
        if self.glImage is not None:
            self.glImage.gl_free()
            self.glImage.user_clear()
            bpy.data.images.remove(self.glImage)
        self.glImage = None
        self.bindcode = None

    def activate(self, context):
        self.load_image(context.scene.bmd_material_active.image_url)
        self.handler = bpy.types.SpaceProperties.draw_handler_add(
                                   render_callback,
                                   (self, context), 'WINDOW', 'POST_PIXEL')
        bpy.context.scene.cursor_location.x += 0.0  # refresh display
        self.activated = True

    def deactivate(self, context):
        self.unload_image()
        bpy.types.SpaceProperties.draw_handler_remove(self.handler, 'WINDOW')
        bpy.context.scene.cursor_location.x += 0.0  # refresh display
        self.activated = False

    def event_callback(self, context, event):
        if not self.activated:
            return {'FINISHED'}
        if event.type == 'MIDDLEMOUSE':
            if event.value == 'PRESS':
                self.move = True
                return {'RUNNING_MODAL'}
            elif event.value == 'RELEASE':
                self.move = False
                return {'RUNNING_MODAL'}
        if event.type in ('LEFTMOUSE', 'RIGHTMOUSE'):
            self.deactivate(context)
            return {'FINISHED'}
        if self.move and event.type == 'MOUSEMOVE':
            self.x += event.mouse_x - event.mouse_prev_x
            self.y += event.mouse_y - event.mouse_prev_y
            bpy.context.scene.cursor_location.x += 0.0  # refresh display
            return {'RUNNING_MODAL'}
        else:
            return {'PASS_THROUGH'}


preview = Preview()


def render_callback(self, context):
    if self.bindcode is not None:
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D,
                            bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D,
                            bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.bindcode)
        bgl.glEnable(bgl.GL_TEXTURE_2D)
        bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
        bgl.glBegin(bgl.GL_QUADS)
        bgl.glTexCoord2f(0.0, 0.0)
        bgl.glVertex2f(self.x, self.y)
        bgl.glTexCoord2f(1.0, 0.0)
        bgl.glVertex2f(self.x + self.width, self.y)
        bgl.glTexCoord2f(1.0, 1.0)
        bgl.glVertex2f(self.x + self.width, self.y + self.height)
        bgl.glTexCoord2f(0.0, 1.0)
        bgl.glVertex2f(self.x, self.y + self.height)
        bgl.glEnd()
        bgl.glDisable(bgl.GL_TEXTURE_2D)


###############################################
###############################################


def update_materials(self, context):
    print(self)
    print(dir(self))
    context.scene.bmd_material_list.clear()
    for i in bmd_client.get_materials(category=bpy.context.scene.bmd_category_active):
        a = context.scene.bmd_material_list.add()
        a.id = i['id']
        a.slug = i['slug']
        a.name = i['name']
    if len(context.scene.bmd_material_list) > 0:
        context.scene.bmd_material_list_idx = 0
        update_active_material(None, context)


def update_active_material(self, context):
    mat = bmd_client.get_material_detail(
        context.scene.bmd_material_list[context.scene.bmd_material_list_idx].id,
    )
    context.scene.bmd_material_active.id = mat['id']
    context.scene.bmd_material_active.slug = mat['slug']
    context.scene.bmd_material_active.name = mat['name']
    context.scene.bmd_material_active.description = mat['description']
    context.scene.bmd_material_active.storage_name = mat['storage_name']
    context.scene.bmd_material_active.image_url = mat['image']
    context.scene.bmd_material_active.library_url = mat['storage']


###############################################
###############################################


bpy.types.Scene.bmd_category_active = StringProperty(update=update_materials)


class BMDMaterialListPG(bpy.types.PropertyGroup):
    id = IntProperty()
    slug = StringProperty()
    name = StringProperty()

bpy.utils.register_class(BMDMaterialListPG)
bpy.types.Scene.bmd_material_list = CollectionProperty(type=BMDMaterialListPG)
bpy.types.Scene.bmd_material_list_idx = IntProperty(update=update_active_material)


class BMDMaterialDetailPG(bpy.types.PropertyGroup):
    id = IntProperty()
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


def material_imported(context):
    name = context.scene.bmd_material_active.storage_name
    if name in bpy.data.materials.keys():
        return True
    return False


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
        row = layout.row()
        row.menu('bmd.category_menu', text=context.scene.bmd_category_active)
        row = layout.row()
        col = row.column()
        col.template_list('BMDMaterialList', '', context.scene, 'bmd_material_list', context.scene, 'bmd_material_list_idx', rows=6)
        col = row.column(align=True)
        col.operator('bmd.update', icon="FILE_REFRESH", text="")
        col.separator()
        col.operator('bmd.preview', icon="MATERIAL", text="")
        col.operator('bmd.description', icon="FILE_TEXT", text="")
        col.operator('bmd.import', icon="IMPORT", text="")
        col.separator()
        col.operator('bmd.help', icon="HELP", text="")
        col.operator('bmd.support', icon="SOLO_ON", text="")


class BMDMaterialList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.name)


class BMDCategoryMenu(bpy.types.Menu):
    bl_idname = "bmd.category_menu"
    bl_label = "Categories Menu"
    bl_description = "Choose category"

    def draw(self, context):
        for cat in bmd_client.get_categories():
            self.layout.operator('bmd.category_select', text=cat['name']).id = cat['name']


class BMDCategorySelect(bpy.types.Operator):
    bl_idname = "bmd.category_select"
    bl_label = "Category Changed"

    id = bpy.props.StringProperty()

    def execute(self, context):
        # update_materials(context, self.id)
        context.scene.bmd_category_active = self.id
        return {'FINISHED'}


class BMDImport(bpy.types.Operator):
    bl_idname = "bmd.import"
    bl_label = "Import"
    bl_description = "Import selected material"

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
            if not material_imported(context):  # some error while importing
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
    bl_label = "Update"
    bl_description = "Update material database"

    def execute(self, context):
        bmd_client.update()
        return {'FINISHED'}


class BMDPreview(bpy.types.Operator):
    bl_idname = 'bmd.preview'
    bl_label = "Preview"
    bl_description = "Preview selected material"

    def modal(self, context, event):
        return preview.event_callback(context, event)

    def invoke(self, context, event):
        if not preview.activated:
            preview.activate(context)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            preview.deactivate(context)
            return {'FINISHED'}


class BMDDescription(bpy.types.Operator):
    bl_idname = 'bmd.description'
    bl_label = "Description"
    bl_description = "Show description of selected material"

    def execute(self, context):
        return {'FINISHED'}


class BMDHelp(bpy.types.Operator):
    bl_idname = 'bmd.help'
    bl_label = "Help"
    bl_description = "View online help"

    def execute(self, context):
        bpy.ops.wm.url_open(url="http://blendermada.com/addon.html")
        return {'FINISHED'}


class BMDSupport(bpy.types.Operator):
    bl_idname = 'bmd.support'
    bl_label = "Support"
    bl_description = "Support Blendermada"

    def execute(self, context):
        bpy.ops.wm.url_open(url="http://blendermada.com/support.html")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BMDPanel)
    bpy.utils.register_class(BMDImport)
    bpy.utils.register_class(BMDMaterialList)
    bpy.utils.register_class(BMDCategoryMenu)
    bpy.utils.register_class(BMDCategorySelect)
    bpy.utils.register_class(BMDUpdate)
    bpy.utils.register_class(BMDPreview)
    bpy.utils.register_class(BMDDescription)
    bpy.utils.register_class(BMDHelp)
    bpy.utils.register_class(BMDSupport)


def unregister():
    bpy.utils.unregister_class(BMDPanel)
    bpy.utils.unregister_class(BMDImport)
    bpy.utils.unregister_class(BMDMaterialList)
    bpy.utils.unregister_class(BMDCategoryMenu)
    bpy.utils.unregister_class(BMDCategorySelect)
    bpy.utils.unregister_class(BMDUpdate)
    bpy.utils.unregister_class(BMDPreview)
    bpy.utils.unregister_class(BMDDescription)
    bpy.utils.unregister_class(BMDHelp)
    bpy.utils.unregister_class(BMDSupport)


if __name__ == '__main__':
    register()
