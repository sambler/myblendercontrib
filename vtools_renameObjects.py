bl_info = {
    "name": "vtools - Rename objects",
    "author": "Antonio Mendoza",
    "location": "View3D > Panel Tools > Tool Tab",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "warning": "",
    "description": "Batch renaming objects keeping selection order",
    "category": "Object", 
}


import bpy
import math 
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, FloatProperty, EnumProperty

    
def setName(p_objects, p_newName, p_startIn=0, p_numDigits=3, p_numbered=False):
    id = p_startIn
    cont = 1
    numberDigits = p_numDigits
    replacingName = p_newName
    
    if p_numbered == True:
         replacingName += ".000"    
 
    for obj in p_objects:
        
        if p_startIn == 0 or p_numbered == False:
            obj.name = replacingName
        else:
            addZero = 0    
            for i in range(1,numberDigits):
                mod = int(id / (pow(10,i)))
                if mod == 0:
                    addZero += 1
 
            newNameId = str(id)
            for i in range(0,addZero):
                newNameId = '0' + newNameId
               
            oldName = obj.name
            obj.name = ''
            newName = p_newName + '.' + newNameId
            obj.name = newName
            id += 1
            
 
def replace(p_objects, p_findString, p_replaceString=''):
    exist = 0
    if p_findString != '':
        for obj in p_objects:
            obj.name = obj.name.replace(p_findString, p_replaceString)
            
def hasId (p_name):
    
    
    idFound = False
    i = len(p_name) - 1
    str = p_name[i]
    str_res = ""
    
    while p_name[i].isnumeric() and i >= 0:
        str_res = p_name[i] + str_res
        i = i - 1
        

    if i < 0 or not str_res.isnumeric():
        idFound = False
        i = - 1
        
    return i

def addPrefixSubfix(p_objects,p_prefix='',p_subfix='',p_keepId=True):
    
    for obj in p_objects:
        obj.name = p_prefix + obj.name
        if p_keepId == True:
            id = hasId(obj.name)
            if id >= 0:
                obj.name = obj.name[:id] + p_subfix + obj.name[id:]
            else:
                obj.name = obj.name + p_subfix
        else:
            obj.name = obj.name + p_subfix   

def copyNametoData(p_objects):
    
    for obj in p_objects:
        if obj.type == 'MESH':
            obj.data.name = obj.name
            
class RNO_OP_setName(bpy.types.Operator):
    bl_idname = "object.rno_setname"
    bl_label = "Set new name"

    selection_list = []
    
       
    def execute(self,context):
        newName = context.scene.rno_str_new_name
        numbered = context.scene.rno_bool_numbered
        startIn = 1
        numDigits = 3
        
        if context.scene.rno_str_numFrom != '':
            startIn = int(context.scene.rno_str_numFrom)
            numDigits = len(context.scene.rno_str_numFrom)
            
        if context.scene.rno_bool_keepOrder == True:
            setName(self.selection_list,newName, p_startIn=startIn,p_numDigits=numDigits, p_numbered=numbered)
        else:
            setName(bpy.context.selected_objects, newName, p_startIn=startIn,p_numDigits=numDigits, p_numbered=numbered)
        
        return{'FINISHED'}

class RNO_OP_replaceInName(bpy.types.Operator):
    bl_idname = "object.rno_replace_in_name"
    bl_label = "replace"
        

    def execute(self,context):
        oldName = context.scene.rno_str_old_string
        newName = context.scene.rno_str_new_string
        
        replace(bpy.context.selected_objects,oldName, newName)
        
        return{'FINISHED'}
      
      
class RNO_OP_addSubfixPrefix(bpy.types.Operator):
    bl_idname = "object.rno_add_subfix_prefix"
    bl_label = "Add subfix / Prefix"
        

    def execute(self,context):
        prefix = context.scene.rno_str_prefix
        subfix = context.scene.rno_str_subfix
        keepIndex = context.scene.rno_bool_keepIndex 
        
        
        addPrefixSubfix(bpy.context.selected_objects,p_prefix=prefix,p_subfix=subfix,p_keepId=keepIndex)
        
        return{'FINISHED'}
      

