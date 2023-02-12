import gpu
from gpu_extras.batch import batch_for_shader


class Widget():
    '''TODO: Documentation
    '''
    def __init__(self, pos=(0, 0), size=(0, 0)):
        self.size = size
        self._children: list[Widget] = []
        self._children_reversed: list[Widget] = self.children.__reversed__()
        self.vertices = ((0, 0), (0, 0), (0, 0), (0, 0))
        self.show = True
        self.z = 0
        self._pos = [0, 0]
        self._parent = None
        self.pos = pos
        self.start()

    @property
    def system(self):
        pa = self
        while pa.parent is not None:
            pa = pa.parent
        return pa

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, val):
        self._children = val
        self._children_reversed = val.__reversed__()

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, val):
        self._parent = val
        print(self.z)
        self.pos = self.pos

    @property
    def pos_abs(self):
        return self.vertices[0]

    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, val):
        self._pos = list(val)
        self.build_shader()
        for widget in self.children:
            widget.pos = widget.pos

    @property
    def width(self):
        return self.size[0]

    @width.setter
    def width(self, val):
        self.size[0] = val

    @property
    def height(self):
        return self.size[1]

    @height.setter
    def height(self, val):
        self.size[1] = val

    @property
    def child_offset(self):
        return [0, 0]

    @property
    def _draw_pos(self):
        inherit_pos = self.parent.pos_abs if self.parent else [0, 0]
        return [self.pos[0] + inherit_pos[0], self.pos[1] + inherit_pos[1]]

    def start(self):
        pass

    def build_shader(self):
        pos = self._draw_pos
        vertices = self.vertices = (
            (pos[0], pos[1]),
            (pos[0] + self.size[0], pos[1]),
            (pos[0] + self.size[0], pos[1] + self.size[1]),
            (pos[0], pos[1] + self.size[1])
        )
        indices = (
            (0, 1, 2), (2, 3, 0)
        )
        self.shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        self.batch = batch_for_shader(self.shader, 'TRIS', {"pos": vertices}, indices=indices)
        self.batch_line = batch_for_shader(self.shader, 'LINE_LOOP', {"pos": vertices})
        self.batch_points = batch_for_shader(self.shader, 'POINTS', {"pos": vertices})

    def draw(self):
        """This is called each frame.
        """
        if self.show:
            self.system._to_evaluate.append(self)
            for widget in self.children:
                widget.draw()

    def evaluate(self):
        pass

    def add_widget(self, widget):
        '''Add a `Widget`.

        :param `action`: `Widget` to add.
        '''
        if widget not in self.children and widget.parent is None:
            self.children.append(widget)
            widget.z = self.z + len(self.children)
            widget.parent = self
        self.children = sorted(self.children, key=lambda widget: widget.z, reverse=False)

    def remove_widget(self, widget):
        '''Remove a `Widget`.

        :param `action`: `Widget` which to remove.
        '''
        if widget in self.children:
            self.children.remove(widget)
            widget.parent = None
