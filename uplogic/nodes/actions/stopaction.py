from uplogic.animation import ULActionSystem
from uplogic.data import GlobalDB
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULStopAction(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.action_layer = None
        self.done = None
        self.act_system = self.get_act_system()
        self.OUT = ULOutSocket(self, self.get_done)
        
    def get_act_system(self):
        act_systems = GlobalDB.retrieve('uplogic.animation')
        if act_systems.check('default'):
            return act_systems.get('default')
        else:
            return ULActionSystem('default')

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        action_layer = self.get_input(self.action_layer)

        action = self.act_system.get_layer(game_object, action_layer)
        if action is not None:
            self.act_system.remove(action)
        self.done = True
