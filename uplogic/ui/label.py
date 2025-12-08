from .widget import Widget
from .widget import ALIGNMENTS
from .widget import ALIGN_TOP
from .widget import ALIGN_BOTTOM
from .widget import ALIGN_CENTER
from .widget import ALIGN_LEFT
from .widget import ALIGN_RIGHT
import blf
from bpy.types import VectorFont
from uplogic.utils.math import rotate2d
from mathutils import Vector
import math


class Label(Widget):
    '''Widget for displaying text

    :param pos: Initial position of this widget in either pixels or factor.
    :param relative: Whether to use pixels or factor for size or pos; example: `{'pos': True, 'size': True}`.
    :param text: Initial text for this label.
    :param font: Font name.
    :param font_color: Color in RGBA.
    :param font_size: Font size in pt or factor.
    :param line_height: Total line height relative to character size (1 is same as character height).
    :param shadow: Draw a shadow behind the text.
    :param shadow_offset: Relative position of the shadow in px.
    :param shadow_color: Shadow color in RGBA.
    :param halign: Horizontal alignment of the widget, can be (`left`, `center`, `right`).
    :param valign: Vertical alignment of the widget, can be (`bottom`, `center`, `top`).
    :param wrap: Split lines that are too long for the containing widget.
    :param angle: Rotation in degrees of this widget around the pivot defined by the alignment.
    '''

    def __init__(
        self,
        pos=[0, 0],
        relative={},
        text='',
        font='',
        font_color=[1., 1., 1., 1.],
        font_size=12,
        line_height=1.5,
        shadow=False,
        shadow_offset=[1, -1],
        shadow_color=[.0, .0, .0, 1.],
        halign='left',
        valign='bottom',
        wrap=False,
        angle=0,
        show=True
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
        self.lines = []
        Widget.__init__(self, pos, (0, 0), (0, 0, 0, 0), relative, angle=angle, show=show)
        self.text_halign = halign
        self.text_valign = valign
        self.start()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, val):
        self._text = str(val)

    @property
    def text_halign(self):
        return self._text_halign

    @text_halign.setter
    def text_halign(self, val):
        self._text_halign = ALIGNMENTS.get(val, val)

    @property
    def text_valign(self):
        return self._text_valign

    @text_valign.setter
    def text_valign(self, val):
        self._text_valign = ALIGNMENTS.get(val, val)

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
    def color(self):
        return self.font_color

    @color.setter
    def color(self, val):
        self.font_color = val

    @property
    def dimensions(self):
        text = self.text
        if len(self.lines):
            text = max(self.lines, key=len)
        dim = blf.dimensions(self.font, text)
        lines = len(self.lines) or 1
        return Vector((dim[0], blf.dimensions(self.font, 'A')[1] * lines * self.line_height - self.line_height))

    @property
    def _draw_size(self):
        relative = self.relative.get('font_size', False)
        fontsize = self.parent._draw_size[1] * self.font_size if relative else self.font_size
        blf.size(self.font, fontsize)
        return self.dimensions

    def make_floating(self, pos=True, size=True, halign='center', valign='center'):
        self.relative['pos'] = pos
        self.relative['size'] = size
        self.text_halign = halign
        self.text_valign = valign
        return self

    def _wrap(self, parsize):
        if self.dimensions[0] < parsize[0]:
            return self.text
        offset = parsize[0] * self.pos[0] if self.relative.get('pos') else self.pos[0]
        max_width = int(parsize[0] - offset)
        text = ''
        words = self.text.split(' ')

        for i, w in enumerate(words):
            line = text.split('\n')[-1]
            blf.size(self.font, self.font_size)
            dim = blf.dimensions(self.font, line + w)
            too_long = dim[0] >= max_width
            if too_long:
                w = f'\n{w}'
            text = ' '.join([text, w])
        return text[1:]

    def draw(self):
        self._setup_draw()
        if self.parent is None:
            return
        parsize = self.parent._draw_size
        relative = self.relative.get('font_size', False)
        font = self.font
        blf.size(font, parsize[1] * self.font_size if relative else self.font_size)
        col = self.font_color
        blf.color(font, col[0], col[1], col[2], col[3] * self.opacity)
        charsize = blf.dimensions(font, 'A')

        if self.angle or self.parent._draw_angle:
            blf.enable(font, blf.ROTATION)
            blf.rotation(font, math.radians(self._draw_angle))
        if self.parent.use_clipping:
            verts = self.parent._vertices
            blf.enable(font, blf.CLIPPING)
            blf.clipping(font, verts[0][0], verts[0][1], verts[2][0], verts[2][1] - charsize[1]*2)
        else:
            blf.disable(font, blf.CLIPPING)
        if self.shadow:
            col = self.shadow_color
            blf.enable(font, blf.SHADOW)
            blf.shadow(font, 0, col[0], col[1], col[2], col[3] * self.opacity)
            blf.shadow_offset(font, int(self.shadow_offset[0]), int(self.shadow_offset[1]))
        txt = self._wrap(parsize) if self.wrap else self.text
        lines = txt.split('\n')
        if len(lines) > 1:
            for i, txt in enumerate(lines):
                pos = self._draw_pos.copy()
                dimensions = blf.dimensions(font, txt)
                lheight = (charsize[1] * self.line_height)
                if self.text_halign == ALIGN_CENTER:
                    pos[0] -= (dimensions[0] * .5)
                elif self.text_halign == ALIGN_RIGHT:
                    pos[0] -= dimensions[0]
                if self.text_valign == ALIGN_TOP:
                    pos[1] -= lheight
                elif self.text_valign == ALIGN_CENTER:
                    pos[1] += (.5 * lheight * (len(lines) - 1)) - (.5 * lheight)
                elif self.text_valign == ALIGN_BOTTOM:
                    pos[1] += (lheight * (len(lines) -2))
                if self.parent and self.parent._draw_angle:
                    pos = rotate2d(pos, self.pivot, self.parent.angle)
                blf.position(font, pos[0], pos[1] - (charsize[1] * (i) * self.line_height), 0)
                blf.draw(font, txt)
        else:
            dimensions = blf.dimensions(font, self.text)
            pos = self._draw_pos.copy()

            if self.text_halign == ALIGN_CENTER:
                pos[0] -= (dimensions[0] * .5)
            elif self.text_halign == ALIGN_RIGHT:
                pos[0] -= dimensions[0]
            if self.text_valign == ALIGN_TOP:
                pos[1] -= charsize[1] * self.line_height
            elif self.text_valign == ALIGN_CENTER:
                pos[1] -= (.5 * charsize[1])
            if self.parent and self.parent._draw_angle:
                pos = rotate2d(pos, self.pivot, self.parent.angle)
            blf.position(font, pos[0], pos[1], 0)
            blf.draw(font, self.text)

        super().draw()
        self.lines = lines
        blf.disable(font, blf.WORD_WRAP)
        blf.disable(font, blf.SHADOW)
        blf.disable(font, blf.ROTATION)
