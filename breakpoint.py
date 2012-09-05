# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>


bl_info = {
    "name": "BreakPoint",
    "description": "Breakpoint allows you to pause script execution and display variables values.",
    "author": "Christopher Barrett  (www.goodspiritgraphics.com)",
    "version": (2,0),
    "blender": (2, 6, 3),
    "api": 46461,
    "location": "Text Editor > Properties",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"
                "Scripts/Development/BreakPoint",
    "tracker_url": "http://projects.blender.org/tracker/index.php?"
                   "func=detail&aid=28802",
    "category": "Development"}


import bpy
import code
import traceback
import textwrap
from collections import OrderedDict
from bpy.props import BoolProperty
from bpy.props import IntProperty
from bpy.props import EnumProperty


class BreakPoint_Class:
    """ this class contains all variables concerning BreakPoint """

    def __init__(self):
        bpy.types.Scene.gsg1_mode = EnumProperty(attr='mode', name='bp_mode', items=(\
        ('enable', 'Enable', 'Enable all BreakPoint statements.'),\
        ('disable', 'Disable', "Disable all BreakPoint statements, and discontinue incrementing the 'BreakPoint' log counter.")), default='enable')
 
        bpy.types.Scene.gsg1_console_print = BoolProperty(name= "Print to Console", description = "Select to print 'BreakPoint' commands to the 'Console' window." , default = True)
        bpy.types.Scene.gsg1_panel_print = BoolProperty(name= "Print to Panel", description = "Select to print 'BreakPoint' commands to the 'BreakPoint' panel." , default = True)
        bpy.types.Scene.gsg1_log_print = BoolProperty(name= "Print to Log", description = "Select to print 'BreakPoint' commands to the log." , default = False)
        bpy.types.Scene.gsg1_ignore_pause = BoolProperty(name= "Ignore Pause", description = "Global setting to ignore all 'Pause' args in the 'BreakPoint' commands.  This stops 'BreakPoint' from pausing." , default = False)
        bpy.types.Scene.gsg1_ignore_print = BoolProperty(name= "Ignore Print", description = "Global setting to ignore all 'Prnt' args in the 'BreakPoint' commands.  This stops 'Breakpoint' from printing." , default = False)
        bpy.types.Scene.gsg1_update_panel = BoolProperty(name= "Update Panel", description = "Select to force Blender to update the 'BreakPoint' panel.  Slow, but it guarantees valid display of variable values." , default = True)
        bpy.types.Scene.gsg1_columns = IntProperty(name="Column Width", description = "Sets the number of characters to display on a single line." , min = 25 , max = 200 , default = 50)
        bpy.types.Scene.gsg1_display_help = BoolProperty(name= "Display Help", description = "Display 'BreakPoint' help info." , default = False)
        bpy.types.Scene.gsg1_double_space = BoolProperty(name= "Double Space", description = "Double-space lines between variables in both the 'BreakPoint_log' file, and in the console." , default = False)
        bpy.types.Scene.gsg1_wrap_text = BoolProperty(name= "Line Wrap", description = "Wrap text lines, and indent wrapped text in both the 'BreakPoint_log' file, and in the console." , default = True)

        #Create list type for variables.
        bpy.types.Scene.gsg1_variables_list = []


# Create the instance class for global variables.
gsg1bp = BreakPoint_Class()




