'''Audio device management for uplogic.

Wraps the BGE ``aud.Device`` into a scene-aware :class:`AudioSystem` that
tracks the active camera (or a VR headset) as the 3-D listener, manages
reverb volumes, and applies a master volume and lowpass filter to all active
sounds. Module-level helpers provide convenient one-call access.
'''

from bge import logic
from uplogic.data.globaldb import GlobalDB
from uplogic.input.vr import ULHeadsetVRWrapper
from uplogic.utils import check_vr_session_status
from uplogic.console import warning
from mathutils import Vector
import aud
import bpy


class AudioCache:
    '''Global in-memory cache for decoded ``aud.Sound`` objects.

    Avoids reloading the same file from disk when multiple sounds reference
    the same path.
    '''
    _sounds = {}

    @classmethod
    def get(cls, key, default=None):
        '''Return the cached sound for *key*, or *default* if not cached.

        :param key: File path used as the cache key.
        :param default: Value to return when the key is absent.
        :returns: Cached ``aud.Sound`` or *default*.
        '''
        return cls._sounds.get(key, default)


DISTANCE_MODELS = {
    'EXPONENT': aud.DISTANCE_MODEL_EXPONENT,
    'EXPONENT_CLAMPED': aud.DISTANCE_MODEL_EXPONENT_CLAMPED,
    'INVERSE': aud.DISTANCE_MODEL_INVERSE,
    'INVERSE_CLAMPED': aud.DISTANCE_MODEL_INVERSE_CLAMPED,
    'LINEAR': aud.DISTANCE_MODEL_LINEAR,
    'LINEAR_CLAMPED': aud.DISTANCE_MODEL_LINEAR_CLAMPED,
    'NONE': aud.DISTANCE_MODEL_INVALID
}


def set_lowpass(frequency, system_name='default') -> None:
    """Set the lowpass filter cutoff frequency on an :class:`AudioSystem`.

    All sounds currently playing through the system will have their lowpass
    value updated immediately.

    :param frequency: Cutoff frequency as a factor of 20 000 Hz.
    :param system_name: Name of the target :class:`AudioSystem`.
    """
    aud_sys = get_audio_system(system_name)
    if aud_sys:
        aud_sys.lowpass = frequency


def set_master_volume(volume, system_name='default') -> None:
    """Set the master volume of an :class:`AudioSystem`.

    All sounds played through the system will have their amplitude multiplied
    by this value.

    :param volume: Master amplitude multiplier (``1.0`` = unity gain).
    :param system_name: Name of the target :class:`AudioSystem`.
    """
    aud_sys = get_audio_system(system_name)
    if aud_sys:
        aud_sys.volume = volume


def set_vr_audio(flag, system_name='default') -> None:
    """Toggle VR listener mode on an :class:`AudioSystem`.

    When *flag* is ``True`` the system tracks the VR headset position and
    orientation instead of the active scene camera.

    :param flag: ``True`` to use the VR headset as the listener.
    :param system_name: Name of the target :class:`AudioSystem`.
    """
    aud_sys = get_audio_system(system_name)
    if aud_sys:
        aud_sys.use_vr = flag


def stop_all_audio() -> None:
    """Shut down every :class:`AudioSystem` registered in the current scene,
    stopping all sounds immediately.
    """
    for sys in GlobalDB.retrieve('uplogic.audio'):
        sys.shutdown()


