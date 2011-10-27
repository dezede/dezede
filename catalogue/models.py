# coding: utf-8
from django.db.models import *
from tinymce.models import *
import datetime
from django.template.defaultfilters import slugify

def autoslugify(Mod, nom, slug):
    if slug != '':
        return slug
    nom_slug = slug_orig = slugify(nom)
    n = 0
    while Mod.objects.filter(slug=nom_slug).count():
        n += 1;
        nom_slug = slug_orig + str(n)
    return nom_slug

class Statut(Model):
    nom = CharField(max_length=200)
    slug = SlugField(blank=True)
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Statut, self.nom, self.slug)
        super(Statut, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.nom

class NaturedeLieu(Model):
    nom = CharField(max_length=400)
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
    parent = ForeignKey('self', related_name='enfants', null=True, blank=True)
    nature = ForeignKey(NaturedeLieu, related_name='lieux')
    historique = HTMLField(blank=True)
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

class Individu(Model):
    nom = CharField(max_length=200)
    nom_jeunesse = CharField(max_length=200, verbose_name='nom de jeunesse')
    prenoms = CharField(max_length=200, verbose_name='prénoms', blank=True)
    surnom = CharField(max_length=200, blank=True)
    naissance = CharField(max_length=100, blank=True)
    mort = CharField(max_length=100, blank=True)
    profession = CharField(max_length=200)
    parents = ManyToManyField('Individu', related_name='enfants', blank=True)
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

class Oeuvre(Model):
    titre = CharField(max_length=200)
    soustitre = CharField(max_length=200, blank=True, verbose_name='sous-titre')
    genre = CharField(max_length=400)
    auteurs = ManyToManyField(Individu, related_name='oeuvres', blank=True)
    referenced = BooleanField(default=True, verbose_name='référencée')
    statut = ForeignKey(Statut, related_name='oeuvres', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    class Meta:
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
    statut = ForeignKey(Statut, related_name='representations', null=True, blank=True)
    class Meta:
        verbose_name = 'Représentation'
    def __unicode__(self):
        disp_str = ''
        for i, oeuvre in enumerate(self.oeuvres.all()):
            disp_str += oeuvre.titre
            if i < len(self.oeuvres.all()) - 2:
                disp_str += ', '
            if i == len(self.oeuvres.all()) - 1:
                disp_str += ' et '
        return disp_str

class Evenement(Model):
    date = DateField()
    heure = TimeField(blank=True, null=True)
    lieu = ForeignKey(Lieu, related_name='evenements')
    circonstance = CharField(max_length=500, blank=True)
    representations = ForeignKey(Representation, related_name='evenements')
    statut = ForeignKey(Statut, related_name='evenements', null=True, blank=True)
    notes = HTMLField(blank=True)
    class Meta:
        verbose_name = 'événement'
        ordering = ['date', 'heure', 'lieu']
    def __unicode__(self):
        out = self.lieu.nom + ' le ' + self.date.__str__()
        return out

class TypedeSource(Model):
    nom = CharField(max_length=200)
    pluriel = CharField(max_length=230)
    class Meta:
        verbose_name = 'type de source'
        verbose_name_plural = 'types de source'
        ordering = ['nom']
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
    statut = ForeignKey(Statut, related_name='sources', null=True, blank=True)
    notes = HTMLField(blank=True)
    class Meta:
        ordering = ['date', 'nom']
    def __unicode__(self):
        return self.pk.__str__()