class RNO_PN_EndSelectionOrder(bpy.types.Operator):
    bl_idname = "object.rno_end_selection_order"
    bl_label = "leave selection order"
    
    def execute(self,context):
        context.scene.rno_bool_keepOrder = False
        return {'FINISHED'}
      
class RNO_OP_copyNameToDataName(bpy.types.Operator):
    bl_idname = "object.copynametodata"
    bl_label = "Copy object name to mesh data name"
        

    def execute(self,context):

        copyNametoData(bpy.context.selected_objects)
        
        return{'FINISHED'}
    
class RNO_PN_KeepSelectionOrder(bpy.types.Operator):
    bl_idname = "object.rno_keep_selection_order"
    bl_label = "respect selection order Start / Finish"
    
    num_selected = 0
    selection_list = []    
  
    def getSelectionList(self):
        return self.selection_list
    
    def findObject(self, p_object, p_list):
        
        found = False
        for obj in p_list:
            if obj.name == p_object.name:
                found = True
                break            
        return found
    
    def removeUnselecteds(self, p_oldList, p_newList):
        
        for obj in p_oldList:
            found = self.findObject(obj, p_newList)
            if found == False:
                p_oldList.remove(obj)
                
        return p_oldList
              
            
    def sortList(self):
        
        objects = bpy.context.selected_objects
        num_sel = len(objects)
        num_sortElements = len(self.selection_list)
        
        if num_sel < num_sortElements:
            self.removeUnselecteds(self.selection_list,objects)
            
        else:
            for obj in objects:
                found = self.findObject(obj,self.selection_list)
                
                if found == False:
                    self.selection_list.append(obj)
        
        return True
        
    def execute(self,context):
        
        if context.scene.rno_bool_keepOrder == False:
            bpy.ops.object.select_all(action='DESELECT')
            context.scene.rno_bool_keepOrder = True
            self.active = False
            
            #print("------------------ INIT -----------------------")
            
        else:
            context.scene.rno_bool_keepOrder = False
            #print("------------------ END -----------------------")
            

        context.window_manager.modal_handler_add(self)            
        return {'RUNNING_MODAL'}
    
    
         
    def modal(self, context, event):
       
        active = context.scene.rno_bool_keepOrder 
        if active == True:
            self.sortList()
            return {'PASS_THROUGH'}
        else:
            return {'FINISHED'} 
              
        return {'PASS_THROUGH'}
 
    
class RNO_PN_RenamePanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Rename Objects"
    bl_context = "objectmode"
    bl_category = 'Tool'
    bl_options = {'DEFAULT_CLOSED'}       
    
       
    def draw(self,context):
        
        layout = self.layout
        row = layout.row(align=True)
        row.alignment = 'EXPAND' 
        
        # ----------- RESPECT ORDER ------------------ #
        
        
        col = row.column()
        subrow = col.row()
        subrow.prop(context.scene,'rno_bool_keepOrder',text='')
        subrow.enabled = False
        col = row.column()
        subrow = col.row()
        op_SelectionOrder = subrow.operator(RNO_PN_KeepSelectionOrder.bl_idname, text=RNO_PN_KeepSelectionOrder.bl_label)
        
   
        # ----------- NEW NAME ------------------ #
        
        row = layout.row()
        box = row.box()
        rbox = box.row(align=True)
        rbox.prop(context.scene,"rno_str_new_name")
        rbox = box.row(align=True)
        rbox.prop(context.scene,"rno_bool_numbered")
        rbox.prop(context.scene,"rno_str_numFrom")
        rbox = box.row()
        op_SetName = rbox.operator(RNO_OP_setName.bl_idname, text=RNO_OP_setName.bl_label)
        RNO_OP_setName.selection_list = RNO_PN_KeepSelectionOrder.selection_list
        
        # ----------- REPLACE NAME ------------------ #
        
        
        row=layout.row()
        box = row.box()
        rbox = box.column(align=True)
        rbox.prop(context.scene, "rno_str_old_string")
        rbox.prop(context.scene, "rno_str_new_string")
        box.operator(RNO_OP_replaceInName.bl_idname, text=RNO_OP_replaceInName.bl_label)

        # ----------- ADD SUBFIX / PREFIX NAME ------------------ #
        row = layout.row()
        box = row.box()
        rbox = box.row()
        
        box.prop(context.scene,'rno_bool_keepIndex',text='keep object Index')
        rbox.prop(context.scene, "rno_str_prefix")
        rbox.prop(context.scene, "rno_str_subfix")
        
        
        box.operator(RNO_OP_addSubfixPrefix.bl_idname, text=RNO_OP_addSubfixPrefix.bl_label)
        
        # ----------- COPY OBJECT NAME TO DATA NAME -------------------#
        row = layout.row()
        box = row.box()
        box.operator(RNO_OP_copyNameToDataName.bl_idname, text=RNO_OP_copyNameToDataName.bl_label)
        

        
