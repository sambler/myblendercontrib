bl_info = {
    "name": "Darkfall VFX Nodes",
    "author": "Darkfall",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Window > Scene > Darkfall VFX Nodes",
    "description": "Tools to help speed up your VFX Workflow for thw following tasks." "VFX Eye Color Change." "VFX Scifi Eyes." "Patch Node." "Glitch Effect." "Sketch Effect." "Posterize Effect." "Ink Drop Effect",
        "category": "Nodes",
        "Blog": "http://bit.ly/2kB5XYt"
}

import bpy





    #context for eye color change
def eyecolchange(context):
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    #removes unwanted nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    #set render res to 100
    bpy.context.scene.render.resolution_percentage = 100


        # create a group
    colchange_group = bpy.data.node_groups.new('Col Change Node', 'CompositorNodeTree')



        # create group inputs
    group_inputs = colchange_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-200,400)
    colchange_group.inputs.new('NodeSocketFloat','Eye Mask')
    colchange_group.inputs.new('NodeSocketFloat','Eye Lid Mask')
    colchange_group.inputs.new('NodeSocketFloat','Garbage Mask')
    colchange_group.inputs.new('NodeSocketColor','Movie Clip')
    colchange_group.inputs.new('NodeSocketColor','Eye Color')
    colchange_group.inputs.new('NodeSocketFloatFactor','Eye Brightness')
    colchange_group.inputs.new('NodeSocketFloatFactor','Eyeball Brightness')
    colchange_group.inputs.new('NodeSocketFloat','Eye Feather')
    colchange_group.inputs.new('NodeSocketFloat','Garbage Feather')
    colchange_group.inputs[5].default_value = 1
    colchange_group.inputs[6].default_value = 1
    colchange_group.inputs[4].default_value = (1, 1, 1, 1)
    colchange_group.inputs[3].default_value = (1, 1, 1, 1)
    colchange_group.inputs[1].default_value = 1
    colchange_group.inputs[5].min_value = 0.1
    colchange_group.inputs[6].min_value = 0.1
    colchange_group.inputs[5].max_value = 1
    colchange_group.inputs[6].max_value = 1


        # create group outputs
    group_outputs = colchange_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (2800,400)
    colchange_group.outputs.new('NodeSocketColor','Output')


    #nodes to be added

    eyemath_node = colchange_group.nodes.new('CompositorNodeMath')
    eyemath_node.location = 700,400
    eyemath_node.operation = 'MULTIPLY'
    eyemath_node.use_clamp = True
    eyemath_node.label = "Eye Math"
    eyemath_node.inputs[0].default_value = 1
    eyemath_node.inputs[1].default_value = 0
    eyemath_node.hide = True

    garbmath_node = colchange_group.nodes.new('CompositorNodeMath')
    garbmath_node.location = 900,200
    garbmath_node.operation = 'SUBTRACT'
    garbmath_node.use_clamp = True
    garbmath_node.inputs[0].default_value = 1
    garbmath_node.inputs[1].default_value = 0
    garbmath_node.hide = True

    eyeballmath_node = colchange_group.nodes.new('CompositorNodeMath')
    eyeballmath_node.location = 1150,700
    eyeballmath_node.operation = 'MULTIPLY'
    eyeballmath_node.use_clamp = True
    eyemath_node.inputs[0].default_value = 0
    eyemath_node.inputs[1].default_value = 1
    eyeballmath_node.hide = True


    inv_node = colchange_group.nodes.new(type= 'CompositorNodeInvert')
    inv_node.location = 700,700
    inv_node.hide = True




    mix_node = colchange_group.nodes.new(type= 'CompositorNodeMixRGB')
    mix_node.location = 1400, 200
    mix_node.blend_type = 'SOFT_LIGHT'
    mix_node.use_clamp = True
    mix_node.hide = True



    blur1_node = colchange_group.nodes.new(type= 'CompositorNodeBlur')
    blur1_node.location = 500,700
    blur1_node.size_x = 1
    blur1_node.size_y = 1
    blur1_node.inputs[1].default_value = 0
    blur1_node.label = "Eye Mask Blur"
    blur1_node.hide = True



    #blur2_node = colchange_group.nodes.new(type= 'CompositorNodeBlur')
    #blur2_node.location = 500,500
    #blur2_node.size_x = 1
    #blur2_node.size_y = 1
    #blur2_node.inputs[1].default_value = 0
    #blur2_node.label = "Eyelid Mask Blur"

    blur3_node = colchange_group.nodes.new(type= 'CompositorNodeBlur')
    blur3_node.location = 500,200
    blur3_node.size_x = 1
    blur3_node.size_y = 1
    blur3_node.inputs[1].default_value = 0
    blur3_node.label = "Garbage Mask Blur"
    blur3_node.hide = True



    rgb1_node = colchange_group.nodes.new(type= 'CompositorNodeCurveRGB')
    rgb1_node.location = 1800, 400
    rgb1_node.label = "Eyeball Brightness"
    rgb1_node.hide = True



    rgb2_node = colchange_group.nodes.new(type= 'CompositorNodeCurveRGB')
    rgb2_node.location = 2200, 400
    rgb2_node.label = "Eye Color Brightness"
    rgb2_node.hide = True


    rerout1_node = colchange_group.nodes.new(type= 'NodeReroute')
    rerout1_node.location = 400, 400




        #link nodes together


    colchange_group.links.new(eyemath_node.outputs[0], garbmath_node.inputs[0])

    colchange_group.links.new(garbmath_node.outputs[0], mix_node.inputs[0])

    colchange_group.links.new(blur1_node.outputs[0], eyemath_node.inputs[0])

    colchange_group.links.new(rerout1_node.outputs[0], eyemath_node.inputs[1])

    colchange_group.links.new(rerout1_node.outputs[0], eyeballmath_node.inputs[1])


    colchange_group.links.new(blur3_node.outputs[0], garbmath_node.inputs[1])

    colchange_group.links.new(blur1_node.outputs[0], inv_node.inputs[1])


    colchange_group.links.new(inv_node.outputs[0], eyeballmath_node.inputs[0])

    colchange_group.links.new(mix_node.outputs[0], rgb1_node.inputs[1])

    colchange_group.links.new(eyeballmath_node.outputs[0], rgb1_node.inputs[0])

    colchange_group.links.new(rgb1_node.outputs[0], rgb2_node.inputs[1])

    colchange_group.links.new(garbmath_node.outputs[0], rgb2_node.inputs[0])

    colchange_group.links.new



        # link inputs
    colchange_group.links.new(group_inputs.outputs['Eye Mask'], blur1_node.inputs[0])

    colchange_group.links.new(group_inputs.outputs['Eye Lid Mask'], rerout1_node.inputs[0])
    colchange_group.links.new(group_inputs.outputs['Garbage Mask'], blur3_node.inputs[0])

    colchange_group.links.new(group_inputs.outputs['Movie Clip'], mix_node.inputs[1])

    colchange_group.links.new(group_inputs.outputs['Eye Color'], mix_node.inputs[2])

    colchange_group.links.new(group_inputs.outputs['Eye Brightness'], rgb2_node.inputs[3])

    colchange_group.links.new(group_inputs.outputs['Eyeball Brightness'], rgb1_node.inputs[3])

    colchange_group.links.new(group_inputs.outputs['Eye Feather'], blur1_node.inputs[1])


    colchange_group.links.new(group_inputs.outputs['Garbage Feather'], blur3_node.inputs[1])




        #link output
    colchange_group.links.new(rgb2_node.outputs[0], group_outputs.inputs['Output'])



        #outside group nodes
    mov_node = tree.nodes.new(type= 'CompositorNodeMovieClip')
    mov_node.location = 0,0
    mov_node.select = False

    eyemask_node = tree.nodes.new(type= 'CompositorNodeMask')
    eyemask_node.location = -200,0
    eyemask_node.label = "Eye Mask"
    eyemask_node.select = False

    eyelidmask_node = tree.nodes.new(type= 'CompositorNodeMask')
    eyelidmask_node.location = -200,-110
    eyelidmask_node.label = "Eyelid Mask"
    eyelidmask_node.select = False

    garbmask_node = tree.nodes.new(type= 'CompositorNodeMask')
    garbmask_node.location = -200,-220
    garbmask_node.label = "Garbage Mask"
    garbmask_node.select = False


    comp_node = tree.nodes.new(type= 'CompositorNodeComposite')
    comp_node.location = 900,-200
    comp_node.select = False

    view_node = tree.nodes.new(type= 'CompositorNodeViewer')
    view_node.location = 900,0
    view_node.select = False

    #connections bewteen nodes
    links = tree.links

    link = links.new(mov_node.outputs[0], comp_node.inputs[0])

    link = links.new(mov_node.outputs[0], view_node.inputs[0])
















    #Context for Sci Fi Eye Nodes
