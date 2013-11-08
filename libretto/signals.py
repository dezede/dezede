# coding: utf-8

from __future__ import unicode_literals
from django.contrib.admin.models import LogEntry
from haystack.signals import BaseSignalProcessor
from reversion.models import (
    Version, Revision, post_revision_commit)
from .tasks import enqueue_with_stale_objects


class HaystackAutoInvalidator(BaseSignalProcessor):
    def setup(self):
        post_revision_commit.connect(self.enqueue)

    def teardown(self):
        post_revision_commit.connect(self.enqueue)

    def enqueue(self, sender, **kwargs):
        if sender in (LogEntry, Revision, Version):
            return

        instances = kwargs['instances']
        versions = kwargs['versions']
        for instance, version in zip(instances, versions):
            enqueue_with_stale_objects.delay('update', instance)
