from uplogic.nodes import ULConditionNode
from uplogic.utils import is_waiting


class ULPulsify(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.condition = None
        self.status = False

    def evaluate(self):
        socket = self.get_output('status')
        if socket is None:
            condition = self.get_input(self.condition)
            if is_waiting(condition):
                return self.set_output('status', self.status)
            elif condition:
                self.status = not self.status
            self._set_ready()
            self._set_value(self.status)
            self.set_output('status', self.status)
        return socket
