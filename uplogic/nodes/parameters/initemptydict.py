from uplogic.nodes import ULParameterNode


class ULInitEmptyDict(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.condition = None
        self.dict = None
        self.DICT = self.add_output(self.get_dict)

    def get_dict(self):
        return {}
