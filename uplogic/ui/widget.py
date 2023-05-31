import gpu
from gpu_extras.batch import batch_for_shader
from bge import render
from uplogic.utils.math import rotate2d, lerp
from mathutils import Vector


class Widget():
    '''TODO: Documentation
    '''
    def __init__(self, pos=(0, 0), size=(0, 0), bg_color=(0, 0, 0, 0), relative={}, halign='left', valign='bottom', angle=0):
        self.halign = halign
        self.valign = valign
        self._parent = None
        self._show = True
        self._pos = [0, 0]
        self._children: list[Widget] = []
        self.relative = relative
        self._rebuild = True 
        self.size = size
        self.pos = pos
        self.bg_color = bg_color
        self._vertices = None # (Vector((0, 0)), Vector((0, 0)), Vector((0, 0)), Vector((0, 0)))
        self.angle = angle
        self.build_shader()
        self._clipped = [0, 0]
        self.use_clipping = False
        self.z = 0
        self.start()

    def toggle(self, *args):
        self.show = not self.show

    @property
    def show(self):
        return self._show

    @show.setter
    def show(self, val):
        if val != self._show:
            self._show = val
            if val:
                self._rebuild = True
                for child in self.children:
                    child.pos = child.pos

    @property
    def _children_reversed(self):
        return self.children.__reversed__()

    @property
    def canvas(self):
        pa = self
        while pa.parent is not None:
            pa = pa.parent
        return pa

    @property
    def pivot(self):
        if self.parent is None:
            return (0, 0)
        v = self._vertices
        x0 = Vector(v[0])
        x1 = Vector(v[1])
        y1 = Vector(v[2])
        y0 = Vector(v[3])
        return self._get_pivot(x0, x1, y0, y1)

    @property
    def _draw_angle(self):
        if self.parent:
            return self._angle + self.parent._draw_angle
        return self._angle

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, val):
        self._angle = val
        if self.parent:
            self._rebuild_tree()

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

    @property
    def bg_color(self):
        return self._bg_color

    @bg_color.setter
    def bg_color(self, val):
        val = list(val)
        self._bg_color = val

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, val):
        if self.parent is not val and self.parent:
            self.parent.remove_widget(self)
        if self.use_clipping is None:
            self.use_clipping = val.use_clipping
        self._parent = val
        self.pos = self.pos
        self.size = self.size
        self.build_shader()

    @property
    def pos_abs(self):
        if self._vertices is None:
            return [0, 0]
        pos = self._vertices[0]
        return [
            pos[0] - self._clipped[0],
            pos[1] - self._clipped[1]
        ]

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, val):
        self._pos = list(val)
        if not self.show:
            return
        if self.parent and self.show:
            self._rebuild = True
        for child in self.children:
            child.pos = child.pos

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, val):
        self._size = list(val)
        if not self.show:
            return
        if self.parent and self.show:
            self._rebuild = True
        for child in self.children:
            child.pos = child.pos

    @property
    def use_clipping(self):
        return self._use_clipping

    @use_clipping.setter
    def use_clipping(self, val):
        self._use_clipping = val
        for widget in self.childrenRecursive:
            widget._use_clipping = val
        if self.parent and self.show:
            self._rebuild = True

    @property
    def width(self):
        return self.size[0]

    @width.setter
    def width(self, val):
        self.size[0] = val
        if self.parent and self.show:
            self._rebuild = True

    @property
    def height(self):
        return self.size[1]

    @height.setter
    def height(self, val):
        self.size[1] = val
        if self.parent and self.show:
            self._rebuild = True

    @property
    def opacity(self):
        return self.bg_color[3]

    @opacity.setter
    def opacity(self, val):
        self.bg_color[3] = val
        if self.parent and self.show:
            self._rebuild = True

    @property
    def child_offset(self):
        return [0, 0]

    @property
    def clipping(self):
        pdpos = self.parent._draw_pos
        pdsize = self.parent._draw_size
        return [
            pdpos[0],
            pdpos[0] + pdsize[0],
            pdpos[1] + pdsize[1],
            pdpos[1]
        ]

    @property
    def _draw_pos(self):
        if self.parent is None:
            return [0, 0]
        inherit_pos = self.parent.pos_abs if self.parent else [0, 0]
        pdsize = self.parent._draw_size
        pos = [
            self.pos[0] * pdsize[0],
            self.pos[1] * pdsize[1]
        ] if self.relative.get('pos') else self.pos
        if self.parent and self.parent._draw_angle and self._vertices is not None:
            pos = rotate2d(pos, (0, 0), self.parent._draw_angle)
        offset = [0, 0]
        dsize = self._draw_size
        if self.halign == 'center':
            offset[0] += dsize[0] * .5
        elif self.halign == 'right':
            offset[0] += dsize[0]
        if self.valign == 'center':
            offset[1] += dsize[1] * .5
        elif self.valign == 'top':
            offset[1] += dsize[1]
        pos = [pos[0] + inherit_pos[0] - offset[0], pos[1] + inherit_pos[1] - offset[1]]
        return pos

    @property
    def _draw_size(self):
        if self.parent is None:
            return self.size
        if self.relative.get('size'):
            return [
                self.size[0] * self.parent._draw_size[0],
                self.size[1] * self.parent._draw_size[1]
            ]
        return self.size

    def start(self):
        pass

    def _get_pivot(self, x0, x1, y0, y1):
        halign = self.halign
        valign = self.valign
        if self.parent is None:
            return (0, 0)
        if halign == 'center' and valign == 'center':
            return x0.lerp(y1, .5)
        elif halign == 'left' and valign == 'bottom':
            return x0
        elif halign == 'center' and valign == 'top':
            return y0.lerp(y1, .5)
        elif halign == 'center' and valign == 'bottom':
            return x0.lerp(x1, .5)
        elif halign == 'left' and valign == 'center':
            return x0.lerp(y0, .5)
        elif halign == 'left' and valign == 'top':
            return y0
        elif halign == 'right' and valign == 'bottom':
            return x1
        elif halign == 'right' and valign == 'center':
            return x1.lerp(y1, .5)
        elif halign == 'right' and valign == 'top':
            return y1
        return x0


    def build_shader(self):
        if self.parent is None:
            return
        pos = self._draw_pos
        size = self._draw_size
        x0 = Vector([pos[0], pos[1]])
        x1 = Vector([pos[0] + size[0], pos[1]])
        y0 = Vector([pos[0], pos[1] + size[1]])
        y1 = Vector([pos[0] + size[0], pos[1] + size[1]])
        pivot = self._get_pivot(x0, x1, y0, y1)
        if self._draw_angle and self._vertices is not None:
            x0 = rotate2d(x0, pivot, self._draw_angle)
            x1 = rotate2d(x1, pivot, self._draw_angle)
            y0 = rotate2d(y0, pivot, self._draw_angle)
            y1 = rotate2d(y1, pivot, self._draw_angle)
        v = [x0, x1, y0, y1]
        if self.parent.use_clipping:
            clip = self.clipping
            for vert in v:
                if vert[0] < clip[0]:
                    self._clipped[0] = clip[0] - vert[0]
                    vert[0] = clip[0]
                elif vert[0] > clip[1]:
                    vert[0] = clip[1]
                if vert[1] < clip[3]:
                    self._clipped[1] = clip[3] - vert[1]
                    vert[1] = clip[3]
                elif vert[1] > clip[2]:
                    vert[1] = clip[2]
        vertices = self._vertices = (
            Vector(x0),
            Vector(x1),
            Vector(y1),
            Vector(y0)
        )
        indices = (
            (0, 1, 2), (2, 3, 0)
        )
        self._shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        self._batch = batch_for_shader(self._shader, 'TRIS', {"pos": vertices}, indices=indices)
        self._batch_line = batch_for_shader(self._shader, 'LINE_LOOP', {"pos": vertices})
        self._batch_points = batch_for_shader(self._shader, 'POINTS', {"pos": vertices})

    def _setup_draw(self):
        if self._rebuild is True:
            self.build_shader()
            self._rebuild = False

    def _rebuild_tree(self):
        self.build_shader()
        for c in self.children:
            c._rebuild_tree()

    def draw(self):
        """This is called each frame.
        """
        gpu.state.blend_set('ALPHA')
        self.canvas._to_evaluate.append(self)
        for widget in self.children:
            if widget.show:
                widget.draw()

    def update(self):
        pass

    def add_widget(self, widget):
        '''Add a `Widget`.

        :param `action`: `Widget` to add.
        '''
        if widget not in self.children:
            self.children.append(widget)
            self.canvas.set_z(-1)
            widget.parent = self
        self.children = sorted(self.children, key=lambda widget: widget.z, reverse=False)

    def set_z(self, z):
        z += 1
        self.z = z
        for c in self.children:
            z = c.set_z(z)
        return z

    def remove_widget(self, widget):
        '''Remove a `Widget`.

        :param `action`: `Widget` which to remove.
        '''
        if widget in self.children:
            self.children.remove(widget)
            widget.parent = None

    def clear(self):
        to_remove = self.children.copy()
        for child in to_remove:
            self.remove_widget(child)
