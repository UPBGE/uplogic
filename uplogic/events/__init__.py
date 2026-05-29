'''Event system for uplogic.

Provides a lightweight publish/subscribe mechanism on top of the BGE scene
loop. Events are sent by name, live for exactly one game tick, and can be
received, consumed, or bound to callbacks. Delayed dispatch is supported via
:class:`ScheduledEvent` and :class:`ScheduledCallback`.

Typical usage::

    from uplogic import events

    # send an event
    events.send('player_died', content={'score': 42})

    # receive it later in the same or next tick
    evt = events.receive('player_died')
    if evt:
        print(evt.content)

    # or bind a callback
    events.bind('player_died', lambda evt: print(evt.content))

    # delayed dispatch
    events.schedule('level_up', delay=2.0)
    events.schedule(my_function, delay=1.0)
'''

from bge import logic
import time
# from uplogic.physics import on_collision  # noqa


def on_pre_draw(callback):
    '''Register *callback* to be called on the scene pre-draw list.

    :param callback: Callable with no required arguments.
    '''
    EventManager.update_on.append(callback)


def on_post_draw(callback):
    '''Register *callback* to be called on the scene post-draw list.

    :param callback: Callable with no required arguments.
    '''
    EventManager.update_on.append(callback)


# class _DeferredCallback:
#     '''Executes *callback* once on the next post-draw tick, then removes
#     itself from the scene's post-draw list automatically.
#     '''

#     def callback(self):
#         ...

#     def __init__(self, callback) -> None:
#         self.callback = callback
#         logic.getCurrentScene().post_draw.append(self._call)

#     def _call(self):
#         self.callback()
#         if self._call in logic.getCurrentScene().post_draw:
#             logic.getCurrentScene().post_draw.remove(self._call)


def later(callback):
    '''Execute *callback* on the next post-draw tick.

    Unlike :class:`_DeferredCallback`, the inner implementation here removes
    itself even if the scene reference changes between registration and
    execution.

    :param callback: Callable with no required arguments.
    '''
    class _DeferredCallback():

        def __init__(self, callback) -> None:
            self.callback = callback
            logic.getCurrentScene().post_draw.append(self._call)

        def _call(self):
            self.callback()
            logic.getCurrentScene().post_draw.remove(self._call)
    _DeferredCallback(callback)


def get_event_manager():
    '''Return the :class:`EventManager` class, registering its update loop
    with the current scene's post-draw list if not already registered.

    :returns: :class:`EventManager`
    '''
    update = EventManager.update_on
    if update is None:
        update = logic.getCurrentScene().post_draw
    if EventManager.update not in update:
        update.append(EventManager.update)
    return EventManager


def set_update_loop(loop):
    '''Replace the list that drives the :class:`EventManager` update tick.

    Pass ``None`` to revert to the current scene's post-draw list.

    :param loop: A list that is iterated each frame (e.g. a scene's
        ``post_draw`` list), or ``None``.
    '''
    EventManager.set_update_on(loop)


