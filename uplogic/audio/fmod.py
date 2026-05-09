'''FMOD Studio integration for uplogic.

Wraps `pyfmodex <https://pypi.org/project/pyfmodex/>`_ to expose FMOD Studio
events, file-based sounds, and a channel/parameter system inside the BGE
scene loop. FMOD DLLs must be installed alongside the Blender Python runtime
(see the error messages in :class:`FMod` for exact paths).

.. note::
    Linux and macOS are not currently supported.

Typical usage::

    from uplogic.audio import fmod

    fmod.load_bank('//banks/Master.bank')
    fmod.load_bank('//banks/Master.strings.bank')

    # fire an event at a fixed world position
    fmod.start_event('Explosion', source=(10, 0, 0))

    # or attach it to a game object
    fmod.start_event('Engine', source=my_vehicle)
'''
import sys, os
from uplogic.console import error
from uplogic.console import success
from uplogic.console import warning
from uplogic.console import debug
from uplogic.utils.math import get_local
from uplogic.utils.raycasting import raycast
from uplogic.utils.visualize import draw_arrow, draw_cube
from uplogic.events import schedule
from uplogic.input.vr import VR_HEADSET, VR_STATE
from sys import platform
import bge, bpy
from bge.types import KX_GameObject
from mathutils import Vector, Matrix


pypath = sys.executable
if platform == "linux" or platform == "linux2":
    error('FMod: Linux support not added yet, please consider contributing.')
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
        try:
            import pyfmodex
        except ImportError:
            error('"pyfmodex" module missing, please install!')
        os.environ["PYFMODEX_STUDIO_DLL_PATH"] = fmodstudioL
        os.environ["PYFMODEX_DLL_PATH"] = fmodL
        success('FMod libraries successfully loaded. Please check license at "https://www.fmod.com/licensing".')
        success(f'Using pyfmodex version {pyfmodex.__version__}.')




from pyfmodex import studio as fstudio
from pyfmodex.studio import enums
from pyfmodex import flags


version = pyfmodex.__version__.split('.')
if int(version[1]) < 7 and int(version[2]) < 2:
    error(f'"pyfmodex" module version {version} not supported, please update!')
    sys.exit(0)


def get_studio():
    '''Return the active :class:`FMod` FMOD Studio instance, initialising it
    if it has not been created yet.

    :returns: ``pyfmodex.studio.StudioSystem``
    '''
    FMod.initialize()
    return FMod.studio


class Sound:
    '''Abstract base class for all FMOD sound sources.

    Subclasses must implement :meth:`stop` and :meth:`update`.
    '''
    _mode = flags.MODE.TWOD

    @property
    def position(self):
        '''World position of this sound source as a ``Vector``.'''
        return self._position

    @position.setter
    def position(self, val):
        self._position = Vector(val)

    @property
    def velocity(self):
        '''World-space velocity of this sound source, used for Doppler.'''
        return self._velocity

    @velocity.setter
    def velocity(self, val):
        self._velocity = Vector(val)

    @property
    def is_valid(self):
        '''``True`` if the underlying FMOD object is still valid.'''
        return False

    @property
    def is_virtual(self):
        '''``True`` if FMOD has virtualised this sound (inaudible but alive).'''
        return False

    @property
    def paused(self):
        '''``True`` if this sound is currently paused.'''
        return True

    @property
    def occluded(self):
        '''``True`` if a geometry ray-cast determined the sound is occluded.'''
        return False

    def visualize(self, color=(1, 1, 1, 1), size=.2):
        '''Draw a debug overlay for this sound in the BGE viewport.

        :param color: RGBA colour tuple.
        :param size: Scale of the visualisation gizmo.
        '''
        raise NotImplementedError

    def stop(self):
        '''Stop this sound and release its FMOD resources.'''
        raise NotImplementedError

    def update(self):
        '''Per-frame update called by the owning :class:`Channel`.'''
        raise NotImplementedError


class File2D(Sound):
    '''Non-spatial (2-D) sound loaded directly from a file path.

    :param path: Absolute or relative path to the audio file.
    :param channel: Name of the :class:`Channel` to play on.
    '''

    def __init__(self, path, channel='default') -> None:
        self.channel = FMod.channels.get(channel, None)
        self.channel.sounds.append(self)
        system = FMod.studio.core_system
        self.sound: pyfmodex.sound.Sound = system.create_sound(path, self._mode)
        self.channel: pyfmodex.channel.Channel = system.play_sound(self.sound, paused=True)
        self.channel.paused = False

    def update(self):
        '''Per-frame update (no-op for file-based sounds).'''
        pass

    def stop(self):
        '''Stop playback and release the FMOD sound and channel resources.'''
        self.channel.stop()
        self.sound.release()
        self.channel.sounds.remove(self)


