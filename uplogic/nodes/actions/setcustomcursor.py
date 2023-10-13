from bge import render
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.ui import Cursor, remove_custom_cursor
from bpy.types import Image


class ULSetCustomCursor(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.texture = None
        self.size: list = None
        self.done: bool = None
        self._cursor = None
        self.OUT = ULOutSocket(self, self.get_done)
        self.CURSOR = ULOutSocket(self, self.get_cursor)

    def get_done(self):
        return self.done

    def get_cursor(self):
        return self._cursor

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        remove_custom_cursor()
        texture: Image = self.get_input(self.texture)
        size = self.get_input(self.size)
        self._cursor = Cursor(texture=texture.name, size=size)
        self.done = True
