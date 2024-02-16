from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULDictValue(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.dict = None
        self.key = None
        self.default_value = None
        self.OUT = self.add_output(self.get_val)

    def get_val(self):
        dictionary = self.get_input(self.dict)
        if dictionary is None:
            return None
        key = self.get_input(self.key)
        return dictionary.get(
            key,
            self.get_input(self.default_value)
        )
