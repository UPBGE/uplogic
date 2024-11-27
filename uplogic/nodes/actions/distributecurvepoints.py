from uplogic.nodes import ULActionNode
from uplogic.utils.objects import Curve
from uplogic.utils import draw_cube


class DistributeCurvePointsNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = False
        self.curve = None
        self.debug = False
        self.custom_density = False
        self.density = 1
        self._curve = None
        self._points = None
        self.DONE = self.add_output(self.get_done)
        self.POINTS = self.add_output(self.get_points)

    def get_done(self):
        return self._done

    def get_points(self):
        return self._points

    def distribute_points(self):
        len_points = max(len(self._curve.points), 1)
        res = self.density if self.custom_density else self._curve.resolution * len_points
        fac = 1 / (res)
        return [self._curve.evaluate(x * fac) for x in range(res + 1)]

    def evaluate(self):
        if self.get_condition() or self._curve is None:
            self._curve = Curve(self.get_input(self.curve), use_evaluate=True)
            self._points = self.distribute_points()
            self._done = True
        if self.debug:
            for x in self._points:
                draw_cube(x, centered=True, width=.2)
