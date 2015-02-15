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

# <pep8 compliant>

__all__ = (
    "wrap_text",
    "messagebox",
    "NestedLayout",
    "tag_redraw",
    )

import bpy
import blf

from mathutils import Color, Vector, Matrix, Quaternion, Euler

from .utils_python import AttributeHolder

#============================================================================#

# ===== SPLIT TEXT TO LINES ===== #
def split_word(width, x, max_x, word, lines, fontid=0):
    line = ""
    
    for c in word:
        x_dx = x + blf.dimensions(fontid, line+c)[0]
        
        if (x_dx) > width:
            x_dx = blf.dimensions(fontid, line)[0]
            lines.append(line)
            line = c
            x = 0
        else:
            line += c
        
        max_x = max(x_dx, max_x)
    
    return line, x, max_x

def split_line(width, x, max_x, line, lines, fontid=0):
    words = line.split(" ")
    line = ""
    
    for word in words:
        c = (word if not line else " " + word)
        x_dx = x + blf.dimensions(fontid, line+c)[0]
        
        if (x_dx) > width:
            x_dx = blf.dimensions(fontid, line)[0]
            if not line:
                # one word is longer than the width
                line, x, max_x = split_word(
                    width, x, max_x, word, lines, fontid)
            else:
                lines.append(line)
                line = word
            x = 0
        else:
            line += c
        
        max_x = max(x_dx, max_x)
    
    if line:
        lines.append(line)
    
    return max_x

def split_text(width, x, max_x, text, lines, fontid=0):
    for line in text.splitlines():
        if not line:
            lines.append("")
        else:
            max_x = split_line(width, x, max_x, line, lines, fontid)
        x = 0
    
    return max_x

def wrap_text(text, width, fontid=0, indent=0):
    """
    Splits text into lines that don't exceed the given width.
    text -- the text.
    width -- the width the text should fit into.
    fontid -- the id of the typeface as returned by blf.load().
        Defaults to 0 (the default font).
    indent -- the indent of the paragraphs.
        Defaults to 0.
    Returns: lines, actual_width
    lines -- the list of the resulting lines
    actual_width -- the max width of these lines
        (may be less than the supplied width).
    """
    lines = []
    max_x = 0
    for line in text.splitlines():
        if not line:
            lines.append("")
        else:
            max_x = split_line(width, indent, max_x, line, lines, fontid)
    return lines, max_x
#============================================================================#

# ===== MESSAGEBOX ===== #
class INFO_OT_messagebox(bpy.types.Operator):
    bl_idname = "info.messagebox"
    
    # "Attention!" is quite generic caption that suits
    # most of the situations when "OK" button is desirable.
    # bl_label isn't really changeable at runtime
    # (changing it causes some memory errors)
    bl_label = "Attention!"
    
    # We can't pass arguments through normal means,
    # since in this case a "Reset" button would appear
    args = {}
    
    # If we don't define execute(), there would be
    # an additional label "*Redo unsupported*"
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        text = self.args.get("text", "")
        self.icon = self.args.get("icon", 'NONE')
        if (not text) and (self.icon == 'NONE'):
            return {'CANCELLED'}
        
        border_w = 8*2
        icon_w = (0 if (self.icon == 'NONE') else 16)
        w_incr = border_w + icon_w
        
        width = self.args.get("width", 300) - border_w
        
        self.lines = []
        max_x = split_text(width, icon_w, 0, text, self.lines)
        width = max_x + border_w
        
        self.spacing = self.args.get("spacing", 0.5)
        self.spacing = max(self.spacing, 0.0)
        
        wm = context.window_manager
        
        confirm = self.args.get("confirm", False)
        
        if confirm:
            return wm.invoke_props_dialog(self, width)
        else:
            return wm.invoke_popup(self, width)
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column()
        col.scale_y = 0.5 * (1.0 + self.spacing * 0.5)
        
        icon = self.icon
        for line in self.lines:
            col.label(text=line, icon=icon)
            icon = 'NONE'

