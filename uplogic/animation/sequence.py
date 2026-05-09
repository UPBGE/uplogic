from bge import logic
from uplogic.animation.action import PLAY_MODES
import bpy
import time
from bpy.types import ShaderNodeSpritesAnimation
from bpy.types import ShaderNodeTexImage
from bpy.types import Material
import gpu
from os.path import isfile
from uplogic.utils import clamp



class Sequence():
    '''Drive a sprite-sheet or image-sequence animation through a Blender
    material node, updated in real-time via the scene ``pre_draw`` callback.

    Supports ``ShaderNodeSpritesAnimation`` and ``ShaderNodeTexImage`` nodes.
    All objects sharing the material will display the same frame.

    :param material: Name of the ``bpy.data.materials`` entry to animate.
    :param node: Name of the shader node that holds the image animation.
    :param start_frame: First frame of the playback range.
    :param end_frame: Last frame of the playback range.
    :param fps: Playback speed in frames per second.
    :param mode: One of ``"play"``, ``"loop"``, or ``"pingpong"``.
    '''

    _deprecated = False

    @property
    def frame(self):
        '''Current frame index shown on the node. Setting writes through to the
        node and calls ``material.update_tag()`` to flush the change.
        '''
        if self._node_type:
            return self.player.frame_offset
        return round(self.player.inputs[0].default_value)

    @frame.setter
    def frame(self, frame):
        if self._node_type:
            self.player.frame_offset = round(frame)
        else:
            self.player.inputs[0].default_value = frame
        self.material.update_tag()

    @property
    def player(self):
        '''The ``image_user`` of the underlying shader node (read-only).'''
        self._node.image_user

    def __init__(
        self,
        material: str,
        node: str,
        start_frame: int,
        end_frame: int,
        fps: int = 60,
        mode: str = 'play'
    ) -> None:
        if self._deprecated:
            from uplogic.console import warning
            warning('Warning: ULSequence class will be renamed to "ULSequence" in future releases!')

        self.material = bpy.data.materials[material]
        '''The Blender material this sequence is played on.'''
        self.node = node
        '''Name of the shader node that drives the image animation.'''
        self.start_frame = start_frame
        '''First frame of the playback range.'''
        self.end_frame = end_frame - .01  # .01 because the sprite node shows the next frame when numer is round
        '''Last frame of the playback range (offset by -0.01 to avoid showing the next frame).'''
        self.fps = fps
        '''Playback speed in frames per second.'''
        self.mode = mode
        '''Playback mode: ``"play"``, ``"loop"``, or ``"pingpong"``.'''
        self.time = 0.0
        '''Accumulated real-time seconds used to advance frames.'''
        # self.frame = 0
        self.on_start = False
        '''``True`` on the frame when the animation (re-)starts.'''
        self.on_finish = False
        '''``True`` on the frame when the animation finishes.'''
        self._initialized = False
        self._reverse = False
        self._running = True
        self._consumed = False
        self._node_type = 0
        self._pause = False
        self._time_then = time.time()
        node = (
            self.material
            .node_tree
            .nodes[node]
        )
        self._node = node


        if isinstance(node, ShaderNodeSpritesAnimation):
            self._node_type = 0
        elif isinstance(node, ShaderNodeTexImage):
            self._node_type = 1
        else:
            return
        self.frame = start_frame
        logic.getCurrentScene().pre_draw.append(self.update)

    def stop(self):
        '''Stop playback and remove the update hook from the scene pre-draw list.'''
        self.on_finish = True
        logic.getCurrentScene().pre_draw.remove(self.update)

    def pause(self):
        '''Freeze the animation on the current frame without removing it from
        the update loop.
        '''
        self._pause = True
        self._running = False

    def restart(self):
        '''Reset the animation so that :meth:`update` restarts from the first
        frame on the next tick.
        '''
        self._initialized = False

    def unpause(self):
        '''Resume a paused animation from the frame it was frozen on.'''
        self._pause = False
        self._running = True

    def update(self):
        '''Advance the animation by the elapsed real-time since the last call,
        handle loop/ping-pong wrap-around, and stop the action when it reaches
        the end in ``"play"`` mode.

        Called automatically via the BGE scene pre-draw list.
        '''
        now = time.time()
        self.time += now - self._time_then
        self._time_then = now
        fps = self.fps
        rate = 1 / fps
        speed = self.time / rate
        if speed < 1:
            return
        self.time -= rate * speed
        if self._pause:
            return
        play_mode = self.mode
        running = self._running
        start_frame = self.end_frame if self._reverse else self.start_frame
        end_frame = self.start_frame if self._reverse else self.end_frame
        if not self._initialized:
            self.frame = start_frame
            self._initialized = True
        inverted = (start_frame > end_frame)
        frame = self.frame = self.frame
        reset_cond = (frame <= end_frame) if inverted else (frame >= end_frame)
        if not running:
            if reset_cond:
                self.frame = start_frame if inverted else end_frame
            self.on_start = True
            self._consumed = False

        start_cond = frame > start_frame if inverted else frame < start_frame

        if start_cond:
            self._running = True
            self.frame = start_frame
        frame = self.frame
        run_cond = (frame > end_frame) if inverted else (frame < end_frame)
        if run_cond:
            self._running = True
            s = round(speed)
            if inverted:
                if frame - s < end_frame:
                    if play_mode == 1:
                        leftover = abs(frame - s - end_frame)
                        span = start_frame - end_frame
                        while leftover > span:
                            leftover -= span
                        self.frame = start_frame - leftover
                    else:
                        self.frame = end_frame
                else:
                    self.frame -= s
            else:
                if frame + s > end_frame:
                    if play_mode == 1:
                        leftover = frame + s - end_frame
                        span = end_frame - start_frame
                        while leftover > span:
                            leftover -= span
                        self.frame = start_frame + leftover
                    else:
                        self.frame = end_frame
                else:
                    self.frame += s
        elif play_mode == 1:
            self.frame = end_frame if inverted else start_frame
        elif play_mode == 2:
            self._reverse = not self._reverse
        else:
            self.stop()


class ULSequence(Sequence):
    '''[DEPRECATED] Use :class:`Sequence` instead.'''
    _deprecated = True
