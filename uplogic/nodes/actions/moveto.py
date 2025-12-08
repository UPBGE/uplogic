from uplogic.nodes import ULActionNode
from uplogic.utils.objects import move_to


class ULMoveTo(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.moving_object = None
        self.destination_point = None
        self.speed = None
        self.dynamic = None
        self.distance = None
        self._reached = False
        self.OUT = self.add_output(self.get_done)
        self.REACHED = self.add_output(self.get_reached)

    def get_done(self):
        return self._done

    def get_reached(self):
        return self._reached

    def evaluate(self):
        if not self.get_condition():
            return
        moving_object = self.get_input(self.moving_object)
        destination_point = self.get_input(self.destination_point)
        speed = self.get_input(self.speed)
        distance = self.get_input(self.distance)
        dynamic = self.get_input(self.dynamic)
        self._reached = move_to(
            moving_object,
            destination_point,
            speed,
            distance
        )
        self._done = True
