'''OSC server implementation for uplogic.

Wraps ``pythonosc.osc_server.ThreadingOSCUDPServer`` in a background thread
and routes incoming OSC messages through the uplogic event system so that
registered callbacks execute safely on the main game thread.
'''

import socket
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
import threading
from uplogic import events
from uplogic import console


class OSC_Server:
    '''UDP OSC server that dispatches messages via the uplogic event system.

    On construction the server binds to *ip*:*port*, registers a built-in
    debug handler for ``/icom``, and starts a background daemon thread that
    calls ``serve_forever``.  All user-registered callbacks are wrapped in a
    :func:`~uplogic.events.schedule` call so they run on the next game tick
    rather than inside the networking thread.

    :param ip: IP address to bind to.  Defaults to the local machine's primary
        hostname address when ``None``.
    :param port: UDP port to listen on.  Defaults to ``8304``.
    '''

    def __init__(self, ip=None, port=8304):
        self._mapped_callbacks = {}

        if ip is None:
            ip = socket.gethostbyname(socket.gethostname())

        self.dispatcher = Dispatcher()
        self.map('/icom', self._print_debug)
        self.server = osc_server.ThreadingOSCUDPServer(
            (ip, port), self.dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        console.debug("Serving on {}".format(self.server.server_address))

    def _print_debug(self, address, args):
        '''Built-in handler for the ``/icom`` address — logs address and args at
        debug level.
        '''
        console.debug(address, args)

    def map(self, address: str, callback, *args: list, needs_reply_address: bool = False):
        '''Register *callback* as the handler for the given OSC *address*.

        The callback is wrapped so it is deferred through
        :func:`~uplogic.events.schedule` and therefore executed on the main
        game thread rather than the networking thread.

        :param address: OSC address pattern to match, e.g. ``"/update"``.
        :param callback: Callable invoked when a matching message arrives.
            Receives ``(address, *osc_args)`` plus any fixed *args*.
        :param args: Additional fixed arguments prepended to the callback
            invocation.
        :param needs_reply_address: When ``True``, the sender's IP address is
            passed as the first argument to *callback*.
        :returns: The ``pythonosc`` handler object, which can be passed to
            :meth:`unmap` to deregister it later.
        '''
        def _deferred_cb(*a):
            events.schedule(callback, content=a)

        handler = self.dispatcher.map(address, _deferred_cb, *args, needs_reply_address=needs_reply_address)
        handlers = self._mapped_callbacks.get(address, [])
        handlers.append(handler)
        self._mapped_callbacks[address] = handlers
        return handler

    def unmap(self, address, handler):
        '''Remove a previously registered *handler* for *address*.

        Silently logs an error if *handler* was not registered under *address*.

        :param address: OSC address pattern the handler was registered for.
        :param handler: Handler object previously returned by :meth:`map`.
        '''
        try:
            self.dispatcher.unmap(address, handler)
            self._mapped_callbacks.get(address, []).remove(handler)
        except ValueError as e:
            console.error(e)

    def unmap_all(self):
        '''Remove every registered handler from all addresses and clear the
        internal callback registry.
        '''
        for address in self._mapped_callbacks.keys():
            for handler in self._mapped_callbacks.get(address, []).copy():
                self.unmap(address, handler)
        self._mapped_callbacks.clear()

    def shutdown(self) -> None:
        '''Stop the background server thread and close the UDP socket.

        After this call the server can no longer receive messages.
        '''
        console.debug(f'Shutting down OSC Server on {self.server.server_address[0]}:{self.server.server_address[1]}')
        self.server.shutdown()
        self.server.socket.close()
