#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import bottle
from bottle import template
from bottle.ext import sqlalchemy as sqlaplugin
import difflib
import hashlib
import IPy
import os
import pkg_resources
import pygments
from pygments import formatters
from pygments import lexers
import sys
import pasttle
from pasttle import util
from pasttle import model


application = bottle.app()

# Load an alternate template directory if specified in pasttle.ini
STATIC_CONTENT = None
if util.conf.has_option(util.cfg_section, 'templates'):
    tpl_path = util.conf.get(util.cfg_section, 'templates')
    tpl_path = os.path.expanduser(tpl_path)
    bottle.TEMPLATE_PATH.append(os.path.realpath(tpl_path))
    STATIC_CONTENT = tpl_path

# Load the templates shipped with the package
tpl_path = pkg_resources.resource_filename('pasttle', 'views')
STATIC_CONTENT = STATIC_CONTENT or tpl_path
bottle.TEMPLATE_PATH.append(tpl_path)

# Install sqlalchemy plugin
db_plugin = sqlaplugin.SQLAlchemyPlugin(
    model.engine, model.Base.metadata, create=True
)

application.install(db_plugin)


def get_url(path=False):
    (scheme, host, q_path, qs, fragment) = bottle.request.urlparts
    if path:
        return '{0}://{1}{2}'.format(scheme, host, q_path)
    else:
        return '{0}://{1}'.format(scheme, host)


@bottle.get('/')
@bottle.view('index')
def index():
    """
    Main index
    """

    return dict(
        url=get_url(),
        title=util.conf.get(util.cfg_section, 'title'),
        version=pasttle.__version__,
    )


@bottle.get('/pygments/<style>.css')
def serve_language_css(style):
    try:
        fmt = formatters.get_formatter_by_name('html', style=style)
    except Exception:
        util.log.warn(
            'Style "{0}" cannot be found, falling back to default'.format(
                style,
            )
        )
        fmt = formatters.get_formatter_by_name('html')
    bottle.response.content_type = 'text/css'
    return fmt.get_style_defs(['.pygmentized'])


@bottle.get('/<filetype:re:(css|images)>/<path:path>')
def serve_static(filetype, path):
    "Serve static files if not configured on the web server"

    return bottle.static_file(os.path.join(filetype, path), STATIC_CONTENT)


@bottle.get('/favicon.ico')
def serve_icon():
    return serve_static('images', 'icon.png')


@bottle.get('/recent')
def recent(db):
    """
    Shows an unordered list of most recent pasted items
    """

    items = util.conf.get(util.cfg_section, 'recent_items')
    return template(
        'recent', dict(
            pastes=db.query(
                model.Paste.id, model.Paste.filename, model.Paste.mimetype,
                model.Paste.created, model.Paste.password
            ).order_by(
                model.Paste.id.desc()
            ).limit(items).all(),
            url=get_url(),
            title=util.conf.get(util.cfg_section, 'title'),
            recent=items,
            version=pasttle.__version__,
        )
    )


@bottle.get('/post')
@bottle.view('post')
def upload_file():
    """
    Frontend for simple posting via web interface
    """
    return dict(
        title='Paste New', content='', password='',
        checked='', syntax='', url=get_url(),
        version=pasttle.__version__,
    )


@bottle.post('/post')
def post(db):
    """
    Main upload interface. Users can password-protect an entry if they so
    desire. You can send an already SHA1 cyphered text to this endpoint so
    your intended password does not fly insecure through the internet
    """

    form = bottle.request.forms
    upload = form.upload
    util.log.debug('In post')
    util.log.debug('Upload: {}'.format(upload))
    filename = form.filename if form.filename != '-' else None
    syntax = form.syntax if form.syntax != '-' else None
    password = form.password
    try:
        parent = int(form.parent) if form.parent else None
    except Exception as e:
        util.log.warn('Parent value does not seem like an int: %s' % (e,))
    is_encrypted = bool(form.is_encrypted)
    redirect = bool(form.redirect)
    util.log.debug('Filename: {0}, Syntax: {1}'.format(filename, syntax,))
    default_lexer = lexers.get_lexer_for_mimetype('text/plain')
    if upload:
        if syntax:
            util.log.debug(
                'Guessing lexer for explicit syntax {0}'.format(syntax,)
            )
            try:
                lexer = lexers.get_lexer_by_name(syntax)
            except lexers.ClassNotFound:
                lexer = default_lexer
        else:
            if filename:
                util.log.debug(
                    'Guessing lexer for filename {0}'.format(filename,)
                )
                try:
                    lexer = lexers.guess_lexer_for_filename(filename, upload)
                except lexers.ClassNotFound:
                    lexer = lexers.guess_lexer(upload)
            else:
                util.log.debug('Use default lexer')
                lexer = default_lexer
        util.log.debug(lexer.mimetypes)
        lx = None
        if lexer.name:
            lx = lexer.name
        else:
            if lexer.aliases:
                lx = lexer.aliases[0]
        mime = lexer.mimetypes[0]
        ip = bottle.request.remote_addr
        if ip:
            # Try not to store crap in the database if it's not a valid IP
            try:
                ip = bin(IPy.IP(ip).int())
            except Exception as ex:
                util.log.warn(
                    'Impossible to store the source IP address: {0}'.format(ex)
                )
                ip = None
        paste = model.Paste(
            content=upload, mimetype=mime, is_encrypted=is_encrypted,
            password=password, ip=ip, filename=filename,
            lexer=lx, parent=parent
        )
        util.log.debug(paste)
        db.add(paste)
        db.commit()
        if redirect:
            bottle.redirect('{0}/{1}'.format(get_url(), paste.id, ))
        else:
            return bottle.HTTPResponse('{0}/{1}'.format(get_url(), paste.id, ))
    else:
        return bottle.HTTPError(400, 'No paste provided')


