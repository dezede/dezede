# coding: utf-8

from .functions import ex, hlp, str_list, str_list_w_last, href, cite
from django.db.models import CharField, ManyToManyField, \
                             PositiveIntegerField, FloatField, ForeignKey, \
                             OneToOneField, IntegerField, TextField, \
                             permalink, get_model
from tinymce.models import HTMLField
from django.utils.html import strip_tags
from django.utils.translation import ungettext_lazy, ugettext, \
                                     ugettext_lazy as _
from django.template.defaultfilters import capfirst
from django.contrib.humanize.templatetags.humanize import apnumber
from .common import CustomModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, \
                    calc_pluriel, SlugModel, UniqueSlugModel, CustomManager, \
                    CustomQuerySet
from django.core.exceptions import ValidationError
from collections import defaultdict
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.generic import GenericRelation


class GenreDOeuvre(CustomModel, SlugModel):
    nom = CharField(max_length=255, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=430, blank=True,
        verbose_name=_('nom (au pluriel)'),
        help_text=PLURAL_MSG)
    parents = ManyToManyField('GenreDOeuvre', related_name='enfants',
        blank=True, null=True)

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
        return 'nom__icontains', 'nom_pluriel__icontains',


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
        return 'type__nom__icontains', 'valeur__icontains',


class Partie(CustomModel):
    nom = CharField(max_length=200,
        help_text=_(u'Le nom d’une partie de la partition, '
                    u'instrumentale ou vocale.'))
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
        help_text=PLURAL_MSG)
    professions = ManyToManyField('Profession', related_name='parties',
        help_text=_(u'La ou les profession(s) permettant '
                    u'd’assurer cette partie.'))
    parente = ForeignKey('Partie', related_name='enfant', blank=True,
                         null=True, verbose_name=_('parente'))
    classement = FloatField(default=1.0)

    class Meta:
        verbose_name = ungettext_lazy('partie', 'parties', 1)
        verbose_name_plural = ungettext_lazy('partie', 'parties', 2)
        ordering = ['classement', 'nom']
        app_label = 'catalogue'

    def interpretes(self):
        return get_model('catalogue', 'Individu').objects.filter(
                                 attributions_de_pupitre__pupitre__partie=self)

    def pluriel(self):
        return calc_pluriel(self)

    @permalink
    def permalien(self):
        return 'partie_pk', (self.pk,)

    def link(self):
        return href(self.permalien(), self.html())

    def html(self):
        return self.nom

    def __unicode__(self):
        return capfirst(self.nom)

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
    nom_relatif = CharField(max_length=100, help_text=LOWER_MSG, unique=True)
    nom_relatif_pluriel = CharField(max_length=130, blank=True,
        verbose_name=_('nom relatif (au pluriel)'), help_text=PLURAL_MSG)
    classement = FloatField(default=1.0)

    class Meta:
        verbose_name = ungettext_lazy(u'type de parenté d’œuvres',
                                      u'types de parentés d’œuvres', 1)
        verbose_name_plural = ungettext_lazy(u'type de parenté d’œuvres',
                                             u'types de parentés d’œuvres', 2)
        ordering = ['classement']
        app_label = 'catalogue'

    def relatif_pluriel(self):
        return calc_pluriel(self, attr_base='nom_relatif')

    def __unicode__(self):
        return '< %s | %s >' % (self.nom, self.nom_relatif)


class ParenteDOeuvres(CustomModel):
    type = ForeignKey('TypeDeParenteDOeuvres', related_name='parentes')
    mere = ForeignKey('Oeuvre', related_name='parentes_filles',
                      verbose_name=_(u'œuvre mère'))
    fille = ForeignKey('Oeuvre', related_name='parentes_meres',
                       verbose_name=_(u'œuvre fille'))

    class Meta:
        verbose_name = ungettext_lazy(u'parenté d’œuvres',
                                      u'parentés d’œuvres', 1)
        verbose_name_plural = ungettext_lazy(u'parenté d’œuvres',
                                             u'parentés d’œuvres', 2)
        ordering = ['type']
        app_label = 'catalogue'
        unique_together = ('type', 'mere', 'fille',)

    def __unicode__(self):
        return u'%s %s %s' % (self.fille, self.type.nom, self.mere)

    def clean(self):
        try:
            type, mere, fille = self.type, self.mere, self.fille
            if mere == fille:
                raise ValidationError(_(u'Les deux champs de parenté ne '
                                        u'peuvent pas être identiques'))
            if ParenteDOeuvres.objects.filter(mere=fille,
                                              fille=mere).exists():
                raise ValidationError(_(u'Une relation entre ces deux objets '
                                        u'existe déjà dans le sens inverse'))
        except Oeuvre.DoesNotExist:
            pass


class AuteurQuerySet(CustomQuerySet):
    def html(self, tags=True):
        auteurs = self
        d = defaultdict(list)
        for auteur in auteurs:
            d[auteur.profession].append(auteur.individu)
        return str_list(
            '%s [%s]' % (str_list_w_last(i.html(tags) for i in ins),
                         p.short_html(tags))
                for p, ins in d.iteritems())


class AuteurManager(CustomManager):
    """
    Manager personnalisé pour utiliser CustomQuerySet par défaut.
    """
    def get_query_set(self):
        return AuteurQuerySet(self.model, using=self._db)


