from bge import constraints
from bge import logic
from bge import render
from bge.types import KX_ConstraintWrapper as GameConstraint
from bge.types import KX_GameObject as GameObject
from mathutils import Vector
from uplogic.utils import debug, get_direction
from uplogic.utils import set_curve_points
from uplogic.utils import xrot_to
from uplogic.utils import yrot_to
from uplogic.utils import zrot_to


CONSTRAINT_TYPES = {
    'point': 0,
    'hinge': 1,
    'angular': 2,
    'conetwist': 3,
    'generic6dof': 4
}


def create_constraint(
    obj: GameObject,
    target: GameObject,
    constraint_type: int or str = 0,
    pivot: set = (0, 0, 0),
    limit: set = (0, 0, 0),
    linked_collision: bool = True,
    local: bool = True
) -> GameConstraint:
    """Wrapper function for `bge.constraints.createConstraint()`. Creates a constraint

    :param `obj`: Object the constraint will be applied to.
    :param `target`: Target for the constraint.
    :param `constraint_type`: Type of the constraint. One of `['point', 'hinge', 'angular', 'conetwist', 'generic6dof']`.
    :param `pivot`: Point of application for the constraint.
    :param `limit`: Limit movement of the object (Like a doorstop).
    :param `linked_collision`: Enable/Disable collision between obj and target.
    :param `local`: Use obj's local space.
    """
    if not local:
        pivot[0] -= obj.worldPosition.x
        pivot[1] -= obj.worldPosition.y
        pivot[2] -= obj.worldPosition.z
    return constraints.createConstraint(
        obj.getPhysicsId(),
        target.getPhysicsId(),
        constraint_type if isinstance(constraint_type, int) else CONSTRAINT_TYPES.get(constraint_type, 0),
        pivot[0],
        pivot[1],
        pivot[2],
        limit[0],
        limit[1],
        limit[2],
        0 if linked_collision else 128
    )


def remove_constraint(constraint: GameConstraint) -> None:
    """Wrapper function for `bge.constraints.removeConstraint()`. Creates a constraint

    :param `constraint`: The constraint to remove.
    """
    constraints.removeConstraint(constraint.getConstraintId())


class ULTrackTo():
    def __init__(
        self,
        game_object: GameObject,
        target: GameObject or Vector,
        axis: int = 2,
        front: int = 1,
        speed: float = 0
    ) -> None:
        self._axis = None
        self._target = None
        self.game_object = game_object
        self.target = target
        self.front = front
        self.speed = speed
        self.axis = axis

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, val):
        if isinstance(val, list) or isinstance(val, tuple):
            self._target = Vector(val)
        elif isinstance(val, Vector):
            self._target = val
        else:
            debug('Could not set TrackTo target!')

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, val):
        if val == 0:
            self.rotate_func = xrot_to
        elif val == 1:
            self.rotate_func = yrot_to
        elif val == 2:
            self.rotate_func = zrot_to
        else:
            self.rotate_func = None
        self._axis = val
        logic.getCurrentScene().pre_draw.append(self.update)

    def remove(self):
        logic.getCurrentScene().pre_draw.remove(self.update)

    def update(self):
        if self.rotate_func:
            self.rotate_func(self.game_object, self.target, self.front, self.speed)


class ULSpring():
    """Spring Physics Constraint.

    :param `origin`: First connection point of the spring.
    :param `target`: Second connection point of the spring.
    :param `rigid_body_origin`: Object to be influenced by the spring (optional).
    :param `rigid_body_target`: Object to be influenced by the spring (optional).
    :param `stiffness`: Amount the spring will bounce back.
    :param `max_force`: Maximum force the spring will use.
    :param `use_push`: Push the objects apart when spring is compressed.
    :param `use_breaking`: Remove the constraint when spring is pulled too much.
    :param `break_threshold`: Amount of strain the spring will endure.
    :param `curve`: Set a curve object to fit the spring.
    :param `visualize`: Enable a visual representation of the spring.
    """
    def __init__(
        self,
        origin: GameObject,
        target: GameObject,
        rigid_body_origin: GameObject = None,
        rigid_body_target: GameObject = None,
        stiffness: float = 1,
        max_force: float = -1,
        distance: float = 0,
        use_push: bool = False,
        use_breaking: bool = False,
        break_threshold: float = 1,
        curve: GameObject or None = None,
        visualize: bool = False
    ) -> None:
        self.force = 0
        if isinstance(origin, tuple) or isinstance(origin, list):
            origin = Vector((origin))
        self.origin = origin
        if isinstance(target, tuple) or isinstance(target, list):
            target = Vector((target))
        self.target = target
        self.use_push = use_push
        self.rigid_body_origin = rigid_body_origin if rigid_body_origin else origin
        self.rigid_body_target = rigid_body_target if rigid_body_target else target
        self.stiffness = stiffness
        self.max_force = max_force
        self.use_breaking = use_breaking
        self.break_threshold = break_threshold
        self.visualize = visualize
        obj_dist = origin.getDistanceTo(target)
        self.distance = distance or obj_dist
        self.curve = curve
        if not use_breaking or self.distance >= obj_dist:
            logic.getCurrentScene().pre_draw.append(self.update)

    @property
    def points(self):
        return [self.origin.worldPosition, self.target.worldPosition]
    
    @points.setter
    def points(self, val):
        print("Attribute 'points' is read-only")

    @property
    def active(self):
        return self.force != 0

    @active.setter
    def active(self, val):
        print("Attribute 'active' is read-only")

    def remove(self):
        logic.getCurrentScene().pre_draw.remove(self.update)

    def update(self):
        o = self.origin
        t = self.target
        force = (o.getDistanceTo(t) - self.distance) * self.stiffness
        if self.max_force >= 0 and force > self.max_force:
            force = self.max_force
        if not self.use_push:
            force = force if force >= 0 else 0
        if self.use_breaking and force > self.break_threshold:
            logic.getCurrentScene().pre_draw.remove(self.update)
            return
        if self.visualize:
            start = getattr(o, 'worldPosition', o)
            end = getattr(t, 'worldPosition', t)
            render.drawLine(
                start,
                end,
                # [1, 1-abs(power), 1-abs(power)]
                [abs(force), 0, 1-abs(force)]
            )
        self.force = force
        if self.curve:
            set_curve_points(self.curve, self.points)
        rbo = self.rigid_body_origin
        rbt = self.rigid_body_target
        if hasattr(rbo, 'blenderObject') and rbo.blenderObject.data:
            rbo.applyImpulse(o.worldPosition, get_direction(o, t) * force)
        if hasattr(rbt, 'blenderObject') and rbt.blenderObject.data:
            rbt.applyImpulse(o.worldPosition, get_direction(t, o) * force)