'''TODO: Documentation
'''

from bge import logic
from uplogic.data.globaldb import GlobalDB
from uplogic.input.vr import ULHeadsetVRWrapper
from uplogic.utils import check_vr_session_status
from uplogic.console import warning
from mathutils import Vector
import aud
import bpy


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
    """Set the overall volume of a `AudioSystem`. All sounds played via this
    system will have their volume multiplied by this value.
    """
    aud_sys = get_audio_system(system_name)
    if aud_sys:
        aud_sys.lowpass = frequency


def set_master_volume(volume, system_name='default') -> None:
    """Set the overall volume of a `AudioSystem`. All sounds played via this
    system will have their volume multiplied by this value.
    """
    aud_sys = get_audio_system(system_name)
    if aud_sys:
        aud_sys.volume = volume


def set_vr_audio(flag, system_name='default') -> None:
    """Set the audio mode for a `AudioSystem`. If set to `True`, the system
    will track a VR Headset instead of the active scene camera.
    """
    aud_sys = get_audio_system(system_name)
    if aud_sys:
        aud_sys.use_vr = flag


def stop_all_audio() -> None:
    """Stop every `AudioSystem` in this scene.
    """
    for sys in GlobalDB.retrieve('uplogic.audio'):
        sys.shutdown()


class AudioSystem(object):
    '''System for managing sounds started using `Sound2D` or `Sound3D`.
    
    :param `name`: ID of this AudioSystem; must be unique.
    :param `mode`: Playback mode for sounds of this system, must be one of `['2D', '3D']`
    '''
    _deprecated = False

    def __init__(self, name: str, mode: str = '3D'):
        if self._deprecated:
            warning('Warning: ULAudioSystem class will be renamed to "AudioSystem" in future releases!')
        if mode not in ['2D', '3D']:
            warning(f"AudioSystem argument 'mode': '{mode}' not recognized in ['2D', '3D'], defaulting to '3D'.")
            mode = '3D'
        self._active_sounds = []
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

    @lowpass.setter
    def lowpass(self, val):
        if val == self._lowpass:
            return
        self._lowpass = val
        for sound in self._active_sounds:
            sound.lowpass = val

    @property
    def volume(self):
        '''Playback amplitude multiplier for all sounds played through this system'''
        return self._volume

    @volume.setter
    def volume(self, val):
        self._volume = val
        for sound in self._active_sounds:
            sound.volume = sound.volume

    def pause(self):
        '''Pause all sounds in this system.'''
        for sound in self._active_sounds:
            sound.pause()

    def resume(self):
        '''Resume all sounds in this system.'''
        for sound in self._active_sounds:
            sound.resume()

    def setup(self, scene=None):
        """Get necessary scene data.
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
        """Compare positions of the listener to calculate velocity.
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
        """This is called each frame and updates every sound currently playing.
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
            dev.listener_location = cpos
            dev.listener_orientation = listener.worldOrientation.to_quaternion()
            dev.listener_velocity = listener_vel
        for s in self._active_sounds:
            s.update()

    def add(self, sound):
        '''Add a `ULSound` to this audio system.'''
        self._active_sounds.append(sound)

    def remove(self, sound):
        '''Remove a `ULSound` from this audio system.'''
        self._active_sounds.remove(sound)

    def shutdown(self, a=None):
        '''Stop and remove this audio system. This will stop all sounds playing
        on this system.'''
        self.device.stopAll()
        self.scene.pre_draw.remove(self.update)
        GlobalDB.retrieve('uplogic.audio').remove(self.name)

    def stop_all(self):
        self.device.stopAll()


class ULAudioSystem(AudioSystem):
    _deprecated = True


def get_audio_system(system_name: str = 'default', mode: str = '3D') -> AudioSystem:
    '''Get or create a `AudioSystem` with the given name.

    :param `system_name`: Look for this name.
    :param `mode`: Playback mode of `['2D', '3D']`. Only relevant a new system is created.

    :returns: `AudioSystem`, new system is created if none is found.
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