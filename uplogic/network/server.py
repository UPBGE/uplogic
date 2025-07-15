import bge
import bpy
import pickle
import socket
import threading
from uplogic.utils.constants import DISCONNECT_MSG
from uplogic import console
import time


class Server:

    def __init__(self, ip=None, port=8303, start=False):
        if ip is None:
            ip = socket.gethostbyname(socket.gethostname())
        self.ip = ip
        self.clients = []
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.scene = bge.logic.getCurrentScene()
        self.running = False
        self.shutdown_on_scene_end = True
        if start:
            self.start()

    def start(self):
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
        if not self.running:
            console.debug(f"{self.ip}:{self.port} offline.")
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
        except Exception as e:
            self.running = False
            self.clients = []
            self.socket.close()
            console.error(e)
            console.error('Runtime Exit.')

    def restart(self):
        self.shutdown()
        self.start()

    def on_receive(self, msg):
        pass

    def send(self, msg, subject=''):
        if self.socket and self.running:
            if subject:
                msg = {
                    'subject': subject,
                    'content': msg
                }
            for conn in self.clients:
                conn.send(pickle.dumps(msg))

    def threaded_client(self, conn, addr):
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
        console.debug(f'[ACTIVE CONNECTIONS] {len(self.clients)}')
        return

    def update(self):
        while self.running:
            try:
                conn, add = self.socket.accept()
                console.debug(f"Established connection to: {add}")
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
