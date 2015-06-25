# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# PEP8 compliant (https://www.python.org/dev/peps/pep-0008)

# ----------------------------------------------------------
# File: measureit_main.py
# Main panel for different Measureit general actions
# Author: Antonio Vazquez (antonioya)
#
# ----------------------------------------------------------
# noinspection PyUnresolvedReferences
import bpy
# noinspection PyUnresolvedReferences
import bmesh
from measureit_tools import *
# noinspection PyUnresolvedReferences
from bpy.app.handlers import persistent


# ------------------------------------------------------
# Handler to detect new Blend load
#
# ------------------------------------------------------
# noinspection PyUnusedLocal
@persistent
def load_handler(dummy):
    RunHintDisplayButton.handle_remove(None, bpy.context)


# ------------------------------------------------------
# Handler to detect save Blend
# Clear not used measured
#
# ------------------------------------------------------
# noinspection PyUnusedLocal
@persistent
def save_handler(dummy):
    # noinspection PyBroadException
    try:
        print("MeasureIt: Cleaning data")
        objlist = bpy.context.scene.objects
        for myobj in objlist:
            if 'MeasureGenerator' in myobj:
                mp = myobj.MeasureGenerator[0]
                x = 0
                for ms in mp.measureit_segments:
                    ms.name = "segment_" + str(x)
                    x += 1
                    if ms.glfree is True:
                        idx = mp.measureit_segments.find(ms.name)
                        if idx > -1:
                            print("MeasureIt: Removed segment not used")
                            mp.measureit_segments.remove(idx)

                # reset size
                mp.measureit_num = len(mp.measureit_segments)
    except:
        pass
bpy.app.handlers.load_post.append(load_handler)
bpy.app.handlers.save_pre.append(save_handler)


# ------------------------------------------------------------------
# Define property group class for measureit data
# ------------------------------------------------------------------
class MeasureitProperties(bpy.types.PropertyGroup):
    gltype = bpy.props.IntProperty(name="gltype",
                                   description="Measure type (1-Segment, 2-Label, etc..)", default=1)
    glpointa = bpy.props.IntProperty(name="glpointa",
                                     description="Hidden property for opengl")
    glpointb = bpy.props.IntProperty(name="glpointb",
                                     description="Hidden property for opengl")
    glpointc = bpy.props.IntProperty(name="glpointc",
                                     description="Hidden property for opengl")
    glcolor = bpy.props.FloatVectorProperty(name="glcolor",
                                            description="Color for the measure",
                                            default=(0.173, 0.545, 1.0, 1.0),
                                            min=0.1,
                                            max=1,
                                            subtype='COLOR',
                                            size=4)
    glview = bpy.props.BoolProperty(name="glview",
                                    description="Measure visible/hide",
                                    default=True)
    glspace = bpy.props.FloatProperty(name='glspace', min=0, max=5, default=0.1,
                                      precision=3,
                                      description='Distance to display measure')
    glwidth = bpy.props.IntProperty(name='glwidth', min=1, max=10, default=1,
                                    description='line width')
    glfree = bpy.props.BoolProperty(name="glfree",
                                    description="This measure is free and can be deleted",
                                    default=False)
    gltxt = bpy.props.StringProperty(name="gltxt", maxlen=48,
                                     description="Short description")
    gladvance = bpy.props.BoolProperty(name="gladvance",
                                       description="Advanced options as line width or position",
                                       default=False)
    gldefault = bpy.props.BoolProperty(name="gldefault",
                                       description="Display measure in position calculated by default",
                                       default=True)
    glnormalx = bpy.props.FloatProperty(name="glnormalx",
                                        description="Change orientation in X axis",
                                        default=1, min=-1, max=1, precision=2)
    glnormaly = bpy.props.FloatProperty(name="glnormaly",
                                        description="Change orientation in Y axis",
                                        default=0, min=-1, max=1, precision=2)
    glnormalz = bpy.props.FloatProperty(name="glnormalz",
                                        description="Change orientation in Z axis",
                                        default=0, min=-1, max=1, precision=2)
    glfont_size = bpy.props.IntProperty(name="Text Size",
                                        description="Text size",
                                        default=14, min=10, max=150)
    gllink = bpy.props.StringProperty(name="gllink",
                                      description="linked object for linked measures")
    glocwarning = bpy.props.BoolProperty(name="glocwarning",
                                         description="Display a warning if some axis is not used in distance",
                                         default=True)
    glocx = bpy.props.BoolProperty(name="glocx",
                                   description="Include changes in X axis for calculating the distance",
                                   default=True)
    glocy = bpy.props.BoolProperty(name="glocy",
                                   description="Include changes in Y axis for calculating the distance",
                                   default=True)
    glocz = bpy.props.BoolProperty(name="glocz",
                                   description="Include changes in Z axis for calculating the distance",
                                   default=True)

