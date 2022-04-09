from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import is_waiting
from uplogic.utils import not_met
from uplogic.utils.raycasting import raycast
from uplogic.utils.raycasting import raycast_face


class ULRaycast(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.origin = None
        self.destination = None
        self.local: bool = None
        self.property_name: str = None
        self.material: str = None
        self.exclude: str = None
        self.xray: bool = None
        self.custom_dist: bool = None
        self.distance: float = None
        self.visualize: bool = None
        self._result = None
        self._picked_object = None
        self._point = None
        self._normal = None
        self._direction = None
        self._material = None
        self._uv = None
        self.RESULT = ULOutSocket(self, self.get_result)
        self.PICKED_OBJECT = ULOutSocket(self, self.get_picked_object)
        self.POINT = ULOutSocket(self, self.get_point)
        self.NORMAL = ULOutSocket(self, self.get_normal)
        self.DIRECTION = ULOutSocket(self, self.get_direction)
        self.MATERIAL = ULOutSocket(self, self.get_material)
        self.UV = ULOutSocket(self, self.get_uv)
        self.network = None

    def setup(self, network):
        self.network = network

    def get_result(self):
        return self._result

    def get_picked_object(self):
        return self._picked_object

    def get_point(self):
        return self._point

    def get_normal(self):
        return self._normal

    def get_direction(self):
        return self._direction

    def get_material(self):
        return self._material

    def get_uv(self):
        return self._uv

    def evaluate(self):
        condition = self.get_input(self.condition)
        if not_met(condition):
            self._set_value(False)
            self._normal = None
            self._object = None
            return
        origin = self.get_input(self.origin)
        destination = self.get_input(self.destination)
        local: bool = self.get_input(self.local)
        property_name: str = self.get_input(self.property_name)
        material: str = self.get_input(self.material)
        exclude: str = self.get_input(self.exclude)
        xray: bool = self.get_input(self.xray)
        distance: float = self.get_input(self.distance)
        visualize: bool = self.get_input(self.visualize)

        if is_waiting(origin, destination, local, property_name, distance):
            return
        self._set_ready()
        caster = self.network._owner
        obj, point, normal = None, None, None
        obj, point, normal, direction, face, uv = raycast_face(
            caster,
            origin,
            destination,
            distance if self.get_input(self.custom_dist) else 0,
            property_name,
            material,
            exclude,
            xray,
            local,
            visualize,
        )
        self._result = obj is not None
        self._picked_object = obj
        self._point = point
        self._normal = normal
        self._direction = direction
        self._material = face.material_name[2:] if face else None
        self._uv = uv
