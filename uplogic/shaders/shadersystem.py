from uplogic.utils.errors import PassIndexOccupiedError


class ShaderSystem:

    def __init__(self) -> None:
        self.shaders: dict = {}

    def add_shader(self, shader):
        if shader.idx and self.shaders.get(shader.idx, None) is None:
            self.shaders[shader.idx] = shader
            shader.start()
        elif shader.idx and self.shaders.get(shader.idx):
            raise PassIndexOccupiedError
        else:
            idx = 0
            while self.shaders.get(idx, None) is not None:
                idx += 1
            self.shaders[idx] = shader
            shader.idx = idx
            shader.start()

    def remove_shader(self, shader):
        if isinstance(shader, int) and self.shaders.get(shader, None):
            self.shaders.get(shader).shutdown()