class File3D(File2D):
    '''Spatial (3-D) sound loaded directly from a file path.

    :param path: Absolute or relative path to the audio file.
    :param position: Initial world position as a ``Vector``.
    :param channel: Name of the :class:`Channel` to play on.
    '''
    _mode = flags.MODE.THREED

    def __init__(self, path, position=Vector((0, 0, 0)), channel='default') -> None:
        super().__init__(path, channel)


class Event(Sound):
    '''FMOD Studio event instance placed at a fixed world position.

    :param name: FMOD Studio event path, e.g. ``'event:/Explosion'``.
    :param position: Initial world position as a ``Vector``.
    :param channel: Name of the :class:`Channel` to register on.
    '''

    def __init__(self, name, position=Vector((0, 0, 0)), channel='default') -> None:
        self._orientation = Matrix()
        self.channel = FMod.channels.get(channel, None)
        evt = FMod.studio.get_event(name)
        self.evt = evt.create_instance()
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
        '''Object used as the origin for occlusion ray-casts.'''
        return self._caster

    @ray_caster.setter
    def ray_caster(self, val):
        self._caster = val

    @property
    def is_valid(self):
        '''``True`` if the underlying FMOD event instance is still valid.'''
        return self.evt.is_valid

    @property
    def is_virtual(self):
        '''``True`` if FMOD has virtualised this event (inaudible but alive).'''
        return self.evt.is_virtual

    @property
    def channel_group(self):
        '''FMOD channel group associated with this event instance.'''
        return self.evt.channel_group

    @property
    def volume(self):
        '''Playback amplitude of this event (``1.0`` = unity gain).'''
        return self.evt.get_volume()

    @volume.setter
    def volume(self, vol):
        self.evt.set_volume(vol)

    @property
    def pitch(self):
        '''Playback pitch multiplier of this event (``1.0`` = normal speed).'''
        return self.evt.get_pitch()

    @pitch.setter
    def pitch(self, vol):
        self.evt.set_pitch(vol)

    @property
    def orientation(self):
        '''Rotation matrix describing the event's facing direction.'''
        return self._orientation

    @orientation.setter
    def orientation(self, val):
        self.evt.forward = val @ Vector((0, 1, 0))
        self.evt.up = val @ Vector((0, 0, 1))
        self._orientation = val

    @property
    def up(self):
        '''World-space up vector derived from the event's orientation.'''
        return self.orientation @ Vector((0, 0, 1))

    @property
    def forward(self):
        '''World-space forward vector derived from the event's orientation.'''
        return self.orientation @ Vector((0, 1, 0))

    @property
    def occluded(self):
        '''``True`` if a ray-cast from the listener to this event's position
        hits at least one geometry object tagged as a sound occluder.
        '''
        direction = (FMod.listener.worldPosition - self.position).normalized()
        ray = raycast(
            self._caster,
            self.position + direction * self.occlusion_near_clipping,
            FMod.listener.worldPosition,
            mask=self.occlusion_mask
        )
        while ray.obj and not ray.obj.blenderObject.get('sound_occluder', True):
            ray = raycast(
                ray.obj,
                ray.point,
                FMod.listener.worldPosition,
                mask=self.occlusion_mask
            )
        return ray.obj is not None
            

    @property
    def paused(self):
        '''``True`` if this event is currently paused.'''
        return self.evt.paused

    @paused.setter
    def paused(self, val):
        self.evt.paused = val

    @property
    def playback_state(self):
        '''Current FMOD ``PLAYBACK_STATE`` enum value for this event.'''
        return self.evt.playback_state

    @property
    def timeline_position(self):
        '''Current timeline position in milliseconds.'''
        return self.evt.timeline_position

    def update(self):
        '''Per-frame update: release the event when it has stopped, otherwise
        push the current 3-D attributes to FMOD.
        '''
        if self.evt.playback_state is enums.PLAYBACK_STATE.STOPPED:
            self.evt.release()
            self.stop()
            return
        cam = bge.logic.getCurrentScene().active_camera
        self.evt.set_3d_attributes(get_local(cam, self.position), self.velocity, self.forward)

    def visualize(self, color=(1, 1, 1, 1), size=.2):
        '''Draw a direction arrow at this event's world position.

        :param color: RGBA colour tuple.
        :param size: Length of the arrow in world units.
        '''
        draw_arrow(self.position, self.position + Vector(self.evt.forward) * size, color)
        # draw_cube(self.position, size * .5, centered=True)

    def set_parameter(self, parameter, value, ignore_seek_speed=False):
        '''Set a named FMOD Studio parameter on this event instance.

        :param parameter: Parameter name string.
        :param value: Target value.
        :param ignore_seek_speed: Skip the parameter's seek speed when ``True``.
        '''
        self.evt.set_parameter_by_name(parameter, value, ignore_seek_speed)

    def get_parameter(self, parameter, actual=False):
        '''Read a named FMOD Studio parameter from this event instance.

        :param parameter: Parameter name string.
        :param actual: When ``True`` return the actual (current) value instead
            of the target value.
        :returns: ``float`` parameter value.
        '''
        param = self.evt.get_parameter_by_name(parameter)
        return param[1] if actual else param[0]

    def stop(self):
        '''Stop and release this event instance, removing it from its channel.'''
        self.evt.stop()
        if self in self.channel.sounds:
            self.channel.sounds.remove(self)
        self.evt.release()


