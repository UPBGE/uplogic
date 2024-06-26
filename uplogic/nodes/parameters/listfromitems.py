from uplogic.nodes import ULParameterNode


class ULListFromItems(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.items: list = None
        self.LIST = self.add_output(self.get_list)

    def get_list(self):
        return [self.get_input(item) for item in self.items]