# Register
bpy.utils.register_class(MeasureitProperties)


# ------------------------------------------------------------------
# Define object class (container of segments)
# Measureit
# ------------------------------------------------------------------
class MeasureContainer(bpy.types.PropertyGroup):
    measureit_num = bpy.props.IntProperty(name='Number of measures', min=0, max=1000, default=0,
                                          description='Number total of measureit elements')
    # Array
    measureit_segments = bpy.props.CollectionProperty(type=MeasureitProperties)


bpy.utils.register_class(MeasureContainer)
bpy.types.Object.MeasureGenerator = bpy.props.CollectionProperty(type=MeasureContainer)


# ------------------------------------------------------------------
# Define UI class
# Measureit
# ------------------------------------------------------------------
class MeasureitEditPanel(bpy.types.Panel):
    bl_idname = "measureit.editpanel"
    bl_label = "Measureit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MesureIt'

    # -----------------------------------------------------
    # Verify if visible
    # -----------------------------------------------------
    @classmethod
    def poll(cls, context):
        o = context.object
        if o is None:
            return False
        if 'MeasureGenerator' not in o:
            return False
        else:
            mp = context.object.MeasureGenerator[0]
            if mp.measureit_num > 0:
                return True
            else:
                return False

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    # noinspection PyUnusedLocal
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        if context.object is not None:
            if 'MeasureGenerator' in context.object:
                box = layout.box()
                row = box.row()
                row.label(context.object.name)
                row = box.row()
                row.prop(scene, 'measureit_gl_precision', text="Precision")
                row.prop(scene, 'measureit_units')
                row = box.row()
                row.prop(scene, 'measureit_gl_show_d', text="Measures")
                row.prop(scene, 'measureit_gl_show_n', text="Names")
                # Scale factor
                row = box.row()
                row.prop(scene, 'measureit_scale', text="Scale")
                if scene.measureit_scale is True:
                    row.prop(scene, 'measureit_scale_factor', text="1")
                    row.prop(scene, 'measureit_scale_precision', text="")
                    row.prop(scene, 'measureit_gl_scaletxt', text="")
                    row = box.row()
                    row.prop(scene, 'measureit_scale_color')
                    row.prop(scene, 'measureit_scale_font')
                    row = box.row()
                    row.prop(scene, 'measureit_scale_pos_x')
                    row.prop(scene, 'measureit_scale_pos_y')

                # Override
                row = box.row()
                row.prop(scene, 'measureit_ovr', text="Override")
                if scene.measureit_ovr is True:
                    row.prop(scene, 'measureit_ovr_color', text="")
                    row.prop(scene, 'measureit_ovr_font', text="Font")
                    row.prop(scene, 'measureit_ovr_width', text="Width")

                mp = context.object.MeasureGenerator[0]
                # -----------------
                # loop
                # -----------------
                if mp.measureit_num > 0:
                    box = layout.box()
                    for idx in range(0, mp.measureit_num):
                        if mp.measureit_segments[idx].glfree is False:
                            add_item(box, idx, mp.measureit_segments[idx])

                row = box.row()
                row.operator("measureit.deleteallsegmentbutton", text="Delete all", icon="X")