bpy.utils.register_class(INFO_OT_messagebox) # REGISTER

def messagebox(text, icon='NONE', width=300, confirm=False, spacing=0.5):
    """
    Displays a message box with the given text and icon.
    text -- the messagebox's text
    icon -- the icon (displayed at the start of the text)
        Defaults to 'NONE' (no icon).
    width -- the messagebox's max width
        Defaults to 300 pixels.
    confirm -- whether to display "OK" button (this is purely
        cosmetical, as the message box is non-blocking).
        Defaults to False.
    spacing -- relative distance between the lines
        Defaults to 0.5.
    """
    INFO_OT_messagebox.args["text"] = text
    INFO_OT_messagebox.args["icon"] = icon
    INFO_OT_messagebox.args["width"] = width
    INFO_OT_messagebox.args["spacing"] = spacing
    INFO_OT_messagebox.args["confirm"] = confirm
    bpy.ops.info.messagebox('INVOKE_DEFAULT')
#============================================================================#

# ===== NESTED LAYOUT ===== #
class NestedLayout:
    """
    Utility for writing more structured UI drawing code.
    Attention: layout properties are propagated to sublayouts!
    
    Example:
    
    def draw(self, context):
        layout = NestedLayout(self.layout, self.bl_idname)
        
        exit_layout = True
        
        # You can use both the standard way:
        
        sublayout = layout.split()
        sublayout.label("label A")
        sublayout.label("label B")
        
        # And the structured way:
        
        with layout:
            layout.label("label 1")
            if exit_layout: layout.exit()
            layout.label("label 2") # won't be executed
        
        with layout.row(True)["main"]:
            layout.label("label 3")
            with layout.row(True)(enabled=False):
                layout.label("label 4")
                if exit_layout: layout.exit("main")
                layout.label("label 5") # won't be executed
            layout.label("label 6") # won't be executed
        
        with layout.fold("Foldable micro-panel", "box"):
            if layout.folded: layout.exit()
            layout.label("label 7")
            with layout.fold("Foldable 2"):
                layout.label("label 8") # not drawn if folded
    """
    
    _sub_names = {"row", "column", "column_flow", "box", "split", "menu_pie"}
    
    _default_attrs = dict(
        active = True,
        alert = False,
        alignment = 'EXPAND',
        enabled =  True,
        operator_context = 'INVOKE_DEFAULT',
        scale_x = 1.0,
        scale_y = 1.0,
    )
    
    def __new__(cls, layout, idname="", parent=None):
        """
        Wrap the layout in a NestedLayout.
        To avoid interference with other panels' foldable
        containers, supply panel's bl_idname as the idname.
        """
        if isinstance(layout, cls):
            return layout
        
        self = object.__new__(cls)
        self._idname = idname
        self._parent = parent
        self._layout = layout
        self._stack = [self]
        self._attrs = dict(self._default_attrs)
        self._tag = None
        
        if parent:
            # propagate settings to sublayouts
            self(**parent._stack[-1]._attrs)
        
        return self
    
    def __getattr__(self, name):
        layout = self._stack[-1]._layout
        if not layout:
            # This is the dummy layout; imitate normal layout
            # behavior without actually drawing anything.
            if name in self._sub_names:
                return (lambda *args, **kwargs:
                    NestedLayout(None, self._idname, self))
            else:
                return self._attrs.get(name, self._dummy_callable)
        
        if name in self._sub_names:
            func = getattr(layout, name)
            return (lambda *args, **kwargs:
                NestedLayout(func(*args, **kwargs), self._idname, self))
        else:
            return getattr(layout, name)
    
    def __setattr__(self, name, value):
        if name.startswith("_"):
            self.__dict__[name] = value
        else:
            wrapper = self._stack[-1]
            wrapper._attrs[name] = value
            if wrapper._layout:
                setattr(wrapper._layout, name, value)
    
    def __call__(self, **kwargs):
        """Batch-set layout attributes."""
        wrapper = self._stack[-1]
        wrapper._attrs.update(kwargs)
        layout = wrapper._layout
        if layout:
            for k, v in kwargs.items():
                setattr(layout, k, v)
        return self
    
    @staticmethod
    def _dummy_callable(*args, **kwargs):
        pass
    
    # ===== FOLD (currently very hacky) ===== #
    # Each foldable micropanel needs to store its fold-status
    # as a Bool property (in order to be clickable in the UI)
    # somewhere where it would be saved with .blend, but won't
    # be affected by most of the other things (i.e., in Screen).
    # At first I thought to implement such storage with
    # nested dictionaries, but currently layout.prop() does
    # not recognize ID-property dictionaries as a valid input.
    class FoldPG(bpy.types.PropertyGroup):
        # indicates that the widget needs to be force-updated
        changed = bpy.props.BoolProperty()
        def update(self, context):
            self.changed = True
        value = bpy.props.BoolProperty(description="Fold/unfold", update=update, name="")
    bpy.utils.register_class(FoldPG) # REGISTER
    
    # make up some name that's unlikely to be used by normal addons
    folds_keyname = "bpy_extras_ui_utils_NestedLayout_ui_folds"
    setattr(bpy.types.Screen, folds_keyname, bpy.props.CollectionProperty(type=FoldPG)) # REGISTER
    
    folded = False # stores folded status from the latest fold() call
    
    def fold(self, text, container=None, folded=False, key=None):
        """
        Create a foldable container.
        text -- the container's title/label
        container -- a sequence (type_of_container, arg1, ..., argN)
            where type_of_container is one of {"row", "column",
            "column_flow", "box", "split"}; arg1..argN are the
            arguments of the corresponding container function.
            If you supply just the type_of_container, it would be
            interpreted as (type_of_container,).
        folded -- whether the container should be folded by default.
            Default value is False.
        key -- the container's unique identifier within the panel.
            If not specified, the container's title will be used
            in its place.
        """
        data_path = "%s:%s" % (self._idname, key or text)
        folds = getattr(bpy.context.screen, self.folds_keyname)
        
        try:
            this_fold = folds[data_path]
        except KeyError:
            this_fold = folds.add()
            this_fold.name = data_path
            this_fold.value = folded
        
        is_fold = this_fold.value
        icon = ('DOWNARROW_HLT' if not is_fold else 'RIGHTARROW')
        
        # make the necessary container...
        if not container:
            container = "column"
            container_args = ()
        elif isinstance(container, str):
            container_args = ()
        else:
            container_args = container[1:]
            container = container[0]
        res = getattr(self, container)(*container_args)
        
        with res.row(True)(alignment='LEFT'):
            if not this_fold.changed:
                res.prop(this_fold, "value", text=text, icon=icon,
                    emboss=False, toggle=True)
            else:
                # Blender won't redraw active UI element
                # until user moves mouse out of its bounding box.
                # To force update, we have to actually "delete"
                # and "recreate" the element (achieved by
                # replacing it with label)
                res.label(text=text, icon=icon)
                this_fold.changed = False
        
        # make fold-status accessible to the calling code
        self.__dict__["folded"] = is_fold
        
        if is_fold:
            # If folded, return dummy layout
            return NestedLayout(None, self._idname, self)
        
        return res
    
    # ===== NESTED CONTEXT MANAGEMENT ===== #
    class ExitSublayout(Exception):
        def __init__(self, tag=None):
            self.tag = tag
    
    @classmethod
    def exit(cls, tag=None):
        """
        Jump out of current (or marked with the given tag) layout's context.
        """
        raise cls.ExitSublayout(tag)
    
    def __getitem__(self, tag):
        """Mark this layout with the tag"""
        self._tag = tag
        return self
    
    def __enter__(self):
        # Only nested (context-managed) layouts are stored in stack
        parent = self._parent
        if parent:
            parent._stack.append(self)
    
    def __exit__(self, type, value, traceback):
        # Only nested (context-managed) layouts are stored in stack
        parent = self._parent
        if parent:
            parent._stack.pop()
        
        if type == self.ExitSublayout:
            # Is this the layout the exit() was requested for?
            # Yes: suppress the exception. No: let it propagate to the parent.
            return (value.tag is None) or (value.tag == self._tag)

