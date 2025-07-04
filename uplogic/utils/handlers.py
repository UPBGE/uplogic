from bge import logic
import bpy
import gpu
from math import floor
from uplogic.utils import clamp
from os.path import isfile





class ImageHandler:

    def __init__(self, texture, fps=60, min_frame=0, max_frame=None, load_audio=False):
        self.play_mode = 'play'
        self.sound = None
        self._texture = None
        self._image = None
        self._opacity = 1
        self.load_audio = load_audio
        if texture is not None and texture not in bpy.data.images and isfile(texture):
            self.image = bpy.data.images.load(texture)
        self.texture = texture
        self._frame = 1

        self._min_frame = min_frame
        self._max_frame = self.image.frame_duration
        if max_frame is not None:
            self._max_frame = max_frame
        self.fps = fps
        self._is_playing = False
        self._ref_time = 0
        self.time = 0
        self._flushed = False
        logic.getCurrentScene().pre_draw.append(self.update)

    @property
    def filepath(self):
        return self.image.filepath if self.image else ''

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, val):
        self._fps = val

    @property
    def playback_position(self):
        return self.frame / self.fps

    @playback_position.setter
    def playback_position(self, val):
        self.seek(val)

    @property
    def is_playing(self):
        return self._is_playing

    @is_playing.setter
    def is_playing(self, val):
        if not self.is_playing and val:
            self._ref_time = logic.getRealTime() - self.playback_position
            if self.sound is not None:
                self.sound.play()
                self.sound.position = self.playback_position
        elif not val and self.sound is not None:
            self.sound.pause()
        self._is_playing = val

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, val):
        if val is None:
            return
        texture = bpy.data.images.get(val, None)
        if not texture:
            texture = bpy.data.images.load(val)
        self.image = texture
        self._texture = gpu.texture.from_image(texture)
        self._max_frame = self.image.frame_duration
        if self.load_audio:
            if self.sound is not None:
                self.sound.stop()
            try:
                from uplogic.audio import Sound2D
                self.sound = Sound2D(self.filepath)
                self.sound.keep = True
            except Exception:
                self.sound = None
                print("Couldn't read audio from movie file.")

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, val):
        if val is None:
            return
        texture = bpy.data.images.get(val, None)
        if not texture:
            texture = bpy.data.images.load(val)
        self.image = texture
        self._texture = gpu.texture.from_image(texture)

    @property
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self, val):
        self._frame = clamp(val, self._min_frame, self._max_frame)
        self.flush()

    @property
    def max_frame(self):
        return self._max_frame

    def play(self):
        self.is_playing = True

    def seek(self, position):
        self._ref_time = logic.getRealTime() - position
        self.time = logic.getRealTime() - self._ref_time
        self.frame = floor(self.time * self._fps)
        if self.sound is not None:
            self.sound.position = self.playback_position
            if self.is_playing:
                self.sound.play()

    def flush(self):
        if not self._flushed:
            self.image.gl_free()
            # self.image.buffers_free()
            self.image.gl_load(frame=self.frame)

            self._texture = gpu.texture.from_image(self.image)
            self.image.update_tag()

    def update(self):
        if self.is_playing:
            self.time = logic.getRealTime() - self._ref_time
            self.frame = int(self.time * self._fps)
            if self.frame >= self.max_frame:
                self._finish()

    def _finish(self):
        if self.play_mode == 'loop':
            self.seek(0)
        else:
            self.is_playing = False
        self.on_finish()

    def on_finish(self):
        ...

    def free(self):
        self.image.gl_free()
        self.image.buffers_free()

    def stop(self):
        self.free()
        self.sound.stop()
        self.is_playing = False