from pythonosc import udp_client
from uplogic import console


class OSC_Client:

    def __init__(self, server, port=8304):
        self.client = udp_client.DispatchClient(server, port)
        console.debug(f'OSC Client Connected to {server}')

    def map(self, address: str, callback, *args: list, needs_reply_address: bool = False):
        """Map a callback to an address.
        Valid callback signatures:
        - (`address`, `*osc_args`)
        - (`address`, `args`, `*osc_args`)
        - (`client_address`, `address`, `*osc_args`)
        - (`client_address`, `address`, `args`, `*osc_args`)
        
        :param address: address identifier (example: `"/update"`).
        :param callback: Callback function that will be called as the handler for the given address.
        :param args: Fixed arguements that will be passed to the callback function.
        :param needs_reply_address: Whether the IP address from which the message originated from shall be passed as
        an argument to the handler callback identifier.
        """
        return self.client.dispatcher.map(address, callback, *args, needs_reply_address=needs_reply_address)

    def send(self, address, content=[0]):
        try:
            self.client.send_message(address=address, value=content)
        except Exception as e:
            console.warning(f'OSC Client: Message could not be sent. Reason:\n\t{e}')
