from uplogic.nodes import ULActionNode


class FModSetEventParameterNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = False
        self.event = None
        self.parameter = ''
        self.value = 0.0
        self.ignore_seek = False
        self.DONE = self.add_output(self.get_done)

    def evaluate(self):
        if not self.get_condition():
            return
        evt = self.get_input(self.event)
        if evt is None:
            return
        evt.set_parameter(
            self.get_input(self.parameter),
            float(self.get_input(self.value)),
            self.get_input(self.ignore_seek)
        )
