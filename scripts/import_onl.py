# coding: utf-8

from __future__ import unicode_literals
import datetime
import re

from bs4 import BeautifulSoup
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import transaction
from django.test import Client
from django.utils.encoding import force_text
from haystack import signal_processor
from IPython.display import display, HTML
from accounts.models import HierarchicUser
import johnny.cache
import numpy as np
import pandas

from libretto.api.models.utils import update_or_create, KEEP
from libretto.models import Etat, Ensemble, Profession, Prenom, Individu, \
    Auteur, Oeuvre, NatureDeLieu, LieuDivers, Institution, \
    ElementDeDistribution, AncrageSpatioTemporel, Evenement, ElementDeProgramme


signal_processor.teardown()
cache.clear()
johnny.cache.enable()


#client = Client()
#client.login(username='bertrand', password='')

def display_evenement(evenement):
    r = client.get(reverse('evenement_pk', args=(evenement.pk,)))
    evenement_html = BeautifulSoup(r.content).section
    evenement_html.find(class_='btn-toolbar').extract()
    display(HTML(force_text(evenement_html)))

etat = update_or_create(Etat, dict(
            nom='importé(e) automatiquement',
            nom_pluriel='importé(e)s automatiquement',
            message='<p>Les données ci-dessous ont été importées '
                    'automatiquement et sont en attente de relecture.',
            public=False), unique_keys=('nom',))

onl_ensemble = Ensemble.objects.get_or_create(nom='Orchestre national de Lyon', defaults={'etat': etat})[0]
onl = HierarchicUser.objects.get_or_create(
    username='onl', last_name='Orchestre national de Lyon',
    content_type=ContentType.objects.get_for_model(Ensemble),
    object_id=onl_ensemble.pk)[0]
onl_ensemble.owner = onl
onl_ensemble.save()



DATE_COL = u'Date de la représentation'
TIME_COL = 'Horaire'
PROGRAMME_COL = u'Code du programme / série'
OEUVRES_COL = u'Œuvres'
SALLE_COL = 'Nom de la salle'
VILLE_COL = 'ville'
DISTRIBUTION_COL = u'Distribution : direction, mise en scène, interprètes, etc.'

def to_time(time_str):
    if time_str == 'nan':
        return np.NaN
    parts = map(int, time_str.split('h'))
    return datetime.time(*parts)

def to_oeuvres(oeuvres_str):
    rows = oeuvres_str.split('\n')
    oeuvres = []
    compositeur = Profession.objects.get(nom__iexact='compositeur')
    for row in rows:
        row = row.strip(' ,.;')
        if not row:
            continue
        parts = row.split(';')
        auteur_prenoms, auteur_nom = '', ''
        if len(parts) > 3:
            print row
            parts = parts[:3]
        if len(parts) == 3:
            oeuvre, auteur_prenoms, auteur_nom = parts
        elif len(parts) == 1:
            oeuvre = row
        elif len(parts) == 2:
            oeuvre, auteur = parts
            auteur_parts = auteur.split(' ')
            if len(auteur_parts) == 2:
                auteur_prenoms, auteur_nom = auteur_parts
            else:
                auteur_nom = auteur
        auteurs = []
        if auteur_nom:
            auteur_nom = auteur_nom.strip()
            prenoms = []
            if auteur_prenoms:
                auteur_prenoms = auteur_prenoms.strip()
                prenom = Prenom.objects.create(prenom=auteur_prenoms, owner=onl)
                prenoms.append(prenom)
            individu = update_or_create(Individu, dict(nom=auteur_nom, prenoms=prenoms, etat=etat, owner=onl), unique_keys=('nom', 'prenoms__prenom'), conflict_handling=KEEP)
            auteurs.append(Auteur(individu=individu, profession=compositeur, owner=onl))
        oeuvre = update_or_create(Oeuvre, dict(titre=oeuvre, auteurs=auteurs, etat=etat, owner=onl), unique_keys=('titre', 'auteurs__individu'), conflict_handling=KEEP)
        oeuvres.append(oeuvre)
    return oeuvres

VILLE = NatureDeLieu.objects.get(nom='ville')
SALLE = NatureDeLieu.objects.get(nom='salle')


def to_lieux(row):
    ville = LieuDivers.objects.get_or_create(nom=row[VILLE_COL], nature=VILLE, defaults={'etat': etat, 'owner': onl})[0]
    salle = Institution.objects.get_or_create(nom=row[SALLE_COL], parent=ville, defaults={'etat': etat, 'owner': onl, 'nature': SALLE})[0]
    row[SALLE_COL] = salle
    return row


