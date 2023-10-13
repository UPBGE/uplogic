from bge import render
from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULGetVSync(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.OUT = ULOutSocket(self, self.get_vsync)

    def get_vsync(self):
        return render.getVsync()