def sfe(context):
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    #removes unwanted nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

        #set render res to 100
    bpy.context.scene.render.resolution_percentage = 100



    # create a group
    scifi_group = bpy.data.node_groups.new('Sci fi Eyes Node', 'CompositorNodeTree')



        # create group inputs
    group_inputs = scifi_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-500,400)
    scifi_group.inputs.new('NodeSocketFloat','Eye Lid Mask')
    scifi_group.inputs.new('NodeSocketFloat','Shadow Mask')
    scifi_group.inputs.new('NodeSocketColor','Movie Clip')
    scifi_group.inputs.new('NodeSocketColor','Eye Image')
    scifi_group.inputs.new('NodeSocketFloat','Left Eye: X')
    scifi_group.inputs.new('NodeSocketFloat','Left Eye: Y')
    scifi_group.inputs.new('NodeSocketFloatAngle','Left Eye: Rotation')
    scifi_group.inputs.new('NodeSocketFloat','Left Eye: Scale')
    scifi_group.inputs.new('NodeSocketFloat','Right Eye: X')
    scifi_group.inputs.new('NodeSocketFloat','Right Eye: Y')
    scifi_group.inputs.new('NodeSocketFloatAngle','Right Eye: Rotation')
    scifi_group.inputs.new('NodeSocketFloat','Right Eye: Scale')
    scifi_group.inputs.new('NodeSocketFloatFactor','Eyeball Brightness')
    scifi_group.inputs.new('NodeSocketFloat','Eye Mask Feather')
    scifi_group.inputs.new('NodeSocketFloat','Shadow Feather')
    scifi_group.inputs.new('NodeSocketFloat','Left Eye (Track Pos X)')
    scifi_group.inputs.new('NodeSocketFloat','Left Eye (Track Pos Y)')
    scifi_group.inputs.new('NodeSocketFloat','Right Eye (Track Pos X)')
    scifi_group.inputs.new('NodeSocketFloat','Right Eye (Track Pos Y)')
    scifi_group.inputs[7].default_value = 0.5
    scifi_group.inputs[11].default_value = 0.5
    scifi_group.inputs[8].default_value = 550
    scifi_group.inputs[0].default_value = 1
    scifi_group.inputs[12].min_value = 0.1
    scifi_group.inputs[12].max_value = 1
    scifi_group.inputs[12].default_value = 1





        # create group outputs
    group_outputs = scifi_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (2000,400)
    scifi_group.outputs.new('NodeSocketColor','Output')





        #nodes to be added to group

    rerout1_node = scifi_group.nodes.new(type= 'NodeReroute')
    rerout1_node.location = 0,0

    rerout2_node = scifi_group.nodes.new(type= 'NodeReroute')
    rerout2_node.location = 50,300

    rerout3_node = scifi_group.nodes.new(type= 'NodeReroute')
    rerout3_node.location = 50,500


    transf1_node = scifi_group.nodes.new(type= 'CompositorNodeTransform')
    transf1_node.location = 180,150
    transf1_node.inputs[4].default_value = 0.5
    transf1_node.label = "Left Eye Position"
    transf1_node.hide = True

    blur1_node = scifi_group.nodes.new(type= 'CompositorNodeBlur')
    blur1_node.location = -200,150
    blur1_node.size_x = 1
    blur1_node.size_y = 1
    blur1_node.inputs[1].default_value = 0
    blur1_node.label = "Eye M F"
    blur1_node.hide = True

    rgb1_node = scifi_group.nodes.new(type= 'CompositorNodeCurveRGB')
    rgb1_node.location = 180,400
    rgb1_node.label = "Eye Ball Brightness"
    rgb1_node.hide = True

    transf2_node = scifi_group.nodes.new(type= 'CompositorNodeTransform')
    transf2_node.location = 100,-50
    transf2_node.inputs[4].default_value = 0.5
    transf2_node.label = "Right Eye Position"
    transf2_node.hide = True

    translate1_node = scifi_group.nodes.new(type= 'CompositorNodeTranslate')
    translate1_node.location = 360,150
    translate1_node.label = "Left Eye Track Position"
    translate1_node.hide = True

    translate2_node = scifi_group.nodes.new(type= 'CompositorNodeTranslate')
    translate2_node.location = 360,-50
    translate2_node.label = "Right Eye Track Position"
    translate2_node.hide = True

    alphaover1_node = scifi_group.nodes.new(type= 'CompositorNodeAlphaOver')
    alphaover1_node.location = 600,300
    alphaover1_node.use_premultiply = True
    alphaover1_node.hide = True
    alphaover1_node.label = "Alpha 1"


    alphaover2_node = scifi_group.nodes.new(type= 'CompositorNodeAlphaOver')
    alphaover2_node.location = 1000,300
    alphaover2_node.use_premultiply = True
    alphaover2_node.hide = True

    math1_node = scifi_group.nodes.new(type= 'CompositorNodeMath')
    math1_node.location = 1050,200
    math1_node.hide = True
    math1_node.operation = 'MULTIPLY'
    math1_node.use_clamp = True

    blur2_node = scifi_group.nodes.new(type= 'CompositorNodeBlur')
    blur2_node.location = 1200,200
    blur2_node.hide = True
    blur2_node.size_x = 1
    blur2_node.size_y = 1
    blur2_node.inputs[1].default_value = 0
    blur2_node.label = "Shadow Feather"
    blur2_node.hide = True



    alphaover3_node = scifi_group.nodes.new(type= 'CompositorNodeAlphaOver')
    alphaover3_node.location = 1350,300
    alphaover3_node.inputs[2].default_value = (0, 0, 0, 0.5)
    alphaover3_node.label = "Shadow"
    alphaover3_node.hide = True



    #link nodes together


    scifi_group.links.new(transf1_node.outputs[0], translate1_node.inputs[0])

    scifi_group.links.new(translate1_node.outputs[0], alphaover1_node.inputs[2])


    scifi_group.links.new(transf2_node.outputs[0], translate2_node.inputs[0])

    scifi_group.links.new(translate2_node.outputs[0], alphaover2_node.inputs[2])

    scifi_group.links.new(alphaover1_node.outputs[0], alphaover2_node.inputs[1])


    scifi_group.links.new(alphaover2_node.outputs[0], alphaover3_node.inputs[1])


    scifi_group.links.new(rerout1_node.outputs[0], transf1_node.inputs[0])

    scifi_group.links.new(rerout1_node.outputs[0], transf2_node.inputs[0])


    scifi_group.links.new(rerout2_node.outputs[0], alphaover1_node.inputs[0])

    scifi_group.links.new(rerout2_node.outputs[0], alphaover2_node.inputs[0])

    scifi_group.links.new(rgb1_node.outputs[0], alphaover1_node.inputs[1])

    scifi_group.links.new(rerout2_node.outputs[0], rgb1_node.inputs[0])

    scifi_group.links.new(blur1_node.outputs[0], rerout2_node.inputs[0])

    scifi_group.links.new(rerout2_node.outputs[0], math1_node.inputs[1])

    scifi_group.links.new(math1_node.outputs[0], blur2_node.inputs[0])

    scifi_group.links.new(blur2_node.outputs[0], alphaover3_node.inputs[0])









        # link inputs
    scifi_group.links.new(group_inputs.outputs['Eye Image'], rerout1_node.inputs[0])

    scifi_group.links.new(group_inputs.outputs['Movie Clip'], rgb1_node.inputs[1])

    scifi_group.links.new(group_inputs.outputs['Eye Lid Mask'], blur1_node.inputs[0])

    scifi_group.links.new(group_inputs.outputs['Shadow Mask'], math1_node.inputs[0])
    scifi_group.links.new(group_inputs.outputs['Shadow Feather'], blur2_node.inputs[1])

    scifi_group.links.new(group_inputs.outputs['Left Eye (Track Pos X)'], translate1_node.inputs[1])

    scifi_group.links.new(group_inputs.outputs['Left Eye (Track Pos Y)'], translate1_node.inputs[2])

    scifi_group.links.new(group_inputs.outputs['Right Eye (Track Pos X)'], translate2_node.inputs[1])

    scifi_group.links.new(group_inputs.outputs['Right Eye (Track Pos Y)'], translate2_node.inputs[2])

    scifi_group.links.new(group_inputs.outputs['Left Eye: X'], transf1_node.inputs[1])

    scifi_group.links.new(group_inputs.outputs['Left Eye: Y'], transf1_node.inputs[2])

    scifi_group.links.new(group_inputs.outputs['Right Eye: X'], transf2_node.inputs[1])

    scifi_group.links.new(group_inputs.outputs['Right Eye: Y'], transf2_node.inputs[2])

    scifi_group.links.new(group_inputs.outputs['Left Eye: Rotation'], transf1_node.inputs[3])

    scifi_group.links.new(group_inputs.outputs['Right Eye: Rotation'], transf2_node.inputs[3])

    scifi_group.links.new(group_inputs.outputs['Left Eye: Scale'], transf1_node.inputs[4])

    scifi_group.links.new(group_inputs.outputs['Right Eye: Scale'], transf2_node.inputs[4])

    scifi_group.links.new(group_inputs.outputs['Eyeball Brightness'], rgb1_node.inputs[3])

    scifi_group.links.new(group_inputs.outputs['Eye Mask Feather'], blur1_node.inputs[1])




    #link output
    scifi_group.links.new(alphaover3_node.outputs[0], group_outputs.inputs['Output'])





    #nodes outside group
    mov_node = tree.nodes.new(type= 'CompositorNodeMovieClip')
    mov_node.location = -200,300
    mov_node.select = False
    mov_node.label = "Background Movie Clip"



    img_node = tree.nodes.new(type= 'CompositorNodeImage')
    img_node.location = 0,100
    img_node.select = False
    img_node.label = "Sci fi Eye Image"

    trackpos_node = tree.nodes.new(type= 'CompositorNodeTrackPos')
    trackpos_node.location = -200,-100
    trackpos_node.select = False
    trackpos_node.label = "Left Eye Track Position"

    trackpos2_node = tree.nodes.new(type= 'CompositorNodeTrackPos')
    trackpos2_node.location = -200,-250
    trackpos2_node.select = False
    trackpos2_node.label = "Right Eye Track Position"

    mask1_node = tree.nodes.new(type= 'CompositorNodeMask')
    mask1_node.location = -400,300
    mask1_node.label = "Eye Lids Mask"
    mask1_node.select = False

    mask2_node = tree.nodes.new(type= 'CompositorNodeMask')
    mask2_node.location = -400,120
    mask2_node.label = "Shadow Mask"
    mask2_node.select = False

    comp_node = tree.nodes.new(type= 'CompositorNodeComposite')
    comp_node.location = 1000,100
    comp_node.select = False

    view_node = tree.nodes.new(type= 'CompositorNodeViewer')
    view_node.location = 1000,300
    view_node.select = False


    #connections bewteen nodes

    links = tree.links

    link = links.new(mov_node.outputs[0], comp_node.inputs[0])

    link = links.new(mov_node.outputs[0], view_node.inputs[0])





    #context for patch node
