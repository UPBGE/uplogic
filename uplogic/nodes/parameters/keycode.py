from uplogic.nodes import ULParameterNode

print('Hello')
class ULKeyCode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.key_code = None
        self.OUT = self.add_output(self.get_out)

    def get_out(self):
        return self.get_input(self.key_code)
