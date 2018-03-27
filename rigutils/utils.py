import bpy


def find_root(rig):
    for bone in rig.pose.bones :
        if bone.name in ['CTRL-root','root','ROOT','Root'] :
            return bone

    for bone in rig.pose.bones :
        if not bone.parent and not bone.constraints :
            return bone



def find_rig_users(rig) :
    users = []
    for ob in bpy.context.scene.objects :
        if ob.find_armature()== rig or ob.parent == rig and ob not in users:
            users.append(ob)

    return ob

def find_mirror(name) :
    mirror = None
    prop= False

    if name :

        if name.startswith('[')and name.endswith(']'):
            prop = True
            name= name[:-2][2:]

        match={
        'R' : 'L',
        'r' : 'l',
        'L' : 'R',
        'l' : 'r',
        }

        separator=['.','_']

        if name.startswith(tuple(match.keys())):
            if name[1] in separator :
                mirror = match[name[0]]+name[1:]

        if name.endswith(tuple(match.keys())):
            if name[-2] in separator :
                mirror = name[:-1]+match[name[-1]]

        if mirror and prop == True:
            mirror='["%s"]'%mirror

        return mirror

    else :
        return None


def mirror_path(dp) :
    bone = split_path(dp)[0]
    prop = split_path(dp)[1]

    mirror_bone = find_mirror(bone)

    if not mirror_bone :
        mirror_bone = bone

    if prop :
        mirror_prop = find_mirror(prop)

        if not mirror_prop :
            mirror_prop = prop

        mirror_data_path = dp.replace('["%s"]'%prop,'["%s"]'%mirror_prop)

    mirror_data_path = dp.replace('["%s"]'%bone,'["%s"]'%mirror_bone)



    if dp!= mirror_data_path :
        return mirror_data_path

    else :
        return None

def is_bone_protected(bone) :
    rig = bone.id_data

    protected_layer = [i for i,l in enumerate(rig.data.layers_protected) if l]
    bone_layer = [i for i,l in enumerate(bone.bone.layers) if l]

    if set(protected_layer)& set(bone_layer) :
        return True
    else :
        return False

def bone_constraints(bone) :
    constraints_info = {}

    for c in bone.constraints :
        constraints_info[c.name] ={}

        for attr in [prop.identifier for prop in c.bl_rna.properties] :
            constraints_info[c.name][attr] = getattr(c,attr)


    return constraints_info

def rig_info(rig) :
    info = {}

    for bone in rig.pose.bones :

        if not is_bone_protected(bone) :

            info[bone.name] = {}

            info[bone.name]['rotation_mode'] = bone.rotation_mode
            info[bone.name]['bone_group'] = bone.bone_group.name if bone.bone_group else ''
            info[bone.name]['constraints'] = bone_constraints(bone)

        #print(info[bone.name])
    return info
