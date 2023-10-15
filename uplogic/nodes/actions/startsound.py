from uplogic.audio import Sound2D
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from bpy.types import Sound


class ULStartSound(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.sound = None
        self.loop_count = None
        self.pitch = None
        self.volume = None
        self.ignore_timescale = None
        self.done = None
        self.device = None
        self.on_finish = False
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
        pitch = self.get_input(self.pitch)
        volume = self.get_input(self.volume)
        if self._handle:
            self._handle.pitch = pitch
            self._handle.volume = volume
        if not self.get_input(self.condition):
            return
        file: Sound = self.get_input(self.sound)
        loop_count = self.get_input(self.loop_count)
        ignore_timescale = self.get_input(self.ignore_timescale)
        self._handle = Sound2D(
            file.filepath,
            volume,
            pitch,
            loop_count,
            False,
            ignore_timescale,
            'ln_audio_system'
        )
        self.done = True