# -----------------------------------------------------
# Add segment to the panel.
# -----------------------------------------------------
def add_item(box, idx, segment):
    row = box.row(True)
    if segment.glview is True:
        icon = "VISIBLE_IPO_ON"
    else:
        icon = "VISIBLE_IPO_OFF"

    row.prop(segment, 'glview', text="", toggle=True, icon=icon)
    row.prop(segment, 'gladvance', text="", toggle=True, icon="MANIPUL")
    row.prop(segment, 'gltxt', text="")
    row.prop(segment, 'glcolor', text="")
    op = row.operator("measureit.deletesegmentbutton", text="", icon="X")
    op.tag = idx  # saves internal data
    if segment.gladvance is True:
        row = box.row(True)
        row.prop(segment, 'glspace', text="Distance")
        row.prop(segment, 'glfont_size', text="Font")
        row = box.row(True)
        row.prop(segment, 'glwidth', text="Line")
        row.prop(segment, 'gldefault', text="Automatic position")
        if segment.gldefault is False:
            row = box.row(True)
            row.prop(segment, 'glnormalx', text="X")
            row.prop(segment, 'glnormaly', text="Y")
            row.prop(segment, 'glnormalz', text="Z")
        # Loc axis
        row = box.row(True)
        row.prop(segment, 'glocx', text="X", toggle=True)
        row.prop(segment, 'glocy', text="Y", toggle=True)
        row.prop(segment, 'glocz', text="Z", toggle=True)
        if segment.glocx is False or segment.glocy is False or segment.glocz is False:
            row = box.row()
            row.prop(segment, 'glocwarning', text="Display warning")


# ------------------------------------------------------------------
# Define panel class for main functions.
# ------------------------------------------------------------------
class MeasureitMainPanel(bpy.types.Panel):
    bl_idname = "measureit_main_panel"
    bl_label = "Measureit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "TOOLS"
    bl_category = 'Measureit'

    # ------------------------------
    # Draw UI
    # ------------------------------
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # ------------------------------
        # Tool Buttons
        # ------------------------------
        box = layout.box()
        box.label("Tools", icon='MODIFIER')
        row = box.row()
        row.operator("measureit.addsegmentbutton", text="Segment", icon="ALIGN")
        row.operator("measureit.addanglebutton", text="Angle", icon="LINCURVE")
        row.operator("measureit.addlabelbutton", text="Label", icon="FONT_DATA")
        row = box.row()
        row.operator("measureit.addlinkbutton", text="Link", icon="ROTATECENTER")
        row.operator("measureit.addoriginbutton", text="Origin", icon="CURSOR")
        row = box.row()
        row.prop(scene, "measureit_gl_txt", text="Text")
        row = box.row()
        row.prop(scene, "measureit_default_color", text="")
        row.prop(scene, "measureit_hint_space")
        row = box.row()
        row.prop(scene, "measureit_font_size")

        # ------------------------------
        # Display Buttons
        # ------------------------------
        row = box.row()
        if context.window_manager.measureit_run_opengl is False:
            icon = 'PLAY'
            txt = 'Show'
        else:
            icon = "PAUSE"
            txt = 'Hide'
        row.operator("measureit.runopenglbutton", text=txt, icon=icon)
        row.prop(scene, "measureit_gl_ghost", text="", icon='GHOST_ENABLED')


