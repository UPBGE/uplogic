from bge import logic
from uplogic.nodes import ULConditionNode


class ULGamepadActive(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.index = None
        self.out = False
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        index = self.get_input(self.index)
        if logic.joysticks[index]:
            joystick = logic.joysticks[index]
        else:
            return False
        axis_active = False
        for x in joystick.axisValues:
            if x < -.1 or x > .1:
                axis_active = True
                break
        return (
            len(joystick.activeButtons) > 0 or
            axis_active
        )
