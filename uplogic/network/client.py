import socket
import pickle
import threading
import bge
from uplogic.utils.constants import DISCONNECT_MSG
from uplogic.logging import error, success
from uplogic.serialize import *

class Client:

    def __init__(self, server, port=8303, connect=False):
        self.scene = bge.logic.getCurrentScene()
        self.server = server
        self.socket = None
        self.port = port
        self.connected = False
        if connect:
            self.connect()

    def connect(self):
        if self.connected:
            print('Client Already Connected! Aborting.')
            return
        print(f'Connecting to {self.server}...')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self.disconnect not in self.scene.onRemove:
                self.scene.onRemove.append(self.disconnect)
            self.socket.connect((self.server, self.port))
            self.connected = True
            thread = threading.Thread(target=self.update)
            thread.start()
            success('[SUCCESS]')
        except socket.error as e:
            error('[ERROR]')
            error(e)
            return

    def disconnect(self, flag=True):
        if not self.connected or self.socket is None:
            print('Client Not Connected!')
            return
        print(f'Disconnecting from {self.server}...')
        if flag:
            self.socket.send(pickle.dumps(DISCONNECT_MSG))
            self.socket.shutdown(socket.SHUT_WR)
            self.socket.close()
        self.socket = None
        self.connected = False
        success('[SUCCESS]')

    def send(self, msg, subject=''):
        if self.connected and self.socket is not None:
            try:
                if subject:
                    msg = {
                        'subject': subject,
                        'content': msg
                    }
                self.socket.send(pickle.dumps(msg))
            except pickle.PicklingError:
                error(f'Cannot serialize {msg}!')
            except TypeError:
                error(f'Cannot serialize {msg}!')
            except socket.error:
                error('Server unreachable')
                self.disconnect()
            except Exception as e:
                error(f'Exception: {e}')
                self.disconnect()

    def on_receive(self, msg):
        pass

    def update(self):
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
        self.disconnect(False)
        print('Closing')
