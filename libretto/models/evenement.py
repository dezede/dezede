# coding: utf-8

from __future__ import unicode_literals
import re
import warnings
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import connection
from django.db.models import (
    CharField, ForeignKey, ManyToManyField, BooleanField,
    PositiveSmallIntegerField, permalink, Q, PositiveIntegerField, get_model,
    PROTECT, Count, DecimalField)
from django.utils.encoding import (
    python_2_unicode_compatible, smart_text, force_text)
from django.utils.html import strip_tags
from django.utils.translation import (
    ungettext_lazy, ugettext, ugettext_lazy as _)
from cache_tools import model_method_cached
from .base import (
    CommonModel, AutoriteModel, CommonQuerySet, CommonManager,
    PublishedManager, PublishedQuerySet,
    TypeDeCaracteristique, Caracteristique, AncrageSpatioTemporel)
from common.utils.html import capfirst, href, hlp, microdata
from common.utils.text import str_list


__all__ = (b'ElementDeDistribution', b'CaracteristiqueDeProgramme',
           b'ElementDeProgramme', b'Evenement')


class ElementDeDistributionQuerySet(CommonQuerySet):
    def individus(self):
        return get_model('libretto', 'Individu').objects.filter(
            pk__in=self.values_list('individu', flat=True))

    def evenements(self):
        return Evenement.objects.filter(
            Q(distribution__in=self)
            | Q(programme__distribution__in=self)).distinct()

    def prefetch(self):
        return self.select_related(
            'individu', 'ensemble', 'pupitre', 'pupitre__partie', 'profession')

    def html(self, tags=True):
        return str_list(e.html(tags=tags) for e in self)


class ElementDeDistributionManager(CommonManager):
    queryset_class = ElementDeDistributionQuerySet

    def individus(self):
        return self.get_queryset().individus()

    def evenements(self):
        return self.get_queryset().evenements()

    def prefetch(self):
        return self.get_queryset().prefetch()

    def html(self, tags=True):
        return self.get_queryset().html(tags=tags)


@python_2_unicode_compatible
class ElementDeDistribution(CommonModel):
    evenement = ForeignKey(
        'Evenement', null=True, blank=True, related_name='distribution',
        verbose_name=_('événement'), on_delete=PROTECT)

    individu = ForeignKey(
        'Individu', blank=True, null=True, on_delete=PROTECT,
        related_name='+', verbose_name=_('individu'))
    ensemble = ForeignKey(
        'Ensemble', blank=True, null=True, on_delete=PROTECT,
        related_name='+', verbose_name=_('ensemble'))
    pupitre = ForeignKey(
        'Pupitre', verbose_name=_('pupitre'), null=True, blank=True,
        related_name='elements_de_distribution', on_delete=PROTECT)
    profession = ForeignKey(
        'Profession', verbose_name=_('profession'), null=True, blank=True,
        related_name='elements_de_distribution', on_delete=PROTECT)
    # TODO: Ajouter une FK (ou M2M?) vers Individu pour les remplacements.

    objects = ElementDeDistributionManager()

    class Meta(object):
        verbose_name = ungettext_lazy('élément de distribution',
                                      'éléments de distribution', 1)
        verbose_name_plural = ungettext_lazy('élément de distribution',
                                             'éléments de distribution', 2)
        ordering = ('pupitre', 'profession', 'individu', 'ensemble')
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('evenement', 'elements_de_programme')

    def __str__(self):
        return self.html(tags=False)

    def html(self, tags=True):
        l = []
        feminin = False

        assert not (self.individu and self.ensemble)
        if self.individu:
            l.append(self.individu.html(tags=tags))
            feminin = self.individu.is_feminin()
        elif self.ensemble:
            l.append(self.ensemble.html(tags=tags))

        if self.pupitre:
            l.append('[' + self.pupitre.html() + ']')
        elif self.profession:
            l.append('[' + self.profession.html(feminin=feminin) + ']')

        out = str_list(l, infix=' ')
        if not tags:
            return strip_tags(out)
        return out

    def related_label(self):
        return self.get_change_link()

    @permalink
    def get_change_url(self):
        return 'admin:libretto_elementdedistribution_change', (self.pk,)

    def get_change_link(self):
        return href(self.get_change_url(), smart_text(self), new_tab=True)

    @staticmethod
    def autocomplete_search_fields():
        return (
            'pupitre__partie__nom__icontains',
            'individu__nom__icontains',
            'individu__pseudonyme__icontains',
            'ensemble__nom__icontains',
        )


class TypeDeCaracteristiqueDeProgramme(TypeDeCaracteristique):
    class Meta(object):
        verbose_name = ungettext_lazy(
            "type de caractéristique de programme",
            "types de caractéristique de programme", 1)
        verbose_name_plural = ungettext_lazy(
            "type de caractéristique de programme",
            "types de caractéristique de programme", 2)
        ordering = ('classement',)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('typedecaracteristique_ptr',)