class EventManager:
    '''Central manager for all :class:`Event` objects.

    Maintains the event registry, per-frame bindings, and the scheduled
    callback queue. Not intended for direct use — prefer the module-level
    helper functions (:func:`send`, :func:`receive`, :func:`bind`, etc.).
    '''
    events = {}
    bindings = []
    scheduled = []
    done = []

    update_on = None

    @classmethod
    def set_update_on(cls, li):
        '''Migrate the update hook to a different frame list *li*.

        Removes the update method from the old list and appends it to *li*.
        Pass ``None`` to use the current scene's post-draw list.

        :param li: Target frame list, or ``None``.
        '''
        old = cls.update_on
        if li is None:
            li = logic.getCurrentScene().post_draw
        if old is None:
            old = logic.getCurrentScene().post_draw
        if cls.update in old:
            old.remove(cls.update)
        if cls.update not in li:
            li.append(cls.update)
        cls.update_on = li

    @classmethod
    def update(cls):
        '''Execute all bound callbacks and scheduled callbacks for this tick.

        Called automatically each frame via the scene post-draw list.
        '''
        cbs = cls.bindings.copy()
        cbs.extend(cls.scheduled)
        for cb in cbs:
            cb()

    @classmethod
    def log(cls):
        '''Print all currently registered events and their content to stdout.'''
        if cls.events:
            print('Events:')
            for evt in cls.events:
                print(f'\t{evt}:\t{cls.events[evt].content}')

    @classmethod
    def schedule(cls, cb):
        '''Add *cb* to the per-frame scheduled queue.

        :param cb: Callable with no required arguments.
        '''
        get_event_manager()
        cls.scheduled.append(cb)

    @classmethod
    def cancel(cls, cb):
        '''Remove *cb* from the per-frame scheduled queue if present.

        :param cb: Previously scheduled callable.
        '''
        get_event_manager()
        if cb in cls.scheduled:
            cls.scheduled.remove(cb)

    @classmethod
    def bind(cls, cb):
        '''Add *cb* to the persistent bindings list (called every frame).

        :param cb: Callable with no required arguments.
        '''
        get_event_manager()
        cls.bindings.append(cb)

    @classmethod
    def unbind(cls, cb):
        '''Remove *cb* from the persistent bindings list if present.

        :param cb: Previously bound callable.
        '''
        get_event_manager()
        if cb in cls.bindings:
            cls.bindings.remove(cb)

    @classmethod
    def release(cls, cb):
        '''Alias for :meth:`cancel`.

        :param cb: Previously scheduled callable.
        '''
        get_event_manager()
        cls.cancel(cb)

    @classmethod
    def register(cls, event):
        '''Store *event* in the registry and schedule its one-tick removal.

        :param event: :class:`Event` instance to register.
        '''
        get_event_manager()
        cls.events[event.id] = event
        cls.schedule(event.remove)

    @classmethod
    def send(cls, id, content, messenger, target) -> None:
        '''Create and register a new :class:`Event`.

        :param id: Event identifier.
        :param content: Optional payload.
        :param messenger: Optional sender reference.
        :param target: Optional target object; ``None`` means broadcast.
        '''
        get_event_manager()
        Event(id, content, messenger, target)

    @classmethod
    def receive(cls, id, target=None):
        '''Return the :class:`Event` with *id* if it exists and matches *target*.

        :param id: Event identifier to look up.
        :param target: If provided, only return the event when its target
            matches this object.
        :returns: Matching :class:`Event` or ``None``.
        '''
        get_event_manager()
        evt = cls.events.get(id, None)
        if evt:
            if evt.target is None:
                return evt
            elif evt.target is not None and evt.target is target:
                return evt
        return None
        # return evt if evt and target is evt.target else None

    @classmethod
    def consume(cls, id):
        '''Remove and return the :class:`Event` with *id* from the registry.

        :param id: Event identifier to consume.
        :returns: :class:`Event` or ``None`` if not found.
        '''
        get_event_manager()
        return cls.events.pop(id, None)

    @classmethod
    def clear_schedule(cls):
        '''Remove all entries from the scheduled callback queue.'''
        cls.scheduled.clear()

    @classmethod
    def clear_bindings(cls):
        '''Remove all entries from the persistent bindings list.'''
        cls.bindings.clear()

class Event():
    '''Event generated by `uplogic.events.send()`.

    **Not intended for manual use.**

    :param id: Identifier of the event; can be any object.
    :param content: This can be used to store data in an event.
    :param messenger: Can be used to store an object.
    '''

    def __init__(self, id: int, content=None, messenger=None, target=None):
        self.id = id
        self.content = content
        self.messenger = messenger
        self.target = target
        EventManager.schedule(self.register)

    def register(self):
        '''Register this event in the :class:`EventManager` and remove the
        registration callback from the scheduled queue.
        '''
        EventManager.register(self)
        EventManager.cancel(self.register)

    def remove(self):
        '''Remove this event from the registry at end of its tick.'''
        EventManager.events.pop(self.id, None)
        EventManager.cancel(self.remove)


def clear_schedule():
    '''Remove all pending scheduled callbacks from the :class:`EventManager`.'''
    EventManager.clear_schedule()


def send(id: int, content=None, messenger=None, target=None) -> None:
    '''Send an event that can be reacted to.

    :param id: Identifier of the event; can be anything, not just `int`.
    :param content: This can be used to store data in an event.
    :param messenger: Can be used to store an object.
    :param target: Target object. If defined, only target object can receive.
    '''
    EventManager.send(id, content, messenger, target)


def receive(id, target=None) -> Event:
    '''Check if an event has occured.

    :param id: Identifier of the event; can be any object.
    :param target: Target object. If defined, only target object can receive.

    :returns: `Event` with `id`, `content` and `messenger` as attributes.
    '''
    return EventManager.receive(id, target)


def consume(id: int):
    '''Check if an event has occured. This will remove the event.

    :param id: Identifier of the event; can be any object.

    :returns: `Event` with `id`, `content` and `messenger` as attributes.
    '''
    return EventManager.consume(id)


def bind(id: int, callback, *args):
    '''Bind a callback to an event. This callback will be executed whenever
    the specified event is received.

    **Required signature**:
    ```
    def callback(evt):
        ...
    ```

    :param id: Identifier of the event; can be any object.
    :param callback: This callback will be called every time the event is
    triggered.
    '''
    class _BoundCallback():
        def __init__(self, id, cb, *args) -> None:
            self.id = id
            self.callback = cb
            self.args = args
            EventManager.bind(self._check_evt)

        def _check_evt(self):
            evt = receive(self.id)
            if evt:
                self.callback(evt, *self.args)

        def unbind(self):
            EventManager.unbind(self._check_evt)

        def release(self):
            EventManager.unbind(self._check_evt)

    return _BoundCallback(id, callback, *args)


