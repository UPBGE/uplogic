from uplogic.animation import ULActionSystem
from uplogic.animation.action import ULAction
from uplogic.data import GlobalDB
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import is_invalid
from uplogic.utils import is_waiting
from uplogic.utils import not_met
import bpy


class ULSetActionFrame(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.action_layer = None
        self.action_frame = None
        self.action_name = None
        self.layer_weight = None
        self.freeze = None
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
        condition = self.get_input(self.condition)
        if not_met(condition):
            self._set_ready()
            return
        game_object = self.get_input(self.game_object)
        action_layer = self.get_input(self.action_layer)
        action_frame = self.get_input(self.action_frame)
        freeze = self.get_input(self.freeze)
        action_name = self.get_input(self.action_name)
        layer_weight = self.get_input(self.layer_weight)
        self._set_ready()
        if is_waiting(
            action_layer,
            action_frame,
            layer_weight
        ):
            return
        if is_invalid(
            game_object,
        ):
            return

        action = self.act_system.get_layer(game_object, action_layer)
        same_action = action is not None and action.name == action_name
        if not same_action or action is None:
            action = bpy.data.actions[action_name]
            start_frame = action.frame_range[0]
            end_frame = action.frame_range[1]
            action = ULAction(
                game_object,
                action_name,
                start_frame,
                end_frame,
                action_layer,
                layer_weight=layer_weight
            )

        game_object.setActionFrame(action_frame, action_layer)
        if freeze:
            action.speed = 0
        action.layer_weight = layer_weight
        self.done = True
