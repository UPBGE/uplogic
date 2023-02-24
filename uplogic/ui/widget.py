import gpu
from gpu_extras.batch import batch_for_shader
from bge import render


class Widget():
    '''TODO: Documentation
    '''
    def __init__(self, pos=(0, 0), size=(0, 0), color=(0, 0, 0, 0), relative={}):
        self._parent = None
        self._pos = [0, 0]
        self._children: list[Widget] = []
        self._children_reversed: list[Widget] = self.children.__reversed__()
        self.relative = relative
        self.size = size
        self.pos = pos
        self.color = color
        self.vertices = ((0, 0), (0, 0), (0, 0), (0, 0))
        self.show = True
        self.z = 0
        self.start()

    @property
    def window(self):
        pa = self
        while pa.parent is not None:
            pa = pa.parent
        return pa

    @property
    def _recurse(self):
        widgets = [self]
        for w in self.children:
            widgets.extend(w._recurse)
        return widgets

    @property
    def childrenRecursive(self):
        widgets = []
        for w in self.children:
            widgets.extend(w._recurse)
        return widgets

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
        for child in self.children:
            child.pos = child.pos

    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, val):
        self._size = list(val)
        self.build_shader()

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
    def opacity(self):
        return self.color[3]

    @opacity.setter
    def opacity(self, val):
        self.color[3] = val

    @property
    def child_offset(self):
        return [0, 0]

    @property
    def _draw_pos(self):
        inherit_pos = self.parent.pos_abs if self.parent else [0, 0]
        pos = [
            self.pos[0] * render.getWindowWidth(),
            self.pos[1] * render.getWindowHeight(),
        ] if self.relative.get('pos') else self.pos
        return [pos[0] + inherit_pos[0], pos[1] + inherit_pos[1]]

    @property
    def _draw_size(self):
        return [
            self.size[0] * render.getWindowWidth(),
            self.size[1] * render.getWindowHeight(),
        ] if self.relative.get('size') else self.size

    def start(self):
        pass

    def build_shader(self):
        pos = self._draw_pos
        size = self._draw_size
        vertices = self.vertices = (
            (pos[0], pos[1]),
            (pos[0] + size[0], pos[1]),
            (pos[0] + size[0], pos[1] + size[1]),
            (pos[0], pos[1] + size[1])
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
            self.window._to_evaluate.append(self)
            for widget in self.children:
                widget.draw()

    def update(self):
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