#============================================================================#

def tag_redraw(arg=None):
    """A utility function to tag redraw of arbitrary UI units."""
    if arg is None:
        arg = bpy.context.window_manager
    elif isinstance(arg, bpy.types.Window):
        arg = arg.screen
    
    if isinstance(arg, bpy.types.Screen):
        for area in arg.areas:
            area.tag_redraw()
    elif isinstance(arg, bpy.types.WindowManager):
        for window in arg.windows:
            for area in window.screen.areas:
                area.tag_redraw()
    else: # Region, Area, RenderEngine
        arg.tag_redraw()

def calc_region_rect(area, r, overlap=True):
    # Note: there may be more than one region of the same type (e.g. in quadview)
    if (not overlap) and (r.type == 'WINDOW'):
        x0, y0, x1, y1 = r.x, r.y, r.x+r.width, r.y+r.height
        ox0, oy0, ox1, oy1 = x0, y0, x1, y1
        for r in area.regions:
            if r.type == 'TOOLS':
                ox0 = r.x + r.width
            elif r.type == 'UI':
                ox1 = r.x
        x0, y0, x1, y1 = max(x0, ox0), max(y0, oy0), min(x1, ox1), min(y1, oy1)
        return (Vector((x0, y0)), Vector((x1-x0, y1-y0)))
    else:
        return (Vector((r.x, r.y)), Vector((r.width, r.height)))

