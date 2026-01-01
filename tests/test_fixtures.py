from conftest import AppBlend
from pathlib import Path
import bpy


def test_AppBlend_fixture(output):
    app_blend = AppBlend()
    assert app_blend.tempdir is None

    app_blend.set_up()
    assert app_blend.tempdir is not None
    assert Path(app_blend.tempdir).exists() is True
    output.check('/tmp/...', app_blend.tempdir)

    tempdir = app_blend.tempdir
    app_blend.tear_down()
    assert app_blend.tempdir is None
    assert Path(tempdir).exists() is False
    assert len(bpy.data.objects) == 1
