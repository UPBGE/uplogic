'''Sound playback classes for uplogic.

Provides :class:`Sound2D` / :class:`Sound3D` for non-spatial and positional
audio respectively, :class:`Sample2D` / :class:`Sample3D` for time-limited
clips, and :class:`Speaker2D` / :class:`Speaker3D` convenience wrappers that
read their parameters directly from a BGE speaker object. All classes
integrate with the uplogic :class:`~uplogic.audio.audiosystem.AudioSystem`
for master volume, lowpass, and per-frame updates.
'''

from os.path import isfile
from bge import logic
from bge.types import KX_GameObject as GameObject
from mathutils import Vector
from uplogic.audio import AudioSystem
from uplogic.audio.audiosystem import AudioCache
from uplogic.audio import get_audio_system
from uplogic.events import schedule_callback
from uplogic.utils.math import interpolate
from uplogic import console
from uplogic.utils import DELTA_TIME
import bpy
import aud


class ULReverb():
    """Simulated reverb for a :class:`Sound3D` by playing up to 30 delayed
    copies of the source sound behind the listener.

    Created automatically by :class:`Sound3D` when ``reverb=True``. The
    volume of each sample fades in when the listener enters a reverb volume
    tagged in the scene, and fades out otherwise.
    """

    volume: float

    def __init__(
        self,
        parent,
        sound,
        handle
    ):
        self.volume = 0
        self.parent = parent
        self.handle = handle
        self.aud_system = parent.aud_system
        self.samples = []
        schedule_callback(self.add_sample, 1/60, sound)

    def add_sample(self, sound):
        '''Play one more delayed reverb copy of *sound* and mirror the source
        handle's spatial attributes onto it.

        Schedules itself recursively until 30 samples have been created.

        :param sound: ``aud.Sound`` to play as a reverb sample.
        '''
        handle = self.handle
        sample = self.aud_system.device.play(sound)
        self.samples.append(sample)
        sample.loop_count = handle.loop_count
        sample.position = handle.position - (.0001 * len(self.samples))
        sample.relative = handle.relative
        sample.location = handle.location
        sample.velocity = handle.velocity
        sample.attenuation = handle.attenuation
        ori = self.parent.speaker.worldOrientation.to_quaternion()
        ori.negate()
        sample.orientation = ori
        sample.pitch = handle.pitch
        sample.volume = 0
        sample.distance_reference = handle.distance_reference
        sample.distance_maximum = handle.distance_maximum
        sample.cone_angle_inner = handle.cone_angle_inner
        sample.cone_angle_outer = handle.cone_angle_outer
        sample.cone_volume_outer = handle.cone_volume_outer
        if len(self.samples) < 30:
            schedule_callback(self.add_sample, 1/60, sound)

    def update(self):
        '''Per-frame update: adjust each reverb sample's volume and spatial
        attributes based on the current reverb state and occlusion of the
        parent :class:`Sound3D`.
        '''
        sample_count = self.aud_system.bounces
        use_reverb = (
            self.aud_system.reverb
        )
        handle = self.handle
        if not use_reverb or sample_count == 0:
            if self.volume < .001:
                return
            else:
                self.volume = interpolate(self.volume, 0, .1)
        else:
            parent = self.parent
            target_vol = (
                parent.volume / 10 if
                parent.occluded else
                parent.volume / 2
            )
            self.volume = interpolate(self.volume, target_vol, .1)
        for idx, sample in enumerate(self.samples):
            if not sample.status:
                sample.stop()
                continue
            if idx > sample_count:
                sample.volume = 0
                continue
            mult = idx/sample_count
            loc = handle.location
            lloc = self.aud_system.device.listener_location
            loc = (loc[0]-lloc[0], loc[1]-lloc[1], loc[2]-lloc[2])
            sample.location = (
                -(loc[0]-lloc[0]),
                -(loc[1]-lloc[1]),
                -(loc[2]-lloc[2])
            )
            sample.velocity = handle.velocity
            sample.attenuation = handle.attenuation
            ori = self.parent.speaker.worldOrientation.to_quaternion()
            ori.negate()
            sample.orientation = ori
            sample.distance_maximum = handle.distance_maximum
            sample.cone_angle_inner = handle.cone_angle_inner
            sample.pitch = handle.pitch
            sample.volume = (1-(handle.volume * (mult**2)))*.5 * self.volume * self.aud_system.volume
            sample.cone_volume_outer = handle.cone_volume_outer


