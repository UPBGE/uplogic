from bge import logic, render
from io import StringIO
from uplogic.ui.canvas import Canvas
from uplogic.ui.layout import RelativeLayout
from uplogic.ui.label import Label
from uplogic.ui.textinput import TextInput
from uplogic.data import GlobalDB
from uplogic.utils.raycasting import raycast_mouse
from uplogic.utils.math import world_to_screen
from uplogic.utils.math import cycle
from uplogic.input import key_down, mouse_down, key_pulse, mouse_wheel
import bpy
import sys
from datetime import datetime
from mathutils import Vector


GLOBALS = {}


def set_depth(depth):
    ConsoleLayout.max_msg = depth


def set_global(key, val):
    global GLOBALS
    GLOBALS[key] = val


def _get_globals():
    scene = logic.getCurrentScene()
    global GLOBALS
    GLOBALS['scene'] = scene
    GLOBALS['bpy'] = bpy
    GLOBALS['bge'] = bge
    GLOBALS['logic'] = logic
    GLOBALS['render'] = render
    for obj in scene.objects:
        GLOBALS[obj.blenderObject.name] = obj
    return GLOBALS


def enable(toggle_key='F12', visible=False):
    get_console(True, toggle_key=toggle_key, visible=visible)
    sys.stdout = Console()
    debug('On-Screen Console active; Check System Console for Errors.')


def disable():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    console = get_console()
    if console:
        console.stop()


class Console(StringIO):

    # def writelines(self, __lines: Iterable[str]) -> None:
    #     log(__lines, newline=False)

    def write(self, __s: str) -> int:
        log(__s)
        sys.__stdout__.write(__s)


class ErrorConsole(StringIO):
    def write(self, __s: str) -> int:
        error(__s)
        # sys.__stderr__.write(__s)


class ConsoleLayout(Canvas):
    colors = {
        'INFO': [1, 1, 1, 1],
        'DEBUG': [1, 1, .6, 1],
        'WARNING': [1, 1, .3, 1],
        'ERROR': [1, .3, .3, 1],
        'SUCCESS': [.3, 1, .3, 1]
    }
    max_msg = 50
    opacity = 1
    padding = [5, 10]
    toggle_key = 'F12'

    def __init__(self, toggle_key='F12', visible=False):
        scene = logic.getCurrentScene()
        self.toggle_key = toggle_key
        self._mouse_down = False
        self._goback_index = 0
        super().__init__()
        if not getattr(bpy.context.scene, 'screen_console_open', False) and not visible:
            self.show = False
        self.input = TextInput(text='', shadow=True, valign='center')
        self.input.on_enter = self.on_enter
        self.input.edit = True
        self.layout = RelativeLayout(relative={'size': True, 'pos': True}, pos=[0, 0], size=(1, .4), bg_color=[0, 0, 0, .3])
        self.layout.use_clipping = True
        self.add_widget(self.layout)
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

    def on_enter(self):
        self.add_message(self.input.text)
        command_name = self.input.text.split(' ')[0]
        command = Commands.commands.get(command_name)
        if command:
            command.invoke(self.input.text)
        else:
            # try:
            exec(self.input.text, _get_globals())
            # except:
            #     error(f'Command "{command_name}" not found.')
        self._goback_index = 0
        self.input.text = ''

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

    def update(self):
        if key_pulse('DOWNARROW'):
            self.input.text = ''
        if key_pulse('UPARROW'):
            self.input.text = self.layout.children[self._goback_index].text[13:]
            self._goback_index = cycle(self._goback_index + 1, 0, len(self.layout.children) - 1)
        if key_down(self.toggle_key):
            if not self._toggle_key:
                self.show = not self.show
                self.opacity = 1
            self._toggle_key = True
        else:
            self._toggle_key = False
        logic.mouse.visible = self.show

    def stop(self):
        self.clear()
        scene = logic.getCurrentScene()
        if self.toggle in scene.pre_draw:
            scene.pre_draw.remove(self.toggle)

    def add_message(self, msg, type='INFO', time=True):
        if (msg == ' ' or self._prev_msg == ' ') and len(self.layout.children):
            self.layout.children[-1].text += msg
            self._prev_msg = msg
            return
        if len(self.layout.children) > self.max_msg -1:
            self.layout.remove_widget(self.layout.children[0])
        now = datetime.now()
        current_time = f'[{now.strftime("%H:%M:%S")}]' if time else "\t\t\t\t\t\t".replace('\t', '    ')
        self.layout.add_widget(Label(text=f'>{current_time}  {msg}', pos=[5, 10], font_color=self.colors[type], shadow=True))
        dim = self.layout.children[0].dimensions[1]
        lheight = self.layout._draw_size[1]
        amount = lheight / dim
        y = 40
        for i, child in enumerate(self.layout._children_reversed):
            if child is self.input:
                continue
            child.pos[1] = y
            y+=15
            if child.pos[1] > lheight - dim:
                self.layout.remove_widget(child)
            child.opacity = 1 - (i * (1/amount))
            child.shadow_color[3] = child.font_color[3]
        self.input.pos[1] = 20
        self.input.pos[0] = 5
        self._prev_msg = msg


