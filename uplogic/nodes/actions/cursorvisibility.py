from bge import logic
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetCursorVisibility(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.visibility_status = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        visibility_status = self.get_input(self.visibility_status)
        logic.mouse.visible = visibility_status
        self.done = True
