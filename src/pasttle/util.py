#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

try:
    import ConfigParser as configparser
except ImportError:
    import configparser
import logging
import os

try:
    import StringIO as py2StringIO
    StringIO = py2StringIO.StringIO
except ImportError:
    import io
    StringIO = io.StringIO


cfg = os.environ.get('PASTTLECONF', 'pasttle.ini').split(':')
if len(cfg) < 2:
    cfg.append('main')

cfg_file, cfg_section = cfg[0], cfg[1]

# Load configuration, or default
default_ini = StringIO("""
[{0}]
debug: true
bind: localhost
port: 9669
title: Simple paste bin
wsgi: wsgiref
pool_recycle: 3600
recent_items: 20
pygments_style: tango
""".format(cfg_section,))

conf = configparser.SafeConfigParser()
conf.readfp(default_ini)
conf.read(os.path.realpath(cfg_file))

is_debug = conf.getboolean(cfg_section, 'debug')
format = '%(asctime)s %(levelname)s %(name)s %(message)s'

# Set up logging
log = logging.getLogger('pasttle')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
if is_debug:
    ch.setLevel(logging.DEBUG)
else:
    ch.setLevel(logging.INFO)
formatter = logging.Formatter(format)
ch.setFormatter(formatter)
log.addHandler(ch)

# This needs to be loaded eagerly
pool_recycle = conf.getint(cfg_section, 'pool_recycle')
log.debug('Running with configuration: {0}'.format(conf.items(cfg_section),))
log.debug(
    'Recycling pool connections every {0} seconds'.format(pool_recycle,)
)
