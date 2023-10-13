from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket


class ULLogicTreeStatus(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.game_object = None
        self.tree_name = None
        self._running = False
        self._stopped = False
        self.tree = None
        self.IFRUNNING = ULOutSocket(self, self.get_running)
        self.IFSTOPPED = ULOutSocket(self, self.get_stopped)

    def get_running(self):
        tree = self.tree
        if not tree:
            return False
        return tree.is_running()

    def get_stopped(self):
        tree = self.tree
        if not tree:
            return False
        return tree.is_stopped()

    def evaluate(self):
        game_object = self.get_input(self.game_object)
        tree_name = self.get_input(self.tree_name)
        self._running = False
        self._stopped = False
        self.tree = game_object.get(f'IGNLTree_{tree_name}')
