from bge import logic
from bge.types import KX_GameObject
from bge.constraints import createVehicle
from uplogic.utils.visualize import draw_cube, draw_mesh
from uplogic import console
from mathutils import Euler
from mathutils import Vector
from uplogic.utils.constants import VEHICLE

FWD = 'FRONT'
'''Front Wheel Drive. Addresses wheel indices starting in the front.'''

RWD = 'REAR'
'''Rear Wheel Drive. Addresses wheel indices starting in the back.'''

FOURWD = 'ALL'
'''Four Wheel Drive. Addresses all wheels on the vehicle.'''


class Vehicle():
    '''BGE physics vehicle controller built on top of a Bullet vehicle constraint.

    On construction the class scans all children of ``body`` recursively
    (sorted by name) for objects whose name contains ``FWheel`` (front,
    steering) or ``RWheel`` (rear, non-steering), detaches each from its
    parent, and registers it with the BGE vehicle constraint. Body
    orientation is temporarily zeroed to ``(0, 0, 0)`` during this
    process and restored afterwards.

    The ``drive``, ``brakes`` and ``steer_axle`` attributes accept one of
    the module-level constants ``FWD``, ``RWD`` or ``FOURWD``.

    :param body: The rigid-body ``KX_GameObject`` that acts as the chassis.
    :param suspension: Suspension compression length applied to all wheels.
    :param stiffness: Suspension stiffness applied to all wheels.
    :param damping: Suspension damping applied to all wheels.
    :param friction: Tyre friction coefficient applied to all wheels.
    :param wheel_size: Multiplier for the auto-detected wheel radius.
    :param drive: Drive axle constant (``FWD``, ``RWD`` or ``FOURWD``).
    :param steer_axle: Steering axle constant (``FWD``, ``RWD`` or ``FOURWD``).
    '''

    _deprecated = False

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
        '''Initialise the vehicle constraint and register the pre-draw reset callback.

        :param body: Chassis ``KX_GameObject``. Children named ``FWheel*``
            and ``RWheel*`` are automatically discovered and added as wheels.
        :param suspension: Initial suspension compression for all wheels.
        :param stiffness: Initial suspension stiffness for all wheels.
        :param damping: Initial suspension damping for all wheels.
        :param friction: Initial tyre friction for all wheels.
        :param wheel_size: Radius multiplier applied to each wheel's
            auto-detected size.
        :param drive: Drive axle; one of ``FWD``, ``RWD`` or ``FOURWD``.
        :param steer_axle: Steering axle; one of ``FWD``, ``RWD`` or ``FOURWD``.
        '''
        if self._deprecated:
            from uplogic.console import warning
            warning('Warning: ULVehicle class will be renamed to "Vehicle" in future releases!')
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

    def rebuild(self):
        '''Placeholder for rebuilding the vehicle constraint. Not yet implemented.'''
        pass

    def visualize(self):
        '''Draw debug geometry for all wheels and the chassis mesh.

        Each wheel is drawn as a blue cube via ``draw_cube`` and the
        chassis is drawn via ``draw_mesh``.
        '''
        for wheel in self.wheels:
            draw_cube(wheel, color=(0, 0, 1, 1))
        draw_mesh(self.body)

    def add_wheel(self, wheel, steering=False):
        '''Add an additional wheel to the vehicle constraint at runtime.

        Body orientation is temporarily zeroed to ``(0, 0, 0)`` before
        calling ``car.addWheel`` and restored afterwards, mirroring the
        constructor behaviour.

        :param wheel: The ``KX_GameObject`` to register as a wheel. If it
            has a parent it is detached first.
        :param steering: Whether the wheel should be a steering wheel.
        '''
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
            abs(wheel.worldScale.z/2) * self.wheel_size,
            steering
        )
        self.wheels.append(wheel)
        body.localOrientation = orig_ori

    def reset(self):
        '''Pre-draw callback that zeroes inputs not set during the current tick.

        If ``is_accelerating``, ``is_braking`` or ``is_steering`` was not
        set to ``True`` this tick the corresponding value is reset to ``0``
        and the flag is cleared. Called automatically each frame via
        ``pre_draw``.
        '''
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
        '''Disable the vehicle and remove the pre-draw reset callback.'''
        self.disable()
        logic.getCurrentScene().pre_draw.remove(self.reset)

    def enable(self):
        '''Enable the vehicle so that inputs are processed.'''
        self.active = True

    def disable(self):
        '''Disable the vehicle so that all inputs are ignored.'''
        self.active = False

    @property
    def acceleration(self):
        '''Engine force applied this tick, scaled by chassis mass.

        Setting this property calls ``applyEngineForce`` on the configured
        drive wheels. The value is multiplied by ``body.mass`` before being
        passed to the constraint. Does nothing when the vehicle is disabled.
        '''
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value):
        if not self.active:
            return
        self._acceleration = value
        self.is_accelerating = True
        drive = self.drive
        wheelcount = self.acc_wheels
        value *= self.body.mass
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
        '''Brake force applied this tick, scaled by chassis mass.

        Setting this property first clears braking on all wheels by calling
        ``applyBraking(0, wheel)``, then applies the new force to the
        configured brake wheels. The value is multiplied by ``body.mass``
        before being passed to the constraint. Does nothing when the vehicle
        is disabled.
        '''
        return self._braking

    @braking.setter
    def braking(self, value):
        if not self.active:
            return
        self._braking = value
        self.is_braking = True
        brakes = self.brakes
        wheelcount = self.brake_wheels
        value *= self.body.mass

        for wheel in range(wheelcount):
            self.constraint.applyBraking(0, wheel)
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
        '''Steering angle applied this tick in radians.

        Setting this property calls ``setSteeringValue`` on the configured
        steering-axle wheels. Does nothing when the vehicle is disabled.
        '''
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
        '''Suspension compression length applied to all wheels immediately on set.'''
        return self._suspension

    @suspension.setter
    def suspension(self, value):
        for wheel in range(self.constraint.getNumWheels()):
            self.constraint.setSuspensionCompression(value, wheel)
        self._suspension = value

    @property
    def stiffness(self):
        '''Suspension stiffness applied to all wheels immediately on set.'''
        return self._stiffness

    @stiffness.setter
    def stiffness(self, value):
        self._stiffness = value
        for wheel in range(self.constraint.getNumWheels()):
            self.constraint.setSuspensionStiffness(value, wheel)

    @property
    def speed(self):
        '''Current forward speed in km/h (read-only).

        Computed as ``localLinearVelocity.y * 3.6``. Attempting to set
        this property logs a debug message and has no effect.

        :returns: Forward speed in km/h as a ``float``.
        '''
        return self.body.localLinearVelocity.y * 3.6

    @speed.setter
    def speed(self, value):
        console.debug('Vehicle.speed is read-only!')

    @property
    def damping(self):
        '''Suspension damping applied to all wheels immediately on set.'''
        return self._damping

    @damping.setter
    def damping(self, value):
        self._damping = value
        for wheel in range(self.constraint.getNumWheels()):
            self.constraint.setSuspensionDamping(value, wheel)

    @property
    def friction(self):
        '''Tyre friction coefficient applied to all wheels immediately on set.'''
        return self._friction

    @friction.setter
    def friction(self, value):
        self._friction = value
        for wheel in range(self.constraint.getNumWheels()):
            self.constraint.setTyreFriction(value, wheel)

    @property
    def roll_influence(self):
        '''Roll influence factor applied to all wheels immediately on set.'''
        return self._roll_influence

    @roll_influence.setter
    def roll_influence(self, value):
        self._roll_influence = value
        for wheel in range(self.constraint.getNumWheels()):
            self.constraint.setRollInfluence(value, wheel)

    def set_wheel_suspension(self, wheel, suspension):
        '''Set suspension compression for a single wheel by index.

        :param wheel: Zero-based index of the target wheel.
        :param suspension: Suspension compression length to apply.
        '''
        self.constraint.setSuspensionCompression(suspension, wheel)

    def set_wheel_stiffness(self, wheel, stiffness):
        '''Set suspension stiffness for a single wheel by index.

        :param wheel: Zero-based index of the target wheel.
        :param stiffness: Suspension stiffness value to apply.
        '''
        self.constraint.setSuspensionStiffness(stiffness, wheel)

    def set_wheel_damping(self, wheel, damping):
        '''Set suspension damping for a single wheel by index.

        :param wheel: Zero-based index of the target wheel.
        :param damping: Suspension damping value to apply.
        '''
        self.constraint.setSuspensionDamping(damping, wheel)

    def set_wheel_friction(self, wheel, friction):
        '''Set tyre friction for a single wheel by index.

        :param wheel: Zero-based index of the target wheel.
        :param friction: Tyre friction coefficient to apply.
        '''
        self.constraint.setTyreFriction(friction, wheel)

    def accelerate(self, power: float = 1, drive='', wheelcount: int = None):
        '''Apply engine force to the vehicle, optionally changing the drive axle.

        This is the primary public API for acceleration. It optionally
        updates ``drive`` and ``acc_wheels`` before assigning to the
        ``acceleration`` property.

        :param power: Normalised engine force (``1.0`` = full throttle).
        :param drive: If non-empty and different from the current ``drive``,
            overrides the drive axle (``FWD``, ``RWD`` or ``FOURWD``).
        :param wheelcount: If provided and different from ``acc_wheels``,
            overrides the number of driven wheels.
        '''
        if drive != self.drive and drive:
            self.drive = drive
        if wheelcount and wheelcount != self.acc_wheels:
            self.acc_wheels = wheelcount
        self.acceleration = power

    def brake(self, power: float = .1, brakes: str = '', wheelcount: int = None):
        '''Apply brake force to the vehicle, optionally changing the brake axle.

        This is the primary public API for braking. It optionally updates
        ``brakes`` and ``brake_wheels`` before assigning to the ``braking``
        property.

        :param power: Normalised brake force (``0.1`` by default).
        :param brakes: If non-empty and different from the current ``brakes``,
            overrides the brake axle (``FWD``, ``RWD`` or ``FOURWD``).
        :param wheelcount: If provided and different from ``brake_wheels``,
            overrides the number of braked wheels.
        '''
        if brakes != self.brakes and brakes:
            self.brakes = brakes
        if wheelcount and wheelcount != self.brake_wheels:
            self.brake_wheels = wheelcount
        self.braking = power

    def steer(self, power: float = 0, steer_axle: str = '', wheelcount: int = None):
        '''Apply steering angle to the vehicle, optionally changing the steer axle.

        This is the primary public API for steering. It optionally updates
        ``steer_axle`` and ``steer_wheels`` before assigning to the
        ``steering`` property.

        :param power: Steering angle in radians (positive = left).
        :param steer_axle: If non-empty and different from the current
            ``steer_axle``, overrides the steering axle (``FWD``, ``RWD``
            or ``FOURWD``).
        :param wheelcount: If provided and different from ``steer_wheels``,
            overrides the number of steered wheels.
        '''
        if steer_axle != self.steer_axle and steer_axle:
            self.steer_axle = steer_axle
        if wheelcount and wheelcount != self.steer_wheels:
            self.steer_wheels = wheelcount
        self.steering = power


class ULVehicle(Vehicle):
    '''[DEPRECATED] Use :class:`Vehicle` instead.'''

    _deprecated = True
