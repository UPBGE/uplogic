
from .widget import Widget
from .path import Path
from uplogic.utils.scene import world_to_screen
from bge.render import getWindowWidth, getWindowHeight
from bge.types import KX_GameObject
from mathutils import Vector
from gpu_extras.batch import batch_for_shader
import gpu


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
        self.start()
    
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
        self._shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        self._batch_line = batch_for_shader(self._shader, 'LINE_STRIP', {"pos": vertices})


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
        self.start()

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
        self._shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        self._batch_line = batch_for_shader(self._shader, 'LINES', {"pos": vertices})
