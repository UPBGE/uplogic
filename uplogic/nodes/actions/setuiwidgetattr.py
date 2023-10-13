from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
import bpy

attrs = {
    "show": 'bool_value',
    "color": 'color_value',
    "opacity": 'alpha_value',
    "pos": 'vec2_value',
    "size": 'vec2_value',
    "angle": 'angle_value',
    "width": 'float_value',
    "height": 'float_value',
    "use_clipping": 'bool_value',
    "halign": 'str_value',
    "valign": 'str_value',
    "border_width": 'int_value',
    "border_color": 'color_value',
    "orientation": 'str_value',
    "spacing": 'int_value',
    "hover_color": 'color_value',
    "text": 'str_value',
    "font": 'font_value',
    "font_color": 'color_value',
    "font_size": 'int_value',
    "font_opacity": 'alpha_value',
    "line_height": 'float_value',
    "text_halign": 'str_value',
    "text_valign": 'str_value',
    "wrap": 'bool_value',
    "shadow": 'bool_value',
    "shadow_offset": 'vec2_value',
    "shadow_color": 'color_value',
    "texture": 'img_value',
    "icon": 'int_value',
    "rows": 'int_value',
    "cols": 'int_value',
}


class ULSetUIWidgetAttr(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.widget = None
        self.bool_value = None
        self.color_value = None
        self.alpha_value = None
        self.vec2_value = None
        self.str_value = None
        self.int_value = None
        self.float_value = None
        self.font_value = None
        self.img_value = None
        self.widget_attr = 'show'
        self.show = None
        self._done = False
        self.OUT = ULOutSocket(self, self._get_done)

    def _get_done(self):
        return self._done

    def evaluate(self):
        self._done = False
        if not self.get_input(self.condition):
            return
        widget = self.get_input(self.widget)
        value = self.get_input(getattr(self, attrs.get(self.widget_attr, 0)))
        if self.widget_attr in ['font', 'texture']:
            value = value.filepath.replace('\\', '/') if value else 0
        setattr(widget, self.widget_attr, value)
        self._done = True
