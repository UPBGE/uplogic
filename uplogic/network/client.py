'''TCP client implementation for uplogic networking.'''
import socket
import pickle
import threading
import bge
from uplogic.utils.constants import DISCONNECT_MSG
from uplogic import console
from uplogic.serialize import *
import sys


class Client:
    '''TCP client that connects to a :class:`~uplogic.network.server.Server`.

    Messages are serialised with :mod:`pickle`. Override :meth:`on_receive` in
    a subclass to handle data pushed from the server. Incoming messages are
    processed in a background ``threading.Thread``.

    :param server: IP address or hostname of the server to connect to.
    :param port: TCP port (default ``8303``).
    :param connect: When ``True``, call :meth:`connect` immediately after
        construction.
    '''

    def __init__(self, server, port=8303, connect=False):
        self.scene = bge.logic.getCurrentScene()
        self.server = server
        self.socket = None
        self.port = port
        self.connected = False
        self.disconnect_on_scene_end = True
        if connect:
            self.connect()

    def connect(self):
        '''Open a TCP connection to the server and start the receive loop.

        Registers :meth:`disconnect` on the scene ``onRemove`` list when
        :attr:`disconnect_on_scene_end` is ``True``. Does nothing if already
        connected.
        '''
        if self.connected:
            # console.debug('Client Already Connected! Aborting.')
            return
        console.debug(f'Connecting to {self.server}...')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self.disconnect_on_scene_end:
                if self.disconnect not in self.scene.onRemove:
                    self.scene.onRemove.append(self.disconnect)
            self.socket.connect((self.server, self.port))
            self.connected = True
            thread = threading.Thread(target=self.update)
            thread.start()
            console.success('[SUCCESS]')
        except socket.error as e:
            console.error('[ERROR]')
            console.error(e)
            return

    def disconnect(self, flag=True):
        '''Close the connection to the server.

        Sends the disconnect sentinel, shuts down the socket write half, and clears
        :attr:`connected`. Removes the ``onRemove`` hook if registered.

        :param flag: When ``True`` (default), send the disconnect message and
            perform a clean socket shutdown before closing. Set to ``False`` when
            the server has already closed the connection.
        '''
        if not self.connected or self.socket is None:
            console.debug('Client Not Connected!')
            return
        console.debug(f'Disconnecting from {self.server}...')
        if flag:
            self.socket.send(pickle.dumps(DISCONNECT_MSG))
            self.socket.shutdown(socket.SHUT_WR)
            self.socket.close()
        self.socket = None
        self.connected = False
        if self.disconnect in self.scene.onRemove:
            self.scene.onRemove.remove(self.disconnect)
        console.success('[SUCCESS]')

    def send(self, msg, subject=''):
        '''Send *msg* to the server.

        When *subject* is provided the data is wrapped in a ``dict`` with
        ``"subject"`` and ``"content"`` keys before serialisation. Silently
        disconnects on socket errors.

        :param msg: Any :mod:`pickle`-serialisable Python object.
        :param subject: Optional routing string; wraps *msg* in an envelope dict.
        '''
        if self.connected and self.socket is not None:
            try:
                if subject:
                    msg = {
                        'subject': subject,
                        'content': msg
                    }
                self.socket.send(pickle.dumps(msg))
            # except pickle.PicklingError:
            #     console.error(f'Cannot serialize {msg}!')
            # except TypeError:
            #     console.error(f'Cannot serialize {msg}!')
            except socket.error:
                # console.error('Server unreachable')
                self.disconnect()
            except Exception as e:
                # console.error(f'Exception: {e}')
                self.disconnect()

    def on_receive(self, msg):
        '''Called in the receive thread each time a complete message arrives from
        the server.

        Override this method in a subclass to handle incoming data.

        :param msg: The deserialised Python object received from the server.
        '''
        pass

    def update(self):
        '''Receive loop that runs in a background thread while :attr:`connected` is
        ``True``.

        Reads messages from the socket, deserialises them with :mod:`pickle`, and
        calls :meth:`on_receive` for each. Stops when the server sends the
        disconnect sentinel or the socket raises an exception.
        '''
        while self.connected and self.socket:
            try:
                bmsg = self.socket.recv(2048)
                msg = pickle.loads(bmsg)
                if not bmsg or msg == DISCONNECT_MSG:
                    self.connected = False
                else:
                    self.on_receive(msg)
            except Exception as e:
                self.connected = False
        # self.disconnect(False)
        # console.debug('Closing')
