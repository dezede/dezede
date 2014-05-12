# coding: utf-8

from __future__ import unicode_literals
from celery_haystack.signals import CelerySignalProcessor
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session
from reversion.models import Version, Revision
from .tasks import auto_invalidate


class CeleryAutoInvalidator(CelerySignalProcessor):
    def enqueue(self, action, instance, sender, **kwargs):
        if sender in (LogEntry, Session, Revision, Version):
            return

        auto_invalidate.delay(action, instance.__class__, instance.pk)
