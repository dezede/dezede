# coding: utf-8
from django.db.models import *
from tinymce.models import HTMLField
from django.template.defaultfilters import slugify
from filebrowser.fields import FileBrowseField
from musicologie.catalogue.templatetags.extras import replace, abbreviate
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.functional import allow_lazy
from django.template.defaultfilters import date, time, capfirst
from django.contrib.humanize.templatetags.humanize import apnumber

#
# Définitions globales du fichier
#

LOWER_MSG = _(u'En minuscules.')
PLURAL_MSG = _(u'À remplir si le pluriel n\'est pas un simple ajout de « s ».  Exemple : « animal » devient « animaux » et non « animals ».')
DATE_MSG = _(u'Ex. : « 6/6/1944 » pour le 6 juin 1944.')

@classmethod
def class_name(cls):
    return unicode(cls.__name__)
Model.class_name = class_name

def autoslugify(obj, nom):
    nom_slug = slug_orig = slugify(nom[:50])
    n = 0
    objects = obj.__class__.objects
    while objects.filter(slug=nom_slug).count() and nom_slug != obj.slug:
        n += 1;
        nom_slug = slug_orig + str(n)
    return nom_slug

def date_html(d, tags=True):
    pre = date(d, 'l')
    post = date(d, 'F Y')
    j = date(d, 'j')
    if j == '1':
        k = ugettext('er')
        if tags:
            k = '<sup>%s</sup>' % k
        j += k
    return '%s %s %s' % (pre, j, post)

def str_list(l, infix=', ', last_infix=None):
    l = filter(bool, l)
    suffix = ''
    if len(l) > 1 and last_infix:
        suffix = last_infix + l.pop()
    return infix.join(l) + suffix

def str_list_w_last(l, infix=', ', last_infix=' et '):
    return str_list(l, infix, last_infix)

def calc_pluriel(obj):
    try:
        if obj.nom_pluriel:
            return obj.nom_pluriel
        return obj.nom + 's'
    except:
        return unicode(obj)

def ex(txt):
    return _(u'Exemple : « %s »') % txt
ex = allow_lazy(ex, unicode)

def no(txt):
    return _(u'n°\u00A0%s') % txt

# Fonctions HTML

def cite(txt, tags=True):
    if tags:
        return u'<cite>%s</cite>' % txt
    return txt

def href(url, txt, tags=True):
    if tags:
        return u'<a href="%s">%s</a>' % (url, txt)
    return txt

def sc(txt, tags=True):
    if tags:
        return u'<span class="sc">%s</span>' % txt
    return txt

def hlp(txt, title, tags=True):
    if tags:
        return u'<span title="%s">%s</span>' % (title, txt)
    return txt

def small(txt, tags=True):
    if tags:
        return u'<small>%s</small>' % txt
    return txt

#
# Modélisation
#

def save(self, *args, **kwargs):
    try:
        for field in self._meta.fields:
            if field.__class__.__name__ in ['CharField', 'HTMLField']:
                value = replace(getattr(self, field.attname))
                setattr(self, field.attname, value)
    except:
        pass
    self._old_save(*args, **kwargs)

Model._old_save = Model.save
Model.save = save

SlugField.unique = True

class Document(Model):
    nom = CharField(max_length=300, blank=True)
    document = FileBrowseField('Document', max_length=400, directory='documents/')
    description = HTMLField(blank=True)
    auteurs = ManyToManyField('Auteur', related_name='documents', blank=True,
        null=True)
    class Meta:
        verbose_name = _('document')
        verbose_name_plural = _('documents')
        ordering = ['document']
    def __unicode__(self):
        if self.nom:
            return self.nom
        return self.document.__unicode__()
    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'document__icontains',
                'description__icontains', 'auteurs__individus__nom',)

class Illustration(Model):
    legende = CharField(max_length=300, blank=True, verbose_name=_(u'légende'))
    image = FileBrowseField('Image', max_length=400, directory='images/')
    commentaire = HTMLField(blank=True)
    auteurs = ManyToManyField('Auteur', related_name='illustrations',
        blank=True, null=True)
    class Meta:
        verbose_name = _('illustration')
        verbose_name_plural = _('illustrations')
        ordering = ['image']
    def __unicode__(self):
        if self.legende:
            return self.legende
        return self.image.__unicode__()
    @staticmethod
    def autocomplete_search_fields():
        return ('legende__icontains', 'image__icontains',
                'commentaire__icontains', 'auteurs__individus__nom',)

class Etat(Model):
    nom = CharField(max_length=200, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=230, blank=True,
        verbose_name=_('nom (au pluriel)'), help_text=PLURAL_MSG)
    message = HTMLField(blank=True,
        help_text=_(u'Message à afficher dans la partie consultation.'))
    publie = BooleanField(default=True, verbose_name=_(u'publié'))
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = _(u'état')
        verbose_name_plural = _(u'états')
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(self, self.__unicode__())
        super(Etat, self).save(*args, **kwargs)
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class NatureDeLieu(Model):
    nom = CharField(max_length=255, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=430, blank=True,
                            verbose_name=_('nom (au pluriel)'),
                            help_text=PLURAL_MSG)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = _('nature de lieu')
        verbose_name_plural = _('natures de lieu')
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(self, self.__unicode__())
        super(NatureDeLieu, self).save(*args, **kwargs)
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom
    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains',)

