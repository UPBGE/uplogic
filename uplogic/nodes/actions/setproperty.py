from uplogic.nodes import ULActionNode


class ULSetProperty(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.property_name = None
        self.property_value = None
        self.mode = 0
        self.OUT = self.add_output(self._get_done)

    def _get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        property_name = self.get_input(self.property_name)
        property_value = self.get_input(self.property_value)
        self._done = True
        obj = game_object.blenderObject if self.mode else game_object
        obj[property_name] = property_value
        if self.mode:
            obj.color = obj.color  # force object data refresh
