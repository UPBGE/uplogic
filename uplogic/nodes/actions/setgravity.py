from bge import logic
from uplogic.nodes import ULActionNode


class ULSetGravity(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.scene = None
        self.gravity = None
        self.done = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        gravity = self.get_input(self.gravity)
        logic.setGravity(gravity)
        self.done = True
