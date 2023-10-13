from bge import logic
from bge.types import KX_GameObject as GameObject
from mathutils import Vector
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
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
        self.DONE = ULOutSocket(self, self.get_done)

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
                    invert=list(self.get_input(self.inverted).values()),
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
        # axis: int = self.get_input(self.axis)
        # if not self.get_input(self.condition):
        #     return
        # main_obj: GameObject = self.get_input(self.main_obj)
        # head_obj: GameObject = self.get_input(self.head_obj)
        # inverted: bool = self.get_input(self.inverted)
        # index: int = self.get_input(self.index)
        # sensitivity: float = self.get_input(self.sensitivity)
        # exponent: float = self.get_input(self.exponent)
        # threshold: float = self.get_input(self.threshold)
        # use_cap_x: Vector = self.get_input(self.use_cap_x)
        # use_cap_y: Vector = self.get_input(self.use_cap_y)
        # if logic.joysticks[index]:
        #     joystick = logic.joysticks[index]
        # else:
        #     return
        # raw_values = joystick.axisValues
        # if axis == 0:
        #     x, y = raw_values[0], raw_values[1]
        # elif axis == 1:
        #     x, y = raw_values[2], raw_values[3]
        # neg_x = -1 if x < 0 else 1
        # neg_y = 1 if y < 0 else -1

        # if -threshold < x < threshold:
        #     x = 0
        # else:
        #     x = abs(x) ** exponent

        # if -threshold < y < threshold:
        #     y = 0
        # else:
        #     y = abs(y) ** exponent
        # if x == y == 0:
        #     self.done = True
        #     return

        # x *= neg_x
        # y *= neg_y

        # x = -x if inverted['x'] else x
        # y = -y if inverted['y'] else y
        # x *= sensitivity
        # if use_cap_x:
        #     cap_x: Vector = self.get_input(self.cap_x)
        #     uppercapX: float = cap_x.x
        #     lowercapX: float = -cap_x.y
        #     objectRotation = main_obj.localOrientation.to_euler()
        #     if objectRotation.z + x > uppercapX:
        #         x = 0
        #         objectRotation.z = uppercapX
        #         main_obj.localOrientation = objectRotation.to_matrix()

        #     if objectRotation.z + x < lowercapX:
        #         x = 0
        #         objectRotation.z = lowercapX
        #         main_obj.localOrientation = objectRotation.to_matrix()

        # y *= sensitivity
        # if use_cap_y:
        #     cap_y: Vector = self.get_input(self.cap_y)
        #     uppercapY: float = cap_y.y
        #     lowercapY: float = cap_y.x
        #     objectRotation = head_obj.localOrientation.to_euler()
        #     if objectRotation.x + y > uppercapY:
        #         y = 0
        #         objectRotation.x = uppercapY
        #         head_obj.localOrientation = objectRotation.to_matrix()

        #     if objectRotation.x + y < lowercapY:
        #         y = 0
        #         objectRotation.x = lowercapY
        #         head_obj.localOrientation = objectRotation.to_matrix()

        # main_obj.applyRotation(Vector((0, 0, x)), True)
        # head_obj.applyRotation(Vector((y, 0, 0)), True)
        # self.done = True
