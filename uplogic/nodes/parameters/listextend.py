from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULListExtend(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.list_1: list = None
        self.list_2: list = None
        self.OUT = ULOutSocket(self, self.get_done)
        self.LIST = ULOutSocket(self, self.get_list)

    def get_done(self):
        return False

    def get_list(self):
        list_1 = self.get_input(self.list_1)
        list_2 = self.get_input(self.list_2)
        return list_1.extend(list_2)
