#  ***** BEGIN GPL LICENSE BLOCK *****
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
#
#  The Original Code is: all of this file.
#
#  ***** END GPL LICENSE BLOCK *****
#
bl_info = {
    'name': 'Export: Adobe After Effects (.jsx)',
    'description': 'Export selected cameras, objects & bundles to Adobe After Effects CS3 and above',
    'author': 'Bartek Skorupa',
    'version': (0, 54),
    'blender': (2, 6, 0),
    'api': 41098,
    'location': 'File > Export > Adobe After Effects (.jsx)',
    'category': 'Import-Export',
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Import-Export/Adobe_After_Effects"
    }

from math import pi
import bpy
import datetime

# <pep8 compliant>

# create list of static blender's data
def GetCompData():
    compData = {}
    aspectX = bpy.context.scene.render.pixel_aspect_x
    aspectY = bpy.context.scene.render.pixel_aspect_y
    aspect = aspectX / aspectY
    fps = bpy.context.scene.render.fps
    compData['scn'] = bpy.context.scene
    compData['width'] = bpy.context.scene.render.resolution_x
    compData['height'] = bpy.context.scene.render.resolution_y
    compData['aspect'] = aspect
    compData['fps'] = fps
    compData['start'] = bpy.context.scene.frame_start
    compData['end'] = bpy.context.scene.frame_end
    compData['duration'] = (bpy.context.scene.frame_end-bpy.context.scene.frame_start + 1) / fps
    compData['curframe'] = bpy.context.scene.frame_current
    return compData

# create managable list of selected objects
# (only selected objects will be analyzed and exported)
def GetSelected(prefix):
    selection = {}
    cameras = [] # list of selected cameras
    cams_names = [] # list of selected cameras' names (prevent from calling "ConvertName(ob)" function too many times)
    nulls = [] # list of all selected objects exept cameras (will be used to create nulls in AE) 
    nulls_names = [] # list of above objects names (prevent from calling "ConvertName(ob)" function too many times)
    obs = bpy.context.selected_objects
    for ob in obs:
        if ob.type == 'CAMERA':
            cameras.append(ob)
            cams_names.append(ConvertName(ob,prefix))
        else:
            nulls.append(ob)
            nulls_names.append(ConvertName(ob,prefix))
    selection['cameras'] = cameras
    selection['cams_names'] = cams_names
    selection['nulls'] = nulls
    selection['nulls_names'] = nulls_names
    return selection   

# convert names of objects to avoid errors in AE. Add user specified prefix
def ConvertName(ob,prefix):
    obName = prefix + ob.name
    obName = obName.replace('.','_')
    obName = obName.replace(' ','_')
    obName = obName.replace('-','_')
    obName = obName.replace(',','_')
    obName = obName.replace('=','_')
    obName = obName.replace('+','_')
    obName = obName.replace('*','_')
    return obName

# get object's blender's location and rotation and return AE's Position and Rotation/Orientation
# this function will be called for every object for every frame
def ConvertPosRot(obs, width, height, aspect, x_rot_correction = False):
    matrix = obs.matrix_world

    # get blender location for ob
    bLocX = matrix.to_translation().x
    bLocY = matrix.to_translation().y
    bLocZ = matrix.to_translation().z

    # get blender rotation for ob
    if x_rot_correction:
      bRotX = (matrix.to_euler().x) / pi * 180 - 90
    else:
      bRotX = (matrix.to_euler().x) / pi * 180
    bRotY = (matrix.to_euler().y) / pi * 180
    bRotZ = (matrix.to_euler().z) / pi * 180

    # convert to AE Position and Rotation
    # Axes in AE are different. AE's X is blender's X, AE's Y is negative Blender's Z, AE's Z is Blender's Y
    x = (bLocX * 100) / aspect + width / 2 #calculate AE's X position
    y = (-1 * bLocZ * 100) + (height / 2) #calculate AE's Y position
    z = bLocY * 100 #calculate AE's Z position
    rx = bRotX #calculate AE's X rotation. Will become AE's RotationX property
    ry = -1 * bRotZ #calculate AE's Y rotation. Will become AE's OrientationY property
    rz = bRotY #calculate AE's Z rotation. Will become AE's OrentationZ property
    # Using AE's rotation combined with AE's orientation allows to compensate for different euler rotation order.
    aePosRot = ('%.3f' % x,'%.3f' % y,'%.3f' % z,'%.3f' % rx, '%.3f' % ry, '%.3f' % rz)
    return aePosRot

