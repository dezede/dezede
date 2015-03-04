# coding: utf-8

from __future__ import unicode_literals
from datetime import datetime
from django.core.urlresolvers import reverse
from django.db.models import (
    CharField, DateField, ManyToManyField,
    TextField, permalink, PositiveSmallIntegerField, Q,
    ForeignKey, SlugField)
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from accounts.models import HierarchicUser
from libretto.models import Lieu, Oeuvre, Evenement, Individu, Ensemble, Source
from libretto.models.base import PublishedModel, PublishedManager, \
    CommonTreeManager, PublishedQuerySet, CommonTreeQuerySet
from common.utils.html import href
from common.utils.text import str_list_w_last


@python_2_unicode_compatible
class CategorieDeDossiers(PublishedModel):
    nom = CharField(max_length=75)
    position = PositiveSmallIntegerField(default=1)

    class Meta(object):
        ordering = ('position',)
        verbose_name = _('catégorie de dossiers')
        verbose_name_plural = _('catégories de dossiers')

    def __str__(self):
        return self.nom

    def get_children(self):
        return self.dossiersdevenements.all()


class DossierDEvenementsQuerySet(CommonTreeQuerySet, PublishedQuerySet):
    pass


class DossierDEvenementsManager(CommonTreeManager, PublishedManager):
    queryset_class = DossierDEvenementsQuerySet


# TODO: Dossiers de photos: présentation, contexte historique,
#       sources et protocole, et bibliographie indicative.
#       Les photos doivent pouvoir être classées par cote (ex: AJ13)
#       ou par thème (ex: censure, livret, etc).


