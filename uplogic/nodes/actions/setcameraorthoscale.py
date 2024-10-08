from uplogic.nodes import ULActionNode


class ULSetCameraOrthoScale(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.camera = None
        self.scale = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        camera = self.get_input(self.camera)
        scale = self.get_input(self.scale)
        camera.ortho_scale = scale
        self._done = True
