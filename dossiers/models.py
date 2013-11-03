# coding: utf-8

from __future__ import unicode_literals
from datetime import datetime
from django.core.urlresolvers import reverse
from django.db.models import CharField, DateField, ManyToManyField, \
                             TextField, permalink, PositiveSmallIntegerField
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.translation import ungettext_lazy
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from accounts.models import HierarchicUser
from cache_tools import cached_ugettext_lazy as _
from libretto.models import Lieu, Oeuvre, Evenement, Individu
from libretto.models.common import PublishedModel, PublishedManager, \
    CommonTreeManager, PublishedQuerySet, CommonTreeQuerySet
from libretto.models.functions import str_list_w_last, href


class DossierDEvenementsQuerySet(CommonTreeQuerySet, PublishedQuerySet):
    pass


class DossierDEvenementsManager(CommonTreeManager, PublishedManager):
    queryset_class = DossierDEvenementsQuerySet


# TODO: Créer des catégories de dossiers.


@python_2_unicode_compatible
class DossierDEvenements(MPTTModel, PublishedModel):
    titre = CharField(_('titre'), max_length=100)
    titre_court = CharField(_('titre court'), max_length=100, blank=True,
                            help_text=_('Utilisé pour le chemin de fer.'))
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', verbose_name=_('parent'))
    position = PositiveSmallIntegerField(_('position'), default=1)

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
    contexte = TextField(_('contexte historique'))
    sources = TextField(_('sources et protocole'))
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
        return self.titre

    def link(self):
        return href(self.get_absolute_url(), smart_text(self))

    @permalink
    def get_absolute_url(self):
        return 'dossierdevenements_detail', (self.pk,)

    @permalink
    def get_data_absolute_url(self):
        return 'dossierdevenements_data_detail', (self.pk,)

    def get_queryset(self, dynamic=False):
        if not dynamic and self.pk and self.evenements.exists():
            return self.evenements.all()
        kwargs = {}
        if self.debut:
            kwargs['ancrage_debut__date__gte'] = self.debut
        if self.fin:
            kwargs['ancrage_debut__date__lte'] = self.fin
        if self.pk:
            if self.lieux.exists():
                lieux = self.lieux.non_polymorphic() \
                    .get_descendants(include_self=True)
                kwargs['ancrage_debut__lieu__in'] = lieux
            if self.oeuvres.exists():
                oeuvres = self.oeuvres.get_descendants(include_self=True)
                kwargs['programme__oeuvre__in'] = oeuvres
            auteurs = self.auteurs.all()
            if auteurs:
                kwargs['programme__oeuvre__auteurs__individu__in'] = auteurs
        if self.circonstance:
            kwargs['circonstance__icontains'] = self.circonstance
        if kwargs:
            return Evenement.objects.filter(**kwargs).distinct()
        return Evenement.objects.none()
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
        return str_list_w_last([a.html() for a in self.auteurs.all()])
    auteurs_html.short_description = _('auteurs')
    auteurs_html.allow_tags = True

    def get_contributors(self):
        return HierarchicUser.objects.exclude(
            pk__in=self.editeurs_scientifiques.values_list('pk', flat=True)
        ).filter(
            pk__in=self.get_queryset().values_list('owner_id', flat=True))