# get camera's lens and convert to AE's "zoom" value in pixels
# this function will be called for every camera for every frame
#
#
# AE's lens is defined by "zoom" in pixels. Zoom determines focal angle or focal length.
# AE's camera's focal length is calculated basing on zoom value.
#
# Known values:
#     - sensor (blender's sensor is 32mm)
#     - lens (blender's lens in mm)
#     - width (witdh of the composition/scene in pixels)
#
# zoom can be calculated from simple proportions.
#
#                             |
#                           / |
#                         /   |
#                       /     | w
#       s  |\         /       | i
#       e  |  \     /         | d
#       n  |    \ /           | t
#       s  |    / \           | h
#       o  |  /     \         |
#       r  |/         \       |
#                       \     |
#          |     |        \   |
#          |     |          \ |
#          |     |            |
#           lens |    zoom    
#
#    zoom/width = lens/sensor   =>
#    zoom = lens/sensor*width = lens*width * (1/sensor)
#    sensor - sensor_width will be taken into account if version of blender supports it. If not - standard blender's 32mm will be caclulated.
#    
#    
#    above is true if square pixels are used. If not - aspect compensation is needed, so final formula is:
#    zoom = lens * width * (1/sensor) * aspect
#
def ConvertLens(camera, width, aspect):
    # wrap camera.data.sensor_width in 'try' to maintain compatibility with blender version not supporting camera.data.sensor_width
    try:
        sensor = camera.data.sensor_width #if camera.data.sensor_width is supported - it will be taken into account
    except:
        sensor = 32 #if version of blender doesn't yet support sensor_width - default blender's 32mm will be taken.
    zoom = camera.data.lens * width * (1/sensor) * aspect
    return zoom

