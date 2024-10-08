from bge import logic
from uplogic.nodes import ULActionNode
from uplogic.utils.scene import SceneLoader
from bpy.types import Scene


class ULLoadScene(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.scene = None
        self.updated = False
        self.status = 0.0
        self.datatype = ''
        self.item = ''
        self.loader = None
        self.OUT = self.add_output(self.get_done)
        self.UPDATED = self.add_output(self.get_updated)
        self.STATUS = self.add_output(self.get_status)
        self.DATATYPE = self.add_output(self.get_datatype)
        self.ITEM = self.add_output(self.get_item)

    def get_status(self):
        return self.status

    def get_datatype(self):
        return self.datatype

    def get_item(self):
        return self.item

    def get_done(self):
        return self._done

    def get_updated(self):
        return self.updated

    def evaluate(self):
        condition: bool = self.get_condition()
        scene: Scene = self.get_input(self.scene)
        if condition and self.loader is None:
            self.loader = SceneLoader(scene)
        if self.loader:
            self.updated = True
            self.status = self.loader.status
            self.item = self.loader.item
            self.datatype = self.loader.data
            if self.loader.finished:
                self._done = True
                self.loader = None
        else:
            self.updated = False
