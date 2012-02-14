# coding: utf-8
from django.db.models import *
from tinymce.models import HTMLField
from django.template.defaultfilters import slugify
from filebrowser.fields import FileBrowseField
from django.template.defaultfilters import date, time, capfirst
from musicologie.catalogue.templatetags.extras import replace, abbreviate
from django.core.urlresolvers import reverse
from musicologie.settings import DATE_FORMAT

#
# Définitions globales du fichier
#

LOWER_MSG = u'En minuscules.'
PLURAL_MSG = u'À remplir si le pluriel n\'est pas un simple ajout de « s ».  Exemple : « animal » devient « animaux » et non « animals ».'
DATE_MSG = u'Ex. : « 6/6/1944 » pour le 6 juin 1944.'

def autoslugify(Mod, nom, slug):
    if slug != '':
        return slug
    nom_slug = slug_orig = slugify(nom)
    n = 0
    while Mod.objects.filter(slug=nom_slug).count():
        n += 1;
        nom_slug = slug_orig + str(n)
    return nom_slug

def calc_pluriel(object):
        if object.nom_pluriel:
            return object.nom_pluriel
        return object.nom + 's'

def ex(str):
    return u'Exemple : « '+ str + u' »'

# 
# Modélisation
#

def save(self, *args, **kwargs):
    try:
        for field in self._meta.fields:
            if field.__class__.__name__ == 'HTMLField':
                value = replace(getattr(self, field.attname))
                setattr(self, field.attname, value)
    except:
        pass
    self._old_save(*args, **kwargs)

Model._old_save = Model.save
Model.save = save

class Document(Model):
    nom = CharField(max_length=300, blank=True)
    document = FileBrowseField('Document', max_length=400, directory='documents/')
    description = HTMLField(blank=True)
    auteurs = ManyToManyField('Auteur', related_name='documents', blank=True,
        null=True)
    class Meta:
        ordering = ['document']
    def __unicode__(self):
        if self.nom:
            return self.nom
        return self.document.__unicode__()

class Illustration(Model):
    legende = CharField(max_length=300, blank=True, verbose_name=u'légende')
    image = FileBrowseField('Image', max_length=400, directory='images/')
    commentaire = HTMLField(blank=True)
    auteurs = ManyToManyField('Auteur', related_name='illustrations', blank=True,
        null=True)
    class Meta:
        ordering = ['image']
    def __unicode__(self):
        if self.legende:
            return self.legende
        return self.image.__unicode__()

class Etat(Model):
    nom = CharField(max_length=200, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=230, blank=True,
        verbose_name='nom (au pluriel)', help_text=PLURAL_MSG)
    message = HTMLField(blank=True,
        help_text=u'Message à afficher dans la partie consultation.')
    publie = BooleanField(default=True, verbose_name=u'publié')
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = u'état'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Etat, self.__unicode__(), self.slug)
        super(Etat, self).save(*args, **kwargs)
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class NatureDeLieu(Model):
    nom = CharField(max_length=255, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=430, blank=True,
                            verbose_name='nom (au pluriel)',
                            help_text=PLURAL_MSG)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = 'nature de lieu'
        verbose_name_plural = 'natures de lieu'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(NatureDeLieu, self.__unicode__(), self.slug)
        super(NatureDeLieu, self).save(*args, **kwargs)
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class Lieu(Model):
    nom = CharField(max_length=200)
    parent = ForeignKey('Lieu', related_name='enfants', null=True, blank=True)
    nature = ForeignKey(NatureDeLieu, related_name='lieux')
    historique = HTMLField(blank=True)
    illustrations = ManyToManyField(Illustration, related_name='lieux', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='lieux', blank=True, null=True)
    etat = ForeignKey(Etat, related_name='lieux', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    def evenements(self):
        return Evenement.objects.filter(ancrage_debut__lieu=self)
    def html(self):
        url = reverse('musicologie.catalogue.views.detail_lieu',
            args=[self.slug])
        out = '<a href="' + url + '">'
        parent = self.parent
        if parent:
            out += parent.nom + ', '
        out += self.nom + '</a>'
        return replace(out)
    class Meta:
        verbose_name_plural = 'lieux'
        ordering = ['nom']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Lieu, self.__unicode__(), self.slug)
        super(Lieu, self).save(*args, **kwargs)
    def __unicode__(self):
        if self.parent:
            return self.nom + ', ' + self.parent.nom
        return self.nom

