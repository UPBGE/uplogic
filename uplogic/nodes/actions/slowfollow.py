from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import is_waiting
from uplogic.utils import not_met
from uplogic.utils import debug
from uplogic.utils import interpolate


class ULSlowFollow(ULActionNode):
    def __init__(self, value_type='worldPosition'):
        ULActionNode.__init__(self)
        self.value_type = str(value_type)
        self.condition = NotImplementedError
        self.game_object = None
        self.target = None
        self.factor = None
        self.done = None
        self.OUT = ULOutSocket(self, self.get_done)

    def get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        condition = self.get_input(self.condition)
        if not_met(condition):
            return
        game_object = self.get_input(self.game_object)
        target = self.get_input(self.target)
        attribute = self.get_input(self.value_type)
        factor = self.get_input(self.factor)
        if is_waiting(game_object, target, attribute, factor):
            return
        data = getattr(game_object, attribute)
        t_data = getattr(target, attribute)
        setattr(
            game_object,
            attribute,
            data.lerp(t_data, factor)
        )
        if attribute == 'worldScale':
            game_object.reinstancePhysicsMesh(
                game_object,
                game_object.meshes[0]
            )
        self.done = True
