'''Base widget class and alignment constants for the uplogic UI system.'''

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
'''Centre alignment (horizontal or vertical).'''

ALIGN_LEFT = 1
'''Left horizontal alignment.'''

ALIGN_RIGHT = 2
'''Right horizontal alignment.'''

ALIGN_BOTTOM = 3
'''Bottom vertical alignment.'''

ALIGN_TOP = 4
'''Top vertical alignment.'''


ALIGNMENTS = {
    'center': ALIGN_CENTER,
    'left': ALIGN_LEFT,
    'right': ALIGN_RIGHT,
    'bottom': ALIGN_BOTTOM,
    'top': ALIGN_TOP,
}
'''Mapping from alignment name strings to their integer constants.'''


class Widget():
    '''Base class for all uplogic UI elements.

    Handles sizing, positioning, alignment, rotation, opacity, clipping, and
    the GPU shader lifecycle.  Has no visual representation on its own; subclass
    it to draw something or use one of the built-in subclasses.

    :param pos: Position in pixels or factor relative to the parent.
    :param size: Size ``[width, height]`` in pixels or factor.
    :param bg_color: RGBA background fill colour.
    :param relative: Dict controlling coordinate interpretation.  Supported
        keys: ``'pos'`` and ``'size'`` (``True`` = factor of parent size,
        ``False`` = pixels); ``'font_size'`` for :class:`~uplogic.ui.label.Label`.
    :param halign: Horizontal alignment pivot: ``'left'``, ``'center'``, or ``'right'``.
    :param valign: Vertical alignment pivot: ``'bottom'``, ``'center'``, or ``'top'``.
    :param angle: Rotation in degrees around the alignment pivot.
    :param show: Initial visibility.
    '''

    vertex_in: list[tuple[str, str]] = [
        ('VEC2', 'texCoord'),
        ('VEC3', "position")
    ]
    '''Vertex-shader input attributes: UV texture coordinates and world position.'''

    interfaces: list[tuple[str, str]] = [
        ('VEC3', "pos"),
        ('VEC2', "uv")
    ]
    '''Variables interpolated from the vertex shader to the fragment shader.'''

    constants: list[tuple[str, str]] = [
        ('VEC2', "resolution"),
        ('VEC4', "color"),
        ('VEC4', "border_color"),
        ('FLOAT', "border_width")
    ]
    '''Push-constant uniforms: widget resolution, fill colour, border colour, and border width.'''

    samplers: list[tuple[str, str]] = []
    '''Texture sampler declarations (none for the base Widget).'''

    vertex_shader: str = '''
        void main()
        {
            uv = texCoord;
            pos = position;
            gl_Position = ModelViewProjectionMatrix * vec4(position, 1.0f);
        }
    '''
    '''GLSL vertex shader source string.'''

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
    '''GLSL fragment shader: solid fill with an optional inset border.'''

    _is_canvas = False

    def __init__(self, pos=(0, 0), size=(0, 0), bg_color=(0, 0, 0, 0), relative={}, halign='left', valign='bottom', angle=0, show=True):
        self.id = uuid.uuid4()
        self._parent = None
        self._vertices = None  # (Vector((0, 0)), Vector((0, 0)), Vector((0, 0)), Vector((0, 0)))
        self._show = show
        self._pos = [0, 0]
        self._size = [0, 0]
        self._rebuild = True
        self._z = 0
        self._clipped = [0, 0]
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
        self.opacity = 1.

    @property
    def idx(self):
        '''Index of this widget among its parent's children, or ``-1`` if unparented.'''
        if self.parent:
            children = self.parent.children
            return children.index(self)
        return -1

    def move_up(self):
        '''Swap this widget one position higher in the parent's draw order (drawn later/on top).'''
        if self.parent is not None:
            children = self.parent.children
            idx = children.index(self)
            if idx < len(children)-1:
                children[idx], children[idx + 1] = children[idx + 1], children[idx]

    def move_down(self):
        '''Swap this widget one position lower in the parent's draw order (drawn earlier/behind).'''
        if self.parent is not None:
            children = self.parent.children
            idx = children.index(self)
            if idx > 0:
                children[idx], children[idx - 1] = children[idx - 1], children[idx]

    def move_to_top(self):
        '''Move this widget to the end of the parent's children list (drawn last/on top).'''
        if self.parent is not None:
            children = self.parent.children
            children.remove(self)
            children.append(self)

    def move_to_bottom(self):
        '''Move this widget to the beginning of the parent's children list (drawn first/behind everything).'''
        if self.parent is not None:
            children = self.parent.children
            children.remove(self)
            children.insert(0, self)

    def register(self):
        '''Override to add custom logic when the widget is attached to a parent.  Default is a no-op.'''
        pass

    def toggle(self, *args):
        '''Toggle :attr:`show` between ``True`` and ``False``.'''
        self.show = not self.show

    def set_visible(self, flag=True):
        '''Set :attr:`show` to *flag*.

        :param flag: Visibility state to apply.  Defaults to ``True``.
        '''
        self.show = flag

    def set_invisible(self):
        '''Set :attr:`show` to ``False``.'''
        self.show = False

    def make_floating(self, pos=True, size=True, halign='center', valign='center'):
        '''Convenience: set relative positioning and alignment in one call.

        :param pos: Use relative (factor) position.  Defaults to ``True``.
        :param size: Use relative (factor) size.  Defaults to ``True``.
        :param halign: Horizontal alignment.  Defaults to ``'center'``.
        :param valign: Vertical alignment.  Defaults to ``'center'``.
        :returns: ``self`` for chaining.
        '''
        self.relative['pos'] = pos
        self.relative['size'] = size
        self.halign = halign
        self.valign = valign
        return self

    @property
    def halign(self):
        '''Horizontal alignment pivot: ``'left'``, ``'center'``, or ``'right'``.

        Accepts a string name and stores the corresponding :data:`ALIGN_*` integer.
        '''
        return self._halign

    @halign.setter
    def halign(self, val):
        alignment = ALIGNMENTS.get(val, val)
        if val and self.show and alignment != self._halign:
            self._rebuild = True
        self._halign = alignment


    @property
    def valign(self):
        '''Vertical alignment pivot: ``'bottom'``, ``'center'``, or ``'top'``.

        Accepts a string name and stores the corresponding :data:`ALIGN_*` integer.
        '''
        return self._valign

    @valign.setter
    def valign(self, val):
        alignment = ALIGNMENTS.get(val, val)
        if val and self.show and alignment != self._valign:
            self._rebuild = True
        self._valign = alignment

    @property
    def active(self):
        '''``True`` when this widget and every ancestor have ``_active`` set.

        Setting to ``False`` effectively disables the widget without hiding it.
        '''
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
        '''``False`` hides this widget and all its children from rendering.
        Inherits the parent's visibility: if the parent is hidden this returns
        ``False`` regardless of the local flag.
        '''
        pshow = self.parent.show if self.parent is not None else True
        return self._show and pshow

    @show.setter
    def show(self, val):
        if val != self._show:
            self._show = val
            if val:
                self._rebuild = True
                for child in self.children:
                    child.pos = child.pos  # noqa

    @property
    def _children_reversed(self):
        return list(self.children.__reversed__())

    @property
    def canvas(self):
        '''Root :class:`~uplogic.ui.canvas.Canvas` this widget is attached to.

        Walks the parent chain to the root.  Returns ``None`` when the widget
        has not been added to a canvas.
        '''
        pa = self
        while pa.parent is not None:
            pa = pa.parent
        return pa if pa._is_canvas else None

    @property
    def pivot(self):
        '''Screen-space rotation pivot point derived from the widget's alignment.

        Returns a zero vector when the widget has no parent or the vertex
        buffer has not yet been built.
        '''
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
        '''Local rotation in degrees.  Positive values rotate counter-clockwise.
        Combines with parent rotations when computing :attr:`_draw_angle`.
        '''
        return self._angle

    @angle.setter
    def angle(self, val):
        if val and self.show and val != self.angle:
            self._rebuild = True
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
        '''Flat list of all descendants (children, grandchildren, …) in draw order.'''
        widgets = []
        for w in self.children:
            widgets.extend(w._recurse)
        return widgets

    @property
    def children(self):
        '''Immediate children of this widget in draw order.'''
        return self._children

    @children.setter
    def children(self, val):
        self._children = val

    @property
    def children_visible(self):
        '''Immediate children of this widget that are currently visible.'''
        return [c for c in self._children if c.show]

    @property
    def bg_color(self):
        '''RGBA background fill colour for the full rectangular area of this widget.'''
        return self._bg_color

    @bg_color.setter
    def bg_color(self, val):
        val = list(val)
        self._bg_color = val

    @property
    def parent(self) -> 'Widget':
        '''Parent widget that provides the coordinate and size reference for this widget.

        Setting re-parents the widget, removes it from the old parent, and
        triggers a full geometry rebuild.
        '''
        return self._parent

    @parent.setter
    def parent(self, val):
        if val and self.show and val != self.pos[0]:
            self._rebuild = True
        if self.parent is not val and self.parent:
            self.parent.remove_widget(self)
        if self.use_clipping is None:
            self.use_clipping = val.use_clipping
        self._parent = val
        self.pos = self.pos  # noqa
        self.size = self.size  # noqa
        for c in self.children:
            c.parent = c.parent  # noqa
        self.on_parent()

    @property
    def pos_pixel(self):
        '''Absolute bottom-left corner position of this widget in screen pixels.

        Returns ``[0, 0]`` before the first draw call.
        '''
        if self._vertices is None:
            return [0, 0]
        pos = self._vertices[1]
        return [
            pos[0],# - self._clipped[0],
            pos[1] #- self._clipped[1]
        ]

    @property
    def pos_abs(self):
        '''Alias for :attr:`pos_pixel`.'''
        return self.pos_pixel

    @property
    def pos(self):
        '''Position of this widget relative to its parent.

        Interpreted as pixels when ``relative['pos']`` is ``False``, or as a
        factor of the parent's draw size when ``True``.
        '''
        return self._pos

    @pos.setter
    def pos(self, val):
        val = list(val)
        if self._pos == val:
            return
        self._pos = val
        if not self.show:
            return
        self.on_pos()
        if self.parent and self.show:
            self._rebuild = True

    def on_pos(self):
        ...

    @property
    def x(self):
        '''Horizontal component of :attr:`pos`.'''
        return self._pos[0]

    @x.setter
    def x(self, val):
        if self.parent and self.show and val != self.pos[0]:
            self._rebuild = True
        self._pos = [val, self.pos[1]]

    @property
    def y(self):
        '''Vertical component of :attr:`pos`.'''
        return self._pos[1]

    @y.setter
    def y(self, val):
        if self.parent and self.show and val != self.pos[1]:
            self._rebuild = True
        self._pos = [self._pos[0], val]

    @property
    def size(self):
        '''Size ``[width, height]`` of this widget.

        Interpreted as pixels when ``relative['size']`` is ``False``, or as a
        factor of the parent's draw size when ``True``.
        '''
        return self._size

    @size.setter
    def size(self, val):
        val = list(val)
        if self._size == val:
            return
        self._size = val
        if not self.show:
            return
        self.on_size()
        if self.parent and self.show:
            self._rebuild = True

    def on_size(self):
        ...

    @property
    def width(self):
        '''Horizontal component of :attr:`size`.'''
        return self.size[0]

    @width.setter
    def width(self, val):
        if self.parent and self.show and val != self.size[0]:
            self._rebuild = True
        self.size = [val, self.size[1]]

    @property
    def height(self):
        '''Vertical component of :attr:`size`.'''
        return self.size[1]

    @height.setter
    def height(self, val):
        if self.parent and self.show and val != self.size[1]:
            self._rebuild = True
        self.size = [self.size[0], val]

    @property
    def size_pixel(self):
        '''Actual rendered size ``[width, height]`` in screen pixels.

        Derived from the vertex buffer; returns ``[0, 0]`` before the first draw.
        '''
        if self._vertices is None:
            return [0, 0]
        bottom_left = self._vertices[1]
        top_right = self._vertices[2]
        return [top_right[0] - bottom_left[0], top_right[1] - bottom_left[1]]

    @property
    def width_pixel(self):
        '''Rendered width in screen pixels.'''
        return self.size_pixel[0]

    @property
    def height_pixel(self):
        '''Rendered height in screen pixels.'''
        return self.size_pixel[1]

    @property
    def clip(self):
        return self.use_clipping

    @clip.setter
    def clip(self, val):
        self.use_clipping = val

    @property
    def use_clipping(self):
        '''When ``True``, drawing is scissored to the parent's pixel bounds.

        Automatically inherits the parent's value: if any ancestor enables
        clipping all descendants are clipped too.
        '''
        return True if self.parent and self.parent.use_clipping else self._use_clipping

    @use_clipping.setter
    def use_clipping(self, val):
        if self.parent and self.show and val != self._opacity:
            self._rebuild = True
        self._use_clipping = val
        for widget in self.childrenRecursive:
            widget._use_clipping = val

    @property
    def opacity(self):
        '''Alpha multiplier for this widget's own draw call (``0.0``–``1.0``).

        Multiplied with the parent's opacity so that hiding a parent dims
        all descendants proportionally.
        '''
        op = self._opacity
        if self.parent:
            op *= self.parent.opacity
        return op

    @opacity.setter
    def opacity(self, val):
        if self.parent and self.show and val != self._opacity:
            self._rebuild = True
        self._opacity = val

    @property
    def content_width(self):
        '''Pixel span of all visible children along the X axis.

        Computed as the distance between the leftmost and rightmost child
        edges.  Returns ``0`` when there are no visible children.
        '''
        widths = []
        for c in self.children:
            if not c.show:
                continue
            p = c._draw_pos[0]
            w = c._draw_size[0]
            widths.extend([p, p + w])
        return (max(widths) - min(widths)) if len(widths) else 0

    @property
    def content_height(self):
        '''Pixel span of all visible children along the Y axis.

        Computed as the distance between the bottommost and topmost child
        edges.  Returns ``0`` when there are no visible children.
        '''
        heights = []
        for c in self.children:
            if not c.show:
                continue
            p = c._draw_pos[1]
            h = c._draw_size[1]
            heights.extend([p, p + h])
        return (max(heights) - min(heights)) if len(heights) else 0

    @property
    def clipping(self):
        '''Scissor rectangle ``[left, right, top, bottom]`` in screen pixels.

        Derived from the parent's pixel position and size.  Used when
        :attr:`use_clipping` is ``True`` to constrain vertex positions.
        '''
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
        '''Next visible sibling in the parent's draw order, or ``None``.'''
        if self.parent is not None and self in self.parent.children_visible:
            idx = self.parent.children_visible.index(self)
            if idx == len(self.parent.children_visible) - 1:
                return None
            return self.parent.children_visible[idx + 1]
        return None

    @property
    def previous_widget(self):
        '''Previous visible sibling in the parent's draw order, or ``None``.'''
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
        if self.parent is None:
            return [0, 0]
        inherit_pos = self.parent._draw_pos if self.parent else [0, 0]
        pdsize = self.parent._draw_size
        pos = [
            math.floor(self.pos[0] * pdsize[0]),
            math.floor(self.pos[1] * pdsize[1])
        ] if self.relative.get('pos') else self.pos
        child_offset = self.parent.child_offset if self.parent else [0, 0]
        pos = [pos[0] + child_offset[0], pos[1] + child_offset[1]]
        if self.parent and self.parent._draw_angle and self._vertices is not None:
            pos = rotate2d(pos, self.parent.pivot - Vector(inherit_pos), self.parent._draw_angle)
        offset = [0, 0]
        dsize = self._draw_size
        if self.halign == ALIGN_CENTER:
            offset[0] += dsize[0] * .5
        elif self.halign == ALIGN_RIGHT:
            offset[0] += dsize[0]
        if self.valign == ALIGN_CENTER:
            offset[1] += dsize[1] * .5
        elif self.valign == ALIGN_TOP:
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
            size = [
                math.floor(self.size[0] * pdsize[0]),
                math.floor(self.size[1] * pdsize[1])
            ]
        if self.copy_width:
            size[1] = size[0]
        elif self.copy_height:
            size[0] = size[1]
        return size

    @property
    def dimensions(self):
        '''``[bottom_left, top_right]`` corners in screen pixels as a pair of vectors.'''
        pos = self._draw_pos
        size = self._draw_size
        return [
            pos,
            Vector((pos[0] + size[0], pos[1] + size[1]))
        ]

    def refresh(self):
        '''Force a full shader and geometry rebuild on the next draw call.'''
        self._build_shader()

    def check_inside(self, x, y):
        '''Return ``True`` when screen pixel ``(x, y)`` falls inside this widget.

        :param x: Screen X position in pixels (origin bottom-left).
        :param y: Screen Y position in pixels (origin bottom-left, Y is flipped internally).
        :returns: ``True`` if the point is within the widget bounds.
        '''
        y = render.getWindowHeight() - y
        dpos = self.pos_pixel
        dsize = self.size_pixel
        return (
            dpos[0] < x < dpos[0] + dsize[0] and
            dpos[1] < y < dpos[1] + dsize[1]
        )

    def start(self):
        '''Override to add one-time initialisation logic after the widget is fully constructed.'''
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

    def _build_shader(self, force=True):
        if self.parent is None:
            return
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
        bg_color[3] *= self.opacity
        border_color[3] *= self.opacity
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
        return self.show and (self.height_pixel > 0 or self.width_pixel > 0)

    def draw(self):
        '''Draw this widget and recurse into visible children.

        Called automatically each frame by the owning :class:`~uplogic.ui.canvas.Canvas`.
        Calling it manually is valid but increases per-frame GPU work.
        '''
        gpu.state.blend_set('ALPHA')
        self.canvas._to_evaluate.append(self)
        for widget in self.children:
            if widget.show:
                widget.draw()

    def evaluate(self):
        '''Override to add per-frame logic that runs after the draw call (e.g. input handling).'''
        ...

    def update(self):
        '''Override to add per-frame update logic (called every frame regardless of visibility).'''
        ...

    def add_widget(self, widget):
        '''Attach *widget* as a child of this widget.

        :param widget: The :class:`Widget` to add.
        :returns: *widget* for chaining.
        '''
        if widget not in self.children:
            widget.parent = self
            self.children.append(widget)
            if self.canvas is not None:
                self.canvas._set_z(-1)
        self.children = sorted(self.children, key=lambda widget: widget._z, reverse=False)
        return widget

    def sort_children(self, key=lambda widget: widget._z, reverse=False):
        '''Sort the children list in-place and refresh Z ordering.

        :param key: Sort key function; defaults to each widget's ``_z`` value.
        :param reverse: Reverse the sort direction.
        '''
        self.children.sort(key=key, reverse=reverse)
        self._set_z(self._z - 1)

    def add_widgets(self, *widgets):
        '''Attach multiple widgets as children in one call.

        :param widgets: Any number of :class:`Widget` instances to add.
        '''
        for w in widgets:
            self.add_widget(w)

    def on_parent(self):
        '''Override to react when this widget is assigned to a new parent.'''
        ...

    def _set_z(self, _z):
        _z += 1
        self._z = _z
        for c in self.children:
            _z = c._set_z(_z)
        return _z

    def remove_widget(self, widget):
        '''Detach *widget* from this widget's children list.

        :param widget: The :class:`Widget` to remove.  No-op if not a child.
        '''
        if widget in self.children:
            self.children.remove(widget)
            widget.parent = None

    def remove(self):
        '''Remove this widget from its parent.  No-op when unparented.'''
        if self.parent:
            self.parent.remove_widget(self)

    def clear(self):
        '''Detach all children from this widget.'''
        to_remove = self.children.copy()
        for child in to_remove:
            self.remove_widget(child)
