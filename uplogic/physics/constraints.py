from bge import constraints
from bge.types import KX_ConstraintWrapper as GameConstraint
from bge.types import KX_GameObject as GameObject


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
