'''TODO: Documentation
'''

from bge import logic
import time
from uplogic.physics import on_collision  # noqa


def get_event_manager():
    scene = logic.getCurrentScene()
    if ULEventManager.update not in scene.post_draw:
        scene.post_draw.append(ULEventManager.update)
        # ULEventManager.initialized = True


class ULEventManager():
    '''Manager for `ULEvent` objects, not inteded for manual use.
    '''
    events = {}
    callbacks = []
    initialized = False
    done = []

    @classmethod
    def update(cls):
        for cb in cls.callbacks.copy():
            cb()

    @classmethod
    def log(cls):
        if cls.events:
            print('Events:')
            for evt in cls.events:
                print(f'\t{evt}:\t{cls.events[evt].content}')


    @classmethod
    def schedule(cls, cb):
        if not cls.initialized:
            get_event_manager()
        cls.callbacks.append(cb)

    @classmethod
    def deschedule(cls, cb):
        if not cls.initialized:
            get_event_manager()
        if cb in cls.callbacks:
            cls.callbacks.remove(cb)

    @classmethod
    def register(cls, event):
        if not cls.initialized:
            get_event_manager()
        cls.events[event.id] = event
        cls.schedule(event.remove)

    @classmethod
    def send(cls, id, content, messenger) -> None:
        if not cls.initialized:
            get_event_manager()
        ULEvent(id, content, messenger)


    @classmethod
    def receive(cls, id):
        if not cls.initialized:
            get_event_manager()
        return cls.events.get(id, None)

    @classmethod
    def consume(cls, id):
        if not cls.initialized:
            get_event_manager()
        return cls.events.pop(id, None)


class ULEvent():
    '''Event generated by `uplogic.events.send()`.
    
    **Not intended for manual use.**

    :param `id`: Identifier of the event; can be anything, not just `str`.
    :param `content`: This can be used to store data in an event.
    :param `messenger`: Can be used to store an object.
    '''

    def __init__(self, id, content=None, messenger=None):
        self.id = id
        self.content = content
        self.messenger = messenger
        ULEventManager.schedule(self.register)

    def register(self):
        ULEventManager.register(self)
        ULEventManager.deschedule(self.register)

    def remove(self):
        ULEventManager.events.pop(self.id, None)
        ULEventManager.deschedule(self.remove)


def send(id, content=None, messenger=None) -> None:
    '''Send an event that can be reacted to.

    :param `id`: Identifier of the event; can be anything, not just `str`.
    :param `content`: This can be used to store data in an event.
    :param `messenger`: Can be used to store an object.
    '''
    ULEventManager.send(id, content, messenger)


def receive(id) -> ULEvent:
    '''Check if an event has occured.

    :param `id`: Identifier of the event; can be anything, not just `str`.

    :returns: `ULEvent` with `id`, `content` and `messenger` as attributes.
    '''
    return ULEventManager.receive(id)


def consume(id: str):
    '''Check if an event has occured. This will remove the event.

    :param `id`: Identifier of the event; can be anything, not just `str`.

    :returns: `ULEvent` with `id`, `content` and `messenger` as attributes.
    '''
    return ULEventManager.consume(id, None)


def bind(id, callback):
    '''Send an event that can be reacted to.

    :param `id`: Identifier of the event; can be anything, not just `str`.
    :param `content`: This can be used to store data in an event.
    :param `messenger`: Can be used to store an object.
    '''
    def _check_evt(id, callback):
        evt = receive(id)
        if evt:
            callback(evt.id, evt.content, evt.messenger)
    logic.getCurrentScene().post_draw.append(_check_evt)


def schedule(id: str, content=None, messenger=None, delay=0.0):
    '''Send an event that can be reacted to with a delay.

    :param `id`: Identifier of the event; can be anything, not just `str`.
    :param `content`: This can be used to store data in an event.
    :param `messenger`: Can be used to store an object.
    :param `delay`: Delay with which to send the event in seconds.
    '''
    ScheduledEvent(delay, id, content, messenger)


class ScheduledEvent():
    '''Event generated by `uplogic.events.schedule()`.
    
    **Not intended for manual use.**

    :param `delay`: Delay with which to send the event in seconds.
    :param `id`: Identifier of the event; can be anything, not just `str`
    :param `content`: This can be used to store data in an event.
    :param `messenger`: Can be used to store an object.
    '''

    def __init__(self, delay, id, content, messenger):
        self.time = time.time()
        self.delay = self.time + delay
        self.id = id
        self.content = content
        self.messenger = messenger
        ULEventManager.schedule(self.send_scheduled)

    def send_scheduled(self):
        if time.time() >= self.delay:
            ULEventManager.deschedule(self.send_scheduled)
            ULEvent(self.id, self.content, self.messenger)


def schedule_callback(cb, delay=0.0, arg=None):
    '''Call a function with a delay. The function can have an argument when
    defined as a keyword.

    Callback cannot return anything.

    :param `cb`: Callback to be evaluated.
    :param `delay`: Delay with which to call the function in seconds.
    :param `arg`: If this is defined, callback will be called with this
    argument.
    '''
    return ScheduledCallback(cb, delay, arg)


class ScheduledCallback():
    '''Event generated by `uplogic.events.schedule_callback()`.
    
    **Not intended for manual use.**

    :param `cb`: Callback to be evaluated.
    :param `delay`: Delay with which to call the function in seconds.
    :param `arg`: If this is defined, callback will be called with this
    argument.
    '''

    def __init__(self, cb, delay=0.0, arg=None):
        ULEventManager.schedule(self.call_scheduled)
        self.time = time.time()
        self.delay = self.time + delay
        self.callback = cb
        self.arg = arg

    def call_scheduled(self):
        if time.time() >= self.delay:
            if self.arg is not None:
                self.callback(self.arg)
            else:
                self.callback()
            ULEventManager.deschedule(self.call_scheduled)

    def cancel(self):
        ULEventManager.deschedule(self.call_scheduled)
