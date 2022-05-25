from bge import logic
from bge.types import KX_GameObject
from bge.constraints import createVehicle
from mathutils import Euler
from mathutils import Vector
from uplogic.utils import VEHICLE

FWD = 'FRONT'
"""Front Wheel Drive\n
This will adress wheel indices starting in the front."""

RWD = 'REAR'
"""Rear Wheel Drive\n
This will adress wheel indices starting in the back."""

FOURWD = 'ALL'
"""Four Wheel Drive\n
This will adress all wheels on the vehicle."""


class ULVehicle():

    def __init__(
        self,
        body: KX_GameObject,
        suspension: float = 0.06,
        stiffness: float = 50.0,
        damping: float = 5.0,
        friction: float = 2.0,
        wheel_size: float = 1.0,
        drive: str = FWD,
        steer_axle: str = FWD
    ) -> None:
        orig_ori = body.localOrientation.copy()
        body.localOrientation = Euler((0, 0, 0), 'XYZ')
        ph_id = body.getPhysicsId()
        car = createVehicle(ph_id)
        down = Vector((0, 0, -1))
        axle_dir = body.getAxisVect(Vector((-1, 0, 0)))
        wheels = []
        cs = sorted(body.childrenRecursive, key=lambda c: c.name)
        for c in cs:
            if 'FWheel' in c.name:
                c.removeParent()
                car.addWheel(
                    c,
                    c.worldPosition - body.worldPosition,
                    down,
                    axle_dir,
                    suspension,
                    abs(c.worldScale.x/2) * wheel_size,
                    True
                )
                wheels.append(c)
            elif 'RWheel' in c.name:
                c.removeParent()
                car.addWheel(
                    c,
                    c.worldPosition - body.worldPosition,
                    down,
                    axle_dir,
                    suspension,
                    abs(c.worldScale.x/2) * wheel_size,
                    False
                )
                wheels.append(c)
        body.localOrientation = orig_ori
        self.constraint = car
        body[VEHICLE] = self
        self.wheels = wheels

        self.body = body
        self.suspension = suspension
        self.stiffness = stiffness
        self.damping = damping
        self.friction = friction
        self.wheel_size = wheel_size
        self.active = True

        self.drive = drive
        self.acc_wheels = 2
        self.brakes = FOURWD
        self.brake_wheels = 4
        self.steer_axle = steer_axle
        self.steer_wheels = 2

        self.acceleration = 0
        self.braking = 0
        self.steering = 0

        self.is_accelerating = False
        self.is_braking = False
        self.is_steering = False

        logic.getCurrentScene().pre_draw.append(self.reset)

    def add_wheel(self, wheel, steering=False):
        body = self.body
        car = self.constraint
        orig_ori = body.localOrientation.copy()
        if wheel.parent:
            wheel.removeParent()
        down = Vector((0, 0, -1))
        axle_dir = body.getAxisVect(Vector((-1, 0, 0)))
        body.localOrientation = Euler((0, 0, 0), 'XYZ')
        car.addWheel(
            wheel,
            wheel.worldPosition - body.worldPosition,
            down,
            axle_dir,
            self.suspension,
            abs(wheel.worldScale.x/2) * self.wheel_size,
            steering
        )
        self.wheels.append(wheel)
        body.localOrientation = orig_ori

    def reset(self):
        if self.active:
            if not self.is_accelerating:
                self.acceleration = 0
            if not self.is_braking:
                self.braking = 0
            if not self.is_steering:
                self.steering = 0
            self.is_accelerating = False
            self.is_braking = False
            self.is_steering = False

    def destroy(self):
        self.disable()
        logic.getCurrentScene().pre_draw.remove(self.reset)

    def enable(self):
        self.active = True

    def disable(self):
        self.active = False

    @property
    def acceleration(self):
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value):
        if not self.active:
            return
        self._acceleration = value
        self.is_accelerating = True
        drive = self.drive
        wheelcount = self.acc_wheels
        if drive == FWD:
            for wheel in range(wheelcount):
                self.constraint.applyEngineForce(-value, wheel)
        elif drive == RWD:
            wheels = self.constraint.getNumWheels()
            for wheel in range(wheelcount):
                wheel = wheels - wheel - 1
                self.constraint.applyEngineForce(-value, wheel)
        elif drive == FOURWD:
            for wheel in range(self.constraint.getNumWheels()):
                self.constraint.applyEngineForce(-value, wheel)

    @property
    def braking(self):
        return self._braking

    @braking.setter
    def braking(self, value):
        if not self.active:
            return
        self._braking = value
        self.is_braking = True
        brakes = self.brakes
        wheelcount = self.brake_wheels
        if brakes == FWD:
            for wheel in range(wheelcount):
                self.constraint.applyBraking(value, wheel)
        elif brakes == RWD:
            wheels = self.constraint.getNumWheels()
            for wheel in range(wheelcount):
                wheel = wheels - wheel - 1
                self.constraint.applyBraking(value, wheel)
        elif brakes == FOURWD:
            for wheel in range(self.constraint.getNumWheels()):
                self.constraint.applyBraking(value, wheel)

    @property
    def steering(self):
        return self._steering

    @steering.setter
    def steering(self, value):
        if not self.active:
            return
        self._steering = value
        self.is_steering = True
        steer_axle = self.steer_axle
        wheelcount = self.steer_wheels
        if steer_axle == FWD:
            for wheel in range(wheelcount):
                self.constraint.setSteeringValue(-value, wheel)
        elif steer_axle == RWD:
            wheels = self.constraint.getNumWheels()
            for wheel in range(wheelcount):
                wheel = wheels - wheel - 1
                self.constraint.setSteeringValue(-value, wheel)
        elif steer_axle == FOURWD:
            for wheel in range(self.constraint.getNumWheels()):
                self.constraint.setSteeringValue(-value, wheel)

    @property
    def suspension(self):
        return self._suspension

    @suspension.setter
    def suspension(self, value):
        self._suspension = value
        for wheel in range(self.constraint.getNumWheels()):
            self.constraint.setSuspensionCompression(value, wheel)

    @property
    def stiffness(self):
        return self._stiffness

    @stiffness.setter
    def stiffness(self, value):
        self._stiffness = value
        for wheel in range(self.constraint.getNumWheels()):
            self.constraint.setSuspensionStiffness(value, wheel)

    @property
    def speed(self):
        return self.body.localLinearVelocity.y * 3.6

    @speed.setter
    def speed(self, value):
        print('ULVecicle.speed is read-only!')


    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        self._damping = value
        for wheel in range(self.constraint.getNumWheels()):
            self.constraint.setSuspensionDamping(value, wheel)

    @property
    def friction(self):
        return self._friction

    @friction.setter
    def friction(self, value):
        self._friction = value
        for wheel in range(self.constraint.getNumWheels()):
            self.constraint.setTyreFriction(value, wheel)

    @property
    def roll_influence(self):
        return self._roll_influence

    @roll_influence.setter
    def roll_influence(self, value):
        self._roll_influence = value
        for wheel in range(self.constraint.getNumWheels()):
            self.constraint.setRollInfluence(value, wheel)

    def set_wheel_suspension(self, wheel, suspension):
        self.constraint.setSuspensionCompression(suspension, wheel)

    def set_wheel_stiffness(self, wheel, stiffness):
        self.constraint.setSuspensionStiffness(stiffness, wheel)

    def set_wheel_damping(self, wheel, damping):
        self.constraint.setSuspensionDamping(damping, wheel)

    def set_wheel_friction(self, wheel, friction):
        self.constraint.setTyreFriction(friction, wheel)

    def accelerate(self, power: float = 1, drive='', wheelcount=''):
        if drive != self.drive and drive:
            self.drive = drive
        if wheelcount != self.acc_wheels and wheelcount:
            self.acc_wheels = wheelcount
        self.acceleration = power

    def brake(self, power: float = .1, brakes: str = '', wheelcount: str = ''):
        if brakes != self.brakes and brakes:
            self.drive = brakes
        if wheelcount != self.brake_wheels and wheelcount:
            self.brake_wheels = wheelcount
        self.braking = power

    def steer(self, power: float = 0, steer_axle: str = '', wheelcount: str = ''):
        if steer_axle != self.steer_axle and steer_axle:
            self.steer_axle = steer_axle
        if wheelcount != self.steer_wheels and wheelcount:
            self.steer_wheels = wheelcount
        self.steering = power
