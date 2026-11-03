'''BGE 2D post-processing filter system.

Provides :class:`Filter2D` and its subclasses for wrapping ``KX_2DFilter``
objects, a :class:`FilterSystem` registry that tracks all active filters, and
module-level helpers for loading GLSL source and managing filter state by pass
index.
'''
from bge import logic
from mathutils import Vector, Matrix
from uplogic.utils.errors import PassIndexOccupiedError
from uplogic.console import debug, warning
from pathlib import Path
import bpy, bge, gpu


def uniforms(*uniforms):
    '''Class decorator that generates a property on the decorated class for
    each name supplied.

    Each generated property delegates its getter to
    ``self.uniforms.get(attr_name)`` and its setter to
    ``self.uniforms[attr_name] = value``, where ``attr_name`` is the
    corresponding entry from the ``uniforms`` dict stored on the instance.

    :param uniforms: One or more uniform names to expose as class properties.
    :returns: The decorated class with the new properties attached.
    '''
    def deco(cls):
        for uniform in uniforms:

            def getProp(self, attr_name=uniform):
                return self.uniforms.get(attr_name)

            def setProp(self, value, attr_name=uniform):
                self.uniforms[attr_name] = value

            prop = property(getProp, setProp)

            setattr(cls, uniform, prop)
        return cls

    return deco


def load_glsl(filepath: str):
    '''Read a GLSL source file from disk and return its contents as a string.

    :param filepath: Absolute or relative path to the ``.glsl`` file.
    :returns: The full text content of the file as a ``str``.
    '''
    return Path(filepath).read_text()


def remove_filter(pass_idx):
    '''Remove the filter registered at ``pass_idx`` from the scene.

    Convenience wrapper around :meth:`FilterSystem.remove_filter`. Calls
    ``shutdown`` on the filter, which disables it, unregisters the post-draw
    callback and removes it from the scene's filter manager.

    :param pass_idx: Integer pass index of the filter to remove.
    '''
    FilterSystem.remove_filter(pass_idx)


def toggle_filter(pass_idx):
    '''Flip the ``active`` state of the filter at ``pass_idx``.

    Retrieves the filter via :meth:`FilterSystem.get_filter` and inverts its
    ``active`` property, enabling it if currently disabled and vice versa.

    :param pass_idx: Integer pass index of the filter to toggle.
    '''
    filter = FilterSystem.get_filter(pass_idx)
    filter.active = not filter.active


def set_filter_state(pass_idx, state=True):
    '''Set the ``active`` state of the filter at ``pass_idx`` to ``state``.

    Retrieves the filter via :meth:`FilterSystem.get_filter` and assigns
    ``state`` to its ``active`` property.

    :param pass_idx: Integer pass index of the filter to modify.
    :param state: Desired active state; defaults to ``True``.
    '''
    filter = FilterSystem.get_filter(pass_idx)
    filter.active = state


