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

#----------------------------------------------------------
# File: html_maker.py
# Create HTML documentation of blend file.
# Author: Antonio Vazquez (antonioya)
#
# Version info
# ================================================
# 0.1 Initial version (alpha)
#----------------------------------------------------------
import bpy
import os
import datetime
import time

global pathImages
global pathImagesHtml
global pathStyle
global pathStyleHtml

#------------------------------------------------------------------------------
# Generate HTML file
#------------------------------------------------------------------------------
def write_html(outpath,include_render,only_render,include_header,include_story,threshold,include_images
               ,include_links,typecolor,webserver,include_borders,grease):
    #-------------------------------
    # extract path and filename 
    #-------------------------------
    (filepath, filename) = os.path.split(outpath)
    print("=====================================================")
    print('Exporting %s' % filename)
    #-------------------------------
    # Create output directories
    #-------------------------------
    # Images
    global pathImagesHtml 
    pathImagesHtml = "img_" + get_filename(filename.replace(" ","_")).lower()
    directory = os.path.join(filepath,pathImagesHtml)
    
    global pathImages
    pathImages = directory    
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    # Styles    
    # if webserver, put style outside images
    global pathStyleHtml
    if (webserver == False):    
        directory = os.path.join(directory,"style")
        pathStyleHtml = pathImagesHtml + "/style"
    else:   
        directory = os.path.join(filepath,"style")
        pathStyleHtml = "style"
        
    global pathStyle
    pathStyle = directory    
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    #-------------------------------
    # copy style sheet to style
    #-------------------------------
    fromcss = os.path.join(os.path.dirname(__file__), "template/images","doc_style.css")
    tocss = os.path.join(pathStyle ,"doc_style.css")
    copy_binfile(fromcss,tocss)

    #-------------------------------
    # copy support images to style
    #-------------------------------
    fromimg = os.path.join(os.path.dirname(__file__), "template/images")
    copy_binfile(os.path.join(fromimg,"top_area.png"),os.path.join(pathStyle,"top_area.png"))
    copy_binfile(os.path.join(fromimg,"mid_area.png"),os.path.join(pathStyle,"mid_area.png"))
    copy_binfile(os.path.join(fromimg,"bottom_area.png"),os.path.join(pathStyle,"bottom_area.png"))
    copy_binfile(os.path.join(fromimg,"whitenoise.png"),os.path.join(pathStyle,"whitenoise.png"))
    copy_binfile(os.path.join(fromimg,"c.gif"),os.path.join(pathStyle,"c.gif"))
    
    #-------------------------------
    # export the images 
    # to a new folder
    #-------------------------------
    if (include_images == True):
        export_images(pathImages)
    #-------------------------------
    # Open output file
    #-------------------------------
    realpath = os.path.realpath(os.path.expanduser(outpath))
    fOut = open(realpath, 'w')    

    #-------------------------------
    # generate html
    #-------------------------------
    fInput = open( os.path.join(os.path.dirname(__file__), "template","doc_template.htm"))
    line = fInput.readline()
    while line:
        if ("<!--TITLE-->" in line):
            html_title(fOut,line)
        elif ("<!--STYLE-->" in line):
            html_style(fOut,line)    
        elif ("<!--BCKCOLOR-->" in line):
            html_bckcolor(fOut,line,typecolor)    
        elif ("<!--INFO-->" in line):
            if (include_header == True):
                html_info(filepath,fOut)    
        elif ("<!--RENDER-->" in line):
            if (include_render == True):
                html_render(pathImages,fOut,filename,only_render)    
        elif ("<!--STORYBOARD-->" in line):
            if (int(include_story) > 0):
                html_storyboard(pathImages,fOut,filename,only_render,include_story,threshold,grease,include_header)    
        elif ("<!--IMAGES-->" in line):
            if (include_images == True):
                html_images(pathImages,fOut,include_borders)    
        elif ("<!--LINKS-->" in line):
            if (include_links == True):
                html_links(filepath,fOut,include_borders)    
        elif ("<!--TIME-->" in line):
            html_time(fOut,line,typecolor)    
        else:
            fOut.write(line)
        line = fInput.readline()
    fInput.close()

    fOut.close()
    print('%s successfully exported' % realpath)
    print("=====================================================")
    
    return
