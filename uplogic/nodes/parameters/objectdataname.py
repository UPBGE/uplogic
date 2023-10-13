from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULObjectDataName(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.OUT = ULOutSocket(self, self.get_name)

    def get_name(self):
        obj = self.get_input(self.game_object)
        return obj.blenderObject.name
