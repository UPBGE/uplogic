from uplogic.nodes import ULActionNode


class ULEndObject(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.scene = None
        self.game_object = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_input(self.condition):
            return
        game_object = self.get_input(self.game_object)
        if game_object is self.network._owner:
            self.network._do_remove = True
        game_object.endObject()
        self._done = True
