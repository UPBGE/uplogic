'''OSC (Open Sound Control) subpackage for uplogic networking.

Provides :class:`~uplogic.network.osc.OSC_Server` and
:class:`~uplogic.network.osc.OSC_Client` built on top of the ``python-osc``
(``pythonosc``) library.  Incoming messages are dispatched through the uplogic
event system so handlers execute on the main game thread.

Typical usage::

    from uplogic.network.osc import OSC_Server, OSC_Client

    server = OSC_Server(port=9000)
    server.map('/update', my_handler)

    client = OSC_Client('127.0.0.1', port=9000)
    client.send('/update', [42])
'''

from .server_osc import OSC_Server
from .client_osc import OSC_Client