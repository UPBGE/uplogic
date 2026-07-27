from bge import logic
from bge.types import KX_GameObject
from bge.constraints import createVehicle
from uplogic.utils.visualize import draw_cube, draw_mesh
from uplogic import console
from mathutils import Euler
from mathutils import Vector
from uplogic.utils.constants import VEHICLE, DELTA_TIME
from math import exp, pi
from uplogic.utils.math import clamp, lerp

FWD = 'FRONT'
'''Front Wheel Drive. Addresses wheel indices starting in the front.'''

RWD = 'REAR'
'''Rear Wheel Drive. Addresses wheel indices starting in the back.'''

FOURWD = 'ALL'
'''Four Wheel Drive. Addresses all wheels on the vehicle.'''

SUSPENSION_REFERENCE_MASS = 1200.0
'''Reference chassis mass, in kg, that ``stiffness``/``damping`` values are
calibrated against. A vehicle at this mass gets exactly the configured
stiffness/damping as raw Bullet force; heavier or lighter chassis scale
proportionally from there. Keeps typical values human-tunable (roughly the
same range as an unscaled Bullet constant) instead of tiny per-kg fractions.
'''


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

    An optional ``steering_curve`` scales the steering angle passed to
    :meth:`steer` based on the vehicle's current speed. It is a list of
    ``(speed_kmh, factor)`` tuples sorted by speed ascending; the factor
    is linearly interpolated between the nearest points. ``None`` (default)
    disables speed-dependent steering entirely.

    :param body: The rigid-body ``KX_GameObject`` that acts as the chassis.
    :param suspension: Suspension compression length applied to all wheels.
    :param stiffness: Suspension stiffness applied to all wheels.
    :param damping: Suspension damping applied to all wheels.
    :param friction: Tyre friction coefficient applied to all wheels.
    :param wheel_size: Multiplier for the auto-detected wheel radius.
    :param drive: Drive axle constant (``FWD``, ``RWD`` or ``FOURWD``).
    :param steer_axle: Steering axle constant (``FWD``, ``RWD`` or ``FOURWD``).
    :param steering_curve: Speed-dependent steering scale. ``None`` to
        disable. Example: ``[(0, 1.0), (40, 0.8), (120, 0.35), (200, 0.2)]``.
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
        steer_axle: str = FWD,
        max_steering: float = .9    ,
        steering_curve: list = None
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
        :param max_steering: Maximum steering factor (1 = 80°).
        :param steering_curve: Speed-dependent steering scale as a list of
            ``(speed_kmh, factor)`` tuples sorted by speed. ``None`` disables
            speed-dependent steering.
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

        self.is_accelerating = False
        self.is_braking = False
        self.is_steering = False

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
        self.brake_wheels = None
        self.steer_axle = steer_axle
        self.steer_wheels = 2
        self.max_steering = max_steering
        self.steering_curve = steering_curve

        self.acceleration = 0
        self.braking = 0
        self.steering = 0

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
        if not self.active or self.is_braking:
            return
        self._acceleration = value
        if value > 0:
            self.is_accelerating = True
        drive = self.drive
        wheelcount = self.acc_wheels
        value = clamp(value, -1, 1)
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

        Setting this property first zeroes ``applyEngineForce`` on every
        wheel when ``value > 0`` (Bullet's ``btRaycastVehicle`` ignores
        ``applyBraking`` on any wheel where engine force is non-zero), then
        clears braking via ``applyBraking(0, wheel)``, and finally applies
        the new force to the configured brake wheels. The value is multiplied
        by ``body.mass`` before being passed to the constraint. Does nothing
        when the vehicle is disabled.
        '''
        return self._braking

    @braking.setter
    def braking(self, value):
        if not self.active:
            return
        self._braking = value
        brakes = self.brakes
        wheelcount = self.brake_wheels if self.brake_wheels else self.constraint.getNumWheels()
        if value > 0:
            self.is_braking = True
            # Bullet's btRaycastVehicle ignores applyBraking when engineForce != 0
            # on a wheel; zero it first so braking always takes effect.
            for wheel in range(self.constraint.getNumWheels()):
                self.constraint.applyEngineForce(0, wheel)
        value = clamp(value, 0, 1)
        value *= self.body.mass
        for wheel in range(wheelcount):
            self.constraint.applyBraking(0, wheel)
        if brakes == FWD:
            for wheel in range(wheelcount):
                self.constraint.applyBraking(value, wheel)
        elif brakes == RWD:
            wheels = self.constraint.getNumWheels()
            for wheel in range(wheelcount):
                self.constraint.applyBraking(value, wheel)
        elif brakes == FOURWD:
            wheels = self.constraint.getNumWheels()
            half_wheels = round(wheels * .5)
            for wheel in range(half_wheels):
                self.constraint.applyBraking(value * .7, wheel)
            for wheel in range(half_wheels):
                wheel = wheels - wheel - 1
                self.constraint.applyBraking(value * .3, wheel)

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
        value = value * self.max_steering
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
        '''Suspension stiffness applied to all wheels, scaled by chassis mass.

        The value is scaled by ``body.mass / SUSPENSION_REFERENCE_MASS``
        before being passed to the constraint, so a chassis at the reference
        mass gets exactly this value as raw Bullet stiffness, while heavier
        or lighter chassis scale proportionally to keep comparable ride
        behaviour.
        '''
        return self._stiffness

    @stiffness.setter
    def stiffness(self, value):
        self._stiffness = value
        scaled = value * (self.body.mass / SUSPENSION_REFERENCE_MASS)
        for wheel in range(self.constraint.getNumWheels()):
            self.constraint.setSuspensionStiffness(scaled, wheel)

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
        '''Suspension damping applied to all wheels, scaled by chassis mass.

        The value is scaled by ``body.mass / SUSPENSION_REFERENCE_MASS``
        before being passed to the constraint, so a chassis at the reference
        mass gets exactly this value as raw Bullet damping, while heavier or
        lighter chassis scale proportionally to keep comparable ride
        behaviour.
        '''
        return self._damping

    @damping.setter
    def damping(self, value):
        self._damping = value
        scaled = value * (self.body.mass / SUSPENSION_REFERENCE_MASS)
        for wheel in range(self.constraint.getNumWheels()):
            self.constraint.setSuspensionDamping(scaled, wheel)

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
        :param stiffness: Suspension stiffness value to apply, scaled by
            ``body.mass / SUSPENSION_REFERENCE_MASS`` before being passed to
            the constraint.
        '''
        self.constraint.setSuspensionStiffness(stiffness * (self.body.mass / SUSPENSION_REFERENCE_MASS), wheel)

    def set_wheel_damping(self, wheel, damping):
        '''Set suspension damping for a single wheel by index.

        :param wheel: Zero-based index of the target wheel.
        :param damping: Suspension damping value to apply, scaled by
            ``body.mass / SUSPENSION_REFERENCE_MASS`` before being passed to
            the constraint.
        '''
        self.constraint.setSuspensionDamping(damping * (self.body.mass / SUSPENSION_REFERENCE_MASS), wheel)

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

    def _steering_factor(self, speed: float) -> float:
        '''Return the steering scale factor for the given speed.

        Linearly interpolates within ``steering_curve``. Returns ``1.0``
        when ``steering_curve`` is ``None`` or has fewer than two points,
        clamps to the first or last factor outside the defined range.

        :param speed: Current forward speed in km/h (absolute value).
        :returns: Steering scale factor as a ``float`` in ``[0, 1]``.
        '''
        curve = self.steering_curve
        if not curve or len(curve) < 2:
            return 1.0
        if speed <= curve[0][0]:
            return curve[0][1]
        if speed >= curve[-1][0]:
            return curve[-1][1]
        for i in range(len(curve) - 1):
            s0, f0 = curve[i]
            s1, f1 = curve[i + 1]
            if s0 <= speed <= s1:
                t = (speed - s0) / (s1 - s0)
                return f0 + (f1 - f0) * t
        return 1.0

    def steer(self, power: float = 0, steer_axle: str = '', wheelcount: int = None):
        '''Apply steering angle to the vehicle, optionally changing the steer axle.

        This is the primary public API for steering. It optionally updates
        ``steer_axle`` and ``steer_wheels`` before assigning to the
        ``steering`` property. If ``steering_curve`` is set, ``power`` is
        scaled by the interpolated factor at the current speed before being
        applied.

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
        self.steering = power * self._steering_factor(abs(self.speed))


class ULVehicle(Vehicle):
    '''[DEPRECATED] Use :class:`Vehicle` instead.'''

    _deprecated = True


class Engine():
    '''Simple engine model producing a plausible torque curve.

    Torque peaks at ``peak_torque_rpm`` and falls off toward idle and
    redline via a Gaussian bell curve. Displacement shifts the overall
    torque level: engines larger than 2.0 L gain ~3 % per litre.

    :param horsepower: Peak engine power in metric horsepower.
    :param displacement: Engine displacement in litres. Affects the
        torque multiplier relative to a 2.0 L baseline.
    :param peak_torque_rpm: RPM at which peak torque occurs.
    :param redline_rpm: Maximum RPM; torque falls to near zero here.
    :param idle_rpm: Minimum sustained RPM; torque is minimal here.
    :param rev_rate: Rate at which RPM rises during free-revving, in RPM/s.
        Falls at half this rate on throttle release. Defaults to ``4000``.
    '''

    def __init__(
        self,
        horsepower: float = 180,
        displacement: float = 2.0,
        peak_torque_rpm: float = 3500,
        redline_rpm: float = 7000,
        idle_rpm: float = 800,
        rev_rate: float = 4000
    ) -> None:
        '''Initialise engine parameters and pre-compute the torque curve constants.

        :param horsepower: Peak engine power in metric horsepower.
        :param displacement: Engine displacement in litres.
        :param peak_torque_rpm: RPM at which peak torque is produced.
        :param redline_rpm: RPM ceiling; inputs are clamped to this.
        :param idle_rpm: Minimum RPM floor used when the vehicle is at rest.
        :param rev_rate: Speed at which RPM rises when free-revving, in RPM
            per second. RPM falls at half this rate when throttle is released.
            Defaults to ``4000``.
        '''
        self.horsepower = horsepower
        self.displacement = displacement
        self.peak_torque_rpm = peak_torque_rpm
        self.redline_rpm = redline_rpm
        self.idle_rpm = idle_rpm
        self.rev_rate = rev_rate
        self.peak_torque_nm = horsepower * 9549.0 / peak_torque_rpm
        self.displacement_factor = 1.0 + (displacement - 2.0) * 0.03
        self._sigma = (redline_rpm - idle_rpm) * 0.3

    def torque_at_rpm(self, rpm: float) -> float:
        '''Return engine torque in Nm at the given crankshaft speed.

        Uses a Gaussian bell curve centred on ``peak_torque_rpm``.
        The result is scaled by the displacement factor computed at
        construction time.

        :param rpm: Crankshaft speed in revolutions per minute.
        :returns: Torque in Newton-metres as a ``float``.
        '''
        if self._sigma < 1e-6:
            return self.peak_torque_nm * self.displacement_factor
        torque_factor = exp(-0.5 * ((rpm - self.peak_torque_rpm) / self._sigma) ** 2)
        return self.peak_torque_nm * self.displacement_factor * torque_factor


class Transmission():
    '''Gear-box model with configurable shift automation.

    Stores a list of forward gear ratios and a separate reverse ratio.
    The ``current_ratio`` property returns the combined ratio at the
    wheel (gear ratio × ``final_drive``).

    ``shift_mode`` controls how gear changes are handled:

    - ``0`` — **Manual**: no automatic shifts; call :meth:`shift_up` and
      :meth:`shift_down` from your own code (or bind them to inputs).
      Use :attr:`MotorizedVehicle.clutch` to disengage the drivetrain
      while shifting.
    - ``1`` — **Automated manual**: :class:`MotorizedVehicle` selects and
      executes gears automatically based on RPM thresholds, but cuts
      engine force for ``shift_time`` seconds on each shift to simulate
      clutch engagement. RPM free-revs downward during this window.
    - ``2`` — **Automatic**: gear changes are instant with no power
      interruption, simulating a torque-converter automatic transmission.

    Reverse (``gear = -1``) is never engaged or left automatically; it
    must be set explicitly via the ``gear`` property.

    :param gears: Ordered list of forward gear ratios, lowest to highest.
        Defaults to a generic 5-speed ``[3.5, 2.1, 1.4, 1.0, 0.8]``.
    :param final_drive: Differential ratio applied to every gear.
    :param reverse_ratio: Gear ratio used in reverse (``gear = -1``),
        multiplied by ``final_drive`` like the forward gears.
    :param shift_up_rpm: RPM above which modes 1 and 2 step up one gear.
    :param shift_down_rpm: RPM below which modes 1 and 2 step down one gear.
    :param shift_mode: Shift automation mode (``0``=manual, ``1``=auto-manual,
        ``2``=automatic). Defaults to ``2``.
    :param shift_time: Duration of the power-cut window in seconds for a
        mode-1 shift. Ignored in modes 0 and 2. Defaults to ``0.2``.
    '''

    def __init__(
        self,
        gears: list = None,
        final_drive: float = 3.9,
        reverse_ratio: float = 3.2,
        shift_up_rpm: float = 5500,
        shift_down_rpm: float = 2000,
        shift_mode: int = 2,
        shift_time: float = 0.2
    ) -> None:
        '''Initialise transmission parameters.

        :param gears: Forward gear ratios (lowest first). ``None`` uses a
            default generic 5-speed.
        :param final_drive: Final drive (differential) ratio.
        :param reverse_ratio: Ratio used when ``gear`` is ``-1``.
        :param shift_up_rpm: RPM threshold for automatic upshifts (modes 1 and 2).
        :param shift_down_rpm: RPM threshold for automatic downshifts (modes 1 and 2).
        :param shift_mode: Shift automation (``0``=manual, ``1``=auto-manual,
            ``2``=automatic).
        :param shift_time: Power-cut duration in seconds for mode-1 shifts.
        '''
        if gears is None:
            gears = [3.5, 2.1, 1.4, 1.0, 0.8]
        self.gears = list(gears)
        self.final_drive = final_drive
        self.reverse_ratio = reverse_ratio
        self.shift_up_rpm = shift_up_rpm
        self.shift_down_rpm = shift_down_rpm
        self.shift_mode = shift_mode
        self.shift_time = shift_time
        self._current_gear = 0

    @property
    def gear(self) -> int:
        '''Current gear index (read/write).

        ``-1`` is reverse, ``0`` is neutral, ``1`` is first gear, and
        ``len(gears)`` is the top forward gear. Values outside
        ``[-1, len(gears)]`` are clamped.
        '''
        return self._current_gear

    @gear.setter
    def gear(self, value: int) -> None:
        self._current_gear = max(-1, min(int(value), len(self.gears)))

    @property
    def current_ratio(self) -> float:
        '''Combined gear-and-final-drive ratio for the current gear (read-only).

        Returns ``reverse_ratio * final_drive`` for reverse (``-1``),
        ``0.0`` for neutral (``0``, drivetrain disconnected), and
        ``gears[gear - 1] * final_drive`` for forward gears.
        '''
        if self._current_gear == -1:
            return self.reverse_ratio * self.final_drive
        if self._current_gear == 0:
            return 0.0
        return self.gears[self._current_gear - 1] * self.final_drive

    def shift_up(self) -> None:
        '''Step up one gear.

        From neutral steps into first gear; from any forward gear steps to
        the next. Has no effect in reverse or at the top gear.
        '''
        if 0 <= self._current_gear < len(self.gears):
            self._current_gear += 1

    def shift_down(self) -> None:
        '''Step down one gear, stopping at neutral (index ``0``).

        Does not engage reverse; set ``gear = -1`` explicitly for that.
        '''
        if self._current_gear > 0:
            self._current_gear -= 1


class MotorizedVehicle(Vehicle):
    '''Vehicle controller with engine and transmission simulation.

    Extends :class:`Vehicle` by routing throttle input through an
    :class:`Engine` torque curve and a :class:`Transmission` gear ratio
    before calling ``applyEngineForce`` on the Bullet constraint. RPM is
    estimated from wheel speed each frame; automatic gear changes are
    performed in modes 1 and 2 (see :attr:`Transmission.shift_mode`).

    When the throttle is released while moving, a resistive force
    proportional to ``engine_braking`` (fraction of current engine torque)
    is applied through the drivetrain, simulating engine compression drag.
    Set ``engine_braking = 0`` to disable it.

    A ``clutch`` attribute (``0.0`` = depressed/disconnected,
    ``1.0`` = released/fully engaged) scales wheel force and engine braking,
    and switches RPM tracking to free-revving mode when below ``0.5``.
    In neutral the drivetrain is always disconnected regardless of clutch.
    In shift mode 2 (automatic) the clutch has no effect on shifting;
    in mode 1 (automated manual) a brief power cut is inserted on each
    shift regardless of the clutch value.

    The ``accelerate(power)`` API is identical to :class:`Vehicle`: ``power``
    is a normalised throttle in ``[0, 1]``. Braking and steering are
    inherited unchanged.

    :param body: Chassis ``KX_GameObject`` (see :class:`Vehicle`).
    :param engine: :class:`Engine` instance. Defaults to ``Engine()`` if
        not provided.
    :param transmission: :class:`Transmission` instance. Defaults to
        ``Transmission()`` if not provided.
    :param wheel_radius: Driven-wheel radius in metres. Auto-detected from
        the first wheel object if omitted; falls back to ``0.3`` when no
        wheels exist.
    :param engine_braking: Fraction of current engine torque applied as
        drivetrain drag when coasting. ``0.15`` by default; set to ``0``
        to disable.
    :param kwargs: All remaining keyword arguments are forwarded to
        :class:`Vehicle.__init__` (``suspension``, ``stiffness``,
        ``damping``, ``friction``, ``wheel_size``, ``drive``,
        ``steer_axle``).
    '''

    def __init__(
        self,
        body: KX_GameObject,
        engine: 'Engine' = None,
        transmission: 'Transmission' = None,
        wheel_radius: float = None,
        engine_braking: float = 0.12,
        **kwargs
    ) -> None:
        '''Initialise the motorised vehicle.

        Calls :class:`Vehicle.__init__` first (which scans children and
        registers the pre-draw callback), then attaches the powertrain
        objects and resolves the driven-wheel radius.

        :param body: Chassis ``KX_GameObject``.
        :param engine: :class:`Engine` instance, or ``None`` to use defaults.
        :param transmission: :class:`Transmission` instance, or ``None``
            to use defaults.
        :param wheel_radius: Driven-wheel radius override in metres.
        :param engine_braking: Coasting drag as a fraction of engine torque
            (``0``–``1``). Defaults to ``0.15``.
        :param kwargs: Forwarded to :class:`Vehicle.__init__`.
        '''
        super().__init__(body, **kwargs)
        self.engine = engine if engine is not None else Engine()
        self.transmission = transmission if transmission is not None else Transmission()
        self.engine_braking = engine_braking
        if wheel_radius is not None:
            self._wheel_radius = wheel_radius
        elif self.wheels:
            self._wheel_radius = abs(self.wheels[0].worldScale.x / 2) * self.wheel_size
        else:
            self._wheel_radius = 0.3
        self._rpm = self.engine.idle_rpm
        self._throttle = 0.0
        self._shift_timer = 0.0
        self.clutch = 1.0

    @property
    def rpm(self) -> float:
        '''Current estimated engine RPM (read-only).

        Updated every frame in ``reset()`` based on wheel speed and the
        current gear ratio. Clamped to ``[engine.idle_rpm, engine.redline_rpm]``.
        Attempting to set this property logs a debug message and has no effect.
        '''
        return self._rpm

    @rpm.setter
    def rpm(self, _value) -> None:
        console.debug('MotorizedVehicle.rpm is read-only!')

    @property
    def gear(self) -> int:
        '''Current gear index, delegated to ``transmission.gear`` (read/write).

        ``-1`` = reverse, ``0`` = neutral, ``1`` = first gear,
        ``len(gears)`` = top gear.
        '''
        return self.transmission.gear

    @gear.setter
    def gear(self, value: int) -> None:
        self.transmission.gear = value

    def _update_powertrain(self) -> None:
        '''Estimate RPM and run the auto-shift logic.

        Called by ``reset()`` every frame before the parent's input reset.

        When the drivetrain is connected (clutch engaged, a forward or reverse
        gear selected, and no mode-1 shift in progress), RPM is derived from
        wheel speed, gear ratio, and wheel radius. Otherwise (neutral, clutch
        depressed, or a mode-1 shift window active) the engine free-revs: RPM
        moves toward ``[idle_rpm, redline_rpm]`` scaled by ``_throttle`` at
        ``engine.rev_rate`` RPM/s, falling at half that rate. During a mode-1
        shift the effective throttle is forced to zero so RPM naturally drops
        toward idle.

        Auto-shifting (modes 1 and 2) is only performed in forward gears
        (``gear >= 1``) with the clutch engaged and no shift already in
        progress (mode 1). Mode 1 arms ``_shift_timer`` on each change; mode 2
        changes gear instantly with no power interruption.
        '''
        trans = self.transmission
        eng = self.engine

        if self._shift_timer > 0:
            self._shift_timer = max(0.0, self._shift_timer - DELTA_TIME())

        is_shifting = self._shift_timer > 0
        engaged = self.clutch >= 0.5 and trans.gear != 0

        if engaged and not is_shifting:
            speed_mps = abs(self.body.localLinearVelocity.y)
            ratio = trans.current_ratio
            if self._wheel_radius > 1e-6:
                raw_rpm = (speed_mps / self._wheel_radius) * ratio * 60.0 / (2.0 * pi)
            else:
                raw_rpm = eng.idle_rpm
            self._rpm = clamp(raw_rpm, eng.idle_rpm, eng.redline_rpm)
        else:
            effective_throttle = 0.0 if is_shifting else self._throttle
            target_rpm = lerp(eng.idle_rpm, eng.redline_rpm, effective_throttle)
            step = eng.rev_rate * DELTA_TIME()
            if self._rpm < target_rpm:
                self._rpm = min(self._rpm + step, target_rpm)
            else:
                self._rpm = max(self._rpm - step * 0.5, target_rpm)
            self._rpm = clamp(self._rpm, eng.idle_rpm, eng.redline_rpm)

        if trans.shift_mode == 1 and trans.gear >= 1 and engaged and not is_shifting:
            if self._rpm >= trans.shift_up_rpm and trans.gear < len(trans.gears):
                trans.shift_up()
                self._shift_timer = trans.shift_time
            elif self._rpm <= trans.shift_down_rpm and trans.gear > 1:
                trans.shift_down()
                self._shift_timer = trans.shift_time
        elif trans.shift_mode == 2 and trans.gear >= 1 and engaged:
            if self._rpm >= trans.shift_up_rpm and trans.gear < len(trans.gears):
                trans.shift_up()
            elif self._rpm <= trans.shift_down_rpm and trans.gear > 1:
                trans.shift_down()

    def reset(self) -> None:
        '''Pre-draw callback that updates the powertrain and then delegates to :class:`Vehicle.reset`.

        Zeroes ``_throttle`` when ``accelerate()`` was not called this tick,
        so that auto-shift correctly sees a zero throttle when coasting.
        When ``engine_braking`` is non-zero and the vehicle is moving without
        throttle, a resistive force opposing the current velocity is applied
        through the driven wheels.
        '''
        if not self.is_accelerating:
            self._throttle = 0.0
            if self.engine_braking > 0 and self._wheel_radius > 1e-6 and self.transmission.gear != 0 and self.clutch > 0:
                speed = self.body.localLinearVelocity.y
                if abs(speed) > 0.1:
                    braking_torque = self.engine.torque_at_rpm(self._rpm) * self.engine_braking * self.clutch
                    brake_force = braking_torque * self.transmission.current_ratio / self._wheel_radius
                    mass = self.body.mass
                    if mass > 0:
                        sign = -1.0 if speed > 0 else 1.0
                        self.acceleration = sign * brake_force / mass
        self._update_powertrain()
        super().reset()

    def accelerate(self, power: float = 1, drive: str = '', wheelcount: int = None) -> None:
        '''Apply throttle input routed through the engine and transmission.

        Converts ``power`` (0–1 throttle) to an engine torque at the current
        RPM, multiplies by the current gear ratio and clutch, and applies the
        resulting force to the driven wheels via the parent ``acceleration``
        property.

        During a mode-1 gear change (``_shift_timer > 0``) engine force is
        cut to zero to simulate clutch engagement, but ``_throttle`` is still
        updated so the RPM free-rev target tracks the driver's intent.

        :param power: Normalised throttle in ``[0, 1]``. The absolute value is
            used; direction is determined by the current gear.
        :param drive: If non-empty and different from the current drive mode,
            overrides it (``FWD``, ``RWD`` or ``FOURWD``).
        :param wheelcount: If provided and different from ``acc_wheels``,
            overrides the number of driven wheels.
        '''
        throttle = clamp(abs(power), 0.0, 1.0)
        self._throttle = throttle
        if drive and drive != self.drive:
            self.drive = drive
        if wheelcount and wheelcount != self.acc_wheels:
            self.acc_wheels = wheelcount
        if self._shift_timer > 0:
            self.acceleration = 0
            return
        trans = self.transmission
        torque = self.engine.torque_at_rpm(self._rpm) * throttle
        ratio = trans.current_ratio
        wheel_force = torque * ratio * self.clutch
        mass = self.body.mass
        normalised = (wheel_force / mass) if mass > 0 else 0.0
        if trans.gear == -1:
            normalised = -normalised
        self.acceleration = normalised
