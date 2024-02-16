from mathutils import Vector
from ..utils.objects import GameObject
from bge.types import KX_NavMeshObject, KX_GameObject
from ..utils.visualize import draw_arrow_path, draw_arrow, draw_path
from ..utils.math import rotate_by_axis
from math import degrees


class NavPath:
    def __init__(self):
        self.points: list[Vector] = []
    
    @property
    def points(self) -> list[Vector]:
        return self._points

    @points.setter
    def points(self, val: list[Vector]):
        self._points = val


class NavContainer(GameObject):
    
    def __init__(self, game_object: KX_GameObject):
        super().__init__(game_object)
        self.height = 0
        self.bevel = 0.0
        self._path = NavPath()

    @property
    def next_point(self) -> Vector:
        if self._path.points:
            return self._path.points[0]

    def find_path(self, start: Vector, target: Vector, navmesh: KX_NavMeshObject):
        height = Vector((0, 0, self.height))
        points: list[Vector] = [Vector(p) + height for p in navmesh.findPath(
            start,
            target
        )]

        bevel = self.bevel
        if bevel:
            # last_point = None
            _points: list[Vector] = []
            for i, p in enumerate(points):
                if i == 0 or i == len(points) - 1:
                    _points.append(p)
                    continue
                direction = (p - _points[-1]).normalized()
                next_point = points[i+1]
                next_direction = (next_point - p).normalized()
                start_circle = p - direction * bevel
                end_circle = p + next_direction * bevel


                # KEEP for debugging!
                # up = direction.cross(next_direction).normalized()
                # normal1 = direction.cross(up).normalized()
                # normal2 = next_direction.cross(up).normalized()
                # draw_arrow(start_circle, start_circle - normal1)
                # draw_arrow(end_circle, end_circle - normal2)

                _points.append(start_circle)
                _points.append(end_circle)
            points = _points

        self._path.points = points
        return self._path.points

    def visualize(self, color=Vector((1, 1, 1, 1))):
        draw_path(self._path.points, color)

    def pop(self, idx=0):
        return self._path.points.pop(idx)

    def distance(self, position: Vector):
        if self._path.points:
            return (self.next_point - position).length
        else:
            return Vector((0, 0, 0))

    def direction(self, position: Vector):
        if self._path.points:
            return (self.next_point - position).normalized()
        else:
            return Vector((0, 0, 0))


class NavMesh(NavContainer):
    def __init__(self, game_obj: KX_NavMeshObject):
        self.game_object: KX_NavMeshObject = game_obj
        self._path = NavPath()

    def find_path(self, start: Vector, target: Vector):
        return super().find_path(start, target, self.game_object)
