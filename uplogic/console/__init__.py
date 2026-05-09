'''In-game on-screen console for uplogic.

Provides a :class:`ConsoleLayout` overlay that can be toggled at runtime,
routes ``stdout`` through it, and exposes typed log helpers (``log``,
``debug``, ``info``, ``warning``, ``error``, ``critical``).  An optional
log file is written when :attr:`ConsoleLayout.log_directory` is set.

Typical usage::

    from uplogic import console

    console.enable()          # show overlay; toggle with F12 by default
    console.info('Ready.')
    console.warning('Low memory.')
    console.error('Unhandled exception.')

    # set log level so only warnings and above are shown
    console.set_log_level(3)

The module is enabled automatically when the ``bge_netlogic`` add-on is
present and ``use_screen_console`` is set on the scene.
'''

from bge import logic, render
from io import StringIO
from uplogic.ui.canvas import Canvas
from uplogic.ui.layout import RelativeLayout
from uplogic.ui.label import Label
from uplogic.ui.textinput import TextInput
from uplogic.data import GlobalDB
from uplogic.utils.raycasting import raycast_screen
from uplogic.utils.scene import world_to_screen
from uplogic.utils.math import cycle
from uplogic.utils.math import clamp
from uplogic.input.keyboard import key_down, key_pulse
from uplogic.input.mouse import mouse_down, mouse_wheel
import bpy, blf
import bge
import sys, os
from datetime import datetime
from mathutils import Vector
import uplogic


GLOBALS = {}


def set_global(key, val):
    '''Register a name/value pair that will be available inside expressions
    executed through the on-screen console.

    :param key: Variable name as it will appear in the exec namespace.
    :param val: Value to bind to that name.
    '''
    global GLOBALS
    GLOBALS[key] = val


def _get_globals():
    '''Return the exec namespace populated with common BGE/BPY bindings and
    all current-scene objects, used by :meth:`ConsoleLayout.on_enter`.
    '''
    scene = logic.getCurrentScene()
    global GLOBALS
    GLOBALS['scene'] = scene
    GLOBALS['bpy'] = bpy
    GLOBALS['bge'] = bge
    GLOBALS['uplogic'] = uplogic
    GLOBALS['logic'] = logic
    GLOBALS['render'] = render
    GLOBALS['console'] = get_console(True)
    for obj in scene.objects:
        GLOBALS[obj.blenderObject.name] = obj
    return GLOBALS


def enable(toggle_key='F12', visible=False):
    '''Activate the on-screen console for the current scene.

    Creates the :class:`ConsoleLayout` overlay if it does not already exist,
    hooks it into the scene pre-draw list, and redirects ``sys.stdout`` so
    that ``print()`` output is captured and displayed in the overlay.

    :param toggle_key: Keyboard key name used to show/hide the console.
    :param visible: Whether the console starts visible.
    '''
    scene = logic.getCurrentScene()
    c = get_console(True, toggle_key=toggle_key, visible=visible)
    c.scene = scene
    if disable not in scene.onRemove:
        scene.onRemove.append(disable)
    if c.update not in scene.pre_draw:
        c.register()
        scene.pre_draw.append(c.update)
    sys.stdout = Console()


def disable():
    '''Deactivate the on-screen console.

    Restores ``sys.stdout`` and ``sys.stderr``, stops the
    :class:`ConsoleLayout`, and removes it from the global registry.
    '''
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    console = get_console(True)
    if console:
        console.stop()
    consoles = GlobalDB.retrieve('uplogic.consoles')
    consoles.remove('default')


class Console(StringIO):
    '''``sys.stdout`` replacement that routes all writes through
    :func:`_print` so they appear in the on-screen console.
    '''

    def write(self, __s: str) -> int:
        _print(__s)


class ErrorConsole(StringIO):
    '''``sys.stderr`` replacement that routes all writes through
    :func:`error` so they appear in the on-screen console at error level.
    '''

    def write(self, __s: str) -> int:
        error(__s)

COLORS = {
    'LOG': [1, 1, 1, 1],
    'INFO': [.3, .8, 1, 1],
    'DEBUG': [1, 1, .6, 1],
    'WARNING': [1, .8, .2, 1],
    'ERROR': [1, .3, .3, 1],
    'CRITICAL': [1, .0, .0, 1],
    'SUCCESS': [.3, 1, .3, 1]
}
'''RGBA font colours used by :class:`ConsoleLayout` for each log level.'''


