from datetime import datetime
from functools import cached_property
from typing import Union

from django.db.models import (
    CharField, DateField, ManyToManyField,
    TextField, PositiveSmallIntegerField, Q,
    ForeignKey, SlugField, CASCADE)
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from tree.fields import PathField
from tree.models import TreeModelMixin

from accounts.models import HierarchicUser
from libretto.models import (Lieu, Oeuvre, Evenement, Individu, Ensemble,
                             Source, Saison)
from libretto.models.base import PublishedModel, PublishedManager, \
    CommonTreeManager, PublishedQuerySet, CommonTreeQuerySet
from common.utils.html import href


class CategorieDeDossiers(PublishedModel):
    nom = CharField(_('nom'), max_length=75)
    position = PositiveSmallIntegerField(_('position'), default=1)

    search_fields = ['nom']

    class Meta(PublishedModel.Meta):
        ordering = ('position',)
        verbose_name = _('catégorie de dossiers')
        verbose_name_plural = _('catégories de dossiers')

    def __str__(self):
        return self.nom

    def get_children(self):
        return self.dossiers.all()


class DossierQuerySet(CommonTreeQuerySet, PublishedQuerySet):
    pass


class DossierManager(CommonTreeManager, PublishedManager):
    queryset_class = DossierQuerySet


# TODO: Dossiers de photos: présentation, contexte historique,
#       sources et protocole, et bibliographie indicative.
#       Les photos doivent pouvoir être classées par cote (ex: AJ13)
#       ou par thème (ex: censure, livret, etc).


