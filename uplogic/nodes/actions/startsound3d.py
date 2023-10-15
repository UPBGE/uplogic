from uplogic.audio import Sound3D
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from mathutils import Vector
from bpy.types import Sound


class ULStartSound3D(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.sound = None
        self.occlusion = False
        self.reverb = False
        self.transition = .1
        self.cutoff = .1
        self.speaker = None
        self.device = None
        self.loop_count = None
        self.pitch = 1.0
        self.volume = 1.0
        self.attenuation = 1.0
        self.distance_ref = 1.0
        self.cone_angle = Vector((360, 360))
        self.cone_outer_volume = 1.0
        self.ignore_timescale = True
        self.done = None
        self.on_finish = False
        self._clear_sound = 1
        self._sustained = 1
        self._handle = None
        self.DONE = ULOutSocket(self, self.get_done)
        self.ON_FINISH = ULOutSocket(self, self.get_on_finish)
        self.HANDLE = ULOutSocket(self, self.get_handle)

    def get_handle(self):
        return self._handle

    def get_on_finish(self):
        if not self._handle:
            return False
        if self._handle.finished:
            return True
        return False

    def get_done(self):
        return self.done
    
    def reset(self):
        super().reset()
        if self._handle and self._handle.finished:
            self._handle = None

    def evaluate(self):
        self.done = False
        self.on_finish = False
        volume = self.get_input(self.volume)
        pitch = self.get_input(self.pitch)
        if self._handle:
            self._handle.volume = volume
            self._handle.pitch = pitch
        if not self.get_input(self.condition):
            return
        speaker = self.get_input(self.speaker)
        transition = self.get_input(self.transition)
        reverb = self.get_input(self.reverb)
        occlusion = self.get_input(self.occlusion)
        cone_outer_volume = self.get_input(self.cone_outer_volume)
        attenuation = self.get_input(self.attenuation)
        cutoff = self.get_input(self.cutoff)
        file: Sound = self.get_input(self.sound)
        loop_count = self.get_input(self.loop_count)
        distance_ref = self.get_input(self.distance_ref)
        cone_angle = self.get_input(self.cone_angle)
        ignore_timescale = self.get_input(self.ignore_timescale)

        self._handle = Sound3D(
            speaker,
            file.filepath,
            occlusion,
            transition,
            cutoff,
            loop_count,
            pitch,
            volume,
            reverb,
            attenuation,
            distance_ref,
            [cone_angle.x, cone_angle.y],
            cone_outer_volume,
            ignore_timescale,
            'ln_audio_system'
        )
        self.done = True
