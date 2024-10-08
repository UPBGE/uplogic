from bge import logic
from uplogic.nodes import ULActionNode


class ULCursorBehavior(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.cursor_object = None
        self.world_z = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        cursor_object = self.get_input(self.cursor_object)
        if not self.get_condition():
            if cursor_object.visible:
                cursor_object.setVisible(False, True)
            return
        camera = logic.getCurrentScene().active_camera
        world_z = self.get_input(self.world_z)
        if not cursor_object.visible:
            cursor_object.setVisible(True, True)
        else:
            x = self.network.mouse.position[0]
            y = self.network.mouse.position[1]
            direction = camera.getScreenVect(x, y)
            origin = camera.worldPosition
            aim = direction * -world_z
            point = origin + aim
            cursor_object.worldOrientation = camera.worldOrientation
            cursor_object.worldPosition = point
        self._done = True
