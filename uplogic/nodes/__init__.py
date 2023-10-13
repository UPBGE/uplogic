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


class ULLogicBase(object):
    def get_value(self): pass


class ULLogicContainer(ULLogicBase):

    def __init__(self):
        self._uid = None
        self._value = None
        self._children = []
        self.network = None

    def get_value(self):
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


class ULOutSocket(ULLogicBase):

    def __init__(self, node, value_getter):
        self.node = node
        # self.get_value
        self._value_getter = value_getter

    def _value_getter(self):
        pass
    
    def get_value(self):
        result = self.node.outputs.get(self, None)
        if result is None:
            result = self._value_getter()
            self.node.outputs[self] = result
        return result


###############################################################################
# Basic Cells
###############################################################################


class ULLogicNode(ULLogicContainer):

    def __init__(self):
        super().__init__()
        self.outputs = {}
        self.output_values = {}

    def reset(self):
        super().reset()
        self.outputs = {}
        self.output_values = {}  # XXX: Remove

    def set_output(self, socket, value):
        self.output_values[socket] = value
        return value

    def get_output(self, socket, default=None):
        return self.output_values.get(socket, default)

    def get_input(self, param):
        if isinstance(param, ULLogicBase):
            return param.get_value()
        else:
            return param

    def evaluate(self):
        pass


class ULParameterNode(ULLogicNode):
    pass


class ULActionNode(ULLogicNode):
    pass


class ULConditionNode(ULLogicNode):
    pass
