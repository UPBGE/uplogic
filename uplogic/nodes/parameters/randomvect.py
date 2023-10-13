from mathutils import Vector
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
import random


class ULRandomVect(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.xyz = None
        self.OUT_A = ULOutSocket(self, self._get_output)

    def _get_output(self):
        xyz = self.get_input(self.xyz)
        vmin, vmax = -999999999, 999999999
        delta = vmax - vmin
        x = vmin + (delta * random.random()) if xyz['x'] else 0
        y = vmin + (delta * random.random()) if xyz['y'] else 0
        z = vmin + (delta * random.random()) if xyz['z'] else 0
        return Vector((x, y, z))
