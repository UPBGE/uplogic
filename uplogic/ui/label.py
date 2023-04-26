from .widget import Widget
import blf
from bge import render
from bpy.types import VectorFont


class Label(Widget):
    """Widget for displaying text"""

    def __init__(
        self,
        pos=[0, 0],
        bg_color=[0, 0, 0, 0],
        relative={},
        text='',
        font='',
        font_color=[1, 1, 1, 1],
        font_size=12,
        line_height=1.5,
        shadow=False,
        shadow_offset=[2, -2],
        shadow_color=[0, 0, 0, .6],
        halign='left',
        valign='bottom',
        wrap=False
    ):
        """
        :param parent: the widget's parent
        :param name: the name of the widget
        :param text: the text to display (this can be changed later via the text property)
        :param font: the font to use
        :param pt_size: the point size of the text to draw (defaults to 30 if None)
        :param bg_color: the color to use when rendering the font
        :param pos: a tuple containing the x and y position
        :param sub_theme: name of a sub_theme defined in the theme file (similar to CSS classes)
        :param options: various other options

        """
        self._parent = None
        self._children = None
        self._font_color = font_color
        self.text = text
        self.line_height = line_height
        self.shadow = shadow
        self.shadow_offset = shadow_offset
        self.shadow_color = shadow_color
        self.bg_color = bg_color
        self.font_size = font_size
        self.font_color = font_color
        self.font = font
        self.wrap = wrap
        Widget.__init__(self, pos, (0, 0), bg_color, relative)
        self.text_halign = halign
        self.text_valign = valign

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, val):
        self._text = str(val)

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, val):
        if isinstance(val, VectorFont):
            val = val.filepath.replace('\\', '/')
        self._font = blf.load(val) if val else 0

    @property
    def font_color(self):
        return self._font_color

    @font_color.setter
    def font_color(self, val):
        val = list(val)
        self._font_color = val

    @property
    def opacity(self):
        return self.bg_color[3]

    @opacity.setter
    def opacity(self, val):
        self.bg_color[3] = val
        self.font_opacity = val

    @property
    def font_opacity(self):
        return self._font_color[3]

    @font_opacity.setter
    def font_opacity(self, val):
        self._font_color[3] = val * self.opacity

    @property
    def _draw_size(self):
        # if self.parent is None:
        #     return [0, 0]
        return blf.dimensions(self.font, self.text)

    def draw(self):
        super()._setup_draw()
        if self.parent.use_clipping:
            verts = self.parent._vertices
            blf.enable(self.font, blf.CLIPPING)
            blf.clipping(self.font, verts[0][0], verts[0][1], verts[2][0], verts[2][1])
        else:
            blf.disable(self.font, blf.CLIPPING)
        if self.wrap:
            blf.enable(self.font, blf.WORD_WRAP)
            blf.word_wrap(self.font, self.size[0])
        if self.shadow:
            col = self.shadow_color
            blf.enable(self.font, blf.SHADOW)
            blf.shadow(self.font, 0, col[0], col[1], col[2], col[3])
            blf.shadow_offset(self.font, int(self.shadow_offset[0]), int(self.shadow_offset[1]))
        blf.size(self.font, self.font_size)
        blf.color(self.font, self.font_color[0], self.font_color[1], self.font_color[2], self.font_color[3])
        charsize = blf.dimensions(self.font, 'A')
        lines = [t for t in self.text.split('\n')]
        if len(lines) > 1:
            for i, txt in enumerate(lines):
                pos = self._draw_pos.copy()
                dimensions = blf.dimensions(self.font, txt)
                lheight = (charsize[1] * self.line_height)
                if self.text_halign == 'center':
                    pos[0] -= (dimensions[0] * .5)
                elif self.text_halign == 'right':
                    pos[0] -= dimensions[0]
                if self.text_valign == 'top':
                    pos[1] -= lheight
                elif self.text_valign == 'center':
                    pos[1] += (.5 * lheight * (len(lines) - 1)) - (.5 * lheight)
                elif self.text_valign == 'bottom':
                    pos[1] += (lheight * (len(lines) -2))
                blf.position(self.font, pos[0], pos[1] - (charsize[1] * i * self.line_height), 0)
                blf.draw(self.font, txt)
        else:
            dimensions = blf.dimensions(self.font, self.text)
            pos = self._draw_pos.copy()
            if self.text_halign == 'center':
                pos[0] -= (dimensions[0] * .5)
            elif self.text_halign == 'right':
                pos[0] -= dimensions[0]
            if self.text_valign == 'top':
                pos[1] -= dimensions[1]
            elif self.text_valign == 'center':
                pos[1] -= (.5 * dimensions[1])
            blf.position(self.font, pos[0], pos[1], 0)
            blf.draw(self.font, self.text)

        blf.disable(self.font, blf.WORD_WRAP)
        blf.disable(self.font, blf.SHADOW)
        super().draw()
