from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.network import Server
from uplogic.events import send, receive


class ULLocalServer(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.start_cond = None
        self.ip_address = None
        self.port = None
        self.stop_cond = None

        self.on_init = False

        self._started = False
        self._stopped = False
        self._was_running = False
        self._received = False
        self._message = None

        self.STARTED = ULOutSocket(self, self.get_started)
        self.RUNNING = ULOutSocket(self, self.get_running)
        self.STOPPED = ULOutSocket(self, self.get_stopped)
        self.SERVER = ULOutSocket(self, self.get_server)
        self.RECEIVED = ULOutSocket(self, self.get_received)
        self.MSG = ULOutSocket(self, self.get_message)

    def get_started(self):
        return self._started

    def get_running(self):
        return self._server.running

    def get_stopped(self):
        return self._stopped

    def get_server(self):
        return self._server

    def get_received(self):
        return self._received

    def get_message(self):
        return self._received.content if self._received else None

    def on_receive(self, msg):
        send(self._server, msg)

    def setup(self, tree):
        self._server = Server(
            self.get_input(self.ip_address),
            self.get_input(self.port),
            self.on_init
        )
        self._server.on_receive = self.on_receive

    def evaluate(self):
        self.done = False
        self._started = False
        self._stopped = False
        self._received = receive(self._server)
        if self._was_running != self._server.running:
            if self._server.running:
                self._started = True
            else:
                self._stopped = True
            self._was_running = self._server.running
        if self.get_input(self.start_cond):
            self._server.start()
        if self.get_input(self.stop_cond):
            self._server.shutdown()
        if not self._server.running:
            self._server.ip = self.get_input(self.ip_address)
            self._server.port = self.get_input(self.port)
