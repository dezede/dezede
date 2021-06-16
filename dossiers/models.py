from datetime import datetime
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
from common.utils.text import str_list_w_last


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


class DossierDEvenements(TreeModelMixin, PublishedModel):
    categorie = ForeignKey(
        CategorieDeDossiers, null=True, blank=True,
        related_name='dossiersdevenements', verbose_name=_('catégorie'),
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
    lieux = ManyToManyField(Lieu, blank=True, verbose_name=_('lieux'),
                            related_name='dossiers')
    oeuvres = ManyToManyField(Oeuvre, blank=True, verbose_name=_('œuvres'),
                              related_name='dossiers')
    individus = ManyToManyField(
        Individu, blank=True, verbose_name=_('individus'),
        related_name='dossiers',
    )
    circonstance = CharField(_('circonstance'), max_length=100, blank=True)
    evenements = ManyToManyField(Evenement, verbose_name=_('événements'),
                                 blank=True, related_name='dossiers')
    ensembles = ManyToManyField(Ensemble, verbose_name=_('ensembles'),
                                blank=True, related_name='dossiers')
    sources = ManyToManyField(Source, verbose_name=_('sources'), blank=True,
                              related_name='dossiers')
    saisons = ManyToManyField(Saison, verbose_name=_('saisons'), blank=True,
                              related_name=_('saisons'))

    objects = DossierDEvenementsManager()

    class Meta(object):
        verbose_name = _('dossier d’événements')
        verbose_name_plural = _('dossiers d’événements')
        ordering = ('path',)
        permissions = (('can_change_status', _('Peut changer l’état')),)

    def __str__(self):
        return strip_tags(self.html())

    def html(self):
        return mark_safe(self.titre)

    def link(self):
        return href(self.get_absolute_url(), smart_text(self))

    def short_link(self):
        return href(self.get_absolute_url(), self.titre_court or self.titre)

    def get_absolute_url(self):
        return reverse('dossierdevenements_detail', args=(self.slug,))

    def permalien(self):
        return reverse('dossierdevenements_permanent_detail', args=(self.pk,))

    def get_data_absolute_url(self):
        return reverse('dossierdevenements_data_detail', args=(self.slug,))

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
                lieux = self.lieux.all().get_descendants(include_self=True)
                kwargs['debut_lieu__in'] = lieux
            if self.oeuvres.exists():
                oeuvres = self.oeuvres.all().get_descendants(include_self=True)
                kwargs['programme__oeuvre__in'] = oeuvres
            individus = self.individus.all()
            if individus.exists():
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
            sources = self.sources.all()
            if sources.exists():
                kwargs['sources__in'] = sources
            saisons = self.saisons.all()
            if saisons.exists():
                kwargs['pk__in'] = saisons.evenements()
        if self.circonstance:
            kwargs['circonstance__icontains'] = self.circonstance
        if args or kwargs:
            self._evenement_queryset = Evenement.objects.filter(
                *args, **kwargs,
            ).distinct()
        else:
            self._evenement_queryset = Evenement.objects.none()
        return self._evenement_queryset
    get_queryset.short_description = _('ensemble de données')

    def get_count(self):
        return self.get_queryset().count()
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
        return str_list_w_last([a.html() for a in self.individus.all()])
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
