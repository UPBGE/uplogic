from uplogic.nodes import ULParameterNode

class ULGetSound(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.sound = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self.get_input(self.sound)
