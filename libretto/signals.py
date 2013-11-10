# coding: utf-8

from __future__ import unicode_literals
from celery_haystack.signals import CelerySignalProcessor
from django.contrib.admin.models import LogEntry
from reversion.models import Version, Revision
from .tasks import enqueue_with_stale_objects


class CeleryAutoInvalidator(CelerySignalProcessor):
    @staticmethod
    def enqueue(action, instance, sender, **kwargs):
        if sender in (LogEntry, Revision, Version):
            return

        enqueue_with_stale_objects.delay(action, instance)
