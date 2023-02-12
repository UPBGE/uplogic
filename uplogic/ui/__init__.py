from .widget import Widget
import gpu
import bge


class UI(Widget):

    def __init__(self, pos=(0, 0), size=(100, 100)):
        super().__init__(pos, size)
        self.mouse_consumed = False
        self._to_evaluate = []
        # bge.logic.getCurrentScene().post_draw.append(self.evaluate)
        bge.logic.getCurrentScene().post_draw.append(self.draw)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, val):
        self._parent = val
        self.pos = self.pos
    
    def draw(self):
        gpu.state.blend_set('ALPHA')
        super().draw()
        self.mouse_consumed = False
        while self._to_evaluate:
            self._to_evaluate.pop().evaluate()

    def evaluate(self):
        super().evaluate()
