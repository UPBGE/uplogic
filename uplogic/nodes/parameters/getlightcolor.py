from uplogic.nodes import ULParameterNode


class ULGetLightColor(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.lamp = None
        self.color = 0
        self.COLOR = self.add_output(self.get_color)

    def get_color(self):
        lamp = self.get_input(self.lamp)
        light = lamp.blenderObject.data
        return light.color
