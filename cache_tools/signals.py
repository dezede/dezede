# coding: utf-8

from __future__ import unicode_literals
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session
from reversion.models import Revision, Version
from .tasks import auto_invalidate


__all__ = ('auto_invalidate_signal_receiver',)


def auto_invalidate_signal_receiver(sender, **kwargs):
    if sender in (Session, LogEntry, Revision, Version):
        return

    instances = kwargs['instances']
    for instance in instances:
        auto_invalidate.delay(instance, [])
