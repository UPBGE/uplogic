from uplogic.nodes import ULOutSocket, ULParameterNode


class ULKeyCode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.key_code = None
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        return self.get_input(self.key_code)
