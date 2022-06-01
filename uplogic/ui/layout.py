from .widget import Widget
from .system import get_ui_system
from .system import set_layout


class Layout(Widget):
    """A base layout class to be used with the BGESystem"""

    def __init__(self, system_name: str = 'default', data=None):
        """
        :param sys: The BGUI system
        :param data: User data
        """
        sys = get_ui_system(system_name)
        super().__init__(sys)
        self.data = data

    def set_layout(self):
        set_layout(self)

    def update(self):
        """A function that is called by the system to update the widget (subclasses should override this)"""
        pass
