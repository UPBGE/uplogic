from uplogic.nodes import ULParameterNode


class ULStoreValue(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self.initialize = True
        self.condition = None
        self._stored_value = None

        # WEIRD NAMING: self._done = Condition, self.OUT = Stored value
        self._done = self.add_output(self.get_stored)
        self.OUT = self.add_output(self.get_done)

    def get_stored(self):
        return self._done

    def get_done(self):
        return self._stored_value

    def evaluate(self):
        condition = self.get_input(self.condition)
        if self.initialize:
            self.initialize = False
            condition = True
        if not condition:
            return
        self._stored_value = self.get_input(self.value)
        self._done = True
