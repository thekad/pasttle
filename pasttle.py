#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import bottle
from bottle.ext import sqlalchemy as sqlaplugin
import cgi
import ConfigParser
import hashlib
import logging
import os
import pygments
from pygments import formatters
from pygments import lexers
import sqlalchemy
from sqlalchemy import func
from sqlalchemy.ext import declarative
import sys


# Load configuration, or default
defaults = {
    'debug': 'yes',
    'bind': 'localhost',
    'port': '9669',
    'title': 'Simple pastebin',
    'wsgi': 'wsgiref',
}

cfg = os.environ.get('PASTTLECONF', 'pasttle.ini').split(':')
if len(cfg) < 2:
    cfg.append('main')

cfg_file, cfg_section = cfg[0], cfg[1]
CONF = ConfigParser.SafeConfigParser(defaults)
CONF.read(os.path.realpath(cfg_file))

debug = CONF.getboolean(cfg_section, 'debug')
format = '%(asctime)s %(levelname)s %(name)s %(message)s'

# Set up logging
LOGGER = logging.getLogger('pasttle.web')
LOGGER.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
if debug:
    ch.setLevel(logging.DEBUG)
else:
    ch.setLevel(logging.INFO)
formatter = logging.Formatter(format)
ch.setFormatter(formatter)
LOGGER.addHandler(ch)

# Subclass declarative base for sqla objects
Base = declarative.declarative_base()


class Paste(Base):
    """
    Main paste sqlalchemy construct for database storage
    """

    __tablename__ = 'paste'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    filename = sqlalchemy.Column(sqlalchemy.String(128))
    password = sqlalchemy.Column(sqlalchemy.String(40))
    mimetype = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    created = sqlalchemy.Column(sqlalchemy.DateTime, default=func.now(),
        nullable=False)
    source = sqlalchemy.Column(sqlalchemy.String(45))

    def __init__(self, content, mimetype, filename=None,
        password=None, encrypt=True, source=None):

        self.content = content
        self.mimetype = mimetype
        if filename and filename.strip():
            self.filename = filename.strip()[:128]
        if password:
            if encrypt:
                self.password = hashlib.sha1(password).hexdigest()
            else:
                self.password = password
        if source:
            self.source = source

    def __repr__(self):
        return u'<Paste "%s" (%s), protected=%s>' % (self.filename,
            self.mimetype, bool(self.password))

application = bottle.app()
engine = sqlalchemy.create_engine(CONF.get(cfg_section, 'dsn'), echo=debug,
    convert_unicode=True, logging_name='pasttle.db')
# Create all metadata on loading, if something blows we need to know asap
Base.metadata.create_all(engine)

# Install sqlalchemy plugin
db_plugin = sqlaplugin.SQLAlchemyPlugin(engine, Base.metadata, create=True)
application.install(db_plugin)


def get_url(path=False):
    (scheme, host, q_path, qs, fragment) = bottle.request.urlparts
    if path:
        return u'%s://%s%s' % (scheme, host, q_path)
    else:
        return u'%s://%s' % (scheme, host)


@bottle.route('/')
def index():
    """
    Main index
    """

    return u"""<html>
    <head>
        <title>%(title)s</title>
        <style>
            body {
                font-family: Courier;
                font-size: 12px;
            }

            p {
                margin: 20px;
            }

            a {
                text-decoration: none;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <pre>
pasttle(1)                          PASTTLE                          pasttle(1)

<strong>NAME</strong>
    pasttle: simple pastebin

<strong>EXAMPLES</strong>

    To post the output of a given command:

        &lt;command&gt; | curl -F "upload=&lt;-" %(url)s/post && echo

    To post the contents of a file:

        curl -F "upload=&lt;filename.ext" %(url)s/post && echo

    To post the contents of a file and force the syntax to be python:

        curl -F "upload=&lt;filename.ext" -F "syntax=python" \\
            %(url)s/post && echo

    To post the contents of a file and password protect it:

        curl -F "upload=&lt;filename.ext" -F "password=humptydumpty" \\
            %(url)s/post && echo

    You don't like sending plain-text passwords:

        curl -F "upload=&lt;filename.ext" \\
            -F "password=$( echo -n 'bootcat' | sha1sum | cut -c 1-40 )" \\
            -F "is_encrypted=yes" %(url)s/post && echo

    To get the raw contents of a paste (i.e. paste #6):

        curl %(url)s/raw/6

    To get the raw contents of a password-protected paste (i.e. paste #7):

        curl -d "password=foo" %(url)s/raw/7

    Again you don't like sending plain-text passwords:

        curl -d "is_encrypted=yes" \\
            -d "password=$( echo -n 'bootcat' | sha1sum | cut -c 1-40 )" \\
            %(url)s/raw/7

<strong>HELPERS</strong>

    There are a couple of helper functions in the link below for pasting and
    getting pastes. Import it from your ~/.bash_profile and you should be able
    to use these functions. Creating a ~/.pasttlerc helps you type less too.

    <a href="%(url)s/pasttle.bashrc">Link</a>

        </pre>
        <p>Copyright &copy; Jorge Gallegos, 2012</p>
        <p>
            <a href="https://github.com/thekad/pasttle">Get the source code</a>
        </p>
    </body>
</html>
    """ % {
        'url': get_url(),
        'title': CONF.get(cfg_section, 'title'),
    }