# jsx script for AE creation
def WriteJsxFile(file, data, selection, exportBundles, compName, prefix):
    print("\n---------------------------\n- Export to After Effects -\n---------------------------")
    #store the current frame to restore it at the enf of export
    curframe = data['curframe']
    #create array which will contain all keyframes values
    jsDatas = {}
    jsDatas['times'] = ''
    jsDatas['cameras'] = {}
    jsDatas['objects'] = {}

    # create camera structure
    for i, cam in enumerate (selection['cameras']): #more than one camera can be selected
        nameAE = selection['cams_names'][i]
        jsDatas['cameras'][nameAE] = {}
        jsDatas['cameras'][nameAE]['position'] = ''
        jsDatas['cameras'][nameAE]['pointOfInterest'] = ''
        jsDatas['cameras'][nameAE]['orientation'] = ''
        jsDatas['cameras'][nameAE]['rotationX'] = ''
        jsDatas['cameras'][nameAE]['zoom'] = ''
        
    # create object structure
    for i, obj in enumerate (selection['nulls']): #nulls representing blender's obs except cameras
        nameAE = selection['nulls_names'][i]
        jsDatas['objects'][nameAE] = {}
        jsDatas['objects'][nameAE]['position'] = ''
        jsDatas['objects'][nameAE]['orientation'] = ''
        jsDatas['objects'][nameAE]['rotationX'] = ''


    # get all keyframes for each objects and store into dico
    for frame in range(data['start'],data['end'] + 1):
        print("working on frame: " + str(frame))
        data['scn'].frame_set(frame)
        
        #get time for this loop
        jsDatas['times'] += '%f ,' % float((frame-data['start']) / (data['fps']));

        # keyframes for all cameras
        for i, cam in enumerate (selection['cameras']):
            #get cam name
            nameAE = selection['cams_names'][i]
            #convert cam position to AE space
            aePosRot = ConvertPosRot(cam, data['width'], data['height'], data['aspect'], x_rot_correction = True)
            #convert Blender's cam zoom to AE's
            zoom = ConvertLens(cam, data['width'], data['aspect'])
            #store all the value into dico
            jsDatas['cameras'][nameAE]['position'] += '[%f,%f,%f],' % (float(aePosRot[0]), float(aePosRot[1]), float(aePosRot[2]))
            jsDatas['cameras'][nameAE]['pointOfInterest'] += '[%f,%f,%f],' % (float(aePosRot[0]), float(aePosRot[1]), float(aePosRot[2]))
            jsDatas['cameras'][nameAE]['orientation'] += '[%f,%f,%f],' % (0, float(aePosRot[4]), float(aePosRot[5]))
            jsDatas['cameras'][nameAE]['rotationX'] += '%f ,' % (float(aePosRot[3]))
            jsDatas['cameras'][nameAE]['zoom'] += '[%f],' % (float(zoom))
            
        #keyframes for all nulls
        for i, ob in enumerate (selection['nulls']):
            #get object name
            nameAE = selection['nulls_names'][i]
            #convert ob position to AE space
            aePosRot = ConvertPosRot(ob, data['width'], data['height'], data['aspect'], x_rot_correction = False)
            #store all datas into dico
            jsDatas['objects'][nameAE]['position'] += '[%f,%f,%f],' % (float(aePosRot[0]), float(aePosRot[1]), float(aePosRot[2]))
            jsDatas['objects'][nameAE]['orientation'] += '[%f,%f,%f],' % (0, float(aePosRot[4]), float(aePosRot[5]))
            jsDatas['objects'][nameAE]['rotationX'] += '%f ,' % (float(aePosRot[3]))

            
    # ---- write JSX file
    jsxFile = open (file, 'w')
    
    # make the jsx executable in After Effects (enable double click on jsx)
    jsxFile.write('#target AfterEffects\n\n')
    jsxFile.write('/**************************************\n')
    jsxFile.write('Scene : %s\n' % bpy.context.scene.name)
    jsxFile.write('Resolution : %i x %i\n' % (data['width'], data['height']))
    jsxFile.write('Duration : %f\n' % (data['duration']))
    jsxFile.write('FPS : %f\n' % (data['fps']))
    jsxFile.write('Date : %s\n' % datetime.datetime.now())
    jsxFile.write('Exported with BlenderToAE v. 0.53\n')
    jsxFile.write('**************************************/\n\n\n\n')
    
    #wrap in function
    jsxFile.write("function compFromBlender(){\n")
    # create new comp
    jsxFile.write('\nvar compName = "%s";' % (compName))
    jsxFile.write('\nvar newComp = app.project.items.addComp(compName, %i, %i, %f, %f, %i);\n\n\n'
    %(data['width'], data['height'], data['aspect'], data['duration'], data['fps']))
    
    # create cameras
    jsxFile.write('// **************  CAMERAS  **************\n\n\n')
    for i, cam in enumerate (jsDatas['cameras']): #more than one camera can be selected
        nameAE = cam
        jsxFile.write('var %s = newComp.layers.addCamera("%s",[0,0]);\n' % (nameAE, nameAE))
        jsxFile.write('%s.property("position").setValuesAtTimes([%s],[%s]);\n' % (nameAE,jsDatas['times'],jsDatas['cameras'][cam]['position'],))
        jsxFile.write('%s.property("pointOfInterest").setValuesAtTimes([%s],[%s]);\n' % (nameAE,jsDatas['times'],jsDatas['cameras'][cam]['pointOfInterest'],))
        jsxFile.write('%s.property("orientation").setValuesAtTimes([%s],[%s]);\n' % (nameAE,jsDatas['times'],jsDatas['cameras'][cam]['orientation'],))
        jsxFile.write('%s.property("rotationX").setValuesAtTimes([%s],[%s]);\n' % (nameAE,jsDatas['times'],jsDatas['cameras'][cam]['rotationX'],))
        jsxFile.write('%s.property("rotationY").setValue(0);\n' % nameAE)
        jsxFile.write('%s.property("rotationZ").setValue(0);\n' % nameAE)
        jsxFile.write('%s.property("zoom").setValuesAtTimes([%s],[%s]);\n\n\n' % (nameAE,jsDatas['times'],jsDatas['cameras'][cam]['zoom'],))
        
        
    # create objects
    jsxFile.write('// **************  OBJECTS  **************\n\n\n')
    for i, obj in enumerate (jsDatas['objects']): #more than one camera can be selected
        nameAE = obj
        jsxFile.write('var %s = newComp.layers.addNull();\n' % (nameAE))
        jsxFile.write('%s.threeDLayer = true;\n' % nameAE)
        jsxFile.write('%s.source.name = "%s";\n' % (nameAE,nameAE))
        jsxFile.write('%s.property("position").setValuesAtTimes([%s],[%s]);\n' % (nameAE,jsDatas['times'],jsDatas['objects'][obj]['position'],))
        jsxFile.write('%s.property("orientation").setValuesAtTimes([%s],[%s]);\n' % (nameAE,jsDatas['times'],jsDatas['objects'][obj]['orientation'],))
        jsxFile.write('%s.property("rotationX").setValuesAtTimes([%s],[%s]);\n' % (nameAE,jsDatas['times'],jsDatas['objects'][obj]['rotationX'],))
        jsxFile.write('%s.property("rotationY").setValue(0);\n' % nameAE)
        jsxFile.write('%s.property("rotationZ").setValue(0);\n\n\n' % nameAE)


    # create Bundles
    if exportBundles :
    
        jsxFile.write('// **************  BUNDLES (3d tracks)  **************\n\n\n')
        
        #create a temporary Emtpy which we'll snap on each bundles to send its position to converter
        bpy.ops.object.add(type='EMPTY',view_align=False, enter_editmode=False, location=(0,0,0))
        empty_tmp = bpy.context.active_object
        #Bundles are linked to MovieClip, so we have to find which MC is linked to our selected camera (if any?)
        mc = ''
        
        
        #go through each selected Cameras
        for cam in selection['cameras']:
            #go through each constrains of this camera
            for constrain in cam.constraints : 
                #does the camera have a Camera Solver constrain
                if constrain.type == 'CAMERA_SOLVER' : 
                    #Which movie clip does it use ? 
                    if constrain.use_default_clip : 
                        mc = bpy.context.scene.clip
                    else : 
                        mc = constrain.clip
                    
                    #go throuhg each tracking point
                    for track in mc.tracking.tracks: 
                        #is this tracking point has a Bundles (does it's 3D position has been solved)
                        if track.has_bundle:
                            # bundle are in camera space, so transpose it to world space
                            position = cam.matrix_basis * track.bundle 
                            #apply the new position to our temp Empty
                            empty_tmp.location = [position[0],position[1],position[2]]
                            #update the scene to update matrices
                            bpy.context.scene.update()
                            #convert the position into AE space
                            aePosRot = ConvertPosRot(empty_tmp, data['width'], data['height'], data['aspect'], x_rot_correction = False)
                            #get the name of the tracker
                            nameAE = ConvertName(track,prefix)
                            #write JS script for this Bundle
                            jsxFile.write('var %s = newComp.layers.addNull();\n' % nameAE)
                            jsxFile.write('%s.threeDLayer = true;\n' % nameAE)
                            jsxFile.write('%s.source.name = "%s";\n' % (nameAE,nameAE))
                            jsxFile.write('%s.property("position").setValue([%f,%f,%f]);\n\n\n' % (nameAE,float(aePosRot[0]),float(aePosRot[1]),float(aePosRot[2])))
                            
                            
        # delete the temp empty                 
        bpy.ops.object.delete()
                                    
    jsxFile.write("}\n\n\n")
    jsxFile.write('app.beginUndoGroup("Import Blender animation data");\n')
    jsxFile.write('compFromBlender();\n')
    jsxFile.write('app.endUndoGroup();\n\n\n')
    jsxFile.close()

    data['scn'].frame_set(curframe) # set current frame of animation in blender to state before export