@python_2_unicode_compatible
class DossierDEvenements(MPTTModel, PublishedModel):
    categorie = ForeignKey(
        CategorieDeDossiers, null=True, blank=True,
        related_name='dossiersdevenements', verbose_name=_('catégorie'),
        help_text=_('Attention, un dossier contenu dans un autre dossier '
                    'ne peut être dans une catégorie.'))
    titre = CharField(_('titre'), max_length=100)
    titre_court = CharField(_('titre court'), max_length=100, blank=True,
                            help_text=_('Utilisé pour le chemin de fer.'))
    # TODO: Ajouter accroche d'environ 150 caractères.
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', verbose_name=_('parent'))
    position = PositiveSmallIntegerField(_('position'), default=1)
    slug = SlugField(unique=True)

    # Métadonnées
    editeurs_scientifiques = ManyToManyField(
        'accounts.HierarchicUser', related_name='dossiers_d_evenements_edites',
        verbose_name=_('éditeurs scientifiques'))
    date_publication = DateField(_('date de publication'),
                                 default=datetime.now)
    publications = TextField(_('publication(s) associée(s)'), blank=True)
    developpements = TextField(_('développements envisagés'), blank=True)

    # Article
    presentation = TextField(_('présentation'))
    contexte = TextField(_('contexte historique'), blank=True)
    sources_et_protocole = TextField(_('sources et protocole'), blank=True)
    bibliographie = TextField(_('bibliographie indicative'), blank=True)

    # Sélecteurs
    debut = DateField(_('début'), blank=True, null=True)
    fin = DateField(_('fin'), blank=True, null=True)
    lieux = ManyToManyField(
        Lieu, blank=True, null=True, verbose_name=_('lieux'),
        related_name='dossiers')
    oeuvres = ManyToManyField(
        Oeuvre, blank=True, null=True, verbose_name=_('œuvres'),
        related_name='dossiers')
    auteurs = ManyToManyField(
        Individu, blank=True, null=True, verbose_name=_('auteurs'),
        related_name='dossiers')
    circonstance = CharField(_('circonstance'), max_length=100, blank=True)
    evenements = ManyToManyField(
        Evenement, verbose_name=_('événements'), blank=True, null=True,
        related_name='dossiers')
    ensembles = ManyToManyField(
        Ensemble, verbose_name=_('ensembles'), blank=True, null=True,
        related_name='dossiers')
    sources = ManyToManyField(
        Source, verbose_name=_('sources'), blank=True, null=True,
        related_name='dossiers')

    objects = DossierDEvenementsManager()

    class MPTTMeta(object):
        order_insertion_by = ('position',)

    class Meta(object):
        verbose_name = ungettext_lazy('dossier d’événements',
                                      'dossiers d’événements', 1)
        verbose_name_plural = ungettext_lazy('dossier d’événements',
                                             'dossiers d’événements', 2)
        ordering = ('tree_id', 'lft')
        permissions = (('can_change_status', _('Peut changer l’état')),)

    def __str__(self):
        return strip_tags(self.html())

    def html(self):
        return mark_safe(self.titre)

    def link(self):
        return href(self.get_absolute_url(), smart_text(self))

    def short_link(self):
        return href(self.get_absolute_url(), self.titre_court or self.titre)

    @permalink
    def get_absolute_url(self):
        return 'dossierdevenements_detail', (self.slug,)

    @permalink
    def permalien(self):
        return 'dossierdevenements_permanent_detail', (self.pk,)

    @permalink
    def get_data_absolute_url(self):
        return 'dossierdevenements_data_detail', (self.slug,)

    def get_queryset(self, dynamic=False):
        if hasattr(self, '_evenement_queryset'):
            return self._evenement_queryset
        if not dynamic and self.pk and self.evenements.exists():
            return self.evenements.all()
        args = []
        kwargs = {}
        if self.debut:
            kwargs['debut_date__gte'] = self.debut
        if self.fin:
            kwargs['debut_date__lte'] = self.fin
        if self.pk:
            if self.lieux.exists():
                lieux = self.lieux.non_polymorphic() \
                    .get_descendants(include_self=True)
                kwargs['debut_lieu__in'] = lieux
            if self.oeuvres.exists():
                oeuvres = self.oeuvres.get_descendants(include_self=True)
                kwargs['programme__oeuvre__in'] = oeuvres
            auteurs = self.auteurs.all()
            if auteurs.exists():
                kwargs['programme__oeuvre__auteurs__individu__in'] = auteurs
            ensembles = self.ensembles.all()
            if ensembles.exists():
                args.append(
                    Q(distribution__ensemble__in=ensembles)
                    | Q(programme__distribution__ensemble__in=ensembles))
            sources = self.sources.all()
            if sources.exists():
                kwargs['sources__in'] = sources
        if self.circonstance:
            kwargs['circonstance__icontains'] = self.circonstance
        if args or kwargs:
            self._evenement_queryset = Evenement.objects.filter(
                *args, **kwargs).distinct()
        else:
            self._evenement_queryset = Evenement.objects.none()
        return self._evenement_queryset
    get_queryset.short_description = _('ensemble de données')

    def get_count(self):
        qs = self.get_queryset()
        # TODO: Remove this check when switching to Django 1.7
        #       (see https://code.djangoproject.com/ticket/10181)
        if not qs.exists():
            return 0
        return qs.count()
    get_count.short_description = _('quantité de données sélectionnées')

    def get_queryset_url(self):
        url = reverse('evenements')
        request_kwargs = []
        if self.lieux.exists():
            request_kwargs.append('lieu=|%s|' % '|'.join([str(l.pk)
                                  for l in self.lieux.all()]))
        if self.oeuvres.exists():
            request_kwargs.append('oeuvre=|%s|' % '|'.join([str(o.pk)
                                  for o in self.oeuvres.all()]))
        if request_kwargs:
            url += '?' + '&'.join(request_kwargs)
        return url

    def lieux_html(self):
        return str_list_w_last([l.html() for l in self.lieux.all()])
    lieux_html.short_description = _('lieux')
    lieux_html.allow_tags = True

    def oeuvres_html(self):
        return str_list_w_last([o.titre_html() for o in self.oeuvres.all()])
    oeuvres_html.short_description = _('œuvres')
    oeuvres_html.allow_tags = True

    def auteurs_html(self):
        return str_list_w_last([a.html() for a in self.auteurs.all()])
    auteurs_html.short_description = _('auteurs')
    auteurs_html.allow_tags = True

    def ensembles_html(self):
        return str_list_w_last([e.html() for e in self.ensembles.all()])
    ensembles_html.short_description = _('ensembles')
    ensembles_html.allow_tags = True

    def get_contributors(self):
        return HierarchicUser.objects.filter(
            Q(pk__in=self.get_queryset().values_list('owner_id',
                                                     flat=True).distinct()) |
            Q(pk__in=self.get_queryset().values_list('sources__owner_id',
                                                     flat=True).distinct())
        ).order_by('last_name', 'first_name')