class Lieu(Model):
    nom = CharField(max_length=200)
    parent = ForeignKey('Lieu', related_name='enfants', null=True, blank=True)
    nature = ForeignKey(NatureDeLieu, related_name='lieux')
    historique = HTMLField(blank=True)
    illustrations = ManyToManyField(Illustration, related_name='lieux',
        blank=True, null=True)
    documents = ManyToManyField(Document, related_name='lieux', blank=True,
        null=True)
    etat = ForeignKey(Etat, related_name='lieux', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    @permalink
    def get_absolute_url(self):
        return ('musicologie.catalogue.views.detail_lieu', [self.slug])
    def link(self):
        return self.html()
    def short_link(self):
        return self.html(short=True)
    link.short_description = _('permalien')
    link.allow_tags = True
    def evenements(self): # TODO: gérer les fins d'événements.
        return Evenement.objects.filter(ancrage_debut__lieu=self)
    def individus_nes(self):
        return Individu.objects.filter(ancrage_naissance__lieu=self)
    def individus_decedes(self):
        return Individu.objects.filter(ancrage_deces__lieu=self)
    def oeuvres_composees(self):
        return Oeuvre.objects.filter(ancrage_composition__lieu=self)
    def html(self, tags=True, short=False):
        nom = ''
        parent = self.parent
        if parent and not short:
            nom += parent.nom + ', '
        nom += self.nom
        out = href(self.get_absolute_url(), nom, tags)
        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True
    class Meta:
        verbose_name = _('lieu')
        verbose_name_plural = _('lieux')
        ordering = ['nom']
    def save(self, *args, **kwargs):
        new_slug = slugify(self.nom)
        lieux = Lieu.objects.filter(slug=new_slug)
        if lieux.count() == lieux.filter(pk=self.pk).count():
            self.slug = new_slug
        else:
            self.slug = autoslugify(self, self.__unicode__())
        super(Lieu, self).save(*args, **kwargs)
    def __unicode__(self):
        return strip_tags(self.html(False))
    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains',)

class Saison(Model):
    lieu = ForeignKey(Lieu, related_name='saisons')
    debut = DateField(verbose_name=_(u'début'), help_text=DATE_MSG)
    fin = DateField()
    class Meta:
        verbose_name = _('saison')
        verbose_name_plural = _('saisons')
        ordering = ['lieu', 'debut']
    def __unicode__(self):
        return self.lieu.__unicode__() + ', ' + str(self.debut.year) + '-' + str(self.fin.year)

class Profession(Model):
    nom = CharField(max_length=200, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=230, blank=True,
        verbose_name=_('nom (au pluriel)'), help_text=PLURAL_MSG)
    nom_feminin = CharField(max_length=230, blank=True,
        verbose_name=_(u'nom (au féminin)'),
        help_text=_(u'Ne préciser que s’il est différent du nom.'))
    parente = ForeignKey('Profession', blank=True, null=True,
        related_name='enfant')
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = _('profession')
        verbose_name_plural = _('professions')
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(self, self.__unicode__())
        super(Profession, self).save(*args, **kwargs)
    def pluriel(self):
        return calc_pluriel(self)
    def feminin(self):
        f = self.nom_feminin
        return f if f else self.nom
    def gendered(self, titre='M'):
        return self.nom if titre == 'M' else self.feminin()
    def __unicode__(self):
        return self.nom
    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'nom_pluriel__icontains',)

class AncrageSpatioTemporel(Model):
    date = DateField(blank=True, null=True, help_text=DATE_MSG)
    heure = TimeField(blank=True, null=True)
    lieu = ForeignKey(Lieu, related_name='ancrages', blank=True, null=True)
    date_approx = CharField(max_length=200, blank=True,
        verbose_name=_(u'date approximative'),
        help_text=_(u'Ne remplir que si la date est imprécise.'))
    heure_approx = CharField(max_length=200, blank=True,
        verbose_name=_(u'heure approximative'),
        help_text=_(u'Ne remplir que si l’heure est imprécise.'))
    lieu_approx = CharField(max_length=200, blank=True,
        verbose_name=_(u'lieu approximatif'),
        help_text=_(u'Ne remplir que si le lieu est imprécis.'))
    def year(self):
        if self.date:
            return self.date.year
        return None
    def month(self):
        if self.date:
            return self.date.month
        return None
    def day(self):
        if self.date:
            return self.date.day
        return None
    def calc_date(self, tags=True):
        if self.date:
            return date_html(self.date, tags)
        return self.date_approx
    calc_date.short_description = _('date')
    calc_date.admin_order_field = 'date'
    def calc_heure(self):
        if self.heure:
            return time(self.heure, ugettext('H\hi'))
        return self.heure_approx
    calc_heure.short_description = _('heure')
    calc_heure.admin_order_field = 'heure'
    def calc_moment(self, tags=True):
        l = []
        date = self.calc_date(tags)
        heure = self.calc_heure()
        pat_date = ugettext('le %s') if self.date else ugettext('%s')
        pat_heure = ugettext(u'à %s') if self.heure else ugettext('%s')
        l.append(pat_date % date)
        l.append(pat_heure % heure)
        return str_list(l, ' ')
    def calc_lieu(self, tags=True):
        if self.lieu:
            return self.lieu.html(tags)
        return self.lieu_approx
    calc_lieu.short_description = _('lieu')
    calc_lieu.admin_order_field = 'lieu'
    calc_lieu.allow_tags = True
    def html(self, tags=True):
        l = []
        l.append(self.calc_lieu(tags))
        l.append(self.calc_moment(tags))
        out = str_list(l)
        return capfirst(out)
    class Meta:
        verbose_name = _('ancrage spatio-temporel')
        verbose_name_plural = _('ancrages spatio-temporels')
        ordering = ['date', 'heure', 'lieu', 'date_approx', 'heure_approx', 'lieu_approx']
    def __unicode__(self):
        return strip_tags(self.html(False))
    @staticmethod
    def autocomplete_search_fields():
        return ('lieu__nom__icontains', 'lieu__parent__nom__icontains',
                'date__icontains', 'heure__icontains', 'lieu_approx__icontains',
                'date_approx__icontains', 'heure_approx__icontains',)

