import socket
import pickle
from _thread import start_new_thread
import threading
import sys
from uplogic.utils import debug
import bge
import bpy


server = socket.gethostbyname(socket.gethostname())
DISCONNECT_MSG = '!DISCONNECT'


class Server:

    def __init__(self, port=8303):
        self.clients = []
        self.startup(port)
        bge.logic.getCurrentScene().onRemove.append(self.shutdown)
    
    def startup(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)
        self.socket.settimeout(.0001)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
        # self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
        # self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
        debug('Starting server...')
        try:
            self.socket.bind((server, port))
            thread = threading.Thread(target=self.update)
            thread.start()
        except socket.error as e:
            # print(e)
            return
        self.socket.listen()
        debug('Success')

    def shutdown(self):
        debug('Stopping server...')
        self.socket.close()
        if self.update in bge.logic.getCurrentScene().pre_draw:
            bge.logic.getCurrentScene().pre_draw.remove(self.update)
        debug('Success')

    def threaded_client(self, conn, addr):
        scene = bge.logic.getCurrentScene()
        connected = True
        while connected:
            print('connected')
            try:
                msg = conn.recv(2048)
                if not msg:
                    print('Connection Lost due to missing data')
                    connected = False
                else:
                    dat = pickle.loads(msg)
                    if dat['id'] in bpy.data.objects:
                        bobj = bpy.data.objects[dat['id']]
                        game_object = scene.getGameObjectFromObject(bobj)
                        attrs = dat['set_attrs']
                        for i, (attr, val) in enumerate(attrs.items()):
                            setattr(game_object, attr, val)
                    else:
                        print("Don't find no thang hony")
            except Exception as e:
                print(e)
        debug("Lost connection")
        conn.close()


    def update(self):
        active = True
        while active:
            try:
                conn, add = self.socket.accept()
                print("Connected to:", add)
                # start_new_thread(self.threaded_client, (conn,))
                thread = threading.Thread(target=self.threaded_client, args=(conn, add))
                thread.start()
                print(f'[ACTIVE CONNECTIONS] {threading.activeCount() - 2}')
            except BlockingIOError:
                pass
            except TimeoutError:
                pass
            except OSError:
                active = False
                self.shutdown()
            except Exception:
                active = False
                self.shutdown()
