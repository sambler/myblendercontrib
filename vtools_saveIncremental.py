bl_info = {
    "name": "vtools Auto Incremental Save",
    "author": "Antonio Mendoza",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "File Menu",
    "description": "Auto Incremental Current File. If your file is numbered at the end of the file, it will save incremental in the same file. If there is no number, it will create a new folder in order to storage incremental versions.",
    "category": "User Interface"
}

import bpy
import os 
import glob 
from bpy.props import *
from bpy_extras.io_utils import ExportHelper

def getVersion(p_fileName):
    
    version = ""
    nameLeng = len(p_fileName)
    cont = nameLeng - 1
    isNumber = p_fileName[cont].isdigit()
    
    while cont >= 0 and isNumber:
        
        version = p_fileName[cont] + version
        cont = cont - 1
        isNumber = p_fileName[cont].isdigit()
    
    if version == "":
        version = "NONE"
        
    return version

def incrementVersion(p_version):
    
    version = ""
    nameLeng = len(p_version)
    cont = nameLeng - 1
    sum = 0
    add = 0
    
    nVersion = int(p_version)
    nVersion += 1
    version = str(nVersion)
    
    while len(version) < len(p_version):
        version = "0" + version
        
    return version
    

def hasVersion(p_fileName):
    
    cont = len(p_fileName) - 1
    isNumber = p_fileName[cont].isdigit()
    
    return isNumber

def getVersionPosition(p_fileName):
    
    i = len(p_fileName) - 1
    while p_fileName[i] != "_":
        i = i - 1
    i += 1
    
    return i 
    
def getIncrementedFile(p_file="", p_inIncFolder = True):
    
    incrementedFile = ""
    file = p_file
    baseName= os.path.basename(file)
    folder = os.path.dirname(file)
    fileName = os.path.splitext(baseName)[0]
    versionFolderName = ""
    type = os.path.splitext(baseName)[1]
    version = getVersion(fileName)
    newVersion = ""
    
    #if there is not a first version file, create the new one
    if version == "NONE":
        versionFolderName = "versions_" + fileName
        version = "000"
        fileName = fileName + "_000" 
        
    newVersion = incrementVersion(version) 
    numVersions = fileName.count(version)
    if numVersions >= 1:
        posVersion = getVersionPosition(fileName)
        print("ver: ", posVersion)
        fileName = fileName[:posVersion]
        newFileName = fileName + newVersion
    else:
        newFileName = fileName.replace(version,newVersion)
        
        
    newFullFileName = newFileName + type
    
    
    if p_inIncFolder:
        
        versionFolder = os.path.join(folder,versionFolderName)
        incrementedFile = os.path.join(versionFolder, newFullFileName)
        
    else:
        incrementedFile = os.path.join(folder, newFullFileName)
    
    return incrementedFile 

def getLastVersionFile(p_file = ""):
    
    #look into the version folder for the last one
    #if there is not anything, return an empty string
    
    lastFile = ""
    file = p_file
    baseName= os.path.basename(file)
    folder = os.path.dirname(file)
    fileName = os.path.splitext(baseName)[0]
    versionFolderName = "versions_" + fileName    
    versionFolder = os.path.join(folder,versionFolderName)

    if os.path.exists(versionFolder):
        filesToSearch = os.path.join(versionFolder, "*.blend")
        if len(filesToSearch) > 0:
            blendFiles = sorted(glob.glob(filesToSearch))
            lastFile = blendFiles[len(blendFiles)-1]
    else:
        os.makedirs(versionFolder)
          
    return lastFile
    
    
def saveIncremental():
    
    # check if it has version, 
    # if it has a version in the name save in the same folder with a version up number,
    # if not, save a new version within the version folder.
    
    currentFile = bpy.data.filepath
    baseName= os.path.basename(currentFile)
    currentFileName= os.path.splitext(baseName)[0]
    newFile = ""
        
    hasVersion = getVersion(currentFileName)

    if hasVersion == "NONE":
        
        # save in the version folder
        lastFile = getLastVersionFile(p_file = currentFile)
        if lastFile == "":
            lastFile = currentFile
        
        newFile = getIncrementedFile(p_file = lastFile, p_inIncFolder = True)
        bpy.ops.wm.save_as_mainfile(filepath=currentFile, copy=False)
        bpy.ops.wm.save_as_mainfile(filepath=newFile, copy=True)
        
        
    else:
        
        # save a new version in file current
        newFile = getIncrementedFile(p_file = currentFile, p_inIncFolder = False)
        bpy.ops.wm.save_as_mainfile(filepath=newFile)
     
    return os.path.basename(newFile)

class VTOOLS_OP_saveIncremental(bpy.types.Operator):
    bl_idname = "wm.saveincremental"
    bl_label = "Save incremental"
    
    def execute(self,context):
        
        if bpy.data.is_saved == True:
            savedFileName = saveIncremental()
            textReport = savedFileName + "version saved"
            self.report({'INFO'},textReport)
                   
        else:
            bpy.ops.wm.save_as_mainfile('INVOKE_DEFAULT')
            
            
        return {'FINISHED'}   
    

def addShortcut():
    
    # replace ctrl+s to this save incremental
    # inactive
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.active
    km = kc.keymaps.find("Window")
    
    saveShortcut = km.keymap_items.find("wm.save_mainfile")
    
    cont = 0
    while cont < 10:
        saveShortcut = km.keymap_items.find("wm.save_mainfile")
        if saveShortcut != -1:
            shortCut = km.keymap_items[saveShortcut]
            if shortCut.type == "S":
                km.keymap_items.remove(km.keymap_items[saveShortcut])
                break
        cont = cont + 1
    
    kmi = km.keymap_items.new(VTOOLS_OP_saveIncremental.bl_idname,'S','PRESS', any=False, shift=False, ctrl=True, alt=False, oskey=False, key_modifier='NONE')
    
def menu_draw(self, context):
    self.layout.separator()
    self.layout.operator(VTOOLS_OP_saveIncremental.bl_idname, text=VTOOLS_OP_saveIncremental.bl_label, icon='ADD')
    
def register():
    bpy.utils.register_class(VTOOLS_OP_saveIncremental)
    bpy.types.TOPBAR_MT_file.append(menu_draw)
    
    #addShortcut()
   
def unregister():
    bpy.utils.unregister_class(VTOOLS_OP_saveIncremental)
    bpy.types.TOPBAR_MT_file.remove(menu_draw)
    
    
if __name__ == "__main__":
    register()