def patch(context):
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    #removes unwanted nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    #set render res to 100
    bpy.context.scene.render.resolution_percentage = 100




    # create a group
    patch_group = bpy.data.node_groups.new('Patch Node', 'CompositorNodeTree')



        # create group inputs
    group_inputs = patch_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-200,400)
    patch_group.inputs.new('NodeSocketFloat','Patch Mask')
    patch_group.inputs.new('NodeSocketFloat','Garbage Mask')
    patch_group.inputs.new('NodeSocketColor','Background Movie Clip')
    patch_group.inputs.new('NodeSocketColor','Patch Movie Clip')
    patch_group.inputs.new('NodeSocketFloat','Position X')
    patch_group.inputs.new('NodeSocketFloat','Position Y')
    patch_group.inputs.new('NodeSocketFloat','Rotation')
    patch_group.inputs.new('NodeSocketFloat','Scale')

    patch_group.inputs.new('NodeSocketFloat','Patch Feather')

    patch_group.inputs.new('NodeSocketFloat','Garbage Feather')
    patch_group.inputs.new('NodeSocketFloat','Perspective X')
    patch_group.inputs.new('NodeSocketFloat','Perspective Y')
    patch_group.inputs.new('NodeSocketFloat','Track Pos Input X')
    patch_group.inputs.new('NodeSocketFloat','Track Pos Input Y')
    patch_group.inputs[7].default_value = 1
    patch_group.inputs[11].default_value = 1
    patch_group.inputs[10].default_value = 1
    patch_group.inputs[1].default_value = 1
    patch_group.inputs[1].default_value = 0


        # create group outputs
    group_outputs = patch_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (2800,400)
    patch_group.outputs.new('NodeSocketColor','Output')



    #nodes to be added to group

    rerout1_node = patch_group.nodes.new(type= 'NodeReroute')
    rerout1_node.location = 0,0

    rerout2_node = patch_group.nodes.new(type= 'NodeReroute')
    rerout2_node.location = 0,100

    rerout3_node = patch_group.nodes.new(type= 'NodeReroute')
    rerout3_node.location = 0,200

    rerout4_node = patch_group.nodes.new(type= 'NodeReroute')
    rerout4_node.location = 0,300

    rerout5_node = patch_group.nodes.new(type= 'NodeReroute')
    rerout5_node.location = 0,400

    rerout6_node = patch_group.nodes.new(type= 'NodeReroute')
    rerout6_node.location = 0,500

    rerout7_node = patch_group.nodes.new(type= 'NodeReroute')
    rerout7_node.location = 0,700

    rerout8_node = patch_group.nodes.new(type= 'NodeReroute')
    rerout8_node.location = 0,800



    transf1_node = patch_group.nodes.new(type= 'CompositorNodeTransform')
    transf1_node.location = 200,500
    transf1_node.label = "Patch Mask Transform"
    transf1_node.inputs[0].name = "Mask Input"
    transf1_node.inputs[1].name = "Position X"
    transf1_node.inputs[2].name = "Position Y"
    transf1_node.inputs[3].name = "Rotation"
    transf1_node.hide = True


    transf2_node = patch_group.nodes.new(type= 'CompositorNodeTransform')
    transf2_node.location = 200,200
    transf2_node.label = "Patch Movie Transform"
    transf2_node.inputs[0].name = "Mask Input"
    transf2_node.inputs[1].name = "Position X"
    transf2_node.inputs[2].name = "Position Y"
    transf2_node.inputs[3].name = "Rotation"
    transf2_node.hide = True

    scale1_node = patch_group.nodes.new(type= 'CompositorNodeScale')
    scale1_node.location = 400,500
    scale1_node.label = "Mask Perspective Scale"
    scale1_node.hide = True

    scale2_node = patch_group.nodes.new(type= 'CompositorNodeScale')
    scale2_node.location = 400,200
    scale2_node.label = "Movie Perspective Scale"
    scale2_node.hide = True


    transl1_node = patch_group.nodes.new(type= 'CompositorNodeTranslate')
    transl1_node.location = 600,500
    transl1_node.label = "Patch Mask Track Input"
    transl1_node.hide = True

    transl2_node = patch_group.nodes.new(type= 'CompositorNodeTranslate')
    transl2_node.location = 600,200
    transl2_node.label = "Patch Movie Track Input"
    transl2_node.hide = True

    blur1_node = patch_group.nodes.new(type= 'CompositorNodeBlur')
    blur1_node.location = 800,500
    blur1_node.label = "Patch Mask Feather"
    blur1_node.size_x = 1
    blur1_node.size_y = 1
    blur1_node.inputs[1].name = "Patch Feather"
    blur1_node.inputs[1].default_value = 0
    blur1_node.hide = True

    blur2_node = patch_group.nodes.new(type= 'CompositorNodeBlur')
    blur2_node.location = 800,700
    blur2_node.label = "Garb Mask Feather"
    blur2_node.size_x = 1
    blur2_node.size_y = 1
    blur2_node.inputs[1].name = "Garb Feather"
    blur2_node.inputs[1].default_value = 0
    blur2_node.hide = True

    math1_node = patch_group.nodes.new(type= 'CompositorNodeMath')
    math1_node.location = 1100,600
    math1_node.label = "Garbage Math"
    math1_node.use_clamp = True
    math1_node.operation = 'SUBTRACT'
    math1_node.hide = True

    mix1_node = patch_group.nodes.new(type= 'CompositorNodeMixRGB')
    mix1_node.location = 1300,0
    mix1_node.hide = True


     #link nodes together

    patch_group.links.new(transf1_node.outputs[0], scale1_node.inputs[0])

    patch_group.links.new(scale1_node.outputs[0], transl1_node.inputs[0])

    patch_group.links.new(transl1_node.outputs[0], blur1_node.inputs[0])

    patch_group.links.new(transf2_node.outputs[0], scale2_node.inputs[0])

    patch_group.links.new(scale2_node.outputs[0], transl2_node.inputs[0])

    patch_group.links.new(transl2_node.outputs[0], mix1_node.inputs[2])

    patch_group.links.new(blur1_node.outputs[0], math1_node.inputs[0])

    patch_group.links.new(blur2_node.outputs[0], math1_node.inputs[1])

    patch_group.links.new(math1_node.outputs[0], mix1_node.inputs[0])

    patch_group.links.new(rerout1_node.outputs[0], transf1_node.inputs[1])

    patch_group.links.new(rerout1_node.outputs[0], transf2_node.inputs[1])

    patch_group.links.new(rerout2_node.outputs[0], transf1_node.inputs[2])

    patch_group.links.new(rerout2_node.outputs[0], transf2_node.inputs[2])

    patch_group.links.new(rerout3_node.outputs[0], transf1_node.inputs[3])

    patch_group.links.new(rerout3_node.outputs[0], transf2_node.inputs[3])

    patch_group.links.new(rerout4_node.outputs[0], transf1_node.inputs[4])

    patch_group.links.new(rerout4_node.outputs[0], transf2_node.inputs[4])

    patch_group.links.new(rerout5_node.outputs[0], scale1_node.inputs[1])

    patch_group.links.new(rerout5_node.outputs[0], scale2_node.inputs[1])

    patch_group.links.new(rerout6_node.outputs[0], scale1_node.inputs[2])

    patch_group.links.new(rerout6_node.outputs[0], scale2_node.inputs[2])

    patch_group.links.new(rerout7_node.outputs[0], transl1_node.inputs[1])

    patch_group.links.new(rerout7_node.outputs[0], transl2_node.inputs[1])

    patch_group.links.new(rerout8_node.outputs[0], transl1_node.inputs[2])

    patch_group.links.new(rerout8_node.outputs[0], transl2_node.inputs[2])



    # link inputs
    patch_group.links.new(group_inputs.outputs['Patch Mask'], transf1_node.inputs[0])

    patch_group.links.new(group_inputs.outputs['Garbage Mask'], blur2_node.inputs[0])

    patch_group.links.new(group_inputs.outputs['Background Movie Clip'], mix1_node.inputs[1])

    patch_group.links.new(group_inputs.outputs['Patch Movie Clip'], transf2_node.inputs[0])

    patch_group.links.new(group_inputs.outputs['Position X'], rerout1_node.inputs[0])

    patch_group.links.new(group_inputs.outputs['Position Y'], rerout2_node.inputs[0])

    patch_group.links.new(group_inputs.outputs['Rotation'], rerout3_node.inputs[0])

    patch_group.links.new(group_inputs.outputs['Scale'], rerout4_node.inputs[0])

    patch_group.links.new(group_inputs.outputs['Perspective X'], rerout5_node.inputs[0])

    patch_group.links.new(group_inputs.outputs['Perspective Y'], rerout6_node.inputs[0])

    patch_group.links.new(group_inputs.outputs['Track Pos Input X'], rerout7_node.inputs[0])

    patch_group.links.new(group_inputs.outputs['Track Pos Input Y'], rerout8_node.inputs[0])

    patch_group.links.new(group_inputs.outputs['Patch Feather'], blur1_node.inputs[1])

    patch_group.links.new(group_inputs.outputs['Garbage Feather'], blur2_node.inputs[1])


        #link output
    patch_group.links.new(mix1_node.outputs[0], group_outputs.inputs['Output'])




        #nodes to be added outside group
    mov1_node = tree.nodes.new(type= 'CompositorNodeMovieClip')
    mov1_node.location = 0,100
    mov1_node.select = False
    mov1_node.label = "Background Movie Clip"

    mov2_node = tree.nodes.new(type= 'CompositorNodeMovieClip')
    mov2_node.location = 200,-100
    mov2_node.select = False
    mov2_node.label = "Patch Movie Clip"

    mask1_node = tree.nodes.new(type= 'CompositorNodeMask')
    mask1_node.location = -200,100
    mask1_node.select = False
    mask1_node.label = "Patch Mask"

    trackpos1_node = tree.nodes.new(type= 'CompositorNodeTrackPos')
    trackpos1_node.location = -200,-90
    trackpos1_node.select = False
    trackpos1_node.label = "Track Position"


    comp_node = tree.nodes.new(type= 'CompositorNodeComposite')
    comp_node.location = 1000,-100
    comp_node.select = False

    view_node = tree.nodes.new(type= 'CompositorNodeViewer')
    view_node.location = 1000,100
    view_node.select = False



    #connections bewteen nodes
    links = tree.links

    link = links.new(mov1_node.outputs[0], comp_node.inputs[0])

    link = links.new(mov1_node.outputs[0], view_node.inputs[0])









    #context for patch node
