import bge
import bpy
import pickle
import socket
import threading
from uplogic.utils.constants import DISCONNECT_MSG
from uplogic.logging import error, success, debug
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
        if start:
            self.start()

    def start(self):
        if self.running:
            print('Server already running.')
            return
        try:
            print('Starting server...')
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            bge.logic.getCurrentScene().onRemove.append(self.shutdown)
            self.socket.setblocking(False)
            self.socket.settimeout(.0001)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.ip, self.port))
            self.running = True
            thread = threading.Thread(target=self.update)
            thread.start()
        except socket.error as e:
            error(e)
            self.shutdown()
            return
        except Exception as e:
            error(e)
            self.shutdown()
            return
        self.socket.listen()
        success('[SUCCESS]')

    def shutdown(self):
        if not self.running:
            print("Server offline.")
            return
        print('Stopping server...')
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
            success('[SUCCESS]')
        except Exception as e:
            self.running = False
            self.clients = []
            self.socket.close()
            error(e)
            error('Runtime Exit.')

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
                    print('Client disconnected.')
                    self.clients.remove(conn)
                    connected = False
                else:
                    self.on_receive(msg)
            except socket.error as e:
                error(f'{e.__class__.__name__}: {e}')
                connected = False
            except pickle.UnpicklingError as e:
                pass
            except Exception as e:
                error(f'{e.__class__.__name__}: {e}')
                error('Threaded Client Error')
                connected = False
        conn.send(pickle.dumps(DISCONNECT_MSG))
        print('Closing Connection...')
        conn.close()
        debug(f'[ACTIVE CONNECTIONS] {len(self.clients)}')
        return

    def update(self):
        while self.running:
            try:
                conn, add = self.socket.accept()
                print(f"Connected to: {add}")
                thread = threading.Thread(target=self.threaded_client, args=(conn, add))
                thread.start()
                debug(f'[ACTIVE CONNECTIONS] {len(self.clients)}') # {threading.active_count() - 2}')
            except BlockingIOError:
                pass
            except socket.timeout:
                pass
            except TimeoutError:
                pass
            except OSError as e:
                self.running = False
                self.shutdown()
            except Exception as e:
                print(e, 'Exception')
                self.running = False
                self.shutdown()
        print('Server Shut Down')
