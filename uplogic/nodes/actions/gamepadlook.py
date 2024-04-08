from bge import logic
from bge.types import KX_GameObject as GameObject
from mathutils import Vector
from uplogic.nodes import ULActionNode
from uplogic.input.gamepad import GamepadLook
from math import degrees


class ULGamepadLook(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.axis: int = 0
        self.condition = None
        self.main_obj: GameObject = None
        self.head_obj: GameObject = None
        self.inverted: bool = None
        self.index: int = None
        self.sensitivity: float = None
        self.exponent: float = None
        self.use_cap_x: bool = None
        self.cap_x: Vector = None
        self.use_cap_y: bool = None
        self.cap_y: Vector = None
        self.threshold: float = None
        self.gamepadlook: GamepadLook = None
        self.done: bool = None
        self.DONE = self.add_output(self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        condition = self.get_input(self.condition)
        if condition:
            obj = self.get_input(self.main_obj)
            head = self.get_input(self.head_obj)
            if self.gamepadlook and self.gamepadlook.active:
                if (
                    self.gamepadlook.obj is not obj
                    or
                    self.gamepadlook.head is not head
                ):
                    self.gamepadlook.disable()
                    self.gamepadlook = None
            if self.gamepadlook is None:
                use_cap_x = self.get_input(self.use_cap_x)
                use_cap_y = self.get_input(self.use_cap_y)
                cap_x = [degrees(x) for x in self.get_input(self.cap_x)] if use_cap_x else None
                cap_y = [degrees(y) for y in self.get_input(self.cap_y)] if use_cap_y else None
                self.gamepadlook = GamepadLook(
                    obj=obj,
                    head=head,
                    sensitivity=self.get_input(self.sensitivity),
                    use_cap_x=use_cap_x,
                    cap_x=cap_x,
                    use_cap_y=use_cap_y,
                    cap_y=cap_y,
                    invert=self.get_input(self.inverted),
                    smoothing=0.0,
                    local=head is not obj,
                    front=self.get_input(self.axis),
                    idx=self.get_input(self.index),
                    stick='RS' if self.axis else 'LS',
                    threshold=self.get_input(self.threshold),
                    exponent=self.get_input(self.exponent)
                )
        if self.gamepadlook is not None:
            self.gamepadlook.active = condition
        self.done = True