class EventSpeaker(Event):
    '''FMOD Studio event instance whose position and orientation are driven by
    a ``KX_GameObject`` speaker object.

    :param name: FMOD Studio event path, e.g. ``'event:/Engine'``.
    :param speaker: Game object that acts as the moving sound source.
    :param channel: Name of the :class:`Channel` to register on.
    '''

    def __init__(self, name, speaker: KX_GameObject, channel='default') -> None:
        self.speaker = speaker
        super().__init__(name, speaker.worldPosition, channel)
        self._caster = speaker

    @property
    def velocity(self):
        '''World-space velocity of the speaker object, scaled by the velocity
        factor set on this event.
        '''
        return self.speaker.worldLinearVelocity * self._velocity

    @velocity.setter
    def velocity(self, val):
        self._velocity = Vector(val)

    @property
    def position(self):
        '''World position of the speaker object.'''
        return self.speaker.worldPosition

    @position.setter
    def position(self, val):
        self.speaker.worldPosition = Vector(val)

    @property
    def orientation(self):
        '''World orientation matrix of the speaker object.'''
        return self.speaker.worldOrientation

    @orientation.setter
    def orientation(self, val):
        self.evt.forward = val @ Vector((0, 1, 0))
        self.evt.up = val @ Vector((0, 0, 1))
        self.speaker.worldOrientation = val


class Channel(dict):
    '''Named group of :class:`Sound` instances that share an occlusion mask
    and a set of FMOD Studio parameter values.

    :param name: Unique name for this channel.
    :param occlusion_mask: Bitmask used for occlusion ray-casts; defaults to
        all layers (``65535``).
    '''

    def __init__(self, name, occlusion_mask=65535):
        self.name = name
        self.sounds: list[Sound] = []
        self.occlusion_mask = occlusion_mask

    @property
    def occlusion_mask(self):
        '''Bitmask applied to occlusion ray-casts for all sounds in this channel.

        Setting this value propagates the new mask to every active sound.
        '''
        return self._occlusion_mask

    @occlusion_mask.setter
    def occlusion_mask(self, val):
        self._occlusion_mask = val
        for s in self.sounds:
            s.occlusion_mask = val

    def set(self, key, value):
        '''Set a FMOD Studio parameter on every active sound in this channel.

        :param key: Parameter name string.
        :param value: Target parameter value.
        '''
        self[key] = value
        for sound in self.sounds:
            sound.evt.set_parameter_by_name(key, value)

    def destroy(self):
        '''Stop all sounds in this channel and remove it from :class:`FMod`.'''
        for sound in self.sounds.copy():
            sound.stop()
        del FMod.channels[self.name]

    def event(self, event, position):
        '''Create a new :class:`Event` on this channel.

        :param event: FMOD Studio event path string.
        :param position: World position ``Vector`` for the event.
        :returns: New :class:`Event` instance.
        '''
        evt = Event(event, position, self.name)
        return evt

    def update(self):
        '''Forward the per-frame update to every active sound in this channel.'''
        for sound in self.sounds:
            sound.update()


