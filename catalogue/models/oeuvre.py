# coding: utf-8

from .functions import ex, hlp, str_list, str_list_w_last, href, cite
from django.db.models import CharField, ManyToManyField, \
                             FloatField, ForeignKey, OneToOneField, \
                             IntegerField, TextField, permalink, get_model
from tinymce.models import HTMLField
from ..templatetags.extras import abbreviate
from django.utils.html import strip_tags
from django.utils.translation import ungettext_lazy, ugettext, \
                                     ugettext_lazy as _
from django.template.defaultfilters import capfirst
from django.contrib.humanize.templatetags.humanize import apnumber
from autoslug import AutoSlugField
from .common import CustomModel, LOWER_MSG, PLURAL_MSG, calc_pluriel


class GenreDOeuvre(CustomModel):
    nom = CharField(max_length=255, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=430, blank=True,
        verbose_name=_('nom (au pluriel)'),
        help_text=PLURAL_MSG)
    parents = ManyToManyField('GenreDOeuvre', related_name='enfants',
        blank=True, null=True)
    slug = AutoSlugField(populate_from=unicode)

    class Meta:
        verbose_name = ungettext_lazy(u'genre d’œuvre', u'genres d’œuvre', 1)
        verbose_name_plural = ungettext_lazy(u'genre d’œuvre',
                                             u'genres d’œuvre', 2)
        ordering = ['slug']
        app_label = 'catalogue'

    def html(self, tags=True, caps=False, pluriel=False):
        nom = self.pluriel() if pluriel else self.nom
        if caps:
            nom = capfirst(nom)
        return hlp(nom, ugettext('genre'), tags)

    def pluriel(self):
        return calc_pluriel(self)

    def __unicode__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'nom_pluriel__icontains',)


class TypeDeCaracteristiqueDOeuvre(CustomModel):
    nom = CharField(max_length=200, help_text=ex(_(u'tonalité')), unique=True)
    nom_pluriel = CharField(max_length=230, blank=True,
        verbose_name=_('nom (au pluriel)'), help_text=PLURAL_MSG)
    classement = FloatField(default=1.0)

    class Meta:
        verbose_name = ungettext_lazy(u'type de caractéristique d’œuvre',
                                      u'types de caracteristique d’œuvre', 1)
        verbose_name_plural = ungettext_lazy(
                u'type de caractéristique d’œuvre',
                u'types de caracteristique d’œuvre',
                2)
        ordering = ['classement']
        app_label = 'catalogue'

    def pluriel(self):
        return calc_pluriel(self)

    def __unicode__(self):
        return self.nom


class CaracteristiqueDOeuvre(CustomModel):
    type = ForeignKey('TypeDeCaracteristiqueDOeuvre',
        related_name='caracteristiques_d_oeuvre')
    # TODO: Changer valeur en nom ?
    valeur = CharField(max_length=400, help_text=ex(_(u'en trois actes')))
    classement = FloatField(default=1.0,
        help_text=_(u'''Par exemple, on peut choisir de classer'''
                    u'''les découpages par nombre d’actes.'''))

    class Meta:
        verbose_name = ungettext_lazy(u'caractéristique d’œuvre',
                                      u'caractéristiques d’œuvre', 1)
        verbose_name_plural = ungettext_lazy(u'caractéristique d’œuvre',
                                             u'caractéristiques d’œuvre', 2)
        ordering = ['type', 'classement']
        app_label = 'catalogue'

    def html(self, tags=True):
        return hlp(self.valeur, self.type, tags)
    html.allow_tags = True

    def __unicode__(self):
        return unicode(self.type) + ' : ' + strip_tags(self.valeur)

    @staticmethod
    def autocomplete_search_fields():
        return ('type__nom__icontains', 'valeur__icontains',)


class Partie(CustomModel):
    nom = CharField(max_length=200,
        help_text=_(u'''Le nom d’une partie de la partition, '''
                    u'''instrumentale ou vocale.'''))
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
        help_text=PLURAL_MSG)
    professions = ManyToManyField('Profession', related_name='parties',
        help_text=_(u'''La ou les profession(s) permettant '''
                    u'''d’assurer cette partie.'''))
    parente = ForeignKey('Partie',
        related_name='enfant', blank=True, null=True)
    classement = FloatField(default=1.0)

    class Meta:
        verbose_name = ungettext_lazy('partie', 'parties', 1)
        verbose_name_plural = ungettext_lazy('partie', 'parties', 2)
        ordering = ['classement', 'nom']
        app_label = 'catalogue'

    def interpretes(self):
        return get_model('catalogue', 'Individu').objects.filter(attributions_de_pupitre__pupitre__partie=self)

    def pluriel(self):
        return calc_pluriel(self)

    @permalink
    def permalien(self):
        return 'partie_pk', (self.pk,)

    def link(self):
        return href(self.permalien(), unicode(self))

    def __unicode__(self):
        return self.nom

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'nom_pluriel__icontains',
                'professions__nom__icontains',
                'professions__nom_pluriel__icontains',)


