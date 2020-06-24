from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import (
    CharField, ForeignKey, ManyToManyField, permalink, SmallIntegerField,
    DateField, PositiveSmallIntegerField, Model, BooleanField, CASCADE)
from django.db.models.sql import EmptyResultSet
from django.template.defaultfilters import date
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, ugettext
from common.utils.abbreviate import abbreviate
from common.utils.html import capfirst, href, date_html, sc
from common.utils.sql import get_raw_query
from common.utils.text import str_list
from .base import (CommonModel, LOWER_MSG, PLURAL_MSG, calc_pluriel,
                   UniqueSlugModel, AutoriteModel, ISNI_VALIDATORS)
from .evenement import Evenement


__all__ = (
    'Profession', 'Membre', 'TypeDEnsemble', 'Ensemble')


# TODO: Songer à l’arrivée des Emplois.
class Profession(AutoriteModel, UniqueSlugModel):
    nom = CharField(_('nom'), max_length=200, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
                            help_text=PLURAL_MSG)
    nom_feminin = CharField(
        _('nom (au féminin)'), max_length=230, blank=True,
        help_text=_('Ne préciser que s’il est différent du nom.'))
    nom_feminin_pluriel = CharField(
        _('nom (au féminin pluriel)'), max_length=250, blank=True,
        help_text=PLURAL_MSG)
    parent = ForeignKey('self', blank=True, null=True, related_name='enfants',
                        verbose_name=_('parent'), on_delete=CASCADE)
    classement = SmallIntegerField(_('classement'), default=1, db_index=True)

    class Meta(object):
        verbose_name = _('profession')
        verbose_name_plural = _('professions')
        ordering = ('classement', 'nom')
        permissions = (('can_change_status', _('Peut changer l’état')),)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        relations = ('auteurs', 'elements_de_distribution',)
        if all_relations:
            relations += ('enfants', 'individus', 'parties',)
        return relations

    @permalink
    def get_absolute_url(self):
        return 'profession_detail', (self.slug,)

    @permalink
    def permalien(self):
        return 'profession_permanent_detail', (self.pk,)

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

    def feminin_pluriel(self):
        if self.nom_feminin:
            return calc_pluriel(self, attr_base='nom_feminin')
        return self.pluriel()

    def html(self, tags=True, short=False, caps=False, feminin=False,
             pluriel=False):
        if pluriel:
            nom = self.feminin_pluriel() if feminin else self.pluriel()
        else:
            nom = self.feminin() if feminin else self.nom
        if caps:
            nom = capfirst(nom)
        if short:
            nom = abbreviate(nom, min_len=4, tags=tags)
        url = '' if not tags else self.get_absolute_url()
        return href(url, nom, tags)

    def short_html(self, tags=True, feminin=False, pluriel=False):
        return self.html(tags, short=True, feminin=feminin, pluriel=pluriel)

    def __hash__(self):
        return hash(self.nom)

    def __str__(self):
        return capfirst(self.html(tags=False))

    def individus_count(self):
        return self.individus.count()
    individus_count.short_description = _('nombre d’individus')

    def oeuvres_count(self):
        return self.auteurs.oeuvres().count()
    oeuvres_count.short_description = _('nombre d’œuvres')

    def get_children(self):
        return self.enfants.all()

    def is_leaf_node(self):
        return not self.enfants.exists()

    def related_label(self):
        if self.nom_feminin:
            return f'{self.nom} / {self.nom_feminin}'
        return self.nom

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__unaccent__icontains', 'nom_pluriel__unaccent__icontains',
                'nom_feminin__unaccent__icontains',
                'nom_feminin_pluriel__unaccent__icontains')


