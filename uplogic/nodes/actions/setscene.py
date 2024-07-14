from uplogic.nodes import ULActionNode
from bge import logic
from bpy.types import Scene


class ULSetScene(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.scene = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        scene: Scene = self.get_input(self.scene)
        logic.getCurrentScene().replace(scene.name)
        self._done = True
