from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULActionNode


class ULRunActuator(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_obj = None
        self.cont_name = None
        self.act_name = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
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
        self.done = True
