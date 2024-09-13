from uplogic.nodes import ULActionNode
from uplogic.audio.fmod import Event


class FModModifyEventParameterNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = False
        self.event = None
        self.clamp = False
        self.operation = None
        self.parameter = ''
        self.value = 0.0
        self.DONE = self.add_output(self.get_done)

    def evaluate(self):
        if not self.get_condition():
            return
        evt: Event = self.get_input(self.event)
        if evt is None:
            return
        param = evt.get_parameter(self.get_input(self.parameter))
        result = self.operation(param, self.get_input(self.value))
        evt.set_parameter(
            self.get_input(self.parameter),
            float(result)
        )
