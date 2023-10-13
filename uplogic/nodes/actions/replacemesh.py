from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from bge.types import KX_GameObject
from bpy.types import Mesh


class ULReplaceMesh(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.target_game_object = None
        self.new_mesh_name = None
        self.use_display = None
        self.use_physics = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        target: KX_GameObject = self.get_input(self.target_game_object)
        mesh: Mesh = self.get_input(self.new_mesh_name)
        display: bool = self.get_input(self.use_display)
        physics: bool = self.get_input(self.use_physics)
        target.replaceMesh(mesh.name, display, physics)
        if physics:
            target.reinstancePhysicsMesh()
        self.done = True
