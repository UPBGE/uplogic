from bge import logic
from bge import render
from mathutils import Vector
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import get_bitmask
from uplogic.utils.raycasting import raycast_projectile, RayCastProjectileData


class ULProjectileRayCast(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.origin = None
        self.destination = None
        self.local: bool = None
        self.power: float = None
        self.resolution: float = None
        self.property_name: str = None
        self.xray: bool = None
        self.mask: int = get_bitmask(all=True)
        self.distance: float = None
        self.visualize: bool = None
        self.network = None
        self._data = RayCastProjectileData((None, None, None, None))
        self.RESULT = ULOutSocket(self, self.get_result)
        self.PICKED_OBJECT = ULOutSocket(self, self.get_picked_object)
        self.POINT = ULOutSocket(self, self.get_point)
        self.NORMAL = ULOutSocket(self, self.get_normal)
        self.PARABOLA = ULOutSocket(self, self.get_parabola)

    def setup(self, network):
        self.network = network

    def get_result(self):
        return self._data.obj is not None

    def get_picked_object(self):
        return self._data.obj

    def get_parabola(self):
        return self._data.points

    def get_point(self):
        return self._data.point

    def get_normal(self):
        return self._data.normal

    def calc_projectile(self, t, vel, pos):
        half: float = logic.getCurrentScene().gravity * (.5 * t * t)
        vel = vel * t
        return half + vel + pos

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        origin = self.get_input(self.origin)
        power: float = self.get_input(self.power)
        destination = self.get_input(self.destination)
        resolution: float = 1 - (self.get_input(self.resolution) * .99)
        property_name: str = self.get_input(self.property_name)
        xray: bool = self.get_input(self.xray)
        distance: float = self.get_input(self.distance)
        visualize: bool = self.get_input(self.visualize)
        destination.normalize()

        destination *= power
        origin = getattr(origin, 'worldPosition', origin)
        owner = self.network._owner

        self._data = raycast_projectile(
            caster=owner,
            origin=Vector(origin),
            aim=Vector(destination),
            local=self.get_input(self.local),
            power=power,
            distance=distance,
            resolution=resolution,
            prop=property_name,
            xray=xray,
            mask=self.get_input(self.mask),
            visualize=visualize
        )