class AudioSystem(object):
    '''System for managing sounds started using :class:`Sound2D` or :class:`Sound3D`.

    :param name: Unique identifier for this system.
    :param mode: Playback mode; must be one of ``['2D', '3D']``.
    '''
    _deprecated = False

    def __init__(self, name: str, mode: str = '3D'):
        if self._deprecated:
            warning('Warning: ULAudioSystem class will be renamed to "AudioSystem" in future releases!')
        if mode not in ['2D', '3D']:
            warning(f"AudioSystem argument 'mode': '{mode}' not recognized in ['2D', '3D'], defaulting to '3D'.")
            mode = '3D'
        self._active_sounds = []
        self._cached_sounds = {}
        self.name = name
        self.mode = mode
        self.bounces = 0
        self.volume = 1.0
        self.reverb = False
        self._lowpass = False
        self.device = aud.Device()
        self.device.distance_model = DISTANCE_MODELS[bpy.context.scene.audio_distance_model]
        self.device.speed_of_sound = bpy.context.scene.audio_doppler_speed
        self.device.doppler_factor = bpy.context.scene.audio_doppler_factor
        self._reverb_volumes = []
        self.scene = logic.getCurrentScene()
        self.use_vr = getattr(bpy.data.scenes[self.scene.name], 'use_vr_audio_space', False)
        self.vr_headset = ULHeadsetVRWrapper() if check_vr_session_status() else None
        self.listener = self.vr_headset if self.use_vr else self.scene.active_camera
        self._old_listener_pos = self.listener.worldPosition.copy()
        self.setup(self.scene)
        self.scene.onRemove.append(self.shutdown)

    @property
    def lowpass(self):
        '''Frequency cutoff for muffled sounds.'''
        return self._lowpass

    @property
    def listener_location(self):
        '''World position of the audio listener (camera or VR headset).'''
        return self.device.listener_location

    @listener_location.setter
    def listener_location(self, val):
        self.device.listener_location = val

    @property
    def listener_orientation(self):
        '''Quaternion orientation of the audio listener.'''
        return self.device.listener_orientation

    @listener_orientation.setter
    def listener_orientation(self, val):
        self.device.listener_orientation = val

    @property
    def listener_velocity(self):
        '''World-space velocity of the audio listener, used for Doppler.'''
        return self.device.listener_velocity

    @listener_velocity.setter
    def listener_velocity(self, val):
        self.device.listener_velocity = val

    @lowpass.setter
    def lowpass(self, val):
        if val == self._lowpass:
            return
        self._lowpass = val
        for sound in self._active_sounds:
            sound.lowpass = val

    @property
    def volume(self):
        '''Playback amplitude multiplier for all sounds played through this system.'''
        return self._volume

    @volume.setter
    def volume(self, val):
        self._volume = val
        for sound in self._active_sounds:
            sound.volume = sound.volume  # noqa

    def cache(self, sound):
        '''Store *sound*'s decoded data in the global :class:`AudioCache`.

        :param sound: :class:`~uplogic.audio.sound.ULSound` whose ``soundfile``
            should be cached under its ``file`` path.
        '''
        AudioCache._sounds[sound.file] = sound.soundfile

    def uncache(self, sound):
        '''Remove *sound* from the global :class:`AudioCache` if present.

        :param sound: :class:`~uplogic.audio.sound.ULSound` to evict.
        '''
        if sound.file in self._cached_sounds.keys():
            del AudioCache._sounds[sound.file]

    def pause(self):
        '''Pause all sounds in this system.'''
        for sound in self._active_sounds:
            sound.pause()

    def resume(self):
        '''Resume all sounds in this system.'''
        for sound in self._active_sounds:
            sound.resume()

    def setup(self, scene=None):
        """Bind this system to *scene*, collect reverb volumes, and register
        the per-frame update hook.

        :param scene: BGE scene to bind to; defaults to the current scene.
        """
        if scene is None:
            self.scene = logic.getCurrentScene()
        else:
            self.scene = scene
        for obj in self.scene.objects:
            if getattr(obj.blenderObject, 'reverb_volume', False) and not obj.blenderObject.data:
                self._reverb_volumes.append(obj)
        self.reverb = len(self._reverb_volumes) > 0
        GlobalDB.retrieve('uplogic.audio').put(self.name, self)
        self.scene.pre_draw.append(self.update)

    def compute_listener_velocity(self, listener) -> Vector:
        """Estimate the listener's velocity from its position delta since the
        last frame, scaled to approximate units per second.

        :param listener: Object with a ``worldPosition`` attribute.
        :returns: ``mathutils.Vector`` velocity estimate.
        """
        wpos = listener.worldPosition.copy()
        olp = self._old_listener_pos
        vel = Vector((
            (wpos.x - olp.x) * 50,
            (wpos.y - olp.y) * 50,
            (wpos.z - olp.z) * 50
        ))
        self._old_listener_pos = wpos
        return vel

    def update(self):
        """Per-frame update: sync the 3-D listener transform and forward the
        update call to every active sound.

        In ``'3D'`` mode the listener position, orientation, and velocity are
        pushed to the ``aud.Device`` each tick. Reverb volumes are evaluated
        to set the ``reverb`` flag. Called automatically via the scene
        pre-draw list.
        """
        if self.mode == '3D':
            scene = logic.getCurrentScene()
            if scene is not self.scene:
                self.setup(scene)
            listener = self.vr_headset if self.use_vr else scene.active_camera
            self.reverb = False
            same_cam = listener is self.listener
            if not self.use_vr:
                self.listener = listener
            if not self._active_sounds:
                return  # do not update if no sound has been installed
            # update the listener data
            cpos = listener.worldPosition
            distances = {}
            if self._reverb_volumes:
                for obj in self._reverb_volumes:
                    dist = (obj.worldPosition - cpos).length
                    if dist > 50:
                        continue
                    else:
                        distances[dist] = obj
                if distances:
                    min_dist = distances[min(distances.keys())]
                    obj = min_dist
                    ob = obj.blenderObject
                    r = ob.empty_display_size
                    wpos = obj.worldPosition
                    sca = ob.scale
                    in_range = (
                        wpos.x - r*sca.x < cpos.x < wpos.x + r*sca.x and
                        wpos.y - r*sca.y < cpos.y < wpos.y + r*sca.y and
                        wpos.z - r*sca.z < cpos.z < wpos.z + r*sca.z
                    )
                    if in_range:
                        self.reverb = True
                        self.bounces = ob.reverb_samples
            listener_vel = (0, 0, 0) if self.use_vr or not same_cam else self.compute_listener_velocity(listener)
            dev = self.device
            self.listener_location = cpos
            self.listener_orientation = listener.worldOrientation.to_quaternion()
            self.listener_velocity = listener_vel
        for s in self._active_sounds:
            s.update()

    def add(self, sound):
        '''Add a :class:`~uplogic.audio.sound.ULSound` to this audio system.

        :param sound: Sound instance to register.
        '''
        self._active_sounds.append(sound)

    def remove(self, sound):
        '''Remove a :class:`~uplogic.audio.sound.ULSound` from this audio system.

        :param sound: Sound instance to deregister.
        '''
        self._active_sounds.remove(sound)

    def shutdown(self, a=None):
        '''Stop all sounds and remove this system from the scene.'''
        self.device.stopAll()
        # for sound in self._cached_sounds.copy():
        #     self.uncache(sound)
        self.scene.pre_draw.remove(self.update)
        GlobalDB.retrieve('uplogic.audio').remove(self.name)

    def stop_all(self):
        '''Stop all sounds on the underlying ``aud.Device`` immediately.'''
        self.device.stopAll()


class ULAudioSystem(AudioSystem):
    '''[DEPRECATED] Use :class:`AudioSystem` instead.'''
    _deprecated = True


def get_audio_system(system_name: str = 'default', mode: str = '3D') -> AudioSystem:
    '''Get or create an :class:`AudioSystem` with the given name.

    :param system_name: Name of the system to look up.
    :param mode: Playback mode (``'2D'`` or ``'3D'``); only used when a new
        system is created.
    :returns: Existing or newly created :class:`AudioSystem`.
    '''
    scene = logic.getCurrentScene()
    aud_systems = GlobalDB.retrieve('uplogic.audio')
    if aud_systems.check(system_name):
        aud_sys = aud_systems.get(system_name)
    else:
        aud_sys = AudioSystem(system_name, mode)
    if aud_sys.update not in scene.pre_draw:
        scene.pre_draw.append(aud_sys.update)
    return aud_sys