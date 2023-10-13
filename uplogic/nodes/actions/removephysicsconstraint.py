from bge import constraints
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULRemovePhysicsConstraint(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.object = None
        self.name = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        obj = self.get_input(self.object)
        name = self.get_input(self.name)
        constraints.removeConstraint(obj[name].getConstraintId())
        self.done = True
