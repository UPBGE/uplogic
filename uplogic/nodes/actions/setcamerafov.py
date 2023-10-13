from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetCameraFOV(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.camera = None
        self.fov = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        camera = self.get_input(self.camera)
        fov = self.get_input(self.fov)
        camera.fov = fov
        self.done = True
