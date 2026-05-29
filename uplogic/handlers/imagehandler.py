'''GPU image-sequence / movie-file playback handler for uplogic.

:class:`ImageHandler` wraps a ``bpy.data.images`` entry and drives it
frame-by-frame using real-time elapsed time so that it can be used as a
live GPU texture regardless of the BGE render loop speed.
'''

from bge import logic
import bpy
import gpu
import numpy as np
from math import floor
from os.path import isfile
from uplogic import console


class ImageHandler:
    '''Frame-accurate playback controller for a GPU image sequence or movie.

    Loads the source file into ``bpy.data.images``, exposes the current frame
    as a ``gpu.types.GPUTexture`` via :attr:`texture`, and advances the
    playhead in real time through a ``pre_draw`` callback.  Optionally
    extracts and synchronises an embedded audio track via
    :class:`~uplogic.audio.Sound2D`.

    :param texture: Path to the image or movie file, or ``None`` to create a
        placeholder handler.
    :param fps: Target playback speed in frames per second.
    :param min_frame: First frame of the playback range (currently unused in
        the constructor but stored for later use).
    :param max_frame: Last frame; defaults to the image's own
        ``frame_duration``.
    :param load_audio: When ``True``, attempt to extract an audio track from
        the movie file and keep it in sync during playback.
    '''

    def __init__(self, texture, fps=60, min_frame=0, max_frame=None, load_audio=False):
        self.play_mode = 'play'
        self.sound = None
        self._texture = None
        self._image = None
        self.image = None
        self._opacity = 1
        self.load_audio = load_audio
        min_frame=0
        self.fps = fps
        self._is_playing = False
        self._ref_time = 0
        self.time = 0
        self._flushed = False
        self._frame = 1
        if texture is None:
            max_frame=1000
            return
        # print(self.image)
        if isinstance(texture, bpy.types.Image):
            self.image = texture
            self.texture = texture.name
        elif texture is not None and texture not in bpy.data.images and isfile(texture):
            self.image = bpy.data.images.load(texture)
            self.texture = texture

        self.min_frame = min_frame
        self.max_frame = self.image.frame_duration
        if max_frame is not None:
            self.max_frame = max_frame
        logic.getCurrentScene().pre_draw.append(self.update)

    @property
    def filepath(self):
        '''Absolute filesystem path of the loaded image, or an empty string
        when no image is loaded (read-only).
        '''
        return self.image.filepath if self.image else ''

    @property
    def fps(self):
        '''Playback speed in frames per second. Used together with elapsed
        real time to advance :attr:`frame` each tick.
        '''
        return self._fps

    @fps.setter
    def fps(self, val):
        self._fps = val

    @property
    def playback_position(self):
        '''Current playhead position in seconds (``frame / fps``). Setting
        this is equivalent to calling :meth:`seek`.
        '''
        return self.frame / self.fps

    @playback_position.setter
    def playback_position(self, val):
        self.seek(val)

    @property
    def is_playing(self):
        '''``True`` while the handler is actively advancing frames. Setting
        to ``True`` resumes from the current position (including audio); setting
        to ``False`` pauses audio and stops frame advancement.
        '''
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
        '''The current ``gpu.types.GPUTexture`` for the active frame, or
        ``None`` when no image is loaded. Setting this loads the file from
        *val* (looked up in ``bpy.data.images`` or loaded from disk), refreshes
        :attr:`max_frame`, and optionally initialises the audio track when
        :attr:`load_audio` is ``True``.
        '''
        return self._texture

    def _premultiply_image(self, image):
        if image is None or image.alpha_mode == 'PREMUL':
            return
        count = len(image.pixels)
        px = np.empty(count, dtype=np.float32)
        image.pixels.foreach_get(px)
        px = px.reshape(-1, 4)
        px[:, :3] *= px[:, 3:4]
        image.pixels.foreach_set(px.ravel())
        image.alpha_mode = 'PREMUL'

    @texture.setter
    def texture(self, val):
        if val is None:
            self._texture = None
            return
        if isinstance(val, bpy.types.Image):
            val = val.name
        texture = bpy.data.images.get(val, None)
        if not texture:
            texture = bpy.data.images.load(val, check_existing=True)
        self.image = texture
        self._premultiply_image(texture)
        self._texture = gpu.texture.from_image(texture)
        # self._texture.extend_mode = 'EXTEND'
        self.max_frame = self.image.frame_duration
        if self.load_audio:
            if self.sound is not None:
                self.sound.stop()
            try:
                from uplogic.audio import Sound2D
                self.sound = Sound2D(self.filepath)
                self.sound.keep = True
            except Exception:
                self.sound = None
                console.warning("Couldn't read audio from movie file.")

    @property
    def frame(self):
        '''Current frame index, clamped to ``[min_frame, max_frame]``. Setting
        this clamps the value and calls :meth:`flush` to upload the new frame
        to the GPU texture.
        '''
        return self._frame

    @frame.setter
    def frame(self, val):
        self._frame = max(self.min_frame, min(val, self.max_frame))
        self.flush()

    def play(self):
        '''Start or resume playback from the current :attr:`frame`.'''
        self.is_playing = True

    def seek(self, position):
        '''Jump to *position* seconds from the start of the sequence.

        Resets the internal reference time so that :meth:`update` computes
        the correct frame on the next tick.  Also repositions the audio track
        and resumes audio playback if the handler is currently playing.

        :param position: Target position in seconds.
        '''
        self._ref_time = logic.getRealTime() - position
        self.time = logic.getRealTime() - self._ref_time
        self.frame = floor(self.time * self._fps)
        if self.sound is not None:
            self.sound.position = self.playback_position
            if self.is_playing:
                self.sound.play()

    def flush(self):
        '''Upload the current :attr:`frame` to the GPU texture.

        Frees the previous OpenGL buffer, loads the new frame via
        ``gl_load``, and rebuilds the ``gpu.types.GPUTexture``.  The flush is
        skipped when :attr:`_flushed` is ``True``.
        '''
        if not self._flushed:
            self.image.gl_free()
            self.image.gl_load(frame=self.frame)
            self._texture = gpu.texture.from_image(self.image)
            self.image.update_tag()

    def update(self):
        '''Per-frame callback: advance the playhead based on elapsed real time
        and trigger :meth:`_finish` when the end frame is reached.

        Registered automatically in the BGE scene pre-draw list on construction.
        '''
        if self.is_playing:
            self.time = logic.getRealTime() - self._ref_time
            self.frame = int(self.time * self._fps)
            if self.frame >= self.max_frame:
                self._finish()

    def _finish(self):
        '''Called internally when playback reaches :attr:`max_frame`.

        Loops back to frame 0 when :attr:`play_mode` is ``"loop"``, otherwise
        stops playback.  Always calls :meth:`on_finish`.
        '''
        if self.play_mode == 'loop':
            self.seek(0)
        else:
            self.is_playing = False
        self.on_finish()

    def on_finish(self):
        '''Called once when the sequence reaches its last frame.

        Override this method to react to playback ending.
        '''
        ...

    def free(self):
        '''Release the OpenGL buffer and any CPU-side pixel buffers held by
        the loaded image.  Call before discarding the handler to avoid GPU
        memory leaks.
        '''
        self.image.gl_free()
        self.image.buffers_free()

    def stop(self):
        '''Stop playback, free GPU/CPU image buffers, and stop the audio track.'''
        self.free()
        if self.sound is not None:
            self.sound.stop()
        self.is_playing = False