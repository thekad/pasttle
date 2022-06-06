#!/usr/bin/env python3

import os
import sys
import setuptools

import src.pasttle as pasttle


readme = os.path.join(os.path.dirname(sys.argv[0]), 'README.rst')
requirements = os.path.join(os.path.dirname(sys.argv[0]), 'requirements.txt')

install_requires = open(requirements).readlines()

setuptools.setup(
    name='pasttle',
    packages=[
        'pasttle',
    ],
    package_dir={
        '': 'src',
    },
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
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
)
