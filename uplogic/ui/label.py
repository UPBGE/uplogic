from .widget import Widget
from .widget import ALIGNMENTS
from .widget import ALIGN_TOP
from .widget import ALIGN_BOTTOM
from .widget import ALIGN_CENTER
from .widget import ALIGN_LEFT
from .widget import ALIGN_RIGHT
import blf
import re
from bpy.types import VectorFont
from uplogic.utils.math import rotate2d
from mathutils import Vector
import math


_TAG_RE = re.compile(r'\[(/?)(\w+)(?:=([^\]]*))?\]')


def _parse_markup(text, default_color, default_font):
    '''Parse a markup string into styled segments.

    Returns ``(spans, plain_text)`` where *spans* is a list of
    ``(text, [r, g, b, a], font_id)`` tuples and *plain_text* is the
    markup-stripped string used for layout measurements.

    Supported tags: ``[color=(r,g,b,a)]`` / ``[/color]``,
    ``[font=id]`` / ``[/font]``.  Tags may be nested.  Unknown tags are
    passed through as literal text.
    '''
    spans = []
    plain_parts = []
    color_stack = [list(default_color)]
    font_stack = [default_font]
    last_end = 0

    for m in _TAG_RE.finditer(text):
        segment = text[last_end:m.start()]
        if segment:
            spans.append((segment, color_stack[-1], font_stack[-1]))
            plain_parts.append(segment)
        last_end = m.end()

        closing, tag, value = m.group(1), m.group(2).lower(), m.group(3)
        if closing:
            if tag == 'color' and len(color_stack) > 1:
                color_stack.pop()
            elif tag == 'font' and len(font_stack) > 1:
                font_stack.pop()
        else:
            if tag == 'color' and value:
                try:
                    color_stack.append([float(x) for x in value.strip().strip('()').split(',')])
                except ValueError:
                    pass
            elif tag == 'font' and value:
                val = value.strip()
                try:
                    font_stack.append(int(val))
                except ValueError:
                    try:
                        font_stack.append(blf.load(val))
                    except Exception:
                        pass

    segment = text[last_end:]
    if segment:
        spans.append((segment, color_stack[-1], font_stack[-1]))
        plain_parts.append(segment)

    return spans, ''.join(plain_parts)


