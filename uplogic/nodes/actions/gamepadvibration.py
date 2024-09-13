from bge import logic
from uplogic.nodes import ULActionNode


class ULGamepadVibration(ULActionNode):
    def __init__(self, axis=0):
        ULActionNode.__init__(self)
        self.condition = None
        self.index = None
        self.left = None
        self.right = None
        self.time = None
        self.DONE = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        index = self.get_input(self.index)
        left = self.get_input(self.left)
        right = self.get_input(self.right)
        time = self.get_input(self.time)
        if not logic.joysticks[index]:
            return
        joystick = logic.joysticks[index]
        if not joystick.hasVibration:
            print('Joystick at index {} has no vibration!'.format(index))
            return

        joystick.strengthLeft = left
        joystick.strengthRight = right
        joystick.duration = int(round(time * 1000))

        joystick.startVibration()
        self._done = True
