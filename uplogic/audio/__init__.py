'''Audio subsystem for uplogic.

Provides 2D/3D positional audio, music track management, and optional FMOD
Studio integration. All playback is driven by the BGE ``aud`` module and the
uplogic :class:`AudioSystem` device wrapper.

Typical usage::

    from uplogic import audio

    # one-shot 2D sound
    audio.play_sound_2d('//sfx/click.wav', volume=0.8)

    # looping 3D sound attached to a game object
    audio.play_sound_3d(my_object, '//sfx/engine.wav', loop_count=-1)

    # music with multiple layers
    music = audio.Music()
    music.add_track('//music/bass.wav', 'Bass')
    music.add_track('//music/melody.wav', 'Melody')
'''

from .audiosystem import AudioSystem  # noqa
from .audiosystem import set_master_volume  # noqa
from .audiosystem import set_lowpass  # noqa
from .audiosystem import set_vr_audio  # noqa
from .audiosystem import get_audio_system  # noqa
from .audiosystem import stop_all_audio  # noqa
from .sound import ULSound2D, Sound2D  # noqa
from .sound import Sample2D  # noqa
from .sound import Sample3D  # noqa
from .sound import ULSound3D, Sound3D  # noqa
from .sound import ULSpeaker2D, Speaker2D  # noqa
from .sound import ULSpeaker3D, Speaker3D  # noqa
from .sound import play_sound_2d, play_sound_3d  # noqa
from .music import ULMusic, Music  # noqa