class CommandLabel(Label):
    '''Label variant used to render command-echo lines in the console overlay.'''
    pass


def set_log_level(level: int = 2) -> None:
    '''Set the minimum severity level for messages shown in the console.

    Messages below the given level are silently discarded.

    ====  ==========
    0     No restrictions (all messages)
    1     Debug and above
    2     Info and above *(default)*
    3     Warning and above
    4     Error and above
    5     Critical only
    ====  ==========

    :param level: Log level in the range ``[0, 5]``.
    '''
    get_console().log_level = clamp(level, 0, 5)


def set_log_directory(path):
    '''Set the directory where log files are written.

    A new numbered ``log.<n>.txt`` file is created inside *path* each session.
    Pass ``None`` to disable file logging.

    :param path: Filesystem path to the log directory, or ``None``.
    '''
    get_console().log_directory = path


class ConsoleLayout(Canvas):
    '''On-screen console overlay widget.

    Rendered as a :class:`~uplogic.ui.canvas.Canvas` panel that displays
    timestamped log messages, accepts typed commands through a
    :class:`~uplogic.ui.textinput.TextInput` widget, and writes output to an
    optional log file.  Typically created and managed via :func:`enable` and
    :func:`get_console` rather than instantiated directly.

    :param toggle_key: Keyboard key name used to show/hide the console.
    :param visible: Whether the console starts visible.
    '''

    opacity = 1
    padding = [5, 10]
    toggle_key = 'F12'

    @property
    def log_directory(self):
        '''Path to the directory where log files are written. Setting this
        creates the directory if it does not already exist and opens a new
        numbered log file inside it. Set to ``None`` to disable file logging.
        '''
        return self._log_directory

    @log_directory.setter
    def log_directory(self, folder):
        if folder is not None:
            if not os.path.isdir(folder):
                os.makedirs(folder)
            self._log_file = os.path.join(
                folder,
                f'log.{len(os.listdir(folder))}.txt'
            )
        else:
            self._log_file = None
        self._log_directory = folder

    @property
    def log_file(self):
        '''Full path of the currently active log file, or ``None`` if file
        logging is disabled (read-only). Set :attr:`log_directory` to change
        where logs are written.
        '''
        return self._log_file

    @log_file.setter
    def log_file(self, val):
        error("'ConsoleLayout.log_file' is read-only!")
    
    def __init__(self, toggle_key='F12', visible=False): 
        self.log_directory = None
        scene = logic.getCurrentScene()
        log_levels = {
            'NOTSET': 0,
            'DEBUG': 1,
            'INFO': 2,
            'WARNING': 3,
            'ERROR': 4,
            'CRITICAL': 5
        }
        self.log_level = log_levels.get(bpy.data.scenes[scene.name].game_settings.log_level)
        self.toggle_key = toggle_key
        self._mouse_visible = False
        self.issued_commands = []
        self._mouse_down = False
        self._goback_index = -1
        super().__init__()
        self.input = TextInput(text='', shadow=True, valign='center')
        self.input.on_enter = self.on_enter
        self.input.edit = True
        self.console = RelativeLayout(relative={'size': True, 'pos': True}, pos=[0, 0], size=(1, .4))
        self._layout = self.console
        self.layout = RelativeLayout(relative={'size': True}, size=(1, 1), bg_color=[0, 0, 0, .4])
        self.layout.use_clipping = True
        self.add_widget(self.console)
        self.console.add_widget(self.layout)
        self.layout.add_widget(self.input)
        self.fade_event = None
        self._toggle_key = False
        self._prev_msg = None
        if disable not in scene.onRemove:
            scene.onRemove.append(disable)
        if self.update not in scene.pre_draw:
            scene.pre_draw.append(self.update)
        self.nameplate = Label(text='', shadow=True, relative={'pos': True}, halign='center', font_size=13)
        self.nameplate.update = self.update_nameplate
        self.canvas.add_widget(self.nameplate)
        self.font_size = 12
        self.position = 'bottom'
        self.info_mode = getattr(bpy.context.scene, 'screen_console_open', False)
        self.active = False

    @property
    def layout(self):
        '''The inner :class:`~uplogic.ui.layout.RelativeLayout` that holds log
        message labels. Replacing this widget migrates all existing children
        to the new layout.
        '''
        return self._layout

    @layout.setter
    def layout(self, val):
        for w in self._layout.children:
            val.add_widget(w)
        self._layout = val

    @property
    def info_mode(self):
        '''When ``True`` the overlay background is always shown and the input
        field is only hidden (not the whole canvas) when the console is
        inactive. Toggling this re-applies the :attr:`active` state.
        '''
        return self._info_mode

    @info_mode.setter
    def info_mode(self, val):
        self._info_mode = val
        self.active = self.active

    @property
    def active(self):
        '''Whether the console is currently open and accepting input. In
        :attr:`info_mode` the background stays visible and only the input field
        is toggled; otherwise the entire overlay is shown or hidden.
        '''
        return self._active

    @active.setter
    def active(self, val):
        if self.info_mode:
            self.show = True
            self.layout.bg_color = (0, 0, 0, .4) if val else (0, 0, 0, 0)
            self.input.show = val
            self.nameplate.show = val
        else:
            self.show = val
        self._active = val

    @property
    def position(self):
        '''Docking position of the console panel. Accepted values:
        ``"bottom"`` *(default)*, ``"top"``, ``"left"``, ``"right"``,
        ``"center"``. Setting this repositions and resizes the panel immediately.
        '''
        return self._position

    @position.setter
    def position(self, val):
        if val == 'center':
            self.console.valign = val
            self.console.halign = val
            self.console.pos = (.5, .5)
            self.console.size = (.4, .4)
            self._position = val
        elif val == 'left':
            self.console.valign = 'bottom'
            self.console.halign = val
            self.console.size = (.4, 1)
            self.console.pos = (0, 0)
            self._position = val
        elif val == 'right':
            self.console.valign = 'bottom'
            self.console.halign = val
            self.console.pos = (1, 0)
            self.console.size = (.4, 1)
            self._position = val
        elif val == 'top':
            self.console.valign = 'top'
            self.console.halign = 'left'
            self.console.pos = (0, 1)
            self.console.size = (1, .4)
            self._position = val
        elif val == 'bottom':
            self.console.valign = 'bottom'
            self.console.halign = 'left'
            self.console.pos = (0, 0)
            self.console.size = (1, .4)
            self._position = val
        else:
            error(f'"{val}" not recognized.')
        self.arrange()

    @property
    def font_size(self):
        '''Font size in pixels for all console labels, clamped to ``[5, 30]``.
        Setting this updates every existing label and triggers a layout pass.
        '''
        return self._font_size

    @font_size.setter
    def font_size(self, val):
        val = clamp(val, 5, 30)
        self._font_size = int(val)
        for c in self.layout.children:
            c.font_size = int(val)
        self.nameplate.font_size = int(val)
        self.arrange()

    def on_enter(self):
        '''Handle the user pressing Enter in the input field.

        Echoes the typed text, looks up a registered :class:`Command`, and
        falls back to ``exec()`` in the :func:`_get_globals` namespace.
        Clears the input field afterwards.
        '''
        if self.input.text:
            self.issued_commands.append(self.input.text)
        sys.__stdout__.write(f'>{self.input.text}\n')
        self.add_message(f'>{self.input.text}')
        command_name = self.input.text.split(' ')[0]
        command = Commands.commands.get(command_name)
        if command:
            command.invoke(self.input.text)
        else:
            try:
                exec(self.input.text, _get_globals())
            except Exception as e:
                error(f'Error occured when executing command "{command_name}":\n{e}')
        self._goback_index = -1
        self.input.text = ''
        self.input.edit = True

    def update_nameplate(self):
        '''Per-frame nameplate update: cast a ray from the cursor, show the
        object name under it, and insert the name into the input field on click.
        '''
        ray = raycast_screen()
        mdown = mouse_down()
        if ray.obj:
            self.nameplate.pos = world_to_screen(ray.point) + Vector((0, .01))
            self.nameplate.text = ray.obj.blenderObject.name
            if mdown and not self._mouse_down:
                self.input.write(self.nameplate.text)
        else:
            self.nameplate.text = ''
        self._mouse_down = mdown

    def toggle(self):
        '''Show or hide the console and update mouse visibility accordingly.
        A guard flag prevents repeated toggling while the key is held.
        '''
        if not self.show:
            self._mouse_visible = logic.mouse.visible
        if not self._toggle_key:
            self.active = not self.active
            self.opacity = 1
            self._toggle_key = True

    def update(self):
        '''Per-frame update: poll the toggle key, handle up/down arrow history
        navigation, and sync mouse visibility with the console state.

        Called automatically via the BGE scene pre-draw list.
        '''
        if self.input.edit != self.show:
            self.input.edit = self.show
        move_goback = key_pulse('UPARROW') - key_pulse('DOWNARROW')
        if key_down(self.toggle_key):
            self.toggle()
        elif not self.show:
            self._toggle_key = False
            return
        elif move_goback:
            if not self.issued_commands:
                pass
            elif not self._toggle_key:
                self._goback_index = clamp(self._goback_index + move_goback, -1, len(self.issued_commands) - 1)
                if self._goback_index < 0:
                    self.input.text = ''
                else:
                    self.input.text = list(self.issued_commands.__reversed__())[self._goback_index]
                self.input.move_cursor_to_end()
            self._toggle_key = True
        else:
            self._toggle_key = False
        logic.mouse.visible = self.active or self._mouse_visible

    def stop(self):
        '''Remove all log labels and unregister the toggle callback from the
        scene pre-draw list.
        '''
        self.clear()
        scene = logic.getCurrentScene()
        if self.toggle in scene.pre_draw:
            scene.pre_draw.remove(self.toggle)

    def add_message(self, msg, type='LOG', time=True, command=False):
        '''Append a log message label to the console overlay.

        Consecutive single-space messages are merged onto the previous label.
        After adding the label :meth:`arrange` is called to reflow the stack.

        :param msg: Text to display.
        :param type: One of the keys in :data:`COLORS` (``"LOG"``,
            ``"INFO"``, ``"DEBUG"``, ``"WARNING"``, ``"ERROR"``,
            ``"CRITICAL"``, ``"SUCCESS"``).
        :param time: When ``True`` prefix the message with the current time.
        :param command: When ``True`` use :class:`CommandLabel` instead of
            a plain :class:`~uplogic.ui.label.Label`.
        '''
        if (msg == ' ' or self._prev_msg == ' ') and len(self.layout.children):
            self.layout.children[-1].text += msg
            self._prev_msg = msg
            return
        now = datetime.now()
        current_time = f'[{now.strftime("%H:%M:%S")}]' if time else "\t\t\t\t  ".replace('\t', '    ')
        label_class = CommandLabel if command else Label
        self.layout.add_widget(label_class(text=f'{current_time}  {msg}', pos=[5, 10], font_color=COLORS[type], shadow=True, font_size=self.font_size))
        self._prev_msg = msg
        self.arrange()

    def arrange(self):
        '''Reflow all message labels from the bottom of the layout upwards,
        fade out older labels, and remove any that have scrolled off the top.
        Also repositions the input field.
        '''
        blf.size(0, self.font_size)
        dim = blf.dimensions(0, 'A')
        cheight = dim[1]
        cwidth = dim[0]
        lheight = self.layout._draw_size[1]
        amount = lheight / cheight
        y = cheight * 2.4 * 1.5
        for i, child in enumerate(self.layout._children_reversed):
            if child is self.input:
                continue
            child.pos[1] = y
            y += cheight * 1.5
            if child.pos[1] > lheight - cheight:
                self.layout.remove_widget(child)
            child.opacity = 1 - (i * (1/amount))
            child.shadow_color[3] = child.font_color[3]
        self.input.pos[1] = self.font_size + 3
        self.input.pos[0] = cwidth