def dummy():
    pass


class ULSound():
    """Base class for 2D and 3D sounds.

    Subclasses must set up ``self.sound`` (an ``aud`` handle) and register
    themselves with an :class:`~uplogic.audio.audiosystem.AudioSystem`.
    """

    sound = None
    """Internal ``aud`` playback handle."""
    finished: bool
    """``True`` once the sound has played to its end or been stopped."""
    pitch: float
    """Playback frequency shift (``1.0`` = normal speed)."""
    volume: float
    """Playback amplitude (``1.0`` = unity gain)."""
    aud_system: AudioSystem
    """The :class:`~uplogic.audio.audiosystem.AudioSystem` this sound plays on."""

    @property
    def position(self):
        '''Progression of the soundfile in seconds.'''
        if self.sound:
            return self.sound.position

    @position.setter
    def position(self, val):
        if self.sound:
            self.sound.position = val

    def play(self):
        '''Start playback of this sound.'''
        self.sound.resume()

    def stop(self):
        '''Stop and remove this sound.'''
        self.on_finish = dummy
        self.sound.stop()

    def pause(self):
        '''Stop playback of this sound but keep it.'''
        self.sound.pause()

    def resume(self):
        '''Restart playback of this sound from the position it was paused at.'''
        self.sound.resume()

    def cache(self):
        '''Store this sound's decoded data in the global
        :class:`~uplogic.audio.audiosystem.AudioCache`.
        '''
        self.aud_system.cache(self)

    def uncache(self):
        '''Remove this sound from the global
        :class:`~uplogic.audio.audiosystem.AudioCache`.
        '''
        self.aud_system.uncache(self)

    def _get_soundpath(self, file):
        '''Resolve *file* to an absolute file-system path.

        Accepts a plain path string, a Blender data-block name, or a
        ``//``-relative path. Logs an error and returns ``None`` if the
        resolved file does not exist.

        :param file: Sound file path or Blender data-block name.
        :returns: Absolute path string, or ``None`` on failure.
        '''
        soundpath = file
        if not isinstance(soundpath, bpy.types.Sound):
            soundpath = bpy.data.sounds.get(file, None)
        if soundpath:
            soundpath = soundpath.filepath
        else:
            soundpath = logic.expandPath(file)
        if not isfile(soundpath):
            console.error(f'Soundfile {soundpath} could not be loaded!')
            return None
        return soundpath

    @property
    def keep(self):
        '''When ``True`` the ``aud`` handle is kept alive after playback ends,
        allowing the sound to be resumed.
        '''
        return self.sound.keep

    @keep.setter
    def keep(self, val):
        self.sound.keep = val

    def on_finish(self):
        '''Callback invoked when the sound finishes playback or is stopped.

        Override this method to react to the sound ending. The default
        implementation is a no-op.
        '''
        pass


