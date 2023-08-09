from uplogic.nodes import ULConditionNode
from uplogic.utils.constants import STATUS_READY


class ULOnInit(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self._set_status(STATUS_READY)

    @property
    def _value(self):
        return not self.network._initialized

    @_value.setter
    def _value(self, val):
        pass

    def evaluate(self):
        self._set_ready()
