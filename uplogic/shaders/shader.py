from bge import logic
from mathutils import Vector


class ULShader():
    '''
    :param `uniforms`: Set of uniforms to be fed into the shaders in format `name: [value, type]`
    '''
    def __init__(
        self,
        fragment_shader,
        idx: int = None,
        uniforms: dict = {}
    ) -> None:
        self.frag_code = fragment_shader
        self.idx = idx
        scene = logic.getCurrentScene()
        self.manager = scene.filterManager
        self._uniforms = uniforms
        self.filter = None

    def start(self):
        filter2d = self.filter = self.manager.addFilter(self.idx, 12, self.frag_code)
        types = {
            int: filter2d.setUniform1i,
            float: filter2d.setUniform1f,
            Vector: filter2d.setUniform3f
        }
        for uniform in self._uniforms:
            filter2d
