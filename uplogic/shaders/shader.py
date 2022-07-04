from bge import logic
from mathutils import Vector, Matrix
from uplogic.utils.errors import PassIndexOccupiedError
from pathlib import Path
import os
path = os.path.abspath(os.path.join(__file__, os.pardir, 'filters', 'ssao.glsl'))


def load_glsl(filepath):
    return Path(filepath).read_text()


class ShaderSystem:
    shaders: dict = {}

    @classmethod
    def add_shader(cls, shader):
        if shader.idx and cls.shaders.get(shader.idx, None) is None:
            cls.shaders[shader.idx] = shader
            shader.start()
        elif shader.idx and cls.shaders.get(shader.idx):
            raise PassIndexOccupiedError
        else:
            idx = 0
            while cls.shaders.get(idx, None) is not None:
                idx += 1
            cls.shaders[idx] = shader
            shader.idx = idx
            shader.start()

    @classmethod
    def remove_shader(cls, shader):
        if isinstance(shader, int) and cls.shaders.get(shader, None):
            cls.shaders.get(shader).shutdown()


class ULShader():
    '''
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
        ShaderSystem.add_shader(self)

    def start(self):
        filter2d = self.filter = self.manager.addFilter(self.idx, 12, self.frag_code)
        for uniform in self._uniforms:
            filter2d
    
    def set_uniform(self, name, value):
        cls = value.__class__
        if cls is int:
            self.filter.setUniform1i(name, value)
        elif cls is float:
            self.filter.setUniform1f(name, value)
        elif cls is Vector:
            dim = len(value)
            if dim == 2:
                self.filter.setUniform2f(name, value.x, value.y)
            if dim == 3:
                self.filter.setUniform3f(name, value.x, value.y, value.z)
            if dim == 4:
                self.filter.setUniform4f(name, value.x, value.y, value.z, value.w)
        elif cls is Matrix:
            rows = len(value.row)
            cols = len(value.col)
            if rows == cols == 3:
                self.filter.setUniformMatrix3(
                    name,(
                        [value[0][0], value[0][1], value[0][2]],
                        [value[1][0], value[1][1], value[1][2]],
                        [value[2][0], value[2][1], value[2][2]]
                    ),
                    False
                )
            elif rows == cols == 4:
                self.filter.setUniformMatrix4(
                    name,
                    (
                        [value[0][0], value[0][1], value[0][2], value[0][3]],
                        [value[1][0], value[1][1], value[1][2], value[1][3]],
                        [value[2][0], value[2][1], value[2][2], value[2][3]],
                        [value[3][0], value[2][1], value[3][2], value[3][3]]
                    ),
                )
