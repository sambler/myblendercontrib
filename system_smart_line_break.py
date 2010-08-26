#  ***** GPL LICENSE BLOCK ***** 
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****

bl_addon_info={
    "name":"Text Editor: Smart Line Break",
    "author":"Chris Foster (Kira Vakaan)",
    "version":"1.0 2010/5/20",
    "blender":(2,5,3),
    "location":"Text Editor",
    "description":"Enables Smart Tabs (Auto-indents new lines)",
    'url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/' \
        'Scripts/Text/Smart_Tabs',
    "category":"System"}

#Please send questions or comments to:
#cdbfoster@gmail.com

import bpy
from bpy.props import *

class SmartLineBreak(bpy.types.Operator):
    """Add a new text line using smart tabs"""

    bl_idname="text.smart_line_break"
    bl_label="Smart Line Break"

    def execute(self,context):
        #If not using tabs_as_spaces, perform the old functionality
        if not bpy.context.space_data.text.tabs_as_spaces:
            bpy.ops.text.line_break()
            return {"FINISHED"}
        #Get the current line to break from
        CurrentLine=bpy.context.space_data.text.current_line.line
        Whitespace=""
        #Store each character of whitespace at the beginning of the line in Whitespace
        for Letter in CurrentLine:
            if Letter!=" ":
                break
            Whitespace+=" "
        #Get rid of the whitespace
        CurrentLine=CurrentLine.strip()
        #Unindent after lines that start with...
        if CurrentLine.startswith(("return","break","continue")):
            Whitespace=" "*(bpy.context.space_data.tab_width*((len(Whitespace)//bpy.context.space_data.tab_width)-1))
        #Indent after lines that end with...
        if CurrentLine.endswith(":"):
            Whitespace=" "*(bpy.context.space_data.tab_width*((len(Whitespace)//bpy.context.space_data.tab_width)+1))
        #Add the new line character and the whitespace
        bpy.ops.text.insert(text="\n")
        bpy.ops.text.insert(text=Whitespace)
        return {"FINISHED"}

def register():
    
    #Getting the key item by its index seems like a bit of a hack...
    #Does anyone know a better way?
    Item=bpy.context.manager.keyconfigs["Blender"].keymaps["Text"].item_from_id(59)
    Item.idname="text.smart_line_break"

def unregister():
    Item=bpy.context.manager.keyconfigs["Blender"].keymaps["Text"].item_from_id(59)
    Item.idname="text.line_break"
    
    
if __name__=="__main__":
    register()