class Prenom(Model):
    prenom = CharField(max_length=100, verbose_name=_(u'prénom'))
    classement = FloatField(default=1.0)
    favori = BooleanField(default=True)
    class Meta:
        verbose_name = _(u'prénom')
        verbose_name_plural = _(u'prénoms')
        ordering = ['prenom', 'classement']
    def __unicode__(self):
        return self.prenom
    @staticmethod
    def autocomplete_search_fields():
        return ('prenom__icontains',)

class TypeDeParenteDIndividus(Model):
    nom = CharField(max_length=50, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=55, blank=True, help_text=PLURAL_MSG)
    classement = FloatField(default=1.0)
    class Meta:
        verbose_name = _(u'type de parenté d’individus')
        verbose_name_plural = _(u'types de parenté d’individus')
        ordering = ['classement']
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class ParenteDIndividus(Model):
    type = ForeignKey(TypeDeParenteDIndividus, related_name='parentes')
    individus_cibles = ManyToManyField('Individu',
        related_name='enfances_cibles', verbose_name=_('individus cibles'))
    class Meta:
        verbose_name = _(u'parenté d’individus')
        verbose_name_plural = _(u'parentés d’individus')
        ordering = ['type']
    def __unicode__(self):
        out = self.type.nom
        if len(self.individus_cibles.all()) > 1:
            out = self.type.pluriel()
        out += ' :'
        cs = self.individus_cibles.all()
        out += str_list([c.__unicode__() for c in cs], ' ; ')
        return out

