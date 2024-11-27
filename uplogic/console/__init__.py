from bge import logic, render
from io import StringIO
from uplogic.ui.canvas import Canvas
from uplogic.ui.layout import RelativeLayout
from uplogic.ui.label import Label
from uplogic.ui.textinput import TextInput
from uplogic.data import GlobalDB
from uplogic.utils.raycasting import raycast_mouse
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
    global GLOBALS
    GLOBALS[key] = val


def _get_globals():
    scene = logic.getCurrentScene()
    global GLOBALS
    GLOBALS['scene'] = scene
    GLOBALS['bpy'] = bpy
    GLOBALS['bge'] = bge
    GLOBALS['uplogic'] = uplogic
    GLOBALS['logic'] = logic
    GLOBALS['render'] = render
    GLOBALS['console'] = get_console()
    for obj in scene.objects:
        GLOBALS[obj.blenderObject.name] = obj
    return GLOBALS


def enable(toggle_key='F12', visible=False):
    get_console(True, toggle_key=toggle_key, visible=visible)
    sys.stdout = Console()


def disable():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    console = get_console()
    if console:
        console.stop()
    consoles = GlobalDB.retrieve('uplogic.consoles')
    consoles.remove('default')


class Console(StringIO):

    def write(self, __s: str) -> int:
        log(__s)


class ErrorConsole(StringIO):
    def write(self, __s: str) -> int:
        error(__s)

COLORS = {
    'INFO': [1, 1, 1, 1],
    'DEBUG': [1, 1, .6, 1],
    'WARNING': [1, .8, .2, 1],
    'ERROR': [1, .3, .3, 1],
    'SUCCESS': [.3, 1, .3, 1]
}


class CommandLabel(Label):
    pass


class ConsoleLayout(Canvas):
    opacity = 1
    padding = [5, 10]
    toggle_key = 'F12'

    def __init__(self, toggle_key='F12', visible=False):
        scene = logic.getCurrentScene()
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
        self.font_size = 14
        # self.info_mode = False
        self.position = 'bottom'
        self.info_mode = getattr(bpy.context.scene, 'screen_console_open', False)
        self.active = False
        # if not getattr(bpy.context.scene, 'screen_console_open', False) and not visible:
        #     self.active = False

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, val):
        for w in self._layout.children:
            val.add_widget(w)
        self._layout = val

    @property
    def info_mode(self):
        return self._info_mode

    @info_mode.setter
    def info_mode(self, val):
        self._info_mode = val
        self.active = self.active

    @property
    def active(self):
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
        if self.input.text:
            self.issued_commands.append(self.input.text)
        sys.__stdout__.write(f'{self.input.text}\n')
        self.add_message(self.input.text)
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
        ray = raycast_mouse()
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
        if not self.show:
            self._mouse_visible = logic.mouse.visible
        if not self._toggle_key:
            self.active = not self.active
            self.opacity = 1
            self._toggle_key = True

    def update(self):
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
        self.clear()
        scene = logic.getCurrentScene()
        if self.toggle in scene.pre_draw:
            scene.pre_draw.remove(self.toggle)

    def add_message(self, msg, type='INFO', time=True, command=False):
        if (msg == ' ' or self._prev_msg == ' ') and len(self.layout.children):
            self.layout.children[-1].text += msg
            self._prev_msg = msg
            return
        now = datetime.now()
        current_time = f'[{now.strftime("%H:%M:%S")}]' if time else "\t\t\t\t  ".replace('\t', '    ')
        label_class = CommandLabel if command else Label
        # self.layout.add_widget(label_class(text=f'{current_time}  {msg}', pos=[5, 10], font_color=COLORS[type], shadow=True, font_size=self.font_size))
        self._prev_msg = msg
        self.arrange()

    def arrange(self):
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
    consoles = GlobalDB.retrieve('uplogic.consoles')
    console = consoles.get('default')
    if console is None and create:
        console = ConsoleLayout(toggle_key=toggle_key, visible=visible)
        consoles.put('default', console)
        debug('On-Screen Console active; Check System Console for Errors.')
    return console