def clone(context):
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    #removes unwanted nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    #set render res to 100
    bpy.context.scene.render.resolution_percentage = 100




    # create a group
    clone_group = bpy.data.node_groups.new('Clone Node', 'CompositorNodeTree')



        # create group inputs
    group_inputs = clone_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-200,400)
    clone_group.inputs.new('NodeSocketFloat','Clone Mask')
    clone_group.inputs.new('NodeSocketFloat','Garbage Mask')
    clone_group.inputs.new('NodeSocketColor','Background Movie Clip')
    clone_group.inputs.new('NodeSocketFloat','Position X')
    clone_group.inputs.new('NodeSocketFloat','Position Y')
    clone_group.inputs.new('NodeSocketFloat','Rotation')
    clone_group.inputs.new('NodeSocketFloat','Scale')

    clone_group.inputs.new('NodeSocketFloat','Clone Feather')

    clone_group.inputs.new('NodeSocketFloat','Garbage Feather')
    clone_group.inputs[7].default_value = 1
    clone_group.inputs[6].default_value = 1


        # create group outputs
    group_outputs = clone_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (2300,400)
    clone_group.outputs.new('NodeSocketColor','Output')



    #nodes to be added to group

    rerout1_node = clone_group.nodes.new(type= 'NodeReroute')
    rerout1_node.location = 0,150

    rerout2_node = clone_group.nodes.new(type= 'NodeReroute')
    rerout2_node.location = 0,100

    rerout3_node = clone_group.nodes.new(type= 'NodeReroute')
    rerout3_node.location = 0,200

    rerout4_node = clone_group.nodes.new(type= 'NodeReroute')
    rerout4_node.location = 0,0


    rerout9_node = clone_group.nodes.new(type= 'NodeReroute')
    rerout9_node.location = 0,400


    transf2_node = clone_group.nodes.new(type= 'CompositorNodeTransform')
    transf2_node.location = 200,200
    transf2_node.label = "Movie Transform2"
    transf2_node.inputs[0].name = "Movie Input"
    transf2_node.inputs[1].name = "Position X"
    transf2_node.inputs[2].name = "Position Y"
    transf2_node.inputs[3].name = "Rotation"
    transf2_node.hide = True

    blur1_node = clone_group.nodes.new(type= 'CompositorNodeBlur')
    blur1_node.location = 800,500
    blur1_node.label = "Clone Mask Feather"
    blur1_node.size_x = 1
    blur1_node.size_y = 1
    blur1_node.inputs[1].name = "Patch Feather"
    blur1_node.inputs[1].default_value = 0
    blur1_node.hide = True

    blur2_node = clone_group.nodes.new(type= 'CompositorNodeBlur')
    blur2_node.location = 800,700
    blur2_node.label = "Garb Mask Feather"
    blur2_node.size_x = 1
    blur2_node.size_y = 1
    blur2_node.inputs[1].name = "Garb Feather"
    blur2_node.inputs[1].default_value = 0
    blur2_node.hide = True

    math1_node = clone_group.nodes.new(type= 'CompositorNodeMath')
    math1_node.location = 1100,600
    math1_node.label = "Garbage Math"
    math1_node.use_clamp = True
    math1_node.operation = 'SUBTRACT'
    math1_node.hide = True

    mix1_node = clone_group.nodes.new(type= 'CompositorNodeMixRGB')
    mix1_node.location = 1300,0
    mix1_node.hide = True


     #link nodes together





    clone_group.links.new(blur1_node.outputs[0], math1_node.inputs[0])

    clone_group.links.new(blur2_node.outputs[0], math1_node.inputs[1])

    clone_group.links.new(math1_node.outputs[0], mix1_node.inputs[0])

    clone_group.links.new(rerout1_node.outputs[0], transf2_node.inputs[1])

    clone_group.links.new(rerout2_node.outputs[0], transf2_node.inputs[2])

    clone_group.links.new(rerout3_node.outputs[0], transf2_node.inputs[3])

    clone_group.links.new(rerout4_node.outputs[0], transf2_node.inputs[4])

    clone_group.links.new(rerout9_node.outputs[0], mix1_node.inputs[1])

    clone_group.links.new(rerout9_node.outputs[0], transf2_node.inputs[0])

    clone_group.links.new(transf2_node.outputs[0], mix1_node.inputs[2])



    # link inputs
    clone_group.links.new(group_inputs.outputs['Clone Mask'], blur1_node.inputs[0])

    clone_group.links.new(group_inputs.outputs['Garbage Mask'], blur2_node.inputs[0])

    clone_group.links.new(group_inputs.outputs['Background Movie Clip'], rerout9_node.inputs[0])

    clone_group.links.new(group_inputs.outputs['Position X'], rerout1_node.inputs[0])

    clone_group.links.new(group_inputs.outputs['Position Y'], rerout2_node.inputs[0])

    clone_group.links.new(group_inputs.outputs['Rotation'], rerout3_node.inputs[0])

    clone_group.links.new(group_inputs.outputs['Scale'], rerout4_node.inputs[0])

    clone_group.links.new(group_inputs.outputs['Clone Feather'], blur1_node.inputs[1])

    clone_group.links.new(group_inputs.outputs['Garbage Feather'], blur2_node.inputs[1])


        #link output
    clone_group.links.new(mix1_node.outputs[0], group_outputs.inputs['Output'])




        #nodes to be added outside group
    mov1_node = tree.nodes.new(type= 'CompositorNodeMovieClip')
    mov1_node.location = 0,100
    mov1_node.select = False
    mov1_node.label = "Background Movie Clip"


    mask1_node = tree.nodes.new(type= 'CompositorNodeMask')
    mask1_node.location = -200,100
    mask1_node.select = False
    mask1_node.label = "Clone Mask"


    comp_node = tree.nodes.new(type= 'CompositorNodeComposite')
    comp_node.location = 1000,-100
    comp_node.select = False

    view_node = tree.nodes.new(type= 'CompositorNodeViewer')
    view_node.location = 1000,100
    view_node.select = False



    #connections bewteen nodes
    links = tree.links

    link = links.new(mov1_node.outputs[0], comp_node.inputs[0])

    link = links.new(mov1_node.outputs[0], view_node.inputs[0])



























    #context for glitch effect
