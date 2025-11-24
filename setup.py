from setuptools import setup
# from Cython.Build import cythonize
import os


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


version = '5.1.0b'
shortdesc = "Uplogic utility for UPBGE."
longdesc = '\n\n'.join([read_file(name) for name in [
    'README.md',
    'LICENSE.md'
]])


setup(
    name='uplogic',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Python',
    ],
    keywords='Blender UPBGE logic',
    author='Leopold Auersperg-Castell',
    author_email='lauersperg@gmx.at',
    url='https://github.com/UPBGE/uplogic',
    download_url=f'https://github.com/UPBGE/uplogic/archive/refs/tags/{version}.tar.gz',
    license='GPLv2',
    packages=[
        'uplogic',
        'uplogic.ai',
        'uplogic.animation',
        'uplogic.audio',
        'uplogic.console',
        'uplogic.data',
        'uplogic.decorators',
        'uplogic.events',
        'uplogic.input',
        'uplogic.network',
        'uplogic.network.osc',
        'uplogic.nodes',
        'uplogic.nodes.actions',
        'uplogic.nodes.conditions',
        'uplogic.nodes.fmod',
        'uplogic.nodes.parameters',
        'uplogic.physics',
        'uplogic.serialize',
        'uplogic.shaders',
        'uplogic.sprites',
        'uplogic.ui',
        'uplogic.ui.preview',
        'uplogic.utils'
    ],
    # ext_modules=cythonize([
    #     'uplogic\\nodes\\__init__.pyx',
    #     'uplogic\\utils\\visuals.pyx',
    #     'uplogic\\nodes\\logictree.pyx'
    # ]),
    zip_safe=True,
    install_requires=['setuptools']
)
