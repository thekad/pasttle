#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import hashlib
import os
import sys
import unittest
import urlparse
import webtest

import util


class FunctionalTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

    def setUp(self):
        self.test_ini = os.path.join(util.TEST_DIR, 'pasttle.ini')
        os.environ['PASTTLECONF'] = '{0}:test'.format(self.test_ini,)
        from pasttle import server
        self.app = webtest.TestApp(server.application)

    def test_index(self):
        "Index page, expect a 200"
        assert self.app.get('/').status == '200 OK'

    def test_recent(self):
        "Most recent items page, expect a 200"
        assert self.app.get('/recent').status == '200 OK'

    def test_post_form(self):
        "Form page, expect a 200"
        assert self.app.get('/post').status == '200 OK'

    def test_simple_post(self):
        "Post some text, expect a 200"
        rsp = self.app.post(
            '/post', {
                'upload': 'Some text',
            }
        )
        assert rsp.status == '200 OK'

    def test_redirect_post(self):
        "Post some text, expect a 302"
        rsp = self.app.post(
            '/post', {
                'upload': 'Some text',
                'redirect': 'yes',
            }
        )
        assert rsp.status == '302 Found'

    def test_loop(self):
        "Simple loop paste, expect 200 in all of them"

        text = 'Attempt #'
        for x in range(0, 20):
            rsp = self.app.post(
                '/post', {
                    'upload': '{0}{1}'.format(text, x,)
                }
            )
            assert rsp.status == '200 OK'
        assert True

    def test_round_trip(self):
        "Upload some text, expect the text to come back the same"
        text = 'This is the sample text'
        rsp = self.app.post(
            '/post', {
                'upload': text,
            }
        )
        assert rsp.status == '200 OK'
        url = urlparse.urlparse(rsp.body)
        rsp = self.app.get('/raw{0}'.format(url.path,))
        assert rsp.status == '200 OK'
        assert rsp.body == text

    def test_password_clear(self):
        "Simple paste with a clear-text password, expect a 200 and a match"

        text = 'String for clear text password test'
        password = 'plain text password'
        rsp = self.app.post(
            '/post', {
                'upload': text,
                'password': password,
            }
        )
        assert rsp.status == '200 OK'
        url = urlparse.urlparse(rsp.body)
        rsp = self.app.post(
            '/raw{0}'.format(url.path,),
            {
                'password': password,
            }
        )
        assert rsp.status == '200 OK'
        assert rsp.body == text

    def test_password_encrypted(self):
        "Simple paste with an encrypted password, expect a 200 and a match"

        text = 'String for hashed password test'
        password = hashlib.sha1('hashed password').hexdigest()
        rsp = self.app.post(
            '/post', {
                'upload': text,
                'password': password,
                'is_encrypted': 'yes',
            }
        )
        assert rsp.status == '200 OK'
        url = urlparse.urlparse(rsp.body)
        rsp = self.app.post(
            '/raw{0}'.format(url.path,),
            {
                'password': password,
                'is_encrypted': 'yes',
            }
        )
        assert rsp.status == '200 OK'
        assert rsp.body == text

    def test_upload_file_auto_syntax(self):
        "Upload any file, expect a 200 and auto mime type"
        fn = os.path.join(util.TEST_DIR, 'pasttle.ini')
        # ini files have the content type text/x-ini
        ct = 'text/x-ini'
        fh = open(fn, 'rb')
        text = fh.read()
        fh.close()
        rsp = self.app.post(
            '/post', {
                'upload': text,
                'filename': fn,
            }
        )
        assert rsp.status == '200 OK'
        url = urlparse.urlparse(rsp.body)
        rsp = self.app.get(
            '/raw{0}'.format(url.path,),
        )
        assert rsp.status == '200 OK'
        assert rsp.body == text
        assert rsp.content_type == ct

    def test_upload_file_force_syntax(self):
        "Upload any file, expect a 200 and forced mime type"
        fn = os.path.join(util.TEST_DIR, 'pasttle.ini')
        ct = 'text/plain'
        fh = open(fn, 'rb')
        text = fh.read()
        fh.close()
        rsp = self.app.post(
            '/post', {
                'upload': text,
                'filename': fn,
                'syntax': ct,
            }
        )
        assert rsp.status == '200 OK'
        url = urlparse.urlparse(rsp.body)
        rsp = self.app.get(
            '/raw{0}'.format(url.path,),
        )
        assert rsp.status == '200 OK'
        assert rsp.body == text
        assert rsp.content_type == ct


def test_cases():
    suite = unittest.TestSuite()
    for method in dir(FunctionalTest):
        if method.startswith("test"):
            suite.addTest(FunctionalTest(method))
    alltests = unittest.TestSuite([suite])
    return alltests


def main():
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_cases())
    return (len(result.errors) + len(result.failures)) > 0


if __name__ == '__main__':
    sys.exit(main())