class Sound2D(ULSound):
    '''Non-spatial sound, e.g. music or voice-overs.

    Pitch and volume can be modified at any time during playback.

    :param file: Path to the sound file.
    :param volume: Initial amplitude (``1.0`` = unity).
    :param pitch: Initial frequency shift (``1.0`` = normal speed).
    :param loop_count: Extra repeats after the first play; ``-1`` loops forever.
    :param lowpass: Lowpass cutoff frequency, or ``False`` to disable.
    :param ignore_timescale: When ``True``, pitch is unaffected by the game
        time scale.
    :param mono: Down-mix to mono before playback.
    :param aud_sys: Name of the :class:`~uplogic.audio.audiosystem.AudioSystem`
        to play on.
    '''

    _deprecated = False

    def __init__(
        self,
        file: str = '',
        volume: float = 1,
        pitch: float = 1,
        loop_count: int = 0,
        lowpass = False,
        ignore_timescale = True,
        mono: bool = False,
        aud_sys: str = 'default'
    ):
        if self._deprecated:
            console.warning('Warning: ULSound2D class will be renamed to "Sound2D" in future releases!')
        self.file = file
        self._volume = 1
        self.finished = False
        if not (file):
            return
        self.aud_system = get_audio_system(aud_sys)
        self.ignore_timescale = ignore_timescale
        soundpath = self._get_soundpath(file)
        if soundpath is None:
            return
        sound = self.soundfile = AudioCache.get(self.file, aud.Sound(soundpath))
        lowpass = self.aud_system.lowpass or lowpass
        if lowpass:
            sound = self.soundfile = sound.lowpass(lowpass, .5)
        if mono:
            sound = sound.rechannel(1)
        device = self.aud_system.device
        self.sound = handle = device.play(sound)
        self.sound.pause()
        handle.volume = 0
        handle.relative = True
        handle.loop_count = loop_count
        self.aud_system.add(self)
        self.volume = volume
        self.pitch = pitch
        self._lowpass = False
        self.lowpass = self.aud_system.lowpass

    @property
    def panning(self):
        '''Pan position of this sound, from ``-1`` (left) to ``1`` (right).

        Only effective on mono sounds.
        '''
        return self.sound.location[0]

    @panning.setter
    def panning(self, val):
        panning = list(self.sound.location)
        panning[0] = val
        self.sound.location = panning

    @property
    def volume(self):
        '''Playback amplitude.'''
        return self._volume

    @volume.setter
    def volume(self, val):
        if self.sound and self.sound.status:
            self.sound.volume = val * self.aud_system.volume
        self._volume = val

    @property
    def pitch(self):
        '''Playback frequency shift.'''
        ts = 1 if self.ignore_timescale else logic.getTimeScale()
        if self.sound and self.sound.status:
            return self.sound.pitch / ts

    @pitch.setter
    def pitch(self, val):
        ts = 1 if self.ignore_timescale else logic.getTimeScale()
        if self.sound and self.sound.status:
            self.sound.pitch = val * ts

    @property
    def lowpass(self):
        '''Lowpass filter cutoff as a factor of 20 000 Hz. ``False`` disables
        the filter.
        '''
        return self._lowpass

    @lowpass.setter
    def lowpass(self, val):
        if abs(self._lowpass - val) < 10:
            return
        self._lowpass = val
        sound = self.soundfile
        if val:
            sound = sound.lowpass(val, .5)
        sound = self.aud_system.device.play(sound)
        sound.loop_count = self.sound.loop_count
        sound.position = self.sound.position + DELTA_TIME()
        sound.volume = self.sound.volume
        sound.pitch = self.sound.pitch
        schedule_callback(self.sound.stop)
        self.sound = sound

    def update(self):
        '''Per-frame update: detect when the underlying handle has finished
        and fire :meth:`on_finish`, then remove from the audio system.
        '''
        if self.volume == 0:
            return
        handle = self.sound
        if not handle.status:
            self.finished = True
            self.on_finish()
            self.aud_system.remove(self)
            return


class ULSound2D(Sound2D):
    '''[DEPRECATED] Use :class:`Sound2D` instead.'''

    _deprecated = True


class Sample2D(Sound2D):
    '''Non-spatial sound with an optional time-range clip window.

    Pitch and volume can be modified at any time during playback.

    :param file: Path to the sound file.
    :param sample: ``(start, end)`` timestamps in seconds; ``end=0`` plays
        the whole file.
    :param volume: Initial amplitude (``1.0`` = unity).
    :param pitch: Initial frequency shift (``1.0`` = normal speed).
    :param loop_count: Extra repeats after the first play; ``-1`` loops forever.
    :param lowpass: Lowpass cutoff frequency, or ``False`` to disable.
    :param ignore_timescale: When ``True``, pitch is unaffected by the game
        time scale.
    :param mono: Down-mix to mono before playback.
    :param aud_sys: Name of the :class:`~uplogic.audio.audiosystem.AudioSystem`
        to play on.
    '''

    _deprecated = False

    def __init__(
        self,
        file: str = '',
        sample: tuple = (0, 0),
        volume: float = 1,
        pitch: float = 1,
        loop_count: int = 0,
        lowpass = False,
        ignore_timescale = False,
        mono=False,
        aud_sys: str = 'default'
    ):
        self.file = file
        self.soundfile = None
        self._volume = 1
        self.finished = False
        if not (file):
            return
        self.aud_system = get_audio_system(aud_sys)
        self.ignore_timescale = ignore_timescale
        soundpath = file
        if not isinstance(soundpath, bpy.types.Sound):
            soundpath = bpy.data.sounds.get(file, None)
        if soundpath:
            soundpath = soundpath.filepath
        else:
            soundpath = logic.expandPath(file)
        soundpath = self._get_soundpath(file)
        if soundpath is None:
            return
        sound = self.soundfile = AudioCache.get(self.file, aud.Sound(soundpath))
        if sample[1]:
            sound = sound.limit(sample[0], sample[1])
        if mono:
            sound = sound.rechannel(1)
        lowpass = self.aud_system.lowpass or lowpass
        if lowpass:
            sound = self.soundfile = sound.lowpass(lowpass, .5)
        device = self.aud_system.device
        self.sound = handle = device.play(sound)
        handle.volume = 0

        handle.relative = True
        handle.loop_count = loop_count
        self.aud_system.add(self)
        self.volume = volume
        self.pitch = pitch
        self._lowpass = False
        self.lowpass = self.aud_system.lowpass


