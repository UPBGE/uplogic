from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket
from bge import logic


class ULMouseReleased(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.pulse = False
        self.mouse_button_code = None
        self.network = None
        self.OUT = ULOutSocket(self, self.get_changed)

    def get_changed(self):
        mouse_button = self.get_input(self.mouse_button_code)
        mstat = logic.mouse.inputs[mouse_button]
        if self.pulse:
            return (
                    mstat.released or
                    mstat.inactive
                )
        else:
            return (mstat.released)

    def setup(self, network):
        self.network = network
