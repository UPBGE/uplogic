from bge import logic
from uplogic.nodes import ULActionNode


class ULSetCursorVisibility(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.visibility_status = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        visibility_status = self.get_input(self.visibility_status)
        logic.mouse.visible = visibility_status
        self._done = True
