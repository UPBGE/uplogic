from bge import logic
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils.scene import SceneLoader
from bpy.types import Scene


class ULLoadScene(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.scene = None
        self.done = False
        self.updated = False
        self.status = 0.0
        self.datatype = ''
        self.item = ''
        self.loader = None
        self.OUT = ULOutSocket(self, self.get_done)
        self.UPDATED = ULOutSocket(self, self.get_updated)
        self.STATUS = ULOutSocket(self, self.get_status)
        self.DATATYPE = ULOutSocket(self, self.get_datatype)
        self.ITEM = ULOutSocket(self, self.get_item)

    def get_status(self):
        return self.status

    def get_datatype(self):
        return self.datatype

    def get_item(self):
        return self.item

    def get_done(self):
        return self.done

    def get_updated(self):
        return self.updated

    def evaluate(self):
        self.done = False
        condition: bool = self.get_input(self.condition)
        scene: Scene = self.get_input(self.scene)
        if condition and self.loader is None:
            self.loader = SceneLoader(scene)
        if self.loader:
            self.updated = True
            self.status = self.loader.status
            self.item = self.loader.item
            self.datatype = self.loader.data
            if self.loader.finished:
                self.done = True
                self.loader = None
        else:
            self.updated = False
