from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.shaders import set_filter_state


class ULSetFilterState(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.pass_idx = None
        self.state = None
        self.done = False
        self.OUT = ULOutSocket(self, self._get_done)

    def _get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        pass_idx = self.get_input(self.pass_idx)
        state = self.get_input(self.state)
        set_filter_state(pass_idx, state)
        self.done = True
