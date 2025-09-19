import socket
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
import threading
from uplogic import events
from uplogic import console


class OSC_Server:

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
        console.debug(address, args)

    def map(self, address: str, callback, *args: list, needs_reply_address: bool = False):
        """Map a callback to an address. Callback receives (`address`, `args`, `volume`)
        
        :param `address`: address identifier (example: `"/update"`).
        :param `callback`: Callback function that will be called as the handler for the given address.
        :param `args`: Fixed arguements that will be passed to the callback function.
        :param `needs_reply_address`: Whether the IP address from which the message originated from shall be passed as
        an argument to the handler callback identifier.
        """
        def _deferred_cb(*a):
            events.schedule(callback, content=a)

        handler = self.dispatcher.map(address, _deferred_cb, *args, needs_reply_address=needs_reply_address)
        handlers = self._mapped_callbacks.get(address, [])
        handlers.append(handler)
        self._mapped_callbacks[address] = handlers
        return handler

    def unmap(self, address, handler):
        try:
            self.dispatcher.unmap(address, handler)
            del self._mapped_callbacks[address]
        except ValueError as e:
            console.error(e)

    def unmap_all(self):
        for address in self._mapped_callbacks.keys():
            for handler in self._mapped_callbacks.get(address, []).copy():
                self.unmap(address, handler)
        self._mapped_callbacks.clear()

    def shutdown(self) -> None:
        console.debug(f'Shutting down OSC Server on {self.server.server_address[0]}:{self.server.server_address[1]}')
        self.server.shutdown()
        self.server.socket.close()
