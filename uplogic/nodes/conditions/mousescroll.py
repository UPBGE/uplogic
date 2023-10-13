from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket


class ULMouseScrolled(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.wheel_direction = 0
        self.OUT = ULOutSocket(self, self.get_wheel)
        self.DIFF = ULOutSocket(self, self.get_diff)

    def get_wheel(self):
        wd = self.wheel_direction
        if wd == 1:  # UP
            return self.network.mouse.wheel > 0
        elif wd == 2:  # DOWN
            return self.network.mouse.wheel < 0
        elif wd == 3:  # UP OR DOWN
            return self.network.mouse.wheel != 0

    def get_diff(self):
        return self.network.mouse.wheel
