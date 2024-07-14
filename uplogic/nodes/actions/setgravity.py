from bge import logic
from uplogic.nodes import ULActionNode


class ULSetGravity(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.scene = None
        self.gravity = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        gravity = self.get_input(self.gravity)
        logic.setGravity(gravity)
        self._done = True
