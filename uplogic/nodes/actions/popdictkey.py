from uplogic.nodes import ULActionNode
from uplogic import console


class ULPopDictKey(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.dict = None
        self.key = None
        self.new_dict = None
        self.OUT = self.add_output(self.get_done)
        self.DICT = self.add_output(self.get_dict)
        self.VALUE = self.add_output(self.get_value)

    def get_done(self):
        return self._done

    def get_dict(self):
        return self.new_dict

    def get_value(self):
        return self.value

    def evaluate(self):
        if not self.get_condition():
            return
        dictionary = self.get_input(self.dict)
        key = self.get_input(self.key)
        if key in dictionary:
            self.value = dictionary.pop(key)
        else:
            console.debug("Dict Delete Key Node: Key '{}' not in Dict!".format(key))
            return
        self.new_dict = dictionary
        self._done = True