class PeriodeDActivite(Model):
    YEAR = 0
    MONTH = 1
    DAY = 2
    PRECISIONS = (
        (YEAR, _('Année')),
        (MONTH, _('Mois')),
        (DAY, _('Jour')),
    )
    debut = DateField(_('début'), blank=True, null=True)
    debut_precision = PositiveSmallIntegerField(
        _('précision du début'), choices=PRECISIONS, default=0)
    fin = DateField(_('fin'), blank=True, null=True)
    fin_precision = PositiveSmallIntegerField(
        _('précision de la fin'), choices=PRECISIONS, default=0)

    class Meta(object):
        abstract = True

    def _smart_date(self, attr, attr_precision, tags=True):
        d = getattr(self, attr)
        if d is None:
            return
        precision = getattr(self, attr_precision)
        if precision == self.YEAR:
            return force_text(d.year)
        if precision == self.MONTH:
            return date(d, 'F Y')
        if precision == self.DAY:
            return date_html(d, tags=tags)

    def smart_debut(self, tags=True):
        return self._smart_date('debut', 'debut_precision', tags=tags)

    def smart_fin(self, tags=True):
        return self._smart_date('fin', 'fin_precision', tags=tags)

    def smart_period(self, tags=True):
        debut = self.smart_debut(tags=tags)
        fin = self.smart_fin(tags=tags)
        # TODO: Rendre ceci plus simple en conservant les possibilités
        # d’internationalisation.
        if fin is None:
            if debut is None:
                return ''
            if self.debut_precision == self.DAY:
                t = ugettext('depuis le %(debut)s')
            else:
                t = ugettext('depuis %(debut)s')
        else:
            if debut is None:
                if self.fin_precision == self.DAY:
                    t = ugettext('jusqu’au %(fin)s')
                else:
                    t = ugettext('jusqu’à %(fin)s')
            else:
                if self.debut_precision == self.DAY:
                    if self.fin_precision == self.DAY:
                        t = ugettext('du %(debut)s au %(fin)s')
                    else:
                        t = ugettext('du %(debut)s à %(fin)s')
                else:
                    if self.fin_precision == self.DAY:
                        t = ugettext('de %(debut)s au %(fin)s')
                    else:
                        t = ugettext('de %(debut)s à %(fin)s')
        return t % {'debut': debut, 'fin': fin}
    smart_period.short_description = _('Période d’activité')


def limit_choices_to_instruments():
    return {'type': apps.get_model('libretto', 'Partie').INSTRUMENT}


class Membre(CommonModel, PeriodeDActivite):
    ensemble = ForeignKey('Ensemble', related_name='membres',
                          verbose_name=_('ensemble'), on_delete=CASCADE)
    # TODO: Ajouter nombre pour les membres d'orchestre pouvant être saisi
    #       au lieu d'un individu.
    individu = ForeignKey('Individu', related_name='membres',
                          verbose_name=_('individu'), on_delete=CASCADE)
    instrument = ForeignKey(
        'Partie', blank=True, null=True, related_name='membres',
        limit_choices_to=limit_choices_to_instruments,
        verbose_name=_('instrument'), on_delete=CASCADE)
    profession = ForeignKey(
        'Profession', blank=True, null=True, related_name='membres',
        verbose_name=_('profession'), on_delete=CASCADE,
    )
    classement = SmallIntegerField(_('classement'), default=1)

    class Meta(object):
        verbose_name = _('membre')
        verbose_name_plural = _('membres')
        ordering = ('classement', 'individu__nom', 'individu__prenoms')

    def html(self, to_individus=True, tags=True):
        l = [(self.individu if to_individus
              else self.ensemble).html(tags=tags)]
        if self.instrument:
            l.append(f'[{self.instrument.html(tags=tags)}]')
        if self.profession:
            l.append(f'[{self.profession.html(tags=tags)}]')
        if self.debut or self.fin:
            l.append(f'({self.smart_period(tags=tags)})')
        return mark_safe(' '.join(l))

    def ensemble_html(self, tags=True):
        return self.html(to_individus=False, tags=tags)

    def __str__(self):
        return self.html(tags=False)

    def link(self):
        return self.html()


class TypeDEnsemble(CommonModel):
    nom = CharField(_('nom'), max_length=40, help_text=LOWER_MSG)
    nom_pluriel = CharField(_('nom pluriel'), max_length=45, blank=True,
                            help_text=PLURAL_MSG)
    parent = ForeignKey('self', null=True, blank=True, related_name='enfants',
                        verbose_name=_('parent'), on_delete=CASCADE)

    class Meta(object):
        verbose_name = _('type d’ensemble')
        verbose_name_plural = _('types d’ensemble')
        ordering = ('nom',)

    def __str__(self):
        return self.nom

    @staticmethod
    def autocomplete_search_fields():
        return 'nom__unaccent__icontains', 'nom_pluriel__unaccent__icontains'