class CaracteristiqueDeProgramme(Caracteristique):
    class Meta(object):
        verbose_name = ungettext_lazy(
            'caractéristique de programme',
            'caractéristiques de programme', 1)
        verbose_name_plural = ungettext_lazy(
            'caractéristique de programme',
            'caractéristiques de programme', 2)
        ordering = ('type', 'classement', 'valeur')
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('caracteristique_ptr', 'elements_de_programme',)


class ElementDeProgrammeQueryset(CommonQuerySet):
    def fill_numeros(self):
        numbered = [e for e in self
                    if e.numerotation not in e.NUMEROTATIONS_SANS_ORDRE]
        for element in self:
            if element.numerotation in element.NUMEROTATIONS_SANS_ORDRE:
                element._numero = ''
            else:
                element._numero = len([e for e in numbered
                                       if e.position <= element.position])
        return self


class ElementDeProgrammeManager(CommonManager):
    queryset_class = ElementDeProgrammeQueryset

    def fill_numeros(self):
        return self.get_queryset().fill_numeros()


@python_2_unicode_compatible
class ElementDeProgramme(CommonModel):
    evenement = ForeignKey('Evenement', related_name='programme',
                           db_index=True, verbose_name=_('événement'))
    oeuvre = ForeignKey('Oeuvre', related_name='elements_de_programme',
                        verbose_name=_('œuvre'), blank=True, null=True,
                        db_index=True, on_delete=PROTECT)
    autre = CharField(max_length=500, blank=True, db_index=True)
    caracteristiques = ManyToManyField(
        CaracteristiqueDeProgramme,
        related_name='elements_de_programme', blank=True, null=True,
        verbose_name=_('caractéristiques'))
    NUMEROTATIONS = (
        ('O', _('Numéros')),  # O pour Ordered
        ('B', _('Numéros entre crochets (supposition)')),  # B pour Brackets
        ('U', _('Puce')),  # U pour Unordered
        ('E', _('Absente (entracte, etc)')),  # E pour Empty
    )
    numerotation = CharField(
        _('numérotation'), choices=NUMEROTATIONS, max_length=1, default='O')
    NUMEROTATIONS_SANS_ORDRE = ('U', 'E',)
    position = PositiveSmallIntegerField(_('position'), db_index=True)
    # TODO: Quand les nested inlines seront possibles avec Django, remplacer
    # ceci par une ForeignKey dans ElementDeDistribution.
    distribution = ManyToManyField(
        ElementDeDistribution, related_name='elements_de_programme',
        blank=True, null=True)
    # FIXME: Retirer ceci si on supprime Personnel.
    personnels = ManyToManyField('Personnel', blank=True, null=True,
                                 related_name='elements_de_programme')
    part_d_auteur = DecimalField(_('P. A.'), max_digits=6, decimal_places=2,
                                 blank=True, null=True)

    objects = ElementDeProgrammeManager()

    class Meta(object):
        verbose_name = ungettext_lazy('élément de programme',
                                      'éléments de programme', 1)
        verbose_name_plural = ungettext_lazy('élément de programme',
                                             'éléments de programme', 2)
        ordering = ('position', 'oeuvre')
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('evenement',)
        return ()

    def calc_caracteristiques(self, tags=False):
        if self.pk is None:
            return ''
        return self.caracteristiques.html(tags=tags, caps=False)
    calc_caracteristiques.allow_tags = True
    calc_caracteristiques.short_description = _('caractéristiques')

    @property
    @model_method_cached()
    def numero(self):
        if hasattr(self, '_numero'):
            return self._numero
        if self.numerotation in self.NUMEROTATIONS_SANS_ORDRE:
            return ''
        return self.evenement.programme.exclude(
            Q(position__gt=self.position)
            | Q(numerotation__in=self.NUMEROTATIONS_SANS_ORDRE)).count()

    @model_method_cached()
    def html(self, tags=True):
        has_pk = self.pk is not None

        distribution = ''
        add_distribution = False
        if has_pk:
            distribution = self.distribution.all()
            if distribution:
                distribution = distribution.html(tags=tags)
                add_distribution = True

        if self.oeuvre:
            out = self.oeuvre.html(tags)
        elif self.autre:
            out = self.autre
        elif distribution:
            out = distribution
            add_distribution = False
        else:
            warnings.warn('Il manque des champs dans <%(class)s pk=%(pk)s>' %
                          {'class': self.__class__.__name__, 'pk': self.pk})
            return ''

        caracteristiques = self.calc_caracteristiques(tags=tags)
        if caracteristiques:
            out += ' [' + caracteristiques + ']'

        if add_distribution:
            out += '. — ' + distribution

        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def __str__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return (
            'oeuvre__prefixe_titre__icontains', 'oeuvre__titre__icontains',
            'oeuvre__prefixe_titre_secondaire__icontains',
            'oeuvre__titre_secondaire__icontains',
            'oeuvre__genre__nom__icontains',
        )


