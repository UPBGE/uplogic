# SPDX-License-Identifier: MIT
# Copyright 2010-2011 Mitchell Stokes

# <pep8 compliant>


from uplogic.input.keyboard import key_down
from uplogic.input.mouse import mouse_down, mouse_up
from .theme import Theme
from .widget import BGUI_MOUSE_NONE
from .widget import BGUI_MOUSE_ACTIVE
from .widget import BGUI_MOUSE_CLICK
from .widget import BGUI_MOUSE_RELEASE
from .widget import BGUI_NO_NORMALIZE
from .widget import BGUI_NO_THEME
from .widget import Widget
from bge import events
from bge import logic
from bge import render
from uplogic.data import GlobalDB
from uplogic.input import mouse_tap
import collections
import gpu
from . import key_defs
import weakref


class System(Widget):
    """The main gui system. Add widgets to this and then call the render() method
    draw the gui.

    """

    normalize_text = True

    def __init__(self, theme=None):
        """
        :param theme: the path to a theme directory

        """

        # Size and positions for children to use.
        # The size will the the view port size and
        # the position will be the top left of the screen

        # Get some viewport info
        view = gpu.state.viewport_get()

        # Theming
        self._system = weakref.ref(self)
        self.theme = Theme(theme)

        Widget.__init__(
            self,
            "<System>",
            size=[view[2], view[3]],
            pos=[0, 0],
            options=BGUI_NO_NORMALIZE | BGUI_NO_THEME
        )

        self._focused_widget = weakref.ref(self)
        self.lock_focus = False

    @property
    def focused_widget(self):
        '''The widget which currently has "focus"'''
        return self._focused_widget()

    @focused_widget.setter
    def focused_widget(self, value):
        self._focused_widget = weakref.ref(value)

    def update_mouse(self, pos, click_state=BGUI_MOUSE_NONE):
        """Updates the system's mouse data

        :param pos: the mouse position
        :param click_state: the current state of the mouse
        :rtype: None

        """

        self.cursor_pos = pos

        Widget._handle_mouse(self, pos, click_state)

    def update_keyboard(self, key, is_shifted):
        """Updates the system's keyboard data

        :param key: the key being input
        :param is_shifted: is the shift key held down?
        :rtype: None
        """

        Widget._handle_key(self, key, is_shifted)

    def add_widget(self, widget):
        if widget == self:
            return

        Widget.add_widget(self, widget)

    def render(self):
        """Renders the GUI system

        :rtype: None
        """

        # Get some viewport info
        view = gpu.state.viewport_get()

        # Update the size if the viewport has changed
        if self.size != [view[2], view[3]]:
            self.size = [view[2], view[3]]

        # Update any animations
        Widget._update_anims(self)

        # Render the windows
        Widget._draw(self)


class UISystem(System):
    """A system that is intended to be used with BGE games"""

    def __init__(self, theme=None):
        """
        :param theme: the path to a theme directory

        """
        super().__init__(theme)

        self.mouse = logic.mouse

        # All layouts will be a widget subclass, so we can just keep track of one widget
        self.layout = None

        # We can also add 'overlay' layouts
        self.overlays = collections.OrderedDict()

        # Now we generate a dict to map BGE keys to bgui keys
        self.keymap = {getattr(events, val): getattr(key_defs, val) for val in dir(
            events) if val.endswith('KEY') or val.startswith('PAD')}

        # Now setup the scene callback so we can draw
        logic.getCurrentScene().post_draw.append(self._render)

    def load_layout(self, layout, data=None):
        """Load a layout and replace any previously loaded layout

        :param layout: The layout to load (None to have no layouts loaded)
        :param data: User data to send to the layout's constructor
        """

        if self.layout:
            self._remove_widget(self.layout)

        if layout:
            self.layout = layout
            layout.parent = self
            layout.system = self
        else:
            self.layout = None

    def add_overlay(self, overlay, data=None):
        """Add an overlay layout, which sits on top of the currently loaded layout

        :param overlay: The layout to add as an overlay
        :param data: User data to send to the layout's constructor"""

        name = overlay.__class__.__name__

        if name in self.overlays:
            print("Overlay: %s, is already added" % name)
            return

        self.overlays[overlay.__class__.__name__] = overlay(self, data)

    def remove_overlay(self, overlay):
        """Remove an overlay layout by name

        :param overlay: the class name of the overlay to remove (this is the same name as the layout used to add the overlay)
        """

        name = overlay.__class__.__name__

        if name in self.overlays:
            self._remove_widget(self.overlays[name])
            del self.overlays[name]
        else:
            print("WARNING: Overlay: %s was not found, nothing was removed" % name)

    def toggle_overlay(self, overlay, data=None):
        """Toggle an overlay (if the overlay is active, remove it, otherwise add it)

        :param overlay: The class name of the layout to toggle
        :param data: User data to send to the layout's constructor
        """

        if overlay.__class__.__name__ in self.overlays:
            self.remove_overlay(overlay)
        else:
            self.add_overlay(overlay, data)

    def _render(self):
        try:
            super().render()
        except:
            # If there was a problem with rendering, stop so we don't spam the console
            import traceback
            traceback.print_exc()
            logic.getCurrentScene().post_draw.remove(self._render)

    def run(self):
        """A high-level method to be run every frame"""

        if not self.layout:
            return

        # Update the layout and overlays
        self.layout.update()

        for key, value in self.overlays.items():
            value.update()

        # Handle the mouse
        mouse = self.mouse

        pos = list(mouse.position[:])
        pos[0] *= render.getWindowWidth()
        pos[1] = render.getWindowHeight() - (render.getWindowHeight() * pos[1])

        if mouse_tap():
            mouse_state = BGUI_MOUSE_CLICK
        elif mouse_up():
            mouse_state = BGUI_MOUSE_RELEASE
        elif mouse_down():
            mouse_state = BGUI_MOUSE_ACTIVE
        else:
            mouse_state = BGUI_MOUSE_NONE

        self.update_mouse(pos, mouse_state)

        # Handle the keyboard
        keyboard = logic.keyboard

        key_events = keyboard.inputs
        is_shifted = key_down('leftshift') or key_down('rightshift')

        for key, state in key_events.items():
            if state.activated:
                self.update_keyboard(self.keymap[key], is_shifted)


def get_ui_system(system_name: str = 'default', theme: str = '') -> UISystem:
    """Get or create a `bgui.bgui_utils.System` with the given name.

    :param `system_name`: Look for this name.
    :param `theme`: Use this theme for the UI system.
    """
    ui_systems = GlobalDB.retrieve('uplogic.ui')
    if not ui_systems.check(system_name):
        ui_systems.put(system_name, UISystem(theme))
    return ui_systems.get(system_name)


def set_layout(layout, system='default'):
    sys = get_ui_system(system)
    if sys.layout:
        sys.remove_widget(sys.layout)
    sys.load_layout(layout)
    print(sys.layout)