class Saison(Model):
    lieu = ForeignKey(Lieu, related_name='saisons')
    debut = DateField(verbose_name=u'début', help_text=DATE_MSG)
    fin = DateField()
    class Meta:
        ordering = ['lieu', 'debut']
    def __unicode__(self):
        return self.lieu.__unicode__() + ', ' + str(self.debut.year) + '-' + str(self.fin.year)

class Profession(Model):
    nom = CharField(max_length=200, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=230, blank=True,
        verbose_name='nom (au pluriel)', help_text=PLURAL_MSG)
    parente = ForeignKey('Profession', blank=True, null=True,
        related_name='enfant')
    slug = SlugField(blank=True)
    class Meta:
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Profession, self.__unicode__(), self.slug)
        super(Profession, self).save(*args, **kwargs)
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class AncrageSpatioTemporel(Model):
    date = DateField(blank=True, null=True, help_text=DATE_MSG)
    heure = TimeField(blank=True, null=True)
    lieu = ForeignKey(Lieu, related_name='ancrages', blank=True, null=True)
    date_approx = CharField(max_length=200, blank=True,
        verbose_name=u'date approximative',
        help_text=u'Ne remplir que si la date est imprécise.')
    heure_approx = CharField(max_length=200, blank=True,
        verbose_name=u'heure approximative',
        help_text=u"Ne remplir que si l'heure est imprécise.")
    lieu_approx = CharField(max_length=200, blank=True,
        verbose_name=u'lieu approximatif',
        help_text=u'Ne remplir que si le lieu est imprécis.')
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
    def calc_date(self):
        if self.date:
            return date(self.date, DATE_FORMAT)
        elif self.date_approx:
            return self.date_approx
        return ''
    calc_date.short_description = 'Date'
    calc_date.admin_order_field = 'date'
    def calc_heure(self):
        if self.heure:
            return time(self.heure, 'H\hi')
        elif self.heure_approx:
            return self.heure_approx
        return ''
    calc_heure.short_description = 'Heure'
    calc_heure.admin_order_field = 'heure'
    def calc_moment(self):
        out = ''
        date = self.calc_date()
        heure = self.calc_heure()
        if date != '':
            if self.date:
                out += u'le '
            out += date
            if heure != '':
                out += ' '
        if heure != '':
            if self.heure:
                out += u'à '
            out += heure
        return out
    def calc_lieu(self):
        if self.lieu:
            return self.lieu.html()
        elif self.lieu_approx:
            return self.lieu_approx
        return ''
    calc_lieu.short_description = 'Lieu'
    calc_lieu.admin_order_field = 'lieu'
    class Meta:
        verbose_name = u'ancrage spatio-temporel'
        verbose_name_plural = u'ancrages spatio-temporels'
        ordering = ['date', 'heure', 'lieu', 'date_approx', 'heure_approx', 'lieu_approx']
    def __unicode__(self):
        out = ''
        lieu = self.calc_lieu()
        if lieu != '':
            out = lieu
            if date != '' or heure != '':
                out += ', '
        out += self.calc_moment()
        out = capfirst(out)
        return out

class Prenom(Model):
    prenom = CharField(max_length=100, verbose_name=u'prénom')
    classement = FloatField(default=1.0)
    favori = BooleanField(default=True)
    class Meta:
        verbose_name = u'prénom'
        ordering = ['prenom', 'classement']
    def __unicode__(self):
        return self.prenom

class TypeDeParenteDIndividus(Model):
    nom = CharField(max_length=50, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=55, blank=True, help_text=PLURAL_MSG)
    classement = FloatField(default=1.0)
    class Meta:
        verbose_name = u"type de parenté d'individus"
        verbose_name_plural = u"types de parenté d'individus"
        ordering = ['classement']
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class ParenteDIndividus(Model):
    type = ForeignKey(TypeDeParenteDIndividus, related_name='parentes')
    individus_cibles = ManyToManyField('Individu',
        related_name='parentes_cibles', verbose_name='individus cibles')
    class Meta:
        verbose_name = u"parenté d'individus"
        verbose_name_plural = u"parentés d'individus"
        ordering = ['type']
    def __unicode__(self):
        out = self.type.nom
        if len(self.individus_cibles.all()) > 1:
            out = self.type.pluriel()
        out += ' :'
        cibles = self.individus_cibles.all()
        maxi = len(cibles) - 1
        for i, individu in enumerate(cibles):
            out += ' ' + individu.__unicode__()
            if i < maxi:
                out += ' ;'
        return out

