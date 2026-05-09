'''Keyboard input helpers for uplogic. Wraps ``bge.logic.keyboard.inputs`` into
simple boolean query functions. All key-name strings are looked up via
``bge.events`` (e.g. ``'A'``, ``'SPACE'``, ``'F12'``).
'''
from bge import logic
from bge import events
from uplogic import console
from bge.types import SCA_InputEvent


KEYBOARD_EVENTS = logic.keyboard.inputs
'''Reference to ``bge.logic.keyboard.inputs``.'''

_keys_active = {}


class DummyInput:
    '''Fallback input event returned when a key name cannot be resolved, with
    all state flags set to ``False``.
    '''

    active = False
    activated = False
    released = False


def key_event(key: str) -> SCA_InputEvent:
    '''Look up and return the raw ``SCA_InputEvent`` for *key*.

    Not intended for direct use; call :func:`key_tap`, :func:`key_down`, etc. instead.

    :param key: Key name string (e.g. ``'A'``, ``'SPACE'``, ``'F12'``) or a
        ``bge.events`` integer constant.
    :returns: The :class:`~bge.types.SCA_InputEvent` for the key, or ``0`` if
        the key name is not recognised.
    '''
    if isinstance(key, int):
        key = KEYBOARD_EVENTS.get(key, DummyInput())
    else:
        key = KEYBOARD_EVENTS.get(
        getattr(
            events, f'{key.upper()}KEY',
            (getattr(events, f'PAD{key.upper()}', None))
        ), DummyInput())
    if key:
        return key
    else:
        console.error(f"""
        Key {key} not in [`'A'`, `'B'`, `'C'`, `'D'`, `'E'`, `'F'`, `'G'`, `'H'`, `'I'`, `'J'`, `'K'`, `'L'`, `'M'`, `'N'`, `'O'`, `'P'`, `'Q'`,
        `'R'`, `'S'`, `'T'`, `'U'`, `'V'`, `'W'`, `'X'`, `'Y'`, `'Z'`, `'ZERO'`, `'ONE'`, `'TWO'`, `'THREE'`, `'FOUR'`, `'FIVE'`,
        `'SIX'`, `'SEVEN'`, `'EIGHT'`, `'NINE'`, `'CAPSLOCK'`, `'LEFTCTRL'`, `'LEFTSHIFT'` `'LEFTARROW'`, `'DOWNARROW'`, `'RIGHTARROW'`,
        `'UPARROW'`, `'0'`, `'1'`, `'2'`, `'3'`, `'4'`, `'5'`, `'6'`, `'7'`, `'8'`, `'9'`, `'PADPERIOD'`, `'PADSLASH'`, `'PADASTER'`,
        `'PADMINUS'`, `'PADENTER'`, `'PADPLUS'`, `'F1'`, `'F2'`, `'F3'`, `'F4'`, `'F5'`, `'F6'`, `'F7'`, `'F8'`, `'F9'`, `'F10'`,
        `'F11'`, `'F12'`, `'F13'`, `'F14'`, `'F15'`, `'F16'`, `'F17'`, `'F18'`, `'F19'`, `'ACCENTGRAVE'`, `'BACKSLASH'`,
        `'BACKSPACE'`, `'COMMA'`, `'DEL'`, `'END'`, `'EQUAL'`, `'ESC'`, `'HOME'`, `'INSERT'`, `'LEFTBRACKET'`, `'RIGHTBRACKET'`,
        `'LINEFEED'`, `'MINUS'`, `'PAGEDOWN'`, `'PAGEUP'`, `'PAUSE'`, `'PERIOD'`, `'QUOTE'`, `'RET'`, `'ENTER'`, `'SEMICOLON'`,
        `'SLASH'`, `'SPACE'`, `'TAB'`]
        """)
        return 0


def pad_event(key: str) -> bool:
    '''Look up and return the raw ``SCA_InputEvent`` for a numpad *key*.

    Not intended for direct use.

    :param key: Numpad key suffix (e.g. ``'0'``, ``'ENTER'``, ``'PLUS'``).
    :returns: The :class:`~bge.types.SCA_InputEvent`, or ``0`` if not found.
    '''
    key = KEYBOARD_EVENTS[getattr(events, f'PAD{key}')]
    if key:
        return key
    else:
        console.error(f"""
        Key {key} not in [`'A'`, `'B'`, `'C'`, `'D'`, `'E'`, `'F'`, `'G'`, `'H'`, `'I'`, `'J'`, `'K'`, `'L'`, `'M'`, `'N'`, `'O'`, `'P'`, `'Q'`,
        `'R'`, `'S'`, `'T'`, `'U'`, `'V'`, `'W'`, `'X'`, `'Y'`, `'Z'`, `'ZERO'`, `'ONE'`, `'TWO'`, `'THREE'`, `'FOUR'`, `'FIVE'`,
        `'SIX'`, `'SEVEN'`, `'EIGHT'`, `'NINE'`, `'CAPSLOCK'`, `'LEFTCTRL'`, `'LEFTSHIFT'` `'LEFTARROW'`, `'DOWNARROW'`, `'RIGHTARROW'`,
        `'UPARROW'`, `'0'`, `'1'`, `'2'`, `'3'`, `'4'`, `'5'`, `'6'`, `'7'`, `'8'`, `'9'`, `'PADPERIOD'`, `'PADSLASH'`, `'PADASTER'`,
        `'PADMINUS'`, `'PADENTER'`, `'PADPLUS'`, `'F1'`, `'F2'`, `'F3'`, `'F4'`, `'F5'`, `'F6'`, `'F7'`, `'F8'`, `'F9'`, `'F10'`,
        `'F11'`, `'F12'`, `'F13'`, `'F14'`, `'F15'`, `'F16'`, `'F17'`, `'F18'`, `'F19'`, `'ACCENTGRAVE'`, `'BACKSLASH'`,
        `'BACKSPACE'`, `'COMMA'`, `'DEL'`, `'END'`, `'EQUAL'`, `'ESC'`, `'HOME'`, `'INSERT'`, `'LEFTBRACKET'`, `'RIGHTBRACKET'`,
        `'LINEFEED'`, `'MINUS'`, `'PAGEDOWN'`, `'PAGEUP'`, `'PAUSE'`, `'PERIOD'`, `'QUOTE'`, `'RET'`, `'ENTER'`, `'SEMICOLON'`,
        `'SLASH'`, `'SPACE'`, `'TAB'`]
        """)
        return 0


