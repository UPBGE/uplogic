from bge import logic
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
import bpy


class ULSetEeveeBloom(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.value = None
        self.done = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        value = self.get_input(self.value)
        scene = logic.getCurrentScene()
        bpy.data.scenes[scene.name].eevee.use_bloom = value
        self.done = True