class Filter2D():
    '''Wrapper for a BGE ``KX_2DFilter`` post-processing filter.

    On construction the instance registers itself with :class:`FilterSystem`,
    which calls :meth:`startup` to add the filter to the scene's filter manager
    and then :meth:`activate` to enable it and register the :meth:`update`
    post-draw callback.

    :param program: GLSL source code for the filter as a ``str``.
    :param idx: Pass index to assign to this filter. When ``None`` the
        :class:`FilterSystem` auto-assigns the lowest free index.
    :param uniforms: Mapping of uniform name to a ``dict`` that provides the
        current value under the same key, in the form
        ``{'name': {'name': <value>}}``.

    .. note::
        The :attr:`active` property delegates directly to
        ``self._filter.enabled``; assigning ``True`` calls :meth:`activate`
        and assigning ``False`` calls :meth:`pause`.
    '''

    _deprecated = False

    @property
    def active(self):
        '''Whether the underlying ``KX_2DFilter`` is currently enabled.

        :returns: The value of ``self._filter.enabled``.
        '''
        return self._filter.enabled

    @active.setter
    def active(self, val):
        if val:
            self.activate()
        else:
            self.pause()

    def toggle(self):
        '''Flip the :attr:`active` state of this filter.'''
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

    @property
    def settings(self):
        '''[DEPRECATED] Alias for :attr:`uniforms`.

        Accessing this property logs a deprecation warning. Use
        :attr:`uniforms` instead.

        :returns: The current uniforms mapping.
        '''
        warning('"Filter2D.settings" will be replaced by "Filter2D.uniforms" in future releases!')
        return self.uniforms

    @settings.setter
    def settings(self, val):
        warning('"Filter2D.settings" will be replaced by "Filter2D.uniforms" in future releases!')
        self.uniforms = val

    def startup(self):
        '''Add this filter to the scene's filter manager and apply initial uniforms.

        Called by :class:`FilterSystem` immediately after the filter is
        registered. Raises :class:`~uplogic.utils.errors.PassIndexOccupiedError`
        if ``self.idx`` is already present in :attr:`FilterSystem.filters`.

        :raises PassIndexOccupiedError: When the requested pass index is
            already occupied by another filter.
        '''
        if FilterSystem.filters.get(self.idx) is not None:
            raise PassIndexOccupiedError(self.idx)
        FilterSystem.filters[self.idx] = self
        self._filter = self.manager.addFilter(self.idx, 12, self.program)
        uniforms = self._uniforms
        for uniform in uniforms:
            self.set_uniform(uniform, uniforms[uniform].get(uniform))

    def activate(self):
        '''Enable the filter and register the :meth:`update` post-draw callback.

        Sets ``self._filter.enabled`` to ``True`` and appends :meth:`update`
        to the current scene's ``pre_draw`` list when uniforms are present.
        '''
        self._filter.enabled = True
        if self._uniforms.keys():
            logic.getCurrentScene().pre_draw.append(self.update)

    def update(self):
        '''Push current uniform values to the shader each frame.

        Registered as a post-draw callback by :meth:`activate`. Iterates over
        ``self._uniforms`` and calls :meth:`set_uniform` for each entry.
        '''
        uniforms = self._uniforms
        for uniform in uniforms:
            self.set_uniform(uniform, uniforms[uniform].get(uniform))

    def pause(self):
        '''Disable the filter and unregister the :meth:`update` post-draw callback.

        Sets ``self._filter.enabled`` to ``False`` and removes :meth:`update`
        from the current scene's ``pre_draw`` list if present.
        '''
        self._filter.enabled = False
        if self.update in logic.getCurrentScene().pre_draw:
            logic.getCurrentScene().pre_draw.remove(self.update)

    def shutdown(self):
        '''Disable the filter, remove it from the manager and the registry.

        Calls :meth:`pause`, then removes the filter from
        :attr:`FilterSystem.filters` and from the scene's filter manager via
        ``removeFilter``.
        '''
        self.pause()
        if self in FilterSystem.filters.values():
            FilterSystem.filters.pop(self.idx)
            self.manager.removeFilter(self.idx)

    def set_uniform(self, name, value):
        '''Dispatch a uniform value to the correct ``KX_2DFilter`` setter.

        The setter is chosen by the runtime type of ``value``:

        - ``bool`` or ``int`` -> ``setUniform1i``
        - ``float`` -> ``setUniform1f``
        - ``Vector`` (2-D) -> ``setUniform2f``
        - ``Vector`` (3-D) -> ``setUniform3f``
        - ``Vector`` (4-D) -> ``setUniform4f``
        - ``Matrix`` (3x3) -> ``setUniformMatrix3``
        - ``Matrix`` (4x4) -> ``setUniformMatrix4``
        - ``bpy.types.Image`` -> ``setTexture`` (converted via ``gpu.texture.from_image``)

        :param name: GLSL uniform variable name as a ``str``.
        :param value: Value to upload; type determines which setter is used.
        '''
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
        elif cls is bpy.types.Image:
            self._filter.setTexture(name, gpu.texture.from_image(value))


class ULFilter(Filter2D):
    '''[DEPRECATED] Use :class:`Filter2D` instead.'''
    _deprecated = True


class Attachment2D(Filter2D):
    '''2D filter attachment that delegates construction to :class:`Filter2D`.'''

    def __init__(self, program: str, idx: int = None, uniforms: dict = {}) -> None:
        super().__init__(program, idx, uniforms)


class FilterSystem:
    '''Class-level registry for all active :class:`Filter2D` instances.

    :cvar filters: Mapping of pass index (``int``) to :class:`Filter2D`
        instance for every filter currently managed by this system.
    '''
    filters: dict[Filter2D] = {}

    @classmethod
    def get_filter(cls, idx) -> Filter2D:
        '''Return the :class:`Filter2D` registered at ``idx``, or ``None``.

        :param idx: Integer pass index to look up.
        :returns: The :class:`Filter2D` at that index, or ``None`` if not found.
        '''
        return cls.filters.get(idx)
        # return logic.getCurrentScene().filterManager.getFilter(idx)

    @classmethod
    def add_filter(cls, filter: Filter2D):
        '''Register a :class:`Filter2D` and call its startup and activate hooks.

        When ``filter.idx`` is ``None``, the lowest free integer index is
        assigned automatically. When the requested index is already occupied,
        a debug message is logged and the filter is not started.

        :param filter: The :class:`Filter2D` instance to register.
        '''
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
        '''Shut down and deregister the filter at the given pass index.

        Calls :meth:`Filter2D.shutdown` on the filter registered at ``filter``
        if it exists. Does nothing when no filter is found at that index.

        :param filter: Integer pass index of the filter to remove.
        '''
        if isinstance(filter, int) and cls.filters.get(filter, None):
            cls.filters.get(filter).shutdown()


class Shader:
    '''Placeholder for future shader functionality.'''
    pass