class Sound3D(ULSound):
    '''Spatial sound, e.g. world effects or voices.

    Position, orientation, and velocity are tracked automatically when a
    ``KX_GameObject`` is used as the speaker. Optionally supports occlusion
    ray-casting and reverb volumes.

    :param speaker: ``KX_GameObject`` that acts as the source, or a fixed
        ``Vector`` world position.
    :param file: Path to the sound file.
    :param occlusion: When ``True``, cast rays to muffle sounds behind walls.
    :param transition_speed: Interpolation speed between clear and muffled.
    :param cutoff_frequency: Lowpass cutoff for the muffled version as a
        factor of 20 000 Hz.
    :param loop_count: Extra repeats after the first play; ``-1`` loops forever.
    :param pitch: Initial frequency shift (``1.0`` = normal speed).
    :param volume: Initial amplitude (``1.0`` = unity).
    :param reverb: When ``True``, simulate reverb via
        :class:`ULReverb` (performance-intensive).
    :param attenuation: Distance fade factor for the ``aud`` device.
    :param distance_ref: Distance at which the sound plays at full volume.
    :param cone_angle: ``[inner, outer]`` cone angles in degrees; aligned to
        the speaker's ``-Z`` axis.
    :param cone_outer_volume: Volume multiplier outside the outer cone.
    :param ignore_timescale: When ``True``, pitch is unaffected by the game
        time scale.
    :param aud_sys: Name of the :class:`~uplogic.audio.audiosystem.AudioSystem`
        to play on.
    '''

    _deprecated = False

    @property
    def position(self):
        '''Playback position of this sound in seconds.'''
        if self.handles:
            return self.handles[1][0].position

    @position.setter
    def position(self, val):
        for sound in self.handles[1]:
            sound.position = val

    def __init__(
        self,
        speaker: GameObject or Vector = None,
        file: str = '',
        occlusion: bool = False,
        transition_speed: float = .1,
        cutoff_frequency: float = .1,
        loop_count: int = 0,
        pitch: float = 1,
        volume: float = 1,
        reverb=False,
        attenuation: float = 1,
        distance_ref: float = 1,
        cone_angle: list[float] = [360, 360],
        cone_outer_volume: float = 0,
        ignore_timescale: bool = False,
        aud_sys: str = 'default'
    ):
        if self._deprecated:
            console.warning(f'"{self.__class__.__name__}" class will be renamed to "Sound3D" in future releases!')
        self._is_vector = isinstance(speaker, Vector)
        self.file = file
        self.soundfile = None
        self.finished = False
        if not (file and speaker):
            return
        self._clear_sound = 0 if occlusion else 1
        self._sustained = 1
        self.occluded = False
        self.sounds = []
        self.reverb_samples = None
        self.aud_system = get_audio_system(aud_sys)
        self.speaker = speaker
        self.reverb = reverb
        self.occlusion = occlusion
        self.volume = volume
        self.pitch = pitch
        self.cone_outer_volume = cone_outer_volume
        master_volume = self.aud_system.volume
        self.transition = transition_speed
        self.ignore_timescale = ignore_timescale
        soundpath = self._get_soundpath(file)
        if soundpath is None:
            return
        sound = self.soundfile = AudioCache.get(self.file, aud.Sound(soundpath).rechannel(1))
        device = self.aud_system.device
        handle = self.sound = device.play(sound)
        handle.volume = 0
        if occlusion:
            soundlow = aud.Sound.lowpass(sound, 4400 * cutoff_frequency, .5).rechannel(1)
            handlelow = device.play(soundlow)
            handlelow.volume = 0
            self.handles = [speaker, [handle, handlelow]]
        else:
            self.handles = [speaker, [handle]]
        for handle in self.handles[1]:
            handle.relative = False
            handle.location = speaker if self._is_vector else speaker.worldPosition
            if not self._is_vector and speaker.mass:
                handle.velocity = getattr(
                    speaker,
                    'worldLinearVelocity',
                    Vector((0, 0, 0))
                ) if speaker.blenderObject.game.physics_type != 'NO_COLLISION' else Vector((0, 0, 0))
            handle.attenuation = attenuation
            if not self._is_vector:
                handle.orientation = speaker.worldOrientation.to_quaternion()
            handle.pitch = pitch
            handle.volume = volume * master_volume
            handle.distance_reference = distance_ref
            handle.distance_maximum = 1000
            handle.cone_angle_inner = cone_angle[0]
            handle.cone_angle_outer = cone_angle[1]
            handle.loop_count = loop_count
            handle.cone_volume_outer = cone_outer_volume * volume * master_volume
        if self.reverb:
            self.reverb_samples = ULReverb(
                self,
                sound,
                self.handles[1][0]
            )
        self.aud_system.add(self)
        self.update(True)

    def play(self):
        '''Start playback of this sound.'''
        for sound in self.sounds:
            sound.resume()

    def stop(self):
        '''Stop and remove this sound.'''
        self.on_finish = dummy
        for sound in self.sounds:
            sound.stop()

    def pause(self):
        '''Stop playback of this sound but keep it.'''
        for sound in self.sounds:
            sound.pause()

    def resume(self):
        '''Restart playback of this sound from the position it was paused at.'''
        for sound in self.sounds:
            sound.resume()

    def update(self, init=False):
        '''Per-frame update: sync the sound's spatial attributes (location,
        orientation, velocity) to the speaker object and handle occlusion
        ray-casting when enabled.

        :param init: When ``True`` occlusion transitions are applied
            instantaneously rather than interpolated.
        '''
        aud_system = self.aud_system
        speaker = self.speaker
        if not self._is_vector and (not speaker or speaker.invalid):
            self.finished = True
            self.on_finish()
            aud_system.remove(self)
            return
        location = speaker if self._is_vector else speaker.worldPosition
        for i, handle in enumerate(self.handles[1]):
            if not handle.status:
                self.finished = True
                self.on_finish()
                aud_system.remove(self)
                return
            handle.pitch = self.pitch * (1 if self.ignore_timescale else logic.getTimeScale())
            handle.location = location
            if not self._is_vector:
                handle.orientation = (
                    speaker
                    .worldOrientation
                    .to_quaternion()
                )
                if 'volume' in dir(self.speaker.blenderObject.data):
                    handle.velocity = Vector((0, 0, 0))
                elif speaker.mass:
                    handle.velocity = getattr(speaker, 'worldLinearVelocity', Vector((0, 0, 0)))
            if self.occlusion and handle.status:
                transition = 1 if init else self.transition
                cam = self.aud_system.listener
                occluder, point, normal = cam.rayCast(
                    location,
                    cam.worldPosition,
                    xray=False
                )
                occluded = self.occluded = False
                penetration = 1
                occ_count = 0
                while occluder and occ_count < 5:
                    if occluder is speaker:
                        break
                    sound_occluder = occluder.blenderObject.get(
                        'sound_occluder',
                        True
                    )
                    if sound_occluder:
                        occluded = self.occluded = True
                        block = occluder.blenderObject.get(
                            'sound_blocking',
                            .1
                        )
                        if penetration > 0:
                            penetration -= block
                        else:
                            penetration = 0
                    occluder, point, normal = occluder.rayCast(
                        location,
                        point,
                        xray=False
                    )
                    occ_count += 1
                cs = self._clear_sound
                if occluded and cs > 0:
                    self._clear_sound -= transition
                elif not occluded and cs < 1:
                    self._clear_sound += transition
                if self._clear_sound < 0:
                    self._clear_sound = 0
                sustained = self._sustained
                if sustained > penetration:
                    self._sustained -= transition / 10
                elif sustained < penetration:
                    self._sustained += transition / 10
                mult = (
                    cs * sustained
                    if not i
                    else (1 - cs) * sustained
                )
                master_volume = self.aud_system.volume
                try:
                    handle.volume = self.volume * mult * master_volume
                
                    handle.cone_volume_outer = (
                        self.cone_outer_volume *
                        self.volume *
                        mult *
                        master_volume
                    )
                except Exception:
                    pass
            elif handle.status:
                master_volume = self.aud_system.volume
                handle.volume = self.volume * master_volume
                handle.cone_volume_outer = (
                    self.cone_outer_volume *
                    self.volume *
                    master_volume
                )

        if self.reverb_samples:
            self.reverb_samples.update()

    def pause(self):
        '''Pause all handles of this sound, suppressing the finish callback.'''
        self.on_finish = dummy
        for sound in self.handles[1]:
            sound.pause()

    def resume(self):
        '''Resume all handles of this sound, suppressing the finish callback.'''
        self.on_finish = dummy
        for sound in self.handles[1]:
            sound.resume()

    def stop(self):
        '''Stop all handles of this sound, suppressing the finish callback.'''
        self.on_finish = dummy
        for sound in self.handles[1]:
            sound.stop()


