from uplogic.nodes import ULParameterNode


class FModGetEventAttributeNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.event = None
        self.attribute = 'position'
        self.EVT = self.add_output(self.get_evt)
        self.VALUE = self.add_output(self.get_value)

    def get_evt(self):
        return self.get_input(self.event)

    def get_value(self):
        return getattr(self.get_input(self.event), self.attribute, None)
