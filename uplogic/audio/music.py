from .sound import ULSound2D
from uuid import uuid4
from uplogic.utils import debug, interpolate
from uplogic.events import schedule_callback


class ULMusicEffect():
    def __init__(
        self
    ):
        self._volume = 1.0
        self._pitch = 1.0
        self._fade_event = None

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, val):
        self._volume = val
    
    def fade_out(self, factor=.02):
        self.volume = interpolate(self.volume, 0, factor)
        if self._fade_event:
            self._fade_event.cancel()
            self._fade_event = None
        if self.volume > 0:
            self._fade_event = schedule_callback(self.fade_out, arg=factor)
    
    def fade_in(self, factor=.01):
        self.volume = interpolate(self.volume, 1, factor)
        if self._fade_event:
            self._fade_event.cancel()
            self._fade_event = None
        if self.volume < 1:
            self._fade_event = schedule_callback(self.fade_in, arg=factor)


class ULMusic(ULMusicEffect):
    def __init__(
        self,
        name: str = ''
    ):
        super().__init__()
        self.name = name if name else uuid4()
        self.tracks: list[ULMusicTrack] = []

    @property
    def position(self):
        if not self.tracks:
            return 0.0
        return self.tracks[0].sound.position

    @position.setter
    def position(self, val):
        for track in self.tracks:
            track.position = val

    @property
    def volume(self):
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
        if not track_name:
            track_name = uuid4()
        track = ULMusicTrack(self, sound, track_name)
        self.tracks.append(track)
        return track

    def remove_track(
        self,
        track: int or str = 0,
    ):
        if isinstance(track, str):
            for t in self.tracks:
                if t.name == track:
                    t.remove()
                    return
            debug(f'Track "{track}" not found!')
        else:
            self.tracks[track].remove()

    def get_track(self, name):
        for track in self.tracks:
            if track.name == name:
                return track

    def pause(self):
        for track in self.tracks:
            track.sound.pause()

    def resume(self):
        for track in self.tracks:
            track.sound.resume()
    
    def stop(self):
        for track in self.tracks:
            track.sound.stop()
        self.position = 0.0


class ULMusicTrack(ULMusicEffect):
    def __init__(
        self,
        music: ULMusic,
        sound: str or ULSound2D,
        name: str
    ):
        super().__init__()
        self.music = music
        self.name = name
        sound = ULSound2D(sound) if isinstance(sound, str) else sound
        sound.position = music.position
        self.sound: ULSound2D = sound

    @property
    def position(self):
        return self.sound.position
    
    @position.setter
    def position(self, val):
        self.sound.position = val

    @property
    def volume(self):
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
        return self._pitch
    
    @pitch.setter
    def pitch(self, val):
        self._pitch = 1.0
        self.sound.pitch = val * self.music.pitch

    def remove(self):
        self.sound.stop()
        self.music.tracks.remove(self)
