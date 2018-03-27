from .snapping_utils import *
from .driver_utils import split_path
from .insert_keyframe import insert_keyframe


def snap_ik_fk(rig,way,switch_prop,
                    FK_root,FK_tip,
                    IK_last,IK_tip,IK_pole,
                    IK_stretch_last = None,
                    FK_mid=None,
                    full_snapping=True,
                    invert=False,
                    ik_fk_layer=None,
                    auto_switch=True):

    armature = rig.data
    poseBone = rig.pose.bones
    dataBone = rig.data.bones

    switch_bone,switch_prop_name = split_path(switch_prop)

    for c in IK_last.constraints :
        if c.type == 'IK':
            ik_len = c.chain_count
            break

    if not FK_mid :
        FK_mid = FK_tip.parent_recursive[:ik_len-1].reverse()

    IK_chain = ([IK_last]+IK_last.parent_recursive[:ik_len-1])[::-1]
    IK_root = IK_chain[0]
    FK_chain = ([FK_root]+FK_mid)[-ik_len:]

    if IK_stretch_last :
        IK_stretch_chain = ([IK_stretch_last]+IK_stretch_last.parent_recursive[:ik_len-1])[::-1]
        print('#### IK_stretch_chain',[b.name for b in IK_stretch_chain])
        print('')


    print('#### IK_chain',[b.name for b in IK_chain])
    #print(IK_stretch_chain)
    print('')
    print('#### FK_chain',[b.name for b in FK_chain])

    #######FK2IK
    if way == 'to_FK' :
        for i,FK_bone in enumerate(FK_chain) :
            if IK_stretch_last :
                match_bone = IK_stretch_chain[i]
            else :
                match_bone = IK_chain[i]

            match_matrix(FK_bone,match_bone)
            print('match',FK_bone,'to',match_bone)

        FK_tip.matrix = IK_tip.matrix
        FK_tip.location = (0,0,0)
        bpy.ops.pose.visual_transform_apply()
        #Rigify support
        if FK_root.get('stretch_length'):
            FK_root['stretch_length'] = IK_root.length/IK_root.bone.length

        invert_switch = invert*1.0

        if ik_fk_layer :
            layer_hide = ik_fk_layer[1]
            layer_show = ik_fk_layer[0]

        dataBone.active = FK_root.bone


    #######IK2FK
    elif way == 'to_IK' :
        #mute IK constraint
        for c in IK_last.constraints :
            if c.type == 'IK' :
                c.mute = True

        IK_tip.matrix = FK_tip.matrix
        bpy.ops.pose.visual_transform_apply()

        if full_snapping :
            for i,IK_bone in enumerate(IK_chain) :
                match_matrix(IK_bone,FK_chain[i])

        for c in IK_last.constraints :
            if c.type == 'IK' :
                c.mute = False
        bpy.ops.pose.visual_transform_apply()

        #else :
        match_pole_target(IK_chain[0],IK_last,IK_pole,FK_chain[0],(IK_root.length+IK_last.length))
        bpy.ops.pose.visual_transform_apply()


        invert_switch = (not invert)*1.0
        #setattr(IKFK_chain,'layer_switch',0)

        dataBone.active = IK_tip.bone

        if ik_fk_layer :
            layer_hide = ik_fk_layer[0]
            layer_show = ik_fk_layer[1]

    if ik_fk_layer and auto_switch:
        setattr(poseBone.get(switch_bone),'["%s"]'%switch_prop_name,invert_switch)

        rig.data.layers[layer_hide] = False
        rig.data.layers[layer_show] = True

    ###settings keyframe_points
    keyBone = (FK_root,FK_tip,IK_tip,IK_pole)

    if bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        if not rig.animation_data:
            rig.animation_data_create()

        rig.keyframe_insert(data_path=switch_prop,group=switch_bone)

        for b in keyBone :
            insert_keyframe(b)
        for b in FK_mid :
            insert_keyframe(b)
        #for b in IK_mid :
    #        insert_keyframe(b)
