from uplogic.nodes import ULActionNode
from uplogic.utils.raycasting import raycast, RayCastData
from uplogic.utils.math import get_bitmask
from bge.logic import getCurrentScene
from bpy.types import Material


class ULRaycast(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = False
        self.caster = None
        self.origin = None
        self.destination = None
        self.local: bool = None
        self.property_name: str = None
        self.material: str = None
        self.exclude: str = None
        self.xray: bool = None
        self.custom_dist: bool = None
        self.distance: float = None
        self.mask: int = get_bitmask(all=True)
        self.visualize: bool = None
        self._data = RayCastData((None, None, None, None, None, None))
        self.face_data = False
        self.RESULT = self.add_output(self.get_result)
        self.PICKED_OBJECT = self.add_output(self.get_picked_object)
        self.POINT = self.add_output(self.get_point)
        self.NORMAL = self.add_output(self.get_normal)
        self.DIRECTION = self.add_output(self.get_direction)
        self.MATERIAL = self.add_output(self.get_material)
        self.UV = self.add_output(self.get_uv)
        self.network = None

    def setup(self, network):
        self.network = network

    def get_result(self):
        return self._data.obj is not None

    def get_picked_object(self):
        return self._data.obj

    def get_point(self):
        return self._data.point

    def get_normal(self):
        return self._data.normal

    def get_direction(self):
        return self._data.direction

    def get_material(self):
        return self._data.face.material if self._data.face else None

    def get_uv(self):
        return self._data.uv

    def evaluate(self):
        condition = self.get_condition()
        if not condition:
            self._data = RayCastData((None, None, None, None, None, None))
            return
        origin = self.get_input(self.origin)
        caster = self.get_input(self.caster)
        destination = self.get_input(self.destination)
        local: bool = self.get_input(self.local)
        property_name: str = self.get_input(self.property_name)
        material: Material = self.get_input(self.material)
        exclude: str = self.get_input(self.exclude)
        xray: bool = self.get_input(self.xray)
        distance: float = self.get_input(self.distance)
        visualize: bool = self.get_input(self.visualize)
        self._data = raycast(
            caster,
            origin,
            destination,
            distance=distance if self.get_input(self.custom_dist) else 0,
            prop=property_name,
            material=material.name if material else '',
            exclude=exclude,
            xray=xray,
            local=local,
            mask=self.get_input(self.mask),
            visualize=visualize,
            face_data=self.face_data
        )
