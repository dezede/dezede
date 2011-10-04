from django.db.models import *
import datetime

class Default(Model):
    author = CharField(max_length=200)
    deleted = BooleanField()

class Illustration(Default):
    image = ImageField(upload_to='.')
    description = TextField()

class Lieu(Model):
    nom = CharField(max_length=200)
    parent = ForeignKey('self', related_name='enfants', null=True, blank=True)
    slug = SlugField()
    class Meta:
        ordering = ['nom']
    def __unicode__(self):
        return self.nom

class Individu(Model):
    nom = CharField(max_length=200)
    prenoms = CharField(max_length=200)
    profession = CharField(max_length=200)
    def __unicode__(self):
        return self.nom

class Oeuvre(Model):
    nom = CharField(max_length=200)
    type = CharField(max_length=200)
    auteurs = ManyToManyField(Individu, related_name='oeuvres')
    slug = SlugField()
    def __unicode__(self):
        return self.nom

class Programme(Model):
    oeuvres = ManyToManyField(Oeuvre, related_name='programmes')

class Source(Model):
    date = DateField()
    lieu = ForeignKey(Lieu, related_name='sources')
    nom = CharField(max_length=500, blank=True)
    programme = ForeignKey(Programme, related_name='sources')
    contenu = TextField()
    class Meta:
        ordering = ['date']
    def __unicode__(self):
        return self.date.__str__()
