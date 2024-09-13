from uplogic.nodes import ULActionNode


class ULInstallSubNetwork(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.target_object = None
        self.tree_name = None
        self.initial_status = None
        self._network = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def setup(self, network):
        self._network = network

    def evaluate(self):
        if not self.get_condition():
            return
        target_object = self.get_input(self.target_object)
        tree_name = self.get_input(self.tree_name)
        initial_status = self.get_input(self.initial_status)
        self._network.install_subnetwork(
            target_object,
            tree_name,
            initial_status
        )
        self._done = True
