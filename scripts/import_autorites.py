# coding: utf-8

import csv, re, sys
from django.template.defaultfilters import title
from django.contrib.contenttypes.models import ContentType
from catalogue.models import Oeuvre, Prenom, Individu, Auteur, Profession, \
    AncrageSpatioTemporel, GenreDOeuvre, TypeDeCaracteristiqueDOeuvre, \
    CaracteristiqueDOeuvre
from catalogue.api import build_ancrage
from catalogue.api.models.utils import update_or_create
from catalogue.api.utils import notify_send
from .routines import print_error, print_success, print_warning


TITRE_RE = re.compile(r'^(?P<titre>[^\(]+)\s+'
                      r'\((?P<particule>[^\)]+)\)$')
INDIVIDU_FULL_RE = re.compile(r'^(?P<nom>[^,]+),\s+'
                              r'(?P<prenoms>[^\(]+)\s+'
                              r'\((?P<dates>[^\)]+)\)$')
PSEUDONYME_RE = re.compile(r'^(?P<prenoms>[^,]+),?\s+'
                           r'dit\s+(?P<pseudonyme>[^\)]+)$')


def split_titre(titre):
    particule = ''
    match = TITRE_RE.match(titre)
    if match:
        particule = match.group('particule')
        titre = match.group('titre')
        if particule[-1] not in "'’":
            particule += ' '
    return particule, titre


def split_individus(individus):
    return individus.split(' ; ')


def build_individu(individu_str):
    match = INDIVIDU_FULL_RE.match(individu_str)
    if match:
        nom = title(match.group('nom'))
        pseudonyme = ''
        prenom_str = match.group('prenoms')
        dates = match.group('dates')
        match_pseudonyme = PSEUDONYME_RE.match(prenom_str)
        if match_pseudonyme:
            prenom_str = match_pseudonyme.group('prenoms')
            pseudonyme = match_pseudonyme.group('pseudonyme')
        prenom_strs = [p for p in prenom_str.split() if p]
        prenoms = [Prenom.objects.get_or_create(prenom=prenom_str)[0]
                   for prenom_str in prenom_strs]

        naissance, deces = dates.split('-')
        i = Individu.objects.filter(nom=nom, prenoms__in=prenoms,
                                    pseudonyme=pseudonyme,
                                    ancrage_naissance__date_approx=naissance,
                                    ancrage_deces__date_approx=deces).distinct()
        if i.exists():
            assert i.count() == 1
            return i[0]
        ancrage_naissance = AncrageSpatioTemporel.objects.create(
                                                         date_approx=naissance)
        ancrage_deces = AncrageSpatioTemporel.objects.create(date_approx=deces)
        individu = update_or_create(Individu, ['nom', 'ancrage_naissance',
                                               'ancrage_deces'],
                                    nom=nom, pseudonyme=pseudonyme,
                                    ancrage_naissance=ancrage_naissance,
                                    ancrage_deces=ancrage_deces)
        individu.prenoms.add(*prenoms)
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
        aut = Auteur.objects.get_or_create(profession=profession,
                                           individu=individu,
                                           content_type=Oeuvre_cti,
                                           object_id=oeuvre_obj.id)[0]
        aut.clean()


exceptions = []


def print_exception(i, titre, e, notify=False):
    msg = 'Exception sur la %se ligne (œuvre %s) : %s' % (i, titre, e)
    if notify:
        notify_send(msg)
    print_error(msg)


def import_oeuvre(i, oeuvre, bindings):
    # Titre :
    titre = oeuvre[bindings['titre']]
    particule, titre = split_titre(titre)
    try:
        titre2 = oeuvre[bindings['titre_secondaire']]
        particule2, titre2 = split_titre(titre2)
        coordination = ', ou ' if titre2 else ''
        oeuvre_obj = update_or_create(Oeuvre, ['titre', 'titre_secondaire'],
            prefixe_titre=particule, titre=titre, coordination=coordination,
            prefixe_titre_secondaire=particule2, titre_secondaire=titre2)
        # TODO: Titres de la version originale à faire
        # Auteurs :
        for profession, profession_pluriel, auteurs_key in bindings['auteurs']:
            auteurs = oeuvre[auteurs_key]
            build_auteurs(oeuvre_obj, auteurs, profession, profession_pluriel)
        # Genre :
        genre = GenreDOeuvre.objects.get_or_create(
                                      nom=oeuvre[bindings['genre']].strip())[0]
        oeuvre_obj.genre = genre
        # Caractéristiques :
        for type_nom, type_nom_pluriel, caracteristique_key \
                                               in bindings['caracteristiques']:
            type = update_or_create(TypeDeCaracteristiqueDOeuvre, ['nom'],
                                    nom=type_nom, nom_pluriel=type_nom_pluriel)
            caracteristique = CaracteristiqueDOeuvre.objects.get_or_create(
                              type=type, valeur=oeuvre[caracteristique_key])[0]
            oeuvre_obj.caracteristiques.add(caracteristique)
        # Ancrage de création :
        creation_str = oeuvre[bindings['creation'][0]]
        if creation_str:
            try:
                oeuvre_obj.ancrage_creation = build_ancrage(
                                creation_str.split(bindings['creation'][1])[0])
            except:
                print_warning('Impossible de parser la création de « %s »'
                              % oeuvre_obj)
        # [Sauvegarde] :
        oeuvre_obj.save()
        print_success(oeuvre_obj)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        e = sys.exc_info()
        sys.excepthook(*e)
        print_exception(i, titre, e, notify=True)
        exceptions.append([i, titre, e])


def import_csv_file(csv_file, bindings):
    oeuvres = list(csv.DictReader(csv_file))
    for i, oeuvre in enumerate(oeuvres):
        import_oeuvre(i, oeuvre, bindings)


def import_from_data_module(data_module):
    for csv_file in data_module.csv_files:
        import_csv_file(csv_file, data_module.bindings)


def run():
    from .data import data_modules
    for data_module in data_modules:
        import_from_data_module(data_module)