class Ensemble(AutoriteModel, PeriodeDActivite, UniqueSlugModel):
    particule_nom = CharField(
        _('particule du nom'), max_length=5, blank=True, db_index=True)
    nom = CharField(_('nom'), max_length=75, db_index=True)
    # FIXME: retirer null=True quand la base sera nettoyée.
    type = ForeignKey('TypeDEnsemble', null=True, related_name='ensembles',
                      verbose_name=_('type'), on_delete=CASCADE)
    # TODO: Permettre deux villes sièges.
    siege = ForeignKey('Lieu', null=True, blank=True,
                       related_name='ensembles',
                       verbose_name=_('localisation'), on_delete=CASCADE)
    # TODO: Ajouter historique d'ensemble.

    individus = ManyToManyField(
        'Individu', through=Membre, related_name='ensembles',
        verbose_name=_('individus'))

    isni = CharField(
        _('Identifiant ISNI'), max_length=16, blank=True,
        validators=ISNI_VALIDATORS,
        help_text=_('Exemple : « 0000000115201575 » '
                    'pour Le Poème Harmonique.'))
    sans_isni = BooleanField(_('sans ISNI'), default=False)

    class Meta(object):
        ordering = ('nom',)
        verbose_name = _('ensemble')
        verbose_name_plural = _('ensembles')

    def __str__(self):
        return self.html(tags=False)

    def nom_complet(self):
        return f'{self.particule_nom} {self.nom}'.strip()

    def html(self, tags=True):
        nom = self.nom_complet()
        if tags:
            return href(self.get_absolute_url(),
                        sc(nom, tags=tags), tags=tags)
        return nom

    def link(self):
        return self.html()

    @permalink
    def get_absolute_url(self):
        return 'ensemble_detail', (self.slug,)

    @permalink
    def permalien(self):
        return 'ensemble_permanent_detail', (self.pk,)

    def membres_html(self):
        return str_list([
            membre.html() for membre in
            self.membres.select_related('individu', 'instrument')])
    membres_html.short_description = _('membres')

    def membres_count(self):
        return self.membres.count()
    membres_count.short_description = _('nombre de membres')

    def oeuvres(self):
        oeuvres = self.auteurs.oeuvres()
        return oeuvres.exclude(extrait_de__in=oeuvres)

    def apparitions(self):
        sql = """
        SELECT DISTINCT COALESCE(distribution.evenement_id, programme.evenement_id)
        FROM libretto_elementdedistribution AS distribution
        LEFT JOIN libretto_elementdeprogramme AS programme
            ON (programme.id = distribution.element_de_programme_id)
        WHERE distribution.ensemble_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, (self.pk,))
            evenement_ids = [t[0] for t in cursor.fetchall()]
        return Evenement.objects.filter(id__in=evenement_ids)

    def evenements_par_territoire(self, evenements_qs=None):
        if self.siege is None:
            return ()
        if evenements_qs is None:
            evenements_qs = self.apparitions()
        try:
            evenements_sql, evenements_params = get_raw_query(
                evenements_qs.order_by().values('pk', 'debut_lieu_id'))
        except EmptyResultSet:
            return ()
        sql = f"""
        WITH evenements AS (
            {evenements_sql}
        )
        (
            SELECT %s, COUNT(id) FROM evenements
        ) UNION ALL (
            SELECT ancetre.nom, COUNT(evenement.id)
            FROM libretto_lieu AS ancetre
            INNER JOIN libretto_lieu AS lieu ON (
                lieu.path LIKE ancetre.path || '%%')
            INNER JOIN evenements AS evenement ON (
                evenement.debut_lieu_id = lieu.id)
            WHERE %s LIKE ancetre.path || '%%'
            GROUP BY ancetre.id
            ORDER BY length(ancetre.path)
        );
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, evenements_params + (
                ugettext('Monde'), self.siege.path))
            data = cursor.fetchall()
        new_data = []
        for i, (name, count) in enumerate(data):
            try:
                exclusive_count = count - data[i+1][1]
            except IndexError:
                exclusive_count = count
            if exclusive_count > 0:
                new_data.append((name, count, exclusive_count))
        return new_data

    def clean(self):
        if self.isni and self.sans_isni:
            message = _('« ISNI » ne peut être rempli '
                        'lorsque « Sans ISNI » est coché.')
            raise ValidationError({'isni': message, 'sans_isni': message})

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('elements_de_distribution',)

    @staticmethod
    def autocomplete_search_fields():
        return ('particule_nom__unaccent__icontains',
                'nom__unaccent__icontains',
                'siege__nom__unaccent__icontains')