class ULSound3D(Sound3D):
    '''[DEPRECATED] Use :class:`Sound3D` instead.'''
    _deprecated = True


class Sample3D(Sound3D):
    '''Spatial sound with an optional time-range clip window.

    Behaves like :class:`Sound3D` but trims playback to a ``(start, end)``
    range within the source file.

    :param speaker: ``KX_GameObject`` or fixed ``Vector`` world position.
    :param file: Path to the sound file.
    :param sample: ``(start, end)`` timestamps in seconds; ``end=0`` plays
        the whole file.
    :param occlusion: When ``True``, cast rays to muffle sounds behind walls.
    :param transition_speed: Interpolation speed between clear and muffled.
    :param cutoff_frequency: Lowpass cutoff for the muffled version as a
        factor of 20 000 Hz.
    :param loop_count: Extra repeats after the first play; ``-1`` loops forever.
    :param pitch: Initial frequency shift (``1.0`` = normal speed).
    :param volume: Initial amplitude (``1.0`` = unity).
    :param reverb: When ``True``, simulate reverb via :class:`ULReverb`.
    :param attenuation: Distance fade factor for the ``aud`` device.
    :param distance_ref: Distance at which the sound plays at full volume.
    :param cone_angle: ``[inner, outer]`` cone angles in degrees.
    :param cone_outer_volume: Volume multiplier outside the outer cone.
    :param ignore_timescale: When ``True``, pitch is unaffected by the game
        time scale.
    :param aud_sys: Name of the :class:`~uplogic.audio.audiosystem.AudioSystem`
        to play on.
    '''

    _deprecated = False

    def __init__(
        self,
        speaker: GameObject or Vector = None,
        file: str = '',
        sample: tuple = (0, 0),
        occlusion: bool = False,
        transition_speed: float = .1,
        cutoff_frequency: float = .1,
        loop_count: int = 0,
        pitch: float = 1,
        volume: float = 1,
        reverb=False,
        attenuation: float = 1,
        distance_ref: float = 1,
        cone_angle: list[float] = [360, 360],
        cone_outer_volume: float = 0,
        ignore_timescale: bool = False,
        aud_sys: str = 'default'
    ):
        self._is_vector = isinstance(speaker, Vector)
        self.file = file
        self.soundfile = None
        self.finished = False
        if not (file and speaker):
            return
        self._clear_sound = 1
        self._sustained = 1
        self.occluded = False
        self.sounds = []
        self.reverb_samples = None
        self.aud_system = get_audio_system(aud_sys)
        self.speaker = speaker
        self.reverb = reverb
        self.occlusion = occlusion
        self.volume = volume
        self.pitch = pitch
        self.cone_outer_volume = cone_outer_volume
        master_volume = self.aud_system.volume
        self.transition = transition_speed
        self.ignore_timescale = ignore_timescale
        soundpath = self._get_soundpath(file)
        if soundpath is None:
            return
        sound = self.soundfile = AudioCache.get(self.file, aud.Sound(soundpath).rechannel(1))
        device = self.aud_system.device
        if sample[1]:
            sound = sound.limit(sample[0], sample[1])
        handle = device.play(sound)
        handle.volume = 0
        if occlusion:
            soundlow = aud.Sound.lowpass(sound, 4400 * cutoff_frequency, .5).rechannel(1)
            handlelow = device.play(soundlow)
            handlelow.volume = 0
            self.handles = [speaker, [handle, handlelow]]
        else:
            self.handles = [speaker, [handle]]
        for handle in self.handles[1]:
            handle.relative = False
            handle.location = speaker if self._is_vector else speaker.worldPosition
            if not self._is_vector and speaker.mass:
                handle.velocity = getattr(
                    speaker,
                    'worldLinearVelocity',
                    Vector((0, 0, 0))
                ) if speaker.blenderObject.game.physics_type != 'NO_COLLISION' else Vector((0, 0, 0))
            handle.attenuation = attenuation
            if not self._is_vector:
                handle.orientation = speaker.worldOrientation.to_quaternion()
            handle.pitch = pitch
            handle.volume = volume * master_volume
            handle.distance_reference = distance_ref
            handle.distance_maximum = 1000
            handle.cone_angle_inner = cone_angle[0]
            handle.cone_angle_outer = cone_angle[1]
            handle.loop_count = loop_count
            handle.cone_volume_outer = cone_outer_volume * volume * master_volume
        if self.reverb:
            self.reverb_samples = ULReverb(
                self,
                sound,
                self.handles[1][0]
            )
        self.aud_system.add(self)
        self.update(True)


