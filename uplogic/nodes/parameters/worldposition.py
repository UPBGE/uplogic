from uplogic.nodes import ULParameterNode
from uplogic.nodes import ULOutSocket


class ULWorldPosition(ULParameterNode):
    def __init__(self):
        ULParameterNode.__init__(self)
        self.camera = None
        self.screen_x = None
        self.screen_y = None
        self.world_z = None
        self.OUT = ULOutSocket(self, self.get_pos)

    def get_pos(self):
        camera = self.get_input(self.camera)
        screen_x = self.get_input(self.screen_x)
        screen_y = self.get_input(self.screen_y)
        world_z = self.get_input(self.world_z)
        direction = camera.getScreenVect(screen_x, screen_y)
        origin = camera.worldPosition
        aim = direction * -world_z
        point = origin + (aim)
        return point