# -------------------------------------------------------------
# Defines button for add a measure segment
#
# -------------------------------------------------------------
class AddSegmentButton(bpy.types.Operator):
    bl_idname = "measureit.addsegmentbutton"
    bl_label = "Add"
    bl_description = "(EDITMODE only) Add a new measure segment (select 2 vertices or more. Do no use loop selection)"
    bl_category = 'Measureit'

    # ------------------------------
    # Poll
    # ------------------------------
    @classmethod
    def poll(cls, context):
        o = context.object
        if o is None:
            return False
        else:
            if o.type == "MESH":
                if bpy.context.mode == 'EDIT_MESH':
                    return True
                else:
                    return False
            else:
                return False

    # ------------------------------
    # Execute button action
    # ------------------------------
    def execute(self, context):
        if context.area.type == 'VIEW_3D':
            # Add properties
            scene = context.scene
            mainobject = context.object
            mylist = get_smart_selected(mainobject)
            if len(mylist) < 2:  # if not selected linked vertex
                mylist = get_selected_vertex(mainobject)

            if len(mylist) >= 2:
                if 'MeasureGenerator' not in mainobject:
                    mainobject.MeasureGenerator.add()

                mp = mainobject.MeasureGenerator[0]
                for x in range(0, len(mylist) - 1, 2):
                    # -----------------------
                    # Only if not exist
                    # -----------------------
                    if exist_segment(mp, mylist[x], mylist[x + 1]) is False:
                        # Create all array elements
                        for cont in range(len(mp.measureit_segments) - 1, mp.measureit_num):
                            mp.measureit_segments.add()

                        # Set values
                        ms = mp.measureit_segments[mp.measureit_num]
                        ms.gltype = 1
                        ms.glpointa = mylist[x]
                        ms.glpointb = mylist[x + 1]
                        # color
                        ms.glcolor = scene.measureit_default_color
                        # dist
                        ms.glspace = scene.measureit_hint_space
                        # text
                        ms.gltxt = scene.measureit_gl_txt
                        ms.glfont_size = scene.measureit_font_size
                        # Add index
                        mp.measureit_num += 1

                # redraw
                context.area.tag_redraw()
                return {'FINISHED'}
            else:
                self.report({'ERROR'},
                            "MeasureIt: Select at least two vertices for creating measure segment. "
                            "Do no use loop select")
                return {'FINISHED'}
        else:
            self.report({'WARNING'},
                        "View3D not found, cannot run operator")

        return {'CANCELLED'}


# -------------------------------------------------------------
# Defines button for add a arngle
#
# -------------------------------------------------------------
class AddAngleButton(bpy.types.Operator):
    bl_idname = "measureit.addanglebutton"
    bl_label = "Angle"
    bl_description = "(EDITMODE only) Add a new angle measure (select 3 vertices, 2nd is angle vertex)"
    bl_category = 'Measureit'

    # ------------------------------
    # Poll
    # ------------------------------
    @classmethod
    def poll(cls, context):
        o = context.object
        if o is None:
            return False
        else:
            if o.type == "MESH":
                if bpy.context.mode == 'EDIT_MESH':
                    return True
                else:
                    return False
            else:
                return False

    # ------------------------------
    # Execute button action
    # ------------------------------
    def execute(self, context):
        if context.area.type == 'VIEW_3D':
            # Add properties
            scene = context.scene
            mainobject = context.object
            mylist = get_selected_vertex_history(mainobject)
            if len(mylist) == 3:
                if 'MeasureGenerator' not in mainobject:
                    mainobject.MeasureGenerator.add()

                mp = mainobject.MeasureGenerator[0]
                # -----------------------
                # Only if not exist
                # -----------------------
                if exist_segment(mp, mylist[0], mylist[1], 9, mylist[2]) is False:
                    # Create all array elements
                    for cont in range(len(mp.measureit_segments) - 1, mp.measureit_num):
                        mp.measureit_segments.add()

                    # Set values
                    ms = mp.measureit_segments[mp.measureit_num]
                    ms.gltype = 9
                    ms.glpointa = mylist[0]
                    ms.glpointb = mylist[1]
                    ms.glpointc = mylist[2]
                    # color
                    ms.glcolor = scene.measureit_default_color
                    # dist
                    ms.glspace = scene.measureit_hint_space
                    # text
                    ms.gltxt = scene.measureit_gl_txt
                    ms.glfont_size = scene.measureit_font_size
                    # Add index
                    mp.measureit_num += 1

                # redraw
                context.area.tag_redraw()
                return {'FINISHED'}
            else:
                self.report({'ERROR'},
                            "MeasureIt: Select three vertices for creating angle measure")
                return {'FINISHED'}
        else:
            self.report({'WARNING'},
                        "View3D not found, cannot run operator")

        return {'CANCELLED'}


