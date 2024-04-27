import sys, os
from ..console import error
from ..console import success
from ..console import debug
from sys import platform
import bge


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
            error(f'Missing {fmodstudioL}')
        if not exists_fmodL:
            error(f'Missing {fmodL}')
        error('One or more FMod Libraries not found, go to "https://www.fmod.com/download#fmodengine" and install FMOD Engine, then from ".../api/core/lib/x64" copy "fmodL" and "fmodstudioL" to your local python installation.')
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

    def stop(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError


class File3D(Sound):

    def __init__(self, path, channel='default') -> None:
        self.channel = FMod.channels.get(channel, None)
        self.channel.sounds.append(self)
        sound = FMod.studio.core_system.create_sound(path)
        self.channel: pyfmodex.channel.Channel = sound.play()
        self.channel.paused = True

    def update(self):
        self.channel.paused = False
        if not self.channel.is_playing:
            self.stop()
            return

    def stop(self):
        self.channel.stop()
        # self.channel.current_sound.release()
        self.channel.sounds.remove(self)


class Event(Sound):
    
    def __init__(self, name, channel='default') -> None:
        self.channel = FMod.channels.get(channel, None)
        self.channel.sounds.append(self)
        self.evt = FMod.studio.get_event(name).create_instance()
        self.evt.start()
    
    def update(self):
        if self.evt.playback_state is enums.PLAYBACK_STATE.STOPPED:
            self.stop()
            return
        for setting in self.channel:
            self.evt.set_parameter_by_name(setting, self.channel[setting])
        try:
            self.evt.channel_group.mode = flags.MODE.THREED
            self.evt.channel_group.position = (0, 0, 0)
        except Exception:
            pass

    def stop(self):
        self.evt.stop()
        self.channel.sounds.remove(self)


class Channel(dict):
    def __init__(self, name):
        self.name = name
        self.sounds: list[Sound] = []
    
    def destroy(self):
        for sound in self.sounds.copy():
            sound.stop()
        del FMod.channels[self.name]
    
    def event(self, event):
        evt = Event(event, self.name)
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
    def destroy(cls):
        cls.studio.release()
        cls.studio = None

    @classmethod
    def event(cls, event, channel='default'):
        _channel = cls.channels.get(channel, None)
        if _channel is None:
            _channel = cls.channels[channel] = Channel(channel)
        return Event(event, channel)

    @classmethod
    def file3d(cls, path, channel='default'):
        _channel = cls.channels.get(channel, None)
        if _channel is None:
            _channel = cls.channels[channel] = Channel(channel)
        return File3D(path, channel)
