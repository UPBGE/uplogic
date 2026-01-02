from uplogic.nodes import ULActionNode
from uplogic.utils import make_valid_name


class ToggleLogicTreePropertyNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.prop_name = None
        self.OUT = self.add_output(self.get_property)

    def get_property(self):
        return self._done

    def evaluate(self):
        property_name = self.get_input(self.prop_name)
        condition = self.get_condition()
        if not condition:
            return
        result = getattr(self.network.component, make_valid_name(property_name).lower(), False)
        setattr(self.network.component, make_valid_name(property_name).lower(), not result)
        
        self._done = True
