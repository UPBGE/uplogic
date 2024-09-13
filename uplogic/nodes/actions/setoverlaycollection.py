from bge import logic
from uplogic.nodes import ULActionNode
from bpy.types import Collection
from bge.types import KX_Camera

class ULSetOverlayCollection(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.camera = None
        self.collection = None
        self.OUT = self.add_output(self.get_out)

    def get_out(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        collection:Collection = self.get_input(self.collection)
        camera: KX_Camera = self.get_input(self.camera)
        logic.getCurrentScene().addOverlayCollection(camera, collection)
        self._done = True
