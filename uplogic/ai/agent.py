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
        """Define what navmesh object should be used to calculate a path."""
        self.navmesh = navmesh

    @property
    def position(self):
        """Current horizontal world position of this object. Z is set to 0 for distance calculation """
        pos = self.game_object.worldPosition.copy()
        pos.z = 0
        return pos

    @property
    def next_point(self) -> Vector:
        """World position of next point to approach."""
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

    def find_path(self, target: Vector, navmesh: KX_NavMeshObject = None):
        """Calculate a path to the current target position."""
        return super().find_path(self.game_object.worldPosition, target, navmesh if navmesh else self.navmesh)

    def visualize(self, color=Vector((0, 1, 0))):
        """Draw a line showing the currently calculated path."""
        if self._path:
            compare = self.game_object.worldPosition.copy()
            compare.z = self.next_point.z
            draw_line(compare, self.next_point, color)
            return super().visualize(color)

    def pop(self, idx=0):
        """Remove a point from the calculated path."""
        points = self._path
        if not points:
            return None
        return points.pop(idx)

    def clean(self):
        """Clean all points too close to the agent."""
        while self.next_point and self.distance < .3:
           self.pop()

    @property
    def idle(self):
        """True if agent has no path to follow."""
        return not self._path

    @property
    def distance(self):
        """Horizontal distance from agent to the next point."""
        compare = self.game_object.worldPosition.copy()
        np = self.next_point
        if np is None:
            return 0
        compare.z = self.next_point.z
        return super().distance(compare)

    @property
    def direction(self):
        """Horizontal direction from agent to the next point."""
        compare = self.game_object.worldPosition.copy()
        np = self.next_point
        if np is None:
            return Vector((0, 0, 0))
        compare.z = self.next_point.z
        return super().direction(compare)

    def lookat(self, factor=.1):
        """Rotate the agent to look towards the next point."""
        next_point = self.next_point
        if next_point is not None:
            zrot_to(self.game_object, next_point, 1, factor)

    @property
    def threshold(self):
        """Reach threshold. If set to 0, an appropriate threshold is calculated automatically."""
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
        """Move the agent to the target along the calculated path."""
        while self._path and self.distance < self.threshold:
            self.pop()
        if not self._path:
            return
        if self.dynamic:
            print(self.speed)
            # self.game_object.applyForce(self.direction * self.speed)
            self.game_object.worldLinearVelocity.xy = (self.direction * self.speed).xy
        else:
            self.game_object.applyMovement(self.direction * self.speed)