@bottle.route('/recent')
def recent(db):
    """
    Shows an unordered list of most recent pasted items
    """

    pastes = db.query(Paste.id, Paste.filename, Paste.mimetype,
        Paste.created, Paste.password).\
        order_by(Paste.id.desc()).limit(20).all()
    ul = u'<ul>%s</ul>'
    li = []
    for paste in pastes:
        LOGGER.debug(paste)
        li.append(u'<li><a href="/%s">Paste #%d, %s(%s) %s</a></li>' %
            (paste.id, paste.id, paste.filename or u'',
            paste.mimetype, paste.created, ))
    return ul % ''.join(li)


@bottle.route('/post')
def upload_file():
    """
    Frontend for simple posting via web interface
    """

    return u"""<html>
    <head>
        <title>Upload Form</title>
        <style>
            fieldset {
                padding: 1em;
            }
            label {
                float: left;
                margin-right: 0.5em;
                padding-top: 0.2em;
                text-align: right;
                font-weight: bold;
            }
            .note {
                font-size: small;
            }
        </style>
    </head>
    <body>
        <form method="post" action="%(url)s/post">
            <fieldset>
            <legend>Upload</legend>
                <label for="upload">File: </label>
                <textarea id="upload" name="upload" rows="25"
                cols="80"></textarea>
                <br/>
                <label for="syntax">Force syntax: </label>
                <input id="syntax" name="syntax" />
                <br/>
                <label for="password">Password protect this paste: </label>
                <input id="password" type="password" name="password" />
                <br/>
                <label for="is_encrypted">Is the password encrypted? </label>
                <input type="checkbox" name="is_encrypted" check="false"
                id="is_encrypted" />
                <br/>
                <input type="submit" />
            </fieldset>
            <p class="note">
                Keep in mind that passwords are transmitted in clear-text. The
                password is not cyphered on the client-side because shipping a
                SHA1 javascript library is perhaps too much, if you check the
                "Is encrypted?" checkbox make sure your password is cyphered
                with SHA1. Perhaps you better use the readily available
                <a href="%(url)s/pasttle.bashrc">console helper</a>?
            </p>
        </form>
    </body>
</html>
    """ % {'url': get_url()}


@bottle.post('/post')
def post(db):
    """
    Main upload interface. Users can password-protect an entry if they so
    desire. You can send an already SHA1 cyphered text to this endpoint so
    your intended password does not fly insecure through the internet
    """

    upload = bottle.request.forms.upload
    filename = bottle.request.forms.filename
    syntax = bottle.request.forms.syntax
    password = bottle.request.forms.password
    encrypt = not bool(bottle.request.forms.is_encrypted)
    LOGGER.debug('Filename: %s, Syntax: %s' % (filename, syntax,))
    if upload:
        if syntax and syntax != '-':
            try:
                lexer = lexers.get_lexer_by_name(syntax)
            except lexers.ClassNotFound:
                lexer = lexers.guess_lexer(upload)
        else:
            if filename and filename != '-':
                try:
                    lexer = lexers.guess_lexer_for_filename(filename, upload)
                except lexers.ClassNotFound:
                    lexer = lexers.guess_lexer(upload)
            else:
                lexer = lexers.guess_lexer(upload)
        LOGGER.debug(lexer.mimetypes)
        if lexer.mimetypes:
            mime = lexer.mimetypes[0]
        else:
            mime = u'text/plain'
        source = bottle.request.remote_route
        if source:
            source = source[0]
        paste = Paste(content=upload, mimetype=mime, encrypt=encrypt,
            password=password, source=source)
        LOGGER.debug(paste)
        db.add(paste)
        db.commit()
        return u'%s/%s' % (get_url(), paste.id, )
    else:
        return bottle.HTTPError(400, output='No paste provided')


