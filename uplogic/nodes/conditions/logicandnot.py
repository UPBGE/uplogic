from uplogic.nodes import ULConditionNode
from uplogic.utils import is_waiting


class ULAndNot(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.condition_a = None
        self.condition_b = None

    def evaluate(self):
        ca = self.get_input(self.condition_a)
        self._set_ready()
        if is_waiting(ca) or not ca:
            self._set_value(False)
            return
        cb = not self.get_input(self.condition_b)
        if is_waiting(cb) or not cb:
            self._set_value(False)
            return
        self._set_value(True)
