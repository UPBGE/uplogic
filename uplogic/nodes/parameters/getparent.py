from uplogic.nodes import ULParameterNode


class ULGetParent(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.OUT = self.add_output(self.get_parent)

    def get_parent(self):
        return self.get_input(self.game_object).parent