class Speaker2D(Sound2D):
    '''Non-spatial sound driven by a BGE speaker object's properties.

    Reads the sound file, volume, and pitch directly from the speaker's
    Blender data-block.

    :param speaker: ``KX_GameObject`` of speaker type.
    :param loop_count: Extra repeats after the first play; ``-1`` loops forever.
    :param lowpass: Lowpass cutoff frequency, or ``False`` to disable.
    :param ignore_timescale: When ``True``, pitch is unaffected by the game
        time scale.
    :param aud_sys: Name of the :class:`~uplogic.audio.audiosystem.AudioSystem`
        to play on.
    '''

    _deprecated = False

    def __init__(
        self,
        speaker: GameObject,
        loop_count: int = 0,
        lowpass=False,
        ignore_timescale: bool = False,
        aud_sys: str = 'default'
    ):
        if self._deprecated:
            console.warning('Warning: ULSpeaker2D class will be renamed to "Speaker2D" in future releases!')
        speaker_data = speaker.blenderObject.data
        # ULSound2D()
        super().__init__(
            speaker_data.sound.filepath,
            speaker_data.volume,
            speaker_data.pitch,
            loop_count,
            lowpass,
            ignore_timescale,
            aud_sys
        )


class ULSpeaker2D(Speaker2D):
    '''[DEPRECATED] Use :class:`Speaker2D` instead.'''
    _deprecated = True


