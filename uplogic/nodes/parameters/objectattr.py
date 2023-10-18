from mathutils import Vector
from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket


class ULObjectAttribute(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.attribute_name = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        game_object = self.get_input(self.game_object)
        attribute_name = self.get_input(self.attribute_name)
        if not hasattr(game_object, attribute_name):
            return Vector((0, 0, 0))
        val = getattr(game_object, attribute_name)
        return val.copy() if isinstance(val, Vector) else val
