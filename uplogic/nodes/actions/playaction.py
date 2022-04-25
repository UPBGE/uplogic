from uplogic.animation import ULActionSystem
from uplogic.data import GlobalDB
from uplogic.animation import ULAction
from uplogic.animation import ACTION_STARTED
from uplogic.animation import ACTION_FINISHED
from uplogic.events import receive
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import STATUS_INVALID, STATUS_WAITING
from uplogic.utils import is_invalid
from uplogic.utils import is_waiting
from uplogic.utils import not_met


class ULPlayAction(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.action_name = None
        self.stop_anim = None
        self.frames = None
        self.start_frame = None
        self.end_frame = None
        self.layer = None
        self.priority = None
        self.play_mode = None
        self.layer_weight = None
        self.old_layer_weight = None
        self.speed = None
        self.old_speed = None
        self.blendin = None
        self.blend_mode = None
        self.in_use = False
        self._started = False
        self._running = False
        self._finished = False
        self._action = None
        self.action_evt = None
        self.act_system = self.get_act_system()
        self.STARTED = ULOutSocket(self, self._get_started)
        self.FINISHED = ULOutSocket(self, self._get_finished)
        self.RUNNING = ULOutSocket(self, self._get_running)
        self.FRAME = ULOutSocket(self, self._get_frame)
        
    def get_act_system(self):
        act_systems = GlobalDB.retrieve('uplogic.animation')
        if act_systems.check('default'):
            return act_systems.get('default')
        else:
            return ULActionSystem('default')

    def _get_started(self):
        if self.action_evt:
            return self.action_evt.content == ACTION_STARTED
        return STATUS_WAITING
    
    def on_finish(self):
        self._finished = True

    def _get_finished(self):
        return self._finished

    def _get_running(self):
        if self._action:
            return self._action.is_playing
        return STATUS_WAITING

    def _get_frame(self):
        if self._action:
            return self._action.frame
        return STATUS_WAITING
    
    def reset(self):
        self._finished = False
        return super().reset()

    def evaluate(self):
        action = self._action
        has_action = action is not None
        condition = self.get_input(self.condition)
        layer_weight = self.get_input(self.layer_weight)
        speed = self.get_input(self.speed)
        layer = self.get_input(self.layer)
        game_object = self.get_input(self.game_object)
        play_mode = self.get_input(self.play_mode)
        self.action_evt = receive(self._action)
        if not_met(condition):
            self._set_ready()
            if has_action:
                action.speed = speed
                action.layer_weight = layer_weight
                if self._action.finished:
                    self._action = None
                    self.in_use = False
                elif play_mode > 2:
                    self._action.remove()
                    self._action = None
                    self.in_use = False
            return
        layer_action: ULAction = self.act_system.get_layer(game_object, layer) 
        if layer_action is not self._action:
            self._action = layer_action 
        action_name = self.get_input(self.action_name)
        if layer_action and layer_action.name == action_name:
            layer_action.speed = speed
            layer_action.layer_weight = layer_weight
            return
        if self.in_use:
            return
        if has_action and action.finished:
            self._action = None
        start_frame = self.get_input(self.start_frame)
        end_frame = self.get_input(self.end_frame)
        priority = self.get_input(self.priority)
        blendin = self.get_input(self.blendin)
        blend_mode = self.get_input(self.blend_mode)
        self._set_ready()
        if is_invalid(game_object):
            return
        if is_waiting(
            action_name,
            start_frame,
            end_frame,
            layer,
            priority,
            play_mode,
            layer_weight,
            speed,
            blendin,
            blend_mode
        ):
            return
        if play_mode > 2:
            play_mode -= 3
        if layer_weight <= 0:
            layer_weight = 0.0
        elif layer_weight >= 1:
            layer_weight = 1.0
        if speed <= 0:
            speed = 0.01
        if is_invalid(game_object):  # can't play
            self._action = None
            self.in_use = False

        self._action = ULAction(
            game_object,
            action_name,
            start_frame,
            end_frame,
            layer,
            priority,
            blendin,
            play_mode,
            speed,
            layer_weight,
            blend_mode
        )
        self._action.on_finish = self.on_finish
        self.in_use = True