class Pupitre(CustomModel):
    partie = ForeignKey('Partie', related_name='pupitres')
    quantite_min = IntegerField(_(u'quantité minimale'), default=1)
    quantite_max = IntegerField(_(u'quantité maximale'), default=1)

    class Meta:
        verbose_name = ungettext_lazy('pupitre', 'pupitres', 1)
        verbose_name_plural = ungettext_lazy('pupitre', 'pupitres', 2)
        ordering = ['partie']
        app_label = 'catalogue'

    def __unicode__(self):
        out = ''
        partie = self.partie
        mi = self.quantite_min
        ma = self.quantite_max
        if ma > 1:
            partie = partie.pluriel()
        else:
            partie = unicode(partie)
        mi_str = apnumber(mi)
        ma_str = apnumber(ma)
        if mi != ma:
            d = {'min': mi_str, 'max': ma_str}
            out += ugettext(u'%(min)s à %(max)s ') % d
        elif mi > 1:
            out += mi_str + ' '
        out += partie
        return out

    @staticmethod
    def autocomplete_search_fields():
        return ('partie__nom__icontains', 'partie__nom_pluriel__icontains',
                'partie__professions__nom__icontains',
                'partie__professions__nom_pluriel__icontains',)


class TypeDeParenteDOeuvres(CustomModel):
    nom = CharField(max_length=100, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=130, blank=True,
        verbose_name=_('nom (au pluriel)'),
        help_text=PLURAL_MSG)
    classement = FloatField(default=1.0)

    class Meta:
        verbose_name = ungettext_lazy(u'type de parenté d’œuvres',
                                      u'types de parentés d’œuvres', 1)
        verbose_name_plural = ungettext_lazy(u'type de parenté d’œuvres',
                                             u'types de parentés d’œuvres', 2)
        ordering = ['classement']
        app_label = 'catalogue'

    def pluriel(self):
        return calc_pluriel(self)

    def __unicode__(self):
        return self.nom


class ParenteDOeuvres(CustomModel):
    type = ForeignKey('TypeDeParenteDOeuvres', related_name='parentes')
    oeuvres_cibles = ManyToManyField('Oeuvre',
        related_name='enfances_cibles', verbose_name=_(u'œuvres cibles'))

    class Meta:
        verbose_name = ungettext_lazy(u'parenté d’œuvres',
                                      u'parentés d’œuvres', 1)
        verbose_name_plural = ungettext_lazy(u'parenté d’œuvres',
                                             u'parentés d’œuvres', 2)
        ordering = ['type']
        app_label = 'catalogue'

    def __unicode__(self):
        out = self.type.nom
        cs = self.oeuvres_cibles
        if cs.count() > 1:
            out = self.type.pluriel()
        out += ' : '
        out += str_list((unicode(c) for c in cs.iterator()), ' ; ')
        return out


class Auteur(CustomModel):
    profession = ForeignKey('Profession', related_name='auteurs')
    individus = ManyToManyField('Individu', related_name='auteurs')

    def individus_html(self, tags=True):
        ins = self.individus.iterator()
        return str_list_w_last(i.html(tags) for i in ins)

    def html(self, tags=True):
        individus = self.individus_html(tags)
        prof = abbreviate(unicode(self.profession), 1)
        out = '%s [%s]' % (individus, prof)
        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    class Meta:
        verbose_name = ungettext_lazy('auteur', 'auteurs', 1)
        verbose_name_plural = ungettext_lazy('auteur', 'auteurs', 2)
        ordering = ['profession']
        app_label = 'catalogue'

    def __unicode__(self):
        return strip_tags(self.html(False))


