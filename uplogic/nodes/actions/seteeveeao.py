from bge import logic
from uplogic.nodes import ULActionNode
import bpy


class ULSetEeveeAO(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.value = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        value = self.get_input(self.value)
        scene = logic.getCurrentScene()
        bpy.data.scenes[scene.name].eevee.use_gtao = value
        self._done = True
