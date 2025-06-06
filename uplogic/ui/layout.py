from .widget import Widget
import gpu
from bge import render
import bpy
from mathutils import Vector
from ..utils.math import rotate2d
from ..utils.math import map_range, clamp, lerp
from ..events import schedule, ScheduledEvent


class Layout(Widget):
    '''The Layout class allows you to arrange widgets in a specified area.

    :param `pos`: Initial position of this widget in either pixels or factor.
    :param `size`: Initial size of this widget in either pixels or factor.
    :param `bg_color`: Color to draw in the area of the widget.
    :param `relative`: Whether to use pixels or factor for size or pos; example: `{'pos': True, 'size': True}`.
    :param `border_width`: Width (in pixels) of the border drawn around the area of the widget.
    :param `border_color`: Color to use for drawing the border.
    :param `halign`: Horizontal alignment of the widget, can be (`left`, `center`, `right`).
    :param `valign`: Vertical alignment of the widget, can be (`bottom`, `center`, `top`).
    :param `angle`: Rotation in degrees of this widget around the pivot defined by the alignment.
    '''

    def __init__(
        self,
        pos: list = [0., 0.],
        size: list = [100., 100.],
        bg_color: list = [0, 0, 0, 0],
        relative: dict = {},
        border_width: int = 1,
        border_color: list = [0, 0, 0, 0],
        halign: str = 'left',
        valign: str = 'bottom',
        angle=0,
        show=True
    ):
        self.border_width = border_width
        self.border_color = border_color
        self._inverted = False
        super().__init__(pos, size, bg_color, relative, halign=halign, valign=valign, angle=angle, show=show)
        self.start()

    @property
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, color):
        self._border_color = list(color)

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, val):
        if val < 1:
            val = 1
        self._border_width = int(val)

    def draw(self):
        self._setup_draw()
        gpu.state.line_width_set(self.border_width)
        gpu.state.point_size_set(self.border_width)
        col = self.bg_color.copy()
        col[3] *= self.opacity
        bcol = self.border_color.copy()
        bcol[3] *= self.opacity
        self._shader.uniform_float("color", col)
        self._batch.draw(self._shader)
        self._shader.uniform_float("color", bcol)
        self._batch_line.draw(self._shader)
        self._batch_points.draw(self._shader)
        super().draw()


class RelativeLayout(Layout):
    '''The RelativeLayout allows you to place widgets relative to the Layouts coordinates.

    :param `pos`: Initial position of this widget in either pixels or factor.
    :param `size`: Initial size of this widget in either pixels or factor.
    :param `bg_color`: Color to draw in the area of the widget.
    :param `relative`: Whether to use pixels or factor for size or pos; example: `{'pos': True, 'size': True}`.
    :param `border_width`: Width (in pixels) of the border drawn around the area of the widget.
    :param `border_color`: Color to use for drawing the border.
    :param `halign`: Horizontal alignment of the widget, can be (`left`, `center`, `right`).
    :param `valign`: Vertical alignment of the widget, can be (`bottom`, `center`, `top`).
    :param `angle`: Rotation in degrees of this widget around the pivot defined by the alignment.
    '''
    ...


class FloatLayout(Layout):
    '''The FloatLayout allows you to place widgets in Canvas space.

    :param `pos`: Initial position of this widget in either pixels or factor.
    :param `size`: Initial size of this widget in either pixels or factor.
    :param `bg_color`: Color to draw in the area of the widget.
    :param `relative`: Whether to use pixels or factor for size or pos; example: `{'pos': True, 'size': True}`.
    :param `border_width`: Width (in pixels) of the border drawn around the area of the widget.
    :param `border_color`: Color to use for drawing the border.
    :param `halign`: Horizontal alignment of the widget, can be (`left`, `center`, `right`).
    :param `valign`: Vertical alignment of the widget, can be (`bottom`, `center`, `top`).
    :param `angle`: Rotation in degrees of this widget around the pivot defined by the alignment.
    '''
    # @property
    # def clipping(self):
    #     return [
    #         0,
    #         render.getWindowWidth(),
    #         render.getWindowHeight(),
    #         0
    #     ]

    @property
    def pos_abs(self):
        return [0, 0]


