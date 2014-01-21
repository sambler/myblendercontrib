
# original script copied from
# http://www.blenderartists.org/forum/showthread.php?312821-Run-Script-in-PyConsole-%28Menu%29

bl_info = {
    "name": "Run Script in PyConsole",
    "author": "CoDEmanX",
    "version": (1, 0),
    "blender": (2, 67, 0),
    "location": "Python Console > Console > Run Script",
    "description": "Execute the code of a textblock within the python console.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"}

import bpy

def main(self, context):
    text = bpy.data.texts.get(self.text)
    if text is not None:
        text = "exec(compile(" + repr(text) + ".as_string(), '" + text.name + "', 'exec'))"
        bpy.ops.console.clear_line()
        bpy.ops.console.insert(text=text)
        bpy.ops.console.execute()

class CONSOLE_OT_run_script(bpy.types.Operator):
    """Run a text datablock in PyConsole"""
    bl_idname = "console.run_code"
    bl_label = "Run script"

    text = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}


def get_texts(context):
    l = []
    for area in context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            text = area.spaces[0].text
            if text is not None and text not in l:
                l.append(text)
    return {'visible': [t.name for t in l],
            'invisible': [t.name for t in bpy.data.texts if t not in l]}

class CONSOLE_MT_run_script(bpy.types.Menu):
    bl_label = "Run script"
    bl_idname = "CONSOLE_MT_run_script"

    def draw(self, context):
        layout = self.layout
        texts = get_texts(context)
        visible, invisible = texts['visible'], texts['invisible']

        if not (visible or invisible):
            layout.label("No text blocks!")
        else:
            if invisible:
                for t in invisible:
                    layout.operator(CONSOLE_OT_run_script.bl_idname, text=t).text = t
            if visible and invisible:
                layout.separator()
            if visible:
                for t in visible:
                    layout.operator(CONSOLE_OT_run_script.bl_idname, text=t, icon='VISIBLE_IPO_ON').text = t

def draw_item(self, context):
    layout = self.layout
    layout.menu(CONSOLE_MT_run_script.bl_idname)


def register():
    bpy.utils.register_module(__name__)
    bpy.types.CONSOLE_MT_console.prepend(draw_item)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.CONSOLE_MT_console.remove(draw_item)


if __name__ == "__main__":
    register()
