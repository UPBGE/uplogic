from uplogic.nodes import ULParameterNode


class ULListDuplicate(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.condition = None
        self.items = None
        self.OUT = self.add_output(self.get_points)

    def get_points(self):
        return self.get_input(self.items).copy()
