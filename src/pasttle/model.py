#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import hashlib
import os
import sqlalchemy
from sqlalchemy import func
from sqlalchemy.ext import declarative
from pasttle import util


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
    lexer = sqlalchemy.Column(sqlalchemy.String(64))
    created = sqlalchemy.Column(
        sqlalchemy.DateTime, default=func.now(), nullable=False
    )
    ip = sqlalchemy.Column(sqlalchemy.LargeBinary(16))
    parent = sqlalchemy.Column(sqlalchemy.Integer)

    def __init__(
        self, content, mimetype, filename=None,
        password=None, is_encrypted=True, ip=None,
        lexer=None, parent=None
    ):

        self.content = content
        self.mimetype = mimetype
        if filename and filename.strip():
            self.filename = os.path.basename(filename).strip()[:128]
        if password:
            if is_encrypted:
                self.password = password[:40]
            else:
                self.password = hashlib.sha1(password.encode()).hexdigest()
        self.ip = ip.encode() if ip else None
        self.lexer = lexer
        self.parent = parent

    def __repr__(self):
        return u'<Paste {0} ({1}), protected={2}>'.format(
            self.filename, self.lexer or self.mimetype, bool(self.password))


engine = sqlalchemy.create_engine(
    util.conf.get(util.cfg_section, 'dsn'), echo=util.is_debug,
    convert_unicode=True, logging_name='pasttle.db', echo_pool=util.is_debug,
    pool_recycle=util.pool_recycle
)
# Create all metadata on loading, if something blows we need to know asap
Base.metadata.create_all(engine)
