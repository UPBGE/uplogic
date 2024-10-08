from uplogic.nodes import ULActionNode


class ULSetActuatorValue(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_obj = None
        self.act_name = None
        self.field = None
        self.value = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        game_obj = self.get_input(self.game_obj)
        act_name = self.get_input(self.act_name)
        if not self.get_condition():
            return
        actuator = game_obj.actuators.get(act_name)
        if not actuator:
            return
        field = self.get_input(self.field)
        value = self.get_input(self.value)
        setattr(actuator, field, value)
        self._done = True
