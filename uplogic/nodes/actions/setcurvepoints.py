from uplogic.nodes import ULActionNode


class ULSetCurvePoints(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.curve_object = None
        self.points: list = None
        self._done: bool = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        curve_object = self.get_input(self.curve_object)
        points = self.get_input(self.points)
        if not points:
            return
        curve = curve_object.blenderObject.data
        for spline in curve.splines:
            curve.splines.remove(spline)
        spline = curve.splines.new('NURBS')
        pos = curve_object.worldPosition
        spline.points.add(len(points))
        for p, new_co in zip(spline.points, points):
            p.co = ([
                new_co.x - pos.x,
                new_co.y - pos.y,
                new_co.z - pos.z
            ] + [1.0])
        self._done = True
