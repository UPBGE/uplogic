from bge import logic
from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode


class ULActiveCamera(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.OUT = ULOutSocket(self, self.get_camera)

    def get_camera(self):
        scene = logic.getCurrentScene()
        return scene.active_camera
