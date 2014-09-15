#!/usr/bin/python

import os
from setuptools import setup

setup(
    name='reaper',
    version='0.1.0',
    description='Shared hosting resource manager',
    long_description='Shared hosting resource manager based on libcgroups.',
    author='Luiz Viana',
    author_email='lviana@include.io',
    maintainer='Luiz Viana',
    maintainer_email='lviana@include.io',
    url='https://github.com/lviana/reaper',
    packages=['reaper'],
    package_dir={'reaper': 'src/lib'},
    license='Apache',
    data_files=[('/usr/bin', ['src/bin/reaperd']),
                ('/etc', ['src/etc/reaper.cfg'])]
)
