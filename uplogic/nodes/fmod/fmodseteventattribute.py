from uplogic.nodes import ULActionNode


class FModSetEventAttributeNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = False
        self.event = None
        self.attribute = 'position'
        self.value = 0.0
        self.EVT = self.add_output(self.get_evt)
        self.VALUE = self.add_output(self.get_value)

    def get_evt(self):
        return self.get_input(self.event)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        setattr(
            self.get_input(self.event),
            self.attribute,
            self.get_input(self.value)
        )
