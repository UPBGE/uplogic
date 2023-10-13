from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import make_valid_name


class ULStopSubNetwork(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.logic_network_name = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        logic_network_name = self.get_input(self.logic_network_name)
        tree_name = make_valid_name(logic_network_name)
        network = game_object.get(f'IGNLTree_{tree_name}')
        if network is None:
            return
        network.stop()
        self.done = True
