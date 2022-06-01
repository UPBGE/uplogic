# SPDX-License-Identifier: MIT
# Copyright 2010-2011 Mitchell Stokes

# <pep8 compliant>

from .system import System as BguiSystem
from .widget import Widget, BGUI_MOUSE_NONE, BGUI_MOUSE_CLICK, BGUI_MOUSE_RELEASE, BGUI_MOUSE_ACTIVE
from . import key_defs
from bge import logic, events, render
import collections


