from uplogic.nodes import ULActionNode


class ULRunActuator(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_obj = None
        self.cont_name = None
        self.act_name = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        game_obj = self.get_input(self.game_obj)
        cont_name = self.get_input(self.cont_name)
        act_name = self.get_input(self.act_name)
        controller = game_obj.controllers[cont_name]
        if act_name not in controller.actuators:
            return
        actuator = controller.actuators[act_name]
        if not self.get_input(self.condition):
            return
        controller.activate(actuator)
        self._done = True
