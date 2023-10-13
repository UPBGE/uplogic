from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket


class ULValueChangedTo(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.monitored_value = None
        self.trigger_value = None
        self.changed = None
        self.old = None
        self.OUT = ULOutSocket(self, self.get_changed)

    def get_changed(self):
        monitored_value = self.get_input(self.monitored_value)
        trigger_value = self.get_input(self.trigger_value)
        return (
            monitored_value == trigger_value and
            self.changed
        )

    def evaluate(self):
        monitored_value = self.get_input(self.monitored_value)
        self.changed = monitored_value != self.old
        self.old = monitored_value
