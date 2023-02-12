from bge import logic
from uplogic.animation.action import PLAY_MODES
import bpy
import time


class ULSequence():
    '''[DEPRECATED]

    Play an image animation through a material node.

    :param `material`: Name of the material to play the animation on.
    Each Object with this material applied will play the animation.
    :param `node`: Name of the node the image animation is loaded on.
    :param `start_frame`: Starting frame of the animation.
    :param `end_frame`: End frame of the animation.
    :param `fps`: Frames per second.
    :param `mode`: Animation mode, `str` of [`play`, `loop`, `pingpong`]
    '''

    def __init__(
        self,
        material: str,
        node: str,
        start_frame: int,
        end_frame: int,
        fps: int = 60,
        mode: str = 'play'
    ) -> None:
        self.material = material
        """The material this sequence is played on."""
        self.node = node
        """Name of the node the image animation is loaded on."""
        self.start_frame = start_frame
        """Starting frame of the animation."""
        self.end_frame = end_frame
        """End frame of the animation."""
        self.fps = fps
        """Frames per second."""
        self.mode = PLAY_MODES.get(mode, 0)
        """Animation mode, `str` of [`play`, `loop`, `pingpong`]"""
        self.time = 0.0
        """Animation progress."""
        self.frame = 0
        """Current frame of the animation."""
        self.on_start = False
        """`True` when animation started."""
        self.on_finish = False
        """`True` when animation finished this frame."""
        self._initialized = False
        self._reverse = False
        self._running = True
        self._consumed = False
        self._pause = False
        self._time_then = time.time()
        self._player = (
            bpy.data.materials[material]
            .node_tree
            .nodes[node]
        ).image_user

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
        player = self._player
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
            player.frame_offset = round(start_frame)
            self._initialized = True
        inverted = (start_frame > end_frame)
        frame = self.frame = player.frame_offset
        reset_cond = (frame <= end_frame) if inverted else (frame >= end_frame)
        if not running:
            if reset_cond:
                player.frame_offset = round(start_frame) if inverted else round(end_frame)
            self.on_start = True
            self._consumed = False

        start_cond = frame > start_frame if inverted else frame < start_frame

        if start_cond:
            self._running = True
            player.frame_offset = round(start_frame)
        frame = player.frame_offset
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
                        player.frame_offset = round(start_frame - leftover)
                    else:
                        player.frame_offset = round(end_frame)
                else:
                    player.frame_offset -= round(s)
            else:
                if frame + s > end_frame:
                    if play_mode == 1:
                        leftover = frame + s - end_frame
                        span = end_frame - start_frame
                        while leftover > span:
                            leftover -= span
                        player.frame_offset = round(start_frame + leftover)
                    else:
                        player.frame_offset = round(end_frame)
                else:
                    player.frame_offset += round(s)
        elif play_mode == 1:
            player.frame_offset = round(end_frame) if inverted else round(start_frame)
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
    pass