def get_console(create=False, toggle_key='F12', visible=False) -> ConsoleLayout:
    consoles = GlobalDB.retrieve('uplogic.consoles')
    console = consoles.get('default')
    if console is None and create:
        console = ConsoleLayout(toggle_key=toggle_key, visible=visible)
        consoles.put('default', console)
    return console


def log(msg, type='INFO'):
    console = get_console()
    if console is None:
        print(msg)
        return
    show_time = True
    for msg in str(msg).split('\n'):
        if msg:
            msg = msg.replace('  ', '    ')
            console.add_message(f'{msg}', type, time=show_time)
            show_time = False


def warning(msg):
    console = get_console()
    if console is None:
        print(msg)
        return
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            console.add_message(f'WARNING:\t{msg}', 'WARNING')


def error(msg):
    console = get_console()
    if console is None:
        print(msg)
        return
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            console.add_message(f'{msg}', 'ERROR')
            sys.__stdout__.write(f'{msg}\n')


def success(msg):
    console = get_console()
    if console is None:
        print(msg)
        return
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            console.add_message(f'{msg}', 'SUCCESS')
            sys.__stdout__.write(f'{msg}\n')


def debug(msg):
    console = get_console()
    if console is None:
        print(msg)
        return
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            console.add_message(f'{msg}', 'DEBUG')
            sys.__stdout__.write(f'{msg}\n')

nodeprefs = bpy.context.preferences.addons.get('bge_netlogic', None)
if nodeprefs and getattr(bpy.context.scene, 'use_screen_console', False):
    enable(toggle_key='F12')


import bpy
import bge


class Command:
    command = ''
    usage = ''
    arg_count = 0

    @classmethod
    def invoke(cls, message):
        args = message.split(' ')
        if len(args) - 1 != cls.arg_count:
            debug(f'Usage: "{cls.command} {cls.usage}"')
            return
        try:
            cls.execute(args)
        except Exception as e:
            error(e)

    @classmethod
    def execute(cls, args):
        pass


class RemoveObjectCommand(Command):
    command = 'remove'
    arg_count = 1
    usage = 'OBJECT_ID'

    @classmethod
    def execute(cls, args):
        command, object_name = args
        scene = bge.logic.getCurrentScene()
        scene.getGameObjectFromObject(
            bpy.data.objects[object_name]
        ).endObject()


class DisableCommand(Command):
    command = 'disable'
    arg_count = 1
    usage = 'OBJECT_ID'

    @classmethod
    def execute(cls, args):
        command, object_name = args
        scene = bge.logic.getCurrentScene()
        scene.getGameObjectFromObject(
            bpy.data.objects[object_name]
        ).setVisible(False)


class EnableCommand(Command):
    command = 'enable'
    arg_count = 1
    usage = 'OBJECT_ID'

    @classmethod
    def execute(cls, args):
        command, object_name = args
        scene = bge.logic.getCurrentScene()
        scene.getGameObjectFromObject(
            bpy.data.objects[object_name]
        ).setVisible(True)


class ShowInfoCommand(Command):
    command = 'showinfo'
    arg_count = 1
    usage = 'STAGE(0-3)'

    @classmethod
    def execute(cls, args):
        command, stage = args
        render.showFramerate(int(stage) > 0)
        render.showProfile(int(stage) > 1)
        render.showProperties(int(stage) > 2)


class QuitCommand(Command):
    command = 'quit'
    arg_count = 0
    usage = ''

    @classmethod
    def execute(cls, args):
        logic.endGame()


class RestartCommand(Command):
    command = 'restart'
    arg_count = 0
    usage = ''

    @classmethod
    def execute(cls, args):
        logic.restartGame()


class PrintCommand(Command):
    command = 'print'
    arg_count = 1
    usage = 'MESSAGE'

    @classmethod
    def execute(cls, args):
        command, msg = args
        print(eval(msg, _get_globals()))


class PauseCommand(Command):
    command = 'pause'
    arg_count = 1
    usage = '(0 or 1)'

    @classmethod
    def execute(cls, args):
        command, state = args
        if state:
            logic.getCurrentScene().suspend()
        else:
            logic.getCurrentScene().resume()


class Commands:
    commands = {}

    @classmethod
    def add_command(cls, command):
        cls.commands[command.command] = command


Commands.add_command(RemoveObjectCommand)
Commands.add_command(DisableCommand)
Commands.add_command(EnableCommand)
Commands.add_command(ShowInfoCommand)
Commands.add_command(QuitCommand)
Commands.add_command(RestartCommand)
Commands.add_command(PrintCommand)
Commands.add_command(PauseCommand)


def add_command(command):
    Commands.add_command(command)


def console_command(command):
    Commands.add_command(command)
