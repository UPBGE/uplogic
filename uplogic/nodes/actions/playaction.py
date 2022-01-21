from bge import logic
from uplogic.animation import ULAction
from uplogic.animation import ACTION_STARTED
from uplogic.animation import ACTION_FINISHED
from uplogic.events import receive
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import STATUS_WAITING
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
        self._started = False
        self._running = False
        self._finished = False
        self._action = None
        self.STARTED = ULOutSocket(self, self._get_started)
        self.FINISHED = ULOutSocket(self, self._get_finished)
        self.RUNNING = ULOutSocket(self, self._get_running)
        self.FRAME = ULOutSocket(self, self._get_frame)

    def _get_started(self):
        if self.action_evt:
            return self.action_evt.content == ACTION_STARTED
        return STATUS_WAITING

    def _get_finished(self):
        if self.action_evt:
            return self.action_evt.content == ACTION_FINISHED
        return STATUS_WAITING

    def _get_running(self):
        if self._action:
            return self._action.is_playing
        return STATUS_WAITING

    def _get_frame(self):
        if self._action:
            return self._action.frame
        return STATUS_WAITING

    def evaluate(self):
        condition = self.get_input(self.condition)
        game_object = self.get_input(self.game_object)
        action_name = self.get_input(self.action_name)
        start_frame = self.get_input(self.start_frame)
        end_frame = self.get_input(self.end_frame)
        layer = self.get_input(self.layer)
        priority = self.get_input(self.priority)
        play_mode = self.get_input(self.play_mode)
        layer_weight = self.get_input(self.layer_weight)
        speed = self.get_input(self.speed)
        blendin = self.get_input(self.blendin)
        blend_mode = self.get_input(self.blend_mode)
        self.action_evt = receive(self._action)
        self._set_ready()
        if not_met(condition):
            return
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
            self._action.remove()

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
