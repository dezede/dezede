# coding: utf-8
from django.db.models import *
from tinymce.models import *
import datetime
from django.template.defaultfilters import slugify

def autoslugify(Mod, nom):
    nom_slug = slug_orig = slugify(nom)
    n = 0
    while Mod.objects.filter(slug=nom_slug).count():
        n += 1;
        nom_slug = slug_orig + str(n)
    return nom_slug

class Lieu(Model):
    nom = CharField(max_length=200)
    parent = ForeignKey('self', related_name='enfants', null=True, blank=True)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name_plural = 'lieux'
        ordering = ['nom']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Lieu, self.nom)
        super(Lieu, self).save(*args, **kwargs)
    def __unicode__(self):
        if self.parent:
            return self.nom + ', ' + self.parent.nom
        return self.nom

class Individu(Model):
    nom = CharField(max_length=200)
    prenoms = CharField(max_length=200, verbose_name='prénoms')
    naissance = CharField(max_length=100)
    mort = CharField(max_length=100)
    profession = CharField(max_length=200)
    parents = ManyToManyField('Individu', related_name='enfants', blank=True)
    slug = SlugField(blank=True)
    class Meta:
        ordering = ['nom']
    def save(self, *args, **kwargs):
        if self.slug == '':
            self.slug = autoslugify(Individu, self.__unicode__())
        super(Individu, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.prenoms + ' ' + self.nom

class Oeuvre(Model):
    titre = CharField(max_length=200)
    soustitre = CharField(max_length=200, blank=True, verbose_name='sous-titre')
    genre = CharField(max_length=400)
    auteurs = ManyToManyField(Individu, related_name='oeuvres', blank=True)
    slug = SlugField(blank=True)
    def save(self, *args, **kwargs):
        if self.slug == '':
            self.slug = autoslugify(Oeuvre, self.titre)
        super(Oeuvre, self).save(*args, **kwargs)
    def __unicode__(self):
        if self.soustitre and Oeuvre.objects.filter(titre=self.titre).count() > 1:
            return self.titre + ' / ' + self.soustitre
        else:
            return self.titre

class Programme(Model):
    oeuvres = ManyToManyField(Oeuvre, related_name='programmes', verbose_name='œuvres')
    def __unicode__(self):
        disp_str = ''
        for i, oeuvre in enumerate(self.oeuvres.all()):
            disp_str += oeuvre.titre
            if i < len(self.oeuvres.all()) - 1:
                disp_str += '  -  '
        return disp_str

class Evenement(Model):
    nom = CharField(max_length=500, blank=True)
    date = DateField()
    lieu = ForeignKey(Lieu, related_name='evenements')
    programme = ForeignKey(Programme, related_name='evenements')
    class Meta:
        verbose_name = 'événement'
        ordering = ['date', 'lieu']
    def __unicode__(self):
        if self.nom:
            return self.nom
        else:
            return self.lieu.nom + ' le ' + self.date.__str__()

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
    evenement = ForeignKey(Evenement, related_name='sources', verbose_name='événement')
    type = ForeignKey(TypedeSource, related_name='sources')
    contenu = HTMLField()
    class Meta:
        ordering = ['evenement']
    def __unicode__(self):
        return self.pk.__str__()

