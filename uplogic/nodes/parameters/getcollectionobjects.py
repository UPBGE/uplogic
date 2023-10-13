from uplogic.nodes import ULOutSocket
from uplogic.nodes import ULParameterNode
from bpy.types import Collection
from bge.logic import getCurrentScene


class ULGetCollectionObjects(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.collection = None
        self.OUT = ULOutSocket(self, self.get_objects)

    def get_objects(self):
        collection: Collection = self.get_input(self.collection)
        scene = getCurrentScene()
        return [scene.getGameObjectFromObject(o) for o in collection.objects]
