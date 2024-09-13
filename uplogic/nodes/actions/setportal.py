from uplogic.nodes import ULParameterNode
from uplogic.utils.portals import Portals


class SetPortalNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.value = None
        self._portal = None
    
    @property
    def portal(self):
        return self._portal

    @portal.setter
    def portal(self, val):
        self._portal = Portals.get(val)
        self._portal.node = self
