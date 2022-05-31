from uplogic.audio.audiosystem import get_audio_system
from .sound import ULSound2D
from uuid import uuid4
from uplogic.utils import debug, interpolate
from uplogic.events import schedule_callback


class ULMusicEffect():
    '''Base class for sounds played as music.'''
    def __init__(
        self
    ):
        self._volume = 1.0
        self._pitch = 1.0
        self._fade_event = None

    @property
    def volume(self):
        '''Volume of this component.'''
        return self._volume

    @volume.setter
    def volume(self, val):
        self._volume = val

    def fade_out(self, factor=.02):
        '''Fade out this sound using linear interpolation.

        :param `factor`: Speed of interpolation.'''
        self.volume = interpolate(self.volume, 0, factor)
        if self._fade_event:
            self._fade_event.cancel()
            self._fade_event = None
        if self.volume > 0:
            self._fade_event = schedule_callback(self.fade_out, arg=factor)

    def fade_in(self, factor=.01):
        '''Fade in this sound using linear interpolation.

        :param `factor`: Speed of interpolation.'''
        self.volume = interpolate(self.volume, 1, factor)
        if self._fade_event:
            self._fade_event.cancel()
            self._fade_event = None
        if self.volume < 1:
            self._fade_event = schedule_callback(self.fade_in, arg=factor)


class ULMusic(ULMusicEffect):
    '''Management class for controlling multiple music tracks.

    :param `name`; Name of this music.'''
    def __init__(
        self,
        name: str = '',
        audio_system: str = 'music'
    ):
        super().__init__()
        self.name = name if name else uuid4()
        self.audio_system = get_audio_system(audio_system, '2D')
        self.tracks: list[ULMusicTrack] = []

    @property
    def position(self):
        '''Playback position of the first track of the music (and consequently
        all other tracks).'''
        if not self.tracks:
            return 0.0
        return self.tracks[0].sound.position

    @position.setter
    def position(self, val):
        for track in self.tracks:
            track.position = val

    @property
    def volume(self):
        '''Master volume of this music.'''
        return self._volume

    @volume.setter
    def volume(self, val):
        self._volume = val
        for track in self.tracks:
            track.sound.volume = track.volume * val
        if self._fade_event:
            self._fade_event.cancel()
            self._fade_event = None

    @property
    def pitch(self):
        '''Master pitch of this music.'''
        return self._volume

    @pitch.setter
    def pitch(self, val):
        self._pitch = val
        for track in self.tracks:
            track.sound.pitch = track.pitch * val
        if self._fade_event:
            self._fade_event.cancel()
            self._fade_event = None

    def add_track(
        self,
        sound: str or ULSound2D,
        track_name: str = ''
    ):
        '''Add a track to this music. A track is typically one instrument or
        effect.
        
        :param `sound`: Path to the sound file or `ULSound2D` instance.
        :param `name`: Name of this track (e.g. "Drums")'''
        if not track_name:
            track_name = uuid4()
        track = ULMusicTrack(self, sound, track_name)
        self.tracks.append(track)
        return track

    def remove_track(
        self,
        track: int or str = 0,
    ):
        '''Remove a track from this music.
        
        :param `track`: Index or name of the track to be removed.'''
        if isinstance(track, str):
            for t in self.tracks:
                if t.name == track:
                    t.remove()
                    return
            debug(f'Track "{track}" not found!')
        else:
            self.tracks[track].remove()

    def get_track(self, name):
        '''Get track by name.
        
        :param `name`: Name of the track.'''
        for track in self.tracks:
            if track.name == name:
                return track

    def pause(self):
        '''Pause this music (all tracks).'''
        for track in self.tracks:
            track.sound.pause()

    def resume(self):
        '''Rasume this music (all tracks).'''
        for track in self.tracks:
            track.sound.resume()

    def stop(self):
        '''Stop this music (all tracks).'''
        for track in self.tracks:
            track.sound.stop()
        self.position = 0.0


class ULMusicTrack(ULMusicEffect):
    '''Track to be played on a `ULMusic` instance.
    
    :param `music`: The music object this track will be played on.
    :param `sound`: Path to the soundfile of this track.
    :param `name`: Name of this track (e.g. "Drums).'''
    def __init__(
        self,
        music: ULMusic,
        sound: str or ULSound2D,
        name: str
    ):
        super().__init__()
        self.music = music
        self.name = name
        sound = ULSound2D(
            sound,
            aud_sys=self.music.audio_system
        ) if isinstance(sound, str) else sound
        sound.position = music.position
        self.sound: ULSound2D = sound

    @property
    def position(self):
        '''Playback position of this track.'''
        return self.sound.position

    @position.setter
    def position(self, val):
        self.sound.position = val

    @property
    def volume(self):
        '''Volume of this track.'''
        return self._volume

    @volume.setter
    def volume(self, val):
        self._volume = val
        self.sound.volume = val * self.music.volume
        if self._fade_event:
            self._fade_event.cancel()
            self._fade_event = None

    @property
    def pitch(self):
        '''Pitch of this track.'''
        return self._pitch

    @pitch.setter
    def pitch(self, val):
        self._pitch = 1.0
        self.sound.pitch = val * self.music.pitch

    def remove(self):
        '''Stop and remove this track from its `ULMusic` object.'''
        self.sound.stop()
        self.music.tracks.remove(self)