class ArrangedLayout(RelativeLayout):
    """Metaclass"""

    @property
    def inverted(self):
        return self._inverted

    @inverted.setter
    def inverted(self, val):
        self._inverted = val
        self.arrange()
    
    @property
    def arrange_event(self) -> ScheduledEvent:
        return getattr(self, '_arrange_evt', None)

    @arrange_event.setter
    def arrange_event(self, val):
        if self.arrange_event:
            self.arrange_event.cancel()
        self._arrange_evt = val

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
        for c in self.children:
            c.parent = c.parent
        self.arrange()

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
        self.arrange()

    def _setup_draw(self):
        if self._rebuild:
            self._build_shader()
            self.arrange()
        self._rebuild = False

    def add_widget(self, widget):
        super().add_widget(widget)
        self.arrange()
    
    def remove_widget(self, widget):
        super().remove_widget(widget)
        self.arrange()

    def arrange(self):
        raise NotImplementedError


class BoxLayout(ArrangedLayout):
    '''The BoxLayout allows you to automatically arrange widgets in a row or column.

    :param `orientation`: Whether to arrange widgets horizontally or vertically; Can be (`'horizontal'`, `'vertical'`).
    :param `pos`: Initial position of this widget in either pixels or factor.
    :param `size`: Initial size of this widget in either pixels or factor.
    :param `bg_color`: Color to draw in the area of the widget.
    :param `relative`: Whether to use pixels or factor for size or pos; example: `{'pos': True, 'size': True}`.
    :param `border_width`: Width (in pixels) of the border drawn around the area of the widget.
    :param `border_color`: Color to use for drawing the border.
    :param `inverted`: Invert the direction in which the child widgets are arranged.
    :param `spacing`: Pixels in between child widgets.
    :param `halign`: Horizontal alignment of the widget, can be (`left`, `center`, `right`).
    :param `valign`: Vertical alignment of the widget, can be (`bottom`, `center`, `top`).
    :param `angle`: Rotation in degrees of this widget around the pivot defined by the alignment.
    '''
    def __init__(
        self,
        orientation: str = 'horizontal',
        pos: list = [0, 0],
        size: list = [100, 100],
        bg_color: list = (0, 0, 0, 0),
        relative: dict = {},
        border_width: int = 1,
        border_color: list = (0, 0, 0, 0),
        inverted: bool = False,
        spacing: int = 0,
        halign: str = 'left',
        valign: str = 'bottom',
        angle=0,
        show=True
    ):
        self._arrange_offset = 0
        self._do_arrange = False
        self.orientation = orientation
        self.spacing = spacing
        self.children_align = ['left', 'bottom']
        super().__init__(pos, size, bg_color, relative, border_width, border_color, halign=halign, valign=valign, angle=angle, show=show)
        self.inverted = inverted
        self.use_clipping = False

    @property
    def arrange_offset(self):
        return self._arrange_offset

    @arrange_offset.setter
    def arrange_offset(self, val):
        if self._arrange_offset == val:
            return
        self._arrange_offset = val
        self.arrange()

    def arrange(self):
        '''Arrange the widgets according to the specified orientation.'''
        self._do_arrange = True

    def _arrange(self):
        inverted = self.inverted
        self.children_align = ['right', 'bottom'] if inverted else ['left', 'top']
        dsize = self.size_pixel
        arrange_factor = {
            'left': 0,
            'center': .5,
            'right': 1,
            'top': 0,
            'bottom': 1
        }
        xalign = self.children_align[0]
        yalign = self.children_align[1]
        if self.orientation == 'horizontal':
            offset = dsize[0] if inverted else 0
            for widget in filter(lambda widget: widget.show is True, self.children):
                widget.halign = xalign
                widget.valign = yalign
                widget.relative['pos'] = False
                widget.pos = [offset, dsize[1] - (widget._draw_size[1] * arrange_factor[yalign])]
                if inverted:
                    offset -= widget._draw_size[0] + self.spacing
                else:
                    offset += widget._draw_size[0] + self.spacing
        if self.orientation == 'vertical':
            offset = 0 if inverted else dsize[1]
            for widget in filter(lambda widget: widget.show is True, self.children):
                widget.halign = xalign
                widget.valign = yalign
                widget.relative['pos'] = False
                widget.pos = [arrange_factor[xalign] * dsize[0], offset + self._arrange_offset]
                if inverted:
                    offset += widget._draw_size[1] + self.spacing
                else:
                    offset -= widget._draw_size[1] + self.spacing
        self._rebuild_tree()

    def evaluate(self):
        if self._do_arrange:
            self._arrange()
        self._do_arrange = False