class Individu(Model):
    nom = CharField(max_length=200)
    nom_naissance = CharField(max_length=200, blank=True,
        verbose_name=u'nom de naissance', help_text='''
        Ne remplir que s'il est différent du nom d'usage.''')
    prenoms = ManyToManyField(Prenom, related_name='individus', blank=True,
        null=True, verbose_name=u'prénoms')
    pseudonyme = CharField(max_length=200, blank=True)
    DESIGNATIONS = (
        ('S', 'Standard (nom, prénoms et pseudonyme)'),
        ('P', 'Pseudonyme'),
        ('L', 'Nom de famille'),
        ('F', 'Prénom(s) favori(s)'),
    )
    designation = CharField(max_length=1, choices=DESIGNATIONS, default='S')
    SEXES = (
        ('M', 'Masculin'),
        ('J', 'Féminin (Mlle)'), # J pour Jouvencelle
        ('F', 'Féminin (Mme)'),
    )
    sexe = CharField(max_length=1, choices=SEXES, blank=True)
    ancrage_naissance = OneToOneField(AncrageSpatioTemporel, blank=True, null=True,
        related_name='individus_nes', verbose_name=u'ancrage de naissance')
    ancrage_deces = OneToOneField(AncrageSpatioTemporel, blank=True, null=True,
        related_name='individus_decedes', verbose_name=u'ancrage du décès')
    ancrage_approx = OneToOneField(AncrageSpatioTemporel, blank=True, null=True,
        related_name='individus', verbose_name=u'ancrage approximatif',
        help_text=u'Ne remplir que si on ne connaît aucune date précise.')
    professions = ManyToManyField(Profession, related_name='individus',
        blank=True, null=True)
    parentes = ManyToManyField(ParenteDIndividus, related_name='individus_orig',
        blank=True, null=True, verbose_name='parentes')
    biographie = HTMLField(blank=True)
    illustrations = ManyToManyField(Illustration, related_name='individus',
        blank=True, null=True)
    documents = ManyToManyField(Document, related_name='individus',blank=True,
        null=True)
    etat = ForeignKey(Etat, related_name='individus', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    def calc_prenoms_methode(self, fav):
        prenoms = self.prenoms.all().order_by('classement', 'prenom')
        maxi = len(prenoms) - 1
        if prenoms:
            out = ''
            for i, prenom in enumerate(prenoms):
                if prenom.favori or not fav:
                    out += prenom.__unicode__()
                    if i < maxi:
                        out += ' '
            return out
        return ''
    def calc_prenoms(self):
        return self.calc_prenoms_methode(False)
    calc_prenoms.short_description = u'prénoms'
    def calc_fav_prenoms(self):
        return self.calc_prenoms_methode(True)
    def calc_pseudonyme(self):
        if self.pseudonyme:
            return self.pseudonyme
        return 'Aucun'
    def calc_titre(self):
        titres = {'M': 'M.', 'J': 'M<sup>lle</sup>', 'F': 'M<sup>me</sup>',}
        if self.sexe:
            return titres[self.sexe]
        return ''
    def calc_designation(self):
        out = ''
        designation = self.designation
        prenoms = self.calc_fav_prenoms()
        nom = self.nom
        pseudonyme = self.pseudonyme
        sexe = self.sexe
        if prenoms and (designation == 'F' or designation == 'S'):
            out += prenoms
            if nom and designation == 'S':
                out += ' '
        elif sexe and not prenoms and designation == 'S':
            out += self.calc_titre()
            if nom:
                out += ' '
        if nom and (designation == 'L' or designation == 'S'):
            out += nom
            if designation == 'S':
                out += ' '
        if pseudonyme and (designation == 'P' or designation == 'S'):
            if designation == 'S':
                out += ', dit '
            out += pseudonyme
        return out
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
        professions = self.professions.all()
        if professions:
            out = ''
            maxi = len(professions) - 1
            for i, profession in enumerate(professions):
                out += profession.__unicode__()
                if i < maxi:
                    out += ', '
            return out
        return ''
    calc_professions.short_description = 'professions'
    def html(self):
        designation = self.designation
        prenoms = self.calc_fav_prenoms()
        nom = self.nom
        url = reverse('musicologie.catalogue.views.detail_individu',
            args=[self.slug])
        out = '<a href="' + url + '">'
        if designation == 'S' and nom and not prenoms and self.sexe:
                titre = self.calc_titre()
                out += titre + ' '
        out += '<span style="font-variant: small-caps;">'
        if designation == 'F':
            out += prenoms
        elif designation == 'P':
            out += self.pseudonyme
        else:
            out += nom
        out += '</span>'
        if designation == 'S' and prenoms:
            out += ' (' + abbreviate(prenoms) + ')'
        out += '</a>'
        return replace(out)
    class Meta:
        ordering = ['nom']
    def save(self, *args, **kwargs):
        super(Individu, self).save(*args, **kwargs)
        self.slug = autoslugify(Individu, self.__unicode__(), self.slug)
        super(Individu, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.calc_designation()
    __unicode__.allow_tags = True

class Devise(Model):
    '''
    Modélisation naïve d'une unité monétaire.
    '''
    nom = CharField(max_length=200, blank=True, help_text=ex('euro'), unique=True)
    symbole = CharField(max_length=10, help_text=ex(u'€'), unique=True)
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
    def __unicode__(self):
        return self.profession.nom

class TypeDePersonnel(Model):
    nom = CharField(max_length=100, unique=True)
    class Meta:
        verbose_name = 'type de personnel'
        verbose_name_plural = 'types de personnel'
        ordering = ['nom']
    def __unicode__(self):
        return self.nom

class Personnel(Model):
    type = ForeignKey(TypeDePersonnel, related_name='personnels')
    saison = ForeignKey(Saison, related_name='personnels')
    engagements = ManyToManyField(Engagement, related_name='personnels')
    def __unicode__(self):
        return self.type.__unicode__() + self.saison.__unicode__()

class GenreDOeuvre(Model):
    nom = CharField(max_length=255, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=430, blank=True,
        verbose_name='nom (au pluriel)',
        help_text=PLURAL_MSG)
    parents = ManyToManyField('GenreDOeuvre', related_name='enfants',
        blank=True, null=True)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name=u"genre d'œuvre"
        verbose_name_plural=u"genres d'œuvre"
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(GenreDOeuvre, self.__unicode__(), self.slug)
        super(GenreDOeuvre, self).save(*args, **kwargs)
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class TypeDeCaracteristiqueDOeuvre(Model):
    nom = CharField(max_length=200, help_text=ex(u'tonalité'), unique=True)
    nom_pluriel = CharField(max_length=430, blank=True,
        verbose_name='nom (au pluriel)', help_text=PLURAL_MSG)
    classement = FloatField(default=1.0)
    class Meta:
        verbose_name = u"type de caractéristique d'œuvre"
        verbose_name_plural = u"types de caracteristique d'œuvre"
        ordering = ['classement']
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class CaracteristiqueDOeuvre(Model):
    type = ForeignKey(TypeDeCaracteristiqueDOeuvre, related_name='caracteristiques_d_oeuvre')
    valeur = CharField(max_length=400, help_text=ex(u'en trois actes'))
    classement = FloatField(default=1.0,
        help_text=u"Par exemple, on peut choisir de classer les découpages par nombre d'actes.")
    class Meta:
        verbose_name = u"caractéristique d'œuvre"
        verbose_name_plural = u"caractéristiques d'œuvre"
        ordering = ['type', 'classement']
    def __unicode__(self):
        return self.type.__unicode__() + ' : ' + self.valeur
    __unicode__.allow_tags = True

class Partie(Model):
    nom = CharField(max_length=200,
        help_text="Le nom d'une partie de la partition, instrumentale ou vocale.")
    professions = ManyToManyField(Profession, related_name='parties',
        help_text=u"La ou les profession(s) permettant d'assurer cette partie.")
    parente = ForeignKey('Partie', related_name='enfant', blank=True, null=True)
    classement = FloatField(default=1.0)
    class Meta:
        ordering = ['classement']
    def __unicode__(self):
        return self.nom

class Pupitre(Model):
    partie = ForeignKey(Partie, related_name='pupitres')
    quantite_min = IntegerField(default=1, verbose_name=u'quantité minimale')
    quantite_max = IntegerField(default=1, verbose_name=u'quantité maximale')
    def __unicode__(self):
        out = ''
        mi = self.quantite_min
        ma = self.quantite_max
        if mi > 1:
            out += str(mi) + ' '
        if mi != ma:
            out = u'%d à %d ' % (mi, ma)
        out += self.partie.__unicode__()
        return out

class TypeDeParenteDOeuvres(Model):
    nom = CharField(max_length=100, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=130, blank=True,
        verbose_name='nom (au pluriel)',
        help_text=PLURAL_MSG)
    classement = FloatField(default=1.0)
    class Meta:
        verbose_name = u"type de parenté d'œuvres"
        verbose_name_plural = u"types de parentés d'œuvres"
        ordering = ['classement']
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class ParenteDOeuvres(Model):
    type = ForeignKey(TypeDeParenteDOeuvres, related_name='parentes')
    oeuvres_cibles = ManyToManyField('Oeuvre',
        related_name='parentes_cibles', verbose_name='œuvres cibles')
    class Meta:
        verbose_name = u"parenté d'œuvres"
        verbose_name_plural = u"parentés d'œuvres"
        ordering = ['type']
    def __unicode__(self):
        out = self.type.nom
        if len(self.oeuvres_cibles.all()) > 1:
            out = self.type.pluriel()
        out += ' :'
        cibles = self.oeuvres_cibles.all()
        maxi = len(cibles) - 1
        for i, oeuvre in enumerate(cibles):
            out += ' ' + oeuvre.__unicode__()
            if i < maxi:
                out += ' ;'
        return out

class Auteur(Model):
    profession = ForeignKey(Profession, related_name='auteur')
    individus = ManyToManyField(Individu, related_name='auteurs')
    def individus_html(self):
        out = ''
        individus = self.individus.all()
        maxi = len(individus) - 1
        for i, individu in enumerate(individus):
            out += individu.html()
            if i < maxi:
                out += ', '
        return out
    def html(self):
        out = self.individus_html()
        out += ' [' + abbreviate(self.profession.__unicode__(), 1) + ']'
        return replace(out)
    class Meta:
        ordering = ['profession']
    def save(self, *args, **kwargs):
        super(Auteur, self).save(*args, **kwargs)
        for individu in self.individus.all():
            individu.professions.add(self.profession)
    def __unicode__(self):
        out = self.profession.__unicode__() + ' : '
        for individu in self.individus.all():
            out += individu.__unicode__()
        return out

class Oeuvre(Model):
    prefixe_titre = CharField(max_length=20, blank=True,
        verbose_name=u'préfixe du titre')
    titre = CharField(max_length=200, blank=True)
    liaison = CharField(max_length=20, blank=True, verbose_name='coordination')
    prefixe_soustitre = CharField(max_length=20, blank=True,
        verbose_name=u'préfixe du titre secondaire')
    soustitre = CharField(max_length=200, blank=True, verbose_name='titre secondaire')
    genre = ForeignKey(GenreDOeuvre, related_name='oeuvres', blank=True,
        null=True)
    caracteristiques = ManyToManyField(CaracteristiqueDOeuvre, blank=True,
        null=True, verbose_name=u'caractéristiques')
    auteurs = ManyToManyField(Auteur, related_name='oeuvres', blank=True,
        null=True)
    ancrage_composition = OneToOneField(AncrageSpatioTemporel,
        related_name='oeuvres', blank=True, null=True,
        verbose_name=u'ancrage spatio-temporel de composition')
    pupitres = ManyToManyField(Pupitre, related_name='oeuvres', blank=True,
        null=True)
    parentes = ManyToManyField(ParenteDOeuvres, related_name='oeuvres',
        blank=True, null=True, verbose_name=u'parentes')
    lilypond = TextField(blank=True, verbose_name='LilyPond')
    description = HTMLField(blank=True)
    documents = ManyToManyField(Document, related_name='oeuvres', blank=True,
        null=True)
    illustrations = ManyToManyField(Illustration, related_name='oeuvres',
        blank=True, null=True)
    etat = ForeignKey(Etat, related_name='oeuvres', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    def calc_caracteristiques(self):
        out = ''
        caracteristiques = self.caracteristiques.all()
        if caracteristiques:
            maxi = len(caracteristiques) - 1
            for i, caracteristique in enumerate(caracteristiques):
                out += caracteristique.valeur
                if i < maxi:
                    out += ', '
        return out
    calc_caracteristiques.allow_tags = True
    calc_caracteristiques.short_description = u'caractéristiques'
    def calc_pupitres(self):
        out = ''
        pupitres = self.pupitres.all()
        if pupitres:
            maxi = len(pupitres) - 1
            out += 'pour '
            for i, pupitre in enumerate(pupitres):
                out += pupitre.__unicode__()
                if i < maxi-1:
                    out += ', '
                elif i < maxi:
                    out += ' et '
        return out
    def calc_auteurs(self, html=False):
        out = ''
        auteurs = self.auteurs.all()
        maxi = len(auteurs) - 1
        for i, auteur in enumerate(auteurs):
            if html:
                out += auteur.html() + ', '
            else:
                out += auteur.__unicode__()
                if i < maxi:
                    out += ', '
        return out
    calc_auteurs.short_description = 'auteurs'
    def html(self):
        out = self.calc_auteurs(True)
        titre_complet = self.__unicode__(True)
        if titre_complet:
            out += '<em>' + titre_complet + '</em>'
        genre = self.genre
        caracteristiques = self.calc_caracteristiques()
        if titre_complet and (genre or caracteristiques):
            out += ', '
        if genre:
            out += genre.__unicode__()
            if not titre_complet:
                out = out.capitalize()
            pupitres = self.calc_pupitres()
            if pupitres and not titre_complet:
                out += ' ' + pupitres
            if caracteristiques:
                out += ' ' + caracteristiques
        return replace(out)
    html.allow_tags = True
    class Meta:
        verbose_name = u'œuvre'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Oeuvre, self.__unicode__(False, False), self.slug)
        super(Oeuvre, self).save(*args, **kwargs)
    def __unicode__(self, titre_seul=False, saved=True):
        out = u''
        if self.titre:
            if self.prefixe_titre:
                out = self.prefixe_titre
            out += self.titre
            if self.soustitre:
                if self.liaison:
                    out += self.liaison
                if self.prefixe_soustitre:
                    out += self.prefixe_soustitre
                out += self.soustitre
        elif self.genre and not titre_seul:
            out = self.genre.nom
            if saved and self.caracteristiques:
                out += ' ' + self.calc_caracteristiques()
        elif titre_seul:
            out += ''
        else:
            out = str(self.id)
        return out
    __unicode__.allow_tags = True

class AttributionDePupitre(Model):
    pupitre = ForeignKey(Pupitre, related_name='attributions_de_pupitre')
    individus = ManyToManyField(Individu, related_name='attributions_de_pupitre')
    class Meta:
        verbose_name = u'attribution de pupitre'
    def __unicode__(self):
        out = self.pupitre.partie.__unicode__() + ' : '
        individus = self.individus.all()
        maxi = len(individus) - 1
        for i, individu in enumerate(individus):
            out += individu.__unicode__()
            if i < maxi:
                out += ', '
        return out

class CaracteristiqueDElementDeProgramme(Model):
    nom = CharField(max_length=100, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=110, blank=True,
        verbose_name='nom (au pluriel)', help_text=PLURAL_MSG)
    classement = FloatField(default=1.0)
    def pluriel(self):
        return calc_pluriel(self)
    class Meta:
        verbose_name = u"caractéristique d'élément de programme"
        verbose_name_plural = u"caractéristiques d'élément de programme"
        ordering = ['nom']
    def __unicode__(self):
        return self.nom

class ElementDeProgramme(Model):
    oeuvre = ForeignKey(Oeuvre, related_name='elements_de_programme',
        verbose_name=u'œuvre', blank=True, null=True)
    autre = CharField(max_length=500, blank=True)
    caracteristiques = ManyToManyField(CaracteristiqueDElementDeProgramme,
        related_name='elements_de_programme', blank=True, null=True,
        verbose_name=u'caractéristiques')
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
    def html(self):
        out = ''
        oeuvre = self.oeuvre
        if oeuvre:
            out += oeuvre.html()
        else:
            out += self.autre
        distribution = self.distribution.all()
        maxi = len(distribution) - 1
        if distribution:
            out += '. &mdash; '
        for i, attribution in enumerate(distribution):
            individus = attribution.individus.all()
            maxj = len(individus) - 1
            for j, individu in enumerate(individus):
                out += individu.html()
                if j < maxj:
                    out += ', '
            out += ' [' + attribution.pupitre.partie.__unicode__() + ']'
            if i < maxi:
                out += ', '
        return replace(out)
    html.allow_tags = True
    class Meta:
        verbose_name = u'élément de programme'
        verbose_name_plural = u'éléments de programme'
        ordering = ['classement']
    def __unicode__(self):
        if self.oeuvre:
            return self.oeuvre.__unicode__()
        elif self.autre:
            return self.autre
        return self.classement.__unicode__()

class Evenement(Model):
    ancrage_debut = OneToOneField(AncrageSpatioTemporel,
        related_name='evenements_debuts')
    ancrage_fin = OneToOneField(AncrageSpatioTemporel,
        related_name='evenements_fins', blank=True, null=True)
    relache = BooleanField(verbose_name=u'relâche')
    circonstance = CharField(max_length=500, blank=True)
    programme = ManyToManyField(ElementDeProgramme, related_name='evenements', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='evenements', blank=True, null=True)
    illustrations = ManyToManyField(Illustration, related_name='evenements', blank=True, null=True)
    etat = ForeignKey(Etat, related_name='evenements', null=True, blank=True)
    notes = HTMLField(blank=True)
    class Meta:
        verbose_name = u'événement'
        ordering = ['ancrage_debut']
    def __unicode__(self):
        return self.ancrage_debut.calc_lieu() + ' le ' + self.ancrage_debut.calc_date()

class TypeDeSource(Model):
    nom = CharField(max_length=200, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=230, blank=True,
        verbose_name='nom (au pluriel)',
        help_text=PLURAL_MSG)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = 'type de source'
        verbose_name_plural = 'types de source'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(TypeDeSource, self.__unicode__(), self.slug)
        super(TypeDeSource, self).save(*args, **kwargs)
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class Source(Model):
    nom = CharField(max_length=200, help_text=ex('Le Journal de Rouen'))
    numero = CharField(max_length=50, blank=True)
    date = DateField(help_text=DATE_MSG)
    page = CharField(max_length=50, blank=True)
    type = ForeignKey(TypeDeSource, related_name='sources',
        help_text=ex('compte rendu'))
    contenu = HTMLField(blank=True)
    evenements = ManyToManyField(Evenement, related_name='sources', blank=True,
        null=True)
    documents = ManyToManyField(Document, related_name='sources', blank=True,
        null=True)
    illustrations = ManyToManyField(Illustration, related_name='sources',
        blank=True, null=True)
    etat = ForeignKey(Etat, related_name='sources', null=True, blank=True)
    notes = HTMLField(blank=True)
    def disp_contenu(self):
        return self.contenu[:200] + u'[...]' + self.contenu[-50:]
    disp_contenu.short_description = 'contenu'
    disp_contenu.allow_tags = True
    class Meta:
        ordering = ['date', 'nom', 'numero', 'page', 'type']
    def save(self, *args, **kwargs):
        contenu = self.contenu
        if contenu[:3] == '<p>' and contenu[-4:] == '</p>' and contenu[3:10] != '&laquo;':
            self.contenu = u'<p>&laquo;&nbsp;' + contenu[3:-4] + u'&nbsp;&raquo;</p>'
        super(Source, self).save(*args, **kwargs)
    def __unicode__(self):
        return str(self.pk)

