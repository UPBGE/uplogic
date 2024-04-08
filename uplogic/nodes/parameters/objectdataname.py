from uplogic.nodes import ULParameterNode


class ULObjectDataName(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.OUT = self.add_output(self.get_name)

    def get_name(self):
        obj = self.get_input(self.game_object)
        return obj.blenderObject.name
