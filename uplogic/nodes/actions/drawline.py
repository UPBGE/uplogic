from bge.render import drawLine
from uplogic.nodes import ULActionNode


class ULDrawLine(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.color = None
        self.from_point = None
        self.to_point = None
        self.OUT = self.add_output(self.get_out)

    def get_out(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        from_point = self.get_input(self.from_point)
        to_point = self.get_input(self.to_point)
        color = self.get_input(self.color)
        drawLine(
            from_point,
            to_point,
            [
                color.x,
                color.y,
                color.z,
                1
            ]
        )
        self._done = True
