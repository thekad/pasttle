#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import bottle
from bottle.ext import sqlalchemy as sqlaplugin
from bottle.ext import memcache as mcplugin
import json
import os
import logging
import pygments
from pygments import formatters
from pygments import lexers
import sqlalchemy
from sqlalchemy import func
from sqlalchemy.ext import declarative


cfg_file = os.environ.get('PASTTLECONF', 'pasttle.conf')
CONF = json.load(open(cfg_file))

debug = CONF.get('debug', False)
format = '%(asctime)s %(levelname)s %(name)s %(message)s'

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

Base = declarative.declarative_base()


class Paste(Base):

    __tablename__ = 'paste'

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    filename = sqlalchemy.Column(sqlalchemy.String(128))
    password = sqlalchemy.Column(sqlalchemy.String(64))
    mimetype = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    created = sqlalchemy.Column(sqlalchemy.DateTime)

    def __init__(self, content, mimetype, filename=None, password=None):
        self.content = content
        self.mimetype = mimetype
        if filename:
            self.filename = filename.strip()[:128]
        self.password = password
        self.created = func.now()

    def __repr__(self):
        return u'<Paste "%s" (%s), locked=%s>' % (self.filename,
            self.mimetype, bool(self.password))

app = bottle.Bottle()
engine = sqlalchemy.create_engine(CONF['dsn'], echo=debug,
    convert_unicode=True, logging_name='pasttle.db')
Base.metadata.create_all(engine)
db_plugin = sqlaplugin.SQLAlchemyPlugin(engine, Base.metadata, create=True)
app.install(db_plugin)
mc_plugin = mcplugin.MemcachePlugin(servers=CONF.get('memcache',
    ['localhost:11211']))
app.install(mc_plugin)


@app.route('/')
def index():
    return u"""<style> a { text-decoration: none } </style>
<pre>
pasttle(1)                          PASTTLE                          pasttle(1)

NAME
    pasttle: simple pastebin:

SYNOPSIS
    &lt;command&gt; | curl -F 'upload=@-' %(url)s
</pre>
    """ % {
        'url': bottle.request.url,
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
    if upload.file:
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
        logging.debug(paste)
        db.add(paste)
        db.commit()
        (scheme, host, path, qs, fragment) = bottle.request.urlparts
        return u'%s://%s/%s' % (scheme, host, paste.id, )
    else:
        return bottle.HTTPError(400, output='No paste provided')


def _get_paste(db, id):
    paste = db.query(Paste).filter_by(id=id).one()
    return paste

@app.route('/<id:int>')
def showpaste(db, id):
    paste = _get_paste(db, id)
    lexer = lexers.get_lexer_for_mimetype(paste.mimetype)
    title = u'%s (%s), created on %s' % (paste.filename or u'',
        paste.mimetype, paste.created, )
    LOGGER.debug(lexer)
    bottle.response.content_type = 'text/html'
    return pygments.highlight(paste.content, lexer,
        formatters.HtmlFormatter(full=True, linenos='table',
            encoding='utf-8', lineanchors='ln', title=title))

@app.route('/raw/<id:int>')
def showraw(db, mc, id):
    paste = _get_paste(db, id)
    bottle.response.content_type = 'text/plain'
    return paste.content

bottle.run(app, host=CONF.get('bind', 'localhost'),
    port=CONF.get('port', 9669), reloader=True)

