from bge import logic
from mathutils import Vector, Matrix
from uplogic.utils.errors import PassIndexOccupiedError
from uplogic.utils import debug
from pathlib import Path


def load_glsl(filepath: str):
    return Path(filepath).read_text()


def remove_filter(pass_idx):
    FilterSystem.remove_filter(pass_idx)


def toggle_filter(pass_idx):
    filter = FilterSystem.get_filter(pass_idx)
    filter.active = not filter.active


def set_filter_state(pass_idx, state=True):
    filter = FilterSystem.get_filter(pass_idx)
    filter.active = state


class ULFilter():
    '''Wrapper for KX_2DFilter.

    :param `program`: GLSL code as `str`.
    :param `idx`: Pass Index for this filter.
    :param `uniforms`: A `dict` of [`str`: `dict`] binding dictionary values to
    the filter in the form "key of dictionary".
    '''

    _deprecated = True

    @property
    def active(self):
        return self._filter.enabled

    @active.setter
    def active(self, val):
        if val:
            self.activate()
        else:
            self.pause()

    def toggle(self):
        self.active = not self.active

    def __init__(
        self,
        program: str,
        idx: int = None,
        uniforms: dict = {}
    ) -> None:
        if self._deprecated:
            debug('ULTrackTo class will be renamed to "TrackTo" in future releases!')
        self.program = program
        self.idx = idx
        scene = logic.getCurrentScene()
        self.manager = scene.filterManager
        self._uniforms = uniforms
        self._filter = None
        FilterSystem.add_filter(self)

    def startup(self):
        if FilterSystem.filters.get(self.idx) is not None:
            raise PassIndexOccupiedError(self.idx)
        FilterSystem.filters[self.idx] = self
        self._filter = self.manager.addFilter(self.idx, 12, self.program)
        uniforms = self._uniforms
        for uniform in uniforms:
            self.set_uniform(uniform, uniforms[uniform].get(uniform))

    def activate(self):
        self._filter.enabled = True
        if self._uniforms.keys():
            logic.getCurrentScene().post_draw.append(self.update)

    def update(self):
        uniforms = self._uniforms
        for uniform in uniforms:
            self.set_uniform(uniform, uniforms[uniform].get(uniform))

    def pause(self):
        self._filter.enabled = False
        if self.update in logic.getCurrentScene().post_draw:
            logic.getCurrentScene().post_draw.remove(self.update)

    def shutdown(self):
        self.pause()
        if self in FilterSystem.filters.values():
            FilterSystem.filters.pop(self.idx)
            self.manager.removeFilter(self.idx)

    def set_uniform(self, name, value):
        cls = value.__class__
        if cls is bool:
            self._filter.setUniform1i(name, value)
        elif cls is int:
            self._filter.setUniform1i(name, value)
        elif cls is float:
            self._filter.setUniform1f(name, value)
        elif cls is Vector:
            dim = len(value)
            if dim == 2:
                self._filter.setUniform2f(name, value.x, value.y)
            if dim == 3:
                self._filter.setUniform3f(name, value.x, value.y, value.z)
            if dim == 4:
                self._filter.setUniform4f(name, value.x, value.y, value.z, value.w)
        elif cls is Matrix:
            rows = len(value.row)
            cols = len(value.col)
            if rows == cols == 3:
                self._filter.setUniformMatrix3(
                    name, (
                        [value[0][0], value[0][1], value[0][2]],
                        [value[1][0], value[1][1], value[1][2]],
                        [value[2][0], value[2][1], value[2][2]]
                    ),
                    False
                )
            elif rows == cols == 4:
                self._filter.setUniformMatrix4(
                    name,
                    (
                        [value[0][0], value[0][1], value[0][2], value[0][3]],
                        [value[1][0], value[1][1], value[1][2], value[1][3]],
                        [value[2][0], value[2][1], value[2][2], value[2][3]],
                        [value[3][0], value[2][1], value[3][2], value[3][3]]
                    ),
                )


class Filter2D(ULFilter):
    _deprecated = False


class Attachment2D(ULFilter):

    _deprecated = False

    def __init__(self, program: str, idx: int = None, uniforms: dict = {}) -> None:
        super().__init__(program, idx, uniforms)


class FilterSystem:
    filters: dict[Filter2D] = {}

    @classmethod
    def get_filter(cls, idx) -> Filter2D:
        return cls.filters.get(idx)
        # return logic.getCurrentScene().filterManager.getFilter(idx)

    @classmethod
    def add_filter(cls, filter):
        if filter.idx and cls.filters.get(filter.idx, None) is None:
            filter.startup()
            filter.activate()
        elif filter.idx is not None and cls.filters.get(filter.idx):
            #raise PassIndexOccupiedError
            debug(f"2D Filter pass index {filter.idx} already in-use!")
        else:
            idx = 0
            while cls.filters.get(idx, None) is not None:
                idx += 1
            filter.idx = idx
            filter.startup()
            filter.activate()

    @classmethod
    def remove_filter(cls, filter):
        if isinstance(filter, int) and cls.filters.get(filter, None):
            cls.filters.get(filter).shutdown()