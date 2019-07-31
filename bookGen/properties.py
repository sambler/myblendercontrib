from math import pi, radians
import logging
import time
import functools
import bpy
from bpy.props import FloatProperty, IntProperty, EnumProperty, BoolProperty, FloatVectorProperty, PointerProperty

from .utils import get_bookgen_collection, get_shelf_collection_by_index, get_shelf_parameters
from .shelf import Shelf
from .ui_outline import BookGenShelfOutline
from .ui_preview import BookGenShelfPreview
from .profiling import Profiler

partial = None

def remove_previews(previews):
    for p in previews:
        p.remove()

    bpy.ops.object.book_gen_rebuild()
    return None

class BookGenShelfProperties(bpy.types.PropertyGroup):
    start: FloatVectorProperty(name="start")
    end: FloatVectorProperty(name="end")
    normal: FloatVectorProperty(name="normal")
    id: IntProperty(name="id")

class BookGenProperties(bpy.types.PropertyGroup):
    log = logging.getLogger("bookGen.properties")
    outline = BookGenShelfOutline()
    previews = {}
    f = None

    def update_immediate(self, context):
        time_start = time.time()
        properties = get_bookgen_collection().BookGenProperties

        if properties.auto_rebuild:
            bpy.ops.object.book_gen_rebuild()

        self.log.info("Finished populating shelf in %.4f secs" % (time.time() - time_start))

    

    def update_delayed(self, context):
        global partial
        time_start = time.time()
        parameters = get_shelf_parameters()
        properties = get_bookgen_collection().BookGenProperties

        if not properties.auto_rebuild:
            return


        for shelf_collection in get_bookgen_collection().children:
            shelf_props = shelf_collection.BookGenShelfProperties

            parameters["seed"] += shelf_props.id

            shelf = Shelf(shelf_collection.name, shelf_props.start, shelf_props.end, shelf_props.normal, parameters)
            shelf.clean()
            shelf.fill()

            parameters["seed"] -= shelf_props.id

            if not shelf_props.id in self.previews.keys():
                preview = BookGenShelfPreview()
                self.previews.update({shelf_props.id: preview})
            else:
                preview = self.previews[shelf_props.id]

            preview.update(*shelf.get_geometry(), context)
            

        self.log.info("Finished populating shelf in %.4f secs" % (time.time() - time_start))
        properties = get_bookgen_collection().BookGenProperties
        
        if partial is not None and bpy.app.timers.is_registered(partial):
            bpy.app.timers.unregister(partial)

        partial = functools.partial(remove_previews, self.previews.values())
        bpy.app.timers.register(partial, first_interval=1.0)


    def update_outline_active(self, context):
        properties = get_bookgen_collection().BookGenProperties
        if properties.outline_active and properties.active_shelf != -1:
            shelf_collection = get_shelf_collection_by_index(properties.active_shelf)
            shelf_props = shelf_collection.BookGenShelfProperties
            parameters = get_shelf_parameters(shelf_props.id)
            shelf = Shelf(shelf_collection.name, shelf_props.start, shelf_props.end, shelf_props.normal, parameters)
            shelf.fill()
            self.outline.enable_outline(*shelf.get_geometry(), context)
        else:
            self.outline.disable_outline()

    def update_active_shelf(self, context):
        self.update_outline_active(context)

    # general
    auto_rebuild: BoolProperty(name="auto rebuild", default=True)
    active_shelf: IntProperty(name="active_shelf", update=update_active_shelf)
    outline_active: BoolProperty(name="outline active shelf", default=False, update=update_outline_active)

    #shelf
    scale: FloatProperty(name="scale", min=0.1, default=1,  update=update_delayed)

    seed: IntProperty(name="seed", default=0, update=update_delayed)

    alignment:  EnumProperty(name="alignment", items=(("0", "fore edge", "align books at the fore edge"), (
        "1", "spine", "align books at the spine"), ("2", "center", "align at center")), update=update_immediate)

    lean_amount:  FloatProperty(
        name="lean amount", subtype="FACTOR", min=.0, soft_max=1.0, update=update_delayed)

    lean_direction: FloatProperty(
        name="lean direction", subtype="FACTOR", min=-1, max=1, default=0, update=update_delayed)

    lean_angle: FloatProperty(
        name="lean angle", unit='ROTATION', min=.0, soft_max=radians(30), max=pi / 2.0, default=radians(8), update=update_delayed)
    rndm_lean_angle_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update_delayed)

    book_height: FloatProperty(
        name="height", default=0.15, min=.05, step=0.005, unit="LENGTH", update=update_delayed)
    rndm_book_height_factor: FloatProperty(
        name=" random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update_delayed)

    book_width: FloatProperty(
        name="width", default=0.03, min=.002, step=0.001, unit="LENGTH", update=update_delayed)
    rndm_book_width_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update_delayed)

    book_depth: FloatProperty(
        name="depth", default=0.12, min=.0, step=0.005, unit="LENGTH", update=update_delayed)
    rndm_book_depth_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update_delayed)

    cover_thickness: FloatProperty(
        name="cover thickness", default=0.002, min=.0, step=.02, unit="LENGTH", update=update_delayed) # TODO hinge_inset_guard
    rndm_cover_thickness_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update_delayed)

    textblock_offset: FloatProperty(
        name="textblock offset", default=0.005, min=.0, step=.001, unit="LENGTH", update=update_delayed)
    rndm_textblock_offset_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update_delayed)

    spine_curl: FloatProperty(
        name="spine curl", default=0.002, step=.002, min=.0, unit="LENGTH", update=update_delayed)
    rndm_spine_curl_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update_delayed)

    hinge_inset: FloatProperty(
        name="hinge inset", default=0.001, min=.0, step=.0001, unit="LENGTH", update=update_delayed) #TODO hinge inset guard
    rndm_hinge_inset_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update_delayed)

    hinge_width: FloatProperty(
        name="hinge width", default=0.004, min=.0, step=.05, unit="LENGTH", update=update_delayed)
    rndm_hinge_width_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update_delayed)

    subsurf: BoolProperty(
        name="Add Subsurf-Modifier", default=False, update=update_immediate)


    material: PointerProperty(name="Material", type=bpy.types.Material, update=update_immediate)