def key_tap(key: str) -> bool:
    '''Return ``True`` on the single frame a key is first pressed.

    :param key: Key name string (e.g. ``'A'``, ``'SPACE'``, ``'F12'``) or a
        ``bge.events`` integer constant.
    :returns: ``True`` on the activation frame, ``False`` otherwise.
    '''
    return key_event(key).activated


def key_down(key: str) -> bool:
    '''Return ``True`` while a key is held down (including the first frame).

    :param key: Key name string or ``bge.events`` integer constant.
    :returns: ``True`` while the key is active or activated.
    '''
    key = key_event(key)
    return key.active or key.activated


def key_press(key: str, down=False):
    '''Return ``True`` when a key is tapped, or (when *down* is ``True``) also
    while it is held.

    :param key: Key name string or ``bge.events`` integer constant.
    :param down: When ``True``, also return ``True`` while the key is held.
    :returns: ``True`` on activation, or while active when *down* is ``True``.
    '''
    key = key_event(key)
    return key.active or key.activated if down else key.activated



def key_up(key: str) -> bool:
    '''Return ``True`` on the single frame a key is released.

    :param key: Key name string or ``bge.events`` integer constant.
    :returns: ``True`` on the release frame, ``False`` otherwise.
    '''
    return key_event(key).released


def key_pulse(key: str, time: float = .4) -> bool:
    '''Return ``True`` on the first press and again once the key has been held
    for more than *time* seconds (useful for auto-repeat, e.g. scrolling).

    :param key: Key name string or ``bge.events`` integer constant.
    :param time: Hold duration in seconds before continuous activation begins.
    :returns: ``True`` on the tap frame or while held past *time*.
    '''
    evt = key_event(key)
    if evt.activated:
        _keys_active[key] = 0
        return True
    k = _keys_active.get(key, 0)
    _keys_active[key] = k + (1 / (logic.getAverageFrameRate() or 0.01))
    if _keys_active[key] > time:
        return evt.active
    return False


class RecordedCharacter(tuple):
    '''Named-tuple-like wrapper for a single keyboard event recorded by
    :func:`record_keyboard`.

    Attributes are accessed via read-only properties: :attr:`pressed`,
    :attr:`keycode`, and :attr:`character`.
    '''

    @property
    def pressed(self):
        '''``True`` when the key contributed a printable character or *all* was ``True``.'''
        return self[0]

    @property
    def keycode(self):
        '''Integer ``bge.events`` key constant.'''
        return self[1]

    @property
    def character(self):
        '''Printable character string, or an empty string for non-character keys.'''
        return self[2]


def record_keyboard(down=True, all=False) -> list[RecordedCharacter[bool, int, str]]:
    '''Collect all currently active keyboard events into a list of
    :class:`RecordedCharacter` entries.

    :param down: When ``True``, record continuously while held; when ``False``,
        record only on the activation frame.
    :param all: When ``True``, include non-character keys (arrows, F-keys, etc.)
        with an empty character string.
    :returns: List of :class:`RecordedCharacter` tuples ``(pressed, keycode, character)``.
    '''
    left_shift = KEYBOARD_EVENTS[events.LEFTSHIFTKEY].active
    right_shift = KEYBOARD_EVENTS[events.RIGHTSHIFTKEY].active
    active_events = logic.keyboard.activeInputs.copy()

    func = key_down if down else key_pulse

    evts = []

    for keycode in active_events:
        if func(keycode):
            event = active_events[keycode]
            char = events.EventToCharacter(
                event.type,
                left_shift or right_shift
            )
            evts.append(RecordedCharacter((
                True if char or all else False,
                keycode,
                char
            )))
    return evts


def keyboard_active() -> bool:
    '''Return ``True`` when any keyboard input event is currently registered.

    :returns: ``True`` if ``KEYBOARD_EVENTS`` is non-empty.
    '''
    return len(KEYBOARD_EVENTS) > 0
