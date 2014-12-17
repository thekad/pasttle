#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import os
import pasttle
import sys
from setuptools import setup

extra = {}

readme = os.path.join(os.path.dirname(sys.argv[0]), 'README.rst')
requirements = os.path.join(os.path.dirname(sys.argv[0]), 'requirements.txt')

install_requires = open(requirements).readlines(),

if sys.version_info >= (3,):
    extra['use_2to3'] = True
else:
    pass

setup(
    name='pasttle',
    packages=[
        'pasttle',
    ],
    package_data={
        'pasttle': [
            'views/*.html',
            'views/css/*.css',
            'views/images/*',
        ],
    },
    version=pasttle.__version__,
    url='https://github.com/thekad/pasttle',
    description='Simple pastebin on top of bottle.',
    author='Jorge Gallegos',
    author_email='kad@blegh.net',
    license='MIT',
    platforms='any',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pasttle-server.py=pasttle.server:main'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords=['pastebin', 'web', 'paste', 'bottlepy'],
    long_description=open(readme).read(),
    install_requires=install_requires,
    test_suite='tests.all.test_suites',
    **extra
)
