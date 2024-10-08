from uplogic.nodes import ULActionNode
import bpy


class ULRunPython(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.module_name = None
        self.module_func = None
        self.mode = 1
        self.arg = None
        self.val = None
        self.OUT = self.add_output(self.get_done)
        self.VAL = self.add_output(self.get_val)
        self._old_mod_name = None
        self._code_as_str = ''
        self._old_mod_fun = None
        self._module = None
        self._modfun = None

    def get_done(self):
        return self._done

    def get_val(self):
        return self.val

    def evaluate(self):
        if not self.get_condition():
            return
        text = self.get_input(self.module_name)
        mfun = self.get_input(self.module_func)
        mname = text.name
        if self.mode:
            mname = mname.split('.')[0]
            if mname and (self._old_mod_name != mname):
                exec("import {}".format(mname))
                self._old_mod_name = mname
                self._module = eval(mname)
            if self._old_mod_fun != mfun:
                self._modfun = getattr(self._module, mfun)
                self._old_mod_fun = mfun
            args = [
                self.get_input(arg)
                for arg in self.arg
            ]
            if args:
                self.val = self._modfun(*args)
            else:
                self.val = self._modfun()
        else:
            if self._old_mod_name != mname:
                self._old_mod_name = mname
                self._code_as_str = compile(bpy.data.texts[mname].as_string(), 'custom', 'exec')
            exec(self._code_as_str, globals())
        self._done = True
