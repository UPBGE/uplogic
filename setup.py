from setuptools import setup
import os


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


version = '1.2'
shortdesc = "Uplogic utility for UPBGE."
longdesc = '\n\n'.join([read_file(name) for name in [
    'README.md',
    'CHANGES.md',
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
    url='https://github.com/IzaZed/Uchronian-Logic-UPBGE-Logic-Nodes',
    download_url='https://github.com/UPBGE/uplogic/archive/refs/tags/v1.2.tar.gz',
    license='GPLv2',
    packages=[
        'audio',
        'animation',
        'data',
        'events',
        'input',
        'nodes',
        'nodes.actions',
        'nodes.conditions',
        'nodes.parameters',
        'physics',
        'utils'
    ],
    zip_safe=True,
    install_requires=['setuptools']
)
