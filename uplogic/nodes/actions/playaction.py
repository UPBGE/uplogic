from uplogic.animation import ULActionSystem
from uplogic.data import GlobalDB
from uplogic.animation import Action
from uplogic.events import receive
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils.math import clamp
from bpy.types import Action as BPYAction


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
        self.old_intensity = None
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
        return self._action and self._action.started
    
    def on_finish(self):
        self._finished = True

    def _get_finished(self):
        return self._action and self._action.finished

    def _get_running(self):
        if self._action:
            return self._action.is_playing
        return False

    def _get_frame(self):
        if self._action:
            return self._action.frame
        return False
    
    def reset(self):
        self._finished = False
        return super().reset()

    def evaluate(self):
        condition = self.get_input(self.condition)
        intensity = clamp(self.get_input(self.layer_weight))
        speed = self.get_input(self.speed)
        layer = self.get_input(self.layer)
        game_object = self.get_input(self.game_object)
        layer_action: Action = self.act_system.get_layer(game_object, layer)
        if layer_action is not self._action:
            self._action = layer_action
        action = self._action
        has_action = action is not None
        play_mode = self.get_input(self.play_mode)
        self.action_evt = receive(self._action)
        if not condition:
            if has_action:
                action.speed = speed
                action.intensity = intensity
                if self._action.finished:
                    self._action = None
                    self.in_use = False
                elif play_mode > 2:
                    self._action.remove()
                    self._action = None
                    self.in_use = False
            return
        bpy_action: BPYAction = self.get_input(self.action_name)
        if layer_action and layer_action.name == bpy_action:
            layer_action.speed = speed
            layer_action.intensity = intensity
            return
        if self.in_use and has_action:
            return
        if has_action and action.finished:
            self._action = None
        start_frame = self.get_input(self.start_frame)
        end_frame = self.get_input(self.end_frame)
        priority = self.get_input(self.priority)
        blendin = self.get_input(self.blendin)
        blend_mode = self.get_input(self.blend_mode)
        if play_mode > 2:
            play_mode -= 3
        if speed <= 0:
            speed = 0.01

        self._action = Action(
            game_object,
            bpy_action.name,
            start_frame,
            end_frame,
            layer,
            priority,
            blendin,
            play_mode,
            speed,
            intensity,
            blend_mode
        )
        self._action.on_finish = self.on_finish
        self.in_use = True
