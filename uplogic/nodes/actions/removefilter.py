from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.shaders import remove_filter


class ULRemoveFilter(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.pass_idx = None
        self.done = False
        self.OUT = ULOutSocket(self, self._get_done)

    def _get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        pass_idx = self.get_input(self.pass_idx)
        remove_filter(pass_idx)
        self.done = True
