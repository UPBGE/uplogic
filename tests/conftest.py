import bpy
import doctest
import pytest
import shutil
import tempfile
import bge
import time


class Example(object):

    def __init__(self, want):
        self.want = want + '\n'


class Failure(Exception):
    pass


class Output:

    def __init__(self):
        self._checker = doctest.OutputChecker()
        self._optionflags = (
            doctest.NORMALIZE_WHITESPACE |
            doctest.ELLIPSIS |
            doctest.REPORT_ONLY_FIRST_FAILURE
        )

    def check(self, want, got, optionflags=None):
        if optionflags is None:
            optionflags = self._optionflags
        success = self._checker.check_output(want, got, optionflags)
        if not success:
            raise Failure(self._checker.output_difference(
                Example(want),
                got, optionflags
            ))


@pytest.fixture(scope='session')
def output():
    return Output()


class AppBlend:

    def __init__(self):
        self.tempdir = None
        self.tear_down()

    @property
    def current_scene(self):
        return bge.logic.getCurrentScene()

    def next_frame(self):
        time.sleep(1 / 30)
        bge.logic.NextFrame()

    def wait_until(self, condition):
        while not condition():
            self.next_frame()

    def reset_app(self):
        # remove game objects
        for obj in list(self.current_scene.objects):
            if obj.name == 'Camera':
                continue
            obj.endObject()
        # remove blender objects
        for obj in list(bpy.data.objects):
            if obj.name == 'Camera':
                continue
            bpy.data.objects.remove(obj)
        # remove id data blocks
        for g in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(g)

    def check_initial_state(self):
        # check if application data in initial state
        assert len(self.current_scene.objects) == 1
        assert len(bpy.data.objects) == 1
        assert len(bpy.data.node_groups) == 0

    def set_up(self):
        self.tempdir = tempfile.mkdtemp()

    def tear_down(self):
        if self.tempdir is not None:
            shutil.rmtree(self.tempdir)
            self.tempdir = None
        # reset application data
        self.reset_app()
        # wait for actual object removal
        self.wait_until(lambda: len(self.current_scene.objects) == 1)
        # check if cleanup was successful
        self.check_initial_state()


_app_blend = None


def get_app_blend():
    global _app_blend
    if _app_blend is None:
        _app_blend = AppBlend()
    return _app_blend


@pytest.fixture()
def app_blend():
    app = get_app_blend()
    app.set_up()
    yield app
    app.tear_down()
