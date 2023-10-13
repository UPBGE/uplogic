'''TODO: Documentation
'''

from os.path import isfile
from bge import logic
from bge.types import KX_GameObject as GameObject
from mathutils import Vector
from uplogic.audio import ULAudioSystem
from uplogic.audio import get_audio_system
from uplogic.events import schedule_callback
from uplogic.utils.math import interpolate
import bpy
import aud


class ULReverb():
    """Reverb sound added by `Sound3D` on demand.
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
    """Base class for 2D and 3D Sounds
    """

    sound = None
    """Internal `aud.Sound` instance."""
    finished: bool
    """Whether this sound has finished playing."""
    pitch: float
    """Pitch (Frequency Shift)."""
    volume: float
    aud_system: ULAudioSystem

    @property
    def position(self):
        if self.sound:
            return self.sound.position

    @position.setter
    def position(self, val):
        if self.sound:
            self.sound.position = val

    def stop(self):
        '''TODO: Documentation
        '''
        self.on_finish = dummy
        self.sound.stop()

    def pause(self):
        self.sound.pause()

    def resume(self):
        self.sound.resume()
    
    def on_finish(self):
        pass


class ULSound2D(ULSound):
    '''[DEPRECATED] Use `uplogic.audio.Sound2D` instead
    
    Non-spacial sound, e.g. Music or Voice-Overs.\n
    This class allows for modification of pitch and volume while playing.

    :param `file`: Path to the sound file.
    :param `volume`: Initial volume.
    :param `pitch`: Initial pitch.
    :param `loop_count`: Plays the sound this many times (0 for once, -1 for endless).
    :param `aud_sys`: Audiosystem to play this sound on.
    '''

    _deprecated = True

    def __init__(
        self,
        file: str = '',
        volume: float = 1,
        pitch: float = 1,
        loop_count: int = 0,
        lowpass = False,
        ignore_timescale = True,
        aud_sys: str = 'default'
    ):
        if self._deprecated:
            print('Warning: ULSound2D class will be renamed to "Sound2D" in future releases!')
        self.file = file
        self._volume = 1
        self.finished = False
        if not (file):
            return
        self.aud_system = get_audio_system(aud_sys)
        soundfile = logic.expandPath(file)
        self.ignore_timescale = ignore_timescale
        if not isfile(soundfile):
            print(f'Soundfile {soundfile} could not be loaded!')
            return
        sound = self.soundfile = aud.Sound(soundfile)
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

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, val):
        if self.sound and self.sound.status:
            self.sound.volume = val * self.aud_system.volume
        self._volume = val

    @property
    def pitch(self):
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
        return self._lowpass

    @lowpass.setter
    def lowpass(self, val):
        if self._lowpass == val:
            return
        self._lowpass = val
        sound = self.soundfile
        if val:
            sound = sound.lowpass(val, .5)
        sound = self.aud_system.device.play(sound)
        sound.loop_count = self.sound.loop_count
        sound.position = self.sound.position
        sound.volume = self.sound.volume
        sound.pitch = self.sound.pitch
        schedule_callback(self.sound.stop, .1)
        self.sound = sound

    def update(self):
        '''TODO: Documentation
        '''
        if self.volume == 0:
            return
        handle = self.sound
        if not handle.status:
            self.finished = True
            self.on_finish()
            self.aud_system.remove(self)
            return


class Sound2D(ULSound2D):
    '''
    Non-spacial sound, e.g. Music or Voice-Overs.\n
    This class allows for modification of pitch and volume while playing.

    :param `file`: Path to the sound file.
    :param `volume`: Initial volume.
    :param `pitch`: Initial pitch.
    :param `loop_count`: Plays the sound this many times (0 for once, -1 for endless).
    :param `aud_sys`: Audiosystem to play this sound on.
    '''

    _deprecated = False


class Sample2D(Sound2D):
    '''Non-spacial sample, e.g. Music or Voice-Overs.\n
    This class allows for modification of pitch and volume while playing.
    The played audio file can be limited to a start and end time.

    :param `file`: Path to the sound file.
    :param `volume`: Initial volume.
    :param `pitch`: Initial pitch.
    :param `loop_count`: Plays the sound this many times (0 for once, -1 for endless).
    :param `aud_sys`: Audiosystem to play this sound on.
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
        aud_sys: str = 'default'
    ):
        self.file = file
        self._volume = 1
        self.finished = False
        if not (file):
            return
        self.aud_system = get_audio_system(aud_sys)
        soundfile = logic.expandPath(file)
        self.ignore_timescale = ignore_timescale
        if not isfile(soundfile):
            print(f'Soundfile {soundfile} could not be loaded!')
            return
        sound = self.soundfile = aud.Sound(soundfile)
        if sample[1]:
            sound = sound.limit(sample[0], sample[1])
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


class ULSound3D(ULSound):
    '''Spacial sound, e.g. World Effects or Voices.\n
    This class allows for modification of pitch and volume as well as other attributes while playing.
    '''

    _deprecated = True

    @property
    def position(self):
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
            print('Warning: ULSound3D class will be renamed to "Sound3D" in future releases!')
        self._is_vector = isinstance(speaker, Vector)
        self.file = file
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
        soundfile = bpy.data.sounds.get(file)
        if soundfile:
            soundfile = soundfile.filepath
        else:
            soundfile = logic.expandPath(file)
        if not isfile(soundfile):
            print(f'Soundfile {soundfile} could not be loaded!')
            return
        sound = self.soundpath = aud.Sound(soundfile).rechannel(1)
        device = self.aud_system.device
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

    def update(self, init=False):
        '''TODO: Documentation
        '''
        # if self.volume == 0:
        #     for i, handle in enumerate(self.handles[1]):
        #         handle.volume = 0
        #     return
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
                while occluder:
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
                handle.volume = self.volume * mult * master_volume
                handle.cone_volume_outer = (
                    self.cone_outer_volume *
                    self.volume *
                    mult *
                    master_volume
                )
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
        '''TODO: Documentation
        '''
        self.on_finish = dummy
        for sound in self.handles[1]:
            sound.pause()

    def resume(self):
        '''TODO: Documentation
        '''
        self.on_finish = dummy
        for sound in self.handles[1]:
            sound.resume()

    def stop(self):
        '''TODO: Documentation
        '''
        self.on_finish = dummy
        for sound in self.handles[1]:
            sound.stop()


class Sound3D(ULSound3D):
    _deprecated = False


class Sample3D(Sound3D):
    '''Spacial sound, e.g. World Effects or Voices.\n
    This class allows for modification of pitch and volume as well as other attributes while playing.
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
        soundfile = logic.expandPath(file)
        if not isfile(soundfile):
            print(f'Soundfile {soundfile} could not be loaded!')
            return
        sound = self.soundpath = aud.Sound(soundfile).rechannel(1)
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


class ULSpeaker2D(ULSound2D):

    _deprecated = True

    def __init__(
        self,
        speaker: GameObject,
        loop_count: int = 0,
        lowpass=False,
        ignore_timescale: bool = False,
        aud_sys: str = 'default'
    ):
        if self._deprecated:
            print('Warning: ULSpeaker2D class will be renamed to "Speaker2D" in future releases!')
        speaker_data = speaker.blenderObject.data
        ULSound2D()
        super().__init__(
            speaker_data.sound.filepath,
            speaker_data.volume,
            speaker_data.pitch,
            loop_count,
            lowpass,
            ignore_timescale=
            aud_sys
        )


class Speaker2D(ULSpeaker2D):
    _deprecated = False


class ULSpeaker3D(ULSound3D):

    _deprecated = True

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
            print('Warning: ULSpeaker3D class will be renamed to "Speaker3D" in future releases!')
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


class Speaker3D(ULSpeaker3D):
    _deprecated = False
