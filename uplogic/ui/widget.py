import gpu
from gpu_extras.batch import batch_for_shader

import math
from mathutils import Vector
import bpy
import uuid

try:
    from bge import render
    from uplogic.utils.math import rotate2d
except Exception:
    print('Not in game mode!')
    def rotate2d(origin, pivot, angle):
        angle = math.radians(angle)
        return Vector((
            ((origin[0] - pivot[0]) * math.cos(angle)) - ((origin[1] - pivot[1]) * math.sin(angle)) + pivot[0],
            ((origin[0] - pivot[0]) * math.sin(angle)) + ((origin[1] - pivot[1]) * math.cos(angle)) + pivot[1]
        ))


ALIGN_CENTER = 0
ALIGN_LEFT = 1
ALIGN_RIGHT = 2
ALIGN_BOTTOM = 3
ALIGN_TOP = 4


ALIGNMENTS = {
    'center': ALIGN_CENTER,
    'left': ALIGN_LEFT,
    'right': ALIGN_RIGHT,
    'bottom': ALIGN_BOTTOM,
    'top': ALIGN_TOP,
}


class Widget():
    '''The widget Base class. a Widget has all the basic logic about
    sizing and positioning, but has no visual representation.

    This class is intended to be used as a base for inheriting from
    for custom widgets.

    :param pos: Initial position of this widget in either pixels or factor.
    :param size: Initial size of this widget in either pixels or factor.
    :param bg_color: Color to draw in the area of the widget.
    :param relative: Whether to use pixels or factor for size or pos; example: `{'pos': True, 'size': True}`.
    :param halign: Horizontal alignment of the widget, can be (`left`, `center`, `right`).
    :param valign: Vertical alignment of the widget, can be (`bottom`, `center`, `top`).
    :param angle: Rotation in degrees of this widget around the pivot defined by the alignment.
    '''

    vertex_in: list[tuple[str, str]] = [
        ('VEC2', 'texCoord'),
        ('VEC3', "position")
    ]
    """Data for the vertex shader."""

    interfaces: list[tuple[str, str]] = [
        ('VEC3', "pos"),
        ('VEC2', "uv")
    ]
    """Interfaces are passed from the vertex shader to the fragment shader under the same name."""

    constants: list[tuple[str, str]] = [
        ('VEC2', "resolution"),
        ('VEC4', "color"),
        ('VEC4', "border_color"),
        ('FLOAT', "border_width")
    ]
    """Constant Data."""

    samplers: list[tuple[str, str]] = []
    """Constant Data."""

    vertex_shader: str = '''
        void main()
        {
            uv = texCoord;
            pos = position;
            gl_Position = ModelViewProjectionMatrix * vec4(position, 1.0f);
        }
    '''

    fragment_shader: str = '''
        void main()
        {
            float x_border = border_width / resolution.x;
            float y_border = border_width / resolution.y;
            if (uv.x < x_border || uv.x > 1-x_border || uv.y < y_border || uv.y > 1-y_border){
                FragColor = mix(color, border_color, border_color.a);
                return;
            }
            FragColor = color;
        }
    '''

    _is_canvas = False

    def __init__(self, pos=(0, 0), size=(0, 0), bg_color=(0, 0, 0, 0), relative={}, halign='left', valign='bottom', angle=0, show=True):
        self.id = uuid.uuid4()
        self._parent = None
        self._vertices = None  # (Vector((0, 0)), Vector((0, 0)), Vector((0, 0)), Vector((0, 0)))
        self._show = show
        self._show_effective = show
        self._opacity = 1.0
        self._opacity_effective = 1.0
        self._canvas = None
        self._pos = [0, 0]
        self._size = [0, 0]
        self._rebuild = True
        self._z = 0
        self._clipped = [0, 0]
        self._cached_draw_pos = None
        self._cached_draw_size = None
        self._active = True
        self._children: list[Widget] = []
        self._halign = ALIGNMENTS.get('left')
        self._valign = ALIGNMENTS.get('bottom')
        self.child_offset = [0, 0]
        self.border_color = (0, 0, 0, 0)
        self.border_width = 0

        self.halign = halign
        self.valign = valign
        self.relative = relative
        # self.size = size
        self._size = list(size)
        # self.pos = pos
        self._pos = list(pos)
        self.bg_color = bg_color
        self.angle = angle
        self._shader = None
        self._get_shader()
        self._build_shader()
        self.use_clipping = False
        self.copy_height = False
        self.copy_width = False

    @property
    def idx(self):
        """The index of this widget amongst its parent's children."""
        if self.parent:
            children = self.parent.children
            return children.index(self)
        return -1

    def move_up(self):
        if self.parent is not None:
            children = self.parent.children
            idx = children.index(self)
            if idx < len(children)-1:
                children[idx], children[idx + 1] = children[idx + 1], children[idx]

    def move_down(self):
        if self.parent is not None:
            children = self.parent.children
            idx = children.index(self)
            if idx > 0:
                children[idx], children[idx - 1] = children[idx - 1], children[idx]

    def move_to_top(self):
        if self.parent is not None:
            children = self.parent.children
            children.remove(self)
            children.append(self)

    def move_to_bottom(self):
        if self.parent is not None:
            children = self.parent.children
            children.remove(self)
            children.insert(0, self)

    def register(self):
        pass

    def toggle(self, *args):
        """Toggle the widget on/off."""
        self.show = not self.show

    def set_visible(self, flag=True):
        self.show = flag

    def set_invisible(self):
        self.show = False

    def make_floating(self, pos=True, size=True, halign='center', valign='center'):
        """Quickly set the attributes of this widget to use relative data.

        :param pos: Use relative position.
        :param size: Use relative size.
        :param halign: The horizontal alignment.
        :param valign: The vertical alignment.
        """
        self.relative['pos'] = pos
        self.relative['size'] = size
        self.halign = halign
        self.valign = valign
        return self

    @property
    def halign(self):
        return self._halign

    @halign.setter
    def halign(self, val):
        alignment = ALIGNMENTS.get(val, val)
        if alignment != self._halign:
            self._mark_for_rebuild()
        self._halign = alignment


    @property
    def valign(self):
        return self._valign

    @valign.setter
    def valign(self, val):
        alignment = ALIGNMENTS.get(val, val)
        if alignment != self._valign:
            self._mark_for_rebuild()
        self._valign = alignment

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
        """If `False`, this widget and its children will not be rendered."""
        return self._show

    @show.setter
    def show(self, val):
        if val != self._show:
            self._show = val
            self._cascade_inherited()
            self._mark_for_rebuild()

    @property
    def _children_reversed(self):
        return list(self.children.__reversed__())

    @property
    def canvas(self):
        """Find the canvas this widget is attached to."""
        return self._canvas

    @property
    def pivot(self):
        """Rotation point for this widget."""
        if self.parent is None:
            return Vector((0, 0))
        v = self._vertices
        if v is None:
            return Vector((0, 0))
        x0 = Vector(v[0])
        x1 = Vector(v[1])
        y1 = Vector(v[2])
        y0 = Vector(v[3])
        return Vector(self._get_pivot(x0, x1, y0, y1))

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
        if val != self._angle:
            self._mark_for_rebuild()
        self._angle = val

    @property
    def _recurse(self):
        widgets = [self]
        for w in self.children:
            widgets.extend(w._recurse)
        return widgets

    @property
    def childrenRecursive(self) -> list:  # noqa; for bge consistency reasons
        return self.children_recursive

    @property
    def children_recursive(self) -> list:
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
    def children_visible(self):
        """Immediate visible children of this widget."""
        return [c for c in self._children if c._show_effective]

    @property
    def bg_color(self):
        """Background color of this widget. Colors the whole area of the widget in a rectangular shape."""
        return self._bg_color

    @bg_color.setter
    def bg_color(self, val):
        val = list(val)
        self._bg_color = val

    @property
    def parent(self) -> 'Widget':
        """The widget whose position and size to use relatively."""
        return self._parent

    @parent.setter
    def parent(self, val):
        if self.parent is not val and self.parent:
            self.parent.remove_widget(self)
        if self.use_clipping is None:
            self.use_clipping = val.use_clipping
        self._parent = val
        self._update_inherited()
        self._mark_for_rebuild()
        self.pos = self.pos  # noqa
        self.size = self.size  # noqa
        for c in self.children:
            c.parent = c.parent  # noqa
        self.on_parent()

    @property
    def pos_pixel(self):
        """The absolute position of this widget from the bottom left corner of the screen in pixels."""
        if self._vertices is None:
            return [0, 0]
        pos = self._vertices[1]
        return [
            pos[0],# - self._clipped[0],
            pos[1] #- self._clipped[1]
        ]

    @property
    def pos_abs(self):
        """The absolute position of this widget from the bottom left corner of the screen in pixels."""
        return self.pos_pixel

    @property
    def pos(self):
        """Position of this widget relative to its parent in either pixels or factor."""
        return self._pos

    @pos.setter
    def pos(self, val):
        val = list(val)
        if self._pos == val:
            return
        self._pos = val
        self._mark_for_rebuild()
        if self._show_effective:
            self.on_pos()

    def on_pos(self):
        ...

    @property
    def x(self):
        """Horizontal position of this widget relative to its parent in either pixels or factor."""
        return self._pos[0]

    @x.setter
    def x(self, val):
        if val != self._pos[0]:
            self._mark_for_rebuild()
        self._pos = [val, self._pos[1]]

    @property
    def y(self):
        """Vertical position of this widget relative to its parent in either pixels or factor."""
        return self._pos[1]

    @y.setter
    def y(self, val):
        if val != self._pos[1]:
            self._mark_for_rebuild()
        self._pos = [self._pos[0], val]

    @property
    def size(self):
        """Size of this widget in either pixels or factor relative to its parent."""
        return self._size

    @size.setter
    def size(self, val):
        val = list(val)
        if self._size == val:
            return
        self._size = val
        self._mark_for_rebuild()
        if self._show_effective:
            self.on_size()

    def on_size(self):
        ...

    @property
    def width(self):
        """Horizontal size of this widget in either pixels or factor relative to its parent."""
        return self.size[0]

    @width.setter
    def width(self, val):
        self.size = [val, self.size[1]]

    @property
    def height(self):
        """Vertical size of this widget in either pixels or factor relative to its parent."""
        return self.size[1]

    @height.setter
    def height(self, val):
        self.size = [self.size[0], val]

    @property
    def size_pixel(self):
        if self._vertices is None:
            return [0, 0]
        bottom_left = self._vertices[1]
        top_right = self._vertices[2]
        return [top_right[0] - bottom_left[0], top_right[1] - bottom_left[1]]

    @property
    def width_pixel(self):
        return self.size_pixel[0]

    @property
    def height_pixel(self):
        return self.size_pixel[1]

    @property
    def clip(self):
        return self.use_clipping

    @clip.setter
    def clip(self, val):
        self.use_clipping = val

    @property
    def use_clipping(self):
        """Whether to draw outside of the parent's bounds."""
        return True if self.parent and self.parent.use_clipping else self._use_clipping

    @use_clipping.setter
    def use_clipping(self, val):
        self._mark_for_rebuild()
        self._use_clipping = val
        for widget in self.childrenRecursive:
            widget._use_clipping = val

    @property
    def opacity(self):
        """Opacity for this widget, but not its children."""
        return self._opacity

    @opacity.setter
    def opacity(self, val):
        if val != self._opacity:
            self._opacity = val
            self._cascade_inherited()
            self._mark_for_rebuild()

    @property
    def content_width(self):
        widths = []
        for c in self.children:
            if not c._show_effective:
                continue
            p = c._draw_pos[0]
            w = c._draw_size[0]
            widths.extend([p, p + w])
        return (max(widths) - min(widths)) if len(widths) else 0

    @property
    def content_height(self):
        heights = []
        for c in self.children:
            if not c._show_effective:
                continue
            p = c._draw_pos[1]
            h = c._draw_size[1]
            heights.extend([p, p + h])
        return (max(heights) - min(heights)) if len(heights) else 0

    @property
    def clipping(self):
        """Clipping boundaries. If clipping is enabled, don't draw outside of these boundaries."""
        pdpos = self.parent.pos_pixel
        pdsize = self.parent.size_pixel
        return [
            pdpos[0],
            pdpos[0] + pdsize[0],
            pdpos[1] + pdsize[1],
            pdpos[1]
        ]

    @property
    def next_widget(self):
        if self.parent is not None and self in self.parent.children_visible:
            idx = self.parent.children_visible.index(self)
            if idx == len(self.parent.children_visible) - 1:
                return None
            return self.parent.children_visible[idx + 1]
        return None

    @property
    def previous_widget(self):
        if self.parent is not None and self in self.parent.children_visible:
            idx = self.parent.children_visible.index(self)
            if idx == 0:
                return None
            return self.parent.children_visible[idx - 1]
        return None

    # @property
    # def _offset(self):
    #     return self.parent.child_offset

    @property
    def _draw_pos(self):
        if self._cached_draw_pos is not None:
            return self._cached_draw_pos
        if self.parent is None:
            return [0, 0]
        parent = self.parent
        inherit_pos = parent._draw_pos
        pdsize = parent._draw_size
        if self.relative.get('pos'):
            pos = [math.floor(self._pos[0] * pdsize[0]), math.floor(self._pos[1] * pdsize[1])]
        else:
            pos = list(self._pos)
        pos[0] += parent.child_offset[0]
        pos[1] += parent.child_offset[1]
        if parent._draw_angle and self._vertices is not None:
            pos = rotate2d(pos, parent.pivot - Vector(inherit_pos), parent._draw_angle)
        dsize = self._draw_size
        ox = dsize[0] * (.5 if self.halign == ALIGN_CENTER else 1 if self.halign == ALIGN_RIGHT else 0)
        oy = dsize[1] * (.5 if self.valign == ALIGN_CENTER else 1 if self.valign == ALIGN_TOP else 0)
        result = [pos[0] + inherit_pos[0] - ox, pos[1] + inherit_pos[1] - oy]
        self._cached_draw_pos = result
        return result

    @property
    def _draw_size(self):
        if self._cached_draw_size is not None:
            return self._cached_draw_size
        if self.parent is None:
            return self._size
        if self.relative.get('size'):
            pdsize = self.parent._draw_size
            size = [math.floor(self._size[0] * pdsize[0]), math.floor(self._size[1] * pdsize[1])]
        else:
            size = list(self._size)
        if self.copy_width:
            size[1] = size[0]
        elif self.copy_height:
            size[0] = size[1]
        self._cached_draw_size = size
        return size

    @property
    def dimensions(self):
        pos = self._draw_pos
        size = self._draw_size
        return [
            pos,
            Vector((pos[0] + size[0], pos[1] + size[1]))
        ]

    def refresh(self):
        self._build_shader()

    def check_inside(self, x, y):
        """Check if pixel position (x, y) is inside this widget's area.
        
        :param float x: Screen X position in pixels.
        :param float y: Screen Y position in pixels.
        """
        y = render.getWindowHeight() - y
        dpos = self.pos_pixel
        dsize = self.size_pixel
        return (
            dpos[0] < x < dpos[0] + dsize[0] and
            dpos[1] < y < dpos[1] + dsize[1]
        )

    def start(self):
        """Put your custom startup logic here.
        """
        pass

    def _get_pivot(self, x0, x1, y0, y1):
        halign = self.halign
        valign = self.valign
        if self.parent is None:
            return Vector((0, 0))
        if halign is valign is ALIGN_CENTER:
            return x0.lerp(y1, .5)
        elif halign is ALIGN_CENTER and valign is ALIGN_TOP:
            return y0.lerp(y1, .5)
        elif halign == ALIGN_CENTER and valign == ALIGN_BOTTOM:
            return x0.lerp(x1, .5)
        elif halign == ALIGN_LEFT and valign == ALIGN_BOTTOM:
            return x0
        elif halign == ALIGN_LEFT and valign == ALIGN_CENTER:
            return x0.lerp(y0, .5)
        elif halign == ALIGN_LEFT and valign == ALIGN_TOP:
            return y0
        elif halign == ALIGN_RIGHT and valign == ALIGN_BOTTOM:
            return x1
        elif halign == ALIGN_RIGHT and valign == ALIGN_CENTER:
            return x1.lerp(y1, .5)
        elif halign == ALIGN_RIGHT and valign == ALIGN_TOP:
            return y1
        return x0

    def _get_vertices(self, pos, size):
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
        vertices = [x1, x0, y1, y0]
        if self.parent and self.parent.use_clipping:
            clip = self.clipping
            for vert in vertices:
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
        return vertices

    def _mark_for_rebuild(self):
        self._rebuild = True
        self._cached_draw_pos = None
        self._cached_draw_size = None

    def _update_inherited(self):
        parent = self._parent
        if parent is None:
            self._canvas = None
            self._show_effective = self._show
            self._opacity_effective = self._opacity
        else:
            self._canvas = parent if parent._is_canvas else parent._canvas
            self._show_effective = self._show and parent._show_effective
            self._opacity_effective = self._opacity * parent._opacity_effective

    def _cascade_inherited(self):
        self._update_inherited()
        for c in self._children:
            c._cascade_inherited()

    def _build_shader(self, force=True):
        if self.parent is None:
            return
        self._cached_draw_pos = None
        self._cached_draw_size = None
        pos = self._draw_pos
        size = self._draw_size

        self._shader = self._get_shader()
        vertices = self._vertices = self._get_vertices(pos, size)
        self._set_uniforms()

        _line_vertices = [
            vertices[1], vertices[0], vertices[2], vertices[3], vertices[1]
        ]

        self._batch = batch_for_shader(self._shader, 'TRI_STRIP', {
            "position": vertices,
            "texCoord": (
                (1, 0),
                (0, 0),
                (1, 1),
                (0, 1)
            )
        })

    def _set_uniforms(self):
        bg_color = self.bg_color.copy()
        border_color = self.border_color.copy()
        bg_color[3] *= self._opacity_effective
        border_color[3] *= self._opacity_effective
        self._shader.uniform_float("resolution", (self.width_pixel, self.height_pixel))
        self._shader.uniform_float("border_color", border_color)
        self._shader.uniform_float("border_width", int(self.border_width))
        self._shader.uniform_float("color", bg_color)

    def _get_shader(self):
        if self._shader is None:
            shader_info = gpu.types.GPUShaderCreateInfo()

            for i, vertex_in in enumerate(self.vertex_in):
                shader_info.vertex_in(i, vertex_in[0], vertex_in[1])

            for i, interface in enumerate(self.interfaces):
                vert_out = gpu.types.GPUStageInterfaceInfo(f'{interface[1]}_interface')
                vert_out.smooth(interface[0], interface[1])
                shader_info.vertex_out(vert_out)

            for constant in self.constants:
                shader_info.push_constant(constant[0], constant[1])

            for i, sampler in enumerate(self.samplers):
                shader_info.sampler(i, sampler[0], sampler[1])

            shader_info.push_constant('MAT4', "ModelViewProjectionMatrix")
            shader_info.fragment_out(0, 'VEC4', "FragColor")

            shader_info.vertex_source(self.vertex_shader)
            shader_info.fragment_source(self.fragment_shader)

            shader = gpu.shader.create_from_info(shader_info)

            matrix = gpu.matrix.get_projection_matrix()
            shader.uniform_float("ModelViewProjectionMatrix", matrix)
            return shader
        return self._shader

    def _setup_draw(self):
        if self._rebuild:
            self._rebuild_tree()
        self._rebuild = False

    def _rebuild_tree(self):
        if self.parent:
            self._build_shader()
            for c in self.children:
                c._rebuild = False
                c._rebuild_tree()

    @property
    def _render_needed(self):
        return self._show_effective and (self.height_pixel > 0 or self.width_pixel > 0)

    def draw(self):
        """This is called each frame if the widget is part of a canvas. It can be called manually,
        but it will result in a higher logic load.
        """
        gpu.state.blend_set('ALPHA')
        self.canvas._to_evaluate.append(self)
        for widget in self.children:
            if widget._show_effective:
                widget.draw()

    def evaluate(self):
        """Logic evaluation
        """
        ...

    def update(self):
        """Put your custom update logic here.
        """
        ...

    def add_widget(self, widget):
        '''Add a `Widget` to this widget as child.

        :param widget `Widget` to add.
        '''
        if widget not in self.children:
            widget.parent = self
            self.children.append(widget)
            if self.canvas is not None:
                self.canvas._set_z(-1)
        self.children = sorted(self.children, key=lambda widget: widget._z, reverse=False)
        return widget

    def sort_children(self, key=lambda widget: widget._z, reverse=False):
        self.children.sort(key=key, reverse=reverse)
        self._set_z(self._z - 1)

    def add_widgets(self, *widgets):
        for w in widgets:
            self.add_widget(w)

    def on_parent(self):
        ...

    def _set_z(self, _z):
        _z += 1
        self._z = _z
        for c in self.children:
            _z = c._set_z(_z)
        return _z

    def remove_widget(self, widget):
        '''Remove a `Widget` from this widget.

        :param widget: `Widget` to remove.
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
