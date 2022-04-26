from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from uplogic.utils import STATUS_WAITING
from uplogic.utils import is_waiting


class ULExtendList(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.list_1: list = None
        self.list_2: list = None
        self.LIST = ULOutSocket(self, self.get_list)

    def get_list(self):
        socket = self.get_output('list')
        if socket is None:
            list_1 = self.get_input(self.list_1)
            list_2 = self.get_input(self.list_2)
            if is_waiting(list_1, list_2):
                return STATUS_WAITING
            return self.set_output('list', list_1.extend(list_2))
        return socket

    def evaluate(self):
        self._set_ready()