class Individu(Model):
    particule_nom = CharField(max_length=10, blank=True,
        verbose_name=_(u'particule du nom d’usage'))
    nom = CharField(max_length=200, verbose_name=_(u'nom d’usage')) # TODO: rendre ce champ 'blank'
    particule_nom_naissance = CharField(max_length=10, blank=True,
        verbose_name=_('particule du nom de naissance'))
    nom_naissance = CharField(max_length=200, blank=True,
        verbose_name=_('nom de naissance'), help_text=_(u'Ne remplir que s’il est différent du nom d’usage.'))
    prenoms = ManyToManyField(Prenom, related_name='individus', blank=True,
        null=True, verbose_name=_(u'prénoms'))
    pseudonyme = CharField(max_length=200, blank=True)
    DESIGNATIONS = (
        ('S', _(u'Standard (nom, prénoms et pseudonyme)')),
        ('P', _('Pseudonyme (uniquement)')),
        ('L', _('Nom de famille (uniquement)')), # L pour Last name
        ('B', _('Nom de naissance (standard)')), # B pour Birth name
        ('F', _(u'Prénom(s) favori(s) (uniquement)')), # F pour First name
    )
    designation = CharField(max_length=1, choices=DESIGNATIONS, default='S')
    TITRES = (
        ('M', _('M.')),
        ('J', _('Mlle')), # J pour Jouvencelle
        ('F', _('Mme')),
    )
    titre = CharField(max_length=1, choices=TITRES, blank=True)
    ancrage_naissance = OneToOneField(AncrageSpatioTemporel, blank=True,
        null=True, related_name='individus_nes',
        verbose_name=_(u'ancrage de naissance'))
    ancrage_deces = OneToOneField(AncrageSpatioTemporel, blank=True, null=True,
        related_name='individus_decedes', verbose_name=_(u'ancrage du décès'))
    ancrage_approx = OneToOneField(AncrageSpatioTemporel, blank=True, null=True,
        related_name='individus', verbose_name=_(u'ancrage approximatif'),
        help_text=_(u'Ne remplir que si on ne connaît aucune date précise.'))
    professions = ManyToManyField(Profession, related_name='individus',
        blank=True, null=True)
    parentes = ManyToManyField(ParenteDIndividus, related_name='individus_orig',
        blank=True, null=True, verbose_name=_(u'parentés'))
    biographie = HTMLField(blank=True)
    illustrations = ManyToManyField(Illustration, related_name='individus',
        blank=True, null=True)
    documents = ManyToManyField(Document, related_name='individus',blank=True,
        null=True)
    etat = ForeignKey(Etat, related_name='individus', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    @permalink
    def get_absolute_url(self):
        return ('musicologie.catalogue.views.detail_individu', [self.slug],)
    def link(self):
        return self.html()
    link.short_description = _('permalien')
    link.allow_tags = True
    def oeuvres(self):
        q = Oeuvre.objects.none()
        for auteur in self.auteurs.all():
            q |= auteur.oeuvres.all()
        return q.distinct().order_by('titre')
    def publications(self):
        q = Source.objects.none()
        for auteur in self.auteurs.all():
            q |= auteur.sources.all()
        return q.distinct()
    def apparitions(self):
        q = Evenement.objects.none()
        els = ElementDeProgramme.objects.none()
        for attribution in self.attributions_de_pupitre.all():
            els |= attribution.elements_de_programme.all()
        for el in els.distinct():
            q |= el.evenements.all()
        return q.distinct()
    def parents(self):
        q = Individu.objects.none()
        for parente in self.parentes.all():
            q |= parente.individus_cibles.all()
        return q.distinct().order_by('nom')
    def enfants(self):
        q = Individu.objects.none()
        for enfance in self.enfances_cibles.all():
            q |= enfance.individus_orig.all()
        return q.distinct().order_by('nom')
    def calc_prenoms_methode(self, fav):
        prenoms = self.prenoms.all().order_by('classement', 'prenom')
        if fav:
            prenoms = filter(lambda p: p.favori, prenoms)
        return ' '.join([p.__unicode__() for p in prenoms])
    def calc_prenoms(self):
        return self.calc_prenoms_methode(False)
    calc_prenoms.short_description = _(u'prénoms')
    def calc_fav_prenoms(self):
        return self.calc_prenoms_methode(True)
    def calc_titre(self, tags=False):
        titres = {}
        if tags:
            titres = {'M': ugettext('M.'), 'J': ugettext('M<sup>lle</sup>'), 'F': ugettext('M<sup>me</sup>'),}
        else:
            titres = {'M': ugettext('Monsieur'), 'J': ugettext('Mademoiselle'), 'F': ugettext('Madame'),}
        if self.titre:
            return titres[self.titre]
        return ''
    def naissance(self):
        if self.ancrage_naissance:
            return self.ancrage_naissance.__unicode__()
        return ''
    def deces(self):
        if self.ancrage_deces:
            return self.ancrage_deces.__unicode__()
        return ''
    def ancrage(self):
        if self.ancrage_approx:
            return self.ancrage_approx.__unicode__()
        return ''
    def calc_professions(self):
        ps = self.professions.all()
        titre = self.titre
        return str_list_w_last([p.gendered(titre) for p in ps])
    calc_professions.short_description = _('professions')
    def html(self, tags=True, lon=False, prenoms_fav=True, force_standard=False):
        designation = self.designation
        titre = self.calc_titre(tags)
        prenoms = self.calc_prenoms_methode(prenoms_fav)
        nom = self.particule_nom + self.nom
        pseudonyme = self.pseudonyme
        nom_naissance = self.particule_nom_naissance + self.nom_naissance
        def main_style(s):
            return sc(s, tags)
        def standard(main):
            l, out = [], ''
            if nom and not prenoms:
                l.append(titre)
            l.append(main)
            if prenoms:
                if lon:
                    l.insert(max(len(l)-1, 0), prenoms)
                else:
                    l.append(u'(%s)' % abbreviate(prenoms))
            out = str_list(l, ' ')
            if pseudonyme:
                out += ugettext(u', dit%(feminin)s %(pseudonyme)s') % \
                    {'feminin': '' if self.titre == 'M' else 'e',
                     'pseudonyme': pseudonyme}
            return out
        main_choices = {
          'S': nom,
          'F': prenoms,
          'L': nom,
          'P': pseudonyme,
          'B': nom_naissance,
        }
        main = main_style(main_choices['S' if force_standard else designation])
        out = standard(main) if designation in ('S', 'B',) or force_standard else main
        url = ''
        if tags:
            url = self.get_absolute_url()
        out = href(url, out, tags)
        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True
    def nom_complet(self, tags=True, prenoms_fav=True, force_standard=True):
        return self.html(tags, True, prenoms_fav, force_standard)
    class Meta:
        verbose_name = _('individu')
        verbose_name_plural = _('individus')
        ordering = ['nom']
    def save(self, *args, **kwargs):
        super(Individu, self).save(*args, **kwargs)
        self.slug = autoslugify(self, self.__unicode__())
        if self.nom:
            new_slug = slugify(self.nom)
            individus = Individu.objects.filter(slug=new_slug)
            if not individus:
                self.slug = new_slug
        super(Individu, self).save(*args, **kwargs)
    def __unicode__(self):
        return strip_tags(self.html(False))
    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'nom_naissance__icontains',
                'pseudonyme__icontains', 'prenoms__prenom__icontains',)

