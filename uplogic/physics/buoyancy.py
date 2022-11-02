from bge import logic
from mathutils import Vector
from uplogic.utils import vec_clamp
from uplogic.utils import raycast
from uplogic.utils import FLOATSAM
from uplogic.utils import SHIP
from uplogic.utils import WATER


class ULBuoy():

    def __init__(self) -> None:
        self._active = True

    def disable(self):
        self._active = False

    def enable(self):
        self._active = True

    def destroy(self):
        raise NotImplementedError


class ULFloatsam(ULBuoy):

    def __init__(self, game_object, buoyancy=1, height=200, align=True) -> None:
        super().__init__()
        self.game_object = game_object
        game_object[FLOATSAM] = self
        self.height = height
        self.buoyancy = buoyancy
        self.align = align
        logic.getCurrentScene().pre_draw.append(self.update)

    def update(self):
        if not self._active:
            return
        up = Vector((0, 0, 1))
        floatsam = self.game_object
        lindamp = .1
        wpos = floatsam.worldPosition
        obj, point, normal, direction = raycast(
            floatsam,
            wpos,
            up,
            self.height,
            WATER,
            xray=True,
            local=True,
            visualize=True
        )
        if obj:
            lindamp = .8
            lift = (up * (wpos - point).length * self.buoyancy)
            floatsam.applyImpulse(
                wpos,
                vec_clamp(lift, max=self.buoyancy),
                False
            )
            if self.align:
                self.game_object.alignAxisToVect(normal, 2, .2)
        floatsam.linearDamping = lindamp
        floatsam.angularDamping = lindamp * .8

    def destroy(self):
        logic.getCurrentScene().pre_draw.remove(self.update)


class ULShip(ULBuoy):

    def __init__(self, game_object, buoyancy=1, height=200, water=None) -> None:
        super().__init__()
        self.game_object = game_object
        self.linear_damping = game_object.linearDamping
        self.angular_damping = game_object.angularDamping
        game_object[SHIP] = self
        self.height = height
        if water:
            water[WATER] = True
        cs = sorted(game_object.childrenRecursive, key=lambda c: c.name)
        self.buoys = [c for c in cs if 'Buoy' in c.name]
        self.buoyancy = buoyancy
        logic.getCurrentScene().pre_draw.append(self.update)

    def update(self):
        if not self._active:
            return
        up = Vector((0, 0, 1))
        lifts = len(self.buoys)
        ship = self.game_object
        max_lin_damp = .9 - self.linear_damping
        max_ang_damp = .8 - self.linear_damping
        lin_dampen_factor = 0
        ang_dampen_factor = 0
        for buoy in self.buoys:
            wpos = buoy.worldPosition
            obj, point, normal, direction = raycast(
                buoy,
                wpos,
                up,
                self.height,
                WATER,
                xray=True,
                local=True
            )
            if obj:
                div = 1 / lifts
                lin_dampen_factor += (max_lin_damp * div)
                ang_dampen_factor += (max_ang_damp * div)
                lift = (up * (wpos - point).length * self.buoyancy) * div
                ship.applyImpulse(
                    wpos,
                    vec_clamp(lift, max=self.buoyancy * 2 * div),
                    False
                )
        ship.linearDamping = self.linear_damping + lin_dampen_factor
        ship.angularDamping = self.angular_damping + ang_dampen_factor

    def destroy(self):
        logic.getCurrentScene().pre_draw.remove(self.update)
