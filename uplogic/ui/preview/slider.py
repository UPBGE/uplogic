from ..widget import Widget
from .layout import RelativeLayout


class SliderPreview(RelativeLayout):
    '''Blender-editor variant of :class:`~uplogic.ui.slider.Slider`.

    Displays a draggable knob on a bar.  Value is normalised to ``[0.0, 1.0]``.
    Unlike the BGE slider, this variant does not read mouse input — set
    :attr:`value` programmatically from an operator or panel.

    :param pos: Position in pixels or factor.
    :param size: Size ``[width, height]``.
    :param relative: Coordinate interpretation flags.
    :param halign: Horizontal alignment.
    :param valign: Vertical alignment.
    :param orientation: ``'horizontal'`` or ``'vertical'``.
    :param bar_width: Bar thickness as a fraction of the minor dimension.
    :param bar_color: Bar fill colour.
    :param bar_hover_color: Bar hover colour (not interactive in preview).
    :param knob_size: Knob size factor.
    :param knob_color: Knob fill colour.
    :param knob_hover_color: Knob hover colour (not interactive in preview).
    :param steps: Discrete steps; ``-1`` = continuous.
    :param allow_bar_click: Unused in preview context.
    :param angle: Rotation in degrees.
    '''

    def __init__(
        self,
        pos=[0., 0.],
        size=[100., 10.],
        relative={},
        halign='left',
        valign='bottom',
        orientation='horizontal',
        bar_width=.3,
        bar_color=(1, 1, 1, 1),
        bar_hover_color=(1, 1, 1, 1),
        knob_size=1,
        knob_color=(.8, .8, .8, 1),
        knob_hover_color=(.8, .8, .8, 1),
        steps=-1,
        allow_bar_click=True,
        angle=0
    ):
        self.bar = None
        self.knob = None
        self._bar_width = bar_width
        self.bar = RelativeLayout(
            pos=(.5, .5),
            size=(0, 0),
            valign='center',
            halign='center',
            relative={'size': True, 'pos': True},
            bg_color=bar_color
        )
        self._orientation = orientation
        super().__init__(pos, size, (0, 0, 0, 0), relative, halign=halign, valign=valign, angle=angle)
        self._value = 0
        self.add_widget(self.bar)
        self.knob = RelativeLayout(pos=(.5, .5), relative={'pos': True}, size=(0, 0), bg_color=knob_color, valign='center', halign='center')
        self.bar.add_widget(self.knob)
        self.bar_width = bar_width
        self.knob_size = knob_size

    @property
    def bar_width(self):
        '''Thickness of the bar as a relative factor of the minor dimension.'''
        return self.bar.height if self.is_horizontal else self.bar.width

    @bar_width.setter
    def bar_width(self, val):
        self.bar.size = (1, val) if self.is_horizontal else (val, 1)
        self._bar_width = val

    @property
    def value(self):
        '''Normalised slider position in ``[0.0, 1.0]``.  Setting repositions the knob.'''
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        self.knob.pos = (val, .5) if self.is_horizontal else (.5, val)

    @property
    def bar_color(self):
        '''Bar fill colour.'''
        return self.bar.bg_color

    @bar_color.setter
    def bar_color(self, val):
        self.bar.bg_color = val
        self.bar.click_color = val

    @property
    def bar_hover_color(self):
        '''Bar hover colour (unused in preview context; kept for API compatibility).'''
        return self.bar.hover_color

    @bar_hover_color.setter
    def bar_hover_color(self, val):
        self.bar.hover_color = val

    @property
    def knob_color(self):
        '''Knob fill colour.'''
        return self.knob.bg_color

    @knob_color.setter
    def knob_color(self, val):
        self.knob.bg_color = val
        self.knob.click_color = val

    @property
    def knob_hover_color(self):
        '''Knob hover colour (unused in preview context; kept for API compatibility).'''
        return self.knob.hover_color

    @knob_hover_color.setter
    def knob_hover_color(self, val):
        self.knob.hover_color = val

    @property
    def knob_size(self):
        '''Knob size in pixels (square).'''
        return self.knob.size[0]

    @knob_size.setter
    def knob_size(self, val):
        fac = self._draw_size[1] if self.is_horizontal else self._draw_size[0]
        self.knob.size = (val * fac, val * fac)

    @property
    def border_width(self):
        '''Always ``0`` for the floating-bar slider variant.'''
        return 0

    @border_width.setter
    def border_width(self, val):
        self.bar.border_width = 0

    @property
    def border_color(self):
        '''Border colour (always transparent for this variant).'''
        return self.bar.border_color

    @border_color.setter
    def border_color(self, val):
        self.bar.border_color = (0, 0, 0, 0)

    @property
    def orientation(self):
        '''Slider orientation: ``'horizontal'`` or ``'vertical'``.'''
        return self._orientation

    @orientation.setter
    def orientation(self, val):
        self.bar_width = self._bar_width
        self._orientation = val

    @property
    def is_horizontal(self):
        '''``True`` when :attr:`orientation` is not ``'vertical'``.'''
        return self.orientation != 'vertical'

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
        self._build_shader()

    def _build_shader(self, force=False):
        super()._build_shader()
        if self.bar and self.knob:
            self.bar._build_shader(force)
            self.knob._build_shader(force)