def glitch(context):
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    #removes unwanted nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

         #set render res to 100
    bpy.context.scene.render.resolution_percentage = 100


        # create a group
    glitch_group = bpy.data.node_groups.new('Glitch Node', 'CompositorNodeTree')

        # create group inputs
    group_inputs = glitch_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-300,0)

    glitch_group.inputs.new('NodeSocketColor','Movie Clip')

    glitch_group.inputs.new('NodeSocketColor','Glitch Image')

    glitch_group.inputs.new('NodeSocketFloat','Glitch Image Offset')

    glitch_group.inputs.new('NodeSocketFloat','Glitch Image Size')

    glitch_group.inputs.new('NodeSocketFloat','Chromatic Amount')

    glitch_group.inputs.new('NodeSocketFloat','Glitch Movement')

    glitch_group.inputs.new('NodeSocketFloat','Movie Clip Scale')

    glitch_group.inputs.new('NodeSocketFloat','Movie Clip Pos X')

    glitch_group.inputs.new('NodeSocketFloat','Movie Clip Pos Y')

    glitch_group.inputs[3].default_value = 1
    glitch_group.inputs[6].default_value = 1


        # create group outputs
    group_outputs = glitch_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (1400,0)
    glitch_group.outputs.new('NodeSocketColor','Output')



    #nodes to be added to group

    rerout1_node = glitch_group.nodes.new(type= 'NodeReroute')
    rerout1_node.location = 0,0

    scale1_node = glitch_group.nodes.new(type= 'CompositorNodeScale')
    scale1_node.location = 100,150
    scale1_node.label = "Scale"
    scale1_node.space = 'RENDER_SIZE'
    scale1_node.hide = True

    transf2_node = glitch_group.nodes.new(type= 'CompositorNodeTransform')
    transf2_node.location = 200,50
    transf2_node.label = "Glitch Size and Movement"
    transf2_node.hide = True

    transf3_node = glitch_group.nodes.new(type= 'CompositorNodeTransform')
    transf3_node.location = 200,-200
    transf3_node.label = "Glitch Offset"
    transf3_node.hide = True

    mix1_node = glitch_group.nodes.new(type= 'CompositorNodeMixRGB')
    mix1_node.location = 400,0
    mix1_node.hide = True
    mix1_node.use_clamp = True
    mix1_node.hide = True

    sep1_node = glitch_group.nodes.new(type= 'CompositorNodeSepRGBA')
    sep1_node.location = 600,0
    sep1_node.hide = True

    transl1_node = glitch_group.nodes.new(type= 'CompositorNodeTranslate')
    transl1_node.location = 800,200
    transl1_node.label = "Glitch Effect Amount (chromatic)"

    comb1_node = glitch_group.nodes.new(type= 'CompositorNodeCombRGBA')
    comb1_node.location = 1000,0
    comb1_node.hide = True

    transf1_node = glitch_group.nodes.new(type= 'CompositorNodeTransform')
    transf1_node.location = 1200,0
    transf1_node.hide = True




    #link nodes together


    glitch_group.links.new(transf2_node.outputs[0], mix1_node.inputs[0])

    glitch_group.links.new(scale1_node.outputs[0], transf2_node.inputs[0])

    glitch_group.links.new(transf2_node.outputs[0], mix1_node.inputs[0])

    glitch_group.links.new(mix1_node.outputs[0], sep1_node.inputs[0])

    glitch_group.links.new(sep1_node.outputs[0], transl1_node.inputs[0])

    glitch_group.links.new(transl1_node.outputs[0], comb1_node.inputs[0])

    glitch_group.links.new(sep1_node.outputs[1], comb1_node.inputs[1])

    glitch_group.links.new(sep1_node.outputs[2], comb1_node.inputs[2])

    glitch_group.links.new(comb1_node.outputs[0], transf1_node.inputs[0])

    glitch_group.links.new(rerout1_node.outputs[0], mix1_node.inputs[1])

    glitch_group.links.new(rerout1_node.outputs[0], transf3_node.inputs[0])

    glitch_group.links.new(transf3_node.outputs[0], mix1_node.inputs[2])

        # link inputs

    glitch_group.links.new(group_inputs.outputs['Movie Clip'], rerout1_node.inputs[0])

    glitch_group.links.new(group_inputs.outputs['Glitch Image'], scale1_node.inputs[0])

    glitch_group.links.new(group_inputs.outputs['Glitch Image Size'], transf2_node.inputs[4])

    glitch_group.links.new(group_inputs.outputs['Glitch Movement'], transf2_node.inputs[2])

    glitch_group.links.new(group_inputs.outputs['Chromatic Amount'], transl1_node.inputs[1])

    glitch_group.links.new(group_inputs.outputs['Movie Clip Scale'], transf1_node.inputs[4])

    glitch_group.links.new(group_inputs.outputs['Movie Clip Pos X'], transf1_node.inputs[1])

    glitch_group.links.new(group_inputs.outputs['Movie Clip Pos Y'], transf1_node.inputs[2])

    glitch_group.links.new(group_inputs.outputs['Glitch Image Offset'], transf3_node.inputs[1])




        #link output
    glitch_group.links.new(transf1_node.outputs[0], group_outputs.inputs['Output'])




        #nodes to be added outside of group
    mov1_node = tree.nodes.new(type= 'CompositorNodeMovieClip')
    mov1_node.location = 0,100
    mov1_node.select = False

    img1_node = tree.nodes.new(type= 'CompositorNodeImage')
    img1_node.location = -200,100
    img1_node.select = False
    img1_node.label = "Glitch Image"

    comp_node = tree.nodes.new(type= 'CompositorNodeComposite')
    comp_node.location = 900,-100
    comp_node.select = False

    view_node = tree.nodes.new(type= 'CompositorNodeViewer')
    view_node.location = 900,100
    view_node.select = False

    #connections bewteen nodes
    links = tree.links

    link = links.new(mov1_node.outputs[0], comp_node.inputs[0])
    link = links.new(mov1_node.outputs[0], view_node.inputs[0])




    #context for Color Presets (Sketch)
def colpre(context):
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

        # create a group
    colpre_group = bpy.data.node_groups.new('Color Presets Node', 'CompositorNodeTree')

        # create group inputs
    group_inputs = colpre_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-200,0)

    #colpre_group.inputs.new('NodeSocketColor','Movie Clip')


    # create group outputs
    group_outputs = colpre_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (200,0)
    colpre_group.outputs.new('NodeSocketColor','Natural White')
    colpre_group.outputs.new('NodeSocketColor','Slightly Aged')
    colpre_group.outputs.new('NodeSocketColor','Parchment 1')
    colpre_group.outputs.new('NodeSocketColor','Parchment 2')


       #nodes to be added to group

    natwhite_node = colpre_group.nodes.new(type= 'CompositorNodeRGB')
    natwhite_node.location = 0,200
    natwhite_node.location = 0,200
    natwhite_node.outputs[0].default_value = (0.938686, 0.930111, 0.846874, 1)
    natwhite_node.hide = True

    aged_node = colpre_group.nodes.new(type= 'CompositorNodeRGB')
    aged_node.location = 0,100
    aged_node.outputs[0].default_value = (0.887923, 0.854993, 0.597202, 1)
    aged_node.hide = True

    parch1_node = colpre_group.nodes.new(type= 'CompositorNodeRGB')
    parch1_node.location = 0,-100
    parch1_node.outputs[0].default_value = (0.83077, 0.665387, 0.450786, 1)
    parch1_node.hide = True

    parch2_node = colpre_group.nodes.new(type= 'CompositorNodeRGB')
    parch2_node.location = 0,-200
    parch2_node.outputs[0].default_value = (0.879623, 0.879623, 0.658375, 1)
    parch2_node.hide = True



        #link output
    colpre_group.links.new(natwhite_node.outputs[0], group_outputs.inputs['Natural White'])

    colpre_group.links.new(aged_node.outputs[0], group_outputs.inputs['Slightly Aged'])

    colpre_group.links.new(parch1_node.outputs[0], group_outputs.inputs['Parchment 1'])

    colpre_group.links.new(parch2_node.outputs[0], group_outputs.inputs['Parchment 2'])






    #context for sketch effect