class Devise(Model):
    u'''
    Modélisation naïve d’une unité monétaire.
    '''
    nom = CharField(max_length=200, blank=True, help_text=ex(_('euro')), unique=True)
    symbole = CharField(max_length=10, help_text=ex(_(u'€')), unique=True)
    class Meta:
        verbose_name = _('devise')
        verbose_name_plural = _('devises')
    def __unicode__(self):
        if self.nom:
            return self.nom
        return self.symbole

class Engagement(Model):
    individus = ManyToManyField(Individu, related_name='engagements')
    profession = ForeignKey(Profession, related_name='engagements')
    salaire = FloatField(blank=True)
    devise = ForeignKey(Devise, blank=True, null=True,
        related_name='engagements')
    class Meta:
        verbose_name = _('engagement')
        verbose_name_plural = _('engagements')
    def __unicode__(self):
        return self.profession.nom

class TypeDePersonnel(Model):
    nom = CharField(max_length=100, unique=True)
    class Meta:
        verbose_name = _('type de personnel')
        verbose_name_plural = _('types de personnel')
        ordering = ['nom']
    def __unicode__(self):
        return self.nom

class Personnel(Model):
    type = ForeignKey(TypeDePersonnel, related_name='personnels')
    saison = ForeignKey(Saison, related_name='personnels')
    engagements = ManyToManyField(Engagement, related_name='personnels')
    class Meta:
        verbose_name = _('personnel')
        verbose_name_plural = _('personnels')
    def __unicode__(self):
        return self.type.__unicode__() + self.saison.__unicode__()

class GenreDOeuvre(Model):
    nom = CharField(max_length=255, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=430, blank=True,
        verbose_name=_('nom (au pluriel)'),
        help_text=PLURAL_MSG)
    parents = ManyToManyField('GenreDOeuvre', related_name='enfants',
        blank=True, null=True)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name=_(u'genre d’œuvre')
        verbose_name_plural=_(u'genres d’œuvre')
        ordering = ['slug']
    def html(self, tags=True, caps=False, pluriel=False):
        nom = self.pluriel() if pluriel else self.nom
        if caps:
            nom = capfirst(nom)
        return hlp(nom, ugettext('genre'), tags)
    def save(self, *args, **kwargs):
        self.slug = autoslugify(self, self.__unicode__())
        super(GenreDOeuvre, self).save(*args, **kwargs)
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return strip_tags(self.html(False))
    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'nom_pluriel__icontains',)

class TypeDeCaracteristiqueDOeuvre(Model):
    nom = CharField(max_length=200, help_text=ex(_(u'tonalité')), unique=True)
    nom_pluriel = CharField(max_length=230, blank=True,
        verbose_name=_('nom (au pluriel)'), help_text=PLURAL_MSG)
    classement = FloatField(default=1.0)
    class Meta:
        verbose_name = _(u'type de caractéristique d’œuvre')
        verbose_name_plural = _(u'types de caracteristique d’œuvre')
        ordering = ['classement']
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class CaracteristiqueDOeuvre(Model):
    type = ForeignKey(TypeDeCaracteristiqueDOeuvre, related_name='caracteristiques_d_oeuvre')
    valeur = CharField(max_length=400, help_text=ex(_(u'en trois actes')))
    classement = FloatField(default=1.0,
        help_text=_(u'Par exemple, on peut choisir de classer les découpages par nombre d’actes.'))
    class Meta:
        verbose_name = _(u'caractéristique d’œuvre')
        verbose_name_plural = _(u'caractéristiques d’œuvre')
        ordering = ['type', 'classement']
    def html(self, tags=True):
        return hlp(self.valeur, self.type, tags)
    html.allow_tags = True
    def __unicode__(self):
        return self.type.__unicode__() + ' : ' + strip_tags(self.valeur)
    @staticmethod
    def autocomplete_search_fields():
        return ('type__nom__icontains', 'valeur__icontains',)

class Partie(Model):
    nom = CharField(max_length=200,
        help_text=_(u'Le nom d’une partie de la partition, instrumentale ou vocale.'))
    nom_pluriel = CharField(max_length=230, blank=True,
        verbose_name=_('nom (au pluriel)'), help_text=PLURAL_MSG)
    professions = ManyToManyField(Profession, related_name='parties',
        help_text=_(u'La ou les profession(s) permettant d’assurer cette partie.'))
    parente = ForeignKey('Partie', related_name='enfant', blank=True, null=True)
    classement = FloatField(default=1.0)
    class Meta:
        verbose_name = _('partie')
        verbose_name_plural = _('parties')
        ordering = ['classement', 'nom']
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom
    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'nom_pluriel__icontains',
                'professions__nom__icontains',
                'professions__nom_pluriel__icontains',)

class Pupitre(Model):
    partie = ForeignKey(Partie, related_name='pupitres')
    quantite_min = IntegerField(default=1, verbose_name=_(u'quantité minimale'))
    quantite_max = IntegerField(default=1, verbose_name=_(u'quantité maximale'))
    class Meta:
        verbose_name = _('pupitre')
        verbose_name_plural = _('pupitres')
        ordering = ['partie']
    def __unicode__(self):
        out = ''
        partie = self.partie
        mi = self.quantite_min
        ma = self.quantite_max
        if ma > 1:
            partie = partie.pluriel()
        else:
            partie = partie.__unicode__()
        mi_str = apnumber(mi)
        ma_str = apnumber(ma)
        if mi != ma:
            out += ugettext(u'%(min)s à %(max)s ') % {'min': mi_str, 'max': ma_str}
        elif mi > 1:
            out += mi_str + ' '
        out += partie
        return out
    @staticmethod
    def autocomplete_search_fields():
        return ('partie__nom__icontains', 'partie__nom_pluriel__icontains',
                'partie__professions__nom__icontains',
                'partie__professions__nom_pluriel__icontains',)

