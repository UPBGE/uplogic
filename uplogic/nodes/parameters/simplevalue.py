from uplogic.nodes import ULParameterNode


class ULSimpleValue(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        value = self.get_input(self.value)
        return value
