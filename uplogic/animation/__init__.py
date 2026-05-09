'''Animation subsystem for uplogic.

Provides scene-object action playback via :class:`Action`, sprite-sheet
sequencing via :class:`Sequence`, armature control via :class:`Rig`, and the
:class:`ActionSystem` that drives per-frame updates.

Typical usage::

    from uplogic import animation

    # play a looping action on a game object
    anim = animation.Action(my_object, 'Run', play_mode='loop')

    # stop it later
    anim.stop()

    # play a sprite sheet
    seq = animation.Sequence('MyMaterial', 'SpriteNode', 0, 8, fps=12, mode='loop')
'''

from .actionsystem import ActionSystem  # noqa
from .actionsystem import get_priority_action  # noqa
from .action import ACTION_FINISHED  # noqa
from .action import ACTION_STARTED  # noqa
from .action import ULAction, Action  # noqa
from .action import start_action
from .sequence import ULSequence, Sequence  # noqa
from .rig import Rig