class ansicol:
    RED = '\033[31m\033[1m'
    GREEN = '\033[32m\033[1m'
    YELLOW = '\033[33m'
    BYELLOW = '\033[93m'
    BBLUE = '\033[36m'
    END = '\033[0m'


def write(msg, type):
    _f = {
        'INFO': log,
        'DEBUG': debug,
        'WARNING': warning,
        'ERROR': error,
        'SUCCESS': success
    }

    _f[type](msg)


def log(msg, type='INFO'):
    console = get_console()

    if console is None:
        print(msg)
        return
    show_time = True
    sys.__stdout__.write(f'{msg}\n')
    for msg in str(msg).split('\n'):
        if msg:
            msg = msg.replace('  ', '    ')
            console.add_message(f'{msg}', type, time=show_time)
            show_time = False


def warning(msg):
    console = get_console()
    sysmsg = f'{ansicol.YELLOW}Warning{ansicol.END}: {msg}'
    if console is None:
        print(sysmsg)
        return
    show_time = True
    sys.__stdout__.write(f'{sysmsg}\n')
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            console.add_message(f'{msg}', 'WARNING', time=show_time)
            show_time = False


def error(msg):
    console = get_console()
    sysmsg = f'{ansicol.RED}Error{ansicol.END}: {msg}'
    if console is None:
        print(sysmsg)
        # print(msg)
        return
    show_time = True
    sys.__stdout__.write(f'{sysmsg}\n')
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            console.add_message(f'{msg}', 'ERROR', time=show_time)
            show_time = False


def success(msg):
    console = get_console()
    sysmsg = f'{ansicol.GREEN}Success{ansicol.END}: {msg}'
    if console is None:
        print(sysmsg)
        return
    show_time = True
    sys.__stdout__.write(f'{sysmsg}\n')
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            console.add_message(f'{msg}', 'SUCCESS', time=show_time)
            show_time = False


def debug(msg):
    console = get_console()
    sysmsg = f'{ansicol.BYELLOW}Debug{ansicol.END}: {msg}'
    if console is None:
        print(sysmsg)
        return
    show_time = True
    sys.__stdout__.write(f'{sysmsg}\n')
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            console.add_message(f'{msg}', 'DEBUG', time=show_time)
            show_time = False

nodeprefs = bpy.context.preferences.addons.get('bge_netlogic', None)
if nodeprefs and getattr(bpy.context.scene, 'use_screen_console', True):
    enable(toggle_key='F12')


##############################################################
# Predefined Commands
##############################################################


class Commands:
    commands = {}

    @classmethod
    def add_command(cls, command):
        cls.commands[command.command] = command


def add_command(command):
    Commands.add_command(command)


def console_command(command):
    Commands.add_command(command)

class Command:
    command = ''
    usage = ''
    arg_count = 0
    description = ''

    @classmethod
    def invoke(cls, message):
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
        pass


@console_command
class RemoveObjectCommand(Command):
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
        obj.setVisible(False)
        obj.suspendPhysics()
        obj.suspendDynamics()


@console_command
class EnableCommand(Command):
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
        obj.setVisible(True)
        obj.restorePhysics()
        obj.restoreDynamics()


@console_command
class ShowInfoCommand(Command):
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
    command = 'quit'
    arg_count = 0
    usage = ''
    description = 'Quit the game.'

    @classmethod
    def execute(cls, args):
        logic.endGame()


@console_command
class RestartCommand(Command):
    command = 'restart'
    arg_count = 0
    usage = ''
    description = 'Restart the game.'

    @classmethod
    def execute(cls, args):
        logic.restartGame()


@console_command
class PrintCommand(Command):
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
    command = 'fontsize'
    arg_count = 1
    usage = 'PX_SIZE'
    description = 'Modify the font size of the console.'

    @classmethod
    def execute(cls, args):
        size = args[0]
        get_console().font_size = int(size)


@console_command
class SetResolutionCommand(Command):
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
    command = 'debug'
    arg_count = 0
    description = 'Toggle Debug Mode'

    @classmethod
    def execute(cls, args):
        console = get_console()
        console.info_mode = not console.info_mode
        debug(f'Console Debug Mode is now {"ON" if console.info_mode else "OFF"}.')
