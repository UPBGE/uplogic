from uplogic.nodes import ULActionNode
from uplogic.utils import rotate_to


class ULActionRotateTo(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.moving_object = None
        self.target_point = None
        self.speed = None
        self.rot_axis = 2
        self.front_axis = 0
        self.OUT = self.add_output(self._get_done)

    def _get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        moving_object = self.get_input(self.moving_object)
        target_point = self.get_input(self.target_point)
        speed = self.get_input(self.speed)
        rot_axis = self.get_input(self.rot_axis)
        front_axis = self.get_input(self.front_axis)
        rotate_to(moving_object, target_point, rot_axis, front_axis, speed)
