from uplogic.nodes import ULParameterNode
from uplogic.utils.portals import Portals


class GetPortalNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.VAL = self.add_output(self.get_value)
        self._portal = None
    
    @property
    def portal(self):
        return self._portal

    @portal.setter
    def portal(self, val):
        self._portal = Portals.get(val)

    def get_value(self):
        node = self.portal.node
        if node:
            return node.get_input(node.value)
        return None