def get_console(create=False, toggle_key='F12', visible=False) -> ConsoleLayout:
    '''Return the active :class:`ConsoleLayout`, optionally creating it.

    :param create: When ``True``, create a new :class:`ConsoleLayout` if one
        does not already exist in the global registry.
    :param toggle_key: Toggle key forwarded to :class:`ConsoleLayout` on
        creation (ignored if the console already exists).
    :param visible: Initial visibility forwarded on creation.
    :returns: The :class:`ConsoleLayout` instance, or ``None`` if *create* is
        ``False`` and no console has been created yet.
    '''
    consoles = GlobalDB.retrieve('uplogic.consoles')
    console = consoles.get('default')
    if console is None and create:
        console = ConsoleLayout(toggle_key=toggle_key, visible=visible)
        consoles.put('default', console)
        console.add_message('On-Screen Console active; Check System Console for Errors.', type='DEBUG')
    return console


class ansicol:
    '''ANSI escape-code constants used to colourise system-console output.'''
    RED = '\033[31m\033[1m'
    GREEN = '\033[32m\033[1m'
    YELLOW = '\033[33m'
    BYELLOW = '\033[93m'
    BBLUE = '\033[36m'
    END = '\033[0m'


def write(*msg, type='LOG'):
    '''Write one or more values to the console using the given log type.

    Objects that are not strings are converted with ``repr()``.

    :param msg: Values to log (joined with spaces).
    :param type: One of ``"LOG"``, ``"SUCCESS"``, ``"DEBUG"``, ``"INFO"``,
        ``"WARNING"``, ``"ERROR"``, ``"CRITICAL"``.
    '''
    msg = ' '.join([m.__repr__() if not isinstance(m, str) else m for m in msg])
    _f = {
        'LOG': log,
        'INFO': info,
        'DEBUG': debug,
        'WARNING': warning,
        'ERROR': error,
        'SUCCESS': success
    }

    _f[type](msg)