class Auteur(CustomModel):
    content_type = ForeignKey(ContentType)
    object_id = PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    individu = ForeignKey('Individu', related_name='auteurs',
                          verbose_name=_('individu'))
    profession = ForeignKey('Profession', related_name='auteurs',
                            verbose_name=_('profession'))
    objects = AuteurManager()

    def html(self, tags=True):
        return Auteur.objects.filter(pk=self.pk).html(tags)
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def clean(self):
        self.individu.professions.add(self.profession)

    class Meta:
        verbose_name = ungettext_lazy('auteur', 'auteurs', 1)
        verbose_name_plural = ungettext_lazy('auteur', 'auteurs', 2)
        ordering = ['profession', 'individu__nom']
        app_label = 'catalogue'

    def __unicode__(self):
        return self.html(tags=False)


class Oeuvre(AutoriteModel, UniqueSlugModel):
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
    auteurs = GenericRelation('Auteur', related_name='oeuvres')
    ancrage_creation = OneToOneField('AncrageSpatioTemporel',
        related_name='oeuvres_creees', blank=True, null=True,
        verbose_name=_(u'ancrage spatio-temporel de création'))
    pupitres = ManyToManyField('Pupitre', related_name='oeuvres', blank=True,
        null=True)
    filles = ManyToManyField('Oeuvre', through='ParenteDOeuvres',
                             related_name='meres', symmetrical=False)
    lilypond = TextField(blank=True, verbose_name='LilyPond')
    description = HTMLField(blank=True)
    evenements = ManyToManyField('Evenement', through='ElementDeProgramme',
                                 related_name='oeuvres')

    @permalink
    def get_absolute_url(self):
        return 'oeuvre', [self.slug]

    @permalink
    def permalien(self):
        return 'oeuvre_pk', [self.pk]

    def link(self):
        return self.html(tags=True, auteurs=False, titre=True, descr=True,
                         parentes=True)
    link.short_description = _('lien')
    link.allow_tags = True

    def individus_auteurs(self):
        return get_model('catalogue', 'Individu').objects.filter(
                                              auteurs__oeuvres=self).distinct()

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

    def auteurs_html(self, tags=True):
        return self.auteurs.all().html(tags)
    auteurs_html.short_description = _('auteurs')
    auteurs_html.allow_tags = True
    auteurs_html.admin_order_field = 'auteurs__individu'

    def calc_parentes(self, tags=True):
        if not self.pk:
            return ''
        return str_list_w_last(unicode(m) for m in self.meres.all())

    def __parentes_html(self, tags=True, relation='mere',
                        type_select='type__nom'):
        d = defaultdict(list)
        parentes = getattr(self, 'parentes_' + relation + 's')
        for k, v in parentes.values_list(type_select, relation):
            d[k].append(v)
        l = []
        for type, id_list in d.items():
            oeuvres = Oeuvre.objects.in_bulk(id_list).values()
            pre = capfirst(type) + ' : '
            l.append(pre + ', '.join(o.titre_descr_html(tags)
                                                             for o in oeuvres))
        infix = '<br />' if tags else '\n'
        return infix.join(l)

    def meres_html(self, tags=True):
        return self.__parentes_html(tags, relation='mere',
                                    type_select='type__nom')

    def filles_html(self, tags=True):
        return self.__parentes_html(tags, relation='fille',
                                    type_select='type__nom_relatif')

    def titre_complet(self):
        l = (self.prefixe_titre, self.titre, self.coordination,
             self.prefixe_titre_secondaire, self.titre_secondaire)
        return str_list(l, infix='')

    def html(self, tags=True, auteurs=True, titre=True,
             descr=True, genre_caps=True, parentes=True):
        # FIXME: Nettoyer cette horreur
        out = ''
        auts = self.auteurs_html(tags)
        pars = self.calc_parentes(tags)
        titre_complet = self.titre_complet()
        genre = self.genre
        caracteristiques = self.calc_caracteristiques(tags=tags)
        url = None if not tags else self.get_absolute_url()
        if auteurs and auts:
            out += auts + ', '
        if titre:
            if parentes and pars:
                out += pars + ', '
            if titre_complet:
                out += href(url, cite(titre_complet, tags), tags)
                if descr and genre:
                    out += ', '
        if genre:
            genre = genre.html(tags, caps=genre_caps)
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
        return self.html(tags, auteurs=False, titre=True, descr=False,
                         parentes=False)

    def titre_descr_html(self, tags=True):
        return self.html(tags, auteurs=False, titre=True, descr=True,
                         parentes=False)

    def description_html(self, tags=True):
        return self.html(tags, auteurs=False, titre=False, descr=True,
                         genre_caps=True)

    def clean(self):
        if not self.titre and not self.genre:
            raise ValidationError(_(u'Un titre ou un genre doit au moins '
                                    u'être précisé.'))

    class Meta:
        verbose_name = ungettext_lazy(u'œuvre', u'œuvres', 1)
        verbose_name_plural = ungettext_lazy(u'œuvre', u'œuvres', 2)
        ordering = ['genre', 'slug']
        app_label = 'catalogue'

    def __unicode__(self):
        return strip_tags(self.titre_html(False))  # strip_tags car on autorise
                         # les rédacteurs à mettre des tags dans les CharFields

    @staticmethod
    def autocomplete_search_fields():
        return ('prefixe_titre__icontains', 'titre__icontains',
                'prefixe_titre_secondaire__icontains',
                'titre_secondaire__icontains', 'genre__nom__icontains',)
