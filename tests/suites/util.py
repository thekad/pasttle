#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import os


TOP_DIR = os.path.realpath(
    '%s/../../' % (
        os.path.dirname(
            os.path.realpath(__file__)
        ),
    )
)
TEST_DIR = os.path.realpath(
    '%s/../' % (
        os.path.dirname(
            os.path.realpath(__file__)
        ),
    )
)


def get_source_filenames():
    """
Get all python files so they can be tested.
    """

    filenames = []
    for root, dirs, files in os.walk(TOP_DIR):
        for f in files:
            filename = os.path.join(root, f)
            if f.endswith('.py') and os.path.getsize(filename) > 0:
                filenames.append(filename)

    return filenames


if __name__ == '__main__':
    print get_source_filenames()
