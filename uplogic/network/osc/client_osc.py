'''OSC client implementation for uplogic.

Wraps ``pythonosc.udp_client.DispatchClient`` to send OSC messages to a remote
server and, optionally, register local handlers for replies.
'''

from pythonosc import udp_client
from uplogic import console


class OSC_Client:
    '''UDP OSC client for sending messages to an :class:`OSC_Server`.

    On construction a ``pythonosc`` ``DispatchClient`` is created and a debug
    message is logged confirming the target address.

    :param server: Hostname or IP address of the remote OSC server.
    :param port: UDP port of the remote server.  Defaults to ``8304``.
    '''

    def __init__(self, server, port=8304):
        self.client = udp_client.DispatchClient(server, port)
        console.debug(f'OSC Client Connected to {server}')

    def map(self, address: str, callback, *args: list, needs_reply_address: bool = False):
        '''Register a local *callback* for incoming OSC messages on *address*.

        Delegates directly to the underlying dispatcher without deferring
        through the event system — suitable for reply handling from the same
        ``DispatchClient``.

        Valid callback signatures accepted by ``pythonosc``:

        - ``(address, *osc_args)``
        - ``(address, args, *osc_args)``
        - ``(client_address, address, *osc_args)``
        - ``(client_address, address, args, *osc_args)``

        :param address: OSC address pattern to match, e.g. ``"/reply"``.
        :param callback: Callable invoked when a matching message arrives.
        :param args: Additional fixed arguments passed to *callback*.
        :param needs_reply_address: When ``True``, the sender's IP address is
            prepended to the callback arguments.
        :returns: The ``pythonosc`` handler object.
        '''
        return self.client.dispatcher.map(address, callback, *args, needs_reply_address=needs_reply_address)

    def send(self, address, content=[0]):
        '''Send an OSC message to the remote server.

        Logs a warning (without raising) if the message cannot be delivered.

        :param address: OSC address string, e.g. ``"/update"``.
        :param content: Value or list of values to include as the message
            payload.  Defaults to ``[0]``.
        '''
        try:
            self.client.send_message(address=address, value=content)
        except Exception as e:
            console.warning(f'OSC Client: Message could not be sent. Reason:\n\t{e}')