def to_distribution(distribution_str):
    parts = distribution_str.split('\n')
    distribution = []
    for part in parts:
        part = part.strip(' ,.')
        profession = None
        if ',' in part:
            nom_complet, profession = part.split(',')
            profession = profession.strip(' ,.')
        else:
            nom_complet = part
        if profession is not None:
            try:
                profession = Profession.objects.get(nom__iexact=profession)
            except Profession.DoesNotExist:
                profession = Profession.objects.create(nom=profession, owner=onl, etat=etat)
        nom_parts = nom_complet.split(' ')
        prenoms = []
        if len(nom_parts) == 2 and part != 'solistes ONL' and u'chœur' not in part and 'choeur' not in part:
            prenom, nom = nom_parts
            prenom = Prenom.objects.create(prenom=prenom, owner=onl)
            prenoms.append(prenom)
        else:
            nom = nom_complet
        individu = update_or_create(Individu, dict(nom=nom, prenoms=prenoms, etat=etat, owner=onl), unique_keys=('nom', 'prenoms__prenom'), conflict_handling=KEEP)
        item = ElementDeDistribution.objects.create(profession=profession, owner=onl)
        item.individus.add(individu)
        distribution.append(item)
    return distribution


@transaction.commit_on_success
def import_excel(excel_path):
    print u'Ouverture de la source…'
    df = pandas.read_excel(excel_path, 1)
    df = df[np.isfinite(df[PROGRAMME_COL])]
    df[PROGRAMME_COL] = df[PROGRAMME_COL].astype(int)
    print u'Conversion des horaires…'
    df[TIME_COL] = df[TIME_COL].astype(str).apply(to_time)
    print u'Analyse des œuvres…'
    replacements = (
        ('Claude.debussy', 'Claude;Debussy'),
        (u'Concerto pour piano n°1,Franz;Liszt', u'Concerto pour piano n°1;Franz;Liszt'),
        (u'Lions;Ned:Rorem', u'Lions;Ned;Rorem'),
        (u'Pied Piper Fantasy;John.Corigliano', u'Pied Piper Fantasy;John;Corigliano'),
        ('Ludwig van Beetoven', 'Ludwig van;Beethoven'),
        ('Ludvwig van Beetoven', 'Ludwig van;Beethoven'),
        ('Benjamin Britten', 'Benjamin;Britten'),
        ('Robert Schumann', 'Robert;Schumann'),
    )
    for a, b in replacements:
        df[OEUVRES_COL] = df[OEUVRES_COL].str.replace(a, b)
    df[OEUVRES_COL] = df[OEUVRES_COL].replace(re.compile(r'\s*,\s*'), ', ')
    df[OEUVRES_COL] = df[OEUVRES_COL].apply(to_oeuvres)
    print u'Analyse des lieux…'
    df = df.apply(to_lieux, axis=1)
    print u'Analyse des distributions…'
    replacements = (
        ('chef de choeur', u'chef de chœur'),
        ('Bruno, Mantovani, direction', 'Bruno Mantovani, direction'),
        (u'Renaud, Capuçon, violon', u'Renaud Capuçon, violon'),
        ('Leonard, Slatkin, direction', 'Leonard Slatkin, direction'),
        (u'Steve, Davislim, ténor', u'Steve Davislim, ténor'),
        (' / ', '\n'),
        (u'Norman, Scribner, chef de chœur', u'Norman Scribner, chef de chœur'),
        (u'Stefan, Bevier, Chef de chœur associé', u'Stefan Bevier, Chef de chœur associé'),
        (u'Catherine, Molmerret, Chef de chœur', u'Catherine Molmerret, chef de chœur'),
    )
    for a, b in replacements:
        df[DISTRIBUTION_COL] = df[DISTRIBUTION_COL].str.replace(a, b)
    df[DISTRIBUTION_COL] = df[DISTRIBUTION_COL].apply(to_distribution)
    print u'Construction des événements…'
    for index, row in df.iterrows():
        ancrage = AncrageSpatioTemporel.objects.create(lieu=row[SALLE_COL], date=row[DATE_COL].date(), heure=row[TIME_COL], owner=onl)
        evenement = Evenement.objects.create(ancrage_debut=ancrage, etat=etat, owner=onl)
        for i, oeuvre in enumerate(row[OEUVRES_COL], start=1):
            ElementDeProgramme.objects.create(evenement=evenement, oeuvre=oeuvre, position=i, owner=onl, etat=etat)
        evenement.distribution.add(*row[DISTRIBUTION_COL])
        el = ElementDeDistribution.objects.create(owner=onl)
        el.ensembles.add(onl_ensemble)
        evenement.distribution.add(el)
        #display_evenement(evenement)


def run():
    import_excel('scripts/data/Orch. Lyon saison 2010-11 - ex. 2011.xls')
    import_excel('scripts/data/Orch. Lyon saison 2011-12 - ex 2012.xls')
    import_excel('scripts/data/Orch. Lyon - saison 2012-13 - ex. 2013.xls')