def _create_msg(msg, log_lvl, type: str, color):
    '''Internal helper: format and route a log message to the overlay and
    system console if the current log level permits it.
    '''
    console = get_console(True)
    if console is None:
        print(sysmsg)
        return
    if console.log_level > log_lvl:
        return

    msg = ' '.join([m.__repr__() if not isinstance(m, str) else m for m in msg])
    msg += '\n'
    sysmsg = f'{color}{type}{ansicol.END}: {msg}'
    show_time = True
    sys.__stdout__.write(f'{sysmsg}')
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            console.add_message(f'{msg}', type.upper(), time=show_time)
            show_time = False
            if console.log_file is not None:
                with open(console.log_file, 'a') as f:
                    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f'[{date}][{type}]\t{msg}\n')


def _print(msg):
    '''Internal helper: route a raw ``print()``/``stdout`` write to the
    overlay and system console without a log-level prefix or colour.
    '''
    console = get_console(True)
    if console is None:
        print(sysmsg)
        return

    msg = ''.join([m.__repr__() if not isinstance(m, str) else m for m in msg])
    sysmsg = msg
    show_time = True
    sys.__stdout__.write(f'{sysmsg}')
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            console.add_message(f'{msg}', 'LOG', time=show_time)
            show_time = False
            if console.log_file is not None:
                with open(console.log_file, 'a') as f:
                    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f'[{date}]\t{msg}\n')