def bind_once(id: int, callback, *args):
    '''Bind a callback to an event and automatically unbind when received.

    Required signature: `def cb(evt)`

    :param id: Identifier of the event; can be any object.
    :param callback: This callback will be called every time the event is
    triggered.
    '''
    class _BoundCallback():
        def __init__(self, id, cb, *args) -> None:
            self.id = id
            self.callback = cb
            self.args = args
            EventManager.bind(self._check_evt)

        def _check_evt(self):
            evt = receive(self.id)
            if evt:
                self.callback(evt, *self.args)
                self.unbind()

        def unbind(self):
            EventManager.unbind(self._check_evt)

        def release(self):
            EventManager.unbind(self._check_evt)

    return _BoundCallback(id, callback, *args)


class ULEvent(Event):
    # XXX: Remove legacy support
    pass


class ScheduledEvent():
    '''Event generated by `uplogic.events.schedule()`.

    :param delay: Delay with which to send the event in seconds.
    :param id: Identifier of the event; can be any object
    :param content: This can be used to store data in an event.
    :param messenger: Can be used to store an object.
    '''

    def __init__(self, delay, id, content, messenger):
        self.time = time.time()
        self.delay = self.time + delay
        self.id = id
        self.content = content
        self.messenger = messenger
        self._consumed = False
        EventManager.schedule(self._send_scheduled)

    @property
    def time_left(self):
        '''Seconds remaining until the event fires.

        :returns: ``float`` — may be negative if the event is overdue.
        '''
        return self.delay - time.time()

    def _send_scheduled(self):
        if time.time() >= self.delay:
            self.consume()

    def cancel(self):
        '''Cancel the scheduled event so it never fires.'''
        EventManager.cancel(self._send_scheduled)

    def consume(self):
        '''Fire the event immediately and mark it as consumed.

        Safe to call multiple times — subsequent calls are no-ops.
        '''
        if self._consumed:
            return
        self.delay = time.time()
        self._consumed = True
        EventManager.cancel(self._send_scheduled)
        Event(self.id, self.content, self.messenger)


class _ScheduledEvent(ScheduledEvent):
    # XXX: Remove legacy support
    pass


def schedule(id: str, delay=0.0, content=None, messenger=None) -> ScheduledEvent:
    '''Send an event that can be reacted to with a delay.

    :param id: Identifier of the event; can be any object. If `id` is callable, `content` can be used as argument.
    :param delay: Time delay in seconds.
    :param content: This can be used to store data in an event.
    :param messenger: Can be used to store an object.
    '''
    if callable(id):
        return ScheduledCallback(id, delay, content)
    return ScheduledEvent(delay, id, content, messenger)


class ScheduledCallback():
    '''Event generated by `uplogic.events.schedule_callback()`.

    **Not intended for manual use.**

    :param cb: Callback to be evaluated.
    :param delay: Delay with which to call the function in seconds.
    :param arg: If this is defined, callback will be called with this
    argument.
    '''

    def __init__(self, cb, delay=0.0, arg=None):
        self.time = time.time()
        self.delay = self.time + delay
        self.callback = cb
        self.arg = arg
        self._consumed = False
        EventManager.schedule(self._call_scheduled)

    @property
    def time_left(self):
        '''Seconds remaining until the callback fires.

        :returns: ``float`` — may be negative if the callback is overdue.
        '''
        return self.delay - time.time()

    def _call_scheduled(self):
        if time.time() >= self.delay:
            self.consume()

    def consume(self):
        '''Invoke the callback immediately and mark it as consumed.

        Passes ``arg`` to the callback if one was provided. Safe to call
        multiple times — subsequent calls are no-ops.
        '''
        if self._consumed:
            return
        self.delay = time.time()
        self._consumed = True
        EventManager.cancel(self._call_scheduled)
        if self.arg is not None:
            self.callback(self.arg)
        else:
            self.callback()

    def cancel(self):
        '''Cancel the scheduled callback so it is never invoked.'''
        EventManager.cancel(self._call_scheduled)


class _ScheduledCallback(ScheduledCallback):
    # XXX: Remove legacy support
    pass


def schedule_callback(cb, delay=0.0, arg=None) -> ScheduledCallback:
    '''Call a function with a delay. The function can have an argument when
    defined as a keyword.

    Callback cannot return anything.

    :param cb: Callback to be evaluated.
    :param delay: Delay with which to call the function in seconds.
    :param arg: If this is defined, callback will be called with this
    argument.
    '''
    return ScheduledCallback(cb, delay, arg)
