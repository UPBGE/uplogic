from bge import logic
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from bpy.types import Collection
from bge.types import KX_Camera

class ULSetOverlayCollection(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.camera = None
        self.collection = None
        self.done = False
        self.OUT = ULOutSocket(self, self.get_out)

    def get_out(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        collection:Collection = self.get_input(self.collection)
        camera: KX_Camera = self.get_input(self.camera)
        logic.getCurrentScene().addOverlayCollection(camera, collection)
        self.done = True
