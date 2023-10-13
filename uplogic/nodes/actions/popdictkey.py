from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import debug


class ULPopDictKey(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.dict = None
        self.key = None
        self.new_dict = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)
        self.DICT = ULOutSocket(self, self.get_dict)
        self.VALUE = ULOutSocket(self, self.get_value)

    def get_done(self):
        return self.done

    def get_dict(self):
        return self.new_dict

    def get_value(self):
        return self.value

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        dictionary = self.get_input(self.dict)
        key = self.get_input(self.key)
        if key in dictionary:
            self.value = dictionary.pop(key)
        else:
            debug("Dict Delete Key Node: Key '{}' not in Dict!".format(key))
            return
        self.new_dict = dictionary
        self.done = True