# -------------------------------------------------------------
# Defines button for add a label segment
#
# -------------------------------------------------------------
class AddLabelButton(bpy.types.Operator):
    bl_idname = "measureit.addlabelbutton"
    bl_label = "Add"
    bl_description = "(EDITMODE only) Add a new measure label (select 1 vertex)"
    bl_category = 'Measureit'

    # ------------------------------
    # Poll
    # ------------------------------
    @classmethod
    def poll(cls, context):
        o = context.object
        if o is None:
            return False
        else:
            if o.type == "MESH":
                if bpy.context.mode == 'EDIT_MESH':
                    return True
                else:
                    return False
            else:
                return False

    # ------------------------------
    # Execute button action
    # ------------------------------
    def execute(self, context):
        if context.area.type == 'VIEW_3D':
            # Add properties
            scene = context.scene
            mainobject = context.object
            mylist = get_selected_vertex(mainobject)
            if len(mylist) == 1:
                if 'MeasureGenerator' not in mainobject:
                    mainobject.MeasureGenerator.add()

                mp = mainobject.MeasureGenerator[0]
                # -----------------------
                # Only if not exist
                # -----------------------
                if exist_segment(mp, mylist[0], mylist[0], 2) is False:  # Both equal
                    # Create all array elements
                    for cont in range(len(mp.measureit_segments) - 1, mp.measureit_num):
                        mp.measureit_segments.add()

                    # Set values
                    ms = mp.measureit_segments[mp.measureit_num]
                    ms.gltype = 2
                    ms.glpointa = mylist[0]
                    ms.glpointb = mylist[0]  # Equal
                    # color
                    ms.glcolor = scene.measureit_default_color
                    # dist
                    ms.glspace = scene.measureit_hint_space
                    # text
                    ms.gltxt = scene.measureit_gl_txt
                    ms.glfont_size = scene.measureit_font_size
                    # Add index
                    mp.measureit_num += 1

                # redraw
                context.area.tag_redraw()
                return {'FINISHED'}
            else:
                self.report({'ERROR'},
                            "MeasureIt: Select one vertex for creating measure label")
                return {'FINISHED'}
        else:
            self.report({'WARNING'},
                        "View3D not found, cannot run operator")

        return {'CANCELLED'}


