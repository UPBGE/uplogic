from bge import logic
from bge import render
from bgui.bgui_utils import Layout
from bgui.bgui_utils import System
from bgui.label import Label
from io import StringIO
from uplogic.data import GlobalDB
from uplogic.utils import lerp
from uplogic.events import schedule_callback
import sys


def set_depth(depth):
    LoggerLayout.max_msg = depth


def enable():
    sys.stdout = Logger()
    sys.stderr = ErrorLogger()


def disable():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


class Logger(StringIO):

    def write(self, __s: str) -> int:
        log(__s)
        sys.__stdout__.write(__s)


class ErrorLogger(StringIO):
    def write(self, __s: str) -> int:
        error(__s)
        sys.__stderr__.write(__s)


class LoggerLayout(Layout):
    colors = {
        'INFO': [1, 1, 1, 1],
        'WARNING': [1, 1, .3, 1],
        'ERROR': [1, .3, .3, 1]
    }
    max_msg = 20
    opacity = 1

    def __init__(self, system, data):
        super().__init__(system, data)
        self.messages: list[Label] = []
        self.fade_event = None
        if disable not in logic.getCurrentScene().onRemove:
            logic.getCurrentScene().onRemove.append(disable)

    def fade_out(self):
        for msg in self.messages:
            msg.color[3] = lerp(msg.color[3], self.messages[0].color[3], .02)
        if self.messages[-1].color[3] != .1:
            self.fade_event = schedule_callback(self.fade_out)
        else:
            self.fade_event = None

    def add_message(self, msg, type='INFO'):
        if len(self.messages) > self.max_msg:
            self._remove_widget(self.messages[0])
            self.messages.pop(0)
        if self._system:
            self.messages.append(Label(
                self,
                text=str(msg),
                pt_size=0,
                color=self.colors.get(type, [1, 1, 1, 1]).copy(),
                pos=[0.02, 0],
                outline_color=(1, 0, 0, 1)
            ))
        for i, log in enumerate(reversed(self.messages)):
            size = 11 * (1080 / render.getWindowHeight())
            log.position[1] = 13 * (i+1)
            log.color[3] = 1 - (i/(self.max_msg + 5))
            log.pt_size = size
        if self.fade_event:
            self.fade_event.cancel()
        self.fade_event = schedule_callback(self.fade_out, 3)


def get_logger() -> LoggerLayout:
    loggers = GlobalDB.retrieve('uplogic.loggers')
    layout = loggers.get('default')
    if layout is None:
        system = System()
        system.load_layout(LoggerLayout, None)
        loggers.put('default', system.layout)
        layout = system.layout
        logic.getCurrentScene().post_draw.append(system.run)
    return layout


def log(msg):
    logger = get_logger()
    if logger is None:
        return
    for msg in str(msg).split('\n'):
        if msg:
            msg = msg.replace('  ', '    ')
            logger.add_message(f'INFO:\t{msg}')


def warning(msg):
    logger = get_logger()
    if logger is None:
        return
    for msg in str(msg).split('\n'):
        if msg:
            msg.replace('  ', '    ')
            logger.add_message(f'WARNING:\t{msg}', 'WARNING')


def error(msg):
    logger = get_logger()
    if logger is None:
        return
    for msg in str(msg).split('\n'):
        print(logger.system)

        if msg:
            msg.replace('  ', '    ')
            logger.add_message(f'ERROR:\t{msg}', 'ERROR')
