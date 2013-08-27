# coding: utf-8

from __future__ import unicode_literals
from celery.task import task
from celery_haystack.indexes import CelerySearchIndex
from celery_haystack.tasks import CeleryHaystackSignalHandler as Original
from celery_haystack.utils import get_update_task
from haystack import connections, connection_router
from haystack.exceptions import NotHandled
from haystack.utils import get_identifier
from polymorphic import PolymorphicModel
from cache_tools.tasks import get_stale_objects


__all__ = ('CeleryHaystackSignalHandler',)


def is_polymorphic_model(model):
    return issubclass(model, PolymorphicModel)


def get_polymorphic_parent_model(model):
    if is_polymorphic_model(model):
        parent_model = [p for p in model.__bases__ if is_polymorphic_model(p)]
        assert len(parent_model) == 1
        parent_model = parent_model[0]
        if not parent_model._meta.abstract:
            return parent_model
    return model


def is_polymorphic_child_model(model):
    return get_polymorphic_parent_model(model) != model


def enqueue(action, instance, model):
    # Taken from celery_haystack.signals.CelerySignalProcessor.enqueue
    using_backends = connection_router.for_write(instance=instance)

    for using in using_backends:
        try:
            connection = connections[using]
            index = connection.get_unified_index().get_index(model)
        except NotHandled:
            continue

        if isinstance(index, CelerySearchIndex):
            if action == 'update' and not index.should_update(instance):
                continue
            identifier = get_identifier(instance)
            get_update_task()()(action, identifier)
            break


@task
def enqueue_with_stale_objects(action, instance):
    for obj in get_stale_objects(instance, [], all_relations=True):
        model = obj.__class__

        if is_polymorphic_child_model(model):
            model = get_polymorphic_parent_model(model)
            obj = model._default_manager.non_polymorphic().get(pk=obj.pk)

        enqueue(action, obj, model)


class CeleryHaystackSignalHandler(Original):
    def get_instance(self, model_class, pk, **kwargs):
        # Taken from the overriden method
        logger = self.get_logger(**kwargs)
        instance = None
        manager = model_class._default_manager
        if is_polymorphic_model(model_class):
            manager = manager.non_polymorphic()
        try:
            instance = manager.get(pk=pk)
        except model_class.DoesNotExist:
            logger.error("Couldn't load %s.%s.%s. Somehow it went missing?" %
                         (model_class._meta.app_label.lower(),
                          model_class._meta.object_name.lower(), pk))
        except model_class.MultipleObjectsReturned:
            logger.error("More than one object with pk %s. Oops?" % pk)
        return instance
