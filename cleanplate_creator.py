bl_info = {
"name": "Cleanplate creator",
"author": "Sebastian Koenig",
"version": (1, 0),
"blender": (2, 7, 2),
"location": "",
"description": "",
"warning": "",
"wiki_url": "",
"tracker_url": "",
"category": "Textures"}

import bpy

'''
2 opertators
1. first extract the texture by baking to cleanplate
2. then prepare for painting

1.1: Prepare the UVs and mesh
1.2: Create material with clip as image for projection with projection Uv uv_layer
1.3: make UVMap active
1.4: Create the cleanplate image
1.5: bake

2.1: Check if uvs exist. if not, create and prepare mesh
2.2: Check if cleanplate image exists. if not, create. create material with cleanplate as input
2.3: make UVMap active
2.4: Prepare painting

3. Save image in UI


'''
def cleanplate_preparator(context, ob, size, canvas, clip):
    # prepare the object as cleanplate
    me = ob.data

    # make sure the plane is subdivided enough
    if len(me.vertices)<81:
        if not context.object.mode=="EDIT":
           bpy.ops.object.mode_set(mode="EDIT")
           bpy.ops.mesh.subdivide(number_cuts=32, smoothness=0)
           bpy.ops.uv.smart_project()
           bpy.ops.object.mode_set(mode="OBJECT")

    # make sure we have something to paint on
    if len(list(me.uv_textures)) > 0:
        if not me.uv_textures.get("projection"):
            me.uv_textures.new(name="projection")
    else:
        me.uv_textures.new(name="UVMap")
        me.uv_textures.new(name="projection")

    print(canvas)
    #get active uvlayer
    for t in  me.uv_textures:
        if t.active:
            uvtex = t.data
            for f in me.polygons:
                #check that material had an image!
                uvtex[f.index].image = canvas

    me.update()

    # create the project modifier
    projector = ob.modifiers.new(name="UVProject", type="UV_PROJECT")
    projector.uv_layer = "projection"
    projector.aspect_x=clip.size[0]
    projector.aspect_y=clip.size[1]
    projector.projectors[0].object = bpy.data.objects["Camera"]
    projector.uv_layer="projection"




def set_cleanplate_brush(context, clip, canvas):

    paint_settings = bpy.context.tool_settings.image_paint
    ps = paint_settings
    ps.brush=bpy.data.brushes['Clone']
    ps.brush.strength=1
    ps.use_clone_layer=True
    ps.mode="IMAGE"
    ps.canvas=canvas
    ps.clone_image = bpy.data.images[clip.name]
    ps.use_normal_falloff=False
    bpy.context.active_object.data.uv_texture_clone = bpy.data.meshes['Ground'].uv_textures["projection"]


def configure_video_image(context, image, length, start, offset):
    # prepare an image that uses the same parameters as the movievclip

    # !! might not work !!

    image.use_auto_refresh=True
    image.frame_start=1
    image.frame_duration=length
    image.frame_start=start
    image.frame_offset=offset


def change_viewport_background_for_painting(context, clip):
    # prepare the viewport for painting
    # changing from movie to image will make it updates.
    space = context.space_data

    bgpic = None

    for x in space.background_images:
        if x.source == 'MOVIE_CLIP':
            bgpic = x
            path = bgpic.clip.filepath
            length = bgpic.clip.frame_duration
            start = bgpic.clip.frame_start
            offset = bgpic.clip.frame_offset
            if bpy.data.images.get(clip.name):
                clipimage=bpy.data.images[clip.name]
            else:
                clipimage = bpy.data.images.load(path)
            print(clipimage)

            bgpic.show_on_foreground = True
            bgpic.source = "IMAGE"
            bgpic.image=clipimage

            backimg = bgpic.image_user

            configure_video_image(context, backimg, length, start, offset)

def bake_extract_texture(context, ob):
    bpy.context.scene.render.bake_type = 'TEXTURE'
    bpy.ops.object.bake_image()

def set_cleanplate_material_cycles(context, object):
    pass


def set_cleanplate_material_internal(context, ob, clip, clean_name):

    # create projection texture
    proj_tex = "projected_texture"

    if not bpy.data.textures.get(proj_tex):
        tex_proj = bpy.data.textures.new(name=proj_tex, type='IMAGE')
    else:
        tex_proj = bpy.data.textures[proj_tex]

    # create cleaned texture
    if not bpy.data.textures.get(clean_name):
        tex = bpy.data.textures.new(name=clean_name, type='IMAGE')
    else:
        tex = bpy.data.textures[clean_name]

    # create material
    if not bpy.data.materials.get(clean_name):
        mat = bpy.data.materials.new(clean_name)
    else:
        mat = bpy.data.materials[clean_name]

    tex_proj.image=bpy.data.images[clip.name]
    found = False
    for m in mat.texture_slots:
        if m and m.texture == tex_proj:
            found = True
            break
    if not found and mat:
        mtex = mat.texture_slots.add()
        mtex.texture = tex
        mtex.texture_coords = 'UV'
        mtex.uv_layer = 'projection'
        mtex.use_map_color_diffuse = True


    mat.use_shadeless=True
    if not ob.material_slots.get(mat.name):
        ob.data.materials.append(mat)
    else:
        ob.material_slots[0].material = mat




def assemble_cleanplate_setup(context):
    clip = context.scene.active_clip
    cleaned_object = context.active_object

    clean_name = "cleanplate"

    # extract texture: bake internal and use as paint image

    # create a canvas to paint and bake on
    if not bpy.data.images.get(clean_name):
        canvas = bpy.data.images.new(clean_name, size, size)
    else:
        canvas=bpy.data.images[clean_name]


    # create BI material
    # create BI texture
    # create cycles material
    # create renderlayer setup
    # set background image to image
    # set texture paint setup
    cleanplate_preparator(context, cleaned_object, 2048, canvas, clip)

    change_viewport_background_for_painting(context, clip)

    set_cleanplate_brush(context,clip, canvas)

    set_cleanplate_material_internal(context, cleaned_object, clip, clean_name)

    bake_extract_texture(context, cleaned_object)


    context.space_data.viewport_shade="SOLID"

    if not context.object.mode=="TEXTURE_PAINT":
        bpy.ops.object.mode_set(mode="TEXTURE_PAINT")




################ CLASSES ##########################

class VIEW3D_cleanplate_setup(bpy.types.Operator):
    bl_idname="object.cleanplate_setup"
    bl_label="Cleanplate Creator"

    def execute(self, context):

        assemble_cleanplate_setup(context)
        return{"FINISHED"}




########## REGISTER ############

def register():
    bpy.utils.register_class(VIEW3D_cleanplate_setup)



def unregister():

    bpy.utils.unregister_class(VIEW3D_cleanplate_setup)

if __name__ == "__main__":
    register()
    #bpy.ops.wm.call_menu_pie(name="mesh.mesh_operators")
