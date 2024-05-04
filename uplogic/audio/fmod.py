import sys, os
from ..console import error
from ..console import success
from ..console import debug
from ..utils.math import get_local
from ..events import schedule
from sys import platform
import bge
from mathutils import Vector


pypath = sys.executable
if platform == "linux" or platform == "linux2":
    error('Linux support not added yet.')
elif platform == "darwin":
    error('OS X support not added yet.')
elif platform == "win32":
    debug("Loading FMod...")
    dllpath = os.path.join(pypath, os.path.pardir, os.path.pardir, 'DLLs')
    fmodstudioL = os.path.join(dllpath, "fmodstudioL.dll")
    fmodL = os.path.join(dllpath, "fmodL.dll")
    exists_fmodstudioL = os.path.exists(fmodstudioL)
    exists_fmodL = os.path.exists(fmodL)
    if not (exists_fmodL and exists_fmodstudioL):
        if not exists_fmodstudioL:
            error(f'Missing "{fmodstudioL}"')
        if not exists_fmodL:
            error(f'Missing "{fmodL}"')
        error('One or more FMod Libraries not found, go to "https://www.fmod.com/download" and install FMOD Engine, then from ".../api/core/lib/x64" copy "fmodL.dll" and "fmodstudioL.dll" to your local python installation.')
        sys.exit(1)
    else:
        os.environ["PYFMODEX_STUDIO_DLL_PATH"] = fmodstudioL
        os.environ["PYFMODEX_DLL_PATH"] = fmodL
        success("FMod support successfully loaded.")


try:
    import pyfmodex
except ImportError:
    error('"pyfmodex" module missing, please install!')


from pyfmodex import studio as fstudio
from pyfmodex.studio import enums
from pyfmodex import flags


def get_studio():
    FMod.initialize()
    return FMod.studio


class Sound:
    _mode = flags.MODE.TWOD

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        self._position = Vector(val)

    def stop(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError


class File2D(Sound):

    def __init__(self, path, channel='default') -> None:
        self.channel = FMod.channels.get(channel, None)
        self.channel.sounds.append(self)
        system = FMod.studio.core_system
        self.sound: pyfmodex.sound.Sound = system.create_sound(path, self._mode)
        self.channel: pyfmodex.channel.Channel = system.play_sound(self.sound, paused=True)
        self.channel.paused = False

    def update(self):
        pass

    def stop(self):
        self.channel.stop()
        self.sound.release()
        self.channel.sounds.remove(self)


class File3D(File2D):
    _mode = flags.MODE.THREED

    def __init__(self, path, position=Vector((0, 0, 0)), channel='default') -> None:
        super().__init__(path, channel)


class Event(Sound):
    
    def __init__(self, name, position=Vector((0, 0, 0)), channel='default') -> None:
        self.channel = FMod.channels.get(channel, None)
        self.evt = FMod.studio.get_event(name).create_instance()
        self.evt.start()
        FMod.studio.update()
        self._position = position
        self.channel.sounds.append(self)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        self._position = Vector(val)
    
    def update(self):
        if self.evt.playback_state is enums.PLAYBACK_STATE.STOPPED:
            self.stop()
            return
        cam = bge.logic.getCurrentScene().active_camera
        self.evt.set_3d_attributes(get_local(cam, self.position), Vector((0, 100, 0)))

    def set_parameter(self, parameter, value):
        self.evt.set_parameter_by_name(parameter, value)

    def stop(self):
        self.evt.stop()
        if self in self.channel.sounds:
            self.channel.sounds.remove(self)


class Channel(dict):
    def __init__(self, name):
        self.name = name
        self.sounds: list[Sound] = []

    def set(self, key, value):
        self[key] = value
        for sound in self.sounds:
            sound.evt.set_parameter_by_name(key, value)
    
    def destroy(self):
        for sound in self.sounds.copy():
            sound.stop()
        del FMod.channels[self.name]
    
    def event(self, event, position):
        evt = Event(event, position, self.name)
        return evt

    def update(self):
        for sound in self.sounds:
            sound.update()


class FMod:
    channels = {'default': Channel('default')}
    studio: fstudio.StudioSystem = None

    @classmethod
    def initialize(cls):
        if cls.studio is None:
            fmodstudio = fstudio.StudioSystem()
            fmodstudio.initialize()
            cls.studio = fmodstudio
            cls.studio.core_system.advanced_settings.randomSeed = 1024
            scene = bge.logic.getCurrentScene()
            scene.pre_draw.append(cls.update)
            scene.onRemove.append(cls.destroy)
        return cls.studio

    @classmethod
    def load_bank(cls, path):
        cls.studio.load_bank_file(path)

    @classmethod
    def update(cls):
        studio = cls.studio
        scene = bge.logic.getCurrentScene()
        cam = scene.active_camera
        studio.core_system.listener().position = cam.worldPosition
        studio.core_system.listener().set_orientation(
            list(cam.getAxisVect((0, 0, 1))),
            list(cam.getAxisVect((0, 1, 0)))
        )
        studio.update()
        for channel in cls.channels.values():
            channel.update()

    @classmethod
    def add_channel(cls, name):
        cls.channels[name] = Channel(name)

    @classmethod
    def set_channel_parameter(cls, parameter_name, value, channel='default'):
        _channel = cls.channels.get(channel, None)
        if _channel is None:
            error(f'Channel {channel} not found.')
            return
        _channel.set(parameter_name, value)

    @classmethod
    def destroy(cls):
        cls.studio.release()
        cls.studio = None

    @classmethod
    def event(cls, event, position=Vector((0, 0, 0)), channel='default'):
        _channel = cls.channels.get(channel, None)
        if _channel is None:
            _channel = cls.channels[channel] = Channel(channel)
        return Event(event, position, channel)

    @classmethod
    def file3d(cls, path, channel='default'):
        _channel = cls.channels.get(channel, None)
        if _channel is None:
            _channel = cls.channels[channel] = Channel(channel)
        return File3D(path, channel)
