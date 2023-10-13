from bge import logic
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import get_bitmask
from uplogic.utils.raycasting import raycast_mouse, RayCastData


class ULMouseRayCast(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.distance = None
        self.property = None
        self.xray = None
        self.camera = None
        self.mask = get_bitmask(all=True)
        self._out_object = None
        self._out_normal = None
        self._out_point = None
        self._data = RayCastData((None, None, None, None, None, None))
        self.RESULT = ULOutSocket(self, self.get_result)
        self.OUTOBJECT = ULOutSocket(self, self.get_out_object)
        self.OUTNORMAL = ULOutSocket(self, self.get_out_normal)
        self.OUTPOINT = ULOutSocket(self, self.get_out_point)

    def get_result(self):
        return self._data.obj is not None

    def get_out_object(self):
        return self._data.obj

    def get_out_normal(self):
        return self._data.normal

    def get_out_point(self):
        return self._data.point

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        self._data = raycast_mouse(
            distance=self.get_input(self.distance),
            prop=self.get_input(self.property),
            xray=self.get_input(self.xray),
            mask=self.get_input(self.mask)

        )
