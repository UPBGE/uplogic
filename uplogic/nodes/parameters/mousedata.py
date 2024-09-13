from mathutils import Vector
from uplogic.nodes import ULParameterNode


class ULMouseData(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.invert_y = False
        self.MX = self.add_output(self.getmx)
        self.MY = self.add_output(self.getmy)
        self.MDX = self.add_output(self.getmdx)
        self.MDY = self.add_output(self.getmdy)
        self.MDWHEEL = self.add_output(self.getmdwheel)
        self.MXY0 = self.add_output(self.getmxyz)
        self.MDXY0 = self.add_output(self.getmdxyz)

    def getmx(self):
        return self.network.mouse.position[0]

    def getmy(self):
        y = self.network.mouse.position[1]
        return (
            1-y if self.invert_y else y
        )

    def getmdx(self):
        return self.network.mouse.movement[0]

    def getmdy(self):
        y = self.network.mouse.movement[1]
        return (
            -y if self.invert_y else y
        )

    def getmdwheel(self):
        return self.network.mouse.wheel

    def getmxyz(self):
        pos = self.network.mouse.position
        y = pos[1]
        return Vector((
            pos[0],
            1 - y if self.invert_y else y,
        ))

    def getmdxyz(self):
        movement = self.network.mouse.movement
        y = movement[1]
        return Vector((
            movement[0],
            -y if self.invert_y else y,
        ))
