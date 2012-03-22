#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import bottle
from bottle.ext import sqlalchemy as sqlaplugin
import cgi
import hashlib
import json
import logging
import os
import pygments
from pygments import formatters
from pygments import lexers
import sqlalchemy
from sqlalchemy import func
from sqlalchemy.ext import declarative


# Load configuration, or default
cfg_file = os.environ.get('PASTTLECONF', 'pasttle.conf')
CONF = json.load(open(cfg_file))

debug = CONF.get('debug', False)
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

    __tablename__ = 'paste'

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    filename = sqlalchemy.Column(sqlalchemy.String(128))
    password = sqlalchemy.Column(sqlalchemy.String(40))
    mimetype = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    created = sqlalchemy.Column(sqlalchemy.DateTime, default=func.now(),
        nullable=False)

    def __init__(self, content, mimetype, filename=None, password=None):
        self.content = content
        self.mimetype = mimetype
        if filename and filename.strip():
            self.filename = filename.strip()[:128]
        if password:
            self.password = hashlib.sha1(password).hexdigest()

    def __repr__(self):
        return u'<Paste "%s" (%s), protected=%s>' % (self.filename,
            self.mimetype, bool(self.password))

app = bottle.Bottle()
engine = sqlalchemy.create_engine(CONF['dsn'], echo=debug,
    convert_unicode=True, logging_name='pasttle.db')
# Create all metadata on loading, if something blows we need to know asap
Base.metadata.create_all(engine)

# Install sqlalchemy plugin
db_plugin = sqlaplugin.SQLAlchemyPlugin(engine, Base.metadata, create=True)
app.install(db_plugin)


@app.route('/')
def index():
    (scheme, host, path, qs, fragment) = bottle.request.urlparts
    return u"""<html>
    <head>
        <title>Pasttle: Simple Pastebin</title>
        <style> a { text-decoration: none } </style>
    </head>
    <body>
        <pre>
pasttle(1)                          PASTTLE                          pasttle(1)

NAME
    pasttle: simple pastebin

SYNOPSIS

    To post the output of a given command:

        &lt;command&gt; | curl -F 'upload=@-' %(url)s/post

    To post the contents of a file:

        curl -F 'upload=@filename.ext' %(url)s/post

    To post the contents of a file and password protect it:

        curl -F 'upload=@filename.ext' -F 'password=humptydumpty' %(url)s/post

    To get the raw contents of a paste (i.e. paste #6):

        curl %(url)s/raw/6

    To get the raw contents of a password-protected paste (i.e. paste #7):

        curl -d password=foo %(url)s/raw/7
        </pre>
    </body>
</html>
    """ % {
        'url': '%s://%s' % (scheme, host, ),
    }


@app.route('/recent')
def recent(db):
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


@app.post('/post')
def post(db):
    upload = bottle.request.files.upload
    password = bottle.request.forms.password
    if isinstance(upload, cgi.FieldStorage) and upload.file:
        raw = upload.file.read()
        filename = None
        if upload.filename != '-':
            filename = upload.filename
            try:
                lexer = lexers.guess_lexer_for_filename(upload.filename, raw)
            except lexers.ClassNotFound:
                lexer = lexers.get_lexer_by_name('text')
        else:
            lexer = lexers.guess_lexer(raw)
        LOGGER.debug(lexer.mimetypes)
        if lexer.mimetypes:
            mime = lexer.mimetypes[0]
        else:
            mime = u'text/plain'
        paste = Paste(content=raw, mimetype=mime,
            filename=filename, password=password)
        LOGGER.debug(paste)
        db.add(paste)
        db.commit()
        (scheme, host, path, qs, fragment) = bottle.request.urlparts
        return u'%s://%s/%s' % (scheme, host, paste.id, )
    else:
        return bottle.HTTPError(400, output='No paste provided')


def _get_paste(db, id):
    paste = db.query(Paste).filter_by(id=id).one()
    return paste


def _password_protect_form(url):
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


@app.route('/<id:int>')
@app.post('/<id:int>')
def showpaste(db, id, lang=None):
    paste = _get_paste(db, id)
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


@app.route('/<id:int>/<lang>')
@app.post('/<id:int>/<lang>')
def forcehighlight(db, id, lang):
    return showpaste(db, id, lang)


@app.route('/raw/<id:int>')
@app.post('/raw/<id:int>')
def showraw(db, id):
    paste = _get_paste(db, id)
    password = bottle.request.forms.password
    LOGGER.debug('%s == %s ? %s' % (hashlib.sha1(password).hexdigest(),
        paste.password,
        hashlib.sha1(password).hexdigest() == paste.password, ))
    if paste.password:
        if not password:
            return _password_protect_form(bottle.request.url)
        if hashlib.sha1(password).hexdigest() == paste.password:
            bottle.response.content_type = 'text/plain'
            return paste.content
        else:
            return bottle.HTTPError(401, output='Wrong password provided')
    else:
        bottle.response.content_type = 'text/plain'
        return paste.content

bottle.run(app, host=CONF.get('bind', 'localhost'),
    port=CONF.get('port', 9669), reloader=True)

