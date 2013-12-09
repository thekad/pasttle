#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import hashlib
import sqlalchemy
from sqlalchemy import func
from sqlalchemy.ext import declarative
import util


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
    created = sqlalchemy.Column(
        sqlalchemy.DateTime, default=func.now(), nullable=False
    )
    ip = sqlalchemy.Column(sqlalchemy.LargeBinary(16))

    def __init__(
        self, content, mimetype, filename=None,
        password=None, encrypt=True, ip=None
    ):

        self.content = content
        self.mimetype = mimetype
        if filename and filename.strip():
            self.filename = filename.strip()[:128]
        if password:
            if encrypt:
                self.password = hashlib.sha1(password).hexdigest()
            else:
                self.password = password[:40]
        self.ip = ip

    def __repr__(self):
        return u'<Paste "%s" (%s), protected=%s>' % (
            self.filename, self.mimetype, bool(self.password))


engine = sqlalchemy.create_engine(
    util.conf.get(util.cfg_section, 'dsn'), echo=util.is_debug,
    convert_unicode=True, logging_name='pasttle.db', echo_pool=util.is_debug,
    pool_recycle=util.pool_recycle
)
# Create all metadata on loading, if something blows we need to know asap
Base.metadata.create_all(engine)
