import argparse
from pythonosc import udp_client


class OSC_Client:

    def __init__(self, server, port=8304):
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default=server,
            help="The ip of the OSC server")
        parser.add_argument("--port", type=int, default=port,
            help="The port the OSC server is listening on")
        args = parser.parse_args()

        self.client = udp_client.DispatchClient(args.ip, args.port)
        self.map('/icom', self._print_debug)
        print(f'OSC Client Connected to {server}')

    def _print_debug(self, address, args):
        print(address, args)

    def map(self, address: str, callback, *args: list, needs_reply_address: bool = False):
        """Map a callback to an address.
        Valid callback signatures:
        - (`address`, `*osc_args`)
        - (`address`, `args`, `*osc_args`)
        - (`client_address`, `address`, `*osc_args`)
        - (`client_address`, `address`, `args`, `*osc_args`)
        
        :param `address`: address identifier (example: `"/update"`).
        :param `callback`: Callback function that will be called as the handler for the given address.
        :param `args`: Fixed arguements that will be passed to the callback function.
        :param `needs_reply_address`: Whether the IP address from which the message originated from shall be passed as
        an argument to the handler callback identifier.
        """
        return self.client.dispatcher.map(address, callback, *args, needs_reply_address=needs_reply_address)

    def send(self, address, content=[0]):
        try:
            self.client.send_message(address=address, value=content)
        except:
            print('oops')
