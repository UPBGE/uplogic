from uplogic.animation import ULActionSystem
from uplogic.data import GlobalDB
from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULActionStatus(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.action_layer = None
        self._action_name = None
        self._action_frame = None
        self.action = None
        self._playing = False
        self.act_system = self.get_act_system()
        self.OUT = ULOutSocket(self, self.get_out)
        self.ACTION_NAME = ULOutSocket(self, self.get_action_name)
        self.ACTION_FRAME = ULOutSocket(self, self.get_action_frame)

    def get_out(self):
        return bool(self.action and self.action.is_playing)

    def get_act_system(self):
        act_systems = GlobalDB.retrieve('uplogic.animation')
        if act_systems.check('default'):
            return act_systems.get('default')
        else:
            return ULActionSystem('default')

    def get_action_name(self):
        return self.action.name if self.action else None

    def get_action_frame(self):
        return self.action.frame if self.action else None

    def evaluate(self):
        game_object = self.get_input(self.game_object)
        action_layer = self.get_input(self.action_layer)
        self.action = self.act_system.get_layer(game_object, action_layer)