class Speaker3D(Sound3D):
    '''Spatial sound driven by a BGE speaker object's properties.

    Reads the sound file, volume, pitch, attenuation, distance reference, and
    cone settings directly from the speaker's Blender data-block.

    :param speaker: ``KX_GameObject`` of speaker type.
    :param occlusion: When ``True``, cast rays to muffle sounds behind walls.
    :param transition_speed: Interpolation speed between clear and muffled.
    :param cutoff_frequency: Lowpass cutoff for the muffled version as a
        factor of 20 000 Hz.
    :param loop_count: Extra repeats after the first play; ``-1`` loops forever.
    :param reverb: When ``True``, simulate reverb via :class:`ULReverb`.
    :param ignore_timescale: When ``True``, pitch is unaffected by the game
        time scale.
    :param aud_sys: Name of the :class:`~uplogic.audio.audiosystem.AudioSystem`
        to play on.
    '''

    _deprecated = False

    def __init__(
        self,
        speaker: GameObject,
        occlusion: bool = False,
        transition_speed: float = 0.1,
        cutoff_frequency: float = 0.1,
        loop_count: int = 0,
        reverb=False,
        ignore_timescale: bool = False,
        aud_sys: str = 'default'
    ):
        if self._deprecated:
            console.warning('Warning: ULSpeaker3D class will be renamed to "Speaker3D" in future releases!')
        speaker_data = speaker.blenderObject.data
        super().__init__(
            speaker,
            speaker_data.sound.filepath,
            occlusion,
            transition_speed,
            cutoff_frequency,
            loop_count,
            speaker_data.pitch,
            speaker_data.volume,
            reverb,
            speaker_data.attenuation,
            speaker_data.distance_reference,
            [speaker_data.cone_angle_inner, speaker_data.cone_angle_outer],
            speaker_data.cone_volume_outer,
            ignore_timescale,
            aud_sys
        )


