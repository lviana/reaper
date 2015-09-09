#!/usr/bin/python


from setuptools import setup
import os

try:
    os.makedirs('/var/lib/reaper')
except OSError:
    pass

setup(
    name='reaper',
    version='1.5.2',
    description='Shared hosting resource manager',
    long_description='Shared hosting resource manager based on Linux cgroups.',
    author='Luiz Viana',
    author_email='lviana@include.io',
    maintainer='Luiz Viana',
    maintainer_email='lviana@include.io',
    url='https://github.com/lviana/reaper',
    packages=['reaper', 'reaper.collectors'],
    package_dir={'reaper': 'src/lib'},
    license='Apache',
    data_files=[('/usr/bin', ['src/bin/reaperd']),
                ('/usr/bin', ['src/bin/reaper']),
                ('/etc', ['src/etc/reaper.cfg'])]
)
