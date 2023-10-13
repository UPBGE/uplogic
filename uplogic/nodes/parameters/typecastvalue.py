from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket


class ULTypeCastValue(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.to_type = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        value = self.get_input(self.value)
        return self.typecast_value(value, self.to_type)

    def typecast_value(self, value, t):
        if t == 'int':
            return int(value)
        elif t == 'bool':
            return bool(value)
        elif t == 'str':
            return str(value)
        elif t == 'float':
            return float(value)
        return value
