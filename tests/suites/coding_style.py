#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import functools
import pep8
import sys
import unittest

import util


class PEP8Test(unittest.TestCase):

    def __init__(self, methodname, filename):
        f = functools.partial(self.pep8, filename)
        f.__doc__ = 'PEP8 for %s' % (filename,)
        self.__setattr__(methodname, f)
        unittest.TestCase.__init__(self, methodname)

    def pep8(self, filename):
        "PEP8 partial check"
        pep8style = pep8.StyleGuide()
        report = pep8style.check_files([filename])
        messages = []
        if report.total_errors != 0:
            report._deferred_print.sort()
            for line_number, offset, code, text, doc in report._deferred_print:
                messages.append('Row %d Col %d: %s' % (
                    line_number, offset + 1, text,)
                )
        self.assertEqual(
            report.total_errors, 0, '; '.join(messages))


def test_cases():
    pep8_suite = unittest.TestSuite()
    for filename in util.get_source_filenames():
        filekey = filename.replace('/', '_').replace('.', '_')
        pep8_suite.addTest(PEP8Test(filekey, filename))
    alltests = unittest.TestSuite([pep8_suite])
    return alltests


def main():
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_cases())
    return (len(result.errors) + len(result.failures)) > 0


if __name__ == '__main__':
    sys.exit(main())
