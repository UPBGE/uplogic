from bge import constraints
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULAddPhysicsConstraint(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.target = None
        self.child = None
        self.name = None
        self.constraint = None
        self.use_world = None
        self.pivot = None
        self.use_limit = None
        self.axis_limits = None
        self.linked_col = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        target = self.get_input(self.target)
        child = self.get_input(self.child)
        name = self.get_input(self.name)
        constraint = self.get_input(self.constraint)
        pivot = self.get_input(self.pivot)
        use_limit = self.get_input(self.use_limit)
        use_world = self.get_input(self.use_world)
        axis_limits = self.get_input(self.axis_limits)
        linked_col = self.get_input(self.linked_col)
        flag = 0 if linked_col else 128
        if use_world:
            pivot.x -= target.localPosition.x
            pivot.y -= target.localPosition.y
            pivot.z -= target.localPosition.z
        if use_limit:
            target[name] = constraints.createConstraint(
                target.getPhysicsId(),
                child.getPhysicsId(),
                constraint,
                pivot_x=pivot.x,
                pivot_y=pivot.y,
                pivot_z=pivot.z,
                axis_x=axis_limits.x,
                axis_y=axis_limits.y,
                axis_z=axis_limits.z,
                flag=flag
            )
        else:
            target[name] = constraints.createConstraint(
                target.getPhysicsId(),
                child.getPhysicsId(),
                constraint,
                pivot_x=pivot.x,
                pivot_y=pivot.y,
                pivot_z=pivot.z,
                flag=flag
            )
        self.done = True
