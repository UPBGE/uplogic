from uplogic.utils import debug
import bge
import bpy
import pickle
import socket
import threading
from uplogic.utils import DISCONNECT_MSG


class Server:

    def __init__(self, ip=None, port=8303):
        if ip is None:
            ip = socket.gethostbyname(socket.gethostname())
        self.ip = ip
        self.clients = []
        self.entities = {'server': []}
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.scene = bge.logic.getCurrentScene()
        self.startup()

    def startup(self):
        print('Starting server...')
        try:
            bge.logic.getCurrentScene().onRemove.append(self.shutdown)
            self.socket.setblocking(False)
            self.socket.settimeout(.0001)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.ip, self.port))
            thread = threading.Thread(target=self.update)
            thread.start()
        except socket.error as e:
            print(e, 'SocketError')
            self.shutdown()
            return
        except Exception as e:
            print(e, 'Exception')
            self.shutdown()
            return
        self.socket.listen()
        print('Success.')

    def shutdown(self):
        print('Stopping server...')
        scene = bge.logic.getCurrentScene()
        if self.shutdown in scene.onRemove:
            scene.onRemove.remove(self.shutdown)
        try:
            self.socket.shutdown(socket.SHUT_WR)
            self.socket.close()
            for conn in self.clients:
                conn.close()
            self.clients = []
            # if self.update in bge.logic.getCurrentScene().pre_draw:
            #     bge.logic.getCurrentScene().pre_draw.remove(self.update)
            print('Success.')
        except Exception as e:
            print(e)
            print('Runtime Exit.')

    def restart(self):
        self.shutdown()
        self.startup()

    def threaded_client(self, conn, addr):
        connected = True
        self.clients.append(conn)
        while connected:
            try:
                msg = conn.recv(2**14)
                if not msg or msg == DISCONNECT_MSG:
                    print('Client disconnected.')
                    connected = False
                else:
                    entity = pickle.loads(msg)
                    # if dat['id'] in bpy.data.objects:
                    if entity['streamtype']:
                        self.entities[conn][entity['id']] = entity
                            # bobj = bpy.data.objects[dat['id']]
                            # game_object = scene.getGameObjectFromObject(bobj)
                            # attrs = dat['set_attrs']
                            # for i, (attr, val) in enumerate(attrs.items()):
                            #     setattr(game_object, attr, val)
                    else:
                        pass
            except socket.error as e:
                pass  # print('SocketError:', e)
                connected = False
            except pickle.UnpicklingError as e:
                pass  # print('PickleError:', e)
            except Exception as e:
                print(e)
                print('Threaded Client error')
                connected = False
        print('Closing Connection...')
        conn.close()

    def sync(self):
        # print(self.entities)
        for connection in self.entities.copy():
            data = self.entities[connection]
            for entity_id in self.entities[connection]:
                # name = entity['id']
                entity = data[entity_id]
                print(data)
                bobj = bpy.data.objects.get(entity_id)
                if bobj is not None:
                    game_object = self.scene.getGameObjectFromObject(bobj)
                    attrs = entity['set_attrs']
                    for i, (attr, val) in enumerate(attrs.items()):
                        setattr(game_object, attr, val)

    def update(self):
        active = True
        while active:
            try:
                conn, add = self.socket.accept()
                print("Connected to:", add)
                thread = threading.Thread(target=self.threaded_client, args=(conn, add))
                thread.start()
                self.entities[conn] = {}
                print(f'[ACTIVE CONNECTIONS] {threading.activeCount() - 2}')
            except BlockingIOError:
                pass
            except TimeoutError:
                pass
            except socket.timeout:
                pass
            except OSError as e:
                print(e, 'OSError')
                active = False
                self.shutdown()
            except Exception as e:
                print(e, 'Exception')
                active = False
                self.shutdown()
