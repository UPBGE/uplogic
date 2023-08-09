from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import is_waiting, make_valid_name
from uplogic.utils import is_invalid
from uplogic.utils import not_met


class ULStartSubNetwork(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.logic_network_name = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def setup(self, network):
        self._network = network

    def evaluate(self):
        self.done = False
        condition = self.get_input(self.condition)
        if not_met(condition):
            return
        game_object = self.get_input(self.game_object)
        logic_network_name = self.get_input(self.logic_network_name)
        if is_waiting(game_object, logic_network_name):
            return
        self._set_ready()
        if is_invalid(game_object):
            return
        tree_name = make_valid_name(logic_network_name)
        network = game_object.get(f'IGNLTree_{tree_name}')
        if network is None:
            network = self._network.install_subnetwork(
                game_object,
                tree_name,
                True
            )
        else:
            if network.stopped:
                network._initialized = False
            network.stopped = False
        self.done = True