def _get_paste(db, id):
    """
    Queries the database for the given paste, or returns False is not found
    """

    try:
        paste = db.query(model.Paste).filter_by(id=id).one()
    except Exception:
        paste = None
    return paste


def _add_header_metadata(paste):
    """
    Adds pasttle special headers for paste metadata
    """

    bottle.response.set_header('X-Pasttle-Creation-Date', paste.created)
    bottle.response.set_header('X-Pasttle-Protected', bool(paste.password))
    bottle.response.set_header('X-Pasttle-Mime-Type', paste.mimetype)
    if paste.lexer:
        bottle.response.set_header('X-Pasttle-Lexer', paste.lexer)
    if paste.filename:
        bottle.response.set_header(
            'X-Pasttle-Filename', paste.filename
        )
    if paste.ip:
        ip = IPy.IP(int(paste.ip, 2))
        bottle.response.set_header('X-Pasttle-Source-IP', ip)


def _pygmentize(paste, lang):
    """
    Guess (or force if lang is given) highlight on a given paste via pygments
    """

    util.log.debug("{0} in {1} language".format(paste, lang,))
    if lang:
        try:
            lexer = lexers.get_lexer_by_name(lang)
        except lexers.ClassNotFound:
            lexer = lexers.get_lexer_by_name('text')
    else:
        try:
            util.log.debug(paste.lexer)
            lexer = lexers.get_lexer_by_name(paste.lexer)
            util.log.debug(lexer)
        except lexers.ClassNotFound:
            lexer = lexers.get_lexer_for_mimetype(paste.mimetype)
    util.log.debug('Lexer is {0}'.format(lexer,))
    if paste.ip:
        ip = IPy.IP(int(paste.ip, 2))
        util.log.debug('Originally pasted from {0}'.format(ip,))
    if paste.filename:
        title = '{0}, created on {1}'.format(paste.filename, paste.created, )
    else:
        title = 'created on {0}'.format(paste.created, )
    title = '{0} {1}'.format(paste.mimetype, title,)
    util.log.debug(lexer)
    content = pygments.highlight(
        paste.content, lexer, formatters.HtmlFormatter(
            linenos='table',
            encoding='utf-8',
            lineanchors='ln',
            anchorlinenos=True,
        )
    )
    _add_header_metadata(paste)
    return template(
        'pygmentize.html',
        pygmentized=content,
        title=title,
        version=pasttle.__version__,
        url=get_url(),
        id=paste.id,
        parent=paste.parent or u'',
        pygments_style=util.conf.get(util.cfg_section, 'pygments_style'),
    )


@bottle.get('/diff/<parent:int>..<id:int>')
def showdiff(db, parent, id):
    this = _get_paste(db, id)
    if not this:
        return bottle.HTTPError(404, 'This paste does not exist')

    that = _get_paste(db, parent)
    if not that:
        return bottle.HTTPError(404, 'Parent paste does not exist')

    if this.password or that.password:
        return bottle.HTTPError(
            403, 'Can only show differences between unprotected entries'
        )

    diff = '\n'.join([_ for _ in difflib.unified_diff(
        that.content.splitlines(),
        this.content.splitlines(),
        fromfile=that.filename or 'Paste #{0}'.format(that.id),
        tofile=this.filename or 'Paste #{0}'.format(this.id)
    )])
    lexer = lexers.get_lexer_by_name('diff')
    content = pygments.highlight(
        diff, lexer, formatters.HtmlFormatter(
            linenos='table',
            encoding='utf-8',
            lineanchors='ln',
            anchorlinenos=True,
        )
    )
    return template(
        'pygmentize.html',
        pygmentized=content,
        title='Showing differences between #{0} and #{1}'.format(parent, id),
        version=pasttle.__version__,
        url=get_url(),
        id=id,
        parent=parent,
        pygments_style=util.conf.get(util.cfg_section, 'pygments_style'),
    )


