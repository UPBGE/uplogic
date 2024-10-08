from bge import logic
from uplogic.nodes import ULActionNode
from uplogic.utils.objects import add_object


class ULAddObject(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.name = None
        self.reference = None
        self.life = None
        self.full_copy = False
        self.obj = False
        self.OBJ = self.add_output(self._get_obj)
        self.OUT = self.add_output(self._get_done)

    def _get_done(self):
        return self._done

    def _get_obj(self):
        return self.obj

    def evaluate(self):
        condition = self.get_condition()
        if not condition:
            return
        life = self.get_input(self.life)
        name = self.get_input(self.name)
        full_copy = self.get_input(self.full_copy)
        reference = self.get_input(self.reference)
        scene = logic.getCurrentScene()
        # self.obj = scene.addObject(name, reference, life, full_copy)
        self.obj = add_object(name, reference, life, full_copy)
        self._done = True
