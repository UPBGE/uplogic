'''Root canvas widget for the uplogic UI system (BGE runtime).

:func:`get_canvas` is the preferred way to obtain a named canvas;
:class:`Canvas` is the full-screen root widget that drives the widget tree
each frame via the scene ``post_draw`` hook.
'''

from .widget import Widget
from bge import render
import gpu
import bge
from ..data import GlobalDB


def get_canvas(name='default', show=True):
    '''Retrieve or create a named :class:`Canvas`.

    Looks up *name* in the ``'uplogic.ui'`` :class:`~uplogic.data.GlobalDB`
    store.  If no canvas with that name exists, a new one is created and
    stored.

    :param name: Unique canvas identifier.  Defaults to ``'default'``.
    :param show: Initial visibility when a new canvas is created.
    :returns: The existing or newly created :class:`Canvas`.
    '''
    canvases = GlobalDB.retrieve('uplogic.ui')
    if canvases.check(name):
        canvas = canvases.get(name)
    else:
        canvas = Canvas(show, name)
    # if aud_sys.update not in scene.pre_draw:
    #     scene.pre_draw.append(aud_sys.update)
    return canvas


class Canvas(Widget):
    '''Full-screen root widget that drives the entire widget tree each frame.

    Spans the whole BGE render window and has no visual representation of its
    own.  On construction it registers :meth:`draw` in the current scene's
    ``post_draw`` list and deregisters when the scene is removed.

    A ``Canvas`` cannot be added as a child of another widget.

    :param show: Initial visibility.  Defaults to ``True``.
    :param name: Identifier used with :func:`get_canvas`.  Defaults to
        ``'default'``.
    '''

    _is_canvas = True

    def __init__(self, show=True, name='default'):
        self._hover_consumed = False
        self._click_consumed = False
        self._old_width = bge.render.getWindowWidth()
        self._old_height = bge.render.getWindowHeight()
        self._to_evaluate: list[Widget] = []
        super().__init__((0, 0), (0, 0), show=show)
        self.use_clipping = False
        bge.logic.getCurrentScene().onRemove.append(self.unregister)
        self.register()
        self.start()

    def register(self):
        '''Register :meth:`draw` at the front of the scene ``post_draw`` list.'''
        # bge.logic.getCurrentScene().pre_draw.insert(0, self.draw)
        bge.logic.getCurrentScene().post_draw.insert(0, self.draw)

    def unregister(self):
        '''Remove all references to :meth:`draw` from the scene ``post_draw`` list.'''
        while self.draw in bge.logic.getCurrentScene().post_draw:
            bge.logic.getCurrentScene().post_draw.remove(self.draw)

    def remove(self):
        '''Deregister the canvas from the scene draw list.'''
        self.unregister()

    def fetch_size(self):
        '''Propagate a window-resize event to all direct children by re-setting
        their ``size``, ``pos``, and ``parent`` attributes.
        '''
        for c in self.children:
            c.size = c.size
            c.pos = c.pos
            c.parent = c.parent

    @property
    def size_pixel(self):
        return [
            render.getWindowWidth(),
            render.getWindowHeight()
        ]

    @property
    def width_pixel(self):
        return render.getWindowWidth()

    @property
    def height_pixel(self):
        return render.getWindowHeight()

    @property
    def _draw_pos(self):
        return [0, 0]

    @property
    def pivot(self):
        return (0, 0)

    @property
    def _draw_size(self):
        return [
            render.getWindowWidth(),
            render.getWindowHeight()
        ]

    @property
    def clipping(self):
        return [
            0,
            render.getWindowWidth(),
            render.getWindowHeight(),
            0
        ]

    @property
    def parent(self):
        return None

    @parent.setter
    def parent(self, val):
        self._parent = None

    def draw(self):
        '''Frame entry point registered in ``post_draw``.

        Detects window resizes (calls :meth:`fetch_size` when needed), then
        iterates the widget tree: calls :meth:`Widget.draw` on each widget,
        runs :meth:`Widget.evaluate` on all widgets that queued themselves,
        calls :meth:`update` on the canvas itself, then calls
        :meth:`Widget.update` on each queued widget in reverse draw order.
        '''
        if not self.show:
            return
        width = bge.render.getWindowWidth()
        height = bge.render.getWindowHeight()
        if width != self._old_width or height != self._old_height:
            self.fetch_size()
        self._old_width = width
        self._old_height = height
        gpu.state.blend_set('ALPHA')
        super().draw()
        self._hover_consumed = False
        self._click_consumed = False
        for w in self._to_evaluate.__reversed__():
            if w.parent:
                w.evaluate()
        self.update()
        while self._to_evaluate:
            w = self._to_evaluate.pop()
            if w.parent:
                w.update()

    def update(self):
        '''Override to add per-frame canvas-level logic.'''
        pass

    def new_layer(self):
        '''Create a new full-screen :class:`Layer` child and return it.'''
        layer = Layer()
        self.add_widget(layer)
        return layer


class Layer(Widget):
    '''Full-screen overlay layer that can only be added to a :class:`Canvas`.

    Acts identically to the canvas for sizing and clipping purposes.  Useful
    for grouping widgets at different z-depths.
    '''

    @property
    def _draw_pos(self):
        return [0, 0]

    @property
    def pivot(self):
        return (0, 0)

    @property
    def _draw_size(self):
        return [
            render.getWindowWidth(),
            render.getWindowHeight()
        ]

    @property
    def clipping(self):
        return [
            0,
            render.getWindowWidth(),
            render.getWindowHeight(),
            0
        ]

    @property
    def parent(self):
        '''The widget whose position and size to use relatively.'''
        return self._parent

    @parent.setter
    def parent(self, val):
        if not isinstance(val, Canvas):
            raise TypeError('ui.Layer can only be added to ui.Canvas type!')
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
