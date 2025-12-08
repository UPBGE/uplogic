from .widget import Widget
import gpu
import bge, bpy
from math import ceil
from uplogic.utils.math import rotate2d
from gpu_extras.batch import batch_for_shader
from mathutils import Vector


class Circle(Widget):

    vertex_shader = """
    in vec2 texCoord;
    in vec2 pos;
    out vec2 uv;

    uniform mat4 ModelViewProjectionMatrix;

    void main() {
        uv = texCoord;
        gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0, 1.0);
    }
    """

    fragment_shader = """
    in vec2 uv;
    out vec4 fragColor;

    uniform sampler2D image;
    uniform float alpha = 1.0;

    void main() {
        vec4 color = mix(vec4(0.0), texture(image, uv), alpha);
        fragColor = pow(color, vec4(.5));
    }
    """

    def __init__(self, pos=[0, 0], radius=100, width=20, relative={}, halign='left', valign='bottom'):
        self._radius = radius
        super().__init__(pos, size=(radius, radius), relative=relative, halign=halign, valign=valign, angle=0)
        self._opacity = 1
        self.width = width
        self.start()

    @property
    def width(self):
        """Horizontal size of this widget in either pixels or factor relative to its parent."""
        return self._width

    @width.setter
    def width(self, val):
        self._width = val
        if self.parent and self.show:
            self._rebuild = True

    @property
    def radius(self):
        """Horizontal size of this widget in either pixels or factor relative to its parent."""
        return self._radius

    @radius.setter
    def radius(self, val):
        self._radius = val
        self.size = (val, val)
        if self.parent and self.show:
            self._rebuild = True

    def _build_shader(self):
        pos = self._draw_pos
        size = self._draw_size
        _resolution = 64

        points = [Vector((pos[0], pos[1] + self.radius))]
        for x in range(_resolution):
            points.append(
                rotate2d(points[-1], self.pos, 360 / _resolution)
            )
        vertices = self._vertices = points
        self._shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        self._batch_line = batch_for_shader(self._shader, 'LINE_STRIP', {"pos": vertices})

    def draw(self):
        self._setup_draw()
        gpu.state.line_width_set(self.width)
        # col = self.line_color.copy()
        col = Vector((0, 1, 0, 1))
        col[3] *= self.opacity
        self._shader.uniform_float("color", col)
        self._batch_line.draw(self._shader)
        super().draw()