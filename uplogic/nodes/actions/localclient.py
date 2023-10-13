from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.network import Client
from time import time
from uplogic.events import send, receive


class ULLocalClient(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.connect_cond = None
        self.ip_address = None
        self.port = None
        self.disconnect_cond = None

        self.on_init = False

        self._connect = False
        self._disconnect = False
        self._was_connected = False
        self._last_time = time()
        self._received = False
        self._message = None

        self.CONNECT = ULOutSocket(self, self.get_connect)
        self.CONNECTED = ULOutSocket(self, self.get_connected)
        self.DISCONNECT = ULOutSocket(self, self.get_disconnect)
        self.CLIENT = ULOutSocket(self, self.get_client)
        self.RECEIVED = ULOutSocket(self, self.get_received)
        self.MSG = ULOutSocket(self, self.get_message)

    def get_connect(self):
        return self._connect

    def get_connected(self):
        return self._client.connected

    def get_disconnect(self):
        return self._disconnect

    def get_client(self):
        return self._client

    def get_received(self):
        return self._received

    def get_message(self):
        return self._received.content if self._received else None

    def on_receive(self, msg):
        send(self._client, msg)

    def setup(self, tree):
        self._client = Client(
            self.get_input(self.ip_address),
            self.get_input(self.port),
            self.on_init
        )
        self._client.on_receive = self.on_receive

    def evaluate(self):
        self.done = False
        self._connect = False
        self._disconnect = False
        self._received = receive(self._client)
        if self._was_connected != self._client.connected:
            if self._client.connected:
                self._connect = True
            else:
                self._disconnect = True
            self._was_connected = self._client.connected
        if self.get_input(self.connect_cond):
            self._client.connect()
        if self.get_input(self.disconnect_cond):
            self._client.disconnect()
        if not self._client.connected:
            self._client.server = self.get_input(self.ip_address)
            self._client.port = self.get_input(self.port)