class Dossier(TreeModelMixin, PublishedModel):
    categorie = ForeignKey(
        CategorieDeDossiers, null=True, blank=True,
        related_name='dossiers', verbose_name=_('catégorie'),
        help_text=_('Attention, un dossier contenu dans un autre dossier '
                    'ne peut être dans une catégorie.'), on_delete=CASCADE)
    titre = CharField(_('titre'), max_length=100)
    titre_court = CharField(_('titre court'), max_length=100, blank=True,
                            help_text=_('Utilisé pour le chemin de fer.'))
    # TODO: Ajouter accroche d'environ 150 caractères.
    parent = ForeignKey('self', null=True, blank=True,
                        related_name='children', verbose_name=_('parent'),
                        on_delete=CASCADE)
    path = PathField(order_by=('position',), db_index=True)
    position = PositiveSmallIntegerField(_('position'), default=1)
    slug = SlugField(unique=True,
                     help_text=_('Personnaliser l’affichage du titre '
                                 'du dossier dans l’adresse URL.'))

    # Métadonnées
    editeurs_scientifiques = ManyToManyField(
        'accounts.HierarchicUser', related_name='dossiers_edites',
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

    objects = DossierManager()

    search_fields = ['titre', 'titre_court']

    class Meta(PublishedModel.Meta):
        verbose_name = _('dossier')
        verbose_name_plural = _('dossiers')
        ordering = ['path']
        permissions = (('can_change_status', _('Peut changer l’état')),)
        indexes = [
            *PathField.get_indexes('dossiers', 'path'),
            *PublishedModel.Meta.indexes,
        ]

    @property
    def specific(self) -> Union['DossierDEvenements']:  # TODO: + DossierDOeuvres.
        try:
            return self.dossierdevenements
        except DossierDEvenements.DoesNotExist:
            # TODO: Add DossierDOeuvres here.
            raise NotImplementedError('Unknown type of dossier!')

    def __str__(self):
        return strip_tags(self.html())

    def html(self):
        return mark_safe(self.titre)

    def link(self):
        return href(self.get_absolute_url(), smart_text(self))

    def short_link(self):
        return href(self.get_absolute_url(), self.titre_court or self.titre)

    def get_absolute_url(self):
        return reverse('dossier_detail', args=(self.slug,))

    def permalien(self):
        return reverse('dossier_permanent_detail', args=(self.pk,))

    def get_data_absolute_url(self):
        return reverse('dossier_data_detail', args=(self.slug,))

    @cached_property
    def queryset(self):
        return self.get_queryset(dynamic=False)

    @cached_property
    def dynamic_queryset(self):
        return self.get_queryset(dynamic=True)

    def get_queryset(self, dynamic=False):
        raise NotImplementedError

    def get_count(self):
        return self.queryset.count()
    get_count.short_description = _('quantité de données sélectionnées')

    @cached_property
    def contributors(self):
        contributor_ids = set()
        for owner_id, source_owner_id in self.queryset.values_list(
            'owner_id', 'sources__owner_id'
        ).distinct():
            contributor_ids.add(owner_id)
            contributor_ids.add(source_owner_id)
        return HierarchicUser.objects.filter(pk__in=contributor_ids)


class DossierDEvenements(Dossier):
    debut = DateField(_('début'), blank=True, null=True)
    fin = DateField(_('fin'), blank=True, null=True)
    lieux = ManyToManyField(Lieu, blank=True, verbose_name=_('lieux'),
                            related_name='dossiersdevenements')
    oeuvres = ManyToManyField(Oeuvre, blank=True, verbose_name=_('œuvres'),
                              related_name='dossiersdevenements')
    individus = ManyToManyField(
        Individu, blank=True, verbose_name=_('individus'),
        related_name='dossiersdevenements',
    )
    circonstance = CharField(_('circonstance'), max_length=100, blank=True)
    evenements = ManyToManyField(Evenement, verbose_name=_('événements'),
                                 blank=True, related_name='dossiersdevenements')
    ensembles = ManyToManyField(Ensemble, verbose_name=_('ensembles'),
                                blank=True, related_name='dossiersdevenements')
    sources = ManyToManyField(Source, verbose_name=_('sources'), blank=True,
                              related_name='dossiersdevenements')
    saisons = ManyToManyField(Saison, verbose_name=_('saisons'), blank=True,
                              related_name=_('dossiersdevenements'))

    class Meta(Dossier.Meta):
        verbose_name = _('dossier d’événements')
        verbose_name_plural = _('dossiers d’événements')
        indexes = []

    def get_queryset(self, dynamic=False):
        if not dynamic and self.pk and self.evenements.exists():
            return self.evenements.all()
        args = []
        kwargs = {}
        if self.debut:
            kwargs['debut_date__gte'] = self.debut
        if self.fin:
            kwargs['debut_date__lte'] = self.fin
        if self.pk:
            lieux = set(self.lieux.all().get_descendants(include_self=True))
            if lieux:
                kwargs['debut_lieu__in'] = lieux
            oeuvres = set(
                self.oeuvres.all().get_descendants(include_self=True)
            )
            if oeuvres:
                kwargs['programme__oeuvre__in'] = oeuvres
            individus = set(self.individus.values_list('pk', flat=True))
            if individus:
                args.append(
                    Q(programme__oeuvre__auteurs__individu__in=individus)
                    | Q(programme__distribution__individu__in=individus)
                    | Q(distribution__individu__in=individus)
                )
            if self.ensembles.exists():
                evenements = Evenement.objects.extra(where=("""
                id IN (
                    SELECT DISTINCT COALESCE(distribution.evenement_id, programme.evenement_id)
                    FROM dossiers_dossierdevenements_ensembles AS dossier_ensemble
                    INNER JOIN libretto_elementdedistribution AS distribution
                        ON (distribution.ensemble_id = dossier_ensemble.ensemble_id)
                    LEFT JOIN libretto_elementdeprogramme AS programme
                        ON (programme.id = distribution.element_de_programme_id)
                    WHERE dossier_ensemble.dossierdevenements_id = %s
                )""",), params=(self.pk,))
                kwargs['pk__in'] = evenements
            sources = set(self.sources.values_list('pk', flat=True))
            if sources:
                kwargs['sources__in'] = sources
            saisons = self.saisons.all()
            if saisons.exists():
                kwargs['pk__in'] = saisons.evenements()
        if self.circonstance:
            kwargs['circonstance__icontains'] = self.circonstance
        if args or kwargs:
            return Evenement.objects.filter(
                *args, **kwargs,
            ).distinct()
        return Evenement.objects.none()