@bottle.get('/<id:int>')
@bottle.post('/<id:int>')
def showpaste(db, id):
    """
    Shows the highlighted entry on the browser. If the entry is protected
    with a password it will display a password entry and will compare against
    the database for a match
    """

    paste = _get_paste(db, id)
    lang = bottle.request.query.lang or None
    if not paste:
        return bottle.HTTPError(404, 'This paste does not exist')
    form = bottle.request.forms
    password = form.get('password')
    if paste.password:
        if not password:
            return template(
                'password_protect',
                url=get_url(),
                title=util.conf.get(util.cfg_section, 'title'),
                version=pasttle.__version__,
            )
        is_encrypted = bool(form.get('is_encrypted'))
        if is_encrypted:
            match = password
        else:
            match = hashlib.sha1(password.encode()).hexdigest()
        util.log.debug(
            '{0} == {1} ? {2}'.format(
                match, paste.password, match == paste.password,
            )
        )
        if match == paste.password:
            bottle.response.content_type = 'text/html'
            return _pygmentize(paste, lang)
        else:
            return bottle.HTTPError(401, 'Wrong password provided')
    else:
        return _pygmentize(paste, lang)


@bottle.get('/raw/<id:int>')
@bottle.post('/raw/<id:int>')
def showraw(db, id):
    """
    Returns the raw version of the entry with the content type set to the
    entry's content type. If the entry is protected with a password it will
    display a simple password entry form until the password is a match in
    the database
    """

    paste = _get_paste(db, id)
    if not paste:
        return bottle.HTTPError(404, 'This paste does not exist')
    form = bottle.request.forms
    if paste.password:
        password = form.get('password')
        if not password:
            return template(
                'password_protect',
                url=get_url(),
                title=util.conf.get(util.cfg_section, 'title'),
                version=pasttle.__version__,
            )
        is_encrypted = bool(form.get('is_encrypted'))
        if is_encrypted:
            match = password
        else:
            match = hashlib.sha1(password.encode()).hexdigest()
        util.log.debug(
            '{0} == {1} ? {2}'.format(
                match, paste.password, match == paste.password,
            )
        )
        if match == paste.password:
            _add_header_metadata(paste)
            bottle.response.content_type = paste.mimetype
            return paste.content
        else:
            return bottle.HTTPError(401, 'Wrong password provided')
    else:
        _add_header_metadata(paste)
        bottle.response.content_type = paste.mimetype
        return paste.content


@bottle.post('/edit/<id:int>')
@bottle.get('/edit/<id:int>')
def edit(db, id):
    """
    Edits the entry. If the entry is protected with a password it will display
    a simple password entry form until the password is a match in the database
    """

    paste = _get_paste(db, id)
    if not paste:
        return bottle.HTTPError(404, 'This paste does not exist')
    post_args = dict(
        title='Create new entry based on #{0}'.format(paste.id),
        password=paste.password or u'',
        content=paste.content,
        checked='',
        syntax=lexers.get_lexer_for_mimetype(paste.mimetype).aliases[0],
        parent=id,
        url=get_url(),
        version=pasttle.__version__,
    )

    form = bottle.request.forms
    if paste.password:
        password = form.get('password')

        if not password:
            return template(
                'password_protect',
                url=get_url(),
                title=util.conf.get(util.cfg_section, 'title'),
                version=pasttle.__version__,
            )

        is_encrypted = bool(form.get('is_encrypted'))
        if not is_encrypted:
            match = hashlib.sha1(password.encode()).hexdigest()
        else:
            match = password
        util.log.debug(
            '{0} == {1} ? {2}'.format(
                match, paste.password,
                match == paste.password,
            )
        )

        if match == paste.password:
            post_args['checked'] = 'checked="checked"'
            return template('post', post_args)
        else:
            return bottle.HTTPError(401, 'Wrong password provided')
    else:
        return template('post', post_args)


def main():
    util.log.info('Using Python {0}'.format(sys.version, ))
    bottle.run(
        application, host=util.conf.get(util.cfg_section, 'bind'),
        port=util.conf.getint(util.cfg_section, 'port'),
        reloader=util.is_debug,
        server=util.conf.get(util.cfg_section, 'wsgi')
    )


if __name__ == '__main__':
    sys.exit(main())
