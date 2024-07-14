from uplogic.nodes import ULParameterNode
from bge.logic import getCurrentScene


class GetObjectByNameNode(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.object_name = None
        self.GAME_OBJECT = self.add_output(self.get_object)

    def get_object(self):
        object_name: str = self.get_input(self.object_name)
        return getCurrentScene().objects.get(object_name, None)

    def evaluate(self):
        pass
