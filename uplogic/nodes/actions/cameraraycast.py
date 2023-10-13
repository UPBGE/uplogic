from mathutils import Vector
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils.raycasting import raycast_camera, RayCastCameraData
from uplogic.utils import get_bitmask


class ULCameraRayCast(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.camera = None
        self.aim = None
        self.property_name = None
        self.xray = None
        self.mask = get_bitmask(all=True)
        self.distance = None
        self._data = RayCastCameraData((None, None, None))
        self.RESULT = ULOutSocket(self, self.get_result)
        self.PICKED_OBJECT = ULOutSocket(self, self.get_picked_object)
        self.PICKED_POINT = ULOutSocket(self, self.get_picked_point)
        self.PICKED_NORMAL = ULOutSocket(self, self.get_picked_normal)

    def get_result(self):
        return self._data.obj is not None

    def get_picked_object(self):
        return self._data.obj

    def get_picked_point(self):
        return self._data.point

    def get_picked_normal(self):
        return self._data.normal

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        self._data = raycast_camera(
            distance=self.get_input(self.distance),
            prop=self.get_input(self.property_name),
            xray=self.get_input(self.xray),
            aim=self.get_input(self.aim),
            mask=self.get_input(self.mask)
        )