class EvenementQuerySet(PublishedQuerySet):
    def yearly_counts(self):
        return (
            self.extra({'year': connection.ops.date_trunc_sql('year',
                                                              'debut_date')})
            .values('year').annotate(count=Count('pk'))
            .order_by('year'))

    def get_distributions(self):
        return ElementDeDistribution.objects.filter(
            Q(evenement__in=self)
            | Q(element_de_programme__evenement__in=self))

    def ensembles(self):
        distributions = self.get_distributions()
        qs = get_model('libretto', 'Ensemble').objects.filter(
            elements_de_distribution__in=distributions).distinct()
        return qs.only('particule_nom', 'nom', 'slug')

    def individus(self):
        distributions = self.get_distributions()
        qs = get_model('libretto', 'individu').objects.filter(
            elements_de_distribution__in=distributions).distinct()
        return qs.only(
            'particule_nom', 'nom', 'prenoms', 'prenoms_complets',
            'particule_nom_naissance', 'nom_naissance', 'pseudonyme',
            'designation', 'titre', 'slug',
        )

    def with_program(self):
        return self.filter(Q(relache=True) | Q(programme__isnull=False))

    def prefetch_all(self):
        # TODO: Retirer ceci quand https://code.djangoproject.com/ticket/24196
        #       sera corrigé et dans notre version de Django.
        if self.query.low_mark == self.query.high_mark:
            return self

        qs = Evenement.objects.filter(
            pk__in=list(self.values_list('pk', flat=True)))
        qs.query.order_by = self.query.order_by
        qs.query.default_ordering = self.query.default_ordering
        qs.query.standard_ordering = self.query.standard_ordering
        return (
            qs.select_related(
                'debut_lieu', 'debut_lieu__nature',
                'fin_lieu', 'fin_lieu__nature',
                'owner', 'etat')
            .prefetch_related(
                'caracteristiques__type',
                'distribution__individu', 'distribution__ensemble',
                'distribution__profession', 'distribution__pupitre__partie',
                'programme__caracteristiques__type',
                'programme__oeuvre__genre',
                'programme__oeuvre__caracteristiques__type',
                'programme__oeuvre__auteurs__individu',
                'programme__oeuvre__auteurs__profession',
                'programme__oeuvre__pupitres__partie',
                'programme__oeuvre__contenu_dans__genre',
                'programme__oeuvre__contenu_dans__caracteristiques__type',
                'programme__oeuvre__contenu_dans__pupitres__partie',
                'programme__distribution__individu',
                'programme__distribution__ensemble',
                'programme__distribution__profession',
                'programme__distribution__pupitre__partie')
            .only(
                'notes_publiques', 'relache', 'circonstance',
                'programme_incomplet',
                'debut_date', 'debut_date_approx',
                'debut_heure', 'debut_heure_approx', 'debut_lieu_approx',
                'fin_date', 'fin_date_approx',
                'fin_heure', 'fin_heure_approx', 'fin_lieu_approx',
                'owner', 'owner__is_superuser', 'owner__username',
                'owner__first_name', 'owner__last_name', 'owner__mentor',
                'etat', 'etat__message', 'etat__public',
                'debut_lieu', 'debut_lieu__slug',
                'debut_lieu__lft', 'debut_lieu__rght', 'debut_lieu__tree_id',
                'debut_lieu__nom', 'debut_lieu__parent',
                'debut_lieu__nature', 'debut_lieu__nature__referent',
                'fin_lieu', 'fin_lieu__slug',
                'fin_lieu__lft', 'fin_lieu__rght', 'fin_lieu__tree_id',
                'fin_lieu__nom', 'fin_lieu__parent',
                'fin_lieu__nature', 'fin_lieu__nature__referent',
                # FIXME: The following fields are not used in rendering,
                #        but an IndexError occurs when removing them…
                'notes_privees', 'code_programme', 'exoneres', 'payantes',
                'frequentation', 'scolaires', 'jauge',
                'recette_generale', 'recette_par_billets',
            )
        )


class EvenementManager(PublishedManager):
    queryset_class = EvenementQuerySet

    def yearly_counts(self):
        return self.get_queryset().yearly_counts()

    def with_program(self):
        return self.get_queryset().with_program()

    def prefetch_all(self):
        return self.get_queryset().prefetch_all()