def point_in_rect(p, r):
    return ((p[0] >= r.x) and (p[0] < r.x + r.width)
            and (p[1] >= r.y) and (p[1] < r.y + r.height))

def rv3d_from_region(area, region):
    if (area.type != 'VIEW_3D') or (region.type != 'WINDOW'):
        return None
    
    space_data = area.spaces.active
    try:
        quadviews = space_data.region_quadviews
    except AttributeError:
        quadviews = None # old API
    
    if not quadviews:
        return space_data.region_3d
    
    x_id = 0
    y_id = 0
    for r in area.regions:
        if (r.type == 'WINDOW') and (r != region):
            if r.x < region.x:
                x_id = 1
            if r.y < region.y:
                y_id = 1
    
    # 0: bottom left (Front Ortho)
    # 1: top left (Top Ortho)
    # 2: bottom right (Right Ortho)
    # 3: top right (User Persp)
    return quadviews[y_id | (x_id << 1)]

# areas can't overlap, but regions can
def ui_contexts_under_coord(x, y):
    point = int(x), int(y)
    window = bpy.context.window
    screen = window.screen
    for area in screen.areas:
        if point_in_rect(point, area):
            space_data = area.spaces.active
            for region in area.regions:
                if point_in_rect(point, region):
                    yield dict(window=window, screen=screen,
                        area=area, region=region, space_data=space_data,
                        region_data=rv3d_from_region(area, region))
            break

def ui_context_under_coord(x, y, index=0):
    ui_context = None
    for i, ui_context in enumerate(ui_contexts_under_coord(x, y)):
        if i == index:
            return ui_context
    return ui_context

# TODO: relative coords?
def convert_ui_coord(window, area, region, xy, src, dst, vector=True):
    x, y = xy
    if src == dst:
        pass
    elif src == 'WINDOW':
        if dst == 'AREA':
            x -= area.x
            y -= area.y
        elif dst == 'REGION':
            x -= region.x
            y -= region.y
    elif src == 'AREA':
        if dst == 'WINDOW':
            x += area.x
            y += area.y
        elif dst == 'REGION':
            x += area.x - region.x
            y += area.y - region.y
    elif src == 'REGION':
        if dst == 'WINDOW':
            x += region.x
            y += region.y
        elif dst == 'AREA':
            x += region.x - area.x
            y += region.y - area.y
    return (Vector((x, y)) if vector else (int(x), int(y)))

#============================================================================#
