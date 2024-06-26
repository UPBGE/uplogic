from uplogic.nodes import ULConditionNode


class ULOnValueChanged(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.old = None
        self.new = None
        self.current_value = None
        self.initialize = False
        self.OUT = self.add_output(self.get_changed)
        self.OLD = self.add_output(
            self.get_previous_value
        )
        self.NEW = self.add_output(self.get_current_value)

    def get_changed(self):
        curr = self.get_input(self.current_value)
        if not self.initialize:
            self.initialize = True
            self.old = self.new = curr
            return False
        elif self.old != curr:
            self.new = curr
            return True

    def get_previous_value(self):
        return self.old

    def get_current_value(self):
        return self.new

    def reset(self):
        super().reset()
        self.old = self.new
