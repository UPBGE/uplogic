from bge import logic
from uplogic.animation.action import PLAY_MODES
import bpy
import time
from bpy.types import ShaderNodeSpritesAnimation
from bpy.types import ShaderNodeTexImage
from bpy.types import Material


class ULSequence():
    '''[DEPRECATED] Use `uplogic.animation.Sequence` instead

    Play an image animation through a material node.

    :param `material`: Name of the material to play the animation on.
    Each Object with this material applied will play the animation.
    :param `node`: Name of the node the image animation is loaded on.
    :param `start_frame`: Starting frame of the animation.
    :param `end_frame`: End frame of the animation.
    :param `fps`: Frames per second.
    :param `mode`: Animation mode, `str` of [`play`, `loop`, `pingpong`]
    '''

    _deprecated = True

    @property
    def frame(self):
        if self._node_type:
            return self._player.frame_offset
        return round(self._player.inputs[0].default_value)

    @frame.setter
    def frame(self, frame):
        if self._node_type:
            self._player.frame_offset = round(frame)
        else:
            self._player.inputs[0].default_value = frame
        self.material.update_tag()

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
            print('Warning: ULSequence class will be renamed to "ULSequence" in future releases!')

        self.material = bpy.data.materials[material]
        """The material this sequence is played on."""
        self.node = node
        """Name of the node the image animation is loaded on."""
        self.start_frame = start_frame
        """Starting frame of the animation."""
        self.end_frame = end_frame - .01  # .01 because the sprite node shows the next frame when numer is round
        """End frame of the animation."""
        self.fps = fps
        """Frames per second."""
        self.mode = mode
        """Animation mode, `str` of [`play`, `loop`, `pingpong`]"""
        self.time = 0.0
        """Animation progress."""
        # self.frame = 0
        """Current frame of the animation."""
        self.on_start = False
        """`True` when animation started."""
        self.on_finish = False
        """`True` when animation finished this frame."""
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
        self._player = node


        if isinstance(node, ShaderNodeSpritesAnimation):
            self._node_type = 0
        elif isinstance(node, ShaderNodeTexImage):
            self._node_type = 1
        else:
            return
        self.frame = start_frame
        logic.getCurrentScene().pre_draw.append(self.update)

    def stop(self):
        '''Stop this animation completely.'''
        self.on_finish = True
        logic.getCurrentScene().pre_draw.remove(self.update)

    def pause(self):
        '''Pause this animation.'''
        self._pause = True
        self._running = False

    def restart(self):
        '''Restart this animation.'''
        self._initialized = False

    def unpause(self):
        '''Continue this animation.'''
        self._pause = False
        self._running = True

    def update(self):
        '''This is called each frame.'''
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
                        print('Restart')
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


class Sequence(ULSequence):
    '''Play an image animation through a material node.

    :param `material`: Name of the material to play the animation on.
    Each Object with this material applied will play the animation.
    :param `node`: Name of the node the image animation is loaded on.
    :param `start_frame`: Starting frame of the animation.
    :param `end_frame`: End frame of the animation.
    :param `fps`: Frames per second.
    :param `mode`: Animation mode, `str` of [`play`, `loop`, `pingpong`]
    '''
    _deprecated = False