def sketch(context):
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    #removes unwanted nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    #set render res to 100
    bpy.context.scene.render.resolution_percentage = 100


        # create a group
    sketch_group = bpy.data.node_groups.new('Sketch Node', 'CompositorNodeTree')

        # create group inputs
    group_inputs = sketch_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-200,400)

    sketch_group.inputs.new('NodeSocketColor','Movie Clip')

    sketch_group.inputs.new('NodeSocketFloat','Sketch Amount')

    sketch_group.inputs.new('NodeSocketFloat','Paper Image')

    sketch_group.inputs.new('NodeSocketColor','Paper Color')


    sketch_group.inputs[2].default_value = 1
    sketch_group.inputs[3].default_value = (1, 1, 1, 1)


    # create group outputs
    group_outputs = sketch_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (2000,0)
    sketch_group.outputs.new('NodeSocketColor','Output')


        #nodes to be added to group

    rerout1_node = sketch_group.nodes.new(type= 'NodeReroute')
    rerout1_node.location = 0,0

    scale1_node = sketch_group.nodes.new(type= 'CompositorNodeScale')
    scale1_node.location = 100,-150
    scale1_node.label = "Scale 1"
    scale1_node.space = 'RENDER_SIZE'
    scale1_node.hide = True

    scale2_node = sketch_group.nodes.new(type= 'CompositorNodeScale')
    scale2_node.location = 100,150
    scale2_node.label = "Scale 2"
    scale2_node.space = 'RENDER_SIZE'
    scale2_node.hide = True




    rgbbw_node = sketch_group.nodes.new(type= 'CompositorNodeRGBToBW')
    rgbbw_node.location = 200,-100
    rgbbw_node.hide = True

    inv_node = sketch_group.nodes.new(type= 'CompositorNodeInvert')
    inv_node.location = 400,-250
    inv_node.hide = True

    blur1_node = sketch_group.nodes.new(type= 'CompositorNodeBlur')
    blur1_node.location = 650,-250
    blur1_node.size_x = 1
    blur1_node.size_y = 1
    blur1_node.hide = True

    rgb_node = sketch_group.nodes.new(type= 'CompositorNodeCurveRGB')
    rgb_node.location = 900,-250

    mix1_node = sketch_group.nodes.new(type= 'CompositorNodeMixRGB')
    mix1_node.location = 400,-20
    mix1_node.blend_type = 'SATURATION'
    mix1_node.use_clamp = True
    mix1_node.hide = True

    mix2_node = sketch_group.nodes.new(type= 'CompositorNodeMixRGB')
    mix2_node.location = 1200,-20
    mix2_node.blend_type = 'DODGE'
    mix2_node.use_clamp = True
    mix2_node.hide = True

    mix3_node = sketch_group.nodes.new(type= 'CompositorNodeMixRGB')
    mix3_node.location = 1600,-20
    mix3_node.blend_type = 'MULTIPLY'
    mix3_node.use_clamp = True
    mix3_node.hide = True

    mix4_node = sketch_group.nodes.new(type= 'CompositorNodeMixRGB')
    mix4_node.location = 1900,-20
    mix4_node.blend_type = 'MULTIPLY'
    mix4_node.use_clamp = True
    mix4_node.label = "Mix4 col"



     #link nodes together

    sketch_group.links.new(rerout1_node.outputs[0], rgbbw_node.inputs[0])

    sketch_group.links.new(scale1_node.outputs[0], mix3_node.inputs[2])

    sketch_group.links.new(rerout1_node.outputs[0], mix1_node.inputs[1])


    sketch_group.links.new(rgbbw_node.outputs[0], inv_node.inputs[1])

    sketch_group.links.new(mix1_node.outputs[0], mix2_node.inputs[1])

    sketch_group.links.new(inv_node.outputs[0], blur1_node.inputs[0])

    sketch_group.links.new(blur1_node.outputs[0], rgb_node.inputs[1])

    sketch_group.links.new(rgb_node.outputs[0], mix2_node.inputs[2])

    sketch_group.links.new(mix2_node.outputs[0], mix3_node.inputs[1])

    sketch_group.links.new(mix3_node.outputs[0], mix4_node.inputs[1])

    sketch_group.links.new(scale2_node.outputs[0], mix4_node.inputs[2])


    # link inputs

    sketch_group.links.new(group_inputs.outputs['Movie Clip'], rerout1_node.inputs[0])

    sketch_group.links.new(group_inputs.outputs['Paper Image'], scale1_node.inputs[0])

    sketch_group.links.new(group_inputs.outputs['Sketch Amount'], blur1_node.inputs[1])

    sketch_group.links.new(group_inputs.outputs['Paper Color'], scale2_node.inputs[0])


        #link output
    sketch_group.links.new(mix4_node.outputs[0], group_outputs.inputs['Output'])





    #nodes to be added outisde of the group
    mov1_node = tree.nodes.new(type= 'CompositorNodeMovieClip')
    mov1_node.location = 0,0
    mov1_node.select = False

    img1_node = tree.nodes.new(type= 'CompositorNodeImage')
    img1_node.location = -200,0
    img1_node.select = False
    img1_node.label = "Paper Image"



    comp_node = tree.nodes.new(type= 'CompositorNodeComposite')
    comp_node.location = 900,-200
    comp_node.select = False

    view_node = tree.nodes.new(type= 'CompositorNodeViewer')
    view_node.location = 900,0
    view_node.select = False

    #connections bewteen nodes
    links = tree.links

    link = links.new(mov1_node.outputs[0], comp_node.inputs[0])

    link = links.new(mov1_node.outputs[0], view_node.inputs[0])









    #context for posterize 1 effect
def post1(context):
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    #removes unwanted nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    #set render res to 100
    bpy.context.scene.render.resolution_percentage = 100


        # create a group
    post1_group = bpy.data.node_groups.new('Posterize Node (Soft Light)', 'CompositorNodeTree')

        # create group inputs
    group_inputs = post1_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-200,0)

    post1_group.inputs.new('NodeSocketColor','Movie Clip')
    post1_group.inputs.new('NodeSocketFloat','Value 1')
    post1_group.inputs.new('NodeSocketFloat','Value 2')
    post1_group.inputs.new('NodeSocketFloat','Value 3')
    post1_group.inputs[1].default_value = 9.1
    post1_group.inputs[2].default_value = 1.3
    post1_group.inputs[3].default_value = 9

    # create group outputs
    group_outputs = post1_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (2000,0)
    post1_group.outputs.new('NodeSocketColor','Output')

        #nodes to be added to group

    rerout1_node = post1_group.nodes.new(type= 'NodeReroute')
    rerout1_node.location = 0,0

    math1_node = post1_group.nodes.new(type= 'CompositorNodeMath')
    math1_node.location = 200,0
    math1_node.operation = 'MULTIPLY'
    math1_node.inputs[1].default_value = 5

    math2_node = post1_group.nodes.new(type= 'CompositorNodeMath')
    math2_node.location = 400,0
    math2_node.operation = 'SUBTRACT'
    math2_node.inputs[1].default_value = 0.1

    math3_node = post1_group.nodes.new(type= 'CompositorNodeMath')
    math3_node.location = 600,0
    math3_node.operation = 'ROUND'
    math3_node.inputs[1].default_value = 0

    math4_node = post1_group.nodes.new(type= 'CompositorNodeMath')
    math4_node.location = 800,0
    math4_node.operation = 'DIVIDE'
    math4_node.inputs[1].default_value = 2

    mix_node = post1_group.nodes.new(type= 'CompositorNodeMixRGB')
    mix_node.location = 1000,0
    mix_node.blend_type = 'SOFT_LIGHT'


        #link nodes together

    post1_group.links.new(rerout1_node.outputs[0], math1_node.inputs[0])

    post1_group.links.new(rerout1_node.outputs[0], mix_node.inputs[2])

    post1_group.links.new(math1_node.outputs[0], math2_node.inputs[0])

    post1_group.links.new(math2_node.outputs[0], math3_node.inputs[0])

    post1_group.links.new(math3_node.outputs[0], math4_node.inputs[0])

    post1_group.links.new(math4_node.outputs[0], mix_node.inputs[1])

    # link inputs

    post1_group.links.new(group_inputs.outputs['Movie Clip'], rerout1_node.inputs[0])
    post1_group.links.new(group_inputs.outputs['Value 1'], math1_node.inputs[1])
    post1_group.links.new(group_inputs.outputs['Value 2'], math2_node.inputs[1])
    post1_group.links.new(group_inputs.outputs['Value 3'], math4_node.inputs[1])

    #link output
    post1_group.links.new(mix_node.outputs[0], group_outputs.inputs['Output'])





    #nodes to be added
    mov1_node = tree.nodes.new(type= 'CompositorNodeMovieClip')
    mov1_node.location = 0,0
    mov1_node.select = False

    comp_node = tree.nodes.new(type= 'CompositorNodeComposite')
    comp_node.location = 1200,-200
    comp_node.select = False

    view_node = tree.nodes.new(type= 'CompositorNodeViewer')
    view_node.location = 1200,0
    view_node.select = False

    links = tree.links


    link = links.new(mov1_node.outputs[0], comp_node.inputs[0])

    link = links.new(mov1_node.outputs[0], view_node.inputs[0])









#context for posterize 2 effect
def post2(context):
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    #removes unwanted nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    #set render res to 100
    bpy.context.scene.render.resolution_percentage = 100


        # create a group
    post2_group = bpy.data.node_groups.new('Posterize Node (Add)', 'CompositorNodeTree')

        # create group inputs
    group_inputs = post2_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-200,0)

    post2_group.inputs.new('NodeSocketColor','Movie Clip')
    post2_group.inputs.new('NodeSocketFloat','Value 1')
    post2_group.inputs.new('NodeSocketFloat','Value 2')
    post2_group.inputs.new('NodeSocketFloat','Value 3')
    post2_group.inputs[1].default_value = 15
    post2_group.inputs[2].default_value = 0.2
    post2_group.inputs[3].default_value = 9

    # create group outputs
    group_outputs = post2_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (2000,0)
    post2_group.outputs.new('NodeSocketColor','Output')

        #nodes to be added to group

    rerout1_node = post2_group.nodes.new(type= 'NodeReroute')
    rerout1_node.location = 0,0

    math1_node = post2_group.nodes.new(type= 'CompositorNodeMath')
    math1_node.location = 200,0
    math1_node.operation = 'MULTIPLY'
    math1_node.inputs[1].default_value = 10

    math2_node = post2_group.nodes.new(type= 'CompositorNodeMath')
    math2_node.location = 400,0
    math2_node.operation = 'SUBTRACT'
    math2_node.inputs[1].default_value = 0

    math3_node = post2_group.nodes.new(type= 'CompositorNodeMath')
    math3_node.location = 600,0
    math3_node.operation = 'ROUND'
    math3_node.inputs[1].default_value = 0

    math4_node = post2_group.nodes.new(type= 'CompositorNodeMath')
    math4_node.location = 800,0
    math4_node.operation = 'DIVIDE'
    math4_node.inputs[1].default_value = 9

    mix_node = post2_group.nodes.new(type= 'CompositorNodeMixRGB')
    mix_node.location = 1000,0
    mix_node.blend_type = 'ADD'


        #link nodes together

    post2_group.links.new(rerout1_node.outputs[0], math1_node.inputs[0])

    post2_group.links.new(rerout1_node.outputs[0], mix_node.inputs[2])

    post2_group.links.new(math1_node.outputs[0], math2_node.inputs[0])

    post2_group.links.new(math2_node.outputs[0], math3_node.inputs[0])

    post2_group.links.new(math3_node.outputs[0], math4_node.inputs[0])

    post2_group.links.new(math4_node.outputs[0], mix_node.inputs[1])

    # link inputs

    post2_group.links.new(group_inputs.outputs['Movie Clip'], rerout1_node.inputs[0])
    post2_group.links.new(group_inputs.outputs['Value 1'], math1_node.inputs[1])
    post2_group.links.new(group_inputs.outputs['Value 2'], math2_node.inputs[1])
    post2_group.links.new(group_inputs.outputs['Value 3'], math4_node.inputs[1])

    #link output
    post2_group.links.new(mix_node.outputs[0], group_outputs.inputs['Output'])





    #nodes to be added
    mov1_node = tree.nodes.new(type= 'CompositorNodeMovieClip')
    mov1_node.location = 0,0
    mov1_node.select = False

    comp_node = tree.nodes.new(type= 'CompositorNodeComposite')
    comp_node.location = 1200,-200
    comp_node.select = False

    view_node = tree.nodes.new(type= 'CompositorNodeViewer')
    view_node.location = 1200,0
    view_node.select = False

    links = tree.links


    link = links.new(mov1_node.outputs[0], comp_node.inputs[0])

    link = links.new(mov1_node.outputs[0], view_node.inputs[0])














    #context for posterize 3 effect
