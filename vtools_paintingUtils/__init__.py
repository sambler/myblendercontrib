
bl_info = {
    "name": "vtools - Painting Utils",
    "author": "Antonio Mendoza",
    "location": "View3D > Sidebar > View Tab > Tool > Brush and Mask Texture",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "description": "What this addond does? 1 - Add the button for load an image as brush texture in the tool panel",
    "category": "Texture Painting"  
}


import bpy

def vt_addMaskImageTexture(self, context):
    
    textureMask = bpy.context.tool_settings.image_paint.brush.mask_texture
    
    if textureMask != None:
        layout = self.layout
        layout.separator()
        layout.label(text = "Brush Mask Image:")
        layout.template_image(textureMask, "image", textureMask.image_user)
    
def vt_addColorImageTexture(self, context):
    
    textureBrush = bpy.context.tool_settings.image_paint.brush.texture
    
    if textureBrush != None:
        layout = self.layout
        layout.separator()
        layout.label(text = "Brush Image:")
        layout.template_image(textureBrush, "image", textureBrush.image_user)

#------  REGISTER ---------------------


def register():
    
    from bpy.utils import register_class
    
    bpy.types.VIEW3D_PT_tools_mask_texture.append(vt_addMaskImageTexture)
    bpy.types.VIEW3D_PT_tools_brush_texture.append(vt_addColorImageTexture)
    
def unregister():
    from bpy.utils import unregister_class
    
        
    bpy.types.VIEW3D_PT_tools_mask_texture.remove(vt_addMaskImageTexture)
    bpy.types.VIEW3D_PT_tools_brush_texture.remove(vt_addColorImageTexture)
    
    
if __name__ == '__main__':
    register()