#-------------------------------------
# Copy bin file
#-------------------------------------
def copy_binfile(fromfile, tofile):
    with open(fromfile,'rb') as f1:
        with open(tofile,'wb') as f2:
            while True:
                bytes=f1.read(1024)
                if bytes: 
                    n=f2.write(bytes)
                else:
                    break    
#-------------------------------------
# Get Color mode function
#-------------------------------------
def find_color_mode(image):
    if not isinstance(image, bpy.types.Image):
        raise(TypeError)
    else:
        #if image.depth <= 8:
        #    return 'BW'
        if image.depth <= 8:
            return 'RGB'
        else:
            return 'RGBA'
#-------------------------------------
# Set only render status
#-------------------------------------
def set_only_render(status):        
    screen = bpy.context.screen
    
    v3d = False
    # get spaceview_3d in current screen
    for a in screen.areas:
        if a.type == 'VIEW_3D':
            for s in a.spaces:
                if s.type == 'VIEW_3D':
                    v3d = s
                    break
    
    if v3d != False:
        s.show_only_render = status        
#-------------------------------------
# Get file name (no extension)
#-------------------------------------
def get_filename(filepath):
    return os.path.splitext(filepath)[0]
#-------------------------------------
# Set viewport to camera
#-------------------------------------
def setCameraView():
    for area in bpy.context.screen.areas: 
        if area.type == 'VIEW_3D': 
            area.spaces[0].region_3d.view_perspective = 'CAMERA'

#------------------------------------------
# Adjust aspect ratio to new size
#
# width/height define original image size
#
# sizeX/Y define the maximum box
# for final image
# 
# Return new image sizes.
#------------------------------------------
def ratio(width,height,sizeX=128, sizeY=128):
    renderX = sizeX
    renderY = sizeY
    
    # avoid errors
    if (width == 0):
        width = 128
        
    if (height == 0):
        height = 128
    
    if (width > height):
        renderY = (height * renderX) / width
    else:
        renderX = (width * renderY) / height 
   
    return [int(renderX),int(renderY)]
#-------------------------------------
# Update title
#-------------------------------------
def html_title(fHandle,line):
    (filepath, filename) = os.path.split(bpy.data.filepath)
    line = line.replace("<!--TITLE-->","Blend file: " +  filename)
    fHandle.write(line)
#-------------------------------------
# Update back color
#-------------------------------------
def html_bckcolor(fHandle,line,typecolor):
    line = line.replace("<!--BCKCOLOR-->",typecolor)
    fHandle.write(line)
#-------------------------------------
# Update style location
#-------------------------------------
def html_style(fHandle,line):
    line = line.replace("<!--STYLE-->",pathStyleHtml)
    fHandle.write(line)
#-------------------------------------
# Update time
#-------------------------------------
def html_time(fHandle,line,typecolor):
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    fHandle.write("<tr>\n")
    fHandle.write("<td align=\"right\" class=\"copyright\">Created by doc_scenes Addon on " + st + "&nbsp;&nbsp;&nbsp;</td>\n")
    fHandle.write("</tr>\n")
