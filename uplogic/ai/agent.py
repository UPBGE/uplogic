from ..utils.visualize import draw_line
from .navigation import NavContainer
from bge.types import KX_GameObject
from bge.types import KX_NavMeshObject
from uplogic.utils import raycast
from uplogic.utils.objects import zrot_to
from uplogic.utils.constants import FPS_FACTOR
from mathutils import Vector


class Agent(NavContainer):
    """Simple AI Agent implementation that uses a Navigation Mesh.

    :param game_object: The game object acting as the agent.
    :param speed: The speed this agent will move at towards the target.
    :param threshold: Reach threshold for Navigation Path points. If none is set, `speed` will be used as theshold.
    :param bevel: Bevel distance at corners. This will cut corners outside of the navmesh.
    :param dynamic: Whether to move the agent using forces or pure vectors.
    :param obstacle_mask: Objects in this collision group will be recognized as obstacles. Set to `65535` for all objects.
    :param height: Z-Offset for the path calculation.
    """
    def __init__(
            self,
            game_object: KX_GameObject,
            speed: float= .1,
            threshold: float = -1,
            bevel=0.0,
            dynamic=False,
            obstacle_mask=0,
            height=0.0
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
        self.navmesh = navmesh

    @property
    def position(self):
        pos = self.game_object.worldPosition.copy()
        pos.z = 0
        return pos

    @property
    def next_point(self) -> Vector:
        if self._path.points:
            if self.obstacle_mask:
                pathpoints = self._path.points
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

            return self._path.points[0]

    def find_path(self, target: Vector, navmesh: KX_NavMeshObject = None):
        return super().find_path(self.game_object.worldPosition, target, navmesh if navmesh else self.navmesh)

    def visualize(self, color=Vector((0, 1, 0))):
        if self._path.points:
            compare = self.game_object.worldPosition.copy()
            compare.z = self.next_point.z
            draw_line(compare, self.next_point, color)
            return super().visualize(color)

    def pop(self, idx=0):
        points = self._path.points
        if not points:
            return None
        return points.pop(idx)

    def clean(self):
       while self.next_point and self.distance < .3:
           self.pop()

    @property
    def idle(self):
        return not self._path.points

    @property
    def distance(self):
        compare = self.game_object.worldPosition.copy()
        np = self.next_point
        if np is None:
            return 0
        compare.z = self.next_point.z
        return super().distance(compare)

    @property
    def direction(self):
        compare = self.game_object.worldPosition.copy()
        np = self.next_point
        if np is None:
            return Vector((0, 0, 0))
        compare.z = self.next_point.z
        return super().direction(compare)

    def lookat(self, factor=.1):
        next_point = self.next_point
        if next_point is not None:
            zrot_to(self.game_object, next_point, 1, factor)

    @property
    def threshold(self):
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
        while self._path.points and self.distance < self.threshold:
            self.pop()
        if not self._path.points:
            return
        if self.dynamic:
            self.game_object.applyForce(self.direction * self.speed)
        else:
            self.game_object.applyMovement(self.direction * self.speed)