# -------------------------------------------------------------
# Defines button for add a link
#
# -------------------------------------------------------------
class AddLinkButton(bpy.types.Operator):
    bl_idname = "measureit.addlinkbutton"
    bl_label = "Add"
    bl_description = "(OBJECT mode only) Add a new measure between objects (select 2 " \
                     "objects and optionally 1 or 2 vertices)"
    bl_category = 'Measureit'

    # ------------------------------
    # Poll
    # ------------------------------
    @classmethod
    def poll(cls, context):
        o = context.object
        if o is None:
            return False
        else:
            if o.type == "MESH" or o.type == "EMPTY" or o.type == "CAMERA" or o.type == "LAMP":
                if bpy.context.mode == 'OBJECT':
                    return True
                else:
                    return False
            else:
                return False

    # ------------------------------
    # Execute button action
    # ------------------------------
    def execute(self, context):
        if context.area.type == 'VIEW_3D':
            scene = context.scene
            mainobject = context.object
            # -------------------------------
            # Verify number of objects
            # -------------------------------
            if len(context.selected_objects) != 2:
                self.report({'ERROR'},
                            "MeasureIt: Select two objects only, and optionally 1 vertex or 2 vertices "
                            "(one of each object)")
                return {'FINISHED'}
            # Locate other object
            linkobject = None
            for o in context.selected_objects:
                if o.name != mainobject.name:
                    linkobject = o.name
            # Verify destination vertex
            lkobj = bpy.data.objects[linkobject]
            mylinkvertex = get_selected_vertex(lkobj)
            if len(mylinkvertex) > 1:
                self.report({'ERROR'},
                            "MeasureIt: The destination object has more than one vertex selected. "
                            "Select only 1 or none")
                return {'FINISHED'}
            # Verify origin vertex
            myobjvertex = get_selected_vertex(mainobject)
            if len(mylinkvertex) > 1:
                self.report({'ERROR'},
                            "MeasureIt: The active object has more than one vertex selected. Select only 1 or none")
                return {'FINISHED'}

            # -------------------------------
            # Add properties
            # -------------------------------
            flag = False
            if 'MeasureGenerator' not in mainobject:
                mainobject.MeasureGenerator.add()

            mp = mainobject.MeasureGenerator[0]

            # if exist_segment(mp, mylist[0], mylist[0], 3) is False:
            #     flag = True
            # Create all array elements
            for cont in range(len(mp.measureit_segments) - 1, mp.measureit_num):
                mp.measureit_segments.add()

            # Set values
            ms = mp.measureit_segments[mp.measureit_num]
            # -----------------------
            # Vertex to Vertex
            # -----------------------
            if len(myobjvertex) == 1 and len(mylinkvertex) == 1:
                ms.gltype = 3
                ms.glpointa = myobjvertex[0]
                ms.glpointb = mylinkvertex[0]
                flag = True
            # -----------------------
            # Vertex to Object
            # -----------------------
            if len(myobjvertex) == 1 and len(mylinkvertex) == 0:
                ms.gltype = 4
                ms.glpointa = myobjvertex[0]
                ms.glpointb = 0
                flag = True
            # -----------------------
            # Object to Vertex
            # -----------------------
            if len(myobjvertex) == 0 and len(mylinkvertex) == 1:
                ms.gltype = 5
                ms.glpointa = 0
                ms.glpointb = mylinkvertex[0]
                flag = True
            # -----------------------
            # Object to Object
            # -----------------------
            if len(myobjvertex) == 0 and len(mylinkvertex) == 0:
                ms.gltype = 8
                ms.glpointa = 0
                ms.glpointb = 0  # Equal
                flag = True

            # ------------------
            # only if created
            # ------------------
            if flag is True:
                # color
                ms.glcolor = scene.measureit_default_color
                # dist
                ms.glspace = scene.measureit_hint_space
                # text
                ms.gltxt = scene.measureit_gl_txt
                ms.glfont_size = scene.measureit_font_size
                # link
                ms.gllink = linkobject
                # Add index
                mp.measureit_num += 1

                # -----------------------
                # Only if not exist
                # -----------------------
                # redraw
                context.area.tag_redraw()
                return {'FINISHED'}
        else:
            self.report({'WARNING'},
                        "View3D not found, cannot run operator")

        return {'CANCELLED'}


# -------------------------------------------------------------
# Defines button for add a origin segment
#
# -------------------------------------------------------------
class AddOriginButton(bpy.types.Operator):
    bl_idname = "measureit.addoriginbutton"
    bl_label = "Add"
    bl_description = "(OBJECT mode only) Add a new measure to origin (select object and optionally 1 vertex)"
    bl_category = 'Measureit'

    # ------------------------------
    # Poll
    # ------------------------------
    @classmethod
    def poll(cls, context):
        o = context.object
        if o is None:
            return False
        else:
            if o.type == "MESH" or o.type == "EMPTY" or o.type == "CAMERA" or o.type == "LAMP":
                if bpy.context.mode == 'OBJECT':
                    return True
                else:
                    return False
            else:
                return False

    # ------------------------------
    # Execute button action
    # ------------------------------
    def execute(self, context):
        if context.area.type == 'VIEW_3D':
            # Add properties
            scene = context.scene
            mainobject = context.object
            mylist = get_selected_vertex(mainobject)
            if 'MeasureGenerator' not in mainobject:
                mainobject.MeasureGenerator.add()

            mp = mainobject.MeasureGenerator[0]
            # Create all array elements
            for cont in range(len(mp.measureit_segments) - 1, mp.measureit_num):
                mp.measureit_segments.add()

            # -----------------------
            # Set values
            # -----------------------
            ms = mp.measureit_segments[mp.measureit_num]
            flag = False
            if len(mylist) > 0:
                if len(mylist) == 1:
                    if exist_segment(mp, mylist[0], mylist[0], 6) is False:  # Both equal
                        flag = True
                        # Vertex to origin
                        ms.gltype = 6
                        ms.glpointa = mylist[0]
                        ms.glpointb = mylist[0]
                else:
                    self.report({'ERROR'},
                                "MeasureIt: Enter in EDITMODE and select one vertex only for creating "
                                "measure from vertex to origin")
                    return {'FINISHED'}
            else:
                # Object to origin
                if exist_segment(mp, 0, 0, 7) is False:  # Both equal
                    flag = True
                    ms.gltype = 7
                    ms.glpointa = 0
                    ms.glpointb = 0
            # ------------------
            # only if created
            # ------------------
            if flag is True:
                # color
                ms.glcolor = scene.measureit_default_color
                # dist
                ms.glspace = scene.measureit_hint_space
                # text
                ms.gltxt = scene.measureit_gl_txt
                ms.glfont_size = scene.measureit_font_size
                # Add index
                mp.measureit_num += 1

            # redraw
            context.area.tag_redraw()

            return {'FINISHED'}
        else:
            self.report({'WARNING'},
                        "View3D not found, cannot run operator")

        return {'CANCELLED'}


