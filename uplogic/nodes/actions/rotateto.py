from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import STATUS_WAITING, is_invalid
from uplogic.utils import is_waiting
from uplogic.utils import get_local
from uplogic.utils import not_met


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
        if front_axis > 2:
            speed = -speed
            front_axis -= 3
        if rot_axis == front_axis:
            return
        if rot_axis == 0:
            aim = aim.yz.normalized()
            rot = -aim.x if front_axis == 2 else aim.y
            moving_object.applyRotation((rot * speed, 0, 0), True)
        elif rot_axis == 1:
            aim = aim.xz.normalized()
            rot = aim.x if front_axis == 2 else -aim.y
            moving_object.applyRotation((0, rot * speed, 0), True)
        elif rot_axis == 2:
            aim = aim.xy.normalized()
            rot = -aim.x if front_axis == 1 else aim.y
            moving_object.applyRotation((0, 0, rot * speed), True)
        self._done = True
