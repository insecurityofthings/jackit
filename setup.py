#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
# import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='JackIt',
    version='0.1.0',
    license='BSD',
    description='JackIt injection tool',
    # long_description='%s\n%s' % (
    #    re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
    #    re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    # ),
    author='phikshun and infamy',
    author_email='',
    url='https://github.com/insecurityofthings/jackit',
    packages=find_packages('jackit'),
    package_dir={'': 'jackit'},
    py_modules=[splitext(basename(path))[0] for path in glob('jackit/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Utilities',
    ],
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    install_requires=[
        'pyusb', 'click', 'tabulate', 'six', 'pyusb'
    ],
    entry_points={
        'console_scripts': [
            'jackit = jackit.jackit:cli',
        ]
    },
)
