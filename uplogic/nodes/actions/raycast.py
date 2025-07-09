from uplogic.nodes import ULActionNode
from uplogic.utils.raycasting import raycast
from uplogic.utils.raycasting import raycast_screen
from uplogic.utils.raycasting import raycast_projectile
from uplogic.utils.raycasting import raycast_mouse
from uplogic.utils.raycasting import RayCastData
from uplogic.utils.math import get_bitmask
from bge.logic import getCurrentScene
from bpy.types import Material
from bge.types import KX_GameObject
from mathutils import Vector


class ULRaycast(ULActionNode):  # XXX: Deprecated!

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


class RaycastNode(ULActionNode):

    def __init__(self):
        ULActionNode.__init__(self)
        self.mode = 0
        self.condition: bool = False
        self.caster: KX_GameObject = None
        self.camera: KX_GameObject = None
        self.origin: Vector = Vector((0, 0, 0))
        self.target: Vector = Vector((0, 0, 1))
        self.aim: Vector = Vector((.5, .5))
        self.power: float = 10
        self.resolution: float = .9
        self.local: bool = False
        self.property_name: str = None
        self.material: str = None
        self.xray: bool = False
        self.use_custom_distance: bool = False
        self.distance: float = 0.0
        self.mask: int = get_bitmask(all=True)
        self.use_custom_gravity: bool = False
        self.gravity: Vector = None
        self.visualize: bool = False
        self._data = RayCastData((None, None, None, None, None, None))
        self.face_data = False
        self.RESULT = self.add_output(self.get_result)
        self.PICKED_OBJECT = self.add_output(self.get_picked_object)
        self.POINT = self.add_output(self.get_point)
        self.NORMAL = self.add_output(self.get_normal)
        self.DIRECTION = self.add_output(self.get_direction)
        self.MATERIAL = self.add_output(self.get_material)
        self.UV = self.add_output(self.get_uv)
        self.PARABOLA = self.add_output(self.get_parabola)

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

    def get_parabola(self):
        return self._data.points

    def evaluate(self):
        condition = self.get_condition()
        if not condition:
            self._data = RayCastData((None, None, None, None, None, None))
            return
        mode = self.mode

        material = self.get_input(self.material)

        if mode == 0:
            self._data = raycast(
                self.get_input(self.caster),
                self.get_input(self.origin),
                self.get_input(self.target),
                distance=self.get_input(self.distance) if self.get_input(self.use_custom_distance) else 0,
                prop=self.get_input(self.property_name),
                material=material.name if material else '',
                xray=self.get_input(self.xray),
                local=self.get_input(self.local),
                mask=self.get_input(self.mask),
                face_data=self.face_data,
                visualize=self.get_input(self.visualize)
            )
        elif mode == 1:
            self._data = raycast_projectile(
                self.get_input(self.caster),
                self.get_input(self.origin),
                self.get_input(self.target),
                power=self.get_input(self.power),
                distance=self.get_input(self.distance),
                resolution=1-self.get_input(self.resolution),
                prop=self.get_input(self.property_name),
                material=material.name if material else '',
                xray=self.get_input(self.xray),
                local=self.get_input(self.local),
                mask=self.get_input(self.mask),
                gravity=self.get_input(self.gravity) if self.get_input(self.use_custom_gravity) else None,
                face_data=self.face_data,
                visualize=self.get_input(self.visualize)
            )
        else:
            self._data = raycast_screen(
                self.get_input(self.caster),
                self.get_input(self.aim) if mode == 3 else None,
                distance=self.get_input(self.distance),
                prop=self.get_input(self.property_name),
                material=material.name if material else '',
                xray=self.get_input(self.xray),
                mask=self.get_input(self.mask),
                face_data=self.face_data
            )
