from uplogic.animation import ULActionSystem
from uplogic.animation.action import Action
from uplogic.data import GlobalDB
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from bpy.types import Action as BPYAction
from bge.types import KX_GameObject


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
        if not self.get_input(self.condition):
            return
        game_object: KX_GameObject = self.get_input(self.game_object)
        action_layer = self.get_input(self.action_layer)
        action_frame = self.get_input(self.action_frame)
        freeze = self.get_input(self.freeze)
        bpy_action: BPYAction = self.get_input(self.action_name)
        intensity = self.get_input(self.layer_weight)
        action: Action = self.act_system.get_layer(game_object, action_layer)
        same_action = action is not None and action.name == bpy_action.name
        if not same_action or action is None:
            start_frame = bpy_action.frame_range[0]
            end_frame = bpy_action.frame_range[1]
            action = Action(
                game_object,
                bpy_action.name,
                start_frame,
                end_frame,
                action_layer,
                intensity=intensity
            )

        game_object.setActionFrame(action_frame, action_layer)
        action._intensity = intensity
        if freeze:
            action._speed=.00000000001
        action._restart_action()
        self.done = True
