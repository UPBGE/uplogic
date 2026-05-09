'''Action playback classes for uplogic.

Wraps the BGE ``playAction`` / ``stopAction`` API into the :class:`Action`
class, which integrates with the :class:`~uplogic.animation.actionsystem.ActionSystem`
for automatic layer management and per-frame callbacks.
'''

from bge import logic
from bge.types import KX_GameObject as GameObject
from random import randint
from random import random
from random import uniform
from uplogic.animation import ActionSystem
from uplogic.animation.actionsystem import get_action_system
# from uplogic.events import schedule
from uplogic import console
from uplogic.utils.constants import FRAMETIME_COMPARE
import bpy
from uplogic.utils.math import clamp


PLAY_MODES = {
    'play': logic.KX_ACTION_MODE_PLAY,
    'pingpong': logic.KX_ACTION_MODE_PING_PONG,
    'loop': logic.KX_ACTION_MODE_LOOP
}
'''Mapping from string play-mode names to BGE constants.

Valid keys: ``"play"``, ``"pingpong"``, ``"loop"``.
'''

BLEND_MODES = {
    'blend': logic.KX_ACTION_BLEND_BLEND,
    'add': logic.KX_ACTION_BLEND_ADD
}
'''Mapping from string blend-mode names to BGE constants.

Valid keys: ``"blend"``, ``"add"``.
'''


ACTION_STARTED = 0
ACTION_RUNNING = 1
ACTION_FINISHED = 2


class ActionCallback:
    '''Callback bound to a specific frame of an :class:`Action`.

    When the action's playhead passes :attr:`frame` (in either direction) the
    callback is invoked with the supplied arguments. It resets automatically
    so it fires again on subsequent passes.

    :param action: The :class:`Action` to attach to.
    :param callback: Callable invoked when the frame is passed.
    :param frame: Frame number that triggers the callback.
    :param args: Extra positional arguments forwarded to the callback.
    '''

    def __init__(self, action, callback, frame, *args):
        action._callbacks.append(self)
        self.frame = frame
        self.callback = callback
        self.consumed = False
        self.args = args


