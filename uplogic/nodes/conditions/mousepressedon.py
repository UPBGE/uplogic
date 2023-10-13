from bge import logic
from uplogic.nodes import ULConditionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils.raycasting import raycast_mouse


class ULMousePressedOn(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.game_object = None
        self.mouse_button = None
        self.OUT = ULOutSocket(self, self.get_changed)

    def get_changed(self):
        mouse_button = self.get_input(self.mouse_button)
        game_object = self.get_input(self.game_object)
        mstat = logic.mouse.inputs[mouse_button]
        if not mstat.activated:
            return False
        mpos = logic.mouse.position
        camera = logic.getCurrentScene().active_camera
        vec = 10 * camera.getScreenVect(*mpos)
        ray_target = camera.worldPosition - vec
        distance = camera.getDistanceTo(game_object) * 2.0
        dat = raycast_mouse(distance=distance)
        return dat.obj == game_object
