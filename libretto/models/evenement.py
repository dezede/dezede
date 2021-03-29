import re
import warnings
from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import connection
from django.db.models import (
    CharField, ForeignKey, ManyToManyField, BooleanField,
    PositiveSmallIntegerField, permalink, Q,
    PROTECT, Count, DecimalField, SmallIntegerField, Max, CASCADE)
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _
from cache_tools import model_method_cached
from .base import (
    CommonModel, AutoriteModel, CommonQuerySet, CommonManager,
    PublishedManager, PublishedQuerySet,
    AncrageSpatioTemporel, calc_pluriel, PLURAL_MSG)
from common.utils.html import capfirst, href, hlp, microdata
from common.utils.text import str_list, ex, BiGrouper


__all__ = ('ElementDeDistribution', 'CaracteristiqueDeProgramme',
           'ElementDeProgramme', 'Evenement')


class ElementDeDistributionBiGrouper(BiGrouper):
    def __init__(self, iterator, tags=False):
        self.tags = tags
        super().__init__(iterator)

    def get_key(self, obj):
        return obj.partie if obj.profession is None else obj.profession

    def get_value(self, obj):
        return obj.individu if obj.ensemble is None else obj.ensemble

    def get_verbose_key(self, key, values):
        if isinstance(key, apps.get_model('libretto.Partie')):
            return key.short_html(tags=self.tags, pluriel=len(values) > 1)
        Individu = apps.get_model('libretto.Individu')
        return key.html(tags=self.tags, pluriel=len(values) > 1,
                        feminin=all(isinstance(v, Individu) and v.is_feminin()
                                    for v in values))

    def get_verbose_value(self, value, keys):
        return value.html(tags=self.tags)


class ElementDeDistributionQuerySet(CommonQuerySet):
    def individus(self):
        return apps.get_model('libretto', 'Individu').objects.filter(
            pk__in=self.values_list('individu', flat=True))

    def evenements(self):
        return Evenement.objects.filter(
            Q(distribution__in=self)
            | Q(programme__distribution__in=self)).distinct()

    def prefetch(self):
        return self.select_related(
            'individu', 'ensemble', 'partie', 'profession')

    def html(self, tags=True):
        return force_text(ElementDeDistributionBiGrouper(self, tags=tags))


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


class ElementDeDistribution(CommonModel):
    # Une contrainte de base de données existe dans les migrations
    # pour éviter que les deux soient remplis.
    evenement = ForeignKey(
        'Evenement', null=True, blank=True, related_name='distribution',
        verbose_name=_('événement'), on_delete=CASCADE)
    element_de_programme = ForeignKey(
        'ElementDeProgramme', null=True, blank=True, related_name='distribution',
        verbose_name=_('élément de programme'), on_delete=CASCADE)

    # Une contrainte de base de données existe dans les migrations
    # pour éviter que les deux soient remplis.
    individu = ForeignKey(
        'Individu', blank=True, null=True, on_delete=PROTECT,
        related_name='elements_de_distribution', verbose_name=_('individu'))
    ensemble = ForeignKey(
        'Ensemble', blank=True, null=True, on_delete=PROTECT,
        related_name='elements_de_distribution', verbose_name=_('ensemble'))
    # Une contrainte de base de données existe dans les migrations
    # pour éviter que les deux soient remplis.
    partie = ForeignKey(
        'Partie', verbose_name=_('rôle ou instrument'), null=True, blank=True,
        related_name='elements_de_distribution', on_delete=PROTECT)
    profession = ForeignKey(
        'Profession', verbose_name=_('profession'), null=True, blank=True,
        related_name='elements_de_distribution', on_delete=PROTECT)
    # TODO: Ajouter une FK (ou M2M?) vers Individu pour les remplacements.

    objects = ElementDeDistributionManager()

    class Meta(object):
        verbose_name = _('élément de distribution')
        verbose_name_plural = _('éléments de distribution')
        ordering = ('partie', 'profession', 'individu', 'ensemble')

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('evenement', 'element_de_programme')

    def __str__(self):
        return self.html(tags=False)

    def html(self, tags=True):
        out = force_text(ElementDeDistributionBiGrouper((self,), tags=tags))
        if not tags:
            return strip_tags(out)
        return mark_safe(out)

    def related_label(self):
        return self.get_change_link()

    @permalink
    def get_change_url(self):
        return 'admin:libretto_elementdedistribution_change', (self.pk,)

    def get_change_link(self):
        return href(self.get_change_url(), force_text(self), new_tab=True)

    @staticmethod
    def autocomplete_search_fields():
        return (
            'partie__nom__unaccent__icontains',
            'individu__nom__unaccent__icontains',
            'individu__pseudonyme__unaccent__icontains',
            'ensemble__nom__unaccent__icontains',
        )


