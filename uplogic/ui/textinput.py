from .widget import Widget
import blf
from uplogic.utils.math import clamp
from uplogic.ui.label import Label
from uplogic.ui.layout import Layout
from bge import logic
from bge import events
import math
from uplogic.events import schedule


class TextInput(Label):
    '''Editable text widget.

    Extends :class:`~uplogic.ui.label.Label` with keyboard input capture and
    a blinking cursor.  When :attr:`edit` is ``True`` all keyboard events are
    consumed and reflected in :attr:`text`.

    :param pos: Position in pixels or factor.
    :param relative: Relative positioning/sizing flags.
    :param text: Initial text content.
    :param font: Font file path.
    :param font_color: RGBA text colour.
    :param font_size: Font size in pt or factor.
    :param line_height: Line spacing factor.
    :param shadow: Enable drop shadow.
    :param shadow_offset: ``[x, y]`` shadow offset in pixels.
    :param shadow_color: RGBA shadow colour.
    :param halign: Widget horizontal alignment.
    :param valign: Widget vertical alignment.
    :param wrap: Break long lines to fit inside the parent's width.
    :param multiline: Allow multi-line input.  When ``False``, pressing Enter
        calls :meth:`on_enter` (default: exit edit mode).
    :param angle: Rotation in degrees.
    '''

    def __init__(
        self,
        pos=[0, 0],
        relative={},
        text='',
        font='',
        font_color=[1., 1., 1., 1.],
        font_size=12,
        line_height=1.5,
        shadow=False,
        shadow_offset=[1, -1],
        shadow_color=[.0, .0, .0, 1.0],
        halign='left',
        valign='bottom',
        wrap=False,
        multiline=False,
        angle=0
    ):
        self._edit = False
        self.lines = None
        self.cursor_evt = None
        self.cursor = Layout(bg_color=(1, 1, 1, 1), size=(0, 0), relative={'pos': False})
        self.cursor_flash_time = .5
        Label.__init__(self, pos=pos, relative=relative, text=text, font=font, font_color=font_color, font_size=font_size, line_height=line_height, shadow=shadow, shadow_offset=shadow_offset, shadow_color=shadow_color, halign=halign, valign=valign, wrap=wrap, angle=angle)
        self.add_widget(self.cursor)
        self.cursor.show = False
        self._key_evts = {}
        events = logic.keyboard.inputs.copy()
        for evt in events.values():
            self._key_evts[evt] = 0.0
        self.multiline = multiline
        self.edit = False
        self._index = 0
        self.line_index = 0
        self.character_index = 0

    def on_enter(self):
        '''Called when Enter is pressed in single-line mode.  Default exits edit mode.  Override to customise.'''
        self.edit = False

    @property
    def edit(self):
        '''When ``True`` the widget captures keyboard events and shows the blinking cursor.
        Setting to ``True`` also moves the cursor to the end of the text.
        '''
        return self._edit

    @edit.setter
    def edit(self, val):
        if val:
            if not self._edit:
                self.index = len(self.text)
            self.cursor.show = True
            if self.cursor_evt:
                self.cursor_evt.cancel()
            self.cursor_evt = schedule(self._cursor_visible, self.cursor_flash_time)
        else:
            self.cursor.show = False
            if self.cursor_evt:
                self.cursor_evt.cancel()
        self._edit = val

    @property
    def index(self):
        '''Cursor insertion position in the full text string.
        Setting also updates ``line_index`` and ``character_index``.
        '''
        return self._index

    @index.setter
    def index(self, val):
        val = clamp(val, 0, len(self.text))
        character_index = val
        line_index = 0
        for line in self.lines:
            if character_index > len(line) and (line != '' or line_index != len(self.lines)):
                line_index += 1
                character_index -= len(line) + 1
            else:
                break
        self._index = val
        self.line_index = line_index
        self.character_index = character_index

    @property
    def text(self):
        '''Full text content.  Setting cancels the cursor blink timer and resets it if in edit mode.'''
        return self._text

    @text.setter
    def text(self, val):
        if self.cursor_evt:
            self.cursor_evt.cancel()
        self.cursor.show = False
        if self.edit:
            self._cursor_visible()
        self._text = str(val)

    def move_cursor_to_end(self):
        '''Place the cursor after the last character and enter edit mode.'''
        line_length = len(self.lines[clamp(self.line_index, 0, len(self.lines) - 1)])
        self.index = len(self.text) #line_length - self.character_index
        self.edit = True

    def write(self, text):
        '''Append *text* to the current content and advance the cursor.

        :param text: String to append.
        '''
        self.text += text
        self.index = len(self.text)

    @property
    def _current_char_pos(self):
        self.index = self.index
        relative = self.relative.get('font_size', False)
        fontsize = self.parent._draw_size[1] * self.font_size if relative else self.font_size
        blf.size(self.font, fontsize)
        if len(self.lines) > 0:
            text = self.lines[self.line_index]
            text = text[0 : self.character_index]
            dim = blf.dimensions(self.font, text)
            # lines = len(self.lines) or 1
            return [dim[0], blf.dimensions(self.font, 'A')[1] * (self.line_index + 1) * self.line_height]
        else:
            return (0, 0)

    def _cursor_visible(self):
        self.cursor.show = not self.cursor.show
        self.cursor_evt = schedule(self._cursor_visible, self.cursor_flash_time)

    def _set_cursor_position(self):
        dsize = self._current_char_pos
        dim = blf.dimensions(self.font, self.lines[self.line_index])
        charsize = blf.dimensions(self.font, 'A')
        if self.text_halign == 'center':
            dsize[0] -= dim[0] * .5
        if self.text_halign == 'right':
            dsize[0] -= dim[0]
        if self.text_valign == 'center':
            dsize[1] *= -.5
        if self.text_valign == 'top':
            dsize[1] *= -1
        self.cursor.pos[0] = dsize[0]
        self.cursor.pos[1] = 0
        self.cursor.height = self.font_size * .9
        self.cursor.width = 1

    def on_tab(self):
        '''Called when Tab is pressed.  Default exits edit mode.  Override to customise.'''
        self.edit = False

    def _listen(self):
        left_shift = logic.keyboard.inputs[events.LEFTSHIFTKEY].active
        right_shift = logic.keyboard.inputs[events.RIGHTSHIFTKEY].active
        keyboard_events = logic.keyboard.inputs.copy()
        tpf = (1 / (logic.getAverageFrameRate() or 0.01))
        self._rebuild = True

        for i, evt in keyboard_events.items():
            text = self.text
            if evt.active and self._key_evts[evt] == 0.0:
                self._key_evts[evt] += tpf
                if evt.type == 59:
                    self.text = text[:self.index][:-1] + text[self.index:]  # Backspace:
                    self.index -= 1
                    return
                if not self.multiline and evt.type == 7:
                    self.on_enter()
                    return
                if evt.type == 57:  # Arrow Left
                    self.on_tab()
                    self.edit = False
                if evt.type == 69:  # Arrow Left
                    self.index -= 1
                    self.edit = True
                if evt.type == 71:  # Arrow Right
                    self.index += 1
                    self.edit = True
                if len(self.lines) <= 0:
                    return
                line_length = len(self.lines[clamp(self.line_index, 0, len(self.lines) - 1)])
                if evt.type == 110:  # Home
                    self.index -= line_length - (line_length - self.character_index)
                    self.edit = True
                if evt.type == 113:  # End
                    self.index += line_length - self.character_index
                    self.edit = True
                # if evt.type == 70:  # Arrow Down
                # if evt.type == 72:  # Arrow Up
                char = events.EventToCharacter(evt.type, left_shift or right_shift)
                if not char:
                    continue
                self.text = text[:self.index] + char + text[self.index:]
                self.index += 1
            elif evt.active:
                self._key_evts[evt] += tpf
                if self._key_evts[evt] > .4:
                    if evt.type == 59:
                        self.text = text[:self.index - 1][:-1] + text[self.index:]  # Backspace:
                        self.index -= 1
                        return
                    if not self.multiline and evt.type == 7:  # Enter
                        self.edit = False
                        return
                    if evt.type == 69:  # Arrow Left
                        self.index -= 1
                        self.edit = True
                    if evt.type == 71:  # Arrow Right
                        self.index += 1
                        self.edit = True
                    text = self.text
                    char = events.EventToCharacter(evt.type, left_shift or right_shift)
                    if not char:
                        continue
                    self.text = text[:self.index] + char + text[self.index:]
                    self.index += 1
            elif evt.inactive:
                self._key_evts[evt] = 0.0

    def move_cursor(self, line, position):
        raise NotImplementedError

    def draw(self):
        if self.edit:
            self._listen()
        super().draw()
        self._set_cursor_position()