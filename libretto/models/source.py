# coding: utf-8

from __future__ import unicode_literals
from django.contrib.contenttypes.generic import GenericRelation
from django.db.models import (
    CharField, ForeignKey, ManyToManyField, permalink, PROTECT, URLField)
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import (
    ungettext_lazy, ugettext, ugettext_lazy as _)
from tinymce.models import HTMLField
from .base import (
    CommonModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, calc_pluriel,
    SlugModel, PublishedManager, PublishedQuerySet, OrderedDefaultDict,
    AncrageSpatioTemporel, Fichier)
from .functions import (ex, cite, href, small, str_list, hlp)
from typography.models import TypographicModel


__all__ = (
    b'TypeDeSource', b'Source', b'SourceEvenement', b'SourceOeuvre',
    b'SourceIndividu', b'SourceEnsemble', b'SourceLieu', b'SourcePartie'
)


@python_2_unicode_compatible
class TypeDeSource(CommonModel, SlugModel):
    nom = CharField(_('nom'), max_length=200, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
                            db_index=True, help_text=PLURAL_MSG)
    # TODO: Ajouter un classement et changer ordering en conséquence.

    class Meta(object):
        verbose_name = ungettext_lazy('type de source', 'types de source', 1)
        verbose_name_plural = ungettext_lazy('type de source',
                                             'types de source', 2)
        ordering = ('slug',)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('sources',)
        return ()

    def pluriel(self):
        return calc_pluriel(self)

    def __str__(self):
        return self.nom


class SourceQuerySet(PublishedQuerySet):
    def group_by_type(self):
        sources = OrderedDefaultDict()
        for source in self:
            sources[source.type].append(source)
        return sources.items()

    def prefetch(self):
        fichiers = Fichier._meta.db_table
        sources = Source._meta.db_table
        return self.select_related('type').extra(select={
            '_has_others':
            'EXISTS (SELECT 1 FROM %s WHERE source_id = %s.id AND type = %s)'
            % (fichiers, sources, Fichier.OTHER),
            '_has_images':
            'EXISTS (SELECT 1 FROM %s WHERE source_id = %s.id AND type = %s)'
            % (fichiers, sources, Fichier.IMAGE),
            '_has_audios':
            'EXISTS (SELECT 1 FROM %s WHERE source_id = %s.id AND type = %s)'
            % (fichiers, sources, Fichier.AUDIO),
            '_has_videos':
            'EXISTS (SELECT 1 FROM %s WHERE source_id = %s.id AND type = %s)'
            % (fichiers, sources, Fichier.VIDEO)})


class SourceManager(PublishedManager):
    queryset_class = SourceQuerySet

    def group_by_type(self):
        return self.get_queryset().group_by_type()

    def prefetch(self):
        return self.get_queryset().prefetch()


