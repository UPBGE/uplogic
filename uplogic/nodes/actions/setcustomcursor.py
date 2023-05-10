from bge import render
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.ui import Cursor, remove_custom_cursor
from uplogic.utils import not_met


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
        condition = self.get_input(self.condition)
        if not_met(condition):
            self._set_ready()
            return
        self._set_ready()
        remove_custom_cursor()
        texture = self.get_input(self.texture)
        size = self.get_input(self.size)
        self._cursor = Cursor(texture=texture, size=size)
        self.done = True
