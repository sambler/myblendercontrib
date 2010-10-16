# retrieving the masterlist with all icon names
bl_addon_info = {
    'name': 'Display All Icons',
    'author': '',
    'version': '0.3.2',
    'blender': (2, 5, 3),
    'location': 'Object > Properties',
    'description': 'Fetch Icons * display',
    'url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/' \
        'Scripts/',
    'category': 'System'}
import bpy
try:
    import urllib.request
    file = urllib.request.urlopen('https://svn.blender.org/svnroot/bf-blender/trunk/blender/source/blender/editors/include/UI_icons.h')
except:
    print("Couldn't find the urllib module or was unable to connect to the internet")
    file = False
if file:
    lines = str(file.read()).split('\\n')
else:
    lines = []

# get the icon names of existing non-blank icons
icons = []
for l in lines:
    if l[:9] == 'DEF_ICON(':
        n = l.strip().split('(')[1].split(')')[0]
        if n[:10] != 'ICON_BLANK':
            icons.append(n[5:])

# create custom operator for each icon
def printdoc_invoke(self, context, event):
    print(self.bl_description)
    return{'FINISHED'}
for i in icons:
    c = type(i,(bpy.types.Operator,),dict(bl_idname="ICONDISPLAY_OT_"+i, bl_label="ICONDISPLAY_OT_"+i, bl_description=i))
    setattr(c, 'invoke', printdoc_invoke)
    bpy.types.register(c)

# draw the panel with the icons
class OBJECT_PT_icons(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "All icons"
    
    def draw(self, context):
        amount = 10
        cols = []
        layout = self.layout
        split = layout.split(percentage=1.0/amount)
        for i in range(amount):
            cols.append(split.column())
        for i in range(len(icons)):
            col = cols[i%amount].row()
            try:
                col.operator("icondisplay."+icons[i], text="", icon=icons[i])
            except:
                col.operator("icondisplay."+icons[i], text="new")

###################################
def register():
    pass

def unregister():
    pass

if __name__ == "__main__":
    register()
