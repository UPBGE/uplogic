'''yes
'''

from bge import logic
from bge.types import KX_GameObject as GameObject
from random import randint
from random import random
from uplogic.animation import ULActionSystem
from uplogic.animation.actionsystem import get_action_system
from uplogic.events import schedule
import bpy
from uplogic.utils.math import clamp


PLAY_MODES = {
    'play': logic.KX_ACTION_MODE_PLAY,
    'pingpong': logic.KX_ACTION_MODE_PING_PONG,
    'loop': logic.KX_ACTION_MODE_LOOP
}
"""Available play modes of [`"play"`, `"pingpong"`, `"loop"`]"""


BLEND_MODES = {
    'blend': logic.KX_ACTION_BLEND_BLEND,
    'add': logic.KX_ACTION_BLEND_ADD
}
"""Available blending modes of [`"blend"`, `"add"`]"""


ACTION_STARTED = 'ACTION_STARTED'
ACTION_FINISHED = 'ACTION_FINISHED'


class ULAction():
    '''
    [DEPRECATED] Use `uplogic.animation.action` instead.

    Wrapper class for animated actions that provides additional parameters
    and quick access properties.

    :param `game_object`: The `KX_GameObject` on which to play the action.
    :param `action_name`: The name of the action  of `bpy.data.actions`.
    :param `start_frame`: The first frame of the action.
    :param `end_frame`: The last frame of the action.
    :param `layer`: The layer on which to play the action. Leave at -1 for
    auto-selection.
    :param `priority`: The priority with which to play the action (only relevant
    for actions on the same layer).
    :param `blendin`: Use this many frames to "blend into" the animation.
    :param `play_mode`: Mode of playback of [`'play'`, `'loop'`, `'pingpong'`].
    :param `speed`: Playback speed.
    :param `intensity`: "Intensity" of the action; Use this to blend
    animations on different layers together.
    :param `blend_mode`: Mode of blending of [`'blend'`, `'add'`]
    :param `keep`: Whether to keep the animation cached after playback has
    finished. This is useful for setting animation frames regardless of the
    action state.
    '''

    _deprecated = True

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
        intensity: float = 1,
        blend_mode: str = 'blend',
        keep: bool = False
    ):
        if self._deprecated:
            print('Warning: ULAction class will be renamed to "Action" in future releases!')
        self._fps_factor = bpy.context.scene.render.fps / 60
        self._locked = False
        self._speed = speed
        self._frozen_speed = speed
        self.stopped = False
        '''Finish state of the animation.'''
        self.keep = keep
        '''Whether to keep or free animation data after playback has finished.'''
        self._intensity = intensity
        self._act_system = get_action_system()
        self.game_object = game_object
        '''The game object the animation is playing on.'''
        self.name = action_name
        '''Name of this action.'''
        self.start_frame = start_frame
        '''Starting Frame of the animation.'''
        self.end_frame = end_frame
        '''End Frame of the animation.'''
        self.priority = priority
        '''Priority of this animation; This is only relevant if multiple
        animations are playing on the same layer.'''
        self.blendin = blendin
        '''The amount of blending frames when starting the animation.'''
        self.layer = layer
        '''The layer the animation is playing on.'''
        self.play_mode = play_mode = PLAY_MODES.get(play_mode, play_mode)
        '''Playback mode of the animation.'''
        self.blend_mode = blend_mode = BLEND_MODES.get(blend_mode, blend_mode)
        '''Blending Mode of the animation.'''
        if layer == -1:
            ULActionSystem.find_free_layer(self)
        # elif ULActionSystem.check_layer(self):
            # self.finished = True
            # return
        layer = self.layer
        layer_action_name = game_object.getActionName(layer)
        same_action = layer_action_name == action_name
        self.on_start()
        if (not same_action and self.is_playing):
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
                layer_weight=1-intensity,
                blend_mode=blend_mode
            )
        self.intensity = intensity
        self.speed = speed
        self._act_system.add(self)

    def on_start(self):
        '''Handler for animation playback start.
        '''
        schedule(self, 0, ACTION_STARTED)

    def on_finish(self):
        '''Handler for animation playback finish.
        '''
        schedule(self, 0, ACTION_FINISHED)

    @property
    def is_playing(self) -> bool:
        '''Check if the animation is being played (Read-Only).'''
        if self.game_object.invalid:
            return False
        return self.game_object.isPlayingAction(self.layer)

    @is_playing.setter
    def is_playing(self):
        print('ULAction.is_playing is read-only!')

    @property
    def started(self):
        return self.frame - self.start_frame < self.speed

    @property
    def finished(self):
        return self.end_frame - self.frame < self.speed

    @property
    def frame(self) -> float:
        '''Current Frame of the animation.'''
        if self.is_playing:
            return self.game_object.getActionFrame(self.layer)
        return -1

    @frame.setter
    def frame(self, value: float):
        self.game_object.setActionFrame(value, self.layer)

    @property
    def intensity(self) -> float:
        '''Intensity of the animation. Higher layers can be blended over lower
        ones.'''
        return self._intensity

    @intensity.setter
    def intensity(self, value: float):
        value = float(value)
        if not self.is_playing:
            return
        if not self.is_playing or value == self._intensity:
            return
        self._intensity = clamp(value, 0, 1)
        self._restart_action()

    @property
    def speed(self) -> float:
        '''Playback speed of the animation.'''
        return self._speed

    @speed.setter
    def speed(self, value: float):
        if value < 0.00000000001:
            value = 0.00000000001
        if not self.is_playing or value == self._speed:
            return
        self._speed = value
        self._restart_action()

    def _restart_action(self):
        '''Restart action to use updated values.

        Not intended for manual use.
        '''
        if self._locked:
            return
        self._locked = True
        layer = self.layer
        game_object = self.game_object
        action_name = self.name
        start_frame = self.start_frame
        end_frame = self.end_frame
        play_mode = self.play_mode
        priority = self.priority
        blendin = self.blendin
        intensity = self.intensity
        speed = self.speed * self._fps_factor * logic.getTimeScale()
        blend_mode = self.blend_mode
        frame = self.frame
        reset_frame = (
            start_frame if
            play_mode == logic.KX_ACTION_MODE_LOOP else
            end_frame
        )
        next_frame = (
            frame + speed
            if
            frame + speed <= end_frame
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
            speed=self.speed,
            layer_weight=1 - intensity,
            blend_mode=blend_mode
        )
        game_object.setActionFrame(next_frame, layer)

    def update(self):
        '''This is called each frame.
        '''
        self._locked = False
        game_object = self.game_object
        if game_object.invalid:
            self.remove()
            return
        if not self.intensity:
            return
        layer = self.layer
        start_frame = self.start_frame
        end_frame = self.end_frame
        playing_action = game_object.getActionName(layer)
        playing_frame = game_object.getActionFrame(layer)
        if end_frame < start_frame:
            start_frame, end_frame = end_frame, start_frame
        if (
            (playing_action == self.name) and
            (playing_frame >= start_frame) and
            (playing_frame <= end_frame)
        ):
            if self.play_mode == logic.KX_ACTION_MODE_PLAY:
                if end_frame > start_frame:
                    is_near_end = (playing_frame >= (end_frame))
                else:
                    is_near_end = (playing_frame <= (end_frame))
                if is_near_end and not self.keep:
                    self._act_system.remove(self)

    def remove(self):
        '''Stop and remove this action.
        '''
        self._act_system.remove(self)

    def pause(self):
        '''Pause this action.
        '''
        self._frozen_speed = self.speed
        self.speed = 0

    def unpause(self):
        '''Unpause this action.
        '''
        self.speed = self._frozen_speed

    def stop(self):
        '''Stop playback of this action.
        '''
        self.stopped = True
        self.on_finish()
        self.game_object.stopAction(self.layer)

    def restart(self):
        '''Restart this animation with its current parameters.
        '''
        self.stopped = False
        self.game_object.stopAction(self.layer)
        self.game_object.playAction(
            self.name,
            self.start_frame,
            self.end_frame,
            layer=self.layer,
            priority=self.priority,
            blendin=self.blendin,
            play_mode=self.play_mode,
            speed=self.speed,
            layer_weight=1 - self.intensity,
            blend_mode=self.blend_mode
        )

    def randomize_frame(self, min: float = -1, max: float = -1):
        '''Randomize the frame of this animation.

        :param `min`: Min range of randomization (Optional).
        :param `max`: Max range of randomization (Optional).
        '''
        if min == -1:
            min = self.start_frame
        if max == -1:
            max = self.end_frame
        frame = randint(min, max)
        self.frame = frame

    def randomize_speed(self, min: float = .9, max: float = 1.1):
        '''Randomize the speed of this animation.

        :param `min`: Min range of randomization (Optional, default 0.9).
        :param `max`: Max range of randomization (Optional, default 1.1).
        '''
        delta = max - min
        self.speed = min + (delta * random())

    def set_frame(self, frame: float):
        '''Set the frame of this action.
        '''
        self.frame = frame

class Action(ULAction):
    '''Wrapper class for animated actions that provides additional parameters
    and quick access properties.

    :param `game_object`: The `KX_GameObject` on which to play the action.
    :param `action_name`: The name of the action  of `bpy.data.actions`.
    :param `start_frame`: The first frame of the action.
    :param `end_frame`: The last frame of the action.
    :param `layer`: The layer on which to play the action. Leave at -1 for
    auto-selection.
    :param `priority`: The priority with which to play the action (only relevant
    for actions on the same layer).
    :param `blendin`: Use this many frames to "blend into" the animation.
    :param `play_mode`: Mode of playback of [`'play'`, `'loop'`, `'pingpong'`].
    :param `speed`: Playback speed.
    :param `intensity`: "Intensity" of the action; Use this to blend
    animations on different layers together.
    :param `blend_mode`: Mode of blending of [`'blend'`, `'add'`]
    :param `keep`: Whether to keep the animation cached after playback has
    finished. This is useful for setting animation frames regardless of the
    action state.'''
    _deprecated = False
    pass