class bp(bpy.types.Panel):
    bl_label = "BreakPoint"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_context = "WINDOW"

    done_once = False
    breakpoints = 0
	
	
    def draw(self, context):
        scn = bpy.context.scene
        #done_once = False

        layout = self.layout; 
        row = layout.row(align = True)
        row.prop(context.scene , "gsg1_mode", expand = True)
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.prop(context.scene , "gsg1_panel_print", toggle = True)
        row.prop(context.scene , "gsg1_console_print", toggle = True)
        row.prop(context.scene , "gsg1_log_print", toggle = True)
        row = layout.row()

        row = layout.row()
        row.prop(context.scene , "gsg1_update_panel")
        row.label("")
        row.operator("gsg1.clear_log")

        row = layout.row()
        row = layout.row()
        row = layout.row()

        row = layout.row()
        row.label("Overide:")

        #row = layout.row()
        row.prop(context.scene, "gsg1_ignore_pause")
        row.prop(context.scene, "gsg1_ignore_print")
        #row.label("")
        #row = layout.row()
        row = layout.row()

        row = layout.row()
        row.label("Print Format:")
        #row = layout.row()
        row.prop(context.scene, "gsg1_double_space")
        row.prop(context.scene, "gsg1_wrap_text")

        row = layout.row()
        row = layout.row()


        if scn.gsg1_display_help:
            #pic = 'QUESTION'
            box = layout.box()
            box.prop(context.scene,"gsg1_display_help", toggle = True)
            box.prop(context.scene,"gsg1_columns", slider = True)

            #box.label(" 'BreakPoint' Instructions:", icon=pic)

            help_text=[" To use 'BreakPoint', put the following line, without the quotes, at the top of your script:",
            "'breakpoint=bpy.types.bp.bp'",
            "----------------------------",
            "To set a breakpoint, insert the following line where you want to stop script execution, and display variable values:",
            "'breakpoint(DICTIONARY)'",
            "Replace the word 'DICTIONARY' above with any dictionary object: 'locals()' to display the local variables; or 'globals()' to display the global variables.",
            "You can also create you own dictionary object that contains select variables of interest.",
            "For example, to pass the variables 'apples' and 'oranges' to breakpoint, create a dictionary object like this: 'myDictionary={'apples':apples,'oranges':oranges}'",
            "Then, pass it to 'BreakPoint' like this:",
            "'breakpoint(myDictionary)'",
            "----------------------------",
            "BreakPoint can take two additional boolean args after the dictionary object.  The first arg, 'pause' is used to stop script execution.  Default = 'True'; The second arg, 'prnt' is used to print the dictionary object.  Default = 'True'.",
            "Example: 'breakpoint(locals(), False), this will print all the local variables within the function without pausing.",
            "----------------------------",
            "To continue script execution, after pausing at a breakPoint, type 'CTRL-Z' into the console if you are on Windows, and 'CTRL-D' into the console if you are on a 'Unix' operating system."]

            w = bpy.context.scene.gsg1_columns
            self.panel_wrap_text(help_text, box, w, help = True)
            box.label("")


        elif scn.gsg1_mode == 'enable':
            pic = 'CONSOLE'

            box = layout.box()
            box.prop(context.scene,"gsg1_display_help", toggle = True)
            box.prop(context.scene,"gsg1_columns", slider = True)

            if (scn.gsg1_panel_print == False) or (not self.done_once) or (bpy.types.Scene.gsg1_variables_list == []):
                box.label(text=" Output:", icon=pic)
                for i in range(1, 3):
                    box.label("")
            else:
                w = bpy.context.scene.gsg1_columns
                self.panel_wrap_text(bpy.types.Scene.gsg1_variables_list, box, w)
                box.label("")

        elif scn.gsg1_mode == 'disable':
            # 'Stop'
            pic = 'CANCEL'

            box = layout.box()
            box.prop(context.scene,"gsg1_display_help", toggle = True)
            box.label(text=" BreakPoint Disabled.", icon=pic)
            
            for i in range(1, 3):
                box.label("")


    #Process text to wrap according to user-setting, and create box labels.                        
    def panel_wrap_text(self, list, ui, text_width, help = False):
        if help:
            pic = 'QUESTION'
            indent = ""
        else:
            indent = "      "
            pic = 'CONSOLE'

        done_once = False
        for x in range(0,len(list)):
            el = textwrap.wrap(list[x], width = text_width, subsequent_indent = indent)
            for y in range(0,len(el)):
                if not done_once:
                    ui.label(text=el[y], icon=pic)
                    done_once = True
                else:
                    ui.label(text=el[y])

				
				
    def bp(dictionary = {}, pause = True, prnt = True):
        scn = bpy.context.scene
        bp.done_once = True


        if scn.gsg1_mode == 'disable':
            #User has disabled BreakPoint.
            return

        #Increment here so if 'disable' breakpoints won't be counted.
        bp.breakpoints += 1

        #Clear the list here so if 'prnt = False' nothing will be dispayed in the panel.
        bpy.types.Scene.gsg1_variables_list = []

        if (not prnt) or (scn.gsg1_ignore_print):
            return


        s = traceback.extract_stack()
        s = s[len(s)-2]
        strng = str(s)
        scrptPos = strng.rfind("\\")
        scrpt = strng[scrptPos + 1 : len(strng) - 1]
        lst = scrpt.split(",")
        scrpt = str(lst[0])
        scrpt = scrpt[0 : len(scrpt) - 1]

		
        #Print the line, object, and file from which 'Breakpoint' was called.
        text = "Breakpoint #" + str(bp.breakpoints) + " >>  Line: " + str(s[1]) + "  In: '" + str(s[2]) + "'  File: '" + scrpt + "'"
        bpy.types.Scene.gsg1_variables_list.append(text)


        if prnt and scn.gsg1_log_print:
            prepare_to_log()
            bpy.data.texts["BreakPoint_Log"].write("\n")
            bpy.data.texts["BreakPoint_Log"].write("=" * 80)


        if dictionary == {}:
            #Empty dictionary passed, so return globals as default.
            d = globals().copy()
        else:
            d = dictionary

        
        #Alphabetize by key.
        d_sorted_by_value = OrderedDict(sorted(d.items(), key=lambda x: x[0]))
        text = ""

        for items in d_sorted_by_value.keys():
            text = str(items) + " = " + str(d_sorted_by_value[items])
            bpy.types.Scene.gsg1_variables_list.append(text)

        print_to_log_wrap(bpy.types.Scene.gsg1_variables_list)
        print_to_console_wrap(bpy.types.Scene.gsg1_variables_list)


        #Necessary here to guarantee that the panel is updated after last variable.
        if scn.gsg1_panel_print:
            force_redraw()

        if pause and not(scn.gsg1_ignore_pause):
            text = "\n\nEnter 'CTRL-Z' to exit the console.  With Unix, use 'CTRL-D'\n"
            print_to_console(text)

            code.interact(local=d)

        return


		
