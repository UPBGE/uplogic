'''TODO: Documentation
'''

from os.path import isfile
from bge import logic
from bge.types import KX_GameObject as GameObject
from mathutils import Vector
from uplogic.audio import AudioSystem
from uplogic.audio import get_audio_system
from uplogic.events import schedule_callback
from uplogic.utils.math import interpolate
from uplogic.console import warning
from uplogic.utils import DELTA_TIME
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
    """Base class for 2D and 3D Sounds"""

    sound = None
    """Internal `aud.Sound` instance."""
    finished: bool
    """True if the sound has played to its end."""
    pitch: float
    """Pitch (Frequency Shift)."""
    volume: float
    """Volume (Amplitude)."""
    aud_system: AudioSystem
    """Audio System this sound is playing on."""

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

    @property
    def keep(self):
        return self.sound.keep
    
    @keep.setter
    def keep(self, val):
        self.sound.keep = val

    def on_finish(self):
        '''Standart callback to be called when the sound finishes or is stopped.'''
        pass


class Sound2D(ULSound):
    '''
    Non-spacial sound, e.g. Music or Voice-Overs.\n
    This class allows for modification of pitch and volume while playing.

    :param `file`: Path to the sound file.
    :param `volume`: Initial volume.
    :param `pitch`: Initial pitch.
    :param `loop_count`: Plays the sound this many times (0 for once, -1 for endless).
    :param `lowpass`: Play this effect with a lowpass filter applied.
    :param `ignore_timescale`: Play the sound using `Sound2D.pitch`, regardless of the current timescale.
    :param `aud_sys`: Audiosystem to play this sound on.
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
        aud_sys: str = 'default'
    ):
        if self._deprecated:
            warning('Warning: ULSound2D class will be renamed to "Sound2D" in future releases!')
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
        '''Frequency cutoff as a factor of 20.000.'''
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
        '''This function is called each frame and updates the attributes of the sound according to the scene.'''
        if self.volume == 0:
            return
        handle = self.sound
        if not handle.status:
            self.finished = True
            self.on_finish()
            self.aud_system.remove(self)
            return


class ULSound2D(Sound2D):
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


class Sample2D(Sound2D):
    '''Non-spacial sample, e.g. Music or Voice-Overs.\n
    This class allows for modification of pitch and volume while playing.
    The played audio file can be limited to a start and end time.

    :param `file`: Path to the sound file.
    :param `sample`: Tuple containing the "start" and "end" timestamp.
    :param `volume`: Initial volume.
    :param `pitch`: Initial pitch.
    :param `loop_count`: Plays the sound this many times (0 for once, -1 for endless).
    :param `lowpass`: Play this effect with a lowpass filter applied.
    :param `ignore_timescale`: Play the sound using `Sample2D.pitch`, regardless of the current timescale.
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


class Sound3D(ULSound):
    '''Spacial sound, e.g. World Effects or Voices.\n
    
    :param `speaker`: Play the sound at a `Vector` or use a `KX_GameObject`.
    :param `file`: Path to the sound file.
    :param `occlusion`: Muffle sounds behind walls (can be bad for performance).
    :param `transition_speed`: Fading speed from regular to muffled.
    :param `cutoff_frequency`: Cutoff for muffled version as a factor of 20.000.
    :param `loop_count`: The amount of times the sound should be played. -1 is looped.
    :param `pitch`: Initial pitch.
    :param `volume`: Initial volume.
    :param `reverb`: Use conditional reverberation (performance intense).
    :param `attenuation`: Distance fade factor.
    :param `distance_ref`: Distance at which the sound is audible at 100% volume.
    :param `cone_angle`: Cone spread for directional sounds. Cone is aligned to the -Z axis.
    :param `cone_outer_volume`: Volume outside of the cone.
    :param `ignore_timescale`: Play the sound using `Sound3D.pitch`, regardless of the current timescale.
    :param `aud_sys`: Audiosystem to play this sound on.
    '''

    _deprecated = False

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
            warning('Warning: ULSound3D class will be renamed to "Sound3D" in future releases!')
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
        '''This function is called each frame and updates the attributes of the sound according to the scene.'''
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
        self.on_finish = dummy
        for sound in self.handles[1]:
            sound.pause()

    def resume(self):
        self.on_finish = dummy
        for sound in self.handles[1]:
            sound.resume()

    def stop(self):
        self.on_finish = dummy
        for sound in self.handles[1]:
            sound.stop()


class ULSound3D(Sound3D):
    _deprecated = True


class Sample3D(Sound3D):
    '''Spacial sound, e.g. World Effects or Voices.\n
    
    :param `speaker`: Play the sound at a `Vector` or use a `KX_GameObject`.
    :param `file`: Path to the sound file.
    :param `sample`: Tuple containing the "start" and "end" timestamp.
    :param `occlusion`: Muffle sounds behind walls (can be bad for performance).
    :param `transition_speed`: Fading speed from regular to muffled.
    :param `cutoff_frequency`: Cutoff for muffled version as a factor of 20.000.
    :param `loop_count`: The amount of times the sound should be played. -1 is looped.
    :param `pitch`: Initial pitch.
    :param `volume`: Initial volume.
    :param `reverb`: Use conditional reverberation (performance intense).
    :param `attenuation`: Distance fade factor.
    :param `distance_ref`: Distance at which the sound is audible at 100% volume.
    :param `cone_angle`: Cone spread for directional sounds. Cone is aligned to the -Z axis.
    :param `cone_outer_volume`: Volume outside of the cone.
    :param `ignore_timescale`: Play the sound using `Sample3D.pitch`, regardless of the current timescale.
    :param `aud_sys`: Audiosystem to play this sound on.
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


class Speaker2D(Sound2D):
    '''Start a speaker object using its properties.\n
    
    :param `speaker`: `KX_GameObject` of speaker type.
    :param `loop_count`: The amount of times the sound should be played. -1 is looped.
    :param `lowpass`: Play this effect with a lowpass filter applied.
    :param `ignore_timescale`: Play the sound using `Speaker2D.pitch`, regardless of the current timescale.
    :param `aud_sys`: Audiosystem to play this sound on.
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
            warning('Warning: ULSpeaker2D class will be renamed to "Speaker2D" in future releases!')
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
    _deprecated = True


class Speaker3D(Sound3D):
    '''Start a speaker object using its properties.\n
    
    :param `speaker`: `KX_GameObject` of speaker type.
    :param `occlusion`: Muffle sounds behind walls (can be bad for performance).
    :param `transition_speed`: Fading speed from regular to muffled.
    :param `cutoff_frequency`: Cutoff for muffled version as a factor of 20.000.
    :param `loop_count`: The amount of times the sound should be played. -1 is looped.
    :param `reverb`: Use conditional reverberation (performance intense).
    :param `ignore_timescale`: Play the sound using `Speaker3D.pitch`, regardless of the current timescale.
    :param `aud_sys`: Audiosystem to play this sound on.
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
            warning('Warning: ULSpeaker3D class will be renamed to "Speaker3D" in future releases!')
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
    _deprecated = True


def play_sound_2d(
        file: str = '',
        volume: float = 1,
        pitch: float = 1,
        loop_count: int = 0,
        lowpass = False,
        ignore_timescale = True,
        aud_sys: str = 'default'
    ):
        sound = Sound2D(
            file=file,
            volume=volume,
            pitch=pitch,
            loop_count=loop_count,
            lowpass=lowpass,
            ignore_timescale=ignore_timescale,
            aud_sys=aud_sys
        )
        sound.play()
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
        aud_sys: str = 'default'
    ):
        return Sound3D(
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