def _get_paste(db, id):
    """
    Queries the database for the given paste, or returns False is not found
    """

    try:
        paste = db.query(Paste).filter_by(id=id).one()
    except:
        paste = False
    return paste


def _password_protect_form(url):
    """
    Really simple password-protect form
    """

    return u"""<html>
    <head>
    </head>
    <body>
        <p>This entry is password protected, write in your password:</p>
        <form method="post" action="%s">
            <input type="password" name="password" id="password" />
            <input type="submit" />
        </form>
    </body>
</html>
    """ % (url, )


def _pygmentize(paste, lang):
    """
    Guess (or force if lang is given) highlight on a given paste via pygments
    """

    if lang:
        try:
            lexer = lexers.get_lexer_by_name(lang)
        except lexers.ClassNotFound:
            lexer = lexers.get_lexer_by_name('text')
    else:
        lexer = lexers.get_lexer_for_mimetype(paste.mimetype)
    title = u'%s (%s), created on %s' % (paste.filename or u'',
        paste.mimetype, paste.created, )
    LOGGER.debug(lexer)
    return pygments.highlight(paste.content, lexer,
        formatters.HtmlFormatter(full=True, linenos='table',
            encoding='utf-8', lineanchors='ln', title=title))


@bottle.route('/<id:int>')
@bottle.post('/<id:int>')
def showpaste(db, id, lang=None):
    """
    Shows the highlighted entry on the browser. If the entry is protected
    with a password it will display a password entry and will compare against
    the database for a match
    """

    paste = _get_paste(db, id)
    if not paste:
        return bottle.HTTPError(404, output='This paste does not exist')
    password = bottle.request.forms.password
    LOGGER.debug('%s == %s ? %s' % (hashlib.sha1(password).hexdigest(),
        paste.password,
        hashlib.sha1(password).hexdigest() == paste.password, ))
    if paste.password:
        if not password:
            return _password_protect_form(bottle.request.url)
        if hashlib.sha1(password).hexdigest() == paste.password:
            bottle.response.content_type = 'text/html'
            return _pygmentize(paste, lang)
        else:
            return bottle.HTTPError(401, output='Wrong password provided')
    else:
        return _pygmentize(paste, lang)


@bottle.route('/<id:int>/<lang>')
@bottle.post('/<id:int>/<lang>')
def forcehighlight(db, id, lang):
    """Forces a certain highlight against an entry"""

    return showpaste(db, id, lang)


@bottle.route('/raw/<id:int>')
@bottle.post('/raw/<id:int>')
def showraw(db, id):
    """
    Returns the plain-text version of the entry. If the entry is protected
    with a password it will display a simple password entry form until the
    password is a match in the database
    """

    paste = _get_paste(db, id)
    if not paste:
        return bottle.HTTPError(404, output='This paste does not exist')
    password = bottle.request.forms.password
    is_encrypted = bool(bottle.request.forms.is_encrypted)
    if not is_encrypted:
        match = hashlib.sha1(password).hexdigest()
    else:
        match = password
    LOGGER.debug('%s == %s ? %s' % (match, paste.password,
        match == paste.password, ))
    if paste.password:
        if not password:
            return _password_protect_form(bottle.request.url)
        if match == paste.password:
            bottle.response.content_type = 'text/plain'
            return paste.content
        else:
            return bottle.HTTPError(401, output='Wrong password provided')
    else:
        bottle.response.content_type = 'text/plain'
        return paste.content


@bottle.route('/pasttle.bashrc')
def serve_bash_helper_script():
    """
    Serves the static file pasttle.bashrc
    """

    root = os.path.realpath(sys.path[0])
    bottle.response.content_type = 'text/plain'
    return bottle.static_file('pasttle.bashrc', root)


if __name__ == '__main__':
    bottle.run(application, host=CONF.get(cfg_section, 'bind'),
        port=CONF.get(cfg_section, 'port'), reloader=debug,
        server=CONF.get(cfg_section, 'wsgi'))
