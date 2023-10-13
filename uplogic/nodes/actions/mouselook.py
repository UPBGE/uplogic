from bge import render
from bge import logic
from mathutils import Vector
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.input import MouseLook
from math import degrees


class ULMouseLook(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.axis = None
        self.condition = None
        self.game_object_x = None
        self.game_object_y = None
        self.inverted = None
        self.sensitivity = None
        self.use_cap_z = None
        self.cap_z = None
        self.use_cap_y = None
        self.cap_y = None
        self.smooth = None
        self.initialized = False
        self.use_local_head = False
        self._x = 0
        self._y = 0
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)
        self.mouselook = None

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        condition = self.get_input(self.condition)
        if condition:
            obj = self.get_input(self.game_object_x)
            head = self.get_input(self.game_object_y)
            if self.mouselook and self.mouselook.active:
                if (
                    self.mouselook.obj is not obj
                    or
                    self.mouselook.head is not head
                ):
                    self.mouselook.disable()
                    self.mouselook = None
            if self.mouselook is None:
                use_cap_x = self.get_input(self.use_cap_z)
                use_cap_y = self.get_input(self.use_cap_y)
                cap_x = [degrees(x) for x in self.get_input(self.cap_z)] if use_cap_x else None
                cap_y = [degrees(y) for y in self.get_input(self.cap_y)] if use_cap_y else None
                self.mouselook = MouseLook(
                    obj=obj,
                    head=head,
                    sensitivity=self.get_input(self.sensitivity),
                    use_cap_x=use_cap_x,
                    cap_x=cap_x,
                    use_cap_y=use_cap_y,
                    cap_y=cap_y,
                    invert=list(self.get_input(self.inverted).values()),  # XXX: Socket type InvertXY to Dict!
                    smoothing=self.get_input(self.smooth),
                    local=head is not obj,
                    front=self.get_input(self.axis)
                )
        if self.mouselook is not None:
            self.mouselook.active = condition
        self.done = True
