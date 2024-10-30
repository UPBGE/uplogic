from uplogic.nodes import ULParameterNode
from uplogic.utils import Curve
from mathutils import Vector


class EvaluateCurveNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.curve = None
        self.factor = 0.0
        self._curve = None
        self._factor = None
        self._vec = Vector((0, 0, 0))
        self.VEC = self.add_output(self.get_out_v)

    def get_out_v(self):
        recalc = False
        curve = self.get_input(self.curve)
        if self._curve is None or curve is not self._curve.game_object:
            self._curve = Curve(curve, use_evaluate=True)
            recalc = True
        fac = self.get_input(self.factor)
        if fac != self._factor:
            self._factor = fac
            recalc = True
        if recalc:
            self._vec = self._curve.evaluate(self._factor)
        return self._vec
