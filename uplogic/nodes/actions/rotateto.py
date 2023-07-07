from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils.constants import STATUS_WAITING
from uplogic.utils.math import get_local
from uplogic.utils import is_invalid
from uplogic.utils import is_waiting
from uplogic.utils import not_met
from uplogic.utils import rotate_to


class ULActionRotateTo(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.moving_object = None
        self.target_point = None
        self.speed = None
        self._done = False
        self.rot_axis = 2
        self.front_axis = 0
        self.OUT = ULOutSocket(self, self._get_done)

    def _get_done(self):
        return self._done

    def evaluate(self):
        self._done = False
        self._set_value(False)
        condition = self.get_input(self.condition)
        if not_met(condition):
            return
        moving_object = self.get_input(self.moving_object)
        target_point = self.get_input(self.target_point)
        speed = self.get_input(self.speed)
        target_point = getattr(target_point, 'worldPosition', target_point)
        rot_axis = self.get_input(self.rot_axis)
        front_axis = self.get_input(self.front_axis)
        if is_invalid(moving_object):
            return
        if is_waiting(target_point, speed, rot_axis, front_axis):
            return
        self._set_ready()
        aim = get_local(moving_object, target_point)
        rotate_to(rot_axis, moving_object, target_point, front_axis, speed)
        self._done = True
