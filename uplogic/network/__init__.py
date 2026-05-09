'''TCP networking for uplogic.

Provides a threaded TCP :class:`~uplogic.network.server.Server` and a
matching :class:`~uplogic.network.client.Client`.  Messages are
serialised with :mod:`pickle` and delivered to an :meth:`on_receive`
hook you override in a subclass.

Typical usage::

    from uplogic.network import Server, Client

    class GameServer(Server):
        def on_receive(self, msg):
            print('got', msg)

    srv = GameServer(port=8303, start=True)
'''
from .server import Server
from .client import Client