class ULSpeaker3D(Speaker3D):
    '''[DEPRECATED] Use :class:`Speaker3D` instead.'''
    _deprecated = True


def play_sound_2d(
        file: str = '',
        volume: float = 1,
        pitch: float = 1,
        loop_count: int = 0,
        lowpass = False,
        ignore_timescale = True,
        mono: bool = False,
        cache: bool = False,
        aud_sys: str = 'default'
    ):
    '''Create and immediately start a :class:`Sound2D`.

    :param file: Path to the sound file.
    :param volume: Playback amplitude (``1.0`` = unity).
    :param pitch: Playback frequency shift (``1.0`` = normal speed).
    :param loop_count: Number of extra repeats; ``-1`` loops forever.
    :param lowpass: Lowpass cutoff frequency, or ``False`` to disable.
    :param ignore_timescale: When ``True`` pitch is unaffected by the game
        time scale.
    :param mono: Down-mix to mono before playback.
    :param cache: Store the decoded sound in :class:`~uplogic.audio.audiosystem.AudioCache`.
    :param aud_sys: Name of the :class:`~uplogic.audio.audiosystem.AudioSystem`
        to play on.
    :returns: The :class:`Sound2D` instance.
    '''
    sound = Sound2D(
        file=file,
        volume=volume,
        pitch=pitch,
        loop_count=loop_count,
        lowpass=lowpass,
        ignore_timescale=ignore_timescale,
        mono=mono,
        aud_sys=aud_sys
    )
    if sound.sound:
        sound.play()
    if cache:
        sound.cache()
    return sound


def play_sound_3d(
        speaker: GameObject or Vector = None,
        file: str = '',
        occlusion: bool = False,
        transition_speed: float = .1,
        cutoff_frequency: float = .1,
        loop_count: int = 0,
        pitch: float = 1,
        volume: float = 1,
        reverb=False,
        attenuation: float = 1,
        distance_ref: float = 1,
        cone_angle: list[float] = [360, 360],
        cone_outer_volume: float = 0,
        ignore_timescale: bool = False,
        cache=False,
        aud_sys: str = 'default'
    ):
    '''Create and immediately start a :class:`Sound3D`.

    :param speaker: ``KX_GameObject`` or ``Vector`` position for the source.
    :param file: Path to the sound file.
    :param occlusion: When ``True``, cast rays to muffle sounds behind walls.
    :param transition_speed: Interpolation speed between clear and muffled.
    :param cutoff_frequency: Lowpass cutoff for the muffled version as a
        factor of 20 000 Hz.
    :param loop_count: Number of extra repeats; ``-1`` loops forever.
    :param pitch: Playback frequency shift (``1.0`` = normal speed).
    :param volume: Playback amplitude (``1.0`` = unity).
    :param reverb: When ``True``, add reverb samples via :class:`ULReverb`.
    :param attenuation: Distance fade factor for the ``aud`` device.
    :param distance_ref: Distance at which the sound plays at full volume.
    :param cone_angle: ``[inner, outer]`` cone angles in degrees; cone is
        aligned to the speaker's ``-Z`` axis.
    :param cone_outer_volume: Volume multiplier outside the outer cone.
    :param ignore_timescale: When ``True`` pitch is unaffected by the game
        time scale.
    :param cache: Store the decoded sound in :class:`~uplogic.audio.audiosystem.AudioCache`.
    :param aud_sys: Name of the :class:`~uplogic.audio.audiosystem.AudioSystem`
        to play on.
    :returns: The :class:`Sound3D` instance.
    '''
    sound = Sound3D(
        speaker=speaker,
        file=file,
        occlusion=occlusion,
        transition_speed=transition_speed,
        cutoff_frequency=cutoff_frequency,
        loop_count=loop_count,
        pitch=pitch,
        volume=volume,
        reverb=reverb,
        attenuation=attenuation,
        distance_ref=distance_ref,
        cone_angle=cone_angle,
        cone_outer_volume=cone_outer_volume,
        ignore_timescale=ignore_timescale,
        aud_sys=aud_sys
    )
    if sound.sound:
        sound.play()
    if cache:
        sound.cache()
    return sound
