from bge import render
from uplogic.nodes import ULParameterNode


class ULGetFullscreen(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.OUT = self.add_output(self.get_fullscreen)

    def get_fullscreen(self):
        return render.getFullScreen()
