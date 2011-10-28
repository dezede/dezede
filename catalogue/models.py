# coding: utf-8
from django.db.models import *
from tinymce.models import *
import datetime
from django.template.defaultfilters import slugify
from filebrowser.fields import FileBrowseField

PLURAL_MSG = 'À remplir si le pluriel n\'est pas un simple ajout de « s ».  Exemple : « animal » devient « animaux » et non « animals ».'

def autoslugify(Mod, nom, slug):
    if slug != '':
        return slug
    nom_slug = slug_orig = slugify(nom)
    n = 0
    while Mod.objects.filter(slug=nom_slug).count():
        n += 1;
        nom_slug = slug_orig + str(n)
    return nom_slug

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
    nom = CharField(max_length=300, blank=True)
    image = FileBrowseField('Image', max_length=400, directory='images/')
    description = HTMLField(blank=True)
    class Meta:
        ordering = ['image']
    def __unicode__(self):
        if self.nom:
            return self.nom
        return self.image.__unicode__()

class Statut(Model):
    nom = CharField(max_length=200)
    nom_pluriel = CharField(max_length=230, blank=True,
                            verbose_name='nom (au pluriel)',
                            help_text=PLURAL_MSG)
    slug = SlugField(blank=True)
    class Meta:
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Statut, self.nom, self.slug)
        super(Statut, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.nom

class NaturedeLieu(Model):
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
        self.slug = autoslugify(NaturedeLieu, self.nom, self.slug)
        super(NaturedeLieu, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.nom

class Lieu(Model):
    nom = CharField(max_length=200)
    parent = ForeignKey('Lieu', related_name='enfants', null=True, blank=True)
    nature = ForeignKey(NaturedeLieu, related_name='lieux')
    historique = HTMLField(blank=True)
    illustrations = ManyToManyField(Illustration, related_name='lieux', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='lieux', blank=True, null=True)
    statut = ForeignKey(Statut, related_name='lieux', null=True, blank=True)
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
    debut = DateField(verbose_name='début')
    fin = DateField()
    class Meta:
        ordering = ['lieu', 'debut']
    def __unicode__(self):
        return self.lieu.__unicode__() + ', ' + self.debut.year.__str__() + '-' + self.fin.year.__str__()

class Profession(Model):
    nom = CharField(max_length=200)
    nom_pluriel = CharField(max_length=230, blank=True,
                            verbose_name='nom (au pluriel)',
                            help_text=PLURAL_MSG)
    slug = SlugField(blank=True)
    class Meta:
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Profession, self.__unicode__(), self.slug)
        super(Profession, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.nom

class Individu(Model):
    nom = CharField(max_length=200)
    nom_jeunesse = CharField(max_length=200, verbose_name='nom de jeunesse', blank=True)
    prenoms = CharField(max_length=200, verbose_name='prénoms', blank=True)
    surnom = CharField(max_length=200, blank=True)
    date_naissance = DateField(blank=True, null=True, verbose_name='date de naissance')
    lieu_naissance = ForeignKey(Lieu, related_name='individus_nes', blank=True, null=True, verbose_name='lieu de naissance')
    date_naissance_approx = CharField(max_length=200, blank=True,
                                      verbose_name='date approximative de naissance',
                                      help_text='Ne remplir que si la date de naissance est imprécise.')
    lieu_naissance_approx = CharField(max_length=200, blank=True,
                                      verbose_name='lieu approximatif de naissance',
                                      help_text='Ne remplir que si le lieu de naissance est imprécis.')
    date_mort = DateField(blank=True, null=True, verbose_name='date de décès')
    lieu_mort = ForeignKey(Lieu, related_name='individus_morts', blank=True, null=True, verbose_name='lieu de décès')
    date_mort_approx = CharField(max_length=200, blank=True,
                                 verbose_name='date approximative de décès',
                                 help_text='Ne remplir que si la date de décès est imprécise.')
    lieu_mort_approx = CharField(max_length=200, blank=True,
                                 verbose_name='lieu approximatif de décès',
                                 help_text='Ne remplir que si le lieu de décès est imprécis.')
    epoque = CharField(max_length=200, blank=True,
                       verbose_name='époque approximative',
                       help_text='Ne remplir que si aucun champ de date ci-dessus ne convient.')
    lieu_approx = CharField(max_length=200, blank=True,
                            verbose_name='lieu approximatif',
                            help_text='Ne remplir que si aucun champ de lieu ci-dessus ne convient.')
    professions = ManyToManyField(Profession, related_name='individus')
    parents = ManyToManyField('Individu', related_name='enfants', blank=True)
    biographie = HTMLField(blank=True)
    illustrations = ManyToManyField(Illustration, related_name='individus', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='individus', blank=True, null=True)
    statut = ForeignKey(Statut, related_name='individus', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    class Meta:
        ordering = ['nom']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Individu, self.__unicode__(), self.slug)
        super(Individu, self).save(*args, **kwargs)
    def __unicode__(self):
        out = self.nom
        if self.prenoms:
            out = self.prenoms + ' ' + out
        if self.surnom:
            out += ', dit ' + self.surnom
        return out

class Livret(Model):
    titre = CharField(max_length=200)
    soustitre = CharField(max_length=200, blank=True, verbose_name='sous-titre')
    auteurs = ManyToManyField(Individu, related_name='livrets', blank=True)
    description = HTMLField(blank=True)
    parents = ManyToManyField('Livret', related_name='enfants', blank=True)
    documents = ManyToManyField(Document, related_name='livrets', blank=True, null=True)
    illustrations = ManyToManyField(Illustration, related_name='livrets', blank=True, null=True)
    statut = ForeignKey(Statut, related_name='livrets', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    class Meta:
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Livret, self.titre, self.slug)
        super(Livret, self).save(*args, **kwargs)
    def __unicode__(self):
        if self.soustitre and Livret.objects.filter(titre=self.titre).count() > 1:
            return self.titre + ' / ' + self.soustitre
        else:
            return self.titre

class Oeuvre(Model):
    titre = CharField(max_length=200)
    soustitre = CharField(max_length=200, blank=True, verbose_name='sous-titre')
    genre = CharField(max_length=400)
    livret = ForeignKey(Livret, related_name='oeuvres', blank=True, null=True)
    auteurs = ManyToManyField(Individu, related_name='oeuvres', blank=True, null=True)
    description = HTMLField(blank=True)
    parents = ManyToManyField('Oeuvre', related_name='enfants', blank=True, null=True)
    referenced = BooleanField(default=True, verbose_name='référencée')
    documents = ManyToManyField(Document, related_name='oeuvres', blank=True, null=True)
    illustrations = ManyToManyField(Illustration, related_name='oeuvres', blank=True, null=True)
    statut = ForeignKey(Statut, related_name='oeuvres', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name='œuvre'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Oeuvre, self.titre, self.slug)
        super(Oeuvre, self).save(*args, **kwargs)
    def __unicode__(self):
        if self.soustitre and Oeuvre.objects.filter(titre=self.titre).count() > 1:
            return self.titre + ' / ' + self.soustitre
        else:
            return self.titre

class Representation(Model):
    oeuvres = ManyToManyField(Oeuvre, related_name='representations', verbose_name='œuvres')
    premiere_relative = BooleanField(verbose_name='première relative')
    premiere_absolue = BooleanField(verbose_name='première absolue')
    illustrations = ManyToManyField(Illustration, related_name='representations', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='representations', blank=True, null=True)
    statut = ForeignKey(Statut, related_name='representations', null=True, blank=True)
    class Meta:
        verbose_name = 'Représentation'
    def __unicode__(self):
        disp_str = ''
        for i, oeuvre in enumerate(self.oeuvres.all()):
            disp_str += oeuvre.titre
            if i < len(self.oeuvres.all()) - 2:
                disp_str += ', '
            if i == len(self.oeuvres.all()) - 2:
                disp_str += ' et '
        return disp_str

class Evenement(Model):
    date_debut = DateField()
    heure_debut = TimeField(blank=True, null=True)
    date_fin = DateField(blank=True, null=True, help_text='À ne préciser que si l\'événement dure plusieurs jours.')
    heure_fin = TimeField(blank=True, null=True)
    lieu = ForeignKey(Lieu, related_name='evenements')
    relache = BooleanField(verbose_name='relâche')
    circonstance = CharField(max_length=500, blank=True)
    representations = ForeignKey(Representation, related_name='evenements', verbose_name='représentations', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='evenements', blank=True, null=True)
    illustrations = ManyToManyField(Illustration, related_name='evenements', blank=True, null=True)
    statut = ForeignKey(Statut, related_name='evenements', null=True, blank=True)
    notes = HTMLField(blank=True)
    class Meta:
        verbose_name = 'événement'
        ordering = ['date_debut', 'heure_debut', 'lieu']
    def __unicode__(self):
        return self.lieu.nom + ' le ' + self.date_debut.__str__()

class TypedeSource(Model):
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
        self.slug = autoslugify(Oeuvre, self.titre, self.slug)
        super(Oeuvre, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.nom

class Source(Model):
    nom = CharField(max_length=200)
    numero = CharField(max_length=50, blank=True)
    date = DateField()
    page = CharField(max_length=50, blank=True)
    type = ForeignKey(TypedeSource, related_name='sources')
    contenu = HTMLField()
    evenements = ManyToManyField(Evenement, related_name='sources', verbose_name='événements')
    documents = ManyToManyField(Document, related_name='sources', blank=True, null=True)
    illustrations = ManyToManyField(Illustration, related_name='sources', blank=True, null=True)
    statut = ForeignKey(Statut, related_name='sources', null=True, blank=True)
    notes = HTMLField(blank=True)
    class Meta:
        ordering = ['date', 'nom']
    def __unicode__(self):
        return self.pk.__str__()

