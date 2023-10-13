from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULSetMousePosition(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.screen_x = None
        self.screen_y = None
        self.network = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def setup(self, network):
        self.network = network

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        screen_x = self.get_input(self.screen_x)
        screen_y = self.get_input(self.screen_y)
        self.network.set_mouse_position(screen_x, screen_y)
        self.done = True
