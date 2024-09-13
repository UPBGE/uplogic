from uplogic.nodes import ULParameterNode


class DictGetKeysNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.dict = None
        self.KEYS = self.add_output(self.get_keys)

    def get_keys(self):
        return list(self.get_input(self.dict).keys())
