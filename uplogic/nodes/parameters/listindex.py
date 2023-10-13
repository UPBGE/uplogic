from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULListIndex(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.items = None
        self.index = None
        self.OUT = ULOutSocket(self, self.get_val)

    def get_val(self):
        list_d = self.get_input(self.items)
        index = self.get_input(self.index)
        if index <= len(list_d) - 1:
            return list_d[index]
        return None