plus_separated_integers_re = re.compile(r'^\d+(?:\+\d+)*$')
plus_separated_integers_validator = RegexValidator(
    plus_separated_integers_re,
    _('Entrez uniquement des entiers séparés par des « + ».'), 'invalid')


@python_2_unicode_compatible
class Evenement(AutoriteModel):
    debut = AncrageSpatioTemporel(('date',),
                                  short_description=_('début'))
    fin = AncrageSpatioTemporel(short_description=_('fin'))
    programme_incomplet = BooleanField(_('programme incomplet'), default=False)
    relache = BooleanField(_('relâche'), default=False, db_index=True)
    circonstance = CharField(_('circonstance'), max_length=500, blank=True,
                             db_index=True)
    caracteristiques = ManyToManyField(
        CaracteristiqueDeProgramme,
        related_name='evenements', blank=True, null=True,
        verbose_name=_('caractéristiques'))

    code_programme = CharField(_('code du programme'), max_length=55,
                               blank=True)
    exoneres = PositiveIntegerField(_('entrées exonérées'), null=True,
                                    blank=True)
    payantes = PositiveIntegerField(_('entrées payantes'), null=True,
                                    blank=True)
    frequentation = PositiveIntegerField(_('fréquentation totale'), null=True,
                                         blank=True)
    scolaires = PositiveIntegerField(_('entrées scolaires'), null=True,
                                     blank=True)
    jauge = PositiveIntegerField(_('jauge'), null=True, blank=True)
    recette_generale = DecimalField(_('recette générale'), max_digits=7,
                                    decimal_places=2, blank=True, null=True)
    recette_par_billets = CharField(
        _('recette par titre de billets'),
        max_length=30,
        validators=[plus_separated_integers_validator], blank=True)

    objects = EvenementManager()

    class Meta(object):
        verbose_name = ungettext_lazy('événement', 'événements', 1)
        verbose_name_plural = ungettext_lazy('événement', 'événements', 2)
        ordering = ('debut_date', 'debut_heure', 'debut_lieu',
                    'debut_date_approx', 'debut_heure_approx',
                    'debut_lieu_approx')
        app_label = 'libretto'
        permissions = (('can_change_status', _('Peut changer l’état')),)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('dossiers',)
        return ()

    @permalink
    def get_absolute_url(self):
        return 'evenement_pk', (self.pk,)

    def permalien(self):
        return self.get_absolute_url()

    def link(self):
        return href(self.get_absolute_url(), smart_text(self))
    link.short_description = _('lien')
    link.allow_tags = True

    def calc_caracteristiques(self, tags=True, caps=True):
        if self.pk is None:
            return ''
        return self.caracteristiques.html(tags=tags, caps=caps)

    def get_meta_name(self, tags=False):
        if self.circonstance:
            out = self.circonstance
        else:
            distribution = self.distribution.all()
            if distribution:
                out = distribution.html(tags=tags)
            else:
                programme = self.programme.all()
                if programme.exists():
                    element = programme[0]
                    out = element.oeuvre or element.autre
                else:
                    return ''
        return microdata(out, 'summary', tags=tags)

    def html(self, tags=True):
        relache = ''
        circonstance = ''
        if self.circonstance:
            circonstance = hlp(self.circonstance, ugettext('circonstance'),
                               tags)
        if self.relache:
            relache = microdata(ugettext('Relâche'), 'eventType', tags=tags)

        lieu = microdata(self.debut.lieu_str(tags), 'location',
                         tags=tags)

        return str_list((lieu, circonstance,
                         self.debut.heure_str(), relache))

    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def has_program(self):
        if self.relache:
            return True
        if hasattr(self, '_has_program'):
            return self._has_program
        return self.programme.exists()
    has_program.short_description = _('programme')
    has_program.boolean = True

    def has_source(self):
        if hasattr(self, '_has_source'):
            return self._has_source
        return self.sources.exists()
    has_source.short_description = _('source')
    has_source.boolean = True
    has_source.admin_order_field = 'sources'

    @property
    def oeuvres(self):
        return get_model('libretto', 'Oeuvre').objects.filter(
            elements_de_programme__evenement=self)

    def __str__(self):
        out = self.debut.date_str(False)
        out = capfirst(out)
        out += '\u00A0> ' + self.html(False)
        return strip_tags(out)

    def related_label(self):
        return href(reverse('admin:libretto_evenement_change',
                            args=(self.pk,)), force_text(self), new_tab=True)

    @staticmethod
    def autocomplete_search_fields():
        return (
            'circonstance__icontains',
            'debut_lieu__nom__icontains',
            'debut_lieu__parent__nom__icontains',
            'debut_date__icontains',
            'debut_heure__icontains',
            'debut_lieu_approx__icontains',
            'debut_date_approx__icontains',
            'debut_heure_approx__icontains',
        )
