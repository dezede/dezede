# coding: utf-8

from __future__ import unicode_literals
from django.contrib.admin.models import LogEntry
from django.db.models.signals import post_delete
from haystack.signals import BaseSignalProcessor
from reversion.models import Version, Revision, post_revision_commit
from .tasks import enqueue_with_stale_objects


# FIXME: Revenir vite (plausiblement lors de la mise en place de Django 1.6)
# à une version plus simple (comme 46df13bc9a7a09aa2ea1bcbaeb876d24b5f336ca).
class CeleryAutoInvalidator(BaseSignalProcessor):
    def setup(self):
        post_revision_commit.connect(self.enqueue_save)
        post_delete.connect(self.enqueue_delete)

    def teardown(self):
        post_revision_commit.disconnect(self.enqueue_save)
        post_delete.disconnect(self.enqueue_delete)

    def enqueue_save(self, sender, **kwargs):
        return self.enqueue('update', sender, **kwargs)

    def enqueue_delete(self, sender, **kwargs):
        return self.enqueue('delete', sender, **kwargs)

    def enqueue(self, action, sender, **kwargs):
        if sender in (LogEntry, Revision, Version):
            return

        instances = kwargs.get('instances', [kwargs.get('instance')])
        for instance in instances:
            enqueue_with_stale_objects.delay(action, instance)
