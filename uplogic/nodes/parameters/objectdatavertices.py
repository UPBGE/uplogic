from mathutils import Vector
from uplogic.nodes import ULParameterNode


class ULObjectDataVertices(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.game_object = None
        self.OUT = self.add_output(self.get_data)

    def get_data(self):
        obj = self.get_input(self.game_object)
        offset = obj.worldPosition
        return sorted(
            [Vector(v.co) + offset for v in (
                obj
                .blenderObject
                .data
                .vertices
            )]
        )
