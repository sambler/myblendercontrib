import bpy


class TextSyncPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_idname = "TextSyncPanel"
    bl_label = "text sync checker"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

    # def poll(self, context):
    #     text_block = context.edit_text
    #     print(dir(context))
    #     return True

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        scn = bpy.context.scene

        row = layout.row()
        row.scale_y = 4

        # show the operator if the text has
        # changed on disk.
        try:
            if context.edit_text.is_modified:
                row.operator("text.text_upsync")
        except:
            print('no \'is_modified\' to check yet')
