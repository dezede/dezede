# coding: utf-8

from __future__ import unicode_literals
from django.db.models import CharField, ForeignKey, ManyToManyField, \
                             FloatField, permalink
from django.template.defaultfilters import capfirst
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from ..templatetags.extras import abbreviate
from .common import CommonModel, LOWER_MSG, PLURAL_MSG, calc_pluriel,\
                    UniqueSlugModel, AutoriteManager, AutoriteModel
from .functions import ex, href


__all__ = (b'Profession', b'Devise', b'Engagement', b'TypeDePersonnel',
           b'Personnel')


class ProfessionManager(TreeManager, AutoriteManager):
    pass


@python_2_unicode_compatible
class Profession(MPTTModel, AutoriteModel, UniqueSlugModel):
    nom = CharField(_('nom'), max_length=200, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
        help_text=PLURAL_MSG)
    nom_feminin = CharField(_('nom (au féminin)'), max_length=230, blank=True,
        help_text=_('Ne préciser que s’il est différent du nom.'))
    parent = TreeForeignKey('Profession', blank=True, null=True, db_index=True,
                            related_name='enfant', verbose_name=_('parent'))

    objects = ProfessionManager()

    class Meta(object):
        verbose_name = ungettext_lazy('profession', 'professions', 1)
        verbose_name_plural = ungettext_lazy('profession', 'professions', 2)
        ordering = ('nom',)
        app_label = 'catalogue'

    @permalink
    def get_absolute_url(self):
        return b'profession_detail', (self.slug,)

    @permalink
    def permalien(self):
        return b'profession_permanent_detail', (self.pk,)

    def pretty_link(self):
        return self.html(caps=True)

    def link(self):
        return self.html()

    def short_link(self):
        return self.short_html()

    def pluriel(self):
        return calc_pluriel(self)

    def feminin(self):
        f = self.nom_feminin
        return f or self.nom

    def pretty_gendered(self, titre='M', tags=True):
        return self.gendered(titre=titre, tags=tags, caps=True)

    def gendered(self, titre='M', tags=True, caps=False):
        return self.html(tags, caps=caps, feminin=titre != 'M')

    def html(self, tags=True, short=False, caps=False, feminin=False):
        nom = self.feminin() if feminin else self.nom
        if caps:
            nom = capfirst(nom)
        if short:
            nom = abbreviate(nom, min_vowels=1, min_len=4, tags=tags)
        url = '' if not tags else self.get_absolute_url()
        out = href(url, nom, tags)
        return out

    def short_html(self, tags=True):
        return self.html(tags, short=True)

    def __hash__(self):
        return hash(self.nom)

    def __str__(self):
        return capfirst(self.html(tags=False))

    @staticmethod
    def autocomplete_search_fields():
        return 'nom__icontains', 'nom_pluriel__icontains',


@python_2_unicode_compatible
class Devise(CommonModel):
    """
    Modélisation naïve d’une unité monétaire.
    """
    nom = CharField(max_length=200, blank=True, help_text=ex(_('euro')),
        unique=True, db_index=True)
    symbole = CharField(max_length=10, help_text=ex(_('€')), unique=True,
                        db_index=True)

    class Meta(object):
        verbose_name = ungettext_lazy('devise', 'devises', 1)
        verbose_name_plural = ungettext_lazy('devise', 'devises', 2)
        app_label = 'catalogue'

    def __str__(self):
        if self.nom:
            return self.nom
        return self.symbole


@python_2_unicode_compatible
class Engagement(CommonModel):
    individus = ManyToManyField('Individu', related_name='engagements',
                                db_index=True)
    profession = ForeignKey('Profession', related_name='engagements',
                            db_index=True)
    salaire = FloatField(blank=True, null=True, db_index=True)
    devise = ForeignKey('Devise', blank=True, null=True, db_index=True,
        related_name='engagements')

    class Meta(object):
        verbose_name = ungettext_lazy('engagement', 'engagements', 1)
        verbose_name_plural = ungettext_lazy('engagement', 'engagements', 2)
        app_label = 'catalogue'

    def __str__(self):
        return self.profession.nom


@python_2_unicode_compatible
class TypeDePersonnel(CommonModel):
    nom = CharField(max_length=100, unique=True, db_index=True)

    class Meta(object):
        verbose_name = ungettext_lazy('type de personnel',
                                      'types de personnel', 1)
        verbose_name_plural = ungettext_lazy('type de personnel',
                                             'types de personnel', 2)
        ordering = ('nom',)
        app_label = 'catalogue'

    def __str__(self):
        return self.nom


@python_2_unicode_compatible
class Personnel(CommonModel):
    type = ForeignKey('TypeDePersonnel', related_name='personnels',
                      db_index=True)
    saison = ForeignKey('Saison', related_name='personnels', db_index=True)
    engagements = ManyToManyField('Engagement', related_name='personnels',
                                  db_index=True)

    class Meta(object):
        verbose_name = ungettext_lazy('personnel', 'personnels', 1)
        verbose_name_plural = ungettext_lazy('personnel', 'personnels', 2)
        app_label = 'catalogue'

    def __str__(self):
        return unicode(self.type) + unicode(self.saison)
