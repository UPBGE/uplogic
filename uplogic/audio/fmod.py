import sys, os
from uplogic.console import error
from uplogic.console import success
from uplogic.console import warning
from uplogic.console import debug
from uplogic.utils.math import get_local
from uplogic.utils.raycasting import raycast
from uplogic.utils import check_vr_session_status
from uplogic.utils.visualize import draw_arrow, draw_cube
from uplogic.events import schedule
from uplogic.input.vr import VR_HEADSET, VR_STATE
from sys import platform
import bge, bpy
from bge.types import KX_GameObject
from mathutils import Vector, Matrix


pypath = sys.executable
if platform == "linux" or platform == "linux2":
    error('FMod: Linux support not added yet.')
elif platform == "darwin":
    error('FMod: OS X not supported, please consider contributing.')
elif platform == "win32":
    debug("Loading FMod...")
    version = bpy.app.version
    dllpath = os.path.join(os.getcwd(), f'{version[0]}.{version[1]}', 'python', 'DLLs')
    fmodstudioL = os.path.join(dllpath, "fmodstudioL.dll")
    fmodL = os.path.join(dllpath, "fmodL.dll")
    exists_fmodstudioL = os.path.exists(fmodstudioL)
    exists_fmodL = os.path.exists(fmodL)
    if not (exists_fmodL and exists_fmodstudioL):
        if not exists_fmodstudioL:
            error(f'Missing "{fmodstudioL}"')
        if not exists_fmodL:
            error(f'Missing "{fmodL}"')
        error('One or more FMod Libraries not found, go to "https://www.fmod.com/download" and install FMOD Engine, then from ".../api/core/lib/x64" copy "fmodL.dll" and from ".../api/studio/lib/x64" copy "fmodstudioL.dll" to your local "python/dlls" installation.')
        sys.exit(0)
    else:
        os.environ["PYFMODEX_STUDIO_DLL_PATH"] = fmodstudioL
        os.environ["PYFMODEX_DLL_PATH"] = fmodL
        success('FMod libraries successfully loaded. Please check license at "https://www.fmod.com/licensing".')


try:
    import pyfmodex
except ImportError:
    error('"pyfmodex" module missing, please install!')


from pyfmodex import studio as fstudio
from pyfmodex.studio import enums
from pyfmodex import flags


version = pyfmodex.__version__.split('.')
if int(version[1]) <= 7 and int(version[2]) <= 2:
    error(f'"pyfmodex" module version {version} not supported, please update!')
    sys.exit(0)


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

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, val):
        self._velocity = Vector(val)
    
    @property
    def is_valid(self):
        return False

    @property
    def is_virtual(self):
        return False

    @property
    def paused(self):
        return True

    @property
    def occluded(self):
        return False

    def visualize(self, color=(1, 1, 1, 1), size=.2):
        raise NotImplementedError

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
        self._orientation = Matrix()
        self.channel = FMod.channels.get(channel, None)
        self.evt = FMod.studio.get_event(name).create_instance()
        self.occlusion_mask = self.channel.occlusion_mask
        self.evt.start()
        self.velocity = Vector((0, 0, 0))
        FMod.studio.update()
        self._position = position
        self.channel.sounds.append(self)
        self.occlusion_near_clipping = 0.0
        self._caster = bge.logic.getCurrentScene().active_camera

    @property
    def ray_caster(self):
        return self._caster

    @ray_caster.setter
    def ray_caster(self, val):
        self._caster = val

    @property
    def is_valid(self):
        return self.evt.is_valid

    @property
    def is_virtual(self):
        return self.evt.is_virtual

    @property
    def channel_group(self):
        return self.evt.channel_group

    @property
    def channel_group(self):
        return self.evt.channel_group

    @property
    def volume(self):
        return self.evt.get_volume()

    @volume.setter
    def volume(self, vol):
        self.evt.set_volume(vol)

    @property
    def pitch(self):
        return self.evt.get_pitch()

    @pitch.setter
    def pitch(self, vol):
        self.evt.set_pitch(vol)

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, val):
        self.evt.forward = val @ Vector((0, 1, 0))
        self.evt.up = val @ Vector((0, 0, 1))
        self._orientation = val

    @property
    def up(self):
        return self.orientation @ Vector((0, 0, 1))

    @property
    def forward(self):
        return self.orientation @ Vector((0, 1, 0))

    @property
    def occluded(self):
        direction = (FMod.listener.worldPosition - self.position).normalized()
        ray = raycast(
            self._caster,
            self.position + direction * self.occlusion_near_clipping,
            FMod.listener.worldPosition,
            mask=self.occlusion_mask,
            visualize=True
        )
        while ray.obj and not ray.obj.blenderObject.get('sound_occluder', True):
            ray = raycast(
                ray.obj,
                ray.point,
                FMod.listener.worldPosition,
                mask=self.occlusion_mask,
                visualize=True
            )
        return ray.obj is not None
            

    @property
    def paused(self):
        return self.evt.paused

    @paused.setter
    def paused(self, val):
        self.evt.paused = val

    @property
    def playback_state(self):
        return self.evt.playback_state

    @property
    def timeline_position(self):
        return self.evt.timeline_position

    def update(self):
        if self.evt.playback_state is enums.PLAYBACK_STATE.STOPPED:
            self.evt.release()
            self.stop()
            return
        cam = bge.logic.getCurrentScene().active_camera
        self.evt.set_3d_attributes(get_local(cam, self.position), self.velocity, self.forward)

    def visualize(self, color=(1, 1, 1, 1), size=.2):
        draw_arrow(self.position, self.position + Vector(self.evt.forward) * size, color)
        # draw_cube(self.position, size * .5, centered=True)

    def set_parameter(self, parameter, value, ignore_seek_speed=False):
        self.evt.set_parameter_by_name(parameter, value, ignore_seek_speed)

    def get_parameter(self, parameter, actual=False):
        param = self.evt.get_parameter_by_name(parameter) 
        return param[1] if actual else param[0]

    def stop(self):
        self.evt.stop()
        if self in self.channel.sounds:
            self.channel.sounds.remove(self)
        self.evt.release()