class FrameSliderPreview(SliderPreview):
    '''Blender-editor variant of :class:`~uplogic.ui.slider.FrameSlider`.

    The entire slider area is surrounded by a visible border; the knob sits
    inside it.  Value is normalised to ``[0.0, 1.0]``.

    :param pos: Position in pixels or factor.
    :param size: Size ``[width, height]``.
    :param relative: Coordinate interpretation flags.
    :param halign: Horizontal alignment.
    :param valign: Vertical alignment.
    :param orientation: ``'horizontal'`` or ``'vertical'``.
    :param border_width: Frame border thickness in pixels.
    :param border_color: Frame border colour.
    :param bg_color: Background colour inside the frame.
    :param bar_color: Knob fill colour.
    :param bar_hover_color: Hover tint (unused in preview).
    :param steps: Discrete steps; ``-1`` = continuous.
    :param allow_bar_click: Unused in preview context.
    :param angle: Rotation in degrees.
    '''

    def __init__(
        self,
        pos=[0., 0.],
        size=[100., 10.],
        relative={},
        halign='left',
        valign='bottom',
        orientation='horizontal',
        border_width=1,
        border_color=(.8, .8, .8, 1),
        bg_color=(0, 0, 0, 0),
        bar_color=(1, 1, 1, 1),
        bar_hover_color=(.1, .1, .1, .3),
        steps=-1,
        allow_bar_click=True,
        angle=0
    ):
        self.bar = None
        self.knob = None
        Widget.__init__(self, pos, size, (0, 0, 0, 0), relative, halign=halign, valign=valign, angle=angle)
        self._value = 0
        # self._horiz = orientation != 'vertical'
        self._bar_width = 1
        self._orientation = orientation
        self.bar = RelativeLayout(
            pos=(.5, .5),
            size=(1, 1),
            valign='center',
            halign='center',
            relative={'size': True, 'pos': True},
            border_color=border_color,
            bg_color=bg_color,
        )
        self.border_color = border_color
        self.border_width = border_width
        self.knob = RelativeLayout(pos=(.5, .5), relative={'pos': True}, size=(1, 1), bg_color=bar_color, valign='center', halign='center')
        self.knob_size = 1
        self.add_widget(self.bar)
        self.add_widget(self.knob)
        self.start()

    @property
    def bar_width(self):
        return 1

    @bar_width.setter
    def bar_width(self, val):
        self.bar.size = (1, 1)

    @property
    def border_width(self):
        return self.bar.border_width

    @border_width.setter
    def border_width(self, val):
        self.bar.border_width = val

    @property
    def border_color(self):
        return self.bar.border_color

    @border_color.setter
    def border_color(self, val):
        self.bar.border_color = val

    @property
    def knob_size(self):
        return self.knob.size[0]

    @knob_size.setter
    def knob_size(self, val):
        fac = self._draw_size[1] if self.is_horizontal else self._draw_size[0]
        self.knob.size = (fac, fac) if self.is_horizontal else (fac, fac)


class ProgressSliderPreview(FrameSliderPreview):
    '''Blender-editor variant of :class:`~uplogic.ui.slider.ProgressSlider`.

    Fills from the origin edge to the current :attr:`value` rather than
    moving a knob.  Suitable for progress bars and loading indicators.
    '''

    def __init__(self, pos=[0, 0], size=[100, 10], relative={}, halign='left', valign='bottom', orientation='horizontal', border_width=1, border_color=(0.8, 0.8, 0.8, 1), bg_color=(0, 0, 0, 0), bar_color=(1, 1, 1, 1), bar_hover_color=(0.1, 0.1, 0.1, 0.3), steps=-1, allow_bar_click=True, angle=0):
        self.bar = None
        self.knob = None
        self._orientation = orientation
        super().__init__(pos, size, relative, halign, valign, orientation, border_width, border_color, bg_color, bar_color, bar_hover_color, steps, allow_bar_click, angle)
        self.knob.relative = {'size': True}
        self.knob.halign = 'left'
        self.knob.valign = 'bottom'
        self.start()

    @property
    def knob_size(self):
        return (1, 1)
        # return self.knob.size[0]

    @knob_size.setter
    def knob_size(self, val):
        pass
        # self.knob.size = (.5, 1) if self.is_horizontal else (1, .5)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        self.knob.size = (val, 1) if self.is_horizontal else (1, val)
