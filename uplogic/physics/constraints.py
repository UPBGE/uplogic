from bge import constraints
from bge import logic
from bge import render
from bge.types import KX_ConstraintWrapper as GameConstraint
from bge.types import KX_GameObject as GameObject
from uplogic.utils import get_direction
from uplogic.utils import set_curve_points


CONSTRAINT_TYPES = {
    'point': 0,
    'hinge': 0,
    'angular': 0,
    'conetwist': 0,
    'generic6dof': 0
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
        self.origin = origin
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
            render.drawLine(
                o.worldPosition,
                t.worldPosition,
                # [1, 1-abs(power), 1-abs(power)]
                [abs(force), 0, 1-abs(force)]
            )
        self.force = force
        if self.curve:
            set_curve_points(self.curve, self.points)
        if self.rigid_body_origin.blenderObject.data:
            self.rigid_body_origin.applyImpulse(o.worldPosition, get_direction(o, t) * force)
        if self.rigid_body_target.blenderObject.data:
            self.rigid_body_target.applyImpulse(o.worldPosition, get_direction(t, o) * force)