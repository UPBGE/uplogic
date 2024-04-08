from mathutils import Vector
from uplogic.nodes import ULParameterNode


class ULMouseData(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
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
        return self.network.mouse.position[1]

    def getmdx(self):
        return self.network.mouse.movement[0]

    def getmdy(self):
        return self.network.mouse.movement[1]

    def getmdwheel(self):
        return self.network.mouse.wheel

    def getmxyz(self):
        return Vector(self.network.mouse.position)

    def getmdxyz(self):
        return Vector(self.network.mouse.movement)
