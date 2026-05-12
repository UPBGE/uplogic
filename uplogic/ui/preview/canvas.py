from ..widget import Widget
import gpu
import bpy


class Canvas(Widget):
    '''Root widget for the Blender-editor UI system.

    Spans the full ``VIEW_3D`` area and drives the per-frame draw/evaluate
    loop via ``SpaceView3D.draw_handler_add``.  Cannot be attached to another
    widget.  Call :meth:`register` to activate the canvas and :meth:`remove`
    (or :meth:`unregister`) to detach it.
    '''

    _is_canvas = True

    def __init__(self):
        super().__init__((0, 0), (0, 0))
        self._hover_consumed = False
        self._click_consumed = False
        self.area = None
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                self.area = area
        if area is None:
            return
        self._old_width = self.area.width
        self._old_height = self.area.height

        self.handle = None
        self.use_clipping = False
        self._to_evaluate: list[Widget] = []
        self.start()
    
    def register(self):
        '''Attach this canvas to the ``VIEW_3D`` draw handler and request a redraw.'''
        self.handle = bpy.types.SpaceView3D.draw_handler_add(self.draw, (), 'WINDOW', 'POST_PIXEL')
        for area in bpy.context.window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()

    def unregister(self):
        '''Remove the draw handler, stopping all rendering.'''
        if self.handle:
            bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')

    def remove(self):
        '''Alias for :meth:`unregister`.'''
        self.unregister()

    def fetch_size(self):
        '''Trigger a layout refresh on all children (called when the viewport is resized).'''
        for c in self.children:
            c.size = c.size
            c.pos = c.pos
            c.parent = c.parent

    @property
    def _draw_pos(self):
        return [0, 0]

    @property
    def pivot(self):
        return (0, 0)

    @property
    def _draw_size(self):
        area = None
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                self.area = area
        if area is None:
            return
        return [
            self.area.width,
            self.area.height
        ]

    @property
    def clipping(self):
        area = None
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                self.area = area
        if area is None:
            return
        return [
            0,
            self.area.width,
            self.area.height,
            0
        ]

    @property
    def parent(self):
        return None

    @parent.setter
    def parent(self, val):
        self._parent = None

    def draw(self):
        area = None
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                self.area = area
        if area is None:
            return
        width = area.width
        height = area.height
        if width != self._old_width or height != self._old_height:
            self.fetch_size()
        self._old_width = width
        self._old_height = height
        if not self.show:
            return
        gpu.state.blend_set('ALPHA')
        super().draw()
        self._hover_consumed = False
        self._click_consumed = False
        for w in self._to_evaluate.__reversed__():
            w.evaluate()
        while self._to_evaluate:
            self._to_evaluate.pop().update()

    def update(self):
        pass

    def new_layer(self):
        '''Create a new :class:`Layer`, add it to this canvas, and return it.'''
        layer = Layer()
        self.add_widget(layer)
        return layer


class Layer(Widget):
    '''Full-viewport transparent widget used to group children on a separate draw plane.

    Behaves identically to :class:`Canvas` in terms of coordinate space but
    can only be parented to a :class:`Canvas`.
    '''

    @property
    def _draw_pos(self):
        return [0, 0]

    @property
    def pivot(self):
        return (0, 0)

    @property
    def _draw_size(self):
        area = None
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                self.area = area
        if area is None:
            return
        return [
            self.area.width,
            self.area.height
        ]

    @property
    def clipping(self):
        area = None
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                self.area = area
        if area is None:
            return
        return [
            0,
            self.area.width,
            self.area.height,
            0
        ]

    @property
    def parent(self):
        '''Parent widget (must be a :class:`Canvas`).'''
        return self._parent

    @parent.setter
    def parent(self, val):
        if not isinstance(val, Canvas):
            raise TypeError('ui.Layout can only be added to ui.Canvas type!')
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