def post3(context):
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    #removes unwanted nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    #set render res to 100
    bpy.context.scene.render.resolution_percentage = 100


        # create a group
    post3_group = bpy.data.node_groups.new('Posterize Node (Color)', 'CompositorNodeTree')

        # create group inputs
    group_inputs = post3_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-200,0)

    post3_group.inputs.new('NodeSocketColor','Movie Clip')
    post3_group.inputs.new('NodeSocketFloat','Value 1')
    post3_group.inputs.new('NodeSocketFloat','Value 2')
    post3_group.inputs.new('NodeSocketFloat','Value 3')
    post3_group.inputs[1].default_value = 6
    post3_group.inputs[2].default_value = 0.5
    post3_group.inputs[3].default_value = 5

    # create group outputs
    group_outputs = post3_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (2000,0)
    post3_group.outputs.new('NodeSocketColor','Output')

        #nodes to be added to group

    rerout1_node = post3_group.nodes.new(type= 'NodeReroute')
    rerout1_node.location = 0,0

    math1_node = post3_group.nodes.new(type= 'CompositorNodeMath')
    math1_node.location = 200,0
    math1_node.operation = 'MULTIPLY'
    math1_node.inputs[1].default_value = 6

    math2_node = post3_group.nodes.new(type= 'CompositorNodeMath')
    math2_node.location = 400,0
    math2_node.operation = 'SUBTRACT'
    math2_node.inputs[1].default_value = 0.5

    math3_node = post3_group.nodes.new(type= 'CompositorNodeMath')
    math3_node.location = 600,0
    math3_node.operation = 'ROUND'
    math3_node.inputs[1].default_value = 0

    math4_node = post3_group.nodes.new(type= 'CompositorNodeMath')
    math4_node.location = 800,0
    math4_node.operation = 'DIVIDE'
    math4_node.inputs[1].default_value = 5

    mix_node = post3_group.nodes.new(type= 'CompositorNodeMixRGB')
    mix_node.location = 1000,0
    mix_node.blend_type = 'COLOR'



        #link nodes together

    post3_group.links.new(rerout1_node.outputs[0], math1_node.inputs[0])

    post3_group.links.new(rerout1_node.outputs[0], mix_node.inputs[2])

    post3_group.links.new(math1_node.outputs[0], math2_node.inputs[0])

    post3_group.links.new(math2_node.outputs[0], math3_node.inputs[0])

    post3_group.links.new(math3_node.outputs[0], math4_node.inputs[0])

    post3_group.links.new(math4_node.outputs[0], mix_node.inputs[1])

        # link inputs

    post3_group.links.new(group_inputs.outputs['Movie Clip'], rerout1_node.inputs[0])
    post3_group.links.new(group_inputs.outputs['Value 1'], math1_node.inputs[1])
    post3_group.links.new(group_inputs.outputs['Value 2'], math2_node.inputs[1])
    post3_group.links.new(group_inputs.outputs['Value 3'], math4_node.inputs[1])

        #link output
    post3_group.links.new(mix_node.outputs[0], group_outputs.inputs['Output'])





        #nodes to be added
    mov1_node = tree.nodes.new(type= 'CompositorNodeMovieClip')
    mov1_node.location = 0,0
    mov1_node.select = False

    comp_node = tree.nodes.new(type= 'CompositorNodeComposite')
    comp_node.location = 1200,-200
    comp_node.select = False

    view_node = tree.nodes.new(type= 'CompositorNodeViewer')
    view_node.location = 1200,0
    view_node.select = False

    links = tree.links


    link = links.new(mov1_node.outputs[0], comp_node.inputs[0])

    link = links.new(mov1_node.outputs[0], view_node.inputs[0])






    #context for ink drop 2
def inkdr2(context):
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    #removes unwanted nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    #set render res to 100
    bpy.context.scene.render.resolution_percentage = 100


        # create a group
    inkdrop_group = bpy.data.node_groups.new('Ink Drop Node', 'CompositorNodeTree')

        # create group inputs
    group_inputs = inkdrop_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-200,0)

    inkdrop_group.inputs.new('NodeSocketColor','Smoke Movie Clip')

    inkdrop_group.inputs.new('NodeSocketColor','Black and White Text Image')

    # create group outputs
    group_outputs = inkdrop_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (2000,0)
    inkdrop_group.outputs.new('NodeSocketColor','Output')

        #nodes to be added to group

    rgb_node = inkdrop_group.nodes.new(type= 'CompositorNodeCurveRGB')
    rgb_node.location = 600,150


    mix_node = inkdrop_group.nodes.new(type= 'CompositorNodeMixRGB')
    mix_node.location = 400,150
    mix_node.hide = True

    rgbtobw_node = inkdrop_group.nodes.new(type= 'CompositorNodeRGBToBW')
    rgbtobw_node.location = 250,160
    rgbtobw_node.hide = True

    inv_node = inkdrop_group.nodes.new(type= 'CompositorNodeInvert')
    inv_node.location = 200,0
    inv_node.hide = True


    #link nodes together

    inkdrop_group.links.new(rgbtobw_node.outputs[0], mix_node.inputs[0])

    inkdrop_group.links.new(inv_node.outputs[0], mix_node.inputs[1])

    inkdrop_group.links.new(mix_node.outputs[0], rgb_node.inputs[1])

    # link inputs

    inkdrop_group.links.new(group_inputs.outputs['Smoke Movie Clip'], rgbtobw_node.inputs[0])

    inkdrop_group.links.new(group_inputs.outputs['Black and White Text Image'], inv_node.inputs[0])


        #link output
    inkdrop_group.links.new(rgb_node.outputs[0], group_outputs.inputs['Output'])



    #nodes to be added outside of group
    mov1_node = tree.nodes.new(type= 'CompositorNodeMovieClip')
    mov1_node.location = 0,100
    mov1_node.select = False
    mov1_node.label = "Smoke Movie Clip"

    img1_node = tree.nodes.new(type= 'CompositorNodeImage')
    img1_node.location = -200,100
    img1_node.select = False
    img1_node.label = "Black and White Image (Your Text)"

    comp_node = tree.nodes.new(type= 'CompositorNodeComposite')
    comp_node.location = 700,-100
    comp_node.select = False

    view_node = tree.nodes.new(type= 'CompositorNodeViewer')
    view_node.location = 700,100
    view_node.select = False



    links = tree.links


    link = links.new(mov1_node.outputs[0], comp_node.inputs[0])

    link = links.new(mov1_node.outputs[0], view_node.inputs[0])










    #operation to add Glitch Effect
class GlitchOP(bpy.types.Operator):
    """Click this button to Add a Glitch Effect to your Video. You need an Image for the Glitch Effect. Then you must animate the the Value"""
    bl_idname = "glitch.addnodes"
    bl_label = " Glitch Effect"

    def execute(self, context):
        glitch(context)
        return {'FINISHED'}





    #operation to add Patch Nodes
class PatchOP(bpy.types.Operator):
    """Click this Button to Add (or patch) an Image / Movie clip on top of your Background Footage. One Mask required for the Object to be Patched"""
    bl_idname = "patch.addnodes"
    bl_label = " Patch Node"

    def execute(self, context):
        patch(context)
        return {'FINISHED'}




    #operation to add Clone Node
class CloneOP(bpy.types.Operator):
    """Click this Button to Clone an area of your Movie clip."""
    bl_idname = "clone.addnodes"
    bl_label = " Clone Node"

    def execute(self, context):
        clone(context)
        return {'FINISHED'}








    #operation to add Sci Fi Eye Nodes
class SciFiEyeOP(bpy.types.Operator):
    """Click this Button to Add Sci-fi Eyes to your Movie clip. Eye Image Texture required. Visit our blog to use our Image Textures or use your own"""
    bl_idname = "scifieye.addnodes"
    bl_label = " Sci fi Eyes"

    def execute(self, context):
        sfe(context)
        return {'FINISHED'}



     #operation to add Col Change Nodes
