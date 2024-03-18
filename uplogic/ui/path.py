from .widget import Widget
from mathutils import Vector
from uplogic.utils.math import rotate2d, world_to_screen
from gpu_extras.batch import batch_for_shader
from bge.render import getWindowWidth, getWindowHeight
from bge.types import KX_GameObject
import gpu


class Path(Widget):
    '''Widget for displaying a path.

    :param `pos`: Initial position of this widget in either pixels or factor.
    :param `size`: Initial size of this widget in either pixels or factor.
    :param `bg_color`: Color to draw in the area of the widget.
    :param `relative`: Whether to use pixels or factor for size or pos; example: `{'pos': True, 'size': True}`.
    :param `halign`: Horizontal alignment of the widget, can be (`left`, `center`, `right`).
    :param `valign`: Vertical alignment of the widget, can be (`bottom`, `center`, `top`).
    :param `angle`: Rotation in degrees of this widget around the pivot defined by the alignment.
    '''

    def __init__(
        self,
        pos=[0, 0],
        points=[],
        relative={},
        line_width=1,
        line_color=(1.0, 1.0, 1.0, 1.0),
        angle=0
    ):
        Widget.__init__(self, pos, (0, 0), (0, 0, 0, 0), relative=relative, angle=angle)
        self.points = points
        self.line_color = line_color
        self.line_width = line_width

    @property
    def line_color(self) -> list:
        return self._line_color

    @line_color.setter
    def line_color(self, val):
        self._line_color = list(val)
        self._build_shader()

    @property
    def line_width(self) -> float:
        return self._line_width

    @line_width.setter
    def line_width(self, val):
        self._line_width = val
        self._build_shader()

    @property
    def points(self) -> list:
        return self._points

    @points.setter
    def points(self, val):
        self._points = val
        self._build_shader()

    def _build_shader(self):
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
        self.shader = gpu.types.GPUShader(self.vertex_code, self.fragment_code)
        self._batch_line = batch_for_shader(self.shader, 'LINE_STRIP', {"pos": vertices})

    def draw(self):
        super()._setup_draw()
        gpu.state.line_width_set(self.line_width)
        col = self.line_color.copy()
        col[3] *= self.opacity
        self.shader.uniform_float("color", col)
        self._batch_line.draw(self.shader)
        super().draw()


class WorldPath(Path):

    def __init__(
        self,
        points=[],
        line_width=1,
        line_color=(1.0, 1.0, 1.0, 1.0)
    ):
        Widget.__init__(self, (0, 0), (0, 0), (0, 0, 0, 0))
        self.points = points
        self.line_color = line_color
        self.line_width = line_width
    
    def _build_shader(self):
        if self.parent is None:
            return
        points = []
        for point in self.points:
            point = world_to_screen(point)
            point *= Vector((
                getWindowWidth(),
                getWindowHeight()
            ))
            points.append(point)
        vertices = self._vertices = points
        self.shader = gpu.types.GPUShader(self.vertex_code, self.fragment_code)
        self._batch_line = batch_for_shader(self.shader, 'LINE_STRIP', {"pos": vertices})


class ObjectPath(Path):
    def __init__(
        self,
        object=None,
        line_width=1,
        line_color=(1.0, 1.0, 1.0, 1.0)
    ):
        Widget.__init__(self, (0, 0), (0, 0), (0, 0, 0, 0))
        self.object: KX_GameObject = object
        self.line_color = line_color
        self.line_width = line_width

    def _build_shader(self):
        if self.parent is None:
            return
        points = []
        mesh = self.object.blenderObject.data
        for edge in mesh.edges:
            v1 = mesh.vertices[edge.vertices[0]]
            v2 = mesh.vertices[edge.vertices[1]]
            v1 = world_to_screen(self.object.worldTransform @ Vector(v1.co))
            v2 = world_to_screen(self.object.worldTransform @ Vector(v2.co))
            # # point = world_to_screen(point)
            v1 *= Vector((
                getWindowWidth(),
                getWindowHeight()
            ))
            v2 *= Vector((
                getWindowWidth(),
                getWindowHeight()
            ))
            points.append(v1)
            points.append(v2)
        vertices = self._vertices = points
        self.shader = gpu.types.GPUShader(self.vertex_code, self.fragment_code)
        self._batch_line = batch_for_shader(self.shader, 'LINES', {"pos": vertices})
