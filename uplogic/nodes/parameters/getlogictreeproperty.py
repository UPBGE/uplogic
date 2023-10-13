from uplogic.nodes import ULOutSocket, ULParameterNode
from uplogic.utils import make_valid_name
from bpy.types import Object


class ULGetLogicTreeProperty(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.property_name = None
        self.OUT = ULOutSocket(self, self.get_property)

    def get_property(self):
        property_name = self.get_input(self.property_name)
        result = getattr(self.network.component, make_valid_name(property_name).lower(), False)
        if isinstance(result, Object):
            result = self.network.scene.getGameObjectFromObject(result)
        return result