class EyeColOP(bpy.types.Operator):
    """Click this Button to Change the Eye Color for the Person in your Movie clip. Requires atleast one Mask for the Area of Effect (Eyes)"""
    bl_idname = "eyecol.addnodes"
    bl_label = " Eye Color Change"

    def execute(self, context):
        eyecolchange(context)
        return {'FINISHED'}

    #operation to add Sketch Effect
class SketchOP(bpy.types.Operator):
    """Click this Button to Add a Sketch Effect to your Video."""
    bl_idname = "sketch.addnodes"
    bl_label = " Sketch Effect"

    def execute(self, context):
        sketch(context)
        return {'FINISHED'}



    #operation to add Color Preset Group
class ColpreOP(bpy.types.Operator):
    """Click this Button to Add a Color Preset Group"""
    bl_idname = "colpre.addnodes"
    bl_label = " Paper Color Presets"

    def execute(self, context):
        colpre(context)
        return {'FINISHED'}







    #operation to add Posterize 1 Effect
class Post1OP(bpy.types.Operator):
    """Click this button to Add a Posterize Effect, using the Soft Light Blend Mode"""
    bl_idname = "post1.addnodes"
    bl_label = " Option 1"

    def execute(self, context):
        post1(context)
        return {'FINISHED'}


    #operation to add Posterize 2 Effect
class Post2OP(bpy.types.Operator):
    """Click this button to Add a Posterize Effect, using the Add Blend Mode"""
    bl_idname = "post2.addnodes"
    bl_label = " Option 2"

    def execute(self, context):
        post2(context)
        return {'FINISHED'}


    #operation to add Posterize 3 Effect
class Post3OP(bpy.types.Operator):
    """Click this button to Add a Posterize Effect, using the Multiply Blend Mode"""
    bl_idname = "post3.addnodes"
    bl_label = " Option 3"

    def execute(self, context):
        post3(context)
        return {'FINISHED'}


    #operation to add inkdrop2
class Inkdrop2(bpy.types.Operator):
    """The Ink Drop Effect, or Negative Inkdrop effect is a variation on the original"""
    bl_idname = "inkdr2.addnodes"
    bl_label = "Ink Drop Effect"

    def execute(self, context):
        inkdr2(context)
        return {'FINISHED'}




    #operation for Panel
class LayoutPanel(bpy.types.Panel):
    bl_label = "Darkfall VFX Nodes"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"


    def draw(self, context):
        layout = self.layout

        scene = context.scene

        layout.label(text="_______________________________________________")

        #Welcome text

        row = layout.row()
        layout.label(text=" Select one of the VFX Buttons,")
        layout.label(text=" and the required nodes will be added to the")
        layout.label(text=" Compositor Editor in the form of a Custom")
        layout.label(text=" Node Group.")
        row = layout.row()
        row = layout.row()
        layout.label(text=" Visit our blog for more information.")
        layout.label(text="_______________________________________________")

        #Col Change and Scifi Eyes UI

        row = layout.row()
        row = layout.row()
        row = layout.row()

        layout.label(text=" VFX Eyes", icon= 'HIDE_OFF')
        row = layout.row()
        row = layout.row()
        row = layout.row()
        layout.label(text=" The Eye Color Change, will change the color")
        layout.label(text=" of your subject's eyes.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        layout.label(text=" You will need a Mask for the Eyes, another")
        layout.label(text=" for the Eyelids, and Ideally (though not")
        layout.label(text=" compulsory), and  a Mask for the Garbage.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.operator("eyecol.addnodes", icon= 'VIS_SEL_11')
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        layout.label(text=" SCI FI Eyes will add an Eye Texture to your")
        layout.label(text=" subject's eyes.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        layout.label(text=" You will need a Mask for the Eyelids and an")
        layout.label(text=" Image Texture for the Eye. You can download")
        layout.label(text=" an Eye Image from our blog or use your own.")
        row = layout.row()
        row = layout.row(align=True)
        row = layout.row()
        row = layout.row()
        row.operator("scifieye.addnodes", icon= 'PROP_ON')
        row = layout.row()
        row = layout.row()
        row = layout.row()
        layout.label(text="_______________________________________________")


        #Patch Node UI

        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" Patch Node", icon= 'SEQ_PREVIEW')
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" The Patch Node will take an Image/Movieclip,")
        row = layout.row()
        row.label(text=" and add (or patch) it on top of your Videos")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" You will Need to Mask around your Patch,")
        row = layout.row()
        row.label(text=" Object. If your camera is moving, you will")
        row = layout.row()
        row.label(text=" also need to Track your shot.")
        row = layout.row()

        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.operator("patch.addnodes", icon= 'SEQ_PREVIEW')
        row = layout.row()
        row = layout.row()
        row = layout.row()

        row = layout.row()
        layout.label(text="_______________________________________________")


        #Clone Node UI

        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" Clone Node", icon= 'ZOOM_PREVIOUS')
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" The Clone Node will take an area of your")
        row = layout.row()
        row.label(text=" Movie clip and replace it with a different.")
        row = layout.row()
        row.label(text=" section of our clip.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" With a Mask we can define the area we want")
        row = layout.row()
        row.label(text=" to be replaced, cloning over any unwanted")
        row = layout.row()
        row.label(text=" objects.")
        row = layout.row()

        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.operator("clone.addnodes", icon= 'ZOOM_SELECTED')
        row = layout.row()
        row = layout.row()
        row = layout.row()

        row = layout.row()
        layout.label(text="_______________________________________________")

        #Glitch Node UI

        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" Glitch Effect", icon= 'HAND')
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" The Glitch Effect will take a Movie clip and")
        row = layout.row()
        row.label(text=" add a Glitch Effect on top of your Videos.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" You will need an Image for the Glitch Pattern,")
        row = layout.row()
        row.label(text="  and you will also need to animate the Glitch")
        row = layout.row()
        row.label(text=" Movement.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.operator("glitch.addnodes", icon= 'HAND')
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        layout.label(text="_______________________________________________")

        #Sketch Effect UI

        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" Sketch Effect", icon= 'GPBRUSH_MARKER')
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" The Sketch Effect will take a Movie clip and")
        row = layout.row()
        row.label(text=" add a Sketch Effect which you can modify.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" You can also add the Paper Color Presets Node,")
        row = layout.row()
        row.label(text=" It will add another Node Group which contains,")
        row = layout.row()
        row.label(text=" some Color Presets.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.operator("sketch.addnodes", icon= 'GREASEPENCIL')
        row = layout.row()
        row.operator("colpre.addnodes", icon= 'PRESET')
        row = layout.row()
        row = layout.row()
        row = layout.row()
        layout.label(text="_______________________________________________")

        #Posterize effect UI

        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" Posterize Effect", icon= 'FCURVE_SNAPSHOT')
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" The Posterize Effect will take a Movie clip and")
        row = layout.row()
        row.label(text=" add a Posterize Effect which you can modify.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" Playing around with the Values and the blend")
        row = layout.row()
        row.label(text=" mode can give many different variations of")
        row = layout.row()
        row.label(text=" this effect.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" Select from the presets below.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.operator("post1.addnodes", icon= 'KEYTYPE_BREAKDOWN_VEC')
        row.operator("post2.addnodes", icon= 'KEYTYPE_MOVING_HOLD_VEC')
        row.operator("post3.addnodes", icon= 'KEYTYPE_JITTER_VEC')
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        layout.label(text="_______________________________________________")

        #Ink Drop Effect UI

        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" Ink Drop Effect", icon= 'MOD_FLUIDSIM')
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text=" The Ink Drop Effect will take a Smoke Movie")
        row = layout.row()
        row.label(text=" Clip and a black and white Text Image, to")
        row = layout.row()
        row.label(text=" create the effect.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.operator("inkdr2.addnodes", icon= 'PMARKER_SEL')
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        layout.label(text="_______________________________________________")

        row = layout.row()
        row = layout.row()






    #register and unregister
def register():
    bpy.utils.register_class(EyeColOP)
    bpy.utils.register_class(LayoutPanel)
    bpy.utils.register_class(SciFiEyeOP)
    bpy.utils.register_class(PatchOP)
    bpy.utils.register_class(GlitchOP)
    bpy.utils.register_class(SketchOP)
    bpy.utils.register_class(Post1OP)
    bpy.utils.register_class(Post2OP)
    bpy.utils.register_class(Post3OP)
    bpy.utils.register_class(Inkdrop2)
    bpy.utils.register_class(ColpreOP)
    bpy.utils.register_class(CloneOP)




def unregister():
    bpy.utils.unregister_class(EyeColOP)
    bpy.utils.unregister_class(LayoutPanel)
    bpy.utils.unregister_class(SciFiEyeOP)
    bpy.utils.unregister_class(PatchOP)
    bpy.utils.unregister_class(GlitchOP)
    bpy.utils.unregister_class(SketchOP)
    bpy.utils.unregister_class(Post1OP)
    bpy.utils.unregister_class(Post2OP)
    bpy.utils.unregister_class(Post3OP)
    bpy.utils.unregister_class(Inkdrop2)
    bpy.utils.unregister_class(ColpreOP)
    bpy.utils.unregister_class(CloneOP)






if __name__ == "__main__":
    register()