class TypeDeParenteDOeuvres(Model):
    nom = CharField(max_length=100, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=130, blank=True,
        verbose_name=_('nom (au pluriel)'),
        help_text=PLURAL_MSG)
    classement = FloatField(default=1.0)
    class Meta:
        verbose_name = _(u'type de parenté d’œuvres')
        verbose_name_plural = _(u'types de parentés d’œuvres')
        ordering = ['classement']
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class ParenteDOeuvres(Model):
    type = ForeignKey(TypeDeParenteDOeuvres, related_name='parentes')
    oeuvres_cibles = ManyToManyField('Oeuvre',
        related_name='enfances_cibles', verbose_name=_(u'œuvres cibles'))
    class Meta:
        verbose_name = _(u'parenté d’œuvres')
        verbose_name_plural = _(u'parentés d’œuvres')
        ordering = ['type']
    def __unicode__(self):
        out = self.type.nom
        cs = self.oeuvres_cibles.all()
        if len(cs) > 1:
            out = self.type.pluriel()
        out += ' : '
        out += str_list([c.__unicode__() for c in cs], ' ; ')
        return out

class Auteur(Model):
    profession = ForeignKey(Profession, related_name='auteurs')
    individus = ManyToManyField(Individu, related_name='auteurs')
    def individus_html(self, tags=True):
        ins = self.individus.all()
        return str_list_w_last([i.html(tags) for i in ins])
    def html(self, tags=True):
        individus = self.individus_html(tags)
        prof = abbreviate(self.profession.__unicode__(), 1)
        out = '%s [%s]' % (individus, prof)
        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True
    class Meta:
        verbose_name = _('auteur')
        verbose_name_plural = _('auteurs')
        ordering = ['profession']
    def __unicode__(self):
        return strip_tags(self.html(False))

