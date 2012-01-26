# coding: utf-8
from django.db.models import *
from tinymce.models import HTMLField
from django.template.defaultfilters import slugify
from filebrowser.fields import FileBrowseField

PLURAL_MSG = u'À remplir si le pluriel n\'est pas un simple ajout de « s ».  Exemple : « animal » devient « animaux » et non « animals ».'

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
        else:
            return object.nom + 's'

class Document(Model):
    nom = CharField(max_length=300, blank=True)
    document = FileBrowseField('Document', max_length=400, directory='documents/')
    description = HTMLField(blank=True)
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
    class Meta:
        ordering = ['image']
    def __unicode__(self):
        if self.nom:
            return self.nom
        return self.image.__unicode__()

class Etat(Model):
    nom = CharField(max_length=200)
    nom_pluriel = CharField(max_length=230, blank=True,
        verbose_name='nom (au pluriel)', help_text=PLURAL_MSG)
    message = CharField(max_length=300, blank=True,
        help_text=u'Message à afficher dans la partie consultation.')
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = u'état'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Etat, self.nom, self.slug)
        super(Etat, self).save(*args, **kwargs)
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class NatureDeLieu(Model):
    nom = CharField(max_length=400)
    nom_pluriel = CharField(max_length=430, blank=True,
                            verbose_name='nom (au pluriel)',
                            help_text=PLURAL_MSG)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = 'nature de lieu'
        verbose_name_plural = 'natures de lieu'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(NatureDeLieu, self.nom, self.slug)
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
    class Meta:
        verbose_name_plural = 'lieux'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Lieu, self.nom, self.slug)
        super(Lieu, self).save(*args, **kwargs)
    def __unicode__(self):
        if self.parent:
            return self.nom + ', ' + self.parent.nom
        return self.nom

class Saison(Model):
    lieu = ForeignKey(Lieu, related_name='saisons')
    debut = DateField(verbose_name=u'début')
    fin = DateField()
    class Meta:
        ordering = ['lieu', 'debut']
    def __unicode__(self):
        return self.lieu.__unicode__() + ', ' + self.debut.year.__str__() + '-' + self.fin.year.__str__()

class Profession(Model):
    nom = CharField(max_length=200)
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
    date = DateField(blank=True, null=True)
    lieu = ForeignKey(Lieu, related_name='ancrages', blank=True, null=True)
    date_approx = CharField(max_length=200, blank=True,
        verbose_name=u'date approximative',
        help_text=u'Ne remplir que si la date est imprécise.')
    lieu_approx = CharField(max_length=200, blank=True,
        verbose_name=u'lieu approximatif',
        help_text=u'Ne remplir que si le lieu est imprécis.')
    class Meta:
        verbose_name = u'ancrage spatio-temporel'
        verbose_name_plural = u'ancrages spatio-temporels'
    def __unicode__(self):
        out = ''
        pre = ''
        post = ''
        if self.date:
            pre = self.date.__str__()
        else:
            pre = self.date_approx
        if self.lieu:
            post = self.lieu.nom
        else:
            post = self.lieu_approx
        if pre != '':
            out = u'le ' + pre + u' '
        if post != '':
            out += u'à ' + post
        return out

class Prenom(Model):
    prenom = CharField(max_length=100, verbose_name=u'prénom')
    classement = FloatField()
    favori = BooleanField()
    class Meta:
        verbose_name = u'prénom'
        ordering = ['classement']
    def __unicode__(self):
        return self.prenom

class TypeDeParenteDIndividus(Model):
    nom = CharField(max_length=50)
    nom_pluriel = CharField(max_length=55, blank=True, help_text=PLURAL_MSG)
    importance = FloatField()
    class Meta:
        verbose_name = u"type de parenté d'individus"
        verbose_name_plural = u"types de parenté d'individus"
        ordering = ['importance']
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
        for i, individu in enumerate(self.individus_cibles.all()):
            out += ' ' + individu.__unicode__()
            if i < len(self.individus_cibles.all()) - 1:
                out += ' ;'
        return out

