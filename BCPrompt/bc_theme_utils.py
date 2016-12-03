import bpy

# leave untracked!

def do_nodeview_theme():
    current_theme = bpy.context.user_preferences.themes.items()[0][0]
    node_editor = bpy.context.user_preferences.themes[current_theme].node_editor

    types = """\
        color_node
        converter_node
        distor_node
        filter_node
        frame_node
        gp_vertex
        gp_vertex_select
        gp_vertex_size
        group_node
        group_socket_node
        input_node
        layout_node
        matte_node
        node_active
        node_backdrop
        node_selected
        noodle_curving
        output_node
        pattern_node
        script_node
        selected_text
        shader_node
        texture_node
        vector_node
        wire
        wire_inner
        wire_select
    """

    current_theme = bpy.context.user_preferences.themes.items()[0][0]
    node_editor = bpy.context.user_preferences.themes[current_theme].node_editor

    settings = """\
color_node         0.894117,1.0,0.7882353
converter_node     0.9098039865493774,1.0,0.960784375667572
distor_node        0.4549019932746887,0.5921568870544434,0.5921568870544434
filter_node        0.6784313917160034,0.6039215922355652,0.7529412508010864
frame_node         1.0,1.0,1.0,0.501960813999176
gp_vertex          0.0,0.0,0.0
gp_vertex_select   1.0,0.5215686559677124,0.0
group_node         0.5411764979362488,0.6117647290229797,0.572549045085907
group_socket_node  0.874509871006012,0.7921569347381592,0.20784315466880798
input_node         1.0,1.0,1.0
layout_node        0.6784313917160034,0.6039215922355652,0.7529412508010864
matte_node         0.5921568870544434,0.4549019932746887,0.4549019932746887
node_active        1.0,0.6666666865348816,0.250980406999588
node_selected      0.9450981020927429,0.3450980484485626,0.0
output_node        1.0,1.0,1.0
pattern_node       0.6784313917160034,0.6039215922355652,0.7529412508010864
script_node        0.6784313917160034,0.6039215922355652,0.7529412508010864
selected_text      0.7019608020782471,0.6117647290229797,0.6117647290229797
shader_node        0.6392157077789307,0.9098039865493774,1.0
texture_node       0.2392157018184662,0.9764706492424011,1.0
vector_node        0.6784313917160034,0.6039215922355652,0.7529412508010864
wire               1.0,1.0,1.0
wire_inner         1.0,1.0,1.0
wire_select        1.0,0.46274513006210327,0.0
    """

    for configurable in settings.split('\n'):
        if not configurable.strip():
            continue
        print(configurable)
        attr_name, attr_value = configurable.split()
        attr_floats = [float(i) for i in attr_value.split(',')]
        setattr(node_editor, attr_name, attr_floats)