class EventSpeaker(Event):

    def __init__(self, name, speaker: KX_GameObject, channel='default') -> None:
        self.speaker = speaker
        super().__init__(name, speaker.worldPosition, channel)
        self._caster = speaker

    @property
    def velocity(self):
        return self.speaker.worldLinearVelocity * self._velocity

    @velocity.setter
    def velocity(self, val):
        self._velocity = Vector(val)

    @property
    def position(self):
        return self.speaker.worldPosition

    @position.setter
    def position(self, val):
        self.speaker.worldPosition = Vector(val)

    @property
    def orientation(self):
        return self.speaker.worldOrientation

    @orientation.setter
    def orientation(self, val):
        self.evt.forward = val @ Vector((0, 1, 0))
        self.evt.up = val @ Vector((0, 0, 1))
        self.speaker.worldOrientation = val


class Channel(dict):
    def __init__(self, name, occlusion_mask=65535):
        self.name = name
        self.sounds: list[Sound] = []
        self.occlusion_mask = occlusion_mask

    @property
    def occlusion_mask(self):
        return self._occlusion_mask

    @occlusion_mask.setter
    def occlusion_mask(self, val):
        self._occlusion_mask = val
        for s in self.sounds:
            s.occlusion_mask = val

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
    listener = None

    @classmethod
    def initialize(cls):
        if cls.studio is None:
            fmodstudio = fstudio.StudioSystem()
            fmodstudio.initialize()
            cls.studio = fmodstudio
            scene = bge.logic.getCurrentScene()
            cls.listener = VR_HEADSET if VR_STATE else scene.active_camera
            scene.pre_draw.append(cls.update)
            scene.onRemove.append(cls.destroy)
        return cls.studio

    @classmethod
    def set_occlusion_mask(self, mask: int):
        for channel in self.channels.values():
            channel.occlusion_mask = mask

    @classmethod
    def load_bank(cls, path):
        if not os.path.exists(path):
            error(f"Couldn't load bank from '{path}'")
        if cls.studio is not None:
            from pyfmodex.exceptions import FmodError
            try:
                cls.studio.load_bank_file(path)
            except FmodError:
                warning(f"Bank '{path}' already loaded!")
                return
        success(f"Bank '{path}' successfully loaded.")

    @classmethod
    def update(cls):
        
        scene = bge.logic.getCurrentScene()
        cls.listener = VR_HEADSET if VR_STATE else scene.active_camera
        studio = cls.studio
        cam = cls.listener
        # if cam is None:
        #     scene = bge.logic.getCurrentScene()
        #     cam = cls.listener = scene.active_camera
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
        if cls.studio is None:
            return
        _channel = cls.channels.get(channel, None)
        if _channel is None:
            error(f'Channel {channel} not found.')
            return
        _channel.set(parameter_name, value)

    @classmethod
    def set_channel_occlusion_mask(cls, mask=65535, channel='default'):
        _channel = cls.channels.get(channel, None)
        if _channel is None:
            error(f'Channel {channel} not found.')
            return
        _channel.occlusion_mask = mask

    @classmethod
    def destroy(cls):
        scene = bge.logic.getCurrentScene()
        if cls.update in scene.pre_draw:
            scene.pre_draw.remove(cls.update)
            cls.studio.release()
            cls.studio = None

    @classmethod
    def event(cls, event, source=Vector((0, 0, 0)), channel='default') -> Event | EventSpeaker:
        if cls.studio is None:
            return
        _channel = cls.channels.get(channel, None)
        if _channel is None:
            _channel = cls.channels[channel] = Channel(channel)
        if isinstance(source, KX_GameObject):
            evt = EventSpeaker(f'event:/{event}', source, channel)
        else:
            evt = Event(f'event:/{event}', Vector(source), channel)
        return evt

    @classmethod
    def file3d(cls, path, channel='default'):
        if cls.studio is None:
            return
        _channel = cls.channels.get(channel, None)
        if _channel is None:
            _channel = cls.channels[channel] = Channel(channel)
        return File3D(path, channel)


FMod.initialize()


def load_bank(path):
    FMod.load_bank(path)


def start_event(event, source=Vector((0, 0, 0)), channel='default'):
    return FMod.event(event, source, channel)


def set_occlusion_mask(mask):
    FMod.set_occlusion_mask(mask)


def set_channel_occlusion_mask(mask):
    FMod.set_channel_occlusion_mask(mask)


def set_channel_parameter(parameter, value, channel='default'):
    FMod.set_channel_parameter(parameter, value, channel)


def add_channel(name):
    FMod.add_channel(name)