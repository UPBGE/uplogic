from mathutils import Vector
from ..utils.objects import GameObject
from bge.types import KX_NavMeshObject, KX_GameObject
from ..utils.visualize import draw_path


class NavPath(list[Vector]):
    """Sequence of points used for NavMesh Pathfinding."""
    # def __init__(self):
    #     self.points: list[Vector] = []
    
    # @property
    # def points(self) -> list[Vector]:
    #     return self._points

    # @points.setter
    # def points(self, val: list[Vector]):
    #     self._points = val


class NavContainer(GameObject):
    
    def __init__(self, game_object: KX_GameObject):
        super().__init__(game_object)
        self.height = 0
        self.bevel = 0.0
        self._path = NavPath()

    @property
    def next_point(self) -> Vector:
        if self._path:
            return self._path[0]

    def find_path(self, start: Vector, target: Vector, navmesh: KX_NavMeshObject) -> NavPath:
        height = Vector((0, 0, self.height))
        points: NavPath = NavPath([Vector(p) + height for p in navmesh.findPath(
            start,
            target
        )])

        bevel = self.bevel
        if bevel:
            _points = self._path
            _points.clear()
            for i, p in enumerate(points):
                if i == 0 or i == len(points) - 1:
                    _points.append(p)
                    continue
                direction = (p - _points[-1]).normalized()
                next_point = points[i+1]
                next_direction = (next_point - p).normalized()
                start_circle = p - direction * bevel
                end_circle = p + next_direction * bevel

                # XXX KEEP for debugging!
                # up = direction.cross(next_direction).normalized()
                # normal1 = direction.cross(up).normalized()
                # normal2 = next_direction.cross(up).normalized()
                # draw_arrow(start_circle, start_circle - normal1)
                # draw_arrow(end_circle, end_circle - normal2)

                _points.append(start_circle)
                _points.append(end_circle)
            points = _points

        self._path = points
        return self._path

    def visualize(self, color: Vector = Vector((1, 1, 1, 1))):
        """
        Visualize the NavPath if there is one.

        :param Vector color: Color of the NavPath.
        """
        draw_path(self._path, color)

    def pop(self, idx: int = 0):
        """
        Remove a point from the NavPath.

        :param int idx: Index of the point.
        """
        return self._path.pop(idx)

    def distance(self, position: Vector):
        """
        Distance from the next point of the NavPath to the target position.

        :param position: Target position in world space.
        :type position: Vector
        """
        if self._path:
            return (self.next_point - position).length
        else:
            return 0

    def direction(self, position: Vector):
        """
        Direction from the next point of the NavPath to the target position

        :param position: Target position in world space.
        :type position: Vector
        """
        if self._path:
            return (self.next_point - position).normalized()
        else:
            return Vector((0, 0, 0))


class NavMesh(NavContainer):
    """
    Logic container for a NavMesh

    :param KX_NavMeshObject | KX_GameObject game_obj: GameObject to use as NavMesh. Must have a NavMesh generated.
    """

    def __init__(self, game_obj: KX_NavMeshObject | KX_GameObject):
        self.game_object: KX_NavMeshObject = game_obj
        self._path = NavPath()

    def find_path(self, start: Vector, target: Vector):
        return super().find_path(start, target, self.game_object)
