from bge import logic
from bge import events


KEYBOARD_EVENTS = logic.keyboard.inputs
'''Reference to `bge.logic.keyboard.inputs`
'''

_keys_active = {}


def key_event(key: str) -> bool:
    '''Retrieve key event.\n
    Not intended for manual use.
    '''
    key = KEYBOARD_EVENTS[
        getattr(
            events, f'{key.upper()}KEY',
            (getattr(events, f'PAD{key.upper()}', None))
        )
    ]
    if key:
        return key
    else:
        print(f"""
        Key {key} not in [`'A'`, `'B'`, `'C'`, `'D'`, `'E'`, `'F'`, `'G'`, `'H'`, `'I'`, `'J'`, `'K'`, `'L'`, `'M'`, `'N'`, `'O'`, `'P'`, `'Q'`,
        `'R'`, `'S'`, `'T'`, `'U'`, `'V'`, `'W'`, `'X'`, `'Y'`, `'Z'`, `'ZERO'`, `'ONE'`, `'TWO'`, `'THREE'`, `'FOUR'`, `'FIVE'`,
        `'SIX'`, `'SEVEN'`, `'EIGHT'`, `'NINE'`, `'CAPSLOCK'`, `'LEFTCTRLKEY'`, `'LEFTARROW'`, `'DOWNARROW'`, `'RIGHTARROW'`,
        `'UPARROW'`, `'0'`, `'1'`, `'2'`, `'3'`, `'4'`, `'5'`, `'6'`, `'7'`, `'8'`, `'9'`, `'PADPERIOD'`, `'PADSLASH'`, `'PADASTER'`,
        `'PADMINUS'`, `'PADENTER'`, `'PADPLUS'`, `'F1'`, `'F2'`, `'F3'`, `'F4'`, `'F5'`, `'F6'`, `'F7'`, `'F8'`, `'F9'`, `'F10'`,
        `'F11'`, `'F12'`, `'F13'`, `'F14'`, `'F15'`, `'F16'`, `'F17'`, `'F18'`, `'F19'`, `'ACCENTGRAVE'`, `'BACKSLASH'`,
        `'BACKSPACE'`, `'COMMA'`, `'DEL'`, `'END'`, `'EQUAL'`, `'ESC'`, `'HOME'`, `'INSERT'`, `'LEFTBRACKET'`, `'RIGHTBRACKET'`,
        `'LINEFEED'`, `'MINUS'`, `'PAGEDOWN'`, `'PAGEUP'`, `'PAUSE'`, `'PERIOD'`, `'QUOTE'`, `'RET'`, `'ENTER'`, `'SEMICOLON'`,
        `'SLASH'`, `'SPACE'`, `'TAB'`]
        """)
        return 0


def pad_event(key: str) -> bool:
    '''Retrieve Numpad event.\n
    Not intended for manual use.
    '''
    key = KEYBOARD_EVENTS[getattr(events, f'PAD{key}')]
    if key:
        return key
    else:
        print(f"""
        Key {key} not in [`'A'`, `'B'`, `'C'`, `'D'`, `'E'`, `'F'`, `'G'`, `'H'`, `'I'`, `'J'`, `'K'`, `'L'`, `'M'`, `'N'`, `'O'`, `'P'`, `'Q'`,
        `'R'`, `'S'`, `'T'`, `'U'`, `'V'`, `'W'`, `'X'`, `'Y'`, `'Z'`, `'ZERO'`, `'ONE'`, `'TWO'`, `'THREE'`, `'FOUR'`, `'FIVE'`,
        `'SIX'`, `'SEVEN'`, `'EIGHT'`, `'NINE'`, `'CAPSLOCK'`, `'LEFTCTRLKEY'`, `'LEFTARROW'`, `'DOWNARROW'`, `'RIGHTARROW'`,
        `'UPARROW'`, `'0'`, `'1'`, `'2'`, `'3'`, `'4'`, `'5'`, `'6'`, `'7'`, `'8'`, `'9'`, `'PADPERIOD'`, `'PADSLASH'`, `'PADASTER'`,
        `'PADMINUS'`, `'PADENTER'`, `'PADPLUS'`, `'F1'`, `'F2'`, `'F3'`, `'F4'`, `'F5'`, `'F6'`, `'F7'`, `'F8'`, `'F9'`, `'F10'`,
        `'F11'`, `'F12'`, `'F13'`, `'F14'`, `'F15'`, `'F16'`, `'F17'`, `'F18'`, `'F19'`, `'ACCENTGRAVE'`, `'BACKSLASH'`,
        `'BACKSPACE'`, `'COMMA'`, `'DEL'`, `'END'`, `'EQUAL'`, `'ESC'`, `'HOME'`, `'INSERT'`, `'LEFTBRACKET'`, `'RIGHTBRACKET'`,
        `'LINEFEED'`, `'MINUS'`, `'PAGEDOWN'`, `'PAGEUP'`, `'PAUSE'`, `'PERIOD'`, `'QUOTE'`, `'RET'`, `'ENTER'`, `'SEMICOLON'`,
        `'SLASH'`, `'SPACE'`, `'TAB'`]
        """)
        return 0


