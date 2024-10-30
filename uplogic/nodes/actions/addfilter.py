from uplogic.nodes import ULActionNode
from uplogic.shaders import FXAA
from uplogic.shaders import HBAO
from uplogic.shaders import SSAO
from uplogic.shaders import Vignette
from uplogic.shaders import Brightness
from uplogic.shaders import ChromaticAberration
from uplogic.shaders import Grayscale
from uplogic.shaders import Levels
from uplogic.shaders import Mist
from uplogic.shaders import Blur


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
        self.OUT = self.add_output(self._get_done)

    def _get_done(self):
        return self._done

    def evaluate(self):
        condition = self.get_condition()
        ftype = self.filter_type
        if not condition or self.filter:
            if self.filter:
                if ftype in [3, 'VIGNETTE']:
                    self.filter.uniforms['power'] = self.get_input(self.power)
                    self.filter.uniforms['color'] = self.get_input(self.color)
                elif ftype in [4, 'BRIGHTNESS']:
                    self.filter.uniforms['brightness'] = self.get_input(self.brightness)
                elif ftype in [5, 'CHROMAB']:
                    self.filter.uniforms['power'] = self.get_input(self.power)
                elif ftype in [6, 'GRAYSCALE']:
                    self.filter.uniforms['power'] = self.get_input(self.power)
                elif ftype in [7, 'LEVELS']:
                    self.filter.uniforms['color'] = self.get_input(self.color)
                elif ftype in [8, 'MIST']:
                    self.filter.uniforms['power'] = self.get_input(self.power)
                    self.filter.uniforms['color'] = self.get_input(self.color)
                    self.filter.uniforms['start'] = self.get_input(self.start)
                    self.filter.uniforms['density'] = self.get_input(self.density)
                elif ftype in [1, 2, 'HBAO', 'SSAO']:
                    self.filter.uniforms['power'] = self.get_input(self.power)
            return

        if ftype in [0, 'FXAA']:
            self.filter = FXAA(self.get_input(self.pass_idx))
        elif ftype in [1, 'HBAO']:
            self.filter = HBAO(self.get_input(self.power), self.get_input(self.pass_idx))
        elif ftype in [2, 'SSAO']:
            self.filter = SSAO(self.get_input(self.power), self.get_input(self.pass_idx))
        elif ftype in [3, 'VIGNETTE']:
            self.filter = Vignette(
                self.get_input(self.power),
                self.get_input(self.color),
                self.get_input(self.pass_idx)
            )
        elif ftype in [4, 'BRIGHTNESS']:
            self.filter = Brightness(
                self.get_input(self.brightness),
                self.get_input(self.pass_idx)
            )
        elif ftype in [5, 'CHROMAB']:
            self.filter = ChromaticAberration(
                self.get_input(self.power),
                self.get_input(self.pass_idx)
            )
        elif ftype in [6, 'GRAYSCALE']:
            self.filter = Grayscale(
                self.get_input(self.power),
                self.get_input(self.pass_idx)
            )
        elif ftype in [7, 'LEVELS']:
            self.filter = Levels(
                self.get_input(self.color),
                self.get_input(self.pass_idx)
            )
        elif ftype in [8, 'MIST']:
            self.filter = Mist(
                self.get_input(self.start),
                self.get_input(self.density),
                self.get_input(self.color),
                self.get_input(self.power),
                self.get_input(self.pass_idx)
            )
        elif ftype == 9:
            self.filter = Blur(
                16,
                self.get_input(self.power),
                self.get_input(self.pass_idx)
            )
        self._done = True
