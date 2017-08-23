#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

from distutils.core import setup

setup(
    name='JackIt',
    version='0.1.0',
    author='infamy and phikshun',
    packages=['jackit', 'jackit.test'],
    scripts=['bin/jackit'],
    url='https://github.com/insecurityofthings/jackit',
    license='BSD',
    description='Exploit framework for MouseJack vulnerability.',
    install_requires=[
        "click==5.1",
        "pyusb==1.0.0",
        "tabulate==0.7.5",
        "six==1.10.0"
    ],
)