class TypeDeCaracteristiqueDeProgramme(CommonModel):
    nom = CharField(_('nom'), max_length=200, help_text=ex(_('tonalité')),
                    unique=True, db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
                            help_text=PLURAL_MSG)
    classement = SmallIntegerField(_('classement'), default=1)

    class Meta(object):
        verbose_name = _('type de caractéristique de programme')
        verbose_name_plural = _('types de caractéristique de programme')
        ordering = ('classement',)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('caracteristiques',)

    def pluriel(self):
        return calc_pluriel(self)

    def __str__(self):
        return self.nom

    @staticmethod
    def autocomplete_search_fields():
        return 'nom__unaccent__icontains', 'nom_pluriel__unaccent__icontains',


class CaracteristiqueQuerySet(CommonQuerySet):
    def html_list(self, tags=True):
        return [hlp(c.valeur, c.type, tags)
                for c in self]

    def html(self, tags=True, caps=False):
        l = []
        first = True
        for c in self:
            valeur = c.valeur
            if first and caps:
                valeur = capfirst(valeur)
                first = False
            valeur = mark_safe(valeur)
            if c.type:
                l.append(hlp(valeur, c.type, tags=tags))
            else:
                l.append(valeur)
        return mark_safe(str_list(l))


class CaracteristiqueManager(CommonManager):
    queryset_class = CaracteristiqueQuerySet

    def html_list(self, tags=True):
        return self.get_queryset().html_list(tags=tags)

    def html(self, tags=True, caps=True):
        return self.get_queryset().html(tags=tags, caps=caps)


class CaracteristiqueDeProgramme(CommonModel):
    type = ForeignKey(
        'TypeDeCaracteristiqueDeProgramme', null=True, blank=True,
        on_delete=PROTECT, related_name='caracteristiques',
        verbose_name=_('type'))
    valeur = CharField(_('valeur'), max_length=400,
                       help_text=ex(_('en trois actes')))
    classement = SmallIntegerField(
        _('classement'), default=1, db_index=True,
        help_text=_('Par exemple, on peut choisir de classer '
                    'les découpages par nombre d’actes.'))

    objects = CaracteristiqueManager()

    class Meta(object):
        unique_together = ('type', 'valeur')
        verbose_name = _('caractéristique de programme')
        verbose_name_plural = _('caractéristiques de programme')
        ordering = ('type', 'classement', 'valeur')

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('elements_de_programme',)

    def html(self, tags=True, caps=False):
        value = self.valeur
        if caps:
            value = capfirst(self.valeur)
        value = mark_safe(value)
        if self.type:
            return hlp(value, self.type, tags=tags)
        return value
    html.allow_tags = True

    def __str__(self):
        valeur = strip_tags(self.valeur)
        if self.type:
            return f'{self.type} : {valeur}'
        return valeur

    @staticmethod
    def autocomplete_search_fields():
        return 'type__nom__unaccent__icontains', 'valeur__unaccent__icontains',


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


