import socket
import pickle
import bge
from uplogic.utils import debug, STREAMTYPE_DOWNSTREAM, STREAMTYPE_UPSTREAM


class Client:

    def __init__(self, server, port=8303, connect=False):
        self.scene = bge.logic.getCurrentScene()
        self.server = server
        self.socket = None
        self.port = port
        self.connected = False
        self.entities = []
        if connect:
            self.connect()

    def connect(self):
        if self.connected:
            print('Client Already Connected! Aborting.')
            return
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.server, self.port))
            if self.update not in self.scene.pre_draw:
                self.scene.pre_draw.append(self.update)
            self.connected = True
        except socket.error as e:
            print(e)
            self.disconnect()
            return

    def disconnect(self):
        if self.socket is None:
            print('Client Not Connected!')
            return
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()
        self.socket = None
        if self.update in self.scene.pre_draw:
            self.scene.pre_draw.remove(self.update)
        self.connected = False

    def add_entity(self, entity):
        self.entities.append(entity)

    def send(self):
        try:
            for entity in self.entities:
                dat = entity.get_data()
                if dat['streamtype']:
                    self.socket.send(pickle.dumps(dat))

        except Exception as e:
            self.disconnect()

    def update(self):
        if self.connected:
            self.send()