@python_2_unicode_compatible
class Source(AutoriteModel):
    type = ForeignKey('TypeDeSource', related_name='sources', db_index=True,
                      help_text=ex(_('compte rendu')), verbose_name=_('type'),
                      on_delete=PROTECT)
    titre = CharField(_('titre'), max_length=200, blank=True, db_index=True,
                      help_text=ex(_('Journal de Rouen')))
    legende = CharField(_('légende'), max_length=600, blank=True)

    ancrage = AncrageSpatioTemporel(has_heure=False, has_lieu=False)
    numero = CharField(_('numéro'), max_length=50, blank=True, db_index=True,
                       help_text=_('Sans « № ». Exemple : « 52 »'))
    folio = CharField(_('folio'), max_length=10, blank=True)
    page = CharField(_('page'), max_length=10, blank=True, db_index=True,
                     help_text=_('Sans « p. ». Exemple : « 3 »'))
    lieu_conservation = CharField(_('lieu de conservation'), max_length=50,
                                  blank=True, db_index=True)
    cote = CharField(_('cote'), max_length=35, blank=True, db_index=True)
    url = URLField(blank=True,
                   help_text=_('Adresse de référence externe à Dezède.'))

    transcription = HTMLField(_('transcription'), blank=True,
        help_text=_('Recopié tel quel, avec les fautes d’orthographe suivies '
                    'de « [<em>sic</em>] » le cas échéant.'))

    auteurs = GenericRelation('Auteur')

    evenements = ManyToManyField('Evenement', through='SourceEvenement',
                                 related_name='sources')
    oeuvres = ManyToManyField('Oeuvre', through='SourceOeuvre',
                              related_name='sources')
    individus = ManyToManyField('Individu', through='SourceIndividu',
                                related_name='sources')
    ensembles = ManyToManyField('Ensemble', through='SourceEnsemble',
                                related_name='sources')
    lieux = ManyToManyField('Lieu', through='SourceLieu',
                            related_name='sources')
    parties = ManyToManyField('Partie', through='SourcePartie',
                              related_name='sources')

    objects = SourceManager()

    class Meta(object):
        verbose_name = ungettext_lazy('source', 'sources', 1)
        verbose_name_plural = ungettext_lazy('source', 'sources', 2)
        ordering = ('date', 'titre', 'numero', 'page',
                    'lieu_conservation', 'cote')
        app_label = 'libretto'
        permissions = (('can_change_status', _('Peut changer l’état')),)

    def __str__(self):
        return strip_tags(self.html(False))

    @permalink
    def get_absolute_url(self):
        return b'source_permanent_detail', (self.pk,)

    def permalien(self):
        return self.get_absolute_url()

    def link(self):
        return self.html()
    link.short_description = _('Lien')
    link.allow_tags = True

    def auteurs_html(self, tags=True):
        return self.auteurs.html(tags)

    def no(self):
        return ugettext('n° %s') % self.numero

    def f(self):
        return ugettext('f. %s') % self.folio

    def p(self):
        return ugettext('p. %s') % self.page

    def html(self, tags=True, pretty_title=False):
        url = None if not tags else self.get_absolute_url()
        conservation = hlp(self.lieu_conservation,
                           'Lieu de conservation', tags)
        if self.ancrage.date or self.ancrage.date_approx:
            ancrage = hlp(self.ancrage.html(tags, caps=False), ugettext('date'))
        else:
            ancrage = None
        if self.cote:
            conservation += ', ' + hlp(self.cote, 'cote', tags)
        if self.titre:
            l = [cite(self.titre, tags)]
            if self.numero:
                l.append(self.no())
            if ancrage is not None:
                l.append(ancrage)
            if self.folio:
                l.append(hlp(self.f(), ugettext('folio'), tags))
            if self.page:
                l.append(hlp(self.p(), ugettext('page'), tags))
            if self.lieu_conservation:
                l[-1] += ' (%s)' % conservation
        else:
            l = [conservation]
            if ancrage is not None:
                l.append(ancrage)
        l = (l[0], small(str_list(l[1:]), tags=tags)) if pretty_title else l
        out = str_list(l)
        return mark_safe(href(url, out, tags))
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def pretty_title(self):
        return self.html(pretty_title=True)

    def has_events(self):
        if hasattr(self, '_has_events'):
            return self._has_events
        return self.evenements.exists()
    has_events.short_description = _('événements')
    has_events.boolean = True
    has_events.admin_order_field = 'evenements'

    def has_program(self):
        if hasattr(self, '_has_program'):
            return self._has_program
        return self.evenements.with_program().exists()
    has_program.short_description = _('programme')
    has_program.boolean = True

    def has_fichiers(self):
        attrs = ('_has_others', '_has_images', '_has_audios', '_has_videos')
        if all(hasattr(self, attr) for attr in attrs):
            return any(getattr(self, attr) for attr in attrs)
        return self.fichiers.exists()

    def has_others(self):
        if hasattr(self, '_has_others'):
            return self._has_others
        return self.fichiers.others().exists()

    def has_images(self):
        if hasattr(self, '_has_images'):
            return self._has_images
        return self.fichiers.images().exists()

    def has_audios(self):
        if hasattr(self, '_has_audios'):
            return self._has_audios
        return self.fichiers.audios().exists()

    def has_videos(self):
        if hasattr(self, '_has_videos'):
            return self._has_videos
        return self.fichiers.videos().exists()

    def is_empty(self):
        return not (self.transcription or self.url or self.has_fichiers())


class SourceEvenement(TypographicModel):
    source = ForeignKey(Source, related_name='sourceevenement_set')
    evenement = ForeignKey('Evenement', verbose_name=_('événement'),
                           related_name='sourceevenement_set')

    class Meta(object):
        app_label = 'libretto'
        db_table = 'libretto_source_evenements'
        unique_together = ('source', 'evenement')


class SourceOeuvre(TypographicModel):
    source = ForeignKey(Source, related_name='sourceoeuvre_set')
    oeuvre = ForeignKey('Oeuvre', verbose_name=_('œuvre'),
                        related_name='sourceoeuvre_set')

    class Meta(object):
        app_label = 'libretto'
        db_table = 'libretto_source_oeuvres'
        unique_together = ('source', 'oeuvre')


class SourceIndividu(TypographicModel):
    source = ForeignKey(Source, related_name='sourceindividu_set')
    individu = ForeignKey('Individu', verbose_name=_('individu'),
                          related_name='sourceindividu_set')

    class Meta(object):
        app_label = 'libretto'
        db_table = 'libretto_source_individus'
        unique_together = ('source', 'individu')


class SourceEnsemble(TypographicModel):
    source = ForeignKey(Source, related_name='sourceensemble_set')
    ensemble = ForeignKey('Ensemble', verbose_name=_('ensemble'),
                          related_name='sourceensemble_set')

    class Meta(object):
        app_label = 'libretto'
        db_table = 'libretto_source_ensembles'
        unique_together = ('source', 'ensemble')


class SourceLieu(TypographicModel):
    source = ForeignKey(Source, related_name='sourcelieu_set')
    lieu = ForeignKey('Lieu', verbose_name=_('lieu'),
                      related_name='sourcelieu_set')

    class Meta(object):
        app_label = 'libretto'
        db_table = 'libretto_source_lieux'
        unique_together = ('source', 'lieu')


class SourcePartie(TypographicModel):
    source = ForeignKey(Source, related_name='sourcepartie_set')
    partie = ForeignKey('Partie', verbose_name=_('rôle ou instrument'),
                        related_name='sourcepartie_set')

    class Meta(object):
        app_label = 'libretto'
        db_table = 'libretto_source_parties'
        unique_together = ('source', 'partie')
