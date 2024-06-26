from uplogic.nodes import ULParameterNode


class ULInitNewDict(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.key = None
        self.val = None
        self.DICT = self.add_output(self.get_dict)

    def get_dict(self):
        key = self.get_input(self.key)
        value = self.get_input(self.val)
        return {str(key): value}
