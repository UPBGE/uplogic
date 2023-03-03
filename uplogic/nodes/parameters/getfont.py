from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import is_invalid
import bpy


class ULGetFont(ULParameterNode):

    def __init__(self):
        ULParameterNode.__init__(self)
        self.font = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        font = self.get_input(self.font)
        if is_invalid(font):
            return
        return bpy.data.fonts[font]

    def evaluate(self):
        self._set_ready()
