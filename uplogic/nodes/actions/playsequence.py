from uplogic.animation.sequence import Sequence
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from bpy.types import Material


class ULPaySequence(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.mat_name = None
        self.node_name = None
        self.play_mode = None
        self.play_continue = None
        self.frames = None
        self.sequence = None
        self.fps = None
        self.ON_START = ULOutSocket(self, self._get_on_start)
        self.RUNNING = ULOutSocket(self, self._get_running)
        self.ON_FINISH = ULOutSocket(self, self._get_on_finish)
        self.FRAME = ULOutSocket(self, self._get_frame)

    def _get_on_start(self):
        return self.on_start

    def _get_running(self):
        return getattr(self.sequence.running, False)

    def _get_on_finish(self):
        return self.on_finish

    def _get_frame(self):
        return self.sequence.frame

    def evaluate(self):
        self.on_finish = False
        self.on_start = False
        condition = self.get_input(self.condition)
        play_continue = self.get_input(self.play_continue)
        if self.sequence:
            if self.sequence.on_finish:
                self.on_finish = True
                if self.sequence.mode < 3:
                    self.sequence = None
        play_mode = self.get_input(self.play_mode)
        frames = self.get_input(self.frames)
        if not condition and play_mode < 2:
            return
        elif not condition and self.sequence:
            if not play_continue:
                self.sequence.restart()
            self.sequence.pause()
        elif condition and self.sequence:
            self.sequence.unpause()
        material: Material = self.get_input(self.mat_name)
        node_name = self.get_input(self.node_name)
        fps = self.get_input(self.fps)
        if not self.sequence:
            if play_mode > 2:
                play_mode -= 3
            self.sequence = Sequence(
                material.name,
                node_name,
                frames.x,
                frames.y,
                fps,
                play_mode
            )
