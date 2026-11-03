'''uplogic — BGE utility library.

Provides high-level components for the Blender Game Engine (UPBGE) organised
into focused subpackages:

- :mod:`~uplogic.animation` — action playback and bone-pose helpers
- :mod:`~uplogic.audio` — spatial and 2-D sound management
- :mod:`~uplogic.console` — coloured logging with configurable severity levels
- :mod:`~uplogic.data` — persistent and per-session data storage
- :mod:`~uplogic.events` — deferred callbacks and per-tick scheduling
- :mod:`~uplogic.input` — keyboard, mouse, gamepad, and gesture input
- :mod:`~uplogic.network` — TCP/UDP and OSC networking
- :mod:`~uplogic.physics` — vehicles, characters, buoyancy, and constraints
- :mod:`~uplogic.shaders` — 2-D post-processing filter pipeline
- :mod:`~uplogic.ui` — canvas-based HUD and widget system
- :mod:`~uplogic.utils` — math, raycasting, object helpers, pooling, and more
- :mod:`~uplogic.ai` — NavMesh-based agent pathfinding (import separately)

The runtime subpackages (everything except ``bpy``-only tools) are imported
inside a ``try/except`` block so that importing uplogic from the Blender
scripting area or a test harness does not raise an error when the BGE runtime
is unavailable.

Version string is exposed as :data:`__version__` and can be checked
programmatically with :func:`check_version`.
'''

__version__ = '5.2'

try:
    from . import console
    from . import animation
    from . import audio
    from . import data
    from . import events
    from . import input
    from . import network
    from . import physics
    from . import shaders
    from . import ui
    from . import utils
except:
    print('Not in runtime!')
import bpy


def check_version(version: str):
    '''Check whether the installed uplogic version matches a version prefix.

    Splits both *version* and :data:`__version__` on ``'.'`` and compares each
    supplied component in order.  Only the components present in *version* are
    checked, so ``check_version('5.1')`` passes for any ``5.1.x`` release.

    :param version: Version string to test against, e.g. ``'5'``, ``'5.1'``,
        or ``'5.1.2'``.
    :returns: ``True`` when every supplied component matches; ``False`` as soon
        as any component differs.
    '''
    version = str(version)
    nums = version.split('.')
    vnums = __version__.split('.')

    while len(vnums) < len(nums):
        vnums.append(0)

    for i, num in enumerate(nums):
        if int(num) != int(vnums[i]):
            return False

    return True


