from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from uplogic.utils import is_invalid
from uplogic.utils import is_waiting


class ULListFromItems(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.items = None
        self.list: list = None
        self.LIST = ULOutSocket(self, self.get_list)

    def get_list(self):
        socket = self.get_output('list')
        if socket is None:
            self.list = self.get_input(self.items)
            return self.set_output('list', [self.get_input(item) for item in self.list])
        return socket

    def evaluate(self):
        self._set_ready()
