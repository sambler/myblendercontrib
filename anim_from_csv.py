import bpy

action="default"
text=action + ".txt"

obj_map = {}

target_map = { "Root" : 0, "Spine" : 1, "ArmFK.L" : 3, "LegIK.L" : 4, "Fingers.L" : 6, 
                "Links.L" : 7, "ArmFK.R" : 19, "LegIK.R" : 20, "Fingers.R" :22, "Links.R" : 23 } 

macros = { "Hand.L": ["Fingers.L", "Links.L"],
           "Hand.R": [ "Fingers.R", "Links.R" ],
           "All":  ["Spine","ArmFK.L","ArmFK.R","LegIK.L","LegIK.R","Links.R","Fingers.R","Links.L","Fingers.L"],
           "Stance": ["Spine","Root","LegIK.L","LegIK.R"],
           "Arm.L": ["ArmFK.L","Links.L","Fingers.L"],
           "Arm.R": ["ArmFK.R","Links.R","Fingers.R"] }
            
def get_pose_index(obj, pose_name ):
    idx = 0
    for pm in obj.pose_library.pose_markers:
        if pose_name == pm.name:
            return idx
        idx += 1
    return None

def build_layers(targets):
    layers = [False]*32
    print( targets )
    for t in targets:
        if t in target_map:
            layers[target_map[ t ] ] = True
    return tuple( layers )
    
def build_layers2(targets):
    for i in range(32):
        bpy.context.object.data.layers[i] = False
    for t in targets:
        if t in target_map:
            layer_id=target_map[ t ]
            bpy.context.object.data.layers[ layer_id ] = True

def apply( obj, targets, pose_name):
    idx = get_pose_index( obj, pose_name )
    if idx is None:
        print("pose %s not found." % pose_name )
        return
    sel_layers = build_layers( targets )
    print("sellayers=" + str(sel_layers))
    bpy.ops.armature.armature_layers(layers=sel_layers) # 2.7 api, alternatively build_layers2 can be used
    bpy.ops.poselib.apply_pose(pose_index=idx)    
    bpy.ops.pose.select_all(action='SELECT')   
    if "Root" in targets:
        bpy.ops.anim.keyframe_insert(type='BUILTIN_KSI_LocRot')
    else:
        bpy.ops.anim.keyframe_insert(type='Rotation')
    

def remove_dummy():
    for key, value in obj_map.items() :
        print (key, value)
        bpy.context.scene.objects.active = obj
        obj.select = True  
        bpy.ops.armature.armature_layers(layers=[True]*32)
        bpy.context.scene.frame_set( 0 ) 
        bpy.ops.anim.keyframe_delete(type='BUILTIN_KSI_LocRot', confirm_success=True)
        bpy.ops.armature.armature_layers(layers=[False]*32)
        
def add_dummy( obj_name ):
    # set dummy keyframe to create an action 8.7.2014
    sel_layers = build_layers( ['Root'] )
    obj = bpy.data.objects.get( obj_name  )
    if obj == None:
        print("obj name=" + obj_name + " not found.")
        return
    bpy.context.scene.frame_set( 0 ) 
    obj.animation_data.action.name = action + '_' + obj_name    
    bpy.context.scene.objects.active = obj
    obj.select = True         
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.anim.keyframe_insert(type='Rotation')
       


txt = bpy.data.texts[ text ].as_string()
for line in txt.splitlines():
    if line.find(" ") != -1 and line.find("#") == -1:
        sframe,rig_and_poses= line.split(" ")
        rest=rig_and_poses.split(":")
        print("frame :%s" % sframe )
        obj_name=rest[0]
        poses=rest[1]
        pose_list=poses.split(",")
        if obj_name.upper() == "SET":
            var,obj_name = pose_list[0].split('=')
            obj_map[var]=obj_name
            print( obj_map )
            add_dummy( obj_name )
            continue
        
        bpy.context.scene.frame_set( int( sframe ))
        for assignment in pose_list:
            bone_group_name,pose_name=assignment.split("=")
            if bone_group_name in macros:
                targets = macros[ bone_group_name ]  
            else:
                 targets = [ bone_group_name ]
            obj = bpy.data.objects.get( obj_map[ obj_name])
            if obj == None:
                print("obj name=" + obj_name + " not found.")
                break
            bpy.context.scene.objects.active = obj
            obj.select = True  
            bpy.ops.object.mode_set(mode = 'POSE')  
            print("assign obj:%s bone_group:%s, pose:%s" % (obj, bone_group_name, pose_name))
            apply(  obj, targets, pose_name)

remove_dummy()