def key_tap(key: str) -> bool:
    '''Detect key tapped.

    :param `key`: key as `str` of
    [`'A'`, `'B'`, `'C'`, `'D'`, `'E'`, `'F'`, `'G'`, `'H'`, `'I'`, `'J'`, `'K'`, `'L'`, `'M'`, `'N'`, `'O'`, `'P'`, `'Q'`,
    `'R'`, `'S'`, `'T'`, `'U'`, `'V'`, `'W'`, `'X'`, `'Y'`, `'Z'`, `'ZERO'`, `'ONE'`, `'TWO'`, `'THREE'`, `'FOUR'`, `'FIVE'`,
    `'SIX'`, `'SEVEN'`, `'EIGHT'`, `'NINE'`, `'CAPSLOCK'`, `'LEFTCTRLKEY'`, `'LEFTARROW'`, `'DOWNARROW'`, `'RIGHTARROW'`,
    `'UPARROW'`, `'0'`, `'1'`, `'2'`, `'3'`, `'4'`, `'5'`, `'6'`, `'7'`, `'8'`, `'9'`, `'PADPERIOD'`, `'PADSLASH'`, `'PADASTER'`,
    `'PADMINUS'`, `'PADENTER'`, `'PADPLUS'`, `'F1'`, `'F2'`, `'F3'`, `'F4'`, `'F5'`, `'F6'`, `'F7'`, `'F8'`, `'F9'`, `'F10'`,
    `'F11'`, `'F12'`, `'F13'`, `'F14'`, `'F15'`, `'F16'`, `'F17'`, `'F18'`, `'F19'`, `'ACCENTGRAVE'`, `'BACKSLASH'`,
    `'BACKSPACE'`, `'COMMA'`, `'DEL'`, `'END'`, `'EQUAL'`, `'ESC'`, `'HOME'`, `'INSERT'`, `'LEFTBRACKET'`, `'RIGHTBRACKET'`,
    `'LINEFEED'`, `'MINUS'`, `'PAGEDOWN'`, `'PAGEUP'`, `'PAUSE'`, `'PERIOD'`, `'QUOTE'`, `'RET'`, `'ENTER'`, `'SEMICOLON'`,
    `'SLASH'`, `'SPACE'`, `'TAB'`]

    :returns: boolean
    '''
    return key_event(key).activated


def key_down(key: str) -> bool:
    '''Detect key held down.

    :param `key`: key as `str` of
    [`'A'`, `'B'`, `'C'`, `'D'`, `'E'`, `'F'`, `'G'`, `'H'`, `'I'`, `'J'`, `'K'`, `'L'`, `'M'`, `'N'`, `'O'`, `'P'`, `'Q'`,
    `'R'`, `'S'`, `'T'`, `'U'`, `'V'`, `'W'`, `'X'`, `'Y'`, `'Z'`, `'ZERO'`, `'ONE'`, `'TWO'`, `'THREE'`, `'FOUR'`, `'FIVE'`,
    `'SIX'`, `'SEVEN'`, `'EIGHT'`, `'NINE'`, `'CAPSLOCK'`, `'LEFTCTRLKEY'`, `'LEFTARROW'`, `'DOWNARROW'`, `'RIGHTARROW'`,
    `'UPARROW'`, `'0'`, `'1'`, `'2'`, `'3'`, `'4'`, `'5'`, `'6'`, `'7'`, `'8'`, `'9'`, `'PADPERIOD'`, `'PADSLASH'`, `'PADASTER'`,
    `'PADMINUS'`, `'PADENTER'`, `'PADPLUS'`, `'F1'`, `'F2'`, `'F3'`, `'F4'`, `'F5'`, `'F6'`, `'F7'`, `'F8'`, `'F9'`, `'F10'`,
    `'F11'`, `'F12'`, `'F13'`, `'F14'`, `'F15'`, `'F16'`, `'F17'`, `'F18'`, `'F19'`, `'ACCENTGRAVE'`, `'BACKSLASH'`,
    `'BACKSPACE'`, `'COMMA'`, `'DEL'`, `'END'`, `'EQUAL'`, `'ESC'`, `'HOME'`, `'INSERT'`, `'LEFTBRACKET'`, `'RIGHTBRACKET'`,
    `'LINEFEED'`, `'MINUS'`, `'PAGEDOWN'`, `'PAGEUP'`, `'PAUSE'`, `'PERIOD'`, `'QUOTE'`, `'RET'`, `'ENTER'`, `'SEMICOLON'`,
    `'SLASH'`, `'SPACE'`, `'TAB'`]

    :returns: boolean
    '''
    return key_event(key).active


