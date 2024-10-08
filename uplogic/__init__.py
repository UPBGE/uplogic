__version__ = '4.0b2'

try:
    from . import animation
    from . import audio
    from . import events
    from . import input
    from . import console
    from . import network
    from . import physics
    from . import shaders
    from . import ui
    from . import utils
except:
    print('Not in runtime!')
import bpy


def check_version(version: str):
    nums = version.split('.')
    vnums = __version__.split('.')
    
    while len(vnums) < len(nums):
        vnums.append(0)
    
    for i, num in enumerate(nums):
        if int(num) < int(vnums[i]):
            return False

    return True