def log(*msg, type='LOG'):
    '''Write one or more values to the console.

    Always shown regardless of the current log level.  If
    :attr:`ConsoleLayout.log_directory` is set, also appends to the log file.

    :param msg: Values to log (joined with spaces; non-strings use ``repr()``).
    :param type: Message type — one of ``"LOG"``, ``"SUCCESS"``, ``"DEBUG"``,
        ``"INFO"``, ``"WARNING"``, ``"ERROR"``, ``"CRITICAL"``.
    '''
    _create_msg(msg, 5, type, '')


def success(*msg):
    '''Write a success message in green. Only shown when :attr:`ConsoleLayout.log_level` is ``0``.

    :param msg: Values to log.
    '''
    _create_msg(msg, 0, 'Success', ansicol.GREEN)


def debug(*msg):
    '''Write a debug message in bright yellow. Shown when :attr:`ConsoleLayout.log_level` is ``1`` or less.

    :param msg: Values to log.
    '''
    _create_msg(msg, 1, 'Debug', ansicol.BYELLOW)


def info(*msg):
    '''Write an info message in blue. Shown when :attr:`ConsoleLayout.log_level` is ``2`` or less.

    :param msg: Values to log.
    '''
    _create_msg(msg, 2, 'Info', ansicol.BBLUE)


def warning(*msg):
    '''Write a warning message in yellow. Shown when :attr:`ConsoleLayout.log_level` is ``3`` or less.

    :param msg: Values to log.
    '''
    _create_msg(msg, 3, 'Warning', ansicol.YELLOW)