class ClearLog(bpy.types.Operator):
    bl_idname = "gsg1.clear_log"
    bl_label = "Clear Log."
    bl_description = "This clears the 'Breakpoint_Log' file, and resets the Breakpoint counter."

    def execute(self, context):
        #Check exists with 'try' 
        prepare_to_log()
        #Empty the file.
        bpy.data.texts["BreakPoint_Log"].clear()
        #Reset counter.
        bp.breakpoints = 0

        return {'FINISHED'}

	

		
def prepare_to_log():
    try:
        #Move the cursor to the 'EOF'.
        bpy.data.texts["BreakPoint_Log"].write("")
        
    except:
        #Text file doesn't exist, so create it.
        bpy.data.texts.new(name='BreakPoint_Log')


def print_to_log(text):
    if bpy.context.scene.gsg1_log_print:
        bpy.data.texts["BreakPoint_Log"].write("\n" + text)
		
#Process text to wrap, and print it to the log.                        
def print_to_log_wrap(list):
    if bpy.context.scene.gsg1_log_print:
        for x in range(0,len(list)):
            if x == 1: bpy.data.texts["BreakPoint_Log"].write("\n")

            if bpy.context.scene.gsg1_wrap_text:
                el = textwrap.wrap(list[x], width = 80, subsequent_indent = "    ")
                for y in range(0,len(el)):
                    bpy.data.texts["BreakPoint_Log"].write("\n" + el[y])
            else:
                bpy.data.texts["BreakPoint_Log"].write("\n" + list[x])

            if bpy.context.scene.gsg1_double_space:
                bpy.data.texts["BreakPoint_Log"].write("\n")

        bpy.data.texts["BreakPoint_Log"].write("\n")

			
def print_to_console(text):
    if bpy.context.scene.gsg1_console_print:
        print(text)

#Process text to wrap, and print it to the console.
def print_to_console_wrap(list):
    if bpy.context.scene.gsg1_console_print:
        print()
        if bpy.context.scene.gsg1_update_panel: print()

        for x in range(0,len(list)):
            if x == 1: print()

            if bpy.context.scene.gsg1_wrap_text:
                el = textwrap.wrap(list[x], width = 75, subsequent_indent = "    ")
                for y in range(0,len(el)):
                    print(el[y])
            else:
                print(list[x])

            if bpy.context.scene.gsg1_double_space:
                print() 

        print()
        if bpy.context.scene.gsg1_update_panel: print()

		
def force_redraw():
    if bpy.context.scene.gsg1_update_panel:
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)


#registration is necessary for the script to appear in the GUI
def register():
    bpy.utils.register_class(bp)
    bpy.utils.register_class(ClearLog)

def unregister():
    bpy.utils.unregister_class(bp)
    bpy.utils.register_class(ClearLog)

if __name__ == '__main__':
    register()
