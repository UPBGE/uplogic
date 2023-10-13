from bge import logic
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket


class ULAddObject(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.name = None
        self.reference = None
        self.life = None
        self.full_copy = False
        self.done = False
        self.obj = False
        self.OBJ = ULOutSocket(self, self._get_obj)
        self.OUT = ULOutSocket(self, self._get_done)

    def _get_done(self):
        return self.done

    def _get_obj(self):
        return self.obj

    def evaluate(self):
        self.done = False
        condition = self.get_input(self.condition)
        if not condition:
            return
        life = self.get_input(self.life)
        name = self.get_input(self.name)
        full_copy = self.get_input(self.full_copy)
        reference = self.get_input(self.reference)
        scene = logic.getCurrentScene()
        self.obj = scene.addObject(name, reference, life, full_copy)
        self.done = True
