from datetime import datetime
from functools import cached_property

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db.models import (
    CharField, DateField, ImageField, TextField, PositiveSmallIntegerField,
    SlugField, ForeignKey, ManyToManyField, Q, CASCADE,
)
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from tree.fields import PathField
from tree.models import TreeModelMixin
from wagtail.search.index import AutocompleteField, Indexed, RelatedFields, SearchField

from accounts.models import HierarchicUser
from libretto.models import (Lieu, Oeuvre, Evenement, Individu, Ensemble,
                             Source, Saison, GenreDOeuvre, TypeDeSource)
from libretto.models.base import PublishedModel, PublishedManager, \
    CommonTreeManager, PublishedQuerySet, CommonTreeQuerySet
from common.utils.html import href


KIND_EVENEMENTS = 'evenements'
KIND_OEUVRES = 'oeuvres'
KIND_SOURCES = 'sources'

KIND_CHOICES = (
    (KIND_EVENEMENTS, _('événements')),
    (KIND_OEUVRES, _('œuvres')),
    (KIND_SOURCES, _('sources')),
)

# Canonical presentation order of the kinds, whatever the stored order.
KINDS_ORDER = (KIND_EVENEMENTS, KIND_OEUVRES, KIND_SOURCES)


class CategorieDeDossiers(Indexed, PublishedModel):
    nom = CharField(_('nom'), max_length=75)
    position = PositiveSmallIntegerField(_('position'), default=1)

    search_fields = [
        SearchField('title', boost=10),
        AutocompleteField('title'),
    ]

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