class ScrollBoxLayout(BoxLayout):

    def __init__(self, orientation: str = 'horizontal', pos: list = [0, 0], size: list = [100, 100], bg_color: list = (0, 0, 0, 0), relative: dict = {}, border_width: int = 1, border_color: list = (0, 0, 0, 0), inverted: bool = False, spacing: int = 5, halign: str = 'left', valign: str = 'bottom', angle=0, show=True):
        self._c_count = 0
        super().__init__(orientation, pos, size, bg_color, relative, border_width, border_color, inverted, spacing, halign, valign, angle, show)
        self._c_height = 0
        self.seek_speed = .2
        self.scroll_speed = 30
        self._height_diff = 0
        self._arrange_offset_target = 0
        self.scroll_position = 0

    @property
    def use_clipping(self):
        return True

    @use_clipping.setter
    def use_clipping(self, val):
        print("'ScrollBoxLayout.use_clipping' is read-only!")

    @property
    def scroll_position_actual(self):
        return map_range(self._arrange_offset, 0, self._height_diff, 1, 0) if self._height_diff > 0 else 0

    @property
    def scroll_position(self):
        return map_range(self._arrange_offset_target, 0, self._height_diff, 1, 0) if self._height_diff > 0 else 0

    @scroll_position.setter
    def scroll_position(self, val):
        self._arrange_offset_target = map_range(clamp(val), 1, 0, 0, self._height_diff) if self._height_diff > 0 else 0

    def scroll(self, difference):
        self._arrange_offset_target = clamp(self._arrange_offset_target - difference * self.scroll_speed, 0, self._height_diff)

    def _arrange(self):
        self._count_children()
        return super()._arrange()

    def _count_children(self):
        yd_sizes = [c._draw_pos[1] for c in self.children]
        yd_sizes.extend([c._draw_size[1] + c._draw_pos[1] for c in self.children])
        if yd_sizes:
            self._c_height = max(yd_sizes) - min(yd_sizes)
            # self._c_height = sum([c._draw_size[1] for c in self.children])
            self._c_count = len(self.children)
            self._height_diff = self._c_height - self.height_pixel# + len(self.children) * self.spacing - self.spacing
            self._height_diff

    def evaluate(self):
        super().evaluate()
        self.arrange_offset = lerp(self._arrange_offset, self._arrange_offset_target, self.seek_speed)
        self._rebuild_tree()


