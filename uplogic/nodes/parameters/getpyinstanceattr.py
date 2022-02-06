from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import STATUS_INVALID, STATUS_WAITING
from uplogic.utils import is_waiting


class ULGetPyInstanceAttr(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.instance = None
        self.attr = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        instance = self.get_input(self.instance)
        attr = self.get_input(self.attr)
        if is_waiting(instance, attr):
            return STATUS_WAITING
        return getattr(instance, attr, STATUS_INVALID)

    def evaluate(self):
        self._set_ready()