class Dossier(Indexed, TreeModelMixin, PublishedModel):
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
    image_couverture = ImageField(_('image de couverture'), upload_to='dossiers/',
                                  null=True, blank=True)

    # Article
    presentation = TextField(_('présentation'))
    contexte = TextField(_('contexte historique'), blank=True)
    sources_et_protocole = TextField(_('sources et protocole'), blank=True)
    bibliographie = TextField(_('bibliographie indicative'), blank=True)

    # Types de données présentés par le dossier (événements/œuvres/sources).
    # Chaque type actif applique les critères partagés ci-dessous à son propre
    # modèle et dispose de sa propre sélection manuelle.
    types_de_donnees = ArrayField(
        CharField(max_length=20, choices=KIND_CHOICES),
        default=list, blank=True, verbose_name=_('types de données'),
        help_text=_('Types de données présentés par ce dossier.'))

    # Critères partagés de la sélection dynamique. Chaque type actif les
    # interprète sur son modèle : par exemple `debut`/`fin` filtrent la date
    # des événements, la date de création des œuvres ou la date des sources.
    debut = DateField(_('début'), blank=True, null=True)
    fin = DateField(_('fin'), blank=True, null=True)
    lieux = ManyToManyField(Lieu, blank=True, verbose_name=_('lieux'),
                            related_name='dossiers')
    individus = ManyToManyField(Individu, blank=True,
                                verbose_name=_('individus'),
                                related_name='dossiers')
    ensembles = ManyToManyField(Ensemble, blank=True,
                                verbose_name=_('ensembles'),
                                related_name='dossiers')
    # Critères ne s’appliquant qu’à certains types : genres (œuvres),
    # types de sources (sources), circonstance et saisons (événements).
    genres = ManyToManyField(GenreDOeuvre, blank=True,
                             verbose_name=_('genres d’œuvre'),
                             related_name='dossiers')
    types_de_sources = ManyToManyField(TypeDeSource, blank=True,
                                       verbose_name=_('types de source'),
                                       related_name='dossiers')
    circonstance = CharField(_('circonstance'), max_length=100, blank=True)
    saisons = ManyToManyField(Saison, blank=True, verbose_name=_('saisons'),
                              related_name='dossiers')
    # Critères sur les œuvres et sources elles-mêmes ; à distinguer des
    # sélections manuelles `oeuvres` et `sources` ci-dessous.
    filtre_oeuvres = ManyToManyField(Oeuvre, blank=True,
                                     verbose_name=_('œuvres'),
                                     related_name='dossiers_filtre')
    filtre_sources = ManyToManyField(Source, blank=True,
                                     verbose_name=_('sources'),
                                     related_name='dossiers_filtre')

    # Sélection manuelle par type. Lorsqu’elle est remplie pour un type,
    # elle remplace la sélection dynamique de ce type.
    evenements = ManyToManyField(Evenement, blank=True,
                                 verbose_name=_('événements'),
                                 related_name='dossiers')
    oeuvres = ManyToManyField(Oeuvre, blank=True, verbose_name=_('œuvres'),
                              related_name='dossiers')
    sources = ManyToManyField(Source, blank=True, verbose_name=_('sources'),
                              related_name='dossiers')

    objects = DossierManager()

    search_fields = [
        SearchField('title', boost=10),
        SearchField('titre_court', boost=10),
        RelatedFields('parent', [
            SearchField('title'),
            SearchField('titre_court'),
            AutocompleteField('title'),
            AutocompleteField('titre_court'),
        ]),
        SearchField('presentation', boost=0.1),
        SearchField('contexte', boost=0.1),
        SearchField('sources_et_protocole', boost=0.1),
        SearchField('bibliographie', boost=0.1),
        AutocompleteField('title'),
        AutocompleteField('titre_court'),
    ]

    class Meta(PublishedModel.Meta):
        verbose_name = _('dossier')
        verbose_name_plural = _('dossiers')
        ordering = ['path']
        permissions = (('can_change_status', _('Peut changer l’état')),)
        indexes = PathField.get_indexes('dossiers', 'path')

    def __str__(self):
        return strip_tags(self.html())

    def html(self):
        return mark_safe(self.titre)

    def link(self):
        return href(self.get_absolute_url(), str(self))

    def short_link(self):
        return href(self.get_absolute_url(), self.titre_court or self.titre)

    def get_absolute_url(self):
        return reverse('dossier_detail', args=(self.slug,))

    def permalien(self):
        return reverse('dossier_permanent_detail', args=(self.pk,))

    def get_data_absolute_url(self, kind=None):
        if kind is None:
            kinds = self.active_kinds
            kind = kinds[0] if kinds else KIND_EVENEMENTS
        return reverse('dossier_data_detail', args=(self.slug, kind))

    @property
    def active_kinds(self):
        return [kind for kind in KINDS_ORDER if kind in self.types_de_donnees]

    def has_kind(self, kind):
        return kind in self.types_de_donnees

    def kind_tabs(self):
        """Template-facing description of each active kind: its label,
        queryset, and per-kind URLs (data list + optional visualisations
        page), for the tab bars and the PDF export."""
        labels = dict(KIND_CHOICES)
        multiple = len(self.active_kinds) > 1
        tabs = []
        for kind in self.active_kinds:
            has_stats = kind in (KIND_EVENEMENTS, KIND_OEUVRES)
            tabs.append({
                'kind': kind,
                'label': labels[kind],
                'queryset': self.queryset_for(kind),
                'data_url': self.get_data_absolute_url(kind),
                'stats_url': (
                    reverse('dossier_stats_detail', args=(self.slug, kind))
                    if has_stats else None),
                'stats_label': (_('Visualisations (%s)') % labels[kind]
                                if multiple else _('Visualisations')),
            })
        return tabs

    @cached_property
    def _querysets(self):
        return {}

    def queryset_for(self, kind):
        """Static-or-dynamic selection of ``kind``, cached per kind."""
        if kind not in self._querysets:
            self._querysets[kind] = self.get_queryset(kind)
        return self._querysets[kind]

    def get_queryset(self, kind, dynamic=False, criteria=None):
        if criteria is None and self.pk:
            criteria = self.criteria
        if kind == KIND_EVENEMENTS:
            return self._get_evenements_queryset(dynamic=dynamic,
                                                 criteria=criteria)
        if kind == KIND_OEUVRES:
            return self._get_oeuvres_queryset(dynamic=dynamic,
                                              criteria=criteria)
        if kind == KIND_SOURCES:
            return self._get_sources_queryset(dynamic=dynamic,
                                              criteria=criteria)
        raise ValueError(f'Unknown kind of dossier data: {kind!r}')

    def get_count(self, kind):
        # Count over the distinct pks only: counting the queryset directly
        # would wrap a `SELECT DISTINCT <every column>` subquery, an order of
        # magnitude slower on the big libretto tables.
        return self.queryset_for(kind).values('pk').count()

    def counts(self):
        return {kind: self.get_count(kind) for kind in self.active_kinds}

    def get_counts_display(self):
        labels = dict(KIND_CHOICES)
        return ' · '.join(f'{count} {labels[kind]}'
                          for kind, count in self.counts().items())
    get_counts_display.short_description = \
        _('quantité de données sélectionnées')

    @staticmethod
    def _descendants_pks(manager, model):
        """Pks of the criterion's objects and all their tree descendants,
        or an empty list — without running the (whole-table) descendants query
        when the criterion is empty."""
        pks = list(manager.values_list('pk', flat=True))
        if not pks:
            return []
        return list(model.objects.filter(pk__in=pks)
                    .get_descendants(include_self=True)
                    .values_list('pk', flat=True))

    def get_criteria(self):
        """The dynamic-selection criteria as plain pk lists (tree criteria
        already expanded to their descendants), the shape the queryset
        builders consume. ``dossiers.rest.batch_criteria`` builds the same
        dicts for many dossiers in a fixed number of queries."""
        return {
            'lieux': self._descendants_pks(self.lieux, Lieu),
            'oeuvres': self._descendants_pks(self.filtre_oeuvres, Oeuvre),
            'individus': list(self.individus.values_list('pk', flat=True)),
            'ensembles': list(self.ensembles.values_list('pk', flat=True)),
            'sources': list(self.filtre_sources.values_list('pk', flat=True)),
            'saisons': list(self.saisons.values_list('pk', flat=True)),
            'genres': list(self.genres.values_list('pk', flat=True)),
            'types_de_sources': list(
                self.types_de_sources.values_list('pk', flat=True)),
        }

    @cached_property
    def criteria(self):
        return self.get_criteria()

    def _get_evenements_queryset(self, dynamic=False, criteria=None):
        if not dynamic and self.pk and self.evenements.exists():
            return self.evenements.all()
        args = []
        kwargs = {}
        if self.debut:
            kwargs['debut_date__gte'] = self.debut
        if self.fin:
            kwargs['debut_date__lte'] = self.fin
        if criteria:
            if criteria['lieux']:
                kwargs['debut_lieu__in'] = criteria['lieux']
            if criteria['oeuvres']:
                # Semi-jointures (sous-requêtes d'ids, mêmes chemins de
                # recherche) plutôt que des jointures : la requête externe
                # reste sans jointure, ce qui évite au COUNT de dédupliquer
                # des lignes larges multipliées par les LEFT JOIN.
                args.append(Q(pk__in=Evenement.objects.filter(
                    programme__oeuvre__in=criteria['oeuvres']).values('pk')))
            individus = criteria['individus']
            if individus:
                args.append(
                    Q(pk__in=Evenement.objects.filter(
                        programme__oeuvre__auteurs__individu__in=individus,
                    ).values('pk'))
                    | Q(pk__in=Evenement.objects.filter(
                        programme__distribution__individu__in=individus,
                    ).values('pk'))
                    | Q(pk__in=Evenement.objects.filter(
                        distribution__individu__in=individus,
                    ).values('pk'))
                )
            if criteria['ensembles']:
                evenements = Evenement.objects.extra(where=("""
                id IN (
                    SELECT DISTINCT COALESCE(distribution.evenement_id, programme.evenement_id)
                    FROM dossiers_dossier_ensembles AS dossier_ensemble
                    INNER JOIN libretto_elementdedistribution AS distribution
                        ON (distribution.ensemble_id = dossier_ensemble.ensemble_id)
                    LEFT JOIN libretto_elementdeprogramme AS programme
                        ON (programme.id = distribution.element_de_programme_id)
                    WHERE dossier_ensemble.dossier_id = %s
                )""",), params=(self.pk,))
                kwargs['pk__in'] = evenements
            # Kept as a direct join (not a semi-jointure): its alias is
            # reused by `contributors`, which must only see the owners of the
            # *filtered* sources.
            if criteria['sources']:
                kwargs['sources__in'] = criteria['sources']
            if criteria['saisons']:
                kwargs['pk__in'] = Saison.objects.filter(
                    pk__in=criteria['saisons']).evenements()
        if self.circonstance:
            kwargs['circonstance__icontains'] = self.circonstance
        if args or kwargs:
            return Evenement.objects.filter(
                *args, **kwargs,
            ).distinct()
        return Evenement.objects.none()

    def _get_oeuvres_queryset(self, dynamic=False, criteria=None):
        if not dynamic and self.pk and self.oeuvres.exists():
            return self.oeuvres.all()
        args = []
        kwargs = {
            'extrait_de__isnull': True,
        }
        if self.debut:
            kwargs['creation_date__gte'] = self.debut
        if self.fin:
            kwargs['creation_date__lte'] = self.fin
        if criteria:
            if criteria['lieux']:
                kwargs['creation_lieu__in'] = criteria['lieux']
            if criteria['genres']:
                kwargs['genre__in'] = criteria['genres']
            individus = criteria['individus']
            if individus:
                # Semi-jointures, comme pour les événements ci-dessus.
                args.append(
                    Q(pk__in=Oeuvre.objects.filter(
                        auteurs__individu__in=individus).values('pk'))
                    | Q(pk__in=Oeuvre.objects.filter(
                        dedicataires__in=individus).values('pk'))
                )
            if criteria['ensembles']:
                args.append(Q(pk__in=Oeuvre.objects.filter(
                    auteurs__ensemble__in=criteria['ensembles']).values('pk')))
            # Kept as a direct join (not a semi-jointure): its alias is reused
            # by `contributors`, which must only see the owners of the
            # *filtered* sources.
            if criteria['sources']:
                kwargs['sources__in'] = criteria['sources']
            # Le critère œuvres restreint ici les œuvres elles-mêmes
            # (avec leur descendance).
            if criteria['oeuvres']:
                kwargs['pk__in'] = criteria['oeuvres']
        if args or kwargs:
            return Oeuvre.objects.filter(
                *args, **kwargs,
            ).distinct()
        return Oeuvre.objects.none()

    def _get_sources_queryset(self, dynamic=False, criteria=None):
        if not dynamic and self.pk and self.sources.exists():
            return self.sources.all()
        args = []
        kwargs = {}
        # Source.date is the ancrage date (SpaceTimeFields named 'ancrage',
        # whose empty prefix yields the bare `date` field).
        if self.debut:
            kwargs['date__gte'] = self.debut
        if self.fin:
            kwargs['date__lte'] = self.fin
        if criteria:
            if criteria['types_de_sources']:
                kwargs['type__in'] = criteria['types_de_sources']
            if criteria['lieux']:
                # Semi-jointures, comme pour les événements ci-dessus.
                args.append(Q(pk__in=Source.objects.filter(
                    lieux__in=criteria['lieux']).values('pk')))
            if criteria['oeuvres']:
                args.append(Q(pk__in=Source.objects.filter(
                    oeuvres__in=criteria['oeuvres']).values('pk')))
            if criteria['individus']:
                args.append(Q(pk__in=Source.objects.filter(
                    individus__in=criteria['individus']).values('pk')))
            if criteria['ensembles']:
                args.append(Q(pk__in=Source.objects.filter(
                    ensembles__in=criteria['ensembles']).values('pk')))
            # Le critère sources restreint ici les sources elles-mêmes.
            if criteria['sources']:
                kwargs['pk__in'] = criteria['sources']
        if args or kwargs:
            return Source.objects.filter(*args, **kwargs).distinct()
        return Source.objects.none()

    @cached_property
    def contributors(self):
        contributor_ids = set()
        for kind in self.active_kinds:
            queryset = self.queryset_for(kind)
            if kind == KIND_SOURCES:
                # Each source is its own contributor via `owner_id`; joining
                # `sources__owner_id` would make no sense here since the
                # queryset items *are* sources.
                contributor_ids.update(
                    queryset.values_list('owner_id', flat=True))
            else:
                for owner_id, source_owner_id in queryset.values_list(
                    'owner_id', 'sources__owner_id'
                ).distinct():
                    contributor_ids.add(owner_id)
                    contributor_ids.add(source_owner_id)
        return HierarchicUser.objects.filter(pk__in=contributor_ids)
