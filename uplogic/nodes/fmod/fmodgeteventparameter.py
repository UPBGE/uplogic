from uplogic.nodes import ULParameterNode
from uplogic.audio.fmod import Event


class FModGetEventParameterNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.event = None
        self.actual = False
        self.parameter = ''
        self.VAL = self.add_output(self.get_value)

    def get_value(self):
        evt: Event = self.get_input(self.event)
        if evt is None:
            return 0.0
        return evt.get_parameter(self.get_input(self.parameter), self.actual)
