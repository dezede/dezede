# coding: utf-8

from __future__ import unicode_literals
from django.db import connection


def get_raw_query(qs):
    return qs.query.get_compiler(connection=connection).as_sql()
