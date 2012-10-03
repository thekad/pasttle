#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import sys
from setuptools import setup

extra = {
    'install_requires': [
        'distribute',
        'bottle>=0.9',
        'Pygments',
        'SQLAlchemy',
        'bottle-sqlalchemy',
        'bottle-sqlite',
    ]
}

if sys.version_info >= (3,):
    extra['use_2to3'] = True


setup(
    name = 'pasttle',
    version = '0.6.3',
    url = 'http://github.com/thekad/pasttle/',
    description = 'Simple pastebin on top of bottle.',
    author = 'Jorge Gallegos',
    author_email = 'kad@blegh.net',
    license = 'MIT',
    platforms = 'any',
    zip_safe = False,
    scripts = [
        'pasttle-server.py',
    ],
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    **extra
)