# -------------------------------------------------------------
# Defines button for delete a measure segment
#
# -------------------------------------------------------------
class DeleteSegmentButton(bpy.types.Operator):
    bl_idname = "measureit.deletesegmentbutton"
    bl_label = "Delete"
    bl_description = "Delete a measure"
    bl_category = 'Measureit'
    tag = bpy.props.IntProperty()

    # ------------------------------
    # Execute button action
    # ------------------------------
    def execute(self, context):
        if context.area.type == 'VIEW_3D':
            # Add properties
            mainobject = context.object
            mp = mainobject.MeasureGenerator[0]
            ms = mp.measureit_segments[self.tag]
            ms.glfree = True
            # Delete element
            mp.measureit_segments.remove(self.tag)
            mp.measureit_num -= 1
            # redraw
            context.area.tag_redraw()
            return {'FINISHED'}
        else:
            self.report({'WARNING'},
                        "View3D not found, cannot run operator")

        return {'CANCELLED'}


# -------------------------------------------------------------
# Defines button for delete all measure segment
#
# -------------------------------------------------------------
class DeleteAllSegmentButton(bpy.types.Operator):
    bl_idname = "measureit.deleteallsegmentbutton"
    bl_label = "Delete"
    bl_description = "Delete all measures (it cannot be undone)"
    bl_category = 'Measureit'
    tag = bpy.props.IntProperty()

    # ------------------------------
    # Execute button action
    # ------------------------------
    def execute(self, context):
        if context.area.type == 'VIEW_3D':
            # Add properties
            mainobject = context.object
            mp = mainobject.MeasureGenerator[0]

            while len(mp.measureit_segments) > 0:
                mp.measureit_segments.remove(0)

            # reset size
            mp.measureit_num = len(mp.measureit_segments)
            # redraw
            context.area.tag_redraw()
            return {'FINISHED'}
        else:
            self.report({'WARNING'},
                        "View3D not found, cannot run operator")

        return {'CANCELLED'}


