from bge import logic

def alpha_move(a, b, fac):
    if a < b:
        return a + fac
    elif a > b:
        return a - fac
    else:
        return a


_loaded_userlogic_files = {}


def load_user_logic(module_name):
    full_path = logic.expandPath(
        "//bgelogic/cells/{}.py".format(module_name)
    )
    loaded_value = _loaded_userlogic_files.get(full_path)
    if loaded_value:
        return loaded_value
    import sys
    python_version = sys.version_info
    major = python_version[0]
    minor = python_version[1]
    if (major < 3) or (major == 3 and minor < 3):
        import imp
        loaded_value = imp.load_source(module_name, full_path)
    elif (major == 3) and (minor < 5):
        from importlib.machinery import SourceFileLoader
        loaded_value = SourceFileLoader(module_name, full_path).load_module()
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, full_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        loaded_value = module
    _loaded_userlogic_files[module_name] = loaded_value
    return loaded_value


class LoopList(list):
    pass


class ULLogicBase(object):
    def get_value(self, to_node=None):
        pass


class ULLogicContainer(ULLogicBase):

    def __init__(self):
        self._uid = None
        self._value = None
        self._children = []
        self._done = False
        self.network = None

    def get_value(self, to_node=None):
        return self._value

    def _set_value(self, value):
        self._value = value

    def setup(self, network):
        """
        This is called by the network once, after all the
        cells have been loaded into the tree.
        :return: None
        """
        pass

    def stop(self, network):
        pass

    def reset(self):
        """
        Resets the status of the cell.
        A cell may override this to reset other states
        or to keep the value if evaluation is required
        to happen only once (or never at all)
        :return:
        """
        pass

    def evaluate(self):
        """
        A logic cell implements this method to do its job. The network
        evaluates a cell. When that happens, the cell is
         removed from the update queue.
        :return:
        """
        raise NotImplementedError(
            "{} doesn't implement evaluate".format(self.__class__.__name__)
        )

    def _skip_evaluate(self):
        return

    def deactivate(self):
        self.evaluate = self._skip_evaluate


###############################################################################
# Socket
###############################################################################


class Output(ULLogicBase):
    def __init__(self, node, value_getter):
        self.node = node
        self.result = None
        self._value_getter = value_getter

    @property
    def result(self):
        return self._result
    
    @result.setter
    def result(self, val):
        # if self.node.loop_mode and val is None:
        #     self._result = LoopList()
        #     return
        self._result = val

    def _value_getter(self):
        pass

    def get_value(self, to_node=None):
        self.node.fetched = True
        result = self.result
        if result is None:
            result = self._value_getter()
            if self.node.loop_mode:
                result = []
                for x in range(self.node.loop_size):
                    self.node.loop_idx = x
                    result.append(self._value_getter())
                result = LoopList(result)
            self.result = result
        return result


class ULOutSocket(Output):
    pass


###############################################################################
# Basic Cells
###############################################################################


def results(*names):

    def deco(cls):
        for name in names:

            def getResult(self, name=name):
                value = self.results.get(name, None)
                if self.loop_mode and value is not None:
                    return value[self.loop_idx]
                return value

            def setResult(self, value, name=name):
                if self.loop_mode:
                    set_val = value
                    value = self.results.get(name, LoopList())
                    value.append(set_val)
                self.results[name] = value

            prop = property(getResult, setResult)
            setattr(cls, name, prop)

        return cls
    return deco


class ULLogicNode(ULLogicContainer):

    def __init__(self):
        self.loop_mode = False
        self.loop_idx = 0
        self.loop_size = 0
        self.condition = False
        self.results = {}
        self.outputs = []
        self.fetched = False
        self.get_input = self._get_input
        super().__init__()

    @property
    def loop_mode(self):
        return self._loop_mode

    @loop_mode.setter
    def loop_mode(self, val):
        self._loop_mode = val
        self.get_input = self._get_input_loop if val else self._get_input

    def reset(self):
        super().reset()
        self.results = {}
        self.loop_mode = False
        self.loop_idx = 0
        self.get_input = self._get_input
        for o in self.outputs:
            o.result = None

    def add_output(self, getter):
        o = Output(self, getter)
        self.outputs.append(o)
        return o

    def _get_input(self, param):
        if isinstance(param, ULLogicBase):
            return param.get_value(self)
        return param

    def _get_input_loop(self, param):
        if isinstance(param, ULLogicBase):
            param.node.loop_mode = True
            param.node.loop_size = self.loop_size
            param.node.loop_idx = self.loop_idx
            param = param.get_value(self)
        if isinstance(param, LoopList):
            return param[self.loop_idx]
        return param

    def evaluate(self):
        pass

    def evaluate_loop(self, loop):
        pass


class ULParameterNode(ULLogicNode):

    def __init__(self):
        self._fetched = False
        super().__init__()

    @property
    def fetched(self):
        return self._fetched

    @fetched.setter
    def fetched(self, val):
        if val and not self._fetched:
            self.fetch()
        self._fetched = val

    def reset(self):
        self._fetched = False
        return super().reset()

    def fetch(self):
        pass


class ULActionNode(ULLogicNode):

    def __init__(self):
        self._done = False
        self.condition = False
        self.get_condition = self._get_condition
        super().__init__()

    def get_done(self):
        return self._done

    def reset(self):
        super().reset()
        self.get_condition = self._get_condition
        self._done = False

    def _get_condition(self, socket=None):
        condition = socket if socket else self.condition
        if isinstance(condition, ULLogicBase):
            condition = condition.get_value(self)
        if isinstance(condition, LoopList):
            if not self.loop_mode:
                self.loop_mode = True
                self.loop_size = len(condition)
                self.get_condition = self._get_condition_loop
                self.evaluate_loop(condition)
            return False
        return condition

    def _get_condition_loop(self, socket=None):
        condition = socket if socket else self.condition
        if isinstance(condition, ULLogicBase):
            return condition.get_value(self)[self.loop_idx]
        return socket
    
    def evaluate_loop(self, loop):    
        self.loop_idx = 0
        dones = LoopList()
        for condition in loop:
            if condition:
                self.evaluate()
                dones.append(self._done)
            self.loop_idx += 1
        self._done = dones


class ULConditionNode(ULLogicNode):

    def __init__(self):
        self.get_condition = self._get_condition
        super().__init__()

    def _get_condition(self, socket=None):
        condition = socket if socket else self.condition
        if isinstance(condition, ULLogicBase):
            condition = condition.get_value(self)
        if isinstance(condition, LoopList):
            if not self.loop_mode:
                self.loop_mode = True
                self.loop_size = len(condition)
            return condition[self.loop_idx]
        return condition

    def _get_condition_loop(self, socket=None):
        condition = socket if socket else self.condition
        if isinstance(condition, ULLogicBase):
            return condition.get_value(self)[self.loop_idx]
        return socket

    def reset(self):
        super().reset()
        self.get_condition = self._get_condition


class LogicNodeCustom(ULLogicNode):
    pass
