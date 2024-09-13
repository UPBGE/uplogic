from uplogic.nodes import ULActionNode
from uplogic.shaders import remove_filter


class ULRemoveFilter(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.pass_idx = None
        self.OUT = self.add_output(self._get_done)

    def _get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        pass_idx = self.get_input(self.pass_idx)
        remove_filter(pass_idx)
        self._done = True