#-------------------------------------
# Create info table
#-------------------------------------
def html_info(rootpath,fHandle):
    fHandle.write("<tr><td class=\"header\"><br />&nbsp;&nbsp;Blend information</td></tr>\n")
    #-------------------
    # Table header
    #-------------------
    fHandle.write("<tr><td>\n")
    fHandle.write("<table width=\"1000\" border=\"0\" align=\"center\" cellpadding=\"0\" cellspacing=\"0\">\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td height=\"20\" class=\"top_area\"><img src=\"" + pathStyleHtml + "/c.gif\"></td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td class=\"mid_area\">\n")
    fHandle.write("  <table width=\"975\" border=\"0\" align=\"center\" cellpadding=\"5\" cellspacing=\"0\">\n")
    # blend name
    (filepath, filename) = os.path.split(bpy.data.filepath)
    fHandle.write("    <tr>\n")
    fHandle.write("     <td colspan=\"4\"><span class=\"smalltitle\">File:</span>&nbsp;<span class=\"medtitle\">" + filename + "</span></td>\n") 
    fHandle.write("    </tr>\n")
    # scene name
    current_scene = bpy.context.scene
    fHandle.write("    <tr>\n")
    fHandle.write("     <td><span class=\"smalltitle\">Scene:</span>&nbsp;" + current_scene.name)
    fHandle.write("     <td><span class=\"smalltitle\">&nbsp;&nbsp;Start:</span>&nbsp;" + str(current_scene.frame_start))
    fHandle.write("     <td><span class=\"smalltitle\">&nbsp;&nbsp;End:</span>&nbsp;" + str(current_scene.frame_end))
    fHandle.write("     <td><span class=\"smalltitle\">&nbsp;&nbsp;FPS:</span>&nbsp;" + str(current_scene.render.fps))
    fHandle.write("     </td>\n") 
    fHandle.write("    </tr>\n")
    fHandle.write("    <tr>\n")
    fHandle.write("     <td><span class=\"smalltitle\">Render:</span>&nbsp;" + current_scene.render.engine)
    fHandle.write("     <td colspan=\"2\"><span class=\"smalltitle\">&nbsp;&nbsp;Render size:</span>&nbsp;" + str(current_scene.render.resolution_x) 
                  + " * " 
                  + str(current_scene.render.resolution_y))
    fHandle.write("     </td>\n") 
    fHandle.write("     <td>&nbsp;</td>\n") 
    fHandle.write("    </tr>\n")
    # Get Author
    prefs = bpy.context.user_preferences.system
    author = prefs.author
    if (len(author) > 0):
        fHandle.write("    <tr>\n")
        fHandle.write("     <td colspan=\"3\"><span class=\"smalltitle\">Author:</span>&nbsp;" + author)
        fHandle.write("     </td>\n") 
        fHandle.write("     <td>&nbsp;</td>\n") 
        fHandle.write("    </tr>\n")
    #-------------------
    # Table foot
    #-------------------
    fHandle.write("  </table>\n")
    fHandle.write(" </td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td height=\"20\" class=\"bottom_area\"><img src=\"" +  pathStyleHtml + "/c.gif\"></td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("</table>\n")    
    fHandle.write("</td></tr>\n")
#-------------------------------------
# Create render table
#-------------------------------------
def html_render(rootpath,fHandle,filehtm,only_render):
    current_scene = bpy.context.scene
    fHandle.write("<tr><td class=\"header\">&nbsp;&nbsp;Render example</td></tr>\n")
    #-------------------
    # Table header
    #-------------------
    fHandle.write("<tr><td>\n")
    fHandle.write("<table width=\"1000\" border=\"0\" align=\"center\" cellpadding=\"0\" cellspacing=\"0\">\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td height=\"25\" class=\"top_area\"><img src=\"" +  pathStyleHtml + "/c.gif\"></td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td class=\"mid_area\">\n")
    fHandle.write("  <table width=\"975\" border=\"0\" align=\"center\" cellpadding=\"5\" cellspacing=\"0\">\n")
    #--------------------------
    # Image (export and table)
    #--------------------------
    flagRender = False
    try:
        oldSlot = bpy.data.images['Render Result'].render_slot
    except:
        oldSlot = 0 
            
    for num in range(0,8):
        try:
            bpy.data.images['Render Result'].render_slot = num
            image = bpy.data.images['Render Result']
            filesave = "render_slot_" + str(num) +  "_" + os.path.splitext(filehtm)[0].lower()  +".png"
            save_image(pathImages,filesave,image)
            if (os.path.exists(rootpath + "/" + pathImages + "/"+ os.path.splitext(filesave)[0].lower() + ".png")):
                z = ratio(current_scene.render.resolution_x
                          ,current_scene.render.resolution_y
                          ,960,600)
                fHandle.write("    <tr>\n")
                fHandle.write("     <td align=\"center\">"
                              + "<a href=\"" + pathImagesHtml + "/" + filesave + "\" target=\"_blank\">" 
                              + "<img src=\"" + pathImagesHtml + "/" 
                              + filesave 
                              + "\" width=\"" + str(z[0]) + "\" height=\"" + str(z[1]) + "\"></td>\n") 
                fHandle.write("    </tr>\n")
                flagRender = True
        except:
            print("slot " + str(num) + " empty.")
    try:        
        bpy.data.images['Render Result'].render_slot = oldSlot
    except:
        flagRender= False
                
    # No render (create OpenGL)
    if (flagRender == False):
        try:
            print("Render default openGL in slot 8...")
            bpy.data.images['Render Result'].render_slot = 7
            
            if (only_render == True):
                set_only_render(True)
                
            setCameraView()
            bpy.ops.render.opengl()
            
            if (only_render == True):
                set_only_render(False)
            
            image = bpy.data.images['Render Result']
            filesave = "render_slot_" + str(num) +  "_" + os.path.splitext(filehtm)[0].lower()  +".png"
            save_image(rootpath,filesave,image)
            
            z = ratio(current_scene.render.resolution_x
                      ,current_scene.render.resolution_y
                      ,960,600)
            fHandle.write("    <tr>\n")
            fHandle.write("     <td align=\"center\">" 
                          + "<a href=\"" + pathImagesHtml + "/" + filesave + "\" target=\"_blank\">" 
                          + "<img src=\"" + pathImagesHtml + "/" 
                          + filesave 
                          + "\" width=\"" + str(z[0]) + "\" height=\"" + str(z[1]) + "\"></td>\n") 
            fHandle.write("    </tr>\n")
            flagRender = True
        except:
            print("slot " + str(num) + " empty.")
    
    try:        
        bpy.data.images['Render Result'].render_slot = oldSlot    
    except:
        print("no render found")
    # No render, add white noise
    if (flagRender == False):
        z = ratio(960,600,960,600)
        fHandle.write("    <tr>\n")
        fHandle.write("     <td align=\"center\">" 
                      + "<a href=\"" + pathStyleHtml + "/whitenoise.png\" target=\"_blank\">"
                      + "<img src=\"" + pathStyleHtml + "/whitenoise.png" 
                      + "\" width=\"" + str(z[0]) + "\" height=\"" + str(z[1]) + "\"></td>\n") 
        fHandle.write("    </tr>\n")
    #-------------------
    # Table foot
    #-------------------
    fHandle.write("  </table>\n")
    fHandle.write(" </td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td height=\"25\" class=\"bottom_area\"><img src=\"" + pathStyleHtml + "/c.gif\"></td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("</table>\n")    
    fHandle.write("</td></tr>\n")
#-------------------------------------
# Verify if exist in list
#-------------------------------------
def existinlist(list,element):
    for l in list:    
        if (l == element):
            return True

    return False
#-------------------------------------
# Create storyboard table
#-------------------------------------
def html_storyboard(rootpath,fHandle,filehtm,only_render,include_story,threshold,grease,include_header):
    current_scene = bpy.context.scene
    f = current_scene.frame_start
    t = current_scene.frame_end
    print("Generating storyboard with a threshold of " + str(threshold) + " keyframes.")    

    #-------------------
    # Get keyframe list
    #-------------------
    klist = []
    #--------------------------------------
    # Using default keyframing
    #--------------------------------------
    if (grease == False):
        for a in bpy.data.actions:    
            for curve in  a.fcurves:
                keyframePoints = curve.keyframe_points
                for keyframe in keyframePoints:
                    if (existinlist(klist,keyframe.co[0]) == False):
                        k = int(keyframe.co[0])
                        if ( k >= f and k <= t):
                            klist.append(k)
    #--------------------------------------
    # Using grease pencil keyframing
    #--------------------------------------
    if (grease == True):
        try:
            gp = bpy.data.grease_pencil[0]
        except:
            return  # nothing to do
        # Get Layer
        layer = gp.layers.get("Storyboard_html")
        # Get Frames
        if layer is not None:
            for frame in layer.frames:
                k = frame.frame_number
                if ( k >= f and k <= t):
                    klist.append(k)
    
    klist.sort()
    if (len(klist) == 0):
        return   
    if (include_header == True):
        fHandle.write("<tr><td class=\"header\">&nbsp;&nbsp;Storyboard<span class=\"smalltitle\">(Camera: " + current_scene.camera.name + ")</span></td></tr>\n")
    else:    
        # blend name
        (filepath, filename) = os.path.split(bpy.data.filepath)
        current_scene = bpy.context.scene
        fHandle.write("<tr><td class=\"header\">&nbsp;&nbsp;Storyboard"
            + "<span class=\"smalltitle\">&nbsp;&nbsp;&nbsp;File: " + filename + "</span>"
            + "<span class=\"smalltitle\">&nbsp;&nbsp;&nbsp;Scene: " + current_scene.name + "</span>"
            + "<span class=\"smalltitle\">&nbsp;&nbsp;&nbsp;Fps: " + str(current_scene.render.fps) + "</span>"
            + "<span class=\"smalltitle\">&nbsp;&nbsp;&nbsp;Camera: " + current_scene.camera.name + "</span>"
            + "</td></tr>\n")
    #-------------------
    # Table header
    #-------------------
    fHandle.write("<tr><td>\n")
    fHandle.write("<table width=\"1000\" border=\"0\" align=\"center\" cellpadding=\"0\" cellspacing=\"0\">\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td height=\"25\" class=\"top_area\"><img src=\"" + pathStyleHtml + "/c.gif\"></td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td class=\"mid_area\">\n")
    fHandle.write("  <table width=\"975\" border=\"0\" align=\"center\" cellpadding=\"5\" cellspacing=\"2\">\n")
    #--------------------------
    # Image (export and table)
    #--------------------------
    try:
        oldSlot = bpy.data.images['Render Result'].render_slot
    except:
        oldSlot = 1
    if (only_render == True):
        set_only_render(True)
        
    current_scene = bpy.context.scene
    oldframe = bpy.context.scene.frame_current
    
    x = 0
    # apply threshold to reduce number of keyframes
    nextframe = klist[0]
    i = 1
    for e in klist:
        try:
            if (e >= nextframe or i == len(klist)):
                nextframe = e + threshold
           
                print("Storyboard keyframe: " + str(e))
                current_scene.frame_set(e)
                bpy.data.images['Render Result'].render_slot = 7
                setCameraView()
                bpy.ops.render.opengl()
                image = bpy.data.images['Render Result']
                filesave = "frame_" + str(e) +  "_" + os.path.splitext(filehtm)[0].lower()  +".png"
                save_image(rootpath,filesave,image)
                if (os.path.exists(rootpath + "/" + os.path.splitext(filesave)[0].lower() + ".png")):
                    # Select size of frame
                    if (int(include_story) != 1):
                        z = ratio(current_scene.render.resolution_x
                                  ,current_scene.render.resolution_y
                                  ,450,275)
                    else:
                        z = ratio(current_scene.render.resolution_x
                                  ,current_scene.render.resolution_y
                                  ,600,365)
                            
                    
                    if (x % 2 == 0): 
                        fHandle.write("    <tr>\n")
                    
                    sec = (e / current_scene.render.fps)
                    sectxt = "%0.03f" % (sec)
                    fHandle.write("     <td align=\"center\">"
                                  + "<a href=\"" + pathImagesHtml + "/" + filesave + "\" target=\"_blank\">" 
                                  + "<img src=\"" + pathImagesHtml + "/" 
                                  + filesave 
                                  + "\" width=\"" + str(z[0]) + "\" height=\"" + str(z[1]) + "\">"
                                  + "<br /><span class=\"smalltitle\">Keyframe: </span>" + str(e)  
                                  + " (" + sectxt + " sec.)"
                                  + "</td>\n")
                    # 1 by row 
                    if (int(include_story) == 1):
                        x = x + 1    
                    # Notes Box 
                    if (int(include_story) == 3):
                        fHandle.write("     <td class=\"box\" width=\"" + str(z[0] - 20) + "\">"
                                      + "<span class=\"smalltitle\">Notes:</span><br />" 
                                      + "</td>\n")
                        x = x + 1
                     
                    if (x % 2 != 0): 
                        fHandle.write("    </tr>\n")
                        
                    x = x + 1
            else:
                print("Omitted storyboard keyframe: " + str(e))    
            # add 1 to keyframe for threshold        
            i = i + 1                    
        except:
            print("Error in storyboard.")
            
    # close table (if even)
    if (x % 2 == 0 and int(include_story) == 2): 
        fHandle.write("    </tr>\n")
    
    
    # back to old configuration        
    try:
        bpy.data.images['Render Result'].render_slot = oldSlot
    except:
        bpy.data.images['Render Result'].render_slot = 1
                
    current_scene.frame_set(oldframe)
    
    if (only_render == True):
        set_only_render(False)
    
    #-------------------
    # Table foot
    #-------------------
    fHandle.write("  </table>\n")
    fHandle.write(" </td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td height=\"25\" class=\"bottom_area\"><img src=\"" + pathStyleHtml + "/c.gif\"></td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("</table>\n")    
    fHandle.write("</td></tr>\n")
#-------------------------------------
# Create images table
#-------------------------------------
def html_images(rootpath,fHandle,include_borders):
    fHandle.write("<tr><td class=\"header\">&nbsp;&nbsp;Images</td></tr>\n")
    #-------------------
    # Table header
    #-------------------
    fHandle.write("<tr><td>\n")
    fHandle.write("<table width=\"1000\" border=\"0\" align=\"center\" cellpadding=\"0\" cellspacing=\"0\">\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td height=\"25\" class=\"top_area\"><img src=\"" + pathStyleHtml + "/c.gif\"></td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td class=\"mid_area\">\n")
    if (include_borders == True):
        fHandle.write("  <table width=\"975\" border=\"1\" align=\"center\" cellpadding=\"5\" cellspacing=\"0\">\n")
    else:
        fHandle.write("  <table width=\"975\" border=\"0\" align=\"center\" cellpadding=\"5\" cellspacing=\"0\">\n")
    # headers
    fHandle.write("    <tr bgcolor=\"#FF9933\">\n")
    fHandle.write("     <td class=\"header_table\">Image</td>\n") 
    fHandle.write("     <td class=\"header_table\">Name</td>\n") 
    fHandle.write("     <td class=\"header_table\">Format</td>\n") 
    fHandle.write("     <td class=\"header_table\">Size</td>\n")
    fHandle.write("     <td class=\"header_table\">Path</td>\n") 
    fHandle.write("     <td class=\"header_table\">Linked</td>\n") 
    fHandle.write("    </tr>\n")
    #-------------------
    # Loop
    #-------------------
    flagImg = False
    imgs = bpy.data.images
    for image in imgs:
        if (image.name != "Render Result" and image.name != "Viewer Node"):
            (filepath, filename) = os.path.split("//.." + image.filepath)
            fHandle.write("    <tr>\n")
            z = ratio(image.size[0],image.size[1])
            filesave = os.path.splitext(filename)[0] + ".png"
            fHandle.write("     <td>"
                          + "<a href=\"" + pathImagesHtml + "/" + filesave + "\" target=\"_blank\">" 
                          + "<img src=\"" + pathImagesHtml + "/" + filesave 
                          + "\" width=\"" + str(z[0]) + "\" height=\"" + str(z[1]) + "\"></td>\n") 
            fHandle.write("     <td>" + image.name + "</td>\n") 
            fHandle.write("     <td>" + image.file_format + "</td>\n") 
            fHandle.write("     <td>" + str(image.size[0]) + "*" + str(image.size[1]) + "</td>\n")
            fHandle.write("     <td>" + image.filepath + "</td>\n") 
            if (image.is_library_indirect):
                fHandle.write("     <td>Yes</td>\n") 
            else:
                fHandle.write("     <td>No</td>\n") 
            fHandle.write("    </tr>\n")
            flagImg = True
            
    # NO images (message)
    if (flagImg == False):
            fHandle.write("    <tr>\n")
            fHandle.write("     <td colspan=\"5\">** No images found in blend file **</td>")
            fHandle.write("    </tr>\n")
       
    #-------------------
    # Table foot
    #-------------------
    fHandle.write("  </table>\n")
    fHandle.write(" </td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td height=\"25\" class=\"bottom_area\"><img src=\"" + pathStyleHtml + "/c.gif\"></td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("</table>\n")    
    fHandle.write("</td></tr>\n")
#-------------------------------------
# Create links table
#-------------------------------------
def html_links(rootpath,fHandle,include_borders):
    fHandle.write("<tr><td class=\"header\">&nbsp;&nbsp;Linked files</td></tr>\n")
    #-------------------
    # Table header
    #-------------------
    fHandle.write("<tr><td>\n")
    fHandle.write("<table width=\"1000\" border=\"0\" align=\"center\" cellpadding=\"0\" cellspacing=\"0\">\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td height=\"25\" class=\"top_area\"><img src=\"" + pathStyleHtml + "/c.gif\"></td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td class=\"mid_area\">\n")
    
    if (include_borders == True):
        fHandle.write("  <table width=\"975\" border=\"1\" align=\"center\" cellpadding=\"5\" cellspacing=\"0\">\n")
    else:
        fHandle.write("  <table width=\"975\" border=\"0\" align=\"center\" cellpadding=\"5\" cellspacing=\"0\">\n")
        
    # headers
    fHandle.write("    <tr bgcolor=\"#FF9933\">\n")
    fHandle.write("     <td class=\"header_table\">Path</td>\n") 
    fHandle.write("    </tr>\n")
    #-------------------
    # Loop
    #-------------------
    libs = bpy.data.libraries
    for lib in libs:
        fHandle.write("    <tr>\n")
        fHandle.write("     <td>" +  lib.filepath + "</td>\n") 
        fHandle.write("    </tr>\n")
       
    # NO Links (message)
    if (len(libs) == 0):
            fHandle.write("    <tr>\n")
            fHandle.write("     <td>** No linked files found in blend file **</td>")
            fHandle.write("    </tr>\n")
       
    #-------------------
    # Table foot
    #-------------------
    fHandle.write("  </table>\n")
    fHandle.write(" </td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("<tr>\n")
    fHandle.write(" <td height=\"25\" class=\"bottom_area\"><img src=\"" + pathStyleHtml + "/c.gif\"></td>\n")
    fHandle.write("</tr>\n")
    fHandle.write("</table>\n")    
    fHandle.write("</td></tr>\n")    
#-------------------------------------
# Save image to file
#-------------------------------------
def save_image(rootpath, filename,image):    
    try:
        filepath = rootpath + "/" + os.path.splitext(filename)[0] + ".png"

        # Save old info
        settings = bpy.context.scene.render.image_settings
        format = settings.file_format
        mode = settings.color_mode
        depth = settings.color_depth

        # Apply new info and save        
        settings.file_format = 'PNG'
        settings.color_mode = find_color_mode(image)
        settings.color_depth = '8'
        image.save_render(filepath)

        # Restore old info
        settings.file_format = format
        settings.color_mode = mode
        settings.color_depth = depth
    except:
        return
        #print("Unable to save")
#-------------------------------------
# Export images to folder
#-------------------------------------
def export_images(rootpath):
    print("\nExporting images...")
    imgs = bpy.data.images
    for image in imgs:
        name = image.name
        if (name != "Render Result" and name != "Viewer Node"): 
            (filepath, filename) = os.path.split("//.." + image.filepath)
            w = image.size[0]  
            h = image.size[1]  
          
            print("Image:" + name)
            print(' width: %d' % w)  
            print(' height: %d' % h)  
            save_image(rootpath,filename,image)    

#----------------------------------------------
# Code to run alone the script
#----------------------------------------------
if __name__ == "__main__":
    write_html("c:/tmp/html/test.htm", True)
    print("Executed")