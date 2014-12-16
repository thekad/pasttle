#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import sys
import suites
import unittest


def test_suites():
    allsuites = []
    for s in (
        suites.coding_style,
        suites.functional,
    ):
        allsuites.append(s.test_cases())
    alltests = unittest.TestSuite(allsuites)
    return alltests


def main():
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suites())
    return (len(result.errors) + len(result.failures)) > 0


if __name__ == '__main__':
    sys.exit(main())
