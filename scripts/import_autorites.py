# coding: utf-8

import csv, re, os.path
from django.template.defaultfilters import title
from django.contrib.contenttypes.models import ContentType
from catalogue.models import Oeuvre, Prenom, Individu, Auteur, Profession, \
    AncrageSpatioTemporel, GenreDOeuvre, TypeDeCaracteristiqueDOeuvre, \
    CaracteristiqueDOeuvre


CURRENT_PATH = os.path.dirname(__file__)

DATA_FILENAME = os.path.join(CURRENT_PATH, 'data/{# destroyed from git history #}.csv')

oeuvres = list(
    csv.DictReader(open(DATA_FILENAME)))

TITRE_RE = re.compile(r'^(.+)\s+\((.+)\)$')
INDIVIDU_FULL_RE = re.compile(r'^(.+),\s+(.+)\s+\((.+)\)$')
PSEUDONYME_RE = re.compile(r'^(.+),?\s+dit\s+(.+)$')

def split_titre(titre):
    particule = ''
    match = TITRE_RE.match(titre)
    if match:
        particule = match.group(2)
        titre = match.group(1)
        if particule[-1] not in ("'", "’"):
            particule += ' '
    return particule, titre


def split_individus(individus):
    return individus.split(' ; ')


def build_individu(individu_str):
    match = INDIVIDU_FULL_RE.match(individu_str)
    if match:
        nom = title(match.group(1))
        pseudonyme = ''
        prenom = match.group(2)
        dates = match.group(3)
        match_pseudonyme = PSEUDONYME_RE.match(prenom)
        if match_pseudonyme:
            prenom = match_pseudonyme.group(1)
            pseudonyme = match_pseudonyme.group(2)
        prenom = Prenom.objects.get_or_create(prenom=prenom)[0]
        naissance, deces = dates.split('-')
        i = Individu.objects.filter(nom=nom, prenoms=prenom,
                                    pseudonyme=pseudonyme,
                                    ancrage_naissance__date_approx=naissance,
                                    ancrage_deces__date_approx=deces)
        if i.exists():
            assert len(i) == 1
            return i[0]
        naissance = AncrageSpatioTemporel.objects.create(date_approx=naissance)
        deces = AncrageSpatioTemporel.objects.create(date_approx=deces)
        individu = Individu.objects.get_or_create(nom=nom,
                                                  pseudonyme=pseudonyme,
                                                  ancrage_naissance=naissance,
                                                  ancrage_deces=deces)[0]
        individu.prenoms.add(prenom)
        individu.save()
        return individu


Oeuvre_cti = ContentType.objects.get(app_label='catalogue', model='oeuvre')


def build_auteurs(oeuvre_obj, individus_str, nom_profession,
                  nom_pluriel_profession=None):
    if nom_pluriel_profession is None:
        nom_pluriel_profession = nom_profession + 's'
    profession = Profession.objects.get_or_create(
        nom=nom_profession, nom_pluriel=nom_pluriel_profession)[0]
    individus = []
    for individu_str in split_individus(individus_str):
        individu = build_individu(individu_str)
        if individu:
            individus.append(individu)
    if not individus:
        return
    for individu in individus:
        aut = Auteur.objects.create(profession=profession, individu=individu,
                                    content_type=Oeuvre_cti,
                                    object_id=oeuvre_obj.id)
        aut.clean()


for oeuvre in oeuvres:
    titre = oeuvre['Titres principaux']
    particule, titre = split_titre(titre)
    titre2 = oeuvre['Titres secondaires']
    particule2, titre2 = split_titre(titre2)
    coordination = ', ou ' if titre2 else ''
    oeuvre_obj, oeuvre_obj_is_new = Oeuvre.objects.get_or_create(
        prefixe_titre=particule, titre=titre, coordination=coordination,
        prefixe_titre_secondaire=particule2, titre_secondaire=titre2)
    if not oeuvre_obj_is_new:
        continue
        #    print oeuvre_obj
    # TODO: Titres de la version originale à faire
    compositeurs = oeuvre['Compositeurs']
    build_auteurs(oeuvre_obj, compositeurs, 'compositeur')
    librettistes = oeuvre['Librettistes']
    build_auteurs(oeuvre_obj, librettistes, 'librettiste')
    genre = GenreDOeuvre.objects.get_or_create(nom=oeuvre['Genres'])[0]
    oeuvre_obj.genre = genre
    decoupage = TypeDeCaracteristiqueDOeuvre.objects.get_or_create(
        nom=u'découpage', nom_pluriel=u'découpages')[0]
    actes = CaracteristiqueDOeuvre.objects.get_or_create(type=decoupage,
                                                         valeur=oeuvre[
                                                                'Actes'])[0]
    oeuvre_obj.caracteristiques.add(actes)
    oeuvre_obj.save()
    print oeuvre_obj
