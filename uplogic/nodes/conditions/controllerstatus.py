from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import debug


class ULControllerStatus(ULConditionNode):

    def __init__(self):
        ULConditionNode.__init__(self)
        self.obj_name = None
        self.cont_name = None
        self.OUT = ULOutSocket(self, self.get_controller)
        self.SENSORS = ULOutSocket(self, self.get_sensors)

    def get_controller(self):
        game_obj = self.game_obj
        cont = game_obj.controllers[self.controller]
        state = (
            game_obj
            .blenderObject
            .game
            .controllers[self.controller]
            .type
        )
        if not cont.sensors:
            return False
        elif state == 'LOGIC_AND':
            return False not in [sens.positive for sens in cont.sensors]
        elif state == 'LOGIC_OR':
            return True in [sens.positive for sens in cont.sensors]
        elif state == 'LOGIC_NAND':
            return False in [sens.positive for sens in cont.sensors]
        elif state == 'LOGIC_NOR':
            return True not in [sens.positive for sens in cont.sensors]
        elif state == 'LOGIC_XOR':
            return [
                    sens.positive
                    for sens in
                    cont.sensors
                ].count(True) % 2 != 0
        elif state == 'LOGIC_XNOR':
            check = cont.sensors[0].positive
            return False not in [
                    sens.positive == check
                    for sens in
                    cont.sensors
                ]
        else:
            debug('Expression/Python not supported for controller.')
            return False

    def get_sensors(self):
        sensors = {}
        cont = self.controller
        for sens in self.game_obj.controllers[cont].sensors:
            sensors[sens] = sens.positive
        return sensors

    def evaluate(self):
        self.game_obj = self.get_input(self.obj_name)
        self.controller = self.get_input(self.cont_name)