class Label(Widget):
    '''Widget for displaying text.

    Text is rendered via Blender's ``blf`` module and supports optional word
    wrap, drop shadow, and rotation.

    :param pos: Position in pixels or factor.
    :param relative: Relative positioning flags; ``'font_size'`` key makes the
        font size relative to the parent's height.
    :param text: Initial text content.
    :param font: Font file path, or empty string for the default font.
    :param font_color: RGBA text colour.
    :param font_size: Font size in pt (or as a factor when ``relative['font_size']`` is set).
    :param line_height: Line spacing factor relative to character height.
        ``1.5`` (default) gives 50 % extra space between lines.
    :param shadow: Enable drop shadow.
    :param shadow_offset: ``[x, y]`` pixel offset of the shadow.
    :param shadow_color: RGBA shadow colour.
    :param halign: Horizontal widget alignment: ``'left'``, ``'center'``, ``'right'``.
    :param valign: Vertical widget alignment: ``'bottom'``, ``'center'``, ``'top'``.
    :param wrap: Break long lines to fit inside the parent's width.
    :param padding: Additional spacing on both axes.
    :param angle: Rotation in degrees around the alignment pivot.
    :param show: Initial visibility.
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
        padding=(0, 0),
        angle=0,
        show=True
    ):
        self._parent = None
        self._children = None
        self._font_color = font_color
        self._font = 0
        self._spans = None
        self._raw_text = ''
        self.text = text
        self.line_height = line_height
        self.shadow = shadow
        self.shadow_offset = shadow_offset
        self.shadow_color = shadow_color
        self.font_size = font_size
        self.font_color = font_color
        self.font = font
        self.wrap = wrap
        if padding == 0:
            print(padding, text, '##########')
        self.padding = padding
        self.lines = []
        self._wrap_cache = None
        self._wrap_key = None
        self._wrap_spans_cache = None
        self._wrap_spans_key = None
        Widget.__init__(self, pos, (0, 0), (0, 0, 0, 0), relative, angle=angle, show=show)
        self.text_halign = halign
        self.text_valign = valign
        self.start()

    # @property
    # def padding(self):
    #     return self._padding

    # @padding.setter
    # def padding(self, val):
    #     print(val)
    #     self._padding = val

    @property
    def text(self):
        '''Current label text.  Always stored as a string.'''
        return self._text

    @text.setter
    def text(self, val):
        val = str(val)
        self._raw_text = val
        if '[' in val:
            self._spans, self._text = _parse_markup(val, self._font_color, self._font)
            if len(self._spans) == 1 and self._spans[0][0] == val:
                self._spans = None
        else:
            self._text = val
            self._spans = None
        self._cached_draw_pos = None

    @property
    def text_halign(self):
        '''Horizontal text alignment within the label: ``'left'``, ``'center'``, or ``'right'``.'''
        return self._text_halign

    @text_halign.setter
    def text_halign(self, val):
        self._text_halign = ALIGNMENTS.get(val, val)

    @property
    def text_valign(self):
        '''Vertical text alignment within the label: ``'bottom'``, ``'center'``, or ``'top'``.'''
        return self._text_valign

    @text_valign.setter
    def text_valign(self, val):
        self._text_valign = ALIGNMENTS.get(val, val)

    @property
    def pos_abs(self):
        return self._draw_pos

    @property
    def font(self):
        '''blf font id used for rendering.  Accepts a file path string or a
        ``bpy.types.VectorFont``; an empty string uses the default font (id 0).
        '''
        return self._font

    @font.setter
    def font(self, val):
        if isinstance(val, VectorFont):
            val = val.filepath.replace('\\', '/')
        self._font = (val if isinstance(val, int) else blf.load(val)) if val else 0
        self._cached_draw_pos = None

    @property
    def font_color(self):
        '''RGBA text colour.'''
        return self._font_color

    @font_color.setter
    def font_color(self, val):
        val = list(val)
        self._font_color = val
        if self._spans is not None and '[' in self._raw_text:
            self._spans, self._text = _parse_markup(self._raw_text, val, self._font)

    @property
    def color(self):
        '''Alias for :attr:`font_color`.'''
        return self.font_color

    @color.setter
    def color(self, val):
        self.font_color = val

    @property
    def dimensions(self):
        '''Pixel dimensions of the rendered text as a ``Vector(width, height)``.

        Uses the longest line for width measurement and scales height by
        ``line_count * line_height``.
        '''
        text = self.text
        if len(self.lines):
            text = max(self.lines, key=len)
        dim = blf.dimensions(self.font, text)
        lines = len(self.lines) or 1
        # self.padding = (0, 0)
        return Vector((dim[0] + 2 * self.padding[0], (blf.dimensions(self.font, 'A')[1] * lines * self.line_height - self.line_height) + 2 * self.padding[1]))

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
        offset = parsize[0] * self.pos[0] if self.relative.get('pos') else self.pos[0]
        max_width = int(parsize[0] - offset)
        relative = self.relative.get('font_size', False)
        font_size = parsize[1] * self.font_size if relative else self.font_size

        key = (self.text, font_size, self.font, max_width)
        if key == self._wrap_key:
            return self._wrap_cache

        blf.size(self.font, font_size)
        lines = []
        current_line = ''
        for word in self.text.split(' '):
            candidate = current_line + ' ' + word if current_line else word
            if blf.dimensions(self.font, candidate)[0] >= max_width:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = candidate
        if current_line:
            lines.append(current_line)

        result = '\n'.join(lines)
        self._wrap_key = key
        self._wrap_cache = result
        return result

    def _get_shader(self):
        import gpu
        if self._shader is None:
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            return shader
        return self._shader

    def _build_shader(self, force=True):
        pass

    def _wrap_spans(self, parsize, font, font_size):
        offset = parsize[0] * self.pos[0] if self.relative.get('pos') else self.pos[0]
        max_width = int(parsize[0] - offset)

        key = (
            tuple((s[0], s[2] if len(s) > 2 else font) for s in self._spans),
            font_size,
            max_width,
        )
        if key == self._wrap_spans_key:
            return self._wrap_spans_cache

        tokens = []
        for span in self._spans:
            fid = span[2] if len(span) > 2 else font
            color = span[1]
            for pi, paragraph in enumerate(span[0].split('\n')):
                if pi > 0:
                    tokens.append(None)
                for word in paragraph.split(' '):
                    if word:
                        tokens.append((word, color, fid))

        lines = []
        current_line = []
        current_w = 0.0
        space_w = blf.dimensions(font, ' ')[0]

        for token in tokens:
            if token is None:
                lines.append(current_line)
                current_line = []
                current_w = 0.0
                continue
            t, color, fid = token
            w = blf.dimensions(fid, t)[0]
            gap = space_w if current_line else 0.0
            if current_w + gap + w >= max_width and current_line:
                lines.append(current_line)
                current_line = [token]
                current_w = w
            else:
                current_line.append(token)
                current_w += gap + w

        if current_line:
            lines.append(current_line)

        self._wrap_spans_key = key
        self._wrap_spans_cache = lines
        return lines

    def _draw_wrapped_spans(self, lines, font, font_size, charsize, padding):
        lheight = charsize[1] * self.line_height
        n_lines = len(lines)
        space_w = blf.dimensions(font, ' ')[0]
        opacity = self.opacity

        for i, line_tokens in enumerate(lines):
            total_w = sum(blf.dimensions(t[2] if len(t) > 2 else font, t[0])[0]
                          for t in line_tokens)
            total_w += space_w * max(len(line_tokens) - 1, 0)

            pos = self._draw_pos.copy()
            if self.text_halign == ALIGN_CENTER:
                pos[0] -= total_w * 0.5
            elif self.text_halign == ALIGN_RIGHT:
                pos[0] -= total_w

            if self.text_valign == ALIGN_TOP:
                pos[1] -= lheight
            elif self.text_valign == ALIGN_CENTER:
                pos[1] += (0.5 * lheight * (n_lines - 1)) - (0.5 * lheight)
            elif self.text_valign == ALIGN_BOTTOM:
                pos[1] += lheight * (n_lines - 1)

            if self.parent and self.parent._draw_angle:
                pos = rotate2d(pos, self.pivot, self.parent.angle)

            x = pos[0] + padding[0]
            y = pos[1] + padding[1] - charsize[1] * i * self.line_height

            rotate = self.angle or self.parent._draw_angle
            angle_rad = math.radians(self._draw_angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            for j, (word, color, fid) in enumerate(line_tokens):
                if j > 0:
                    x += space_w * cos_a
                    y += space_w * sin_a
                if fid != font:
                    blf.size(fid, font_size)
                blf.color(fid, color[0], color[1], color[2], color[3] * opacity)
                if rotate:
                    blf.enable(fid, blf.ROTATION)
                    blf.rotation(fid, angle_rad)
                blf.position(fid, x, y, 0)
                blf.draw(fid, word)
                w = blf.dimensions(fid, word)[0]
                x += w * cos_a
                y += w * sin_a
                if fid != font:
                    blf.size(font, font_size)

    def _draw_spans(self, font, font_size, charsize, padding):
        total_width = sum(
            blf.dimensions(s[2] if len(s) > 2 else font, s[0])[0]
            for s in self._spans
        )
        pos = self._draw_pos.copy()
        if self.text_halign == ALIGN_CENTER:
            pos[0] -= total_width * 0.5
        elif self.text_halign == ALIGN_RIGHT:
            pos[0] -= total_width
        if self.text_valign == ALIGN_TOP:
            pos[1] -= charsize[1] * self.line_height
        elif self.text_valign == ALIGN_CENTER:
            pos[1] -= charsize[1] * 0.5
        if self.parent and self.parent._draw_angle:
            pos = rotate2d(pos, self.pivot, self.parent.angle)

        angle_rad = math.radians(self._draw_angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        x = pos[0] + padding[0]
        y = pos[1] + padding[1]
        rotate = self.angle or self.parent._draw_angle
        for span in self._spans:
            span_text = span[0]
            span_color = span[1]
            span_font = span[2] if len(span) > 2 else font
            if span_font != font:
                blf.size(span_font, font_size)
            blf.color(span_font, span_color[0], span_color[1],
                      span_color[2], span_color[3] * self.opacity)
            if rotate:
                blf.enable(span_font, blf.ROTATION)
                blf.rotation(span_font, angle_rad)
            blf.position(span_font, x, y, 0)
            blf.draw(span_font, span_text)
            w = blf.dimensions(span_font, span_text)[0]
            x += w * cos_a
            y += w * sin_a
            if span_font != font:
                blf.size(font, font_size)

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
            blf.clipping(font, verts[1][0], verts[1][1], verts[2][0], verts[2][1] - charsize[1]*2)
        else:
            blf.disable(font, blf.CLIPPING)
        if self.shadow:
            col = self.shadow_color
            blf.enable(font, blf.SHADOW)
            blf.shadow(font, 0, col[0], col[1], col[2], col[3] * self.opacity)
            blf.shadow_offset(font, int(self.shadow_offset[0]), int(self.shadow_offset[1]))
        padding = self.padding
        font_size = parsize[1] * self.font_size if relative else self.font_size
        if self._spans:
            if self.wrap:
                wrapped = self._wrap_spans(parsize, font, font_size)
                self._draw_wrapped_spans(wrapped, font, font_size, charsize, padding)
                self.lines = [' '.join(t[0] for t in line) for line in wrapped]
            else:
                self._draw_spans(font, font_size, charsize, padding)
                self.lines = [self.text]
            super().draw()
            blf.disable(font, blf.WORD_WRAP)
            blf.disable(font, blf.SHADOW)
            blf.disable(font, blf.ROTATION)
            return
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
                    pos[1] += (lheight * (len(lines) -1))
                if self.parent and self.parent._draw_angle:
                    pos = rotate2d(pos, self.pivot, self.parent.angle)
                blf.position(font, pos[0] + padding[0], pos[1] + padding[1] - (charsize[1] * (i) * self.line_height), 0)
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
            blf.position(font, pos[0] + padding[0], pos[1] + padding[1], 0)
            blf.draw(font, self.text)

        super().draw()
        self.lines = lines
        blf.disable(font, blf.WORD_WRAP)
        blf.disable(font, blf.SHADOW)
        blf.disable(font, blf.ROTATION)