##########################################
# DO IT
##########################################

def Main(file, context,exportBundles,compName,prefix):
    data = GetCompData()
    selection = GetSelected(prefix)
    WriteJsxFile(file, data, selection,exportBundles,compName,prefix)
    print ("\nExport to After Effects Completed")
    return {'FINISHED'}

##########################################
# ExportJsx class register/unregister
##########################################

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty

class ExportJsx(bpy.types.Operator, ExportHelper):
    '''Export selected cameras and objects animation to After Effects'''
    bl_idname = "export.jsx"
    bl_label = "Export to Adobe After Effects"
    filename_ext = ".jsx"
    filter_glob = StringProperty(default="*.jsx", options={'HIDDEN'})

    compName = StringProperty(
            name="Comp Name",
            description="Name of composition to be created in After Effects",
            default="BlendComp"
            )
    prefix = StringProperty(
            name="Layer's Prefix",
            description="Prefix to use before AE layer's name",
            #default="bl_"
            )
    exportBundles = BoolProperty(
            name="Export Bundles",
            description="Export 3D Tracking points of a selected camera",
            default=False,
            )

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        return Main(self.filepath,context,self.exportBundles,self.compName,self.prefix)

def menu_func(self, context):
    self.layout.operator(ExportJsx.bl_idname, text="Adobe After Effects (.jsx)")

def register():
    bpy.utils.register_class(ExportJsx)
    bpy.types.INFO_MT_file_export.append(menu_func)
def unregister():
    bpy.utils.unregister_class(ExportJsx)
    bpy.types.INFO_MT_file_export.remove(menu_func)
if __name__ == "__main__":
    register()