from uplogic.nodes import ULConditionNode
from uplogic.utils import is_waiting


class ULAnd(ULConditionNode):
    def __init__(self):
        ULConditionNode.__init__(self)
        self.ca = None
        self.cb = None

    def evaluate(self):
        ca = self.get_input(self.ca)
        self._set_ready()
        if is_waiting(ca) or not ca:
            self._set_value(False)
            return
        cb = self.get_input(self.cb)
        if is_waiting(cb) or not cb:
            self._set_value(False)
            return
        self._set_value(True)


class ULAndList(ULConditionNode):

    def __init__(self):
        ULConditionNode.__init__(self)
        self.ca = True
        self.cb = True
        self.cc = True
        self.cd = True
        self.ce = True
        self.cf = True

    def evaluate(self):
        self._set_ready()
        ca = self.get_input(self.ca)
        if is_waiting(ca) or not ca:
            self._set_value(False)
            return
        cb = self.get_input(self.cb)
        if is_waiting(cb) or not cb:
            self._set_value(False)
            return
        cc = self.get_input(self.cc)
        if is_waiting(cc) or not cc:
            self._set_value(False)
            return
        cd = self.get_input(self.cd)
        if is_waiting(cd) or not cd:
            self._set_value(False)
            return
        ce = self.get_input(self.ce)
        if is_waiting(ce) or not ce:
            self._set_value(False)
            return
        cf = self.get_input(self.cf)
        if is_waiting(cf) or not cf:
            self._set_value(False)
            return
        self._set_value(True)