def error(*msg):
    '''Write an error message in red. Shown when :attr:`ConsoleLayout.log_level` is ``4`` or less.

    :param msg: Values to log.
    '''
    _create_msg(msg, 4, 'Error', ansicol.RED)


def critical(*msg):
    '''Write a critical message in bright red. Shown when :attr:`ConsoleLayout.log_level` is ``5`` or less.

    :param msg: Values to log.
    '''
    _create_msg(msg, 5, 'Critical', ansicol.RED)


nodeprefs = bpy.context.preferences.addons.get('bge_netlogic', None)
if nodeprefs and getattr(bpy.context.scene, 'use_screen_console', True):
    enable(toggle_key='F12')


##############################################################
# Predefined Commands
##############################################################


class Commands:
    '''Registry of all :class:`Command` subclasses available in the console.

    Commands are keyed by their :attr:`Command.command` string.
    '''

    commands = {}
    '''``dict`` mapping command identifiers to their :class:`Command` classes.'''

    @classmethod
    def add_command(cls, command):
        '''Register *command* in the global command table.

        :param command: A :class:`Command` subclass (not an instance).
        '''
        cls.commands[command.command] = command


def add_command(command):
    '''Register *command* with :class:`Commands` and return it.

    Can be used as a decorator on a :class:`Command` subclass.

    :param command: A :class:`Command` subclass to register.
    :returns: The same *command* class (for decorator usage).
    '''
    Commands.add_command(command)
    return command


def console_command(command):
    '''Decorator that registers a :class:`Command` subclass with the console.

    Equivalent to :func:`add_command`.

    :param command: A :class:`Command` subclass to register.
    :returns: The same *command* class unchanged.
    '''
    Commands.add_command(command)
    return command

class Command:
    '''Base class for on-screen console commands.

    Subclass this and set the class attributes below, then override
    :meth:`execute`.  Decorate with ``@console_command`` (or call
    :func:`add_command`) to register the command so the console can find it.

    .. code-block:: python

        @console_command
        class MyCommand(Command):
            command = 'hello'
            usage = 'NAME'
            arg_count = 1
            description = 'Say hello to NAME.'

            @classmethod
            def execute(cls, args):
                print(f'Hello, {args[0]}!')
    '''

    command = ''
    '''Identifier typed in the console to invoke this command.'''
    usage = ''
    '''Argument placeholder string shown in help output, e.g. ``"RES_X RES_Y"``.'''
    arg_count = 0
    '''Minimum number of arguments required to invoke the command.'''
    description = ''
    '''Human-readable description shown by the built-in ``help -d`` command.'''

    @classmethod
    def invoke(cls, message):
        '''Parse *message*, validate the argument count, and call
        :meth:`execute`. Prints a usage hint if too few arguments are given;
        reports exceptions via :func:`error`.

        :param message: The full input string including the command name.
        '''
        args = message.split(' ')
        args = args[1:]
        if len(args) < cls.arg_count:
            debug(f'Usage: "{cls.command} {cls.usage}"')
            return
        try:
            cls.execute(args)
        except Exception as e:
            error(e)

    @classmethod
    def execute(cls, args):
        '''Execute the command with the given argument list.

        Override this method in subclasses to implement the command logic.

        :param args: List of string arguments (the command name is excluded).
        '''
        pass


@console_command
class RemoveObjectCommand(Command):
    '''Console command: ``remove OBJECT_ID`` — end a scene object by name.'''
    command = 'remove'
    arg_count = 1
    usage = 'OBJECT_ID'
    description = 'Remove an object from the current scene.'

    @classmethod
    def execute(cls, args):
        object_name = args[0]
        scene = logic.getCurrentScene()
        scene.getGameObjectFromObject(
            bpy.data.objects[object_name]
        ).endObject()


@console_command
class DisableCommand(Command):
    '''Console command: ``disable OBJECT_ID`` — hide and suspend physics for an object.'''
    command = 'disable'
    arg_count = 1
    usage = 'OBJECT_ID'
    description = 'Set an object to invisible and inactive.'

    @classmethod
    def execute(cls, args):
        object_name = args[0]
        scene = logic.getCurrentScene()
        obj = scene.getGameObjectFromObject(
            bpy.data.objects[object_name]
        )
        obj.setVisible(False, True)
        obj.suspendPhysics()
        obj.suspendDynamics()


