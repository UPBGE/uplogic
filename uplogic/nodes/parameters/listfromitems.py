from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULListFromItems(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.items = None
        self.list: list = None
        self.LIST = ULOutSocket(self, self.get_list)

    def get_list(self):
        return [self.get_input(item) for item in self.list]
