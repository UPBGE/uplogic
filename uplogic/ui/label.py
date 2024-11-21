from .widget import Widget
import blf
from bpy.types import VectorFont
from uplogic.utils.math import rotate2d
import math


class Label(Widget):
    '''Widget for displaying text

    :param `pos`: Initial position of this widget in either pixels or factor.
    :param `relative`: Whether to use pixels or factor for size or pos; example: `{'pos': True, 'size': True}`.
    :param `text`: Initial text for this label.
    :param `font`: Font name.
    :param `font_color`: Color in RGBA.
    :param `font_size`: Font size in pt or factor.
    :param `line_height`: Total line height relative to character size (1 is same as character height).
    :param `shadow`: Draw a shadow behind the text.
    :param `shadow_offset`: Relative position of the shadow in px.
    :param `shadow_color`: Shadow color in RGBA.
    :param `halign`: Horizontal alignment of the widget, can be (`left`, `center`, `right`).
    :param `valign`: Vertical alignment of the widget, can be (`bottom`, `center`, `top`).
    :param `wrap`: Split lines that are too long for the containing widget.
    :param `angle`: Rotation in degrees of this widget around the pivot defined by the alignment.
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

    # @property
    # def halign(self):
    #     return self.text_halign

    # @halign.setter
    # def halign(self, val):
    #     self.text_halign = str(val)

    # @property
    # def valign(self):
    #     return self.text_valign

    # @valign.setter
    # def valign(self, val):
    #     self.text_valign = str(val)

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

    # @property
    # def opacity(self):
    #     return self.bg_color[3]

    # @opacity.setter
    # def opacity(self, val):
    #     self.bg_color[3] = val
    #     self.font_opacity = val

    # @property
    # def font_opacity(self):
    #     return self._font_color[3]

    # @font_opacity.setter
    # def font_opacity(self, val):
    #     self._font_color[3] = val * self.opacity

    @property
    def dimensions(self):
        dim = blf.dimensions(self.font, self.text)
        lines = len(self.lines) or 1
        return (dim[0], blf.dimensions(self.font, 'Aj')[1] * lines)

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

    def draw(self):
        super()._setup_draw()
        if self.parent is None:
            return
        parsize = self.parent._draw_size
        relative = self.relative.get('font_size', False)
        font = self.font
        blf.size(font, parsize[1] * self.font_size if relative else self.font_size)
        col = self.font_color
        blf.color(font, col[0], col[1], col[2], col[3] * self.opacity)
        charsize = blf.dimensions(font, 'A')
        smallsize = blf.dimensions(font, 'a')[1]
        lowsize = blf.dimensions(font, 'g')[1]
        diff = lowsize - smallsize

        if self.angle or self.parent._draw_angle:
            blf.enable(font, blf.ROTATION)
            blf.rotation(font, math.radians(self._draw_angle))
        if self.parent.use_clipping:
            verts = self.parent._vertices
            blf.enable(font, blf.CLIPPING)
            blf.clipping(font, verts[0][0], verts[0][1] + charsize[1], verts[2][0], verts[2][1])
        else:
            blf.disable(font, blf.CLIPPING)
        if self.wrap and self.parent:
            offset = parsize[0] * self.pos[0] if self.relative.get('pos') else self.pos[0]
            blf.enable(font, blf.WORD_WRAP)
            blf.word_wrap(font, int(parsize[0] - offset))
        if self.shadow:
            col = self.shadow_color
            blf.enable(font, blf.SHADOW)
            blf.shadow(font, 0, col[0], col[1], col[2], col[3] * self.opacity)
            blf.shadow_offset(font, int(self.shadow_offset[0]), int(self.shadow_offset[1]))
        lines = [t for t in self.text.split('\n')]
        if len(lines) > 1:
            for i, txt in enumerate(lines):
                pos = self._draw_pos.copy()
                dimensions = blf.dimensions(font, txt)
                underground = dimensions[1] > charsize[1]
                lheight = (charsize[1] * self.line_height)
                if self.text_halign == 'center':
                    pos[0] -= (dimensions[0] * .5)
                elif self.text_halign == 'right':
                    pos[0] -= dimensions[0]
                if self.text_valign == 'top':
                    # if underground:
                    # pos[1] += (diff)
                    pos[1] -= lheight
                elif self.text_valign == 'center':
                    # if underground:
                        # pos[1] += (diff * .5)
                    pos[1] += (.5 * lheight * (len(lines) - 1)) - (.5 * lheight)
                elif self.text_valign == 'bottom':
                    pos[1] += (lheight * (len(lines) -2))
                if self.parent and self.parent._draw_angle:
                    pos = rotate2d(pos, self.pivot, self.parent.angle)
                blf.position(font, pos[0], pos[1] - (charsize[1] * i * self.line_height), 0)
                blf.draw(font, txt)
        else:
            dimensions = blf.dimensions(font, self.text)
            pos = self._draw_pos.copy()
            # underground = dimensions[1] > charsize[1]

            if self.text_halign == 'center':
                pos[0] -= (dimensions[0] * .5)
            elif self.text_halign == 'right':
                pos[0] -= dimensions[0]
            if self.text_valign == 'top':
                # if underground:
                    # pos[1] += diff
                pos[1] -= charsize[1] * self.line_height
            elif self.text_valign == 'center':
                # if underground:
                    # pos[1] += (diff * .5)
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
