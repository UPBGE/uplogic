"""
Author: Robert Niederreiter

Python based main loop for bge
==============================

Starting the custom mainloop
----------------------------

Add custom property ``__main__`` with value ``main.py`` to scene.

main.py contains:

.. code-block:: python

    from uplogic.mainloop import start

    start(max_fps=60, tick_idle=.001)

Using the mainloop
------------------

.. code-block:: python

    from uplogic.mainloop import MainLoop

    def on_start_callback():
        '''Gets called when custom mainloop starts.'''

    MainLoop.on_start(on_start_callback)

    def on_tick_callback():
        '''Gets called as fast as mainloop runs.'''

    MainLoop.on_tick(on_tick_callback)

    def on_update_callback():
        '''Gets called when enough time has elapsed to render the next frame.'''

    MainLoop.on_update(on_update_callback)

    def on_stop_callback():
        '''Gets called when custom mainloop is stopped.'''

    MainLoop.on_stop(on_stop_callback)


Stopping the mainloop
---------------------

By default, the mainloop gets stopped by SIGTERM. If you want to stop the
mainloop on purpose, use the following code:

.. code-block:: python

    from uplogic.mainloop import get_mainloop

    get_mainloop().stop(
"""

from collections import deque

from .utils import load_user_module
from .input import key_tap
from .logging import enable
import bge
import bpy
import signal
import time


class MainLoop:
    _handles = {}

    def __init__(self, max_fps=60, tick_idle=.001):
        self.max_fps = max_fps
        self.tick_idle = tick_idle
        self.time_per_tick = 0.0
        self._last_frame = 0.0
        self._last_tick = 0.0
        self._running = False
        self._evt_queue = deque()
        signal.signal(signal.SIGTERM, self._terminate)

    @property
    def max_fps(self):
        return self._max_fps

    @max_fps.setter
    def max_fps(self, value):
        self._max_fps = value
        self._frame_delay = 1. / value

    def start(self):
        self._running = True
        self._dispatch('start')
        try:
            while self._running:
                self._do_tick()
                time.sleep(self.tick_idle)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self._dispatch('stop')
        self._running = False
        bge.logic.endGame()

    def _terminate(self, *args):
        self.stop()

    def dispatch(self, event, *a, **kw):
        self._evt_queue.append((event, a, kw))

    def _dispatch_queue(self):
        while len(self._evt_queue) > 0:
            e, a, kw = self._evt_queue.popleft()
            self._dispatch(e, *a, **kw)

    def _dispatch(self, event, *a, **kw):
        for handle in self._handles.get(event, []):
            handle(*a, **kw)

    def _do_tick(self):
        now = time.time()
        self._dispatch('tick')
        self.time_per_tick = now - self._last_tick
        self._last_tick = now
        # print(now + self.time_per_tick, self.time_per_tick)
        if (now - self._last_frame + self.time_per_tick) > self._frame_delay:
            self._last_frame = now
            self._dispatch('update')
            self._dispatch_queue()
            bge.logic.NextFrame()

    @classmethod
    def on(cls, **kw):
        for event, handle in kw.items():
            handles = cls._handles.setdefault(event, [])
            if handle not in handles:
                handles.append(handle)

    @classmethod
    def off(cls, event=None, handle=None):
        if event is not None and handle is None:
            if event in cls._handles:
                del cls._handles[event]
        elif event is None and handle is not None:
            for handles in cls._handles.values():
                if handle in handles:
                    handles.remove(handle)
        elif event is not None and handle is not None:
            handles = cls._handles.get(event, [])
            if handle in handles:
                handles.remove(handle)

    @classmethod
    def on_start(cls, handle):
        cls.on(start=handle)

    @classmethod
    def on_stop(cls, handle):
        cls.on(stop=handle)

    @classmethod
    def on_tick(cls, handle):
        cls.on(tick=handle)

    @classmethod
    def on_update(cls, handle):
        cls.on(update=handle)


_mainloop = None


def create_mainloop(max_fps, tick_idle):
    global _mainloop
    if _mainloop is not None:
        return _mainloop
    _mainloop = MainLoop(
        max_fps=max_fps,
        tick_idle=tick_idle
    )
    return _mainloop


def get_mainloop():
    global _mainloop
    return _mainloop


def start(max_fps=60, tick_idle=.001):
    """Start event loop.
    """
    eventloop = create_mainloop(max_fps, tick_idle)
    eventloop.start()


class ULLoop:

    quit_key = 'esc'

    def __init__(self, max_fps=-1, tick_idle=.00001) -> None:
        self.scene = bge.logic.getCurrentScene()
        logic_tree = bpy.data.scenes[self.scene.name].get('custom_mainloop_tree')
        if logic_tree:
            module = load_user_module(f'nl_{logic_tree.name.lower()}')
            logic_tree = module.get_tree(self.scene)
            MainLoop.on_update(logic_tree.network.evaluate)
        MainLoop.on_start(self.start)
        MainLoop.on_tick(self.tick)
        MainLoop.on_update(self.update)
        MainLoop.on_stop(self.stop)

        self.scene['uplogic.mainloop'] = self
        if max_fps == -1:
            max_fps = bpy.data.scenes[self.scene.name].game_settings.fps
        start(max_fps, tick_idle)

    def start(self):
        pass

    def tick(self):
        if key_tap(self.quit_key):
            get_mainloop().stop()

    def update(self):
        pass

    def stop(self):
        pass
