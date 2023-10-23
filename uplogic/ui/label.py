from .widget import Widget
import blf
from bpy.types import VectorFont
from uplogic.utils.math import rotate2d
import math


class Label(Widget):
    '''Widget for displaying text

    :param `orientation`: Whether to arrange widgets horizontally or vertically; Can be (`'horizontal'`, `'vertical'`).
    :param `pos`: Initial position of this widget in either pixels or factor.
    :param `relative`: Whether to use pixels or factor for size or pos; example: {`'pos'`: `True`, `'size'`: `True`}.
    :param `halign`: Horizontal alignment of the widget, can be (`left`, `center`, `right`).
    :param `valign`: Vertical alignment of the widget, can be (`bottom`, `center`, `top`).
    :param `angle`: Rotation in degrees of this widget around the pivot defined by the alignment.
    '''

    def __init__(
        self,
        pos=[0, 0],
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
        wrap=False,
        angle=0
    ):
        self._parent = None
        self._children = None
        self._font_color = font_color
        self.text = text
        self.line_height = line_height
        self.shadow = shadow
        self.shadow_offset = shadow_offset
        self.shadow_color = shadow_color
        self.font_size = font_size
        self.font_color = font_color
        self.font = font
        self.wrap = wrap
        Widget.__init__(self, pos, (0, 0), (0, 0, 0, 0), relative, angle=angle)
        self.text_halign = halign
        self.text_valign = valign

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, val):
        self._text = str(val)

    @property
    def pos_abs(self):
        return self._draw_pos

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
    def dimensions(self):
        return blf.dimensions(self.font, self.text)

    @property
    def _draw_size(self):
        return blf.dimensions(self.font, self.text)

    def draw(self):
        super()._setup_draw()
        blf.size(self.font, self.font_size)
        blf.color(self.font, self.font_color[0], self.font_color[1], self.font_color[2], self.font_color[3])
        charsize = blf.dimensions(self.font, 'A')
        if self.angle or self.parent._draw_angle:
            blf.enable(self.font, blf.ROTATION)
            blf.rotation(self.font, math.radians(self._draw_angle))
        if self.parent.use_clipping:
            verts = self.parent._vertices
            blf.enable(self.font, blf.CLIPPING)
            blf.clipping(self.font, verts[0][0], verts[0][1] + charsize[1], verts[2][0], verts[2][1])
        else:
            blf.disable(self.font, blf.CLIPPING)
        if self.wrap and self.parent:
            blf.enable(self.font, blf.WORD_WRAP)
            blf.word_wrap(self.font, self.parent._draw_size[0])
        if self.shadow:
            col = self.shadow_color
            blf.enable(self.font, blf.SHADOW)
            blf.shadow(self.font, 0, col[0], col[1], col[2], col[3])
            blf.shadow_offset(self.font, int(self.shadow_offset[0]), int(self.shadow_offset[1]))
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
                if self.parent and self.parent._draw_angle:
                    pos = rotate2d(pos, self.pivot, self.parent.angle)
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
            if self.parent and self.parent._draw_angle:
                pos = rotate2d(pos, self.pivot, self.parent.angle)
            blf.position(self.font, pos[0], pos[1], 0)
            blf.draw(self.font, self.text)

        blf.disable(self.font, blf.WORD_WRAP)
        blf.disable(self.font, blf.SHADOW)
        blf.disable(self.font, blf.ROTATION)
        super().draw()