class ElementDeProgramme(CommonModel):
    evenement = ForeignKey('Evenement', related_name='programme',
                           verbose_name=_('événement'), on_delete=CASCADE)
    oeuvre = ForeignKey(
        'Oeuvre', related_name='elements_de_programme',
        verbose_name=_('œuvre'), blank=True, null=True, on_delete=PROTECT,
        help_text=_('Vous pouvez croiser le titre et le nom des auteurs. '
                    'Évitez les termes généraux comme « de », « la », « le », '
                    '« avec ».'))
    autre = CharField(_('autre'), max_length=500, blank=True)
    caracteristiques = ManyToManyField(
        CaracteristiqueDeProgramme, related_name='elements_de_programme',
        blank=True, verbose_name=_('caractéristiques'))
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
    part_d_auteur = DecimalField(_('P. A.'), max_digits=6, decimal_places=2,
                                 blank=True, null=True)

    objects = ElementDeProgrammeManager()

    class Meta(object):
        verbose_name = _('élément de programme')
        verbose_name_plural = _('éléments de programme')
        ordering = ('position',)

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

    def save(self, *args, **kwargs):
        if self.position is None:
            n = self.evenement.programme.aggregate(n=Max('position'))['n']
            self.position = 0 if n is None else n + 1

        super(ElementDeProgramme, self).save(*args, **kwargs)

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
            warnings.warn(f'Il manque des champs '
                          f'dans <{self.__class__.__name__} pk={self.pk}>')
            return ''

        caracteristiques = self.calc_caracteristiques(tags=tags)
        if caracteristiques:
            out += f' [{caracteristiques}]'

        if add_distribution:
            out += f'. — {distribution}'

        return mark_safe(out)
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def __str__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return (
            'oeuvre__prefixe_titre__unaccent__icontains',
            'oeuvre__titre__unaccent__icontains',
            'oeuvre__prefixe_titre_secondaire__unaccent__icontains',
            'oeuvre__titre_secondaire__unaccent__icontains',
            'oeuvre__genre__nom__unaccent__icontains',
        )


class EvenementQuerySet(PublishedQuerySet):
    def yearly_counts(self):
        return (
            self.extra({'year': connection.ops.date_trunc_sql('year',
                                                              'debut_date')})
            .values('year').annotate(count=Count('pk', distinct=True))
            .order_by('year'))

    def get_distributions(self):
        return ElementDeDistribution.objects.filter(
            Q(evenement__in=self)
            | Q(element_de_programme__evenement__in=self))

    def ensembles(self):
        distributions = self.get_distributions()
        qs = apps.get_model('libretto', 'Ensemble').objects.filter(
            elements_de_distribution__in=distributions).distinct()
        return qs.only('particule_nom', 'nom', 'slug')

    def individus(self):
        distributions = self.get_distributions()
        qs = apps.get_model('libretto', 'Individu').objects.filter(
            elements_de_distribution__in=distributions).distinct()
        return qs.only(
            'particule_nom', 'nom', 'prenoms', 'prenoms_complets',
            'particule_nom_naissance', 'nom_naissance', 'pseudonyme',
            'designation', 'titre', 'slug',
        )

    def individus_auteurs(self):
        return apps.get_model('libretto', 'Individu').objects.filter(
            auteurs__oeuvre__elements_de_programme__evenement__in=self
        ).distinct()

    def oeuvres(self):
        return apps.get_model('libretto', 'Oeuvre').objects.filter(
            elements_de_programme__evenement__in=self).distinct()

    def with_program(self):
        return self.filter(Q(relache=True) | Q(programme__isnull=False))

    def prefetch_all(self, create_subquery=True):
        if create_subquery:
            qs = Evenement.objects.filter(
                pk__in=list(self.values_list('pk', flat=True)))
            qs.query.order_by = self.query.order_by
            qs.query.default_ordering = self.query.default_ordering
            qs.query.standard_ordering = self.query.standard_ordering
        else:
            qs = self
        return (
            qs.select_related(
                'debut_lieu', 'debut_lieu__nature',
                'debut_lieu__parent', 'debut_lieu__parent__nature',
                'fin_lieu', 'fin_lieu__nature',
                'owner', 'etat')
            .prefetch_related(
                'caracteristiques__type',
                'distribution__individu', 'distribution__ensemble',
                'distribution__profession',
                'programme__caracteristiques__type',
                'programme__oeuvre__auteurs__individu',
                'programme__oeuvre__auteurs__ensemble',
                'programme__oeuvre__auteurs__profession',
                'programme__oeuvre__genre',
                'programme__oeuvre__pupitres__partie',
                'programme__oeuvre__extrait_de__genre',
                'programme__oeuvre__extrait_de__pupitres__partie',
                'programme__distribution__individu',
                'programme__distribution__ensemble',
                'programme__distribution__profession',
                'programme__distribution__partie')
            .only(
                'notes_publiques', 'relache', 'circonstance',
                'programme_incomplet',
                'debut_date', 'debut_date_approx',
                'debut_heure', 'debut_heure_approx', 'debut_lieu_approx',
                'fin_date', 'fin_date_approx',
                'fin_heure', 'fin_heure_approx', 'fin_lieu_approx',
                'owner__is_superuser', 'owner__username',
                'owner__first_name', 'owner__last_name', 'owner__mentor',
                'etat__message', 'etat__public',
                'debut_lieu__slug',
                'debut_lieu__nom', 'debut_lieu__parent',
                'debut_lieu__nature__referent',
                'fin_lieu__slug',
                'fin_lieu__nom', 'fin_lieu__parent',
                'fin_lieu__nature__referent',
            )
        )


