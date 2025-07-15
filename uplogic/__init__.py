__version__ = '4.5.1'

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
    version = str(version)
    nums = version.split('.')
    vnums = __version__.split('.')
    
    while len(vnums) < len(nums):
        vnums.append(0)
    
    for i, num in enumerate(nums):
        if int(num) != int(vnums[i]):
            return False

    return True


