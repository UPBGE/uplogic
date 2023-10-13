from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import make_valid_name


class ULExecuteSubNetwork(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self._condition = None
        self.target_object = None
        self.tree_name = None
        self._network = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def setup(self, network):
        self._network = network

    def evaluate(self):
        self.done = False
        condition = self.get_input(self.condition)
        if condition != self._condition:
            target_object = self.get_input(self.target_object)
            tree_name = self.get_input(self.tree_name)
            tree_name = make_valid_name(tree_name)
            network = target_object.get(f'IGNLTree_{tree_name}', None)
            if network is None:
                network = self._network.install_subnetwork(
                    target_object,
                    tree_name,
                    True
                )
            network.stopped = not condition
            self._condition = condition
            self.done = True
