'''TCP server implementation for uplogic networking.'''
import bge
import bpy
import pickle
import socket
import threading
from uplogic.utils.constants import DISCONNECT_MSG
from uplogic import console
import sys


class Server:
    '''Threaded TCP server that accepts multiple simultaneous client connections.

    Messages are serialised with :mod:`pickle`. Override :meth:`on_receive` in a
    subclass to handle incoming data. The server runs its accept loop in a
    background ``threading.Thread`` and spawns a further thread per connected
    client.

    :param ip: Bind address. Defaults to the machine's primary IP via
        ``socket.gethostbyname(socket.gethostname())``.
    :param port: TCP port to listen on (default ``8303``).
    :param start: When ``True``, call :meth:`start` immediately after construction.
    '''

    def __init__(self, ip=None, port=8303, start=False):
        if ip is None:
            ip = socket.gethostbyname(socket.gethostname())
        self.ip = ip
        self.clients: list[socket.socket] = []
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.scene = bge.logic.getCurrentScene()
        self.running = False
        self.shutdown_on_scene_end = True
        if start:
            self.start()

    def start(self):
        '''Bind the socket and begin accepting connections in a background thread.

        Registers :meth:`shutdown` on the scene ``onRemove`` list when
        :attr:`shutdown_on_scene_end` is ``True``. Does nothing if the server is
        already running.
        '''
        if self.running:
            console.debug('Server already running.')
            return
        try:
            console.debug(f'Starting Server: IP={self.ip} Port={self.port}')
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.shutdown_on_scene_end:
                bge.logic.getCurrentScene().onRemove.append(self.shutdown)
            self.socket.settimeout(.0001)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.ip, self.port))
            self.running = True
            thread = threading.Thread(target=self.update)
            thread.start()
        except socket.error as e:
            console.error(e)
            self.shutdown()
            return
        except Exception as e:
            console.error(e)
            self.shutdown()
            return
        self.socket.listen()
        console.success('[SERVER RUNNING]')

    def shutdown(self):
        '''Close all client connections and shut down the listening socket.

        Removes the ``onRemove`` hook, closes every connected socket, and clears
        :attr:`clients`. Safe to call when the server is already stopped.
        '''
        if not self.running:
            # console.debug(f"{self.ip}:{self.port} offline.")
            return
        console.debug(f'Stopping Server: IP={self.ip} Port={self.port}')
        scene = bge.logic.getCurrentScene()
        if self.shutdown in scene.onRemove:
            scene.onRemove.remove(self.shutdown)
        try:
            self.running = False
            for conn in self.clients:
                conn.close()
            if self.clients:
                self.socket.shutdown(socket.SHUT_WR)
            self.clients = []
            self.socket.close()
            console.success('[SERVER STOPPED]')
            # print('[SERVER STOPPED]')
        except Exception as e:
            self.running = False
            self.clients = []
            self.socket.close()
            console.error(e)
            console.error('Runtime Exit.')

    def restart(self):
        '''Shut the server down and immediately start it again.'''
        self.shutdown()
        self.start()

    def on_receive(self, msg):
        '''Called in the client thread each time a complete message arrives.

        Override this method in a subclass to handle incoming data.

        :param msg: The deserialised Python object received from the client.
        '''
        pass

    def send(self, msg, subject=''):
        '''Broadcast *msg* to every connected client.

        When *subject* is provided the data is wrapped in a ``dict`` with
        ``"subject"`` and ``"content"`` keys before serialisation.

        :param msg: Any :mod:`pickle`-serialisable Python object.
        :param subject: Optional routing string; wraps *msg* in an envelope dict.
        '''
        if self.socket and self.running:
            if subject:
                msg = {
                    'subject': subject,
                    'content': msg
                }
            for conn in self.clients:
                conn.send(pickle.dumps(msg))

    def threaded_client(self, conn: socket.socket, addr):
        '''Receive loop for a single client connection, run in its own thread.

        Reads messages in a loop, calls :meth:`on_receive` for each, and removes
        the connection from :attr:`clients` when the client disconnects or an
        unrecoverable error occurs.

        :param conn: The accepted :class:`socket.socket` for this client.
        :param addr: The ``(host, port)`` address tuple of the remote client.
        '''
        connected = True
        self.clients.append(conn)
        while connected and self.running:
            
            try:
                bmsg = conn.recv(2**14)
                msg = pickle.loads(bmsg)
                if not bmsg or msg == DISCONNECT_MSG:
                    console.debug('Client disconnected.')
                    connected = False
                else:
                    self.on_receive(msg)
            except ConnectionResetError:
                console.error(f'{e.__class__.__name__}: {e}')
                connected = False
            except socket.error as e:
                console.error(f'{e.__class__.__name__}: {e}')
                connected = False
            except pickle.UnpicklingError as e:
                pass
            except Exception as e:
                console.error(f'{e.__class__.__name__}: {e}')
                console.error('Threaded Client Error')
                connected = False
        self.clients.remove(conn)
        conn.send(pickle.dumps(DISCONNECT_MSG))
        console.debug('Closing Connection...')
        conn.close()
        # print(f'[ACTIVE CONNECTIONS] {len(self.clients)}')
        console.debug(f'[ACTIVE CONNECTIONS] {len(self.clients)}')
        return

    def update(self):
        '''Accept-loop that waits for incoming connections in a background thread.

        For each new connection a :meth:`threaded_client` thread is started.
        Runs until :attr:`running` is ``False`` or an unrecoverable socket error
        occurs.
        '''
        while self.running:
            # print('SERVER RUNNING')
            try:
                conn, add = self.socket.accept()
                console.debug(f"Established connection to: {add}")
                # print(f"Established connection to: {add}")
                thread = threading.Thread(target=self.threaded_client, args=(conn, add))
                thread.start()
                console.debug(f'[ACTIVE CONNECTIONS] {len(self.clients)}')
            except BlockingIOError:
                pass
            except socket.timeout:
                # debug(f"Operation Timeout")
                pass
            except TimeoutError:
                pass
            except OSError as e:
                self.running = False
                self.shutdown()
            except Exception as e:
                console.debug(e, 'Exception')
                self.running = False
                self.shutdown()
