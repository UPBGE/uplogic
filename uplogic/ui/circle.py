'''Circular outline widget for uplogic UI.'''

import math
from .widget import Widget


class Circle(Widget):
    '''Widget that draws a circle (filled or outlined) using a GPU fragment shader.'''

    constants: list[tuple[str, str]] = [
        ('VEC2', "resolution"),
        ('VEC4', "color"),
        ('VEC4', "border_color"),
        ('VEC2', "shape"),  # x = border_width, y = segment_angle
    ]

    fragment_shader = '''
        void main() {
            const float TWO_PI = 6.28318530718;
            vec2 c = uv - vec2(0.5);
            float d = length(c) * 2.0;  // 0 = centre, 1 = outer edge

            float px = 2.0 / min(resolution.x, resolution.y);
            float inner = 1.0 - (shape.x / (min(resolution.x, resolution.y) * 0.5));

            // smooth outer edge (anti-alias)
            float outer_a = 1.0 - smoothstep(1.0 - px, 1.0 + px, d);
            // smooth inner edge (ring vs fill transition)
            float border_a = smoothstep(inner - px, inner + px, d);

            // segment mask: anti-aliased start and end edges
            float seg_mask = 1.0;
            if (shape.y < 360.0) {
                float a = mod(atan(c.x, c.y) + TWO_PI, TWO_PI);
                float seg_rad = radians(shape.y);
                float px_angle = px / max(d, px);  // angular width of one pixel at radius d
                seg_mask = smoothstep(-px_angle, px_angle, a)
                         * (1.0 - smoothstep(seg_rad - px_angle, seg_rad + px_angle, a));
            }

            vec4 col = mix(color, border_color, border_a);
            FragColor = vec4(col.rgb, col.a * outer_a * seg_mask);
        }
    '''

    def __init__(self, pos=[0, 0], bg_color=(1, 1, 1, 1), border_color=(0, 0, 0, 0), radius=100, border_width=1, relative={}, halign='left', valign='bottom', segment_angle=360, angle=0):
        self._radius = radius
        self.segment_angle = segment_angle
        self._angle = angle
        px_size = (0, 0) if relative.get('radius') else (radius * 2, radius * 2)
        super().__init__(pos, size=px_size, bg_color=bg_color, relative=relative, halign=halign, valign=valign, angle=angle)
        self.border_color = border_color
        self.border_width = border_width
        self.start()

    @property
    def width(self):
        return self.border_width

    @width.setter
    def width(self, val):
        self.border_width = val
        if self.parent and self.show:
            self._rebuild = True

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, val):
        self._radius = val
        if not self.relative.get('radius'):
            self.size = (val * 2, val * 2)
        if self.parent and self.show:
            self._rebuild = True

    @property
    def radius_pixel(self):
        if self.relative.get('radius') and self.parent is not None:
            return math.floor(self._radius * min(self.parent._draw_size))
        return self._radius

    @property
    def size_pixel(self):
        if self._vertices is None:
            return [0, 0]
        d = self.radius_pixel * 2
        return [d, d]

    @property
    def _draw_size(self):
        d = self.radius_pixel * 2
        return [d, d]

    def _set_uniforms(self):
        bg_color = self.bg_color.copy()
        border_color = self.border_color.copy()
        bg_color[3] *= self.opacity
        border_color[3] *= self.opacity
        self._shader.uniform_float("resolution", (self.width_pixel, self.height_pixel))
        self._shader.uniform_float("color", bg_color)
        self._shader.uniform_float("border_color", border_color)
        self._shader.uniform_float("shape", (self.border_width, self.segment_angle))

    def draw(self):
        self._setup_draw()
        self._set_uniforms()
        self._batch.draw(self._shader)
        super().draw()