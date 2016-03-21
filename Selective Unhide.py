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

import bpy


bl_info = {
    "name": "Selective Unhide",
    "description": "Selectively unhide objects instead of unhiding all objects at once",
    "author": "Ray Mairlot",
    "version": (1, 0),
    "blender": (2, 76, 0),
    "location": "3D View> Alt + H",
    "category": "3D View"}



def getHiddenObjects():
    
    return [object for object in bpy.context.scene.objects if object.hide]



def getHiddenGroups():
    
    #Possible, but not very readable
    #hiddenGroups = [group.name for hiddenObject in hiddenObjects if hiddenObject.name in group.objects and group.name not in hiddenGroups]
    
    hiddenObjects = getHiddenObjects()
    
    hiddenGroups = []
                    
    for group in bpy.data.groups:
        
        for hiddenObject in hiddenObjects:

            if hiddenObject.name in group.objects and group not in hiddenGroups:
                
                hiddenGroups.append(group)
                
    return hiddenGroups
    


def getHiddenItems(scene, context):
        
    hiddenGroups = [(item.name, item.name, "Group") for item in getHiddenGroups()]
    
    hiddenObjects = [(item.name, item.name, "Object") for item in getHiddenObjects()]

    return hiddenObjects + hiddenGroups



class UnhideSearch(bpy.types.Operator):
    """Search through a list of hidden items"""
    bl_idname = "object.unhide_search"
    bl_label = "Hidden Items"
    bl_property = "hiddenItems"

    hiddenItems = bpy.props.EnumProperty(name="Hidden Items", description="Holds a list of the hidden items", items=getHiddenItems)

    def execute(self, context):
        
        allHiddenItems = getHiddenItems(context.scene, context)
        
        for item in allHiddenItems:
            
            if item[0] == self.hiddenItems:
                
                itemType = item[2]
                                                  
        bpy.ops.object.show(type=itemType, itemName=self.hiddenItems)
            
        return {'FINISHED'}


    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}



class UnhideObject(bpy.types.Operator):
    """Unhide the object or group of objects"""
    bl_idname = "object.show"
    bl_label = "Show a specific object or group"
    bl_options = {"INTERNAL"}

    itemName = bpy.props.StringProperty()
    type = bpy.props.StringProperty()
    unHideAll = bpy.props.BoolProperty(default=False)

    def execute(self, context):
        
        if self.type == "Object" and not self.unHideAll:
            
            bpy.data.objects[self.itemName].hide = False
            bpy.data.objects[self.itemName].select = True
            bpy.context.scene.objects.active = bpy.data.objects[self.itemName]
        
        elif self.unHideAll:
            
            for object in getHiddenObjects():
                                
                if object.type == self.itemName:
                    
                    object.hide = False
                    object.select = True
                    bpy.context.scene.objects.active = object
            
        elif self.type == "Group":
            
            for object in bpy.data.groups[self.itemName].objects:
                
                if object.hide:
                
                    object.hide = False
                    object.select = True
        
        return {'FINISHED'}



class UnHideAllByTypeMenu(bpy.types.Menu):
    bl_label = "Unhide all by type"
    bl_idname = "view3d.unhide_all_by_type_menu"

    def draw(self, context):
        layout = self.layout

        objectTypes = []
            
        for object in getHiddenObjects():
                            
            if object.type not in objectTypes:
                
                row = layout.row()
                operator = row.operator("object.show", text=object.type.lower().capitalize(), icon="OUTLINER_OB_"+object.type)
                operator.itemName = object.type
                operator.unHideAll = True 
                
                objectTypes.append(object.type)
        
        

class UnHideByTypeMenu(bpy.types.Menu):
    bl_label = "Unhide by type"
    bl_idname = "view3d.unhide_by_type_menu"

    def draw(self, context):
        layout = self.layout
        split = layout.split()
        
        col = split.column()
        
#        rowCount = 0
#        columnCount = 0
#        maxRows = 21
#        maxColumns = 6
        
        for hiddenObject in getHiddenObjects():
#            if rowCount == maxRows and columnCount < maxColumns:
#                col = split.column()
#                rowCount = 0 
#                columnCount +=1
                
            if hiddenObject.type == context.object.type:
                row = col.row()                        
                operator = row.operator("object.show", text=hiddenObject.name)
                operator.itemName = hiddenObject.name
                operator.type = "Object" 
#                rowCount+=1        
        


class UnHideMenu(bpy.types.Menu):
    bl_label = "Unhide"
    bl_idname = "view3d.unhide_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        split = layout.split()
                        
        col = split.column()
        
        hiddenObjects = getHiddenObjects()
        hiddenGroups = getHiddenGroups()     
        
        row = col.row()
        if len(hiddenObjects) > 0:
            row.operator("object.hide_view_clear", text="Unhide all objects", icon="RESTRICT_VIEW_OFF")
            row = col.row()
            row.menu(UnHideAllByTypeMenu.bl_idname, text="UnHide all by type", icon="FILTER")
            row = col.row()
            operator = row.operator("object.unhide_search", text="Search", icon="VIEWZOOM")
            
        else:
            row.label(text="No hidden objects or groups")
                
                
        if len(hiddenGroups) > 0:
            col.separator()            
            row = col.row()
            row.label(text="Hidden groups:")
            
#        rowCount = 3
#        columnCount = 0
#        maxRows = 21
#        maxColumns = 6
            
        for hiddenGroup in hiddenGroups:
#            if rowCount == maxRows and columnCount < maxColumns:
#                col = split.column()
#                rowCount = -2
#                columnCount +=1
                
            row = col.row()
            operator = row.operator("object.show", text=hiddenGroup.name, icon="GROUP")
            operator.itemName = hiddenGroup.name
            operator.type = "Group"
            #rowCount +=1
      
        col.separator()
        
        if len(hiddenObjects) > 0:
            row = col.row()
            row.label(text="Hidden objects by type:")

        objectTypes = []
        
        for object in hiddenObjects:
                            
            if object.type not in objectTypes:
                                
                row = layout.row()
                row.context_pointer_set("object", object)    
                row.menu(UnHideByTypeMenu.bl_idname, text=object.type.lower().capitalize(), icon="OUTLINER_OB_"+object.type)      

                objectTypes.append(object.type)
                    

keymaps = []
                  
def register():
        
    bpy.utils.register_module(__name__)    
                
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    
    kmi = km.keymap_items.new('wm.call_menu', 'H', 'PRESS', alt=True)
    kmi.properties.name = 'view3d.unhide_menu'
    
    keymaps.append((km, kmi))
        


def unregister():
    bpy.utils.unregister_module(__name__)        
        
    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()
    


if __name__ == "__main__":
    register()

             