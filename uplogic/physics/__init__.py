'''Physics components and utilities for uplogic.

Provides buoyancy simulation (:class:`~uplogic.physics.Flotsam`,
:class:`~uplogic.physics.Ship`), a collision-callback helper
(:func:`~uplogic.physics.on_collision`), a vehicle controller
(:class:`~uplogic.physics.Vehicle`), a character physics wrapper
(:class:`~uplogic.physics.Character`), and spring/track-to constraints
(:class:`~uplogic.physics.Spring`, :class:`~uplogic.physics.TrackTo`).

Typical usage::

    from uplogic import physics

    # attach buoyancy to a rigid-body object
    bob = physics.Flotsam(scene_obj, buoyancy=1.5)

    # vehicle controller
    car = physics.Vehicle(body_obj, stiffness=60, drive=physics.RWD)
    car.accelerate(0.8)

    # collision callback
    physics.on_collision(player, on_hit, prop='Enemy')
'''

from .buoyancy import ULFlotsam, Flotsam  # noqa
from .buoyancy import ULShip, Ship  # noqa
from .collision import on_collision  # noqa
from .vehicle import FOURWD  # noqa
from .vehicle import FWD  # noqa
from .vehicle import RWD  # noqa
from .vehicle import ULVehicle, Vehicle  # noqa
from .character import ULCharacter, Character  # noqa
from .constraints import create_constraint  # noqa
from .constraints import remove_constraint  # noqa
from .constraints import ULSpring, Spring
from .constraints import ULTrackTo, TrackTo
