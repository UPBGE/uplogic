from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.shaders import FXAA
from uplogic.shaders import HBAO
from uplogic.shaders import SSAO
from uplogic.shaders import Vignette
from uplogic.shaders import Brightness
from uplogic.shaders import ChromaticAberration
from uplogic.shaders import Grayscale
from uplogic.shaders import Levels
from uplogic.shaders import Mist


class ULAddFilter(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.pass_idx = None
        self.brightness = None
        self.power = None
        self.density = None
        self.color = None
        self.start = None
        self.end = None
        self.filter = None
        self.filter_type = 'FXAA'
        self.done = False
        self.OUT = ULOutSocket(self, self._get_done)

    def _get_done(self):
        return self.done

    def evaluate(self):
        self.done = False
        condition = self.get_input(self.condition)
        ftype = self.filter_type
        if not condition or self.filter:
            if self.filter:
                if ftype == 'VIGNETTE':
                    self.filter.settings['power'] = self.get_input(self.power)
                    self.filter.settings['color'] = self.get_input(self.color)
                elif ftype == 'BRIGHTNESS':
                    self.filter.settings['brightness'] = self.get_input(self.brightness)
                elif ftype == 'CHROMAB':
                    self.filter.settings['power'] = self.get_input(self.power)
                elif ftype == 'GRAYSCALE':
                    self.filter.settings['power'] = self.get_input(self.power)
                elif ftype == 'LEVELS':
                    self.filter.settings['color'] = self.get_input(self.color)
                elif ftype == 'MIST':
                    self.filter.settings['power'] = self.get_input(self.power)
                    self.filter.settings['color'] = self.get_input(self.color)
                    self.filter.settings['start'] = self.get_input(self.start)
                    self.filter.settings['density'] = self.get_input(self.density)
                elif ftype in ['HBAO', 'SSAO']:
                    self.filter.settings['power'] = self.get_input(self.power)
            return

        if ftype == 'FXAA':
            self.filter = FXAA(self.get_input(self.pass_idx))
        elif ftype == 'HBAO':
            self.filter = HBAO(self.get_input(self.power), self.get_input(self.pass_idx))
        elif ftype == 'SSAO':
            self.filter = SSAO(self.get_input(self.power), self.get_input(self.pass_idx))
        elif ftype == 'VIGNETTE':
            self.filter = Vignette(
                self.get_input(self.power),
                self.get_input(self.color),
                self.get_input(self.pass_idx)
            )
        elif ftype == 'BRIGHTNESS':
            self.filter = Brightness(
                self.get_input(self.brightness),
                self.get_input(self.pass_idx)
            )
        elif ftype == 'CHROMAB':
            self.filter = ChromaticAberration(
                self.get_input(self.power),
                self.get_input(self.pass_idx)
            )
        elif ftype == 'GRAYSCALE':
            self.filter = Grayscale(
                self.get_input(self.power),
                self.get_input(self.pass_idx)
            )
        elif ftype == 'LEVELS':
            self.filter = Levels(
                self.get_input(self.color),
                self.get_input(self.pass_idx)
            )
        elif ftype == 'MIST':
            self.filter = Mist(
                self.get_input(self.start),
                self.get_input(self.density),
                self.get_input(self.color),
                self.get_input(self.power),
                self.get_input(self.pass_idx)
            )
        self.done = True
