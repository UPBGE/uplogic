import argparse
import socket
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
import threading
import time

class OSC_Server:

    def __init__(self, ip=None, port=8304):
        parser = argparse.ArgumentParser()
        if ip is None:
            ip = socket.gethostbyname(socket.gethostname())
        parser.add_argument("--ip",
            default=ip, help="The ip to listen on")
        parser.add_argument("--port",
            type=int, default=port, help="The port to listen on")
        args = parser.parse_args()

        self.dispatcher = Dispatcher()
        self.map('/icom', self._print_debug)
        self.server = osc_server.ThreadingOSCUDPServer(
            (args.ip, args.port), self.dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        print("Serving on {}".format(self.server.server_address))

    def _print_debug(self, address, args):
        print(address, args)

    def map(self, address: str, callback, *args: list, needs_reply_address: bool = False):
        print(f'Mapping {address} to {callback}.')
        """Map a callback to an address. Callback receives (`address`, `args`, `volume`)
        
        :param `address`: address identifier (example: `"/update"`).
        :param `callback`: Callback function that will be called as the handler for the given address.
        :param `args`: Fixed arguements that will be passed to the callback function.
        :param `needs_reply_address`: Whether the IP address from which the message originated from shall be passed as
        an argument to the handler callback identifier.
        """
        return self.dispatcher.map(address, callback, *args, needs_reply_address=needs_reply_address)

    def shutdown(self) -> None:
        print(f'Shutting down OSC Server on {self.server.server_address[0]}:{self.server.server_address[1]}')
        self.server.shutdown()
        self.server.socket.close()
