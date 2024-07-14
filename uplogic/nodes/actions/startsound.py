from uplogic.audio import Sound3D, Sound2D, Sample3D, Sample2D
from uplogic.nodes import ULActionNode
from mathutils import Vector


class StartSoundNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = False
        self.sound = None
        self.start_time = 0.0
        self.end_time = 1.0
        # self.position = Vector((0, 0, 0))
        self.occlusion = False
        self.reverb = False
        self.transition = .1
        self.cutoff = .1
        self.speaker = None
        self.device = None
        self.loop_count = None
        self.pitch = 1.0
        self.speed = 1.0
        self.volume = 1.0
        self.lowpass = 1.0
        self.attenuation = 1.0
        self.distance_ref = 1.0
        self.cone_angle = Vector((360, 360))
        self.cone_outer_volume = 1.0
        self.ignore_timescale = True
        self.on_finish = False
        self.mode = 0
        self.update_running = False
        self._clear_sound = 1
        self._sustained = 1
        self._handle = None
        self._done = self.add_output(self.get_done)
        self.ON_FINISH = self.add_output(self.get_on_finish)
        self.HANDLE = self.add_output(self.get_handle)
        self._start = [
            self.start_2D,
            self.start_2D_sample,
            self.start_3D,
            self.start_3D_sample
        ]

    def get_handle(self):
        return self._handle

    def get_on_finish(self):
        if not self._handle:
            return False
        if self._handle.finished:
            return True
        return False

    def get_done(self):
        return self._done
    
    def reset(self):
        super().reset()
        if self._handle and self._handle.finished:
            self._handle = None

    def evaluate(self):
        self.on_finish = False
        volume = self.get_input(self.volume)
        pitch = self.get_input(self.pitch)
        if self._handle and self.update_running:
            self._handle.volume = volume
            self._handle.pitch = pitch
            if hasattr(self._handle, 'lowpass'):
                self._handle.lowpass = self.get_input(self.lowpass) * 20000
        if not self.get_input(self.condition):
            return
        self._start[self.mode](volume, pitch)
        self._done = True

    def start_2D(self, volume, pitch):
        self._handle = Sound2D(
            file=self.get_input(self.sound).filepath,
            volume=volume,
            pitch=pitch,
            loop_count=self.get_input(self.loop_count),
            lowpass=self.get_input(self.lowpass) * 20000,
            ignore_timescale=self.get_input(self.ignore_timescale),
            aud_sys='ln_audio_system'
        )

    def start_2D_sample(self, volume, pitch):
        start = self.get_input(self.start_time)
        end = self.get_input(self.end_time)
        self._handle = Sample2D(
            file=self.get_input(self.sound).filepath,
            sample=(start, end),
            volume=volume,
            pitch=pitch,
            loop_count=self.get_input(self.loop_count),
            lowpass=self.get_input(self.lowpass) * 20000,
            ignore_timescale=self.get_input(self.ignore_timescale),
            aud_sys='ln_audio_system'
        )

    def start_3D(self, volume, pitch):
        self._handle = Sound3D(
            speaker=self.get_input(self.speaker),
            file=self.get_input(self.sound).filepath,
            occlusion=self.get_input(self.occlusion),
            transition_speed=self.get_input(self.transition),
            cutoff_frequency=self.get_input(self.cutoff),
            loop_count=self.get_input(self.loop_count),
            pitch=pitch,
            volume=volume,
            reverb=self.get_input(self.reverb),
            attenuation=self.get_input(self.attenuation),
            distance_ref=self.get_input(self.distance_ref),
            cone_angle=self.get_input(self.cone_angle),
            cone_outer_volume=self.get_input(self.cone_outer_volume),
            ignore_timescale=self.get_input(self.ignore_timescale),
            aud_sys='ln_audio_system'
        )

    def start_3D_sample(self, volume, pitch):
        start = self.get_input(self.start_time)
        end = self.get_input(self.end_time)
        self._handle = Sample3D(
            speaker=self.get_input(self.speaker),
            file=self.get_input(self.sound).filepath,
            sample=(start, end),
            occlusion=self.get_input(self.occlusion),
            transition_speed=self.get_input(self.transition),
            cutoff_frequency=self.get_input(self.cutoff),
            loop_count=self.get_input(self.loop_count),
            pitch=pitch,
            volume=volume,
            reverb=self.get_input(self.reverb),
            attenuation=self.get_input(self.attenuation),
            distance_ref=self.get_input(self.distance_ref),
            cone_angle=self.get_input(self.cone_angle),
            cone_outer_volume=self.get_input(self.cone_outer_volume),
            ignore_timescale=self.get_input(self.ignore_timescale),
            aud_sys='ln_audio_system'
        )
