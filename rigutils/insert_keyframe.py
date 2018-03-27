import bpy

def insert_keyframe(bone,custom_prop=True):
    """ Insert Keyframe on selected_bones channel except for the locked one,
        insert key in custom prop to.
    """
    ob = bpy.context.object

    Transforms ={"location":("lock_location[0]","lock_location[1]","lock_location[2]"),
        "scale":("lock_scale[0]","lock_scale[1]","lock_scale[2]")}

    if bone.rotation_mode in 'QUATERNION':
        Transforms["rotation_quaternion"] = ("lock_rotation[0]","lock_rotation[1]","lock_rotation[2]","lock_rotation_w")
    elif bone.rotation_mode == 'AXIS_ANGLE':
        Transforms["rotation_axis_angle"] = ("lock_rotation[0]","lock_rotation[1]","lock_rotation[2]","lock_rotation_w")
    else :
        Transforms["rotation_euler"]=("lock_rotation[0]","lock_rotation[1]","lock_rotation[2]")

    if not ob.animation_data:
        ob.animation_data_create()

    for prop,lock in Transforms.items() :
        for index,channel in enumerate(lock) :
            #if the channel is not locked
            if not eval("bone."+channel) :
                ob.keyframe_insert(data_path = 'pose.bones["%s"].%s'%(bone.name,prop), index = index,group = bone.name)

        if custom_prop == True :
            for key,value in bone.items() :
                if key != '_RNA_UI' and key and type(value) in (int,float):
                    ob.keyframe_insert(data_path = 'pose.bones["%s"]["%s"]'%(bone.name,key) ,group = bone.name)

    for area in bpy.context.screen.areas :
        area.tag_redraw()