class Action:
    '''Wrapper for a BGE ``playAction`` call with live property control.

    Registers itself with the :class:`~uplogic.animation.actionsystem.ActionSystem`
    for per-frame updates, manages layer allocation automatically when
    ``layer=-1``, and supports per-frame callbacks via
    :meth:`frame_trigger`.

    :param game_object: The ``KX_GameObject`` on which to play the action.
    :param action_name: Name of the action in ``bpy.data.actions``.
    :param start_frame: First frame; defaults to the action's own start.
    :param end_frame: Last frame; defaults to the action's own end.
    :param layer: Animation layer. Pass ``-1`` for automatic selection.
    :param priority: Priority within a layer (currently disabled).
    :param blendin: Number of frames to blend in from the previous pose.
    :param play_mode: One of ``"play"``, ``"loop"``, or ``"pingpong"``.
    :param speed: Playback speed multiplier.
    :param intensity: Layer weight (``1.0`` = fully override lower layers).
    :param blend_mode: One of ``"blend"`` or ``"add"``.
    :param keep: When ``True``, keep the action alive after it finishes so
        the final pose is held.
    :param on_start: Optional callable invoked when the action starts.
    '''

    _deprecated = False

    def __init__(
        self,
        game_object: GameObject,
        action_name: str,
        start_frame: int = None,
        end_frame: int = None,
        layer: int = -1,
        priority: int = 0,
        blendin: float = 0,
        play_mode: str = 'play',
        speed: float = 1,
        intensity: float = 1,
        blend_mode: str = 'blend',
        keep: bool = False,
        on_start = None
    ):
        if self._deprecated:
            console.warning('Warning: ULAction class will be renamed to "Action" in future releases!')
        self._fps_factor = bpy.context.scene.render.fps / 60
        self._locked = False
        self._speed = speed
        self._frozen_speed = -1
        self.stopped = False
        '''``True`` once the action has reached its end frame and stopped.'''
        self.keep = keep
        '''When ``True``, the action data is retained after playback ends.'''
        self._intensity = intensity
        self._act_system = get_action_system()
        self.game_object = game_object
        '''The ``KX_GameObject`` this action is playing on.'''
        self._name = action_name
        '''Name of this action in ``bpy.data.actions``.'''
        bpy_act = bpy.data.actions.get(action_name)
        if start_frame is None:
            start_frame = bpy_act.frame_start
        if end_frame is None:
            end_frame = bpy_act.frame_end
        self._start_frame = start_frame
        '''First frame of the animation range.'''
        self._end_frame = end_frame
        '''Last frame of the animation range.'''
        self.priority = priority
        '''Layer priority (currently disabled).'''
        if priority != 0:
            from uplogic.console import debug
            debug("'uplogic.animation.Action' attribute 'priority' is disabled.")
        self.blendin = blendin
        '''Number of frames used to blend in from the previous pose.'''
        self.layer = layer
        '''Animation layer index this action occupies.'''
        self.play_mode = play_mode = PLAY_MODES.get(play_mode, play_mode)
        '''BGE play-mode constant for this action.'''
        self.blend_mode = blend_mode = BLEND_MODES.get(blend_mode, blend_mode)
        '''BGE blend-mode constant for this action.'''
        if layer == -1:
            ActionSystem.find_free_layer(self)
        layer = self.layer
        layer_action_name = game_object.getActionName(layer)
        same_action = layer_action_name == action_name
        self._callbacks: list[ActionCallback] = []
        if on_start:
            self.on_start = on_start
        if (not same_action and self.is_playing):
            game_object.stopAction(layer)
        if not (self.is_playing or same_action):
            game_object.playAction(
                action_name,
                self.start_frame,
                self.end_frame,
                play_mode=play_mode,
                speed=speed,
                layer=layer,
                # priority=priority,
                blendin=blendin,
                layer_weight=1-intensity,
                blend_mode=blend_mode
            )
            self.intensity = intensity
            self.speed = speed
            self.on_start()
            self._act_system.add(self)

    def on_start(self):
        '''Called once when the action begins playing.

        Override this method to react to the action starting.
        '''
        # schedule(self, 0, ACTION_STARTED)
        ...

    def on_finish(self):
        '''Called once when the action reaches its end frame.

        Override this method to react to the action finishing.
        '''
        # schedule(self, 0, ACTION_FINISHED)
        print('FINISH', self.name)
        ...

    def frame_trigger(self, frame, callback, *args):
        '''Bind a callback to a specific frame of this action.

        The callback fires each time the playhead passes *frame* in either
        direction, then resets so it can fire again on the next pass.

        :param frame: Frame number that triggers the callback.
        :param callback: Callable with signature ``def cb(*args)``.
        :param args: Extra arguments forwarded to the callback.
        '''
        ActionCallback(self, callback, frame, *args)

    @property
    def start_frame(self):
        '''First frame of the playback range. Setting this restarts the action.'''
        return self._start_frame

    @start_frame.setter
    def start_frame(self, val):
        r = val != self._start_frame
        self._start_frame = val
        if r:
            self._restart_action()

    @property
    def end_frame(self):
        '''Last frame of the playback range. Setting this restarts the action.'''
        return self._end_frame

    @end_frame.setter
    def end_frame(self, val):
        if val < self.start_frame:
            self._start_frame = val - 1
        r = val != self._end_frame
        self._end_frame = val
        if r:
            self._restart_action()

    @property
    def is_playing(self) -> bool:
        '''``True`` if the action is currently playing on its layer (read-only).'''
        if self.game_object.invalid:
            return False
        return self.game_object.isPlayingAction(self.layer)

    @is_playing.setter
    def is_playing(self):
        console.debug('ULAction.is_playing is read-only!')

    @property
    def started(self):
        '''``True`` during the first frame of playback.'''
        return self.frame - self.start_frame < self.speed * FRAMETIME_COMPARE

    @property
    def finished(self):
        '''``True`` when the playhead is within one frame of the end.'''
        return self.end_frame - self.frame < 1

    @property
    def frame(self) -> float:
        '''Current playhead position in frames.'''
        if self.is_playing:
            return self.game_object.getActionFrame(self.layer)
        return self.end_frame
        # return -1

    @frame.setter
    def frame(self, value: float):
        self.game_object.setActionFrame(value, self.layer)

    @property
    def intensity(self) -> float:
        '''Layer weight in the range ``[0, 1]``. Higher layers blend over lower
        ones; setting to ``0`` stops the action.
        '''
        return self._intensity

    @intensity.setter
    def intensity(self, value: float):
        if value == self._intensity:
            return
        value = float(value)
        self._intensity = clamp(value, 0, 1)
        if value <= 0:
            if self.is_playing:
                self.game_object.stopAction(self.layer)
            return
        self._restart_action()

    @property
    def speed(self) -> float:
        '''Playback speed multiplier (``1.0`` = normal speed).'''
        return self._speed

    @speed.setter
    def speed(self, value: float):
        if value < 0.00000000001:
            value = 0.00000000001
        if not self.is_playing or value == self._speed:
            return
        self._speed = value
        if self.intensity > 0:
            self._restart_action()

    @property
    def name(self):
        '''Name of the action in ``bpy.data.actions``. Setting this switches
        to a different action and restarts playback.
        '''
        return self._name

    @name.setter
    def name(self, value):
        if value == self.name:
            return
        self._name = value
        self._restart_action()

    def _restart_action(self):
        '''Restart the BGE action to apply changed parameters (speed, frames,
        intensity, name). Not intended for direct use.
        '''
        # if self.name == 'jump':
        #     print('update')
        # XXX: This lockes eternally for some reason
        # if self._locked is True:
        #     return
        layer = self.layer
        game_object = self.game_object
        action_name = self.name
        start_frame = self.start_frame
        end_frame = self.end_frame
        play_mode = self.play_mode
        blendin = self.blendin
        intensity = self.intensity
        speed = self.speed * self._fps_factor * logic.getTimeScale()
        blend_mode = self.blend_mode
        frame = self.frame
        # if not self.is_playing:
        #     print(self.name)
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
            # priority=0,
            blendin=blendin,
            play_mode=play_mode,
            speed=self.speed,
            layer_weight=1 - intensity,
            blend_mode=blend_mode
        )
        game_object.setActionFrame(next_frame, layer)
        self._locked = True

    def update(self):
        '''Per-frame update: fire any due :class:`ActionCallback` entries and
        stop the action when it reaches the end frame in ``"play"`` mode.

        Called automatically by the :class:`~uplogic.animation.actionsystem.ActionSystem`.
        '''
        # print(self.name)
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
        for action_callback in self._callbacks:
            cond = (
                playing_frame > action_callback.frame
                if end_frame > start_frame else
                playing_frame < action_callback.frame
            )
            if cond:
                if not action_callback.consumed:
                    action_callback.callback(*action_callback.args)
                    action_callback.consumed = True
            else:
                action_callback.consumed = False
        if end_frame < start_frame:
            start_frame, end_frame = end_frame, start_frame
        if (
            (playing_action == self.name) and
            (playing_frame >= start_frame) and
            (playing_frame <= end_frame)
        ):
            if self.play_mode == logic.KX_ACTION_MODE_PLAY:
                if end_frame > start_frame:
                    is_at_end = (playing_frame >= (end_frame))
                else:
                    is_at_end = (playing_frame <= (end_frame))
                if is_at_end:
                    # self.on_finish()
                    # self.game_object.stopAction(self.layer)
                    if not self.keep:
                        self.stop()
                        # self._act_system.remove(self)

    def remove(self):
        '''Stop this action and remove it from the action system.'''
        self._act_system.remove(self)

    def pause(self):
        '''Freeze playback by setting speed to zero; the pose is held.'''
        if self._frozen_speed < 0:
            self._frozen_speed = self.speed
            self.speed = 0

    def unpause(self):
        '''Resume playback at the speed that was active before :meth:`pause`.'''
        if self._frozen_speed >= 0:
            self.speed = self._frozen_speed
            self._frozen_speed = -1

    def resume(self):
        '''Resume playback at the speed that was active before :meth:`pause`.'''
        if self._frozen_speed >= 0:
            self.speed = self._frozen_speed
            self._frozen_speed = -1

    def stop(self):
        '''Stop playback of this action and free its layer.'''
        self._act_system.remove(self)

    def disable(self):
        '''Stop the BGE action on this layer without removing the action from
        the system.
        '''
        self.game_object.stopAction(self.layer)

    def _stop(self):
        self.stopped = True
        self.on_finish()
        self.game_object.stopAction(self.layer)

    def restart(self):
        '''Restart this action from its start frame using current parameters.'''
        self._act_system.add(self)
        self.stopped = False
        self.game_object.stopAction(self.layer)
        self.game_object.playAction(
            self.name,
            self.start_frame,
            self.end_frame,
            layer=self.layer,
            blendin=self.blendin,
            play_mode=self.play_mode,
            speed=self.speed,
            layer_weight=1-self.intensity,
            blend_mode=self.blend_mode
        )

    def randomize_frame(self, min: float = -1, max: float = -1):
        '''Jump to a random frame within the given range.

        :param min: Lower bound; defaults to :attr:`start_frame`.
        :param max: Upper bound; defaults to :attr:`end_frame`.
        '''
        if min == -1:
            min = self.start_frame
        if max == -1:
            max = self.end_frame
        frame = uniform(min, max)
        self.frame = frame

    def randomize_speed(self, min: float = .9, max: float = 1.1):
        '''Set a random playback speed within the given range.

        :param min: Lower bound for the speed multiplier.
        :param max: Upper bound for the speed multiplier.
        '''
        delta = max - min
        self.speed = min + (delta * random())

    def set_frame(self, frame: float):
        '''Seek to *frame* on this action's layer.

        :param frame: Target frame number.
        '''
        self.frame = frame

class ULAction(Action):
    '''[DEPRECATED] Use :class:`Action` instead.'''
    _deprecated = True


def start_action(
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
        keep: bool = False,
        on_start = None
    ):
    '''Create and start an :class:`Action` on *game_object*.

    All parameters mirror :class:`Action.__init__`.

    :returns: The new :class:`Action` instance.
    '''
    return Action(
        game_object=game_object,
        action_name=action_name,
        start_frame=start_frame,
        end_frame=end_frame,
        layer=layer,
        priority=priority,
        blendin=blendin,
        play_mode=play_mode,
        speed=speed,
        intensity=intensity,
        blend_mode=blend_mode,
        keep=keep,
        on_start=on_start
    )
