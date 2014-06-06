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

        auto_invalidate.apply_async(
            (action, instance._meta.app_label,
             instance.__class__.__name__, instance.pk),
            countdown=2,  # The countdown ensures that the current transaction
                          # is finished, otherwise celery can't find the object
                          # FIXME: Remove it when we use Django 1.6.
            ignore_result=True)
