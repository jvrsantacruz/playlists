# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

here = os.path.dirname(os.path.realpath(__file__))
readme = os.path.join(here, 'README.rst')

setup(
    name='playlists',
    version='0.0.1',
    description='Multiformat playlist parsing and exporting',
    long_description=open(readme).read(),
    author='Javier Santacruz',
    author_email='javier.santacruz.lc@gmail.com',
    url='http://github.com/jvrsantacruz/playlists',
    py_modules=['playlists'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    platforms=['Any'],
    scripts=[
        'scripts/playlists'
    ]
)