def register():
    
    from bpy.utils import register_class
    
    register_class(RNO_PN_RenamePanel)
    register_class(RNO_OP_setName)
    register_class(RNO_OP_replaceInName)
    register_class(RNO_OP_addSubfixPrefix)
    register_class(RNO_PN_EndSelectionOrder)
    register_class(RNO_OP_copyNameToDataName)
    register_class(RNO_PN_KeepSelectionOrder)
    
    #bpy.utils.register_module(__name__)
    
    bpy.types.Scene.rno_list_selection_ordered = bpy.props.EnumProperty(name="selection orderer", items=[])
    
    bpy.types.Scene.rno_str_new_name = bpy.props.StringProperty(name="New name", default='')
    bpy.types.Scene.rno_str_old_string = bpy.props.StringProperty(name="Old string", default='')
    bpy.types.Scene.rno_str_new_string = bpy.props.StringProperty(name="New string", default='')
    bpy.types.Scene.rno_str_numFrom = bpy.props.StringProperty(name="from", default='')
    bpy.types.Scene.rno_str_prefix = bpy.props.StringProperty(name="Prefix", default='')
    bpy.types.Scene.rno_str_subfix = bpy.props.StringProperty(name="Subfix", default='')
    
    bpy.types.Scene.rno_bool_numbered = bpy.props.BoolProperty(name='numbered', default=True)
    bpy.types.Scene.rno_bool_keepOrder = bpy.props.BoolProperty(name='keep selection order')
    bpy.types.Scene.rno_bool_keepIndex = bpy.props.BoolProperty(name='keep object Index', default=True)

          
def unregister():
    
    from bpy.utils import unregister_class
    
    unregister_class(RNO_PN_RenamePanel)
    unregister_class(RNO_OP_setName)
    unregister_class(RNO_OP_replaceInName)
    unregister_class(RNO_OP_addSubfixPrefix)
    unregister_class(RNO_PN_EndSelectionOrder)
    unregister_class(RNO_OP_copyNameToDataName)
    unregister_class(RNO_PN_KeepSelectionOrder)
    
    #bpy.utils.unregister_module(__name__)
    
    del bpy.types.Scene.rno_str_new_name
    del bpy.types.Scene.rno_str_old_string
    del bpy.types.Scene.rno_str_new_string
    del bpy.types.Scene.rno_bool_keepOrder
    del bpy.types.Scene.rno_bool_numbered
    del bpy.types.Scene.rno_list_selection_ordered
    del bpy.types.Scene.rno_str_prefix
    del bpy.types.Scene.rno_str_subfix
    del bpy.types.Scene.rno_bool_keepIndex 
    
if __name__ == "__main__":
    register()
    