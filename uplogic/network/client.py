import socket
import bge
from uplogic.utils import debug


server = socket.gethostbyname(socket.gethostname())


class Client:

    def __init__(self, port=8303):
        self.scene = bge.logic.getCurrentScene()
        self.socket = None
        self.port = port
        self.connected = False
        self.entities = {'upstream': [], 'downstream': []}
        self.connect()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((server, self.port))
            if self.update not in self.scene.pre_draw:
                self.scene.pre_draw.append(self.update)
            self.connected = True
        except socket.error as e:
            print(e)
            self.disconnect()
            return

    def disconnect(self):
        self.socket.close()
        self.socket = None
        if self.update in self.scene.pre_draw:
            self.scene.pre_draw.remove(self.update)
        self.connected = False
    
    def add_entity(self, entity):
        self.entities[entity.streamtype].append(entity)
    
    def send(self):
        try:
            for entity in self.entities['upstream']:
                self.socket.send(entity.get_data())
        except Exception as e:
            self.disconnect()
 
    def update(self):
        if self.connected:
            self.send()

########################################################################

# import asyncio


# class Client:

#     def __init__(self, port=8303):
#         self.host = '127.0.0.1'
#         self.port = port
#         self.startup()

#     def startup(self, port):
#         self.loop = asyncio.new_event_loop()
#         self.loop.run_until_complete(self.fetch())
    
#     async def fetch(self):
#         reader, writer = await asyncio.open_connection(self.host, self.port)

#         writer.write(b"Hello World")
#         await writer.drain()

