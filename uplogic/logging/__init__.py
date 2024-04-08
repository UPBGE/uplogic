from collections.abc import Iterable
from bge import logic
from bge import render
from io import StringIO
from uplogic.ui.canvas import Canvas
from uplogic.ui.layout import RelativeLayout
from uplogic.ui.label import Label
from uplogic.ui.textinput import TextInput
from uplogic.data import GlobalDB
from uplogic.utils.math import lerp
from uplogic.utils.raycasting import raycast_mouse
from uplogic.utils.math import world_to_screen
from uplogic.input import key_down
from uplogic.events import schedule_callback
import bpy
import sys
from contextlib import redirect_stderr
from datetime import datetime


def set_depth(depth):
    LoggerLayout.max_msg = depth


def enable(toggle_key='BACKSLASH', visible=False):
    get_logger(True, toggle_key=toggle_key, visible=visible)
    sys.stdout = Logger()
    log('On-Screen Console active; Check System Console for Errors.')


def disable():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    logger = get_logger()
    if logger:
        logger.stop()


class Logger(StringIO):

    # def writelines(self, __lines: Iterable[str]) -> None:
    #     log(__lines, newline=False)

    def write(self, __s: str) -> int:
        log(__s)
        sys.__stdout__.write(__s)


class ErrorLogger(StringIO):
    def write(self, __s: str) -> int:
        error(__s)
        # sys.__stderr__.write(__s)


class LoggerLayout(Canvas):
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
    toggle_key = 'BACKSLASH'

    def __init__(self, toggle_key='BACKSLASH', visible=False):
        scene = logic.getCurrentScene()
        self.toggle_key = toggle_key
        super().__init__()
        # prefs = bpy.context.preferences.addons.get('bge_netlogic', None)
        # if not (scene.screen_console_open or visible):
        #     self.show = False
        if not getattr(bpy.context.scene, 'screen_console_open', True) and not visible:
            self.show = False
        self.input = TextInput(text='a', shadow=True, valign='center')
        self.input.on_enter = self.on_enter
        self.input.edit = True
        self.messages: list[Label] = []
        self.layout = RelativeLayout(relative={'size': True, 'pos': True}, pos=[0, 0], size=(1, .4), bg_color=[0, 0, 0, .3])
        self.layout.use_clipping = True
        self.add_widget(self.layout)
        self.layout.add_widget(self.input)
        self.fade_event = None
        self._toggle_key = False
        self._prev_msg = None
        if disable not in scene.onRemove:
            scene.onRemove.append(disable)
        if self.toggle not in scene.pre_draw:
            scene.pre_draw.append(self.toggle)
        self.nameplate = Label(text='Hello', shadow=True, relative={'pos': True}, halign='center')
        self.nameplate.update = self.update_nameplate
        self.canvas.add_widget(self.nameplate)

    def on_enter(self):
        self.add_message(self.input.text)
        self.input.text = ''

    def update_nameplate(self):
        ray = raycast_mouse()
        if ray.obj:
            self.nameplate.pos = world_to_screen(ray.point)
            self.nameplate.text = ray.obj.blenderObject.name
        else:
            self.nameplate.text = ''

    def toggle(self):
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

    def fade_out(self):
        for msg in self.messages:
            msg.color[3] = lerp(msg.color[3], self.messages[0].color[3], .02)
        if self.messages[-1].color[3] != .1:
            self.fade_event = schedule_callback(self.fade_out)
        else:
            self.fade_event = None

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
            # sys.__stdout__.write(str(child.relative))
            child.pos[1] = y
            y+=15
            if child.pos[1] > lheight - dim:
                self.layout.remove_widget(child)
            child.opacity = 1 - (i * (1/amount))
            child.shadow_color[3] = child.font_color[3]
        self.input.pos[1] = 20
        self.input.pos[0] = 5
        self._prev_msg = msg


def get_logger(create=False, toggle_key='BACKSLASH', visible=False) -> LoggerLayout:
    loggers = GlobalDB.retrieve('uplogic.loggers')
    logger = loggers.get('default')
    if logger is None and create:
        logger = LoggerLayout(toggle_key=toggle_key, visible=visible)
        loggers.put('default', logger)
    return logger


def log(msg, type='INFO'):
    logger = get_logger()
    if logger is None:
        print(msg)
        return
    # msg = ''.join([str(e) for e in msg])
    show_time = True
    for msg in str(msg).split('\n'):
        if msg:
            msg = msg.replace('  ', '    ')
            logger.add_message(f'{msg}', type, time=show_time)
            show_time = False


def warning(msg):
    logger = get_logger()
    if logger is None:
        print(msg)
        return
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            logger.add_message(f'WARNING:\t{msg}', 'WARNING')


def error(msg):
    logger = get_logger()
    if logger is None:
        print(msg)
        return
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            logger.add_message(f'{msg}', 'ERROR')
            sys.__stdout__.write(f'{msg}\n')


def success(msg):
    logger = get_logger()
    if logger is None:
        print(msg)
        return
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            logger.add_message(f'{msg}', 'SUCCESS')
            sys.__stdout__.write(f'{msg}\n')


def debug(msg):
    logger = get_logger()
    if logger is None:
        print(msg)
        return
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            logger.add_message(f'{msg}', 'DEBUG')
            sys.__stdout__.write(f'{msg}\n')

nodeprefs = bpy.context.preferences.addons.get('bge_netlogic', None)
if nodeprefs and getattr(bpy.context.scene, 'use_screen_console', False):
    # print(nodeprefs.preferences.screen_console_key)
    enable(toggle_key='BACKSLASH')