# -------------------------------------------------------------
# Defines button for enable/disable the tip display
#
# -------------------------------------------------------------
class RunHintDisplayButton(bpy.types.Operator):
    bl_idname = "measureit.runopenglbutton"
    bl_label = "Display hint data manager"
    bl_description = "Display aditional information in the viewport"
    bl_category = 'Measureit'

    _handle = None  # keep function handler

    # ----------------------------------
    # Enable gl drawing adding handler
    # ----------------------------------
    @staticmethod
    def handle_add(self, context):
        if RunHintDisplayButton._handle is None:
            RunHintDisplayButton._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context),
                                                                                  'WINDOW',
                                                                                  'POST_PIXEL')
            context.window_manager.measureit_run_opengl = True

    # ------------------------------------
    # Disable gl drawing removing handler
    # ------------------------------------
    # noinspection PyUnusedLocal
    @staticmethod
    def handle_remove(self, context):
        if RunHintDisplayButton._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(RunHintDisplayButton._handle, 'WINDOW')
        RunHintDisplayButton._handle = None
        context.window_manager.measureit_run_opengl = False

    # ------------------------------
    # Execute button action
    # ------------------------------
    def execute(self, context):
        if context.area.type == 'VIEW_3D':
            if context.window_manager.measureit_run_opengl is False:
                self.handle_add(self, context)
                context.area.tag_redraw()
            else:
                self.handle_remove(self, context)
                context.area.tag_redraw()

            return {'FINISHED'}
        else:
            self.report({'WARNING'},
                        "View3D not found, cannot run operator")

        return {'CANCELLED'}


# -------------------------------------------------------------
# Handler for drawing OpenGl
# -------------------------------------------------------------
# noinspection PyUnusedLocal
def draw_callback_px(self, context):
    draw_main(context)


# -------------------------------------------------------------
# Check if the segment already exist
#
# -------------------------------------------------------------
def exist_segment(mp, pointa, pointb, typ=1, pointc=None):
    #  for ms in mp.measureit_segments[mp.measureit_num]
    for ms in mp.measureit_segments:
        if ms.gltype == typ and ms.glfree is False:
            if typ != 9:
                if ms.glpointa == pointa and ms.glpointb == pointb:
                    return True
                if ms.glpointa == pointb and ms.glpointb == pointa:
                    return True
            else:
                if ms.glpointa == pointa and ms.glpointb == pointb and ms.glpointc == pointc:
                    return True

    return False


# -------------------------------------------------------------
# Get vertex selected
# -------------------------------------------------------------
def get_selected_vertex(myobject):
    mylist = []
    # if not mesh, no vertex
    if myobject.type != "MESH":
        return mylist
    # --------------------
    # meshes
    # --------------------
    oldobj = bpy.context.object
    bpy.context.scene.objects.active = myobject
    flag = False
    if myobject.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
        flag = True

    bm = bmesh.from_edit_mesh(myobject.data)
    tv = len(bm.verts)
    for v in bm.verts:
        if v.select:
            mylist.extend([v.index])

    if flag is True:
        bpy.ops.object.editmode_toggle()
    # Back context object
    bpy.context.scene.objects.active = oldobj

    # if select all vertices, then use origin
    if tv == len(mylist):
        return []

    return mylist


# -------------------------------------------------------------
# Get vertex selected
# -------------------------------------------------------------
def get_selected_vertex_history(myobject):
    mylist = []
    # if not mesh, no vertex
    if myobject.type != "MESH":
        return mylist
    # --------------------
    # meshes
    # --------------------
    oldobj = bpy.context.object
    bpy.context.scene.objects.active = myobject
    flag = False
    if myobject.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
        flag = True

    bm = bmesh.from_edit_mesh(myobject.data)
    for v in bm.select_history:
        mylist.extend([v.index])

    if flag is True:
        bpy.ops.object.editmode_toggle()
    # Back context object
    bpy.context.scene.objects.active = oldobj

    return mylist


# -------------------------------------------------------------
# Get vertex selected segments
# -------------------------------------------------------------
def get_smart_selected(myobject):
    mylist = []
    # if not mesh, no vertex
    if myobject.type != "MESH":
        return mylist
    # --------------------
    # meshes
    # --------------------
    oldobj = bpy.context.object
    bpy.context.scene.objects.active = myobject
    flag = False
    if myobject.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
        flag = True

    bm = bmesh.from_edit_mesh(myobject.data)
    for e in bm.edges:
        if e.select is True:
            mylist.extend([e.verts[0].index])
            mylist.extend([e.verts[1].index])

    if flag is True:
        bpy.ops.object.editmode_toggle()
    # Back context object
    bpy.context.scene.objects.active = oldobj

    return mylist