def key_up(key: str) -> bool:
    '''Detect key released.

    :param `key`: key as `str` of
    [`'A'`, `'B'`, `'C'`, `'D'`, `'E'`, `'F'`, `'G'`, `'H'`, `'I'`, `'J'`, `'K'`, `'L'`, `'M'`, `'N'`, `'O'`, `'P'`, `'Q'`,
    `'R'`, `'S'`, `'T'`, `'U'`, `'V'`, `'W'`, `'X'`, `'Y'`, `'Z'`, `'ZERO'`, `'ONE'`, `'TWO'`, `'THREE'`, `'FOUR'`, `'FIVE'`,
    `'SIX'`, `'SEVEN'`, `'EIGHT'`, `'NINE'`, `'CAPSLOCK'`, `'LEFTCTRLKEY'`, `'LEFTARROW'`, `'DOWNARROW'`, `'RIGHTARROW'`,
    `'UPARROW'`, `'0'`, `'1'`, `'2'`, `'3'`, `'4'`, `'5'`, `'6'`, `'7'`, `'8'`, `'9'`, `'PADPERIOD'`, `'PADSLASH'`, `'PADASTER'`,
    `'PADMINUS'`, `'PADENTER'`, `'PADPLUS'`, `'F1'`, `'F2'`, `'F3'`, `'F4'`, `'F5'`, `'F6'`, `'F7'`, `'F8'`, `'F9'`, `'F10'`,
    `'F11'`, `'F12'`, `'F13'`, `'F14'`, `'F15'`, `'F16'`, `'F17'`, `'F18'`, `'F19'`, `'ACCENTGRAVE'`, `'BACKSLASH'`,
    `'BACKSPACE'`, `'COMMA'`, `'DEL'`, `'END'`, `'EQUAL'`, `'ESC'`, `'HOME'`, `'INSERT'`, `'LEFTBRACKET'`, `'RIGHTBRACKET'`,
    `'LINEFEED'`, `'MINUS'`, `'PAGEDOWN'`, `'PAGEUP'`, `'PAUSE'`, `'PERIOD'`, `'QUOTE'`, `'RET'`, `'ENTER'`, `'SEMICOLON'`,
    `'SLASH'`, `'SPACE'`, `'TAB'`]

    :returns: boolean
    '''
    return key_event(key).released


def key_pulse(key: str, time: float = .4) -> bool:
    '''Detect key tapped, then held down after `time` has passed.

    :param `key`: key as `str` of
    [`'A'`, `'B'`, `'C'`, `'D'`, `'E'`, `'F'`, `'G'`, `'H'`, `'I'`, `'J'`, `'K'`, `'L'`, `'M'`, `'N'`, `'O'`, `'P'`, `'Q'`,
    `'R'`, `'S'`, `'T'`, `'U'`, `'V'`, `'W'`, `'X'`, `'Y'`, `'Z'`, `'ZERO'`, `'ONE'`, `'TWO'`, `'THREE'`, `'FOUR'`, `'FIVE'`,
    `'SIX'`, `'SEVEN'`, `'EIGHT'`, `'NINE'`, `'CAPSLOCK'`, `'LEFTCTRLKEY'`, `'LEFTARROW'`, `'DOWNARROW'`, `'RIGHTARROW'`,
    `'UPARROW'`, `'0'`, `'1'`, `'2'`, `'3'`, `'4'`, `'5'`, `'6'`, `'7'`, `'8'`, `'9'`, `'PADPERIOD'`, `'PADSLASH'`, `'PADASTER'`,
    `'PADMINUS'`, `'PADENTER'`, `'PADPLUS'`, `'F1'`, `'F2'`, `'F3'`, `'F4'`, `'F5'`, `'F6'`, `'F7'`, `'F8'`, `'F9'`, `'F10'`,
    `'F11'`, `'F12'`, `'F13'`, `'F14'`, `'F15'`, `'F16'`, `'F17'`, `'F18'`, `'F19'`, `'ACCENTGRAVE'`, `'BACKSLASH'`,
    `'BACKSPACE'`, `'COMMA'`, `'DEL'`, `'END'`, `'EQUAL'`, `'ESC'`, `'HOME'`, `'INSERT'`, `'LEFTBRACKET'`, `'RIGHTBRACKET'`,
    `'LINEFEED'`, `'MINUS'`, `'PAGEDOWN'`, `'PAGEUP'`, `'PAUSE'`, `'PERIOD'`, `'QUOTE'`, `'RET'`, `'ENTER'`, `'SEMICOLON'`,
    `'SLASH'`, `'SPACE'`, `'TAB'`]
    :param time: timeout for key down

    :returns: boolean
    '''
    if key_event(key).activated:
        _keys_active[key] = 0
        return True
    k = _keys_active.get(key, 0)
    _keys_active[key] = k + (1 / logic.getAverageFrameRate())
    if _keys_active[key] > time:
        return key_event(key).active
    return False
