'''Canvas-based HUD and widget system for uplogic (BGE runtime).

All widgets are drawn via Blender's GPU module in the scene ``post_draw``
hook.  The root container is :class:`~uplogic.ui.Canvas`; add any widget
hierarchy to it and it will be rendered every frame automatically.

Typical usage::

    from uplogic import ui

    canvas = ui.Canvas()

    label = ui.Label(pos=(20, 20), text='Score: 0', font_size=18)
    canvas.add_widget(label)

    btn = ui.LabelButton(pos=(100, 50), size=(120, 40), text='OK')
    btn.on_press = lambda w: print('pressed')
    canvas.add_widget(btn)

See :mod:`uplogic.ui.preview` for Blender-editor (bpy) viewport variants.
'''

try:
    from .button import Button, LabelButton, SpriteButton, ImageButton
    from .cursor import Cursor, remove_custom_cursor, set_custom_cursor
    from .circle import Circle
    from .image import Image
    from .image import Sprite
    from .image import Video
    from .label import Label
    from .layout import FloatLayout
    from .layout import Layout
    from .layout import RelativeLayout
    from .layout import BoxLayout
    from .layout import ScrollBoxLayout
    from .layout import GridLayout
    from .layout import PolarLayout
    from .views import ScrollView
    from .widget import Widget
    from .canvas import Canvas
    from .canvas import get_canvas
    from .slider import Slider
    from .slider import FrameSlider
    from .slider import ProgressSlider
    from .path import Path
    from .views import ScrollView
    from .worldpath import WorldPath
    from .worldpath import ObjectPath
    from .behaviors import MouseListener
    from .textinput import TextInput
except Exception:
    print('Not in game mode!')