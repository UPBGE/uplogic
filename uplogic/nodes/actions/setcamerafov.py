from uplogic.nodes import ULActionNode


class ULSetCameraFOV(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.camera = None
        self.fov = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        camera = self.get_input(self.camera)
        fov = self.get_input(self.fov)
        camera.fov = fov
        self._done = True
