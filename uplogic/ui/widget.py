import gpu
from gpu_extras.batch import batch_for_shader
from uplogic.utils.math import rotate2d
from mathutils import Vector
from bge import render
from bge import render


class Widget():
    '''The widget Base class. a Widget has all the basic logic about
    sizing and positioning, but has no visual representation.

    This class is intended to be used as a base for inheriting from
    for custom widgets.

    :param `pos`: Initial position of this widget in either pixels or factor.
    :param `size`: Initial size of this widget in either pixels or factor.
    :param `bg_color`: Color to draw in the area of the widget.
    :param `relative`: Whether to use pixels or factor for size or pos; example: `{'pos': True, 'size': True}`.
    :param `halign`: Horizontal alignment of the widget, can be (`left`, `center`, `right`).
    :param `valign`: Vertical alignment of the widget, can be (`bottom`, `center`, `top`).
    :param `angle`: Rotation in degrees of this widget around the pivot defined by the alignment.
    '''

    vertex_code = """
    uniform mat4 ModelViewProjectionMatrix;
    in vec2 pos;
    out vec2 pxpos;

    void main()
    {
        vec4 vertex_pos = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);

        pxpos = (vec2(vertex_pos[0], vertex_pos[1]) + vec2(1, 1)) * .5;

        gl_Position = vertex_pos;
    }
    """

    fragment_code = """
    uniform vec4 color;
    uniform vec2 size;
    uniform vec2 pos;
    uniform vec2 screen;

    // Pixel Position from 0-1 in x, y
    in vec2 pxpos;

    out vec4 fragColor;

    void main()
    {
        vec2 screen_pos = pxpos * screen;

        float x = screen_pos[0];
        float y = screen_pos[1];

        if (
            pos[0] <= x &&
            x <= pos[0] + size[0] &&
            pos[1] <= y &&
            y <= pos[1] + size[1]
        ){
            fragColor = color;  // Pixel inside widget
        } else {
            fragColor = vec4(0, 0, 0, 0); //XXX: Use drawbuffer instead?
        }

        gl_FragDepth = 1.0;
    }
    """


    vertex_code = """
    uniform mat4 ModelViewProjectionMatrix;
    in vec2 pos;
    out vec2 pxpos;

    void main()
    {
        vec4 vertex_pos = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);

        pxpos = (vec2(vertex_pos[0], vertex_pos[1]) + vec2(1, 1)) * .5;

        gl_Position = vertex_pos;
    }
    """

    fragment_code = """
    uniform vec4 color;
    uniform vec2 size;
    uniform vec2 pos;
    uniform vec2 screen;

    // Pixel Position from 0-1 in x, y
    in vec2 pxpos;

    out vec4 fragColor;

    void main()
    {
        vec2 screen_pos = pxpos * screen;

        float x = screen_pos[0];
        float y = screen_pos[1];

        if (
            pos[0] <= x &&
            x <= pos[0] + size[0] &&
            pos[1] <= y &&
            y <= pos[1] + size[1]
        ){
            fragColor = color;  // Pixel inside widget
        } else {
            fragColor = vec4(0, 0, 0, 0); //XXX: Use drawbuffer instead?
        }

        gl_FragDepth = 1.0;
    }
    """

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
        self._vertices = None
        self._vertices = None
        self.angle = angle
        self._build_shader()
        self._clipped = [0, 0]
        self.use_clipping = False
        self.copy_height = False
        self.copy_width = False
        self.opacity = 1
        self.z = 0
        self._active = True
        self.start()

    def toggle(self, *args):
        """Toggle the widget on/off."""
        self.show = not self.show

    def set_visible(self, flag=True):
        self.show = flag

    def set_invisible(self):
        self.show = False

    def make_floating(self, pos=True, size=True, halign='center', valign='center'):
        """Quickly set the attributes of this widget to use relative data.

        :param `pos`: Use relative position.
        :param `size`: Use relative size.
        :param `halign`: The horizontal alignment.
        :param `valign`: The vertical alignment.
        """
        self.relative['pos'] = pos
        self.relative['size'] = size
        self.halign = halign
        self.valign = valign
        return self

    @property
    def active(self):
        parent = self
        while parent is not None:
            if not parent._active:
                return False
            parent = parent.parent
        return True

    @active.setter
    def active(self, val):
        self._active = val

    @property
    def show(self):
        """If `False`, this widget and all its children will not be rendered."""
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
        """Find the canvas this widget is attached to."""
        pa = self
        while pa.parent is not None:
            pa = pa.parent
        return pa

    @property
    def pivot(self):
        """Rotation point for this widget."""
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
        """The angle this widget is rotated by."""
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
        """All children and children's children of this widget."""
        widgets = []
        for w in self.children:
            widgets.extend(w._recurse)
        return widgets

    @property
    def children(self):
        """Immediate children of this widget."""
        return self._children

    @children.setter
    def children(self, val):
        self._children = val

    @property
    def bg_color(self):
        """Background color of this widget. Colors the whole area of the widget in a rectangular shape."""
        return self._bg_color

    @bg_color.setter
    def bg_color(self, val):
        val = list(val)
        self._bg_color = val

    @property
    def parent(self):
        """The widget whose position and size to use relatively."""
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
        for c in self.children:
            c.parent = c.parent
        self._build_shader()

    @property
    def pos_abs(self):
        """The absolute position of this widget from the bottom left corner of the screen in pixels."""
        if self._vertices is None:
            return [0, 0]
        pos = self._vertices[0]
        return [
            pos[0] - self._clipped[0],
            pos[1] - self._clipped[1]
        ]

    @property
    def pos(self):
        """Position of this widget relative to its parent in either pixels or factor."""
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
    def x(self):
        """Horizontal position of this widget relative to its parent in either pixels or factor."""
        return self._pos[0]

    @x.setter
    def x(self, val):
        self._pos = [val, self.pos[1]]
        if not self.show:
            return
        if self.parent and self.show:
            self._rebuild = True
        for child in self.children:
            child.pos = child.pos

    @property
    def y(self):
        """Vertical position of this widget relative to its parent in either pixels or factor."""
        return self._pos[1]

    @y.setter
    def y(self, val):
        self._pos = [self._pos[0], val]
        if not self.show:
            return
        if self.parent and self.show:
            self._rebuild = True
        for child in self.children:
            child.pos = child.pos

    @property
    def size(self):
        """Size of this widget in either pixels or factor relative to its parent."""
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
            child.size = child.size

    @property
    def use_clipping(self):
        """Whether to draw outside of the parent's bounds."""
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
        """Horizontal size of this widget in either pixels or factor relative to its parent."""
        return self.size[0]

    @width.setter
    def width(self, val):
        self.size[0] = val
        if self.parent and self.show:
            self._rebuild = True

    @property
    def height(self):
        """Vertical size of this widget in either pixels or factor relative to its parent."""
        return self.size[1]

    @height.setter
    def height(self, val):
        self.size[1] = val
        if self.parent and self.show:
            self._rebuild = True

    @property
    def opacity(self):
        """Opacity for this widget, but not its children."""
        op = self._opacity
        if self.parent:
            op *= self.parent.opacity
        self._rebuild = True
        return op

    @opacity.setter
    def opacity(self, val):
        self._opacity = val
        if self.parent and self.show:
            self._rebuild = True

    @property
    def child_offset(self):
        return [0, 0]

    @property
    def clipping(self):
        """Clipping boundaries. If clipping is enabled, don't draw outside of these boundaries."""
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
        inherit_pos = self.parent._draw_pos if self.parent else [0, 0]
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
        size = self.size
        if self.parent is None:
            return self.size
        if self.relative.get('size'):
            pdsize = self.parent._draw_size
            x_size = self.size[0] * pdsize[0]
            y_size = self.size[1] * pdsize[1]
            size = [x_size, y_size]
        if self.copy_width:
            size[1] = size[0]
        elif self.copy_height:
            size[0] = size[1]
        return size

    def start(self):
        """Put your custom startup logic here.
        """
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

    def _build_shader(self):
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
            Vector(y0),
            Vector(x0)
        )
        indices = (
            (0, 1, 2), (2, 3, 0)
        )
        vertex_points = (
            Vector((0, 0)),
            Vector((render.getWindowWidth(), 0)),
            Vector((render.getWindowWidth(), render.getWindowHeight())),
            Vector((0, render.getWindowHeight())),
            Vector((0, 0))
        )
        self.shader = gpu.types.GPUShader(self.vertex_code, self.fragment_code)
        self._batch = batch_for_shader(self.shader, 'TRIS', {"pos": vertex_points}, indices=indices)
        vertex_points = (
            Vector((0, 0)),
            Vector((render.getWindowWidth(), 0)),
            Vector((render.getWindowWidth(), render.getWindowHeight())),
            Vector((0, render.getWindowHeight())),
            Vector((0, 0))
        )
        self.shader = gpu.types.GPUShader(self.vertex_code, self.fragment_code)
        self._batch = batch_for_shader(self.shader, 'TRIS', {"pos": vertex_points}, indices=indices)

    def _setup_draw(self):
        if self._rebuild is True:
            self._build_shader()
            self._rebuild = False
        self.set_uniforms()
        self.set_uniforms()

    def _rebuild_tree(self):
        self._build_shader()
        for c in self.children:
            c._rebuild_tree()

    def set_uniforms(self):
        """Assign values for uniforms used by this widget's shader code.
        
        Default:
        - `color`: widget color in RGBA (0-1)
        - `pos`: widget position in pixels
        - `size`: widget size in pixels
        - `screen`: screen size in pixels
        """
        col = self.bg_color.copy()
        col[3] *= self.opacity
        self.shader.uniform_float("color", col)
        self.shader.uniform_float("pos", self._draw_pos)
        self.shader.uniform_float("size", self._draw_size)
        self.shader.uniform_float("screen", Vector((
            render.getWindowWidth(), render.getWindowHeight()
        )))

    def set_uniforms(self):
        """Assign values for uniforms used by this widget's shader code.
        
        Default:
        - `color`: widget color in RGBA (0-1)
        - `pos`: widget position in pixels
        - `size`: widget size in pixels
        - `screen`: screen size in pixels
        """
        col = self.bg_color.copy()
        col[3] *= self.opacity
        self.shader.uniform_float("color", col)
        self.shader.uniform_float("pos", self._draw_pos)
        self.shader.uniform_float("size", self._draw_size)
        self.shader.uniform_float("screen", Vector((
            render.getWindowWidth(), render.getWindowHeight()
        )))

    def draw(self):
        """This function is called each frame if the widget is part of a canvas. It can be called manually,
        """
        gpu.state.blend_set('ALPHA')
        self.canvas._to_evaluate.append(self)
        for widget in self.children:
            if widget.show:
                widget.draw()

    def evaluate(self):
        pass

    def update(self):
        """Put your custom update logic here.
        """
        pass

    def add_widget(self, widget):
        '''Add a `Widget` to this widget as child.

        :param `widget`: `Widget` to add.
        '''
        if widget not in self.children:
            widget.parent = self
            self.children.append(widget)
            self.canvas._set_z(-1)
        self.children = sorted(self.children, key=lambda widget: widget.z, reverse=False)
        return widget

    def _set_z(self, z):
        z += 1
        self.z = z
        for c in self.children:
            z = c._set_z(z)
        return z

    def remove_widget(self, widget):
        '''Remove a `Widget` from this widget.

        :param `widget`: `Widget` to remove.
        :param `widget`: `Widget` to remove.
        '''
        if widget in self.children:
            self.children.remove(widget)
            widget.parent = None

    def remove(self):
        if self.parent:
            self.parent.remove_widget(self)

    def clear(self):
        """Remove all widgets from this widget."""
        to_remove = self.children.copy()
        for child in to_remove:
            self.remove_widget(child)
