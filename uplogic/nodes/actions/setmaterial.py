from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import debug
from bpy.types import Material
from bge.types import KX_GameObject


class ULSetMaterial(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.slot = None
        self.mat_name = None
        self.done = False
        self.OUT = ULOutSocket(self, self._get_done)

    def _get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        game_object: KX_GameObject = self.get_input(self.game_object)
        slot: int = self.get_input(self.slot)
        material: Material = self.get_input(self.mat_name)
        bl_obj = game_object.blenderObject
        if slot > len(bl_obj.material_slots) - 1:
            debug('Set Material: Slot does not exist!')
            return
        bl_obj.material_slots[slot].material = material
        self.done = True