class EvenementManager(PublishedManager):
    queryset_class = EvenementQuerySet

    def yearly_counts(self):
        return self.get_queryset().yearly_counts()

    def ensembles(self):
        return self.get_queryset().ensembles()

    def individus(self):
        return self.get_queryset().individus()

    def individus_auteurs(self):
        return self.get_queryset().individus_auteurs()

    def with_program(self):
        return self.get_queryset().with_program()

    def prefetch_all(self, create_subquery=True):
        return self.get_queryset().prefetch_all(
            create_subquery=create_subquery)


plus_separated_integers_re = re.compile(r'^\d+(?:\+\d+)*$')
plus_separated_integers_validator = RegexValidator(
    plus_separated_integers_re,
    _('Entrez uniquement des entiers séparés par des « + ».'), 'invalid')


class Evenement(AutoriteModel):
    debut = AncrageSpatioTemporel(('date',),
                                  verbose_name=_('début'))
    fin = AncrageSpatioTemporel(verbose_name=_('fin'))
    programme_incomplet = BooleanField(_('programme incomplet'), default=False)
    relache = BooleanField(_('relâche'), default=False, db_index=True)
    circonstance = CharField(_('circonstance'), max_length=500, blank=True)
    caracteristiques = ManyToManyField(
        CaracteristiqueDeProgramme, related_name='evenements', blank=True,
        verbose_name=_('caractéristiques'))

    recette_generale = DecimalField(_('recette générale'), max_digits=9,
                                    decimal_places=2, blank=True, null=True)
    recette_par_billets = CharField(
        _('recette par titre de billets'),
        max_length=30,
        validators=[plus_separated_integers_validator], blank=True)

    objects = EvenementManager()

    class Meta(object):
        verbose_name = _('événement')
        verbose_name_plural = _('événements')
        ordering = ('debut_date', 'debut_heure', 'debut_lieu',
                    'debut_lieu_approx')
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
        return href(self.get_absolute_url(), force_text(self))
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

        return mark_safe(str_list((lieu, circonstance,
                                   self.debut.heure_str(), relache)))

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
        return apps.get_model('libretto', 'Oeuvre').objects.filter(
            elements_de_programme__evenement=self)

    def get_saisons(self):
        # TODO: Gérer les lieux de fin.
        qs = apps.get_model('libretto', 'Saison').objects.filter(
            debut__lte=self.debut_date, fin__gte=self.debut_date)
        extra_where = """
            ensemble_id IN ((
                SELECT ensemble_id
                FROM libretto_elementdedistribution
                WHERE evenement_id = %s
            ) UNION (
                SELECT distribution.ensemble_id
                FROM libretto_elementdeprogramme AS programme
                INNER JOIN libretto_elementdedistribution AS distribution ON (distribution.element_de_programme_id = programme.id)
                WHERE programme.evenement_id = %s))"""
        extra_params = [self.pk, self.pk]
        if self.debut_lieu_id is not None:
            extra_where += ' OR lieu_id = %s'
            extra_params.append(self.debut_lieu_id)

        return qs.extra(where=(extra_where,), params=extra_params)

    def clean(self):
        if self.fin_lieu is not None and self.debut_lieu is None:
            raise ValidationError(
                _('Le lieu de fin est rempli sans lieu de début. '
                  'Merci de retirer le lieu de fin '
                  'ou remplir le lieu de début.'))

    def __str__(self):
        out = self.debut.date_str(False)
        out = capfirst(out)
        out += f'\u00A0> {self.html(False)}'
        return strip_tags(out)

    def related_label(self):
        return href(reverse('admin:libretto_evenement_change',
                            args=(self.pk,)), force_text(self), new_tab=True)

    @staticmethod
    def autocomplete_search_fields():
        return (
            'circonstance__unaccent__icontains',
            'debut_lieu__nom__unaccent__icontains',
            'debut_lieu__parent__nom__unaccent__icontains',
            'debut_date__icontains',
            'debut_heure__icontains',
            'debut_lieu_approx__unaccent__icontains',
            'debut_date_approx__unaccent__icontains',
            'debut_heure_approx__unaccent__icontains',
        )
