from uplogic.nodes import ULActionNode, ULOutSocket
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
        self.done = False
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        moving_object = self.get_input(self.moving_object)
        destination_point = self.get_input(self.destination_point)
        speed = self.get_input(self.speed)
        distance = self.get_input(self.distance)
        dynamic = self.get_input(self.dynamic)
        move_to(
            moving_object,
            destination_point,
            speed,
            self.network.time_per_frame,
            dynamic,
            distance
        )
        self.done = True
