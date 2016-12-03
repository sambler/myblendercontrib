import bpy
import blf, bgl


class ShowHelp(bpy.types.Operator):
    bl_idname = "coa_tools.show_help"
    bl_label = "Show Help"
    bl_description = "Show Help"
    bl_options = {"REGISTER"}

    region_offset = 0
    region_height = 0
    _timer = None
    alpha = 1.0
    alpha_current = 0.0
    i = 0
    fade_in = False
    @classmethod
    def poll(cls, context):
        return True

    def write_text(self,text,size=20,pos_y=0,color=(1,1,1,1)):
        lines = text.split("\n")
        
        bgl.glColor4f(color[0],color[1],color[2],color[3]*self.alpha_current)
        line_height = size + size*.5
        for i,line in enumerate(lines):
            
            blf.position(self.font_id, 15+self.region_offset, pos_y-(line_height*i), 0)
            blf.size(self.font_id, size, 72)
            blf.draw(self.font_id, line)
            
    def invoke(self, context, event):
        wm = context.window_manager
        wm.coa_show_help = True
        args = ()
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        self._timer = wm.event_timer_add(0.1, context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
    
    def fade(self):
        self.alpha_current = self.alpha_current*.55 + self.alpha*.45
            
    def modal(self, context, event):
        wm = context.window_manager
        context.area.tag_redraw()
        if context.user_preferences.system.use_region_overlap:
            for region in context.area.regions:
                if region.type == "TOOLS":
                    self.region_offset = region.width
                if region.type == "WINDOW":    
                    self.region_height = region.height
        else:
            self.region_offset = 0
        
        if not wm.coa_show_help:
            self.alpha = 0.0
            
        if not wm.coa_show_help and round(self.alpha_current,1) == 0:#event.type in {"RIGHTMOUSE", "ESC"}:
            return self.finish()
        
        if self.alpha != round(self.alpha_current,1):
            self.fade()
            
        return {"PASS_THROUGH"}

    def finish(self):
        context = bpy.context
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}

    def draw_callback_px(self):
        self.font_id = 0  # XXX, need to find out how best to get this.
        global_pos = self.region_height - 60
        # draw some text
        headline_color = [1.0, 0.9, 0.6, 1.0]
        
        ### draw gradient overlay
        bgl.glEnable(bgl.GL_BLEND)
        
        line_width = 10
        bgl.glLineWidth(line_width)
        width = int(525/line_width)
        start_at = .2
        for i in range(width):
            bgl.glBegin(bgl.GL_LINE_STRIP)
            alpha = (width-i)/width/(1-start_at)

            if i > width*start_at:
                bgl.glColor4f(0.0, 0.0, 0.0, .7*self.alpha_current*alpha)
            else:
                bgl.glColor4f(0.0, 0.0, 0.0, .7*self.alpha_current)
            x = (i*line_width) + self.region_offset
            y = self.region_height
            bgl.glVertex2i(x, 0)
            bgl.glVertex2i(x, y)
            bgl.glEnd()

        
        ### draw hotkeys        
        self.write_text("Hotkeys - Object Mode",size=20,pos_y=global_pos,color=headline_color)
        self.write_text("   F   -   Contextual Pie Menu",size=15,pos_y=global_pos-20)
        
        self.write_text("Hotkeys - Object Outliner",size=20,pos_y=global_pos-60,color=headline_color)
        self.write_text("   Ctrl + Click    -   Add Item to Selection",size=15,pos_y=global_pos-80)
        self.write_text("   Shift + Click   -   Multi Selection",size=15,pos_y=global_pos-100)
        
        self.write_text("Hotkeys - Keyframing",size=20,pos_y=global_pos-160,color=headline_color)
        self.write_text("   Ctrl + Click on Key Operator    -   Opens Curve Interpolation Options",size=15,pos_y=global_pos-180)
        
        self.write_text("Hotkeys - Edit Armature Mode",size=20,pos_y=global_pos-240,color=headline_color)
        self.write_text("   Click + Drag    -   Draw Bone",size=15,pos_y=global_pos-260)
        self.write_text("   Shift + Click + Drag    -   Draw Bone locked to 45 Angle",size=15,pos_y=global_pos-280)
        self.write_text("   Alt + Click    -    Bind Sprite to selected Bones",size=15,pos_y=global_pos-300)
        self.write_text("   ESC/Tab    -    Exit Armature Mode",size=15,pos_y=global_pos-320)
        
        self.write_text("Hotkeys - Edit Mesh Mode",size=20,pos_y=global_pos-380,color=headline_color)
        self.write_text("   Click + Drag    -   Draw Vertex Contour",size=15,pos_y=global_pos-400)
        self.write_text("   Alt + Click on Vertex   -   Close Contour",size=15,pos_y=global_pos-420)
        self.write_text("   ESC/Tab    -    Exit Mesh Mode",size=15,pos_y=global_pos-440)
        
        # restore opengl defaults
        bgl.glLineWidth(1)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)