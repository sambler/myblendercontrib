def split_path(path) :
    try :
        bone_name = path.split('["')[1].split('"]')[0]

    except :
        bone_name = None

    try :
        prop_name = path.split('["')[2].split('"]')[0]
    except :
        prop_name = None

    return bone_name,prop_name