class FMod:
    '''Singleton manager for the FMOD Studio system.

    Initialises on first use, registers its update hook with the BGE scene
    pre-draw list, and cleans up on scene removal. Not intended for direct
    use — prefer the module-level helper functions.
    '''
    channels = {'default': Channel('default')}
    studio: fstudio.StudioSystem = None
    listener = None

    @classmethod
    def initialize(cls):
        '''Initialise the FMOD Studio system if it has not been created yet.

        Registers :meth:`update` on the current scene's pre-draw list and
        :meth:`destroy` on the scene's removal callback.

        :returns: The active ``pyfmodex.studio.StudioSystem``.
        '''
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
        '''Set the occlusion ray-cast mask on every channel.

        :param mask: Bitmask applied to occlusion ray-casts.
        '''
        for channel in self.channels.values():
            channel.occlusion_mask = mask

    @classmethod
    def load_bank(cls, path):
        '''Load an FMOD Studio bank file.

        Logs a warning if the bank is already loaded and an error if the file
        does not exist.

        :param path: Absolute path to the ``.bank`` file.
        '''
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
        '''Per-frame update: sync the FMOD listener transform to the active
        camera (or VR headset) and forward updates to all channels.

        Called automatically via the BGE scene pre-draw list.
        '''
        scene = bge.logic.getCurrentScene()
        cls.listener = VR_HEADSET if VR_STATE else scene.active_camera
        studio = cls.studio
        cam = cls.listener
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
        '''Create a new :class:`Channel` with the given name.

        :param name: Unique name for the new channel.
        '''
        cls.channels[name] = Channel(name)

    @classmethod
    def set_channel_parameter(cls, parameter_name, value, channel='default'):
        '''Set a named FMOD Studio parameter on every sound in a channel.

        :param parameter_name: Parameter name string.
        :param value: Target parameter value.
        :param channel: Name of the target :class:`Channel`.
        '''
        if cls.studio is None:
            return
        _channel = cls.channels.get(channel, None)
        if _channel is None:
            error(f'Channel {channel} not found.')
            return
        _channel.set(parameter_name, value)

    @classmethod
    def set_channel_occlusion_mask(cls, mask=65535, channel='default'):
        '''Set the occlusion ray-cast mask on a specific channel.

        :param mask: Bitmask for occlusion ray-casts.
        :param channel: Name of the target :class:`Channel`.
        '''
        _channel = cls.channels.get(channel, None)
        if _channel is None:
            error(f'Channel {channel} not found.')
            return
        _channel.occlusion_mask = mask

    @classmethod
    def destroy(cls):
        '''Release the FMOD Studio system and unregister the update hook.

        Called automatically when the BGE scene is removed.
        '''
        scene = bge.logic.getCurrentScene()
        if cls.update in scene.pre_draw:
            scene.pre_draw.remove(cls.update)
            cls.studio.release()
            cls.studio = None

    @classmethod
    def event(cls, event, source=Vector((0, 0, 0)), channel='default') -> 'Event | EventSpeaker':
        '''Start an FMOD Studio event.

        If *source* is a ``KX_GameObject`` an :class:`EventSpeaker` is created
        so the event tracks the object's transform; otherwise an :class:`Event`
        is placed at the given world position.

        :param event: Event name without the ``event:/`` prefix.
        :param source: ``KX_GameObject`` or world-position tuple/``Vector``.
        :param channel: Name of the :class:`Channel` to register on.
        :returns: :class:`Event` or :class:`EventSpeaker` instance.
        '''
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
        '''Create and start a :class:`File3D` spatial sound.

        :param path: Absolute or relative path to the audio file.
        :param channel: Name of the :class:`Channel` to register on.
        :returns: :class:`File3D` instance, or ``None`` if not initialised.
        '''
        if cls.studio is None:
            return
        _channel = cls.channels.get(channel, None)
        if _channel is None:
            _channel = cls.channels[channel] = Channel(channel)
        return File3D(path, channel)


FMod.initialize()


def load_bank(path):
    '''Load an FMOD Studio bank file.

    :param path: Absolute path to the ``.bank`` file.
    '''
    FMod.load_bank(path)


def start_event(event, source=Vector((0, 0, 0)), channel='default'):
    '''Start an FMOD Studio event.

    :param event: Event name without the ``event:/`` prefix.
    :param source: ``KX_GameObject`` or world-position tuple/``Vector``.
    :param channel: Name of the channel to register on.
    :returns: :class:`Event` or :class:`EventSpeaker` instance.
    '''
    return FMod.event(event, source, channel)


def set_occlusion_mask(mask):
    '''Set the occlusion ray-cast mask on every channel.

    :param mask: Integer bitmask.
    '''
    FMod.set_occlusion_mask(mask)


def set_channel_occlusion_mask(mask):
    '''Set the occlusion ray-cast mask on the default channel.

    :param mask: Integer bitmask.
    '''
    FMod.set_channel_occlusion_mask(mask)


def set_channel_parameter(parameter, value, channel='default'):
    '''Set a named FMOD Studio parameter on every sound in a channel.

    :param parameter: Parameter name string.
    :param value: Target parameter value.
    :param channel: Name of the target channel.
    '''
    FMod.set_channel_parameter(parameter, value, channel)


def add_channel(name):
    '''Create a new named channel in :class:`FMod`.

    :param name: Unique name for the new channel.
    '''
    FMod.add_channel(name)