class Individu(Model):
    nom = CharField(max_length=200)
    nom_naissance = CharField(max_length=200, blank=True,
        verbose_name=u'nom de naissance')
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
        ('F', 'Féminin'),
    )
    sexe = CharField(max_length=1, choices=SEXES, blank=True)
    ancrage_naissance = ForeignKey(AncrageSpatioTemporel, blank=True, null=True,
        related_name='individus_nes', verbose_name=u'ancrage de naissance')
    ancrage_deces = ForeignKey(AncrageSpatioTemporel, blank=True, null=True,
        related_name='individus_decedes', verbose_name=u'ancrage du décès')
    ancrage_approx = ForeignKey(AncrageSpatioTemporel, blank=True, null=True,
        related_name='individus', verbose_name=u'ancrage approximatif',
        help_text=u'Ne remplir que si on ne connaît aucune date précise.')
    professions = ManyToManyField(Profession, related_name='individus',
        blank=True, null=True)
    parentes = ManyToManyField(ParenteDIndividus, related_name='individus_orig',
        blank=True, null=True, verbose_name='parentés')
    biographie = HTMLField(blank=True)
    illustrations = ManyToManyField(Illustration, related_name='individus',
        blank=True, null=True)
    documents = ManyToManyField(Document, related_name='individus',blank=True,
        null=True)
    etat = ForeignKey(Etat, related_name='individus', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    class Meta:
        ordering = ['nom']
    def save(self, *args, **kwargs):
        super(Individu, self).save(*args, **kwargs)
        self.slug = autoslugify(Individu, self.__unicode__(), self.slug)
        super(Individu, self).save(*args, **kwargs)
    def __unicode__(self):
        out = ''
        prenoms = ''
        nom = ''
        pseudonyme = ''
        if self.prenoms and (self.designation == 'S' or self.designation == 'F'):
            for i, prenom in enumerate(self.prenoms.all()):
                prenoms += prenom.__unicode__()
                if i < len(self.prenoms.all()) - 1:
                    prenoms += ' '
        if self.designation == 'S' or self.designation == 'L':
            nom = self.nom
        if self.pseudonyme and (self.designation == 'S' or self.designation == 'P'):
                pseudonyme = self.pseudonyme
        if self.designation == 'S':
            if prenoms != '':
                out = prenoms + u' '
            out += nom
            if pseudonyme != '':
                out += u', dit ' + pseudonyme
        else:
            out = prenoms + nom + pseudonyme
        return out

class Devise(Model):
    nom = CharField(max_length=200, blank=True)
    symbole = CharField(max_length=10)

class Engagement(Model):
    individus = ManyToManyField(Individu, related_name='engagements')
    fonction = ForeignKey(Profession, related_name='engagements')
    salaire = FloatField(blank=True)
    devise = ForeignKey(Devise, blank=True, null=True, related_name='engagements')

class Personnel(Model):
    saison = ForeignKey(Saison, related_name='personnels')
    engagements = ManyToManyField(Engagement, related_name='personnels')

class GenreDOeuvre(Model):
    nom = CharField(max_length=400)
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
        self.slug = autoslugify(GenreDOeuvre, self.nom, self.slug)
        super(GenreDOeuvre, self).save(*args, **kwargs)
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class TypeDeCaracteristiqueDOeuvre(Model):
    nom = CharField(max_length=200, help_text=u'Exemple : « tonalité » (sans taper les guillemets)')
    importance = FloatField(help_text=u"Exemple : pour l'ordre « œuvre, découpage, tonalité », on donne une importance plus grande au découpage.")
    class Meta:
        verbose_name = u"type de caractéristique d'œuvre"
        verbose_name_plural = u"types de caracteristique d'œuvre"
        ordering = ['-importance']
    def __unicode__(self):
        return self.nom

class CaracteristiqueDOeuvre(Model):
    type = ForeignKey(TypeDeCaracteristiqueDOeuvre, related_name='caracteristiques_d_oeuvre')
    valeur = CharField(max_length=400, help_text=u'Exemple : « en trois actes » (sans taper les guillemets)')
    classement = FloatField(help_text=u"Par exemple, on peut choisir de classer les découpages par nombre d'actes.")
    class Meta:
        verbose_name = u"caractéristique d'œuvre"
        verbose_name_plural = u"caractéristiques d'œuvre"
        ordering = ['type', 'classement']
    def __unicode__(self):
        return self.type.__unicode__() + ' : ' + self.valeur

class Role(Model):
    nom = CharField(max_length=200)
    importance = FloatField()
    class Meta:
        verbose_name = u'rôle'
        ordering = ['importance']
    def __unicode__(self):
        return self.nom

class Pupitre(Model):
    role = ForeignKey(Role, related_name='pupitres', verbose_name=u'rôle')
    quantite_min = IntegerField(default=1, verbose_name=u'quantité minimale')
    quantite_max = IntegerField(default=1, verbose_name=u'quantité maximale')
    def __unicode__(self):
        out = str(self.quantite_min)
        if self.quantite_min != self.quantite_max:
            out += u' à %d' % self.quantite_max
        out += ' ' + str(self.role)
        return out

class Oeuvre(Model):
    prefixe_titre = CharField(max_length=20, blank=True,
        verbose_name=u'préfixe du titre')
    titre = CharField(max_length=200, blank=True)
    liaison = CharField(max_length=20, blank=True)
    prefixe_soustitre = CharField(max_length=20, blank=True,
        verbose_name=u'préfixe du sous-titre')
    soustitre = CharField(max_length=200, blank=True, verbose_name='sous-titre')
    genre = ForeignKey(GenreDOeuvre, related_name='oeuvres')
    caracteristiques = ManyToManyField(CaracteristiqueDOeuvre, blank=True,
        null=True, verbose_name=u'caractéristiques')
    auteurs = ManyToManyField(Individu, related_name='oeuvres', blank=True,
        null=True)
    description = HTMLField(blank=True)
    pupitres = ManyToManyField(Role, related_name='oeuvres', blank=True,
        null=True)
    parents = ManyToManyField('Oeuvre', related_name='enfants', blank=True,
        null=True)
    referenced = BooleanField(default=True, verbose_name=u'référencée')
    documents = ManyToManyField(Document, related_name='oeuvres', blank=True,
        null=True)
    illustrations = ManyToManyField(Illustration, related_name='oeuvres',
        blank=True, null=True)
    etat = ForeignKey(Etat, related_name='oeuvres', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = u'œuvre'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Oeuvre, self.titre, self.slug)
        super(Oeuvre, self).save(*args, **kwargs)
    def __unicode__(self):
        out = u''
        if self.titre:
            if self.prefixe:
                out = self.prefixe + u' '
            out += self.titre
            if self.soustitre:
                out += u', ou ' + self.soustitre
        else:
            out = self.genre.nom
            for caracteristique in self.caracteristiques:
                out += ', ' + caracteristique.valeur
        return out

class AttributionDeRole(Model):
    pupitre = ForeignKey(Pupitre, related_name='attributions_de_role')
    individus = ManyToManyField(Individu, related_name='attributions_de_role')
    class Meta:
        verbose_name = u'attribution de rôle'
    def __unicode__(self):
        return str(self.pupitre)

class ElementDeProgramme(Model):
    oeuvre = ForeignKey(Oeuvre, related_name='elements_de_programme', verbose_name=u'œuvre', blank=True, null=True)
    autre = CharField(max_length=500, blank=True)
    premiere_relative = BooleanField(verbose_name=u'première relative')
    premiere_absolue = BooleanField(verbose_name=u'première absolue')
    classement = FloatField()
    distribution = ManyToManyField(AttributionDeRole, related_name='elements_de_programme', blank=True, null=True)
    illustrations = ManyToManyField(Illustration, related_name='representations', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='representations', blank=True, null=True)
    etat = ForeignKey(Etat, related_name='elements_de_programme', null=True, blank=True)
    class Meta:
        verbose_name = u'élément de programme'
        verbose_name_plural = u'éléments de programme'
        ordering = ['classement']
    def __unicode__(self):
        if self.oeuvre:
            return self.oeuvre.__unicode__()
        elif self.autre:
            return self.autre
        else:
            return str(self.classement)

class Evenement(Model):
    date_debut = DateField()
    heure_debut = TimeField(blank=True, null=True)
    date_fin = DateField(blank=True, null=True, help_text=u'À ne préciser que si l\'événement dure plusieurs jours.')
    heure_fin = TimeField(blank=True, null=True)
    lieu = ForeignKey(Lieu, related_name='evenements')
    relache = BooleanField(verbose_name=u'relâche')
    circonstance = CharField(max_length=500, blank=True)
    programme = ManyToManyField(ElementDeProgramme, related_name='evenements', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='evenements', blank=True, null=True)
    illustrations = ManyToManyField(Illustration, related_name='evenements', blank=True, null=True)
    etat = ForeignKey(Etat, related_name='evenements', null=True, blank=True)
    notes = HTMLField(blank=True)
    class Meta:
        verbose_name = u'événement'
        ordering = ['date_debut', 'heure_debut', 'lieu']
    def __unicode__(self):
        return self.lieu.nom + ' le ' + self.date_debut.__str__()

class TypeDeSource(Model):
    nom = CharField(max_length=200)
    nom_pluriel = CharField(max_length=230, blank=True,
        verbose_name='nom (au pluriel)',
        help_text=PLURAL_MSG)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = 'type de source'
        verbose_name_plural = 'types de source'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(TypeDeSource, self.nom, self.slug)
        super(TypeDeSource, self).save(*args, **kwargs)
    def pluriel(self):
        return calc_pluriel(self)
    def __unicode__(self):
        return self.nom

class Source(Model):
    nom = CharField(max_length=200)
    numero = CharField(max_length=50, blank=True)
    date = DateField()
    page = CharField(max_length=50, blank=True)
    type = ForeignKey(TypeDeSource, related_name='sources')
    contenu = HTMLField(blank=True)
    evenements = ManyToManyField(Evenement, related_name='sources', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='sources', blank=True, null=True)
    illustrations = ManyToManyField(Illustration, related_name='sources', blank=True, null=True)
    etat = ForeignKey(Etat, related_name='sources', null=True, blank=True)
    notes = HTMLField(blank=True)
    class Meta:
        ordering = ['date', 'nom']
    def __unicode__(self):
        return self.pk.__str__()