class Oeuvre(Model):
    prefixe_titre = CharField(max_length=20, blank=True,
        verbose_name=_(u'préfixe du titre'))
    titre = CharField(max_length=200, blank=True)
    coordination = CharField(max_length=20, blank=True,
        verbose_name=_('coordination'))
    prefixe_titre_secondaire = CharField(max_length=20, blank=True,
        verbose_name=_(u'préfixe du titre secondaire'))
    titre_secondaire = CharField(max_length=200, blank=True,
        verbose_name=_('titre secondaire'))
    genre = ForeignKey(GenreDOeuvre, related_name='oeuvres', blank=True,
        null=True)
    caracteristiques = ManyToManyField(CaracteristiqueDOeuvre, blank=True,
        null=True, verbose_name=_(u'caractéristiques'))
    auteurs = ManyToManyField(Auteur, related_name='oeuvres', blank=True,
        null=True)
    ancrage_composition = OneToOneField(AncrageSpatioTemporel,
        related_name='oeuvres', blank=True, null=True,
        verbose_name=_(u'ancrage spatio-temporel de composition'))
    pupitres = ManyToManyField(Pupitre, related_name='oeuvres', blank=True,
        null=True)
    parentes = ManyToManyField(ParenteDOeuvres, related_name='oeuvres',
        blank=True, null=True, verbose_name=_(u'parentés'))
    lilypond = TextField(blank=True, verbose_name='LilyPond')
    description = HTMLField(blank=True)
    documents = ManyToManyField(Document, related_name='oeuvres', blank=True,
        null=True)
    illustrations = ManyToManyField(Illustration, related_name='oeuvres',
        blank=True, null=True)
    etat = ForeignKey(Etat, related_name='oeuvres', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    @permalink
    def get_absolute_url(self):
        return ('musicologie.catalogue.views.detail_oeuvre', [self.slug])
    def link(self):
        return self.html(True, False, True, True)
    link.short_description = _('permalien')
    link.allow_tags = True
    def individus_auteurs(self):
        q = Individu.objects.none()
        for auteur in self.auteurs.all():
            q |= auteur.individus.all()
        return q.distinct()
    def enfants(self):
        q = Oeuvre.objects.none()
        for enfance in self.enfances_cibles.all():
            q |= enfance.oeuvres.all()
        return q.distinct()
    def evenements(self):
        q = Evenement.objects.none()
        for element in self.elements_de_programme.all():
            q |= element.evenements.all()
        return q.distinct()
    def calc_caracteristiques(self, limite=0, tags=True):
        cs = self.caracteristiques.all()
        def clist(cs):
            return str_list([c.html(tags) for c in cs])
        out2 = clist(cs[limite:])
        if limite:
            out1 = clist(cs[:limite])
            return out1, out2
        return out2
    calc_caracteristiques.allow_tags = True
    calc_caracteristiques.short_description = _(u'caractéristiques')
    def calc_pupitres(self):
        out = ''
        ps = self.pupitres.all()
        if ps:
            out += ugettext('pour ')
            out += str_list_w_last([p.__unicode__() for p in ps])
        return out
    def calc_auteurs(self, tags=True):
        auteurs = self.auteurs.all()
        return str_list([a.html(tags) for a in auteurs])
    calc_auteurs.short_description = _('auteurs')
    calc_auteurs.allow_tags = True
    def calc_parentes(self, tags=True):
        out = ''
        ps = self.parentes.all()
        for p in ps:
            l = [oe.html(tags, False, True, False) for oe in p.oeuvres_cibles.all()]
            out += str_list_w_last(l)
            out += ', '
        return out
    def titre_complet(self):
        out = u''
        if self.titre:
            if self.prefixe_titre:
                out = self.prefixe_titre
            out += self.titre
            if self.titre_secondaire:
                if self.coordination:
                    out += self.coordination
                if self.prefixe_titre_secondaire:
                    out += self.prefixe_titre_secondaire
                out += self.titre_secondaire
        return out
    def html(self, tags=True, auteurs=True, titre=True, descr=True, caps_genre=False):
        # TODO: Nettoyer cette horreur
        out = u''
        auts = self.calc_auteurs(tags)
        parentes = self.calc_parentes(tags)
        titre_complet = self.titre_complet()
        genre = self.genre
        caracteristiques = self.calc_caracteristiques(tags=tags)
        url = '' if not self.slug else self.get_absolute_url()
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
        verbose_name = _(u'œuvre')
        verbose_name_plural = _(u'œuvres')
        ordering = ['genre', 'slug']
    def save(self, *args, **kwargs):
        super(Oeuvre, self).save(*args, **kwargs)
        self.slug = autoslugify(self, self.__unicode__())
        self._old_save(*args, **kwargs)
    def __unicode__(self):
        return strip_tags(self.titre_html(False))
    @staticmethod
    def autocomplete_search_fields():
        return ('prefixe_titre__icontains', 'titre__icontains',
                'prefixe_titre_secondaire__icontains',
                'titre_secondaire__icontains', 'genre__nom__icontains',)

class AttributionDePupitre(Model):
    pupitre = ForeignKey(Pupitre, related_name='attributions_de_pupitre')
    individus = ManyToManyField(Individu, related_name='attributions_de_pupitre')
    class Meta:
        verbose_name = _('attribution de pupitre')
        verbose_name_plural = _('attributions de pupitre')
        ordering = ['pupitre']
    def __unicode__(self):
        out = self.pupitre.partie.__unicode__() + ' : '
        ins = self.individus.all()
        out += str_list_w_last([i.__unicode__() for i in ins])
        return out

class CaracteristiqueDElementDeProgramme(Model):
    nom = CharField(max_length=100, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=110, blank=True,
        verbose_name=_('nom (au pluriel)'), help_text=PLURAL_MSG)
    classement = FloatField(default=1.0)
    def pluriel(self):
        return calc_pluriel(self)
    class Meta:
        verbose_name = _(u'caractéristique d’élément de programme')
        verbose_name_plural = _(u'caractéristiques d’élément de programme')
        ordering = ['nom']
    def __unicode__(self):
        return self.nom

class ElementDeProgramme(Model):
    oeuvre = ForeignKey(Oeuvre, related_name='elements_de_programme',
        verbose_name=_(u'œuvre'), blank=True, null=True)
    autre = CharField(max_length=500, blank=True)
    caracteristiques = ManyToManyField(CaracteristiqueDElementDeProgramme,
        related_name='elements_de_programme', blank=True, null=True,
        verbose_name=_(u'caractéristiques'))
    classement = FloatField(default=1.0)
    distribution = ManyToManyField(AttributionDePupitre,
        related_name='elements_de_programme', blank=True, null=True)
    personnels = ManyToManyField(Personnel,
        related_name='elements_de_programme', blank=True, null=True)
    illustrations = ManyToManyField(Illustration,
        related_name='representations', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='representations',
        blank=True, null=True)
    etat = ForeignKey(Etat, related_name='elements_de_programme', null=True,
        blank=True)
    def calc_caracteristiques(self):
        cs = self.caracteristiques.all()
        return str_list([c.__unicode__() for c in cs])
    calc_caracteristiques.allow_tags = True
    calc_caracteristiques.short_description = _(u'caractéristiques')
    def html(self, tags=True):
        out = ''
        oeuvre = self.oeuvre
        if oeuvre:
            out += oeuvre.html(tags)
        else:
            out += self.autre
        cs = self.calc_caracteristiques()
        if cs:
            out += ' [%s]' % cs
        distribution = self.distribution.all()
        maxi = len(distribution) - 1
        if distribution:
            out += u'. — '
        for i, attribution in enumerate(distribution):
            individus = attribution.individus.all()
            maxj = len(individus) - 1
            for j, individu in enumerate(individus):
                out += individu.html(tags)
                if j < maxj:
                    out += ', '
            out += ' [%s]' % attribution.pupitre.partie.__unicode__()
            if i < maxi:
                out += ', '
        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True
    class Meta:
        verbose_name = _(u'élément de programme')
        verbose_name_plural = _(u'éléments de programme')
        ordering = ['classement', 'oeuvre']
    def __unicode__(self):
        return strip_tags(self.html(False))
    @staticmethod
    def autocomplete_search_fields():
        return ('oeuvre__prefixe_titre__icontains', 'oeuvre__titre__icontains',
                'oeuvre__prefixe_titre_secondaire__icontains',
                'oeuvre__titre_secondaire__icontains',
                'oeuvre__genre__nom__icontains',)

class Evenement(Model):
    ancrage_debut = OneToOneField(AncrageSpatioTemporel,
        related_name='evenements_debuts')
    ancrage_fin = OneToOneField(AncrageSpatioTemporel,
        related_name='evenements_fins', blank=True, null=True)
    relache = BooleanField(verbose_name=u'relâche')
    circonstance = CharField(max_length=500, blank=True)
    programme = ManyToManyField(ElementDeProgramme, related_name='evenements',
        blank=True, null=True)
    documents = ManyToManyField(Document, related_name='evenements', blank=True,
        null=True)
    illustrations = ManyToManyField(Illustration, related_name='evenements',
        blank=True, null=True)
    etat = ForeignKey(Etat, related_name='evenements', null=True, blank=True)
    notes = HTMLField(blank=True)
    @permalink
    def get_absolute_url(self):
        return ('evenement_jour',
                [self.ancrage_debut.lieu.slug, self.ancrage_debut.date.year,
                 self.ancrage_debut.date.month, self.ancrage_debut.date.day])
    def link(self):
        return href(self.get_absolute_url(), self.__unicode__())
    link.short_description = _('permalien')
    link.allow_tags = True
    def sources_dict(self):
        types = TypeDeSource.objects.filter(sources__evenements=self).distinct()
        d = {}
        for type in types:
            sources = self.sources.filter(type=type)
            if sources:
                d[type] = sources
        return d
    def html(self, tags=True):
        relache, circonstance = '', ''
        if self.circonstance:
            circonstance = hlp(self.circonstance, ugettext(u'circonstance'), tags)
        if self.relache:
            relache = ugettext(u'Relâche')
        l = [self.ancrage_debut.calc_lieu(tags), circonstance,
             self.ancrage_debut.calc_heure(), relache]
        out = str_list(l)
        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True
    class Meta:
        verbose_name = _(u'événement')
        verbose_name_plural = _(u'événements')
        ordering = ['ancrage_debut']
    def __unicode__(self):
        out = self.ancrage_debut.calc_date(False)
        out = capfirst(out)
        out += u'\u00A0; ' + self.html(False)
        return strip_tags(out)
    @staticmethod
    def autocomplete_search_fields():
        return ('circonstace__icontains', 'ancrage_debut__lieu__nom__icontains',
                'ancrage_debut__lieu__parent__nom__icontains',
                'ancrage_debut__date__icontains',
                'ancrage_debut__heure__icontains',
                'ancrage_debut__lieu_approx__icontains',
                'ancrage_debut__date_approx__icontains',
                'ancrage_debut__heure_approx__icontains',)

class TypeDeSource(Model):
    nom = CharField(max_length=200, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=230, blank=True,
        verbose_name=_('nom (au pluriel)'),
        help_text=PLURAL_MSG)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = _('type de source')
        verbose_name_plural = _('types de source')
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(self, self.__unicode__())
        super(TypeDeSource, self).save(*args, **kwargs)
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class Source(Model):
    nom = CharField(max_length=200, help_text=ex(_('Journal de Rouen')))
    numero = CharField(max_length=50, blank=True)
    date = DateField(help_text=DATE_MSG)
    page = CharField(max_length=50, blank=True)
    type = ForeignKey(TypeDeSource, related_name='sources',
        help_text=ex(_('compte rendu')))
    contenu = HTMLField(blank=True)
    auteurs = ManyToManyField(Auteur, related_name='sources', blank=True,
        null=True)
    evenements = ManyToManyField(Evenement, related_name='sources', blank=True,
        null=True)
    documents = ManyToManyField(Document, related_name='sources', blank=True,
        null=True)
    illustrations = ManyToManyField(Illustration, related_name='sources',
        blank=True, null=True)
    etat = ForeignKey(Etat, related_name='sources', null=True, blank=True)
    notes = HTMLField(blank=True)
    def calc_auteurs(self, tags=True):
        auteurs = self.auteurs.all()
        return str_list([a.html(tags) for a in auteurs])
    def html(self, tags=True):
        l = []
        l.append('%s' % cite(self.nom, tags))
        if self.numero:
            l.append(no(self.numero))
        l.append('du %s' % date_html(self.date, tags))
        if self.page:
            l.append('p. %s' % self.page)
        out = ' '.join(l)
        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True
    def disp_contenu(self):
        return self.contenu[:200] + u'[...]' + self.contenu[-50:]
    disp_contenu.short_description = _('contenu')
    disp_contenu.allow_tags = True
    class Meta:
        verbose_name = _('source')
        verbose_name_plural = _('sources')
        ordering = ['date', 'nom', 'numero', 'page', 'type']
    def __unicode__(self):
        return strip_tags(self.html(False))