@console_command
class EnableCommand(Command):
    '''Console command: ``enable OBJECT_ID`` — show and restore physics for an object.'''
    command = 'enable'
    arg_count = 1
    usage = 'OBJECT_ID'
    description = 'Set an object to visible and active.'

    @classmethod
    def execute(cls, args):
        object_name = args[0]
        scene = logic.getCurrentScene()
        obj = scene.getGameObjectFromObject(
            bpy.data.objects[object_name]
        )
        obj.setVisible(True, True)
        obj.restorePhysics()
        obj.restoreDynamics()


@console_command
class ShowInfoCommand(Command):
    '''Console command: ``showinfo STAGE`` — toggle FPS/profile/property overlays (0–3).'''
    command = 'showinfo'
    arg_count = 1
    usage = 'STAGE(0-3)'
    description = 'Show game info. 1: Show FPS, 2: Show Profile, 3: Show Properties'

    @classmethod
    def execute(cls, args):
        stage = args[0]
        render.showFramerate(int(stage) > 0)
        render.showProfile(int(stage) > 1)
        render.showProperties(int(stage) > 2)


@console_command
class QuitCommand(Command):
    '''Console command: ``quit`` — end the game immediately.'''
    command = 'quit'
    arg_count = 0
    usage = ''
    description = 'Quit the game.'

    @classmethod
    def execute(cls, args):
        logic.endGame()


@console_command
class RestartCommand(Command):
    '''Console command: ``restart`` — restart the game.'''
    command = 'restart'
    arg_count = 0
    usage = ''
    description = 'Restart the game.'

    @classmethod
    def execute(cls, args):
        logic.restartGame()


@console_command
class PrintCommand(Command):
    '''Console command: ``print MESSAGE`` — evaluate and print an expression.'''
    command = 'print'
    arg_count = 1
    usage = 'MESSAGE'
    description = 'Print a message or variable.'

    @classmethod
    def execute(cls, args):
        msg = args[0]
        print(eval(msg, _get_globals()))


# @console_command
# class PauseCommand(Command):
#     command = 'pause'
#     arg_count = 1
#     usage = 'STATE(0 or 1)'

#     @classmethod
#     def execute(cls, args):
#         state = args[0]
#         if state:
#             logic.getCurrentScene().suspend()
#         else:
#             logic.getCurrentScene().resume()


@console_command
class HelpCommand(Command):
    '''Console command: ``help [-d]`` — list all registered commands; ``-d`` includes descriptions.'''
    command = 'help'
    description = 'Print out all available commands.'

    @classmethod
    def execute(cls, args):
        mode = None
        msg = 'Available Commands:'
        if len(args) > 0:
            mode = args[0]
        for command in Commands.commands.values():
            if mode == '-d':
                msg += f'\n -  "{command.command} {command.usage}"    -    {command.description}'
            else:
                msg += f'\n -  "{command.command} {command.usage}"'
        print(msg)


@console_command
class FontSizeCommand(Command):
    '''Console command: ``fontsize PX_SIZE`` — change the console font size.'''
    command = 'fontsize'
    arg_count = 1
    usage = 'PX_SIZE'
    description = 'Modify the font size of the console.'

    @classmethod
    def execute(cls, args):
        size = args[0]
        get_console(True).font_size = int(size)


@console_command
class SetResolutionCommand(Command):
    '''Console command: ``setres RES_X RES_Y`` — resize the application window.'''
    command = 'setres'
    arg_count = 2
    usage = 'RES_X RES_Y'
    description = 'Set the app resolution'

    @classmethod
    def execute(cls, args):
        rx, ry = args
        render.setWindowSize(int(rx), int(ry))


@console_command
class ToggleDebugCommand(Command):
    '''Console command: ``debug`` — toggle info-mode (always-visible background).'''
    command = 'debug'
    arg_count = 0
    description = 'Toggle Debug Mode'

    @classmethod
    def execute(cls, args):
        console = get_console(True)
        console.info_mode = not console.info_mode
        debug(f'Console Debug Mode is now {"ON" if console.info_mode else "OFF"}.')
