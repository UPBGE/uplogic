from bge import logic
import bpy
from bge.types import KX_GameObject as GameObject
from random import randint
from random import random
from uplogic.animation import ULActionSystem
from uplogic.data import GlobalDB
from uplogic.events import schedule


PLAY_MODES = {
    'play': logic.KX_ACTION_MODE_PLAY,
    'pingpong': logic.KX_ACTION_MODE_PING_PONG,
    'loop': logic.KX_ACTION_MODE_LOOP
}


BLEND_MODES = {
    'blend': logic.KX_ACTION_BLEND_BLEND,
    'add': logic.KX_ACTION_BLEND_ADD
}


ACTION_STARTED = 'ACTION_STARTED'
ACTION_FINISHED = 'ACTION_FINISHED'


class ULAction():
    '''TODO: Documentation
    '''

    def __init__(
        self,
        game_object: GameObject,
        action_name: str,
        start_frame: int = 0,
        end_frame: int = 250,
        layer: int = -1,
        priority: int = 0,
        blendin: float = 0,
        play_mode: str = 'play',
        speed: float = 1,
        layer_weight: float = 1,
        blend_mode: str = 'blend',
        keep: bool =False
    ):
        self._locked = False
        self._speed = speed
        self._frozen_speed = 0
        self.finished = False
        self.keep = keep
        self._layer_weight = layer_weight
        act_system = 'default'
        self.act_system = self.get_act_sys(act_system)
        self.game_object = game_object
        self.name = action_name
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.priority = priority
        self.blendin = blendin
        self.layer = layer
        play_mode = self.play_mode = PLAY_MODES.get(play_mode, play_mode)
        blend_mode = self.blend_mode = BLEND_MODES.get(blend_mode, blend_mode)
        if layer == -1:
            ULActionSystem.find_free_layer(self)
        elif ULActionSystem.check_layer(self):
            self.finished = True
            return
        layer = self.layer
        same_action = game_object.getActionName(layer) == action_name
        self.on_start()
        if not same_action and self.is_playing:
            game_object.stopAction(layer)
        if not (self.is_playing or same_action):
            game_object.playAction(
                action_name,
                start_frame,
                end_frame,
                play_mode=play_mode,
                speed=speed,
                layer=layer,
                priority=priority,
                blendin=blendin,
                layer_weight=1-layer_weight,
                blend_mode=blend_mode
            )
        self.layer_weight = layer_weight
        self.speed = speed
        self.act_system.add(self)

    def on_start(self):
        schedule(self, ACTION_STARTED)

    def on_finish(self):
        schedule(self, ACTION_FINISHED)

    @property
    def is_playing(self) -> bool:
        if self.game_object.invalid:
            return False
        return self.game_object.isPlayingAction(self.layer)

    @is_playing.setter
    def is_playing(self):
        print('ULAction.is_playing is read-only!')

    @property
    def frame(self) -> float:
        if self.is_playing:
            return self.game_object.getActionFrame(self.layer)
        return -1

    @frame.setter
    def frame(self, value):
        self.game_object.setActionFrame(value, self.layer)

    @property
    def layer_weight(self) -> float:
        return self._layer_weight

    @layer_weight.setter
    def layer_weight(self, value):
        if not self.is_playing or value == self.layer_weight:
            return
        self._layer_weight = value
        self._restart_action()

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, value):
        if value < 0.00000000001:
            value = 0.00000000001
        if not self.is_playing or value == self._speed:
            return
        self._speed = value
        self._restart_action()

    def _restart_action(self):
        self._locked = True
        layer = self.layer
        game_object = self.game_object
        action_name = self.name
        start_frame = self.start_frame
        end_frame = self.end_frame
        play_mode = self.play_mode
        priority = self.priority
        blendin = self.blendin
        layer_weight = self.layer_weight
        speed = self.speed
        blend_mode = self.blend_mode
        frame = self.frame
        reset_frame = (
            start_frame if
            play_mode == logic.KX_ACTION_MODE_LOOP else
            end_frame
        )
        next_frame = (
            frame + speed / 2
            if
            frame + speed / 2 <= end_frame
            else
            reset_frame
        )
        game_object.stopAction(layer)
        game_object.playAction(
            action_name,
            start_frame,
            end_frame,
            layer=layer,
            priority=priority,
            blendin=blendin,
            play_mode=play_mode,
            speed=speed,
            layer_weight=1 - layer_weight,
            blend_mode=blend_mode
        )
        game_object.setActionFrame(next_frame, layer)

    def update(self):
        self._locked = False
        layer_weight = self.layer_weight
        speed = self.speed
        if layer_weight <= 0:
            layer_weight = 0.0
        elif layer_weight >= 1:
            layer_weight = 1.0
        if speed <= 0:
            speed = 0.01
        game_object = self.game_object
        if game_object.invalid:
            self.remove()
            return
        layer = self.layer
        start_frame = self.start_frame
        end_frame = self.end_frame
        action_name = self.name
        play_mode = self.play_mode
        playing_action = game_object.getActionName(layer)
        playing_frame = game_object.getActionFrame(layer)
        min_frame = start_frame
        max_frame = end_frame
        if end_frame < start_frame:
            min_frame = end_frame
            max_frame = max_frame
        if (
            (playing_action == action_name) and
            (playing_frame >= min_frame) and
            (playing_frame <= max_frame)
        ):
            if play_mode == logic.KX_ACTION_MODE_PLAY:
                if end_frame > start_frame:  # play 0 to 100
                    is_near_end = (playing_frame >= (end_frame))
                else:  # play 100 to 0
                    is_near_end = (playing_frame <= (end_frame))
                if is_near_end and not self.keep:
                    self.act_system.remove(self)

    def remove(self):
        self.act_system.remove(self)

    def pause(self):
        self._frozen_speed = self.speed
        self.speed = 0

    def unpause(self):
        self.speed = self._frozen_speed

    def stop(self):
        self.finished = True
        self.on_finish()
        self.game_object.stopAction(self.layer)

    def randomize_frame(self, min=None, max=None):
        if min is None:
            min = self.start_frame
        if max is None:
            max = self.end_frame
        frame = randint(min, max)
        self.frame = frame

    def randomize_speed(self, min=.9, max=1.1):
        delta = max - min
        self.speed = min + (delta * random())

    def set_frame(self, frame):
        self.frame = frame

    def get_act_sys(self, name: str) -> ULActionSystem:
        act_systems = GlobalDB.retrieve('uplogic.animation')
        if act_systems.check(name):
            return act_systems.get(name)
        else:
            return ULActionSystem(name)
