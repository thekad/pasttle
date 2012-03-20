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
import sys


cfg_file = os.environ.get('PASTTLECONF', 'pasttle.conf')
CONF = json.load(open(cfg_file))

debug = CONF.get('debug', False)
format = '%(levelname)s %(asctime)s: %(message)s'

if debug:
    logging.basicConfig(level=logging.DEBUG, format=format,
        datefmt='%m/%d/%Y %I:%M:%S %p')
else:
    logging.basicConfig(level=logging.INFO, format=format,
        datefmt='%m/%d/%Y %I:%M:%S %p')

Base = declarative.declarative_base()


class Paste(Base):

    __tablename__ = 'paste'

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)
    content = sqlalchemy.Column(sqlalchemy.Text)
    password = sqlalchemy.Column(sqlalchemy.String(64))
    mimetype = sqlalchemy.Column(sqlalchemy.String(64))
    created = sqlalchemy.Column(sqlalchemy.DateTime,
        default=func.now())

    def __init__(self, content, mimetype, password=None):
        self.content = content
        self.mimetype = mimetype
        self.password = password
        self.created = func.now()

    def __repr__(self):
        return u'<Paste "%s", "%s", locked=%s>' % (self.mimetype,
            self.content[:16], bool(self.password))

app = bottle.Bottle()
engine = sqlalchemy.create_engine(CONF['dsn'], echo=debug,
    convert_unicode=True, logging_name='pasttle.db')
Base.metadata.create_all(engine)
db_plugin = sqlaplugin.SQLAlchemyPlugin(engine, Base.metadata, create=True)
mc_plugin = mcplugin.MemcachePlugin(servers=CONF.get('memcache',
    ['localhost:11211']))
app.install(db_plugin)
app.install(mc_plugin)


@app.route('/')
def index():
    return """<style> a { text-decoration: none } </style>
<pre>
pasttle(1)                          PASTTLE                          pasttle(1)

NAME
    pasttle: simple pastebin:

SYNOPSIS
    &lt;command&gt; | curl -F '%s=&lt;-' %s

</pre>
    """


@app.route('/recent')
def recent(db):
    pastes = db.query(Paste.id, Paste.created, Paste.password).\
        order_by(Paste.id.desc()).limit(20).all()
    ul = u'<ul>%s</ul>'
    li = []
    for paste in pastes:
        li.append(u'<li><a href="/%s">Paste #%d, %s</a></li>' %
            (paste.id, paste.id, paste.created, ))
    return ul % ''.join(li)


@app.post('/post')
def post(db):
    upload = bottle.request.files.upload
    password = bottle.request.forms.password
    if upload.file:
        raw = upload.file.read()
        if upload.filename != '-':
            try:
                lexer = lexers.guess_lexer_for_filename(upload.filename, raw)
            except lexers.ClassNotFound as cnf:
                lexer = lexers.get_lexer_by_name('text')
        else:
            lexer = lexers.guess_lexer(raw)
        mime = lexer.mimetypes[0]
        paste = Paste(content=raw, mimetype=mime, password=password)
        logging.debug(paste)
        db.add(paste)
        return u'%s/%s' % (bottle.request.url, paste.id, )
    else:
        return bottle.HTTPError(400, output='No paste provided')


@app.route('/<id:int>')
def showpaste(db, id):
    paste = db.query(Paste).filter_by(id=id).one()
    lexer = lexers.get_lexer_for_mimetype(paste.mimetype)
    title = u'%s, created on %s' % (paste.mimetype, paste.created, )
    return pygments.highlight(paste.content, lexer,
        formatters.HtmlFormatter(full=True, linenos='table',
            encoding='utf-8', lineanchors='ln', title=title))


bottle.run(app, host='localhost', port=CONF.get('port', 9669), reloader=True)

