from bge import constraints
from uplogic.nodes import ULActionNode


class ULRemovePhysicsConstraint(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.object = None
        self.name = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        obj = self.get_input(self.object)
        name = self.get_input(self.name)
        constraints.removeConstraint(obj[name].getConstraintId())
        self._done = True
