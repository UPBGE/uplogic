

from uplogic.nodes import ULParameterNode


class ULInitEmptyList(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.condition = None
        self.length = None
        self.items = None
        self.LIST = self.add_output(self.get_list)

    def get_list(self):
        length = self.get_input(self.length)
        return [None for x in range(length)]
