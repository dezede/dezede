# coding: utf-8

from __future__ import unicode_literals
from django.db.models import CharField, TextField, Manager, Model
from django.db.models.query import QuerySet
from django.dispatch import receiver
from tinymce.models import HTMLField
from .settings import SIGNALS
from .utils import replace


__all__ = ('TypographicModel', 'TypographicManager', 'TypographicQuerySet',
           'replace_in_kwargs', 'REPLACE_FIELDS')


# Champs dans lesquels effectuer les remplacements typographiques.
REPLACE_FIELDS = (CharField, TextField, HTMLField)


def replace_in_kwargs(obj, kwargs_dict):
    """
    Renvoie kwargs_dict avec remplacements typographiques.

    Si une clé de kwargs_dict est un nom de champ d’obj
    et que la classe de ce champ est dans REPLACE_FIELDS,
    effectue les remplacements dans la valeur du kwarg.
    """
    fields = obj._meta.fields
    field_names = [field.attname for field in fields
                   if field.__class__ in REPLACE_FIELDS]
    for k, v in kwargs_dict.items():
        if k.split('__')[0] in field_names:
            kwargs_dict[k] = replace(v)


class TypographicQuerySet(QuerySet):
    """
    QuerySet personnalisé pour chercher
    des objets avec remplacements typographiques.
    """

    def _filter_or_exclude(self, negate, *args, **kwargs):
        replace_in_kwargs(self.model, kwargs)
        return super(TypographicQuerySet, self)._filter_or_exclude(
            negate, *args, **kwargs)


class TypographicManager(Manager):
    """
    Manager personnalisé pour utiliser TypographicQuerySet par défaut.
    """

    # TODO: Implement get_empty_query_set.
    def get_query_set(self):
        return TypographicQuerySet(self.model, using=self._db)


class TypographicModel(Model):
    objects = TypographicManager()

    class Meta(object):
        abstract = True


@receiver(SIGNALS['pre_init'])
def pre_init_replace(sender, **kwargs):
    replace_in_kwargs(sender, kwargs['kwargs'])


@receiver(SIGNALS['pre_save'])
def pre_save_replace(sender, **kwargs):
    replace_in_kwargs(sender, kwargs['instance'].__dict__)
