from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from bpy.types import Collection


class ULGetCollectionObjectNames(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.condition = None
        self.collection = None
        self.OUT = ULOutSocket(self, self.get_objects)

    def get_objects(self):
        collection: Collection = self.get_input(self.collection)
        return [o.name for o in collection.objects]
