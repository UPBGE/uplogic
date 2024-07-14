from uplogic.nodes import ULOutSocket, ULActionNode
from uplogic.utils import make_valid_name


class ULSetLogicTreeProperty(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.prop_name = None
        self.value = None
        self.OUT = self.add_output(self.get_property)

    def get_property(self):
        return self._done

    def evaluate(self):
        property_name = self.get_input(self.prop_name)
        condition = self.get_input(self.condition)
        if not condition:
            return
        setattr(self.network.component, make_valid_name(property_name).lower(), self.get_input(self.value))
        self._done = True