class Oeuvre(CustomModel):
    prefixe_titre = CharField(max_length=20, blank=True,
        verbose_name=_(u'préfixe du titre'))
    titre = CharField(max_length=200, blank=True)
    coordination = CharField(max_length=20, blank=True,
        verbose_name=_('coordination'))
    prefixe_titre_secondaire = CharField(max_length=20, blank=True,
        verbose_name=_(u'préfixe du titre secondaire'))
    titre_secondaire = CharField(max_length=200, blank=True,
        verbose_name=_('titre secondaire'))
    genre = ForeignKey('GenreDOeuvre', related_name='oeuvres', blank=True,
        null=True)
    caracteristiques = ManyToManyField('CaracteristiqueDOeuvre', blank=True,
        null=True, verbose_name=_(u'caractéristiques'))
    auteurs = ManyToManyField('Auteur', related_name='oeuvres', blank=True,
        null=True)
    ancrage_composition = OneToOneField('AncrageSpatioTemporel',
        related_name='oeuvres', blank=True, null=True,
        verbose_name=_(u'ancrage spatio-temporel de composition'))
    pupitres = ManyToManyField('Pupitre', related_name='oeuvres', blank=True,
        null=True)
    parentes = ManyToManyField('ParenteDOeuvres', related_name='oeuvres',
        blank=True, null=True, verbose_name=_(u'parentés'))
    lilypond = TextField(blank=True, verbose_name='LilyPond')
    description = HTMLField(blank=True)
    documents = ManyToManyField('Document', related_name='oeuvres', blank=True,
        null=True)
    illustrations = ManyToManyField('Illustration', related_name='oeuvres',
        blank=True, null=True)
    etat = ForeignKey('Etat', related_name='oeuvres', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = AutoSlugField(populate_from=unicode)

    @permalink
    def get_absolute_url(self):
        return ('oeuvre', [self.slug])

    @permalink
    def permalien(self):
        return ('oeuvre_pk', [self.pk])

    def link(self):
        return self.html(True, False, True, True)
    link.short_description = _('lien')
    link.allow_tags = True

    def individus_auteurs(self):
        pk_list = self.auteurs.values_list('individus', flat=True)
        return get_model('catalogue',
                         'Individu').objects.in_bulk(pk_list).values()

    def enfants(self):
        pk_list = self.enfances_cibles.values_list('oeuvres', flat=True)
        return Oeuvre.objects.in_bulk(pk_list).values()

    def evenements(self):
        pk_list = self.elements_de_programme.values_list('evenements',
                                                         flat=True)
        return get_model('catalogue',
                         'Evenement').objects.in_bulk(pk_list).values()

    def calc_caracteristiques(self, limite=0, tags=True):
        if not self.pk:
            return ''
        cs = self.caracteristiques.all()

        def clist(cs):
            return str_list(c.html(tags) for c in cs)
        out2 = clist(cs[limite:])
        if limite:
            out1 = clist(cs[:limite])
            return out1, out2
        return out2
    calc_caracteristiques.allow_tags = True
    calc_caracteristiques.short_description = _(u'caractéristiques')
    calc_caracteristiques.admin_order_field = 'caracteristiques__valeur'

    def calc_pupitres(self):
        if not self.pk:
            return ''
        out = ''
        ps = self.pupitres
        if ps.exists():
            out += ugettext('pour ')
            out += str_list_w_last(unicode(p) for p in ps.iterator())
        return out

    def calc_auteurs(self, tags=True):
        if not self.pk:
            return ''
        auteurs = self.auteurs.iterator()
        return str_list(a.html(tags) for a in auteurs)
    calc_auteurs.short_description = _('auteurs')
    calc_auteurs.allow_tags = True
    calc_auteurs.admin_order_field = 'auteurs__individus'

    def calc_parentes(self, tags=True):
        if not self.pk:
            return ''
        out = ''
        ps = self.parentes.iterator()
        for p in ps:
            l = (oe.html(tags, False, True, False)
                                         for oe in p.oeuvres_cibles.iterator())
            out += str_list_w_last(l)
            out += ', '
        return out

    def titre_complet(self):
        l = (self.prefixe_titre, self.titre, self.coordination,
             self.prefixe_titre_secondaire, self.titre_secondaire)
        return str_list(l, infix='')

    def html(self, tags=True, auteurs=True, titre=True,
             descr=True, caps_genre=False):
        # FIXME: Nettoyer cette horreur
        out = ''
        auts = self.calc_auteurs(tags)
        parentes = self.calc_parentes(tags)
        titre_complet = self.titre_complet()
        genre = self.genre
        caracteristiques = self.calc_caracteristiques(tags=tags)
        url = None if not tags else self.get_absolute_url()
        if auteurs and auts:
            out += auts + ', '
        if titre:
            out += parentes
            if titre_complet:
                out += href(url, cite(titre_complet, tags), tags)
                if descr and genre:
                    out += ', '
        if genre:
            genre = genre.html(tags, caps=caps_genre)
            pupitres = self.calc_pupitres()
            if not titre_complet:
                cs = None
                titre_complet = self.genre.html(tags, caps=True)
                if pupitres:
                    titre_complet += ' ' + pupitres
                elif caracteristiques:
                    cs = self.calc_caracteristiques(1, tags)
                    titre_complet += ' ' + cs[0]
                    caracteristiques = cs[1]
                if not parentes:
                    titre_complet = cite(titre_complet, tags)
                if titre:
                    out += href(url, titre_complet, tags)
                    if descr and cs and cs[1]:
                        out += ','
            elif descr:
                out += genre
        if descr and caracteristiques:
            if out:
                # TODO: BUG : le validateur HTML supprime l'espace qu'on ajoute
                #       ci-dessous si on ne le met pas en syntaxe HTML
                if tags:
                    out += '&#32;'
                else:
                    out += ' '
            out += caracteristiques
        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def titre_html(self, tags=True):
        return self.html(tags, False, True, False)

    def description_html(self, tags=True):
        return self.html(tags, False, False, True, caps_genre=True)

    class Meta:
        verbose_name = ungettext_lazy(u'œuvre', u'œuvres', 1)
        verbose_name_plural = ungettext_lazy(u'œuvre', u'œuvres', 2)
        ordering = ['genre', 'slug']
        app_label = 'catalogue'

    def __unicode__(self):
        return strip_tags(self.titre_html(False))

    @staticmethod
    def autocomplete_search_fields():
        return ('prefixe_titre__icontains', 'titre__icontains',
                'prefixe_titre_secondaire__icontains',
                'titre_secondaire__icontains', 'genre__nom__icontains',)
