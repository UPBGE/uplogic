from setuptools import setup
import os


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


version = 'v1.5.2'
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
    download_url='https://github.com/UPBGE/uplogic/archive/refs/tags/v1.5.2.tar.gz',
    license='GPLv2',
    packages=[
        'uplogic',
        'uplogic.audio',
        'uplogic.animation',
        'uplogic.data',
        'uplogic.events',
        'uplogic.input',
        'uplogic.nodes',
        'uplogic.nodetrees',
        'uplogic.nodes.actions',
        'uplogic.nodes.conditions',
        'uplogic.nodes.parameters',
        'uplogic.physics',
        'uplogic.utils'
    ],
    zip_safe=True,
    install_requires=['setuptools']
)
