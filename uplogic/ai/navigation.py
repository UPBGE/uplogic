'''Navigation primitives for uplogic AI.

:class:`NavPath` is an ordered list of world-space waypoints.
:class:`NavContainer` wraps a ``KX_GameObject`` and provides path storage,
traversal helpers, and optional corner bevelling.  :class:`NavMesh` is a
thin convenience wrapper around a ``KX_NavMeshObject`` that delegates path
queries to the BGE NavMesh API.
'''

from mathutils import Vector
from ..utils.objects import GameObject
from bge.types import KX_NavMeshObject, KX_GameObject
from ..utils.visualize import draw_path


class NavPath(list[Vector]):
    '''Ordered sequence of world-space :class:`~mathutils.Vector` waypoints
    produced by a NavMesh path query.

    Subclasses :class:`list` for direct index/pop access.  Each element is a
    :class:`~mathutils.Vector` in world space.
    '''
    # def __init__(self):
    #     self.points: list[Vector] = []

    # @property
    # def points(self) -> list[Vector]:
    #     return self._points

    # @points.setter
    # def points(self, val: list[Vector]):
    #     self._points = val


class NavContainer(GameObject):
    '''Base class for objects that hold and traverse a :class:`NavPath`.

    Wraps a ``KX_GameObject`` and stores a :class:`NavPath` computed by
    :meth:`find_path`.  Concrete subclasses (:class:`~uplogic.ai.Agent`,
    :class:`NavMesh`) are responsible for driving movement along the path.

    :param game_object: The BGE game object this container wraps.
    '''

    def __init__(self, game_object: KX_GameObject):
        super().__init__(game_object)
        self.height = 0
        self.bevel = 0.0
        self._path = NavPath()

    @property
    def next_point(self) -> Vector:
        '''First remaining waypoint in the current path, or ``None`` when the
        path is empty.
        '''
        if self._path:
            return self._path[0]

    def find_path(self, start: Vector, target: Vector, navmesh: KX_NavMeshObject) -> NavPath:
        '''Compute a path from *start* to *target* using *navmesh* and store it
        as the current path.

        When :attr:`bevel` is non-zero each interior corner is replaced by two
        offset waypoints (``corner − bevel`` and ``corner + next_bevel``) so
        the agent rounds the turn rather than cutting sharply through it.

        :param start: World-space start position.
        :param target: World-space destination.
        :param navmesh: BGE ``KX_NavMeshObject`` used for the path query.
        :returns: The newly computed :class:`NavPath`.
        '''
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
        '''Draw the current path as a sequence of line segments.

        :param color: RGBA draw colour.  Defaults to white.
        '''
        draw_path(self._path, color)

    def pop(self, idx: int = 0):
        '''Remove and return the waypoint at *idx* from the current path.

        :param idx: Index of the waypoint to remove.  Defaults to ``0``
            (the next point).
        :returns: The removed :class:`~mathutils.Vector`.
        '''
        return self._path.pop(idx)

    def distance(self, position: Vector):
        '''Distance from *position* to the next waypoint.

        :param position: Reference world-space position.
        :returns: Euclidean distance to :attr:`next_point`, or ``0`` when the
            path is empty.
        '''
        if self._path:
            return (self.next_point - position).length
        else:
            return 0

    def direction(self, position: Vector):
        '''Unit vector from *position* towards the next waypoint.

        :param position: Reference world-space position.
        :returns: Normalised direction towards :attr:`next_point`, or the zero
            vector when the path is empty.
        '''
        if self._path:
            return (self.next_point - position).normalized()
        else:
            return Vector((0, 0, 0))


class NavMesh(NavContainer):
    '''Logic container that wraps a BGE ``KX_NavMeshObject`` for path queries.

    Unlike :class:`~uplogic.ai.Agent`, ``NavMesh`` does not drive a moving
    object — it is a reusable path-computation helper that can serve multiple
    agents.

    :param game_obj: BGE game object with a generated NavMesh.
    '''

    def __init__(self, game_obj: KX_NavMeshObject | KX_GameObject):
        self.game_object: KX_NavMeshObject = game_obj
        self._path = NavPath()

    def find_path(self, start: Vector, target: Vector):
        '''Compute a path from *start* to *target* using the wrapped NavMesh.

        :param start: World-space start position.
        :param target: World-space destination.
        :returns: The newly computed :class:`NavPath`.
        '''
        return super().find_path(start, target, self.game_object)
