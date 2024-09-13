from uplogic.nodes import ULActionNode


class ULCopyProperty(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.from_object = None
        self.to_object = None
        self.property_name = None
        self.mode = 0
        self.OUT = self.add_output(self._get_done)

    def _get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        from_object = self.get_input(self.from_object)
        to_object = self.get_input(self.to_object)
        property_name = self.get_input(self.property_name)
        from_object = from_object.blenderObject if self.mode else from_object
        to_object = from_object.blenderObject if self.mode else to_object
        val = from_object.get(property_name)
        if val is not None:
            to_object[property_name] = val
            self._done = True
