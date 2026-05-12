from .widget import Widget
from mathutils import Vector
from .widget import rotate2d
from gpu_extras.batch import batch_for_shader
import gpu


class Path(Widget):
    '''Widget for drawing a polyline on the canvas.

    Points are given in the coordinate space selected by *relative*: raw
    pixels when ``relative['points']`` is falsy, or as a factor of the
    parent's draw size when ``True``.

    :param pos: Widget origin position (pixels or factor).
    :param points: List of ``[x, y]`` waypoints.
    :param relative: Flags dict; ``'pos'`` and ``'points'`` keys control
        coordinate interpretation.
    :param line_width: Stroke thickness in pixels.
    :param line_color: RGBA draw colour.
    :param angle: Rotation in degrees around the widget origin.
    :param show: Initial visibility.
    '''

    def __init__(
        self,
        pos=[0, 0],
        points=[],
        relative={},
        line_width=1,
        line_color=(1.0, 1.0, 1.0, 1.0),
        angle=0,
        show=True
    ):
        Widget.__init__(self, pos, (0, 0), (0, 0, 0, 0), relative=relative, angle=angle, show=show)
        self.points = points
        self.line_color = line_color
        self.line_width = line_width
        self.start()

    @property
    def line_color(self) -> list:
        '''RGBA draw colour for the line.  Setting this rebuilds the shader.'''
        return self._line_color

    @line_color.setter
    def line_color(self, val):
        self._line_color = list(val)
        self._build_shader()

    @property
    def line_width(self) -> float:
        '''Stroke thickness in pixels.  Setting this rebuilds the shader.'''
        return self._line_width

    @line_width.setter
    def line_width(self, val):
        self._line_width = val
        self._build_shader()

    @property
    def points(self) -> list:
        '''List of waypoints.  Setting this rebuilds the shader.'''
        return self._points

    @points.setter
    def points(self, val):
        self._points = val
        self._build_shader()

    def _build_shader(self, force=False):
        if self.parent is None:
            return
        pos = self._draw_pos
        points = []
        for point in self.points:
            point = Vector(point)
            if self.relative.get('points', False):
                pdsize = Vector(self.parent._draw_size)
                point *= pdsize
            point += Vector(pos)
            if self._draw_angle and self._vertices is not None:
                point = rotate2d(point, pos, self._draw_angle)
            points.append(point)
        vertices = self._vertices = points
        self._shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        self._batch_line = batch_for_shader(self._shader, 'LINE_STRIP', {"pos": vertices})

    def draw(self):
        '''Set line-width GPU state and draw the ``LINE_STRIP`` batch.'''
        self._setup_draw()
        gpu.state.line_width_set(self.line_width)
        col = self.line_color.copy()
        col[3] *= self.opacity
        self._shader.uniform_float("color", col)
        self._batch_line.draw(self._shader)
        super().draw()