from uplogic.animation import ActionSystem
from uplogic.data import GlobalDB
from uplogic.nodes import ULActionNode


class ULStopAction(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.action_layer = None
        self.act_system = self.get_act_system()
        self.OUT = self.add_output(self.get_done)
        
    def get_act_system(self):
        act_systems = GlobalDB.retrieve('uplogic.animation')
        if act_systems.check('default'):
            return act_systems.get('default')
        else:
            return ActionSystem('default')

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        game_object = self.get_input(self.game_object)
        action_layer = self.get_input(self.action_layer)

        action = self.act_system.get_layer(game_object, action_layer)
        if action is not None:
            self.act_system.remove(action)
        self._done = True