class GridLayout(BoxLayout):
    '''The GridLayout allows you automatically arrange widgets in a grid.

    :param `orientation`: Whether to arrange widgets horizontally or vertically; Can be (`'horizontal'`, `'vertical'`).
    :param `pos`: Initial position of this widget in either pixels or factor.
    :param `size`: Initial size of this widget in either pixels or factor.
    :param `bg_color`: Color to draw in the area of the widget.
    :param `relative`: Whether to use pixels or factor for size or pos; example: `{'pos': True, 'size': True}`.
    :param `border_width`: Width (in pixels) of the border drawn around the area of the widget.
    :param `border_color`: Color to use for drawing the border.
    :param `spacing`: Pixels in between child widgets.
    :param `cols`: How many columns this layout should have.
    :param `rows`: How many rows this column should have.
    :param `halign`: Horizontal alignment of the widget, can be (`left`, `center`, `right`).
    :param `valign`: Vertical alignment of the widget, can be (`bottom`, `center`, `top`).
    :param `angle`: Rotation in degrees of this widget around the pivot defined by the alignment.
    '''

    def __init__(
        self,
        orientation: str = 'vertical',
        pos: list = [0, 0],
        size: list = [100, 100],
        bg_color: list = [0, 0, 0, 0],
        relative: dict = {},
        border_width: int = 1,
        border_color: list = [0, 0, 0, 0],
        inverted: bool = False,
        spacing: int = 0,
        cols: int = 2,
        rows: int = 2,
        halign: str = 'left',
        valign: str = 'bottom',
        angle=0,
        show=True
    ):
        super().__init__(
            orientation=orientation,
            pos=pos,
            size=size,
            bg_color=bg_color,
            relative=relative,
            border_width=border_width,
            border_color=border_color,
            inverted=inverted,
            spacing=spacing,
            halign=halign,
            valign=valign,
            angle=angle,
            show=show
        )
        self.rows = rows
        self.cols = cols
        # self.start()

    def add_widget(self, widget):
        max = self.rows * self.cols
        if len(self.children) < max:
            super().add_widget(widget)
            self.arrange()

    def arrange(self):
        dsize = self.size_pixel
        idx = 0
        _widget_sizes = []
        if self.orientation == 'horizontal':
            _offset_y = 0
            row = 0
            offset = 0
            for widget in filter(lambda widget: widget.show is True, self.children):
                offset_y = _offset_y + (self.spacing if row else 0)
                widget.relative['pos'] = False
                wsize = widget._draw_size
                widget.pos = [offset, dsize[1] - wsize[1] - offset_y]
                _widget_sizes.append(widget._draw_size[1])
                offset += wsize[0] + self.spacing
                idx += 1
                if idx >= self.cols:
                    idx = 0
                    row += 1
                    _offset_y = max(_widget_sizes)
                    _widget_sizes = []
                    offset = 0
        if self.orientation == 'vertical':
            _offset_x = 0
            col = 0
            offset = 0
            for widget in filter(lambda widget: widget.show is True, self.children):
                offset_x = _offset_x + (self.spacing if col else 0)
                widget.relative['pos'] = False
                wsize = widget._draw_size
                widget.pos = [offset_x, dsize[1] - wsize[1] - offset]
                _widget_sizes.append(widget._draw_size[0])
                offset += wsize[1] + self.spacing
                idx += 1
                if idx >= self.rows:
                    idx = 0
                    col += 1
                    _offset_x = max(_widget_sizes)
                    _widget_sizes = []
                    offset = 0


class PolarLayout(ArrangedLayout):
    '''The Polar Layout allows you automatically arrange widgets in a circular fashion.

    :param `pos`: Initial position of this widget in either pixels or factor.
    :param `relative`: Whether to use pixels or factor for size or pos; example: `{'pos': True}`.
    :param `starting_angle`: Position angle of the first widget. 0 is to the right, 90 is up, 180 is left, 270 is down.
    :param `angle`: Rotation in degrees of this widget around the pivot defined by the alignment.
    '''

    def __init__(
            self,
            pos: list = [0, 0],
            relative: dict = {},
            starting_angle: str = 0,
            radius: int = 100,
            angle: float = 0,
            show: bool = True
        ):
        self._starting_angle = starting_angle
        self._radius = radius
        super().__init__(
            pos,
            (0, 0),
            (0, 0, 0, 0),
            relative,
            0,
            (0, 0, 0, 0),
            'center',
            'center',
            angle,
            show=show
        )
        self.starting_angle = starting_angle
        self.radius = radius
        # self.start()

    @property
    def starting_angle(self):
        return self._starting_angle

    @starting_angle.setter
    def starting_angle(self, val):
        self._starting_angle = val
        self.arrange()

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, val):
        self._radius = val
        self.arrange()

    def add_widget(self, widget):
        super().add_widget(widget)
        w = self.children[-1]
        w.pos = Vector((self.radius, 0))

    def arrange(self):
        if len(self.children) == 0:
            return
        step = 360 / len(self.children)
        _angle = self.starting_angle
        pos = Vector((self.radius, 0))
        for widget in filter(lambda widget: widget.show is True, self.children):
            widget.relative['pos'] = False
            widget.pos = rotate2d(pos, (0, 0), _angle)
            _angle += step
