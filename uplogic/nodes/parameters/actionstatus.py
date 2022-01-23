from uplogic.animation import ULActionSystem
from uplogic.data import GlobalDB
from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from uplogic.utils import STATUS_WAITING
from uplogic.utils import is_invalid
from uplogic.utils import is_waiting


class ULActionStatus(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.action_layer = None
        self._action_name = None
        self._action_frame = None
        self.action = None
        self.act_system = self.get_act_system()
        self.ACTION_NAME = ULOutSocket(self, self.get_action_name)
        self.ACTION_FRAME = ULOutSocket(self, self.get_action_frame)
        
    def get_act_system(self):
        act_systems = GlobalDB.retrieve('uplogic.animation')
        if act_systems.check('default'):
            return act_systems.get('default')
        else:
            return ULActionSystem('default')

    def get_action_name(self):
        if self.action:
            return self.action.name
        return STATUS_WAITING

    def get_action_frame(self):
        if self.action:
            return self.action.frame
        return STATUS_WAITING

    def evaluate(self):
        game_object = self.get_input(self.game_object)
        action_layer = self.get_input(self.action_layer)
        if is_waiting(game_object, action_layer):
            return
        self._set_ready()
        self.action = self.act_system.get_layer(game_object, action_layer)
        if self.action is None:
            self._set_value(False)
            return
        self._set_value(self.action.is_playing)
