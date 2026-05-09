'''NavMesh-based AI agent for uplogic.

:class:`Agent` wraps a ``KX_GameObject``, computes a :class:`NavPath` via the
BGE NavMesh API, optionally steers around physics obstacles using raycasts,
and moves the object along the resulting waypoints each game tick.
'''

from ..utils.visualize import draw_line
from .navigation import NavContainer
from bge.types import KX_GameObject
from bge.types import KX_NavMeshObject
from uplogic.utils import raycast
from uplogic.utils.objects import zrot_to
from uplogic.utils.constants import FPS_FACTOR
from mathutils import Vector


class Agent(NavContainer):
    '''NavMesh-based AI agent that walks a ``KX_GameObject`` along a computed path.

    Each tick, call :meth:`find_path` once (or only when the destination
    changes), then call :meth:`move` to advance the object along the path.
    Call :meth:`lookat` to face the next waypoint.

    :param game_object: The BGE game object acting as the agent.
    :param speed: Movement speed in world units per tick.  Defaults to ``0.1``.
    :param threshold: Distance at which a waypoint is considered reached.
        Negative values (default ``-1``) cause the threshold to be derived
        automatically from *speed* or from the current velocity for dynamic
        agents.
    :param bevel: Corner-rounding distance applied during path computation.
        ``0.0`` (default) means sharp corners.
    :param dynamic: When ``True`` the agent is pushed by setting
        ``worldLinearVelocity``; when ``False`` (default) ``applyMovement``
        is used instead.
    :param obstacle_mask: Collision-group bitmask for obstacle-avoidance
        raycasts.  ``0`` (default) disables obstacle avoidance; ``65535``
        tests against all objects.
    :param height: Z offset added to every computed waypoint, useful when the
        agent origin sits above ground level.
    '''

    def __init__(
            self,
            game_object: KX_GameObject,
            speed: float = .1,
            threshold: float = -1,
            bevel: float = 0.0,
            dynamic: bool = False,
            obstacle_mask: int = 0,
            height: float = 0.0
        ):
        super().__init__(game_object)
        self.speed = speed
        self.navmesh = None
        self.threshold = threshold
        self.height = height
        self.obstacle_mask = obstacle_mask
        self.bevel = bevel
        self.dynamic = dynamic

    def set_navmesh(self, navmesh: KX_GameObject):
        '''Set the navigation mesh used for path calculations.

        :param navmesh: BGE game object with a generated NavMesh.
        '''
        self.navmesh = navmesh

    @property
    def position(self):
        '''World-space XY position of the agent with Z forced to ``0``.

        Used internally so that distance calculations remain horizontal.
        '''
        pos = self.game_object.worldPosition.copy()
        pos.z = 0
        return pos

    @property
    def next_point(self) -> Vector:
        '''World-space position of the next waypoint to move towards.

        When :attr:`obstacle_mask` is non-zero a short raycast is fired towards
        the first waypoint.  If an obstacle is detected, detour waypoints are
        inserted around its bounding radius so the agent steers clear.

        Returns ``None`` when the path is empty.
        '''
        if self._path:
            if self.obstacle_mask:
                pathpoints = self._path
                dat = raycast(self.game_object, self.game_object.worldPosition.xy.to_3d(), pathpoints[0], distance=5, mask=self.obstacle_mask)
                if dat.obj and dat.obj.blenderObject.game.use_obstacle_create:
                    rad = dat.obj.blenderObject.game.obstacle_radius * 1.5
                    while (pathpoints[0] - dat.obj.worldPosition).length < rad:
                        self.pop()

                    n = dat.normal.copy()
                    n.z = 0
                    next_direction = (pathpoints[0] - dat.obj.worldPosition).normalized()
                    normal = dat.direction.cross(Vector((0, 0, 1))).normalized()
                    normal1 = next_direction.cross(Vector((0, 0, 1))).normalized()
                    angle = dat.direction.to_2d().angle_signed(n.to_2d())
                    direction = 1 if angle > 0 else -1

                    handle_1 = dat.obj.worldPosition + normal * rad * direction
                    handle_2 = dat.obj.worldPosition + normal1 * rad * direction
                    dist_to_next_1 = (handle_1 - pathpoints[0]).length
                    dist_to_next_2 = (handle_2 - pathpoints[0]).length

                    while (pathpoints[0] - self.game_object.worldPosition).length < (self.game_object.worldPosition - handle_1).length:
                        self.pop()
                    pathpoints.insert(0, handle_1)
                    if (pathpoints[0] - handle_2).length > self.speed and dist_to_next_1 > dist_to_next_2:
                        pathpoints.insert(1, handle_2)

            return self._path[0]

    def find_path(self, target: Vector, navmesh: KX_NavMeshObject | KX_GameObject = None):
        '''Calculate a path from the agent's current position to *target*.

        :param target: World-space destination.
        :param navmesh: NavMesh object to use.  Falls back to :attr:`navmesh`
            when ``None``.
        :returns: The computed :class:`~uplogic.ai.navigation.NavPath`.
        '''
        return super().find_path(self.game_object.worldPosition, target, navmesh if navmesh else self.navmesh)

    def visualize(self, color=Vector((0, 1, 0))):
        '''Draw the current path as a sequence of line segments.

        :param color: RGB draw colour.  Defaults to green ``(0, 1, 0)``.
        '''
        if self._path:
            compare = self.game_object.worldPosition.copy()
            compare.z = self.next_point.z
            draw_line(compare, self.next_point, color)
            return super().visualize(color)

    def pop(self, idx=0):
        '''Remove and return the waypoint at *idx* from the current path.

        :param idx: Index of the waypoint to remove.  Defaults to ``0``
            (the next point).
        :returns: The removed :class:`~mathutils.Vector`, or ``None`` if the
            path is already empty.
        '''
        points = self._path
        if not points:
            return None
        return points.pop(idx)

    def clean(self):
        '''Discard all waypoints closer than ``0.3`` world units to the agent.'''
        while self.next_point and self.distance < .3:
            self.pop()

    @property
    def idle(self):
        '''``True`` when the agent has no remaining waypoints to follow.'''
        return not self._path

    @property
    def distance(self):
        '''Horizontal distance from the agent to the next waypoint.

        The agent's Z coordinate is matched to the waypoint's Z before
        measuring so only the XY plane is taken into account.  Returns ``0``
        when the path is empty.
        '''
        compare = self.game_object.worldPosition.copy()
        np = self.next_point
        if np is None:
            return 0
        compare.z = self.next_point.z
        return super().distance(compare)

    @property
    def direction(self):
        '''Horizontal unit vector from the agent towards the next waypoint.

        Z is matched to the waypoint before the direction is normalised.
        Returns the zero vector when the path is empty.
        '''
        compare = self.game_object.worldPosition.copy()
        np = self.next_point
        if np is None:
            return Vector((0, 0, 0))
        compare.z = self.next_point.z
        return super().direction(compare)

    def lookat(self, factor: float = .1):
        '''Rotate the agent to face the next waypoint.

        :param factor: Interpolation factor applied each tick.  Smaller values
            produce slower, smoother turns.  Defaults to ``0.1``.
        '''
        next_point = self.next_point
        if next_point is not None:
            zrot_to(self.game_object, next_point, 1, factor)

    @property
    def threshold(self):
        '''Distance at which the current waypoint is considered reached.

        When the stored value is negative the threshold is derived
        automatically: ``worldLinearVelocity.length * FPS_FACTOR()`` for
        dynamic agents, or :attr:`speed` for kinematic agents.
        '''
        if self._threshold >= 0:
            return self._threshold
        elif self.dynamic:
            return self.game_object.worldLinearVelocity.length * FPS_FACTOR()
        else:
            return self.speed

    @threshold.setter
    def threshold(self, val):
        self._threshold = val

    def move(self):
        '''Advance the agent along its current path by one tick.

        Waypoints within :attr:`threshold` distance are popped before moving.
        For dynamic agents the XY component of ``worldLinearVelocity`` is set
        directly; for kinematic agents ``applyMovement`` is called with the
        scaled :attr:`direction`.
        '''
        while self._path and self.distance < self.threshold:
            self.pop()
        if not self._path:
            return
        if self.dynamic:
            # print(self.speed)
            # self.game_object.applyForce(self.direction * self.speed)
            self.game_object.worldLinearVelocity.xy = (self.direction * self.speed).xy
        else:
            self.game_object.applyMovement(self.direction * self.speed)
