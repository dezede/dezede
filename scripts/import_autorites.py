# coding: utf-8

from __future__ import unicode_literals
import csv
import re
import sys
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import title
from django.utils import translation
from catalogue.api import build_ancrage
from catalogue.api.models.utils import update_or_create, get_or_create, \
                                       enlarged_get
from catalogue.api.utils import notify_send, print_error, print_success, \
                                print_warning
from catalogue.models import Oeuvre, Prenom, Individu, Auteur, Profession, \
    GenreDOeuvre, TypeDeCaracteristiqueDOeuvre, \
    CaracteristiqueDOeuvre, Etat


TITRE_RE = re.compile(r'^(?P<titre>[^\(]+)\s+'
                      r'\((?P<particule>[^\)]+)\)$')
INDIVIDU_FULL_RE = re.compile(r'^(?P<nom>[^,]+),\s+'
                              r'(?P<prenoms>[^\(]+)\s+'
                              r'\((?P<dates>[^\)]+)\)$')
PARTICULES = ('de', 'd’', "d'", 'van', 'von')
PARTICULE_RE = re.compile(r'^(?P<prenoms>[^,]+)\s+(?P<particule>%s)$'
                          % '|'.join(PARTICULES), flags=re.IGNORECASE)
PSEUDONYME_RE = re.compile(r'^(?P<prenoms>[^,]+),?\s+'
                           r'dit(?P<feminin>e?)\s+(?P<pseudonyme>[^\)]+)$')


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
    if not match:
        return
    nom = title(match.group('nom'))
    prenom_str = match.group('prenoms')
    dates = match.group('dates')
    pseudonyme = ''
    particule = ''
    sexe = ''

    match_pseudonyme = PSEUDONYME_RE.match(prenom_str)
    if match_pseudonyme:
        prenom_str = match_pseudonyme.group('prenoms')
        pseudonyme = match_pseudonyme.group('pseudonyme')
        if match_pseudonyme.group('feminin'):
            sexe = 'F'

    match_particule = PARTICULE_RE.match(prenom_str)
    if match_particule:
        prenom_str = match_particule.group('prenoms')
        particule = match_particule.group('particule')
    elif prenom_str.lower() in PARTICULES:
        particule = prenom_str.lower()
        prenom_str = ''

    prenom_strs = [p for p in prenom_str.split() if p]
    prenoms = [get_or_create(Prenom,
                             {'prenom': prenom_str, 'classement': i},
                             unique_keys=('prenom', 'classement'))[0]
               for i, prenom_str in enumerate(prenom_strs)]

    naissance, deces = dates.split('-')
    try:
        return enlarged_get(Individu, {
            'nom': nom, 'pseudonyme': pseudonyme, 'particule_nom': particule,
            'prenoms': prenoms, 'titre': sexe})
    except Individu.DoesNotExist:
        pass

    # FIXME: Quand https://code.djangoproject.com/ticket/10811 sera résolu,
    # il faudra mettre un argument "commit=True" au deux lignes suivantes
    # et supprimer le try/except juste au dessus.
    ancrage_naissance = build_ancrage(naissance)
    ancrage_deces = build_ancrage(deces)

    individu = update_or_create(Individu, {
        'nom': nom, 'prenoms': prenoms,
        'pseudonyme': pseudonyme,
        'particule_nom': particule,
        'ancrage_naissance': ancrage_naissance,
        'ancrage_deces': ancrage_deces,
        'titre': sexe,
    }, unique_keys=['nom', 'prenoms__prenom'])
    return individu


Oeuvre_cti = ContentType.objects.get(app_label='catalogue', model='oeuvre')


def build_auteurs(individus_str, nom_profession,
                  nom_pluriel_profession=None):
    if nom_pluriel_profession is None:
        nom_pluriel_profession = nom_profession + 's'
    profession = get_or_create(
        Profession, {
            'nom': nom_profession, 'nom_pluriel': nom_pluriel_profession
        }, unique_keys=['nom'])[0]
    individus = []
    for individu_str in split_individus(individus_str):
        individu = build_individu(individu_str)
        if individu:
            individus.append(individu)
    auteurs = []
    for individu in individus:
        aut = Auteur(profession=profession, individu=individu)
        aut.clean()
        auteurs.append(aut)
    return auteurs


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
        if 'coordination' in bindings:
            coordination = oeuvre[bindings['coordination']]
        else:
            coordination = ', ou ' if titre2 else ''
        # TODO: Titres de la version originale à faire
        # Auteurs :
        auteurs = []
        for profession, profession_pluriel, auteurs_key in bindings['auteurs']:
            individus_str = oeuvre[auteurs_key]
            auteurs.extend(build_auteurs(individus_str, profession,
                                         profession_pluriel))
        # Genre :
        genre = GenreDOeuvre.objects.get_or_create(
            nom=oeuvre[bindings['genre']].strip())[0]
        # Caractéristiques :
        caracteristiques = []
        for type_nom, type_nom_pluriel, caracteristique_key \
                in bindings['caracteristiques']:
            type = update_or_create(TypeDeCaracteristiqueDOeuvre, {
                'nom': type_nom, 'nom_pluriel': type_nom_pluriel,
            }, unique_keys=['nom'])
            caracteristique = get_or_create(CaracteristiqueDOeuvre, {
                'type': type, 'valeur': oeuvre[caracteristique_key]})[0]
            caracteristiques.append(caracteristique)
        # Ancrage de création :
        ancrage_creation = None
        creation_str = oeuvre[bindings['creation'][0]]
        if creation_str:
            try:
                ancrage_creation = build_ancrage(
                    creation_str.split(bindings['creation'][1])[0])
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                print_warning('Impossible de parser la création de « %s »'
                              % titre)
        notes = oeuvre.get(bindings['notes'], '')
        # [Sauvegarde] :
        etat = Etat.objects.get_or_create(
            nom='importé automatiquement',
            nom_pluriel='importé(e)s automatiquement',
            message='<p>Les données ci-dessous ont été importées '
                    'automatiquement et sont en attente de relecture.',
            public=False)[0]
        oeuvre_obj = update_or_create(
            Oeuvre, {
                'prefixe_titre': particule, 'titre': titre,
                'coordination': coordination,
                'prefixe_titre_secondaire': particule2,
                'titre_secondaire': titre2,
                'genre': genre,
                'caracteristiques': caracteristiques,
                'auteurs': auteurs,
                'ancrage_creation': ancrage_creation,
                'notes': notes,
                'etat': etat,
            }, unique_keys=['titre', 'titre_secondaire', 'genre', 'auteurs'])
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
        oeuvre = {k.decode('utf-8'): v.decode('utf-8')
                  for k, v in oeuvre.items()}
        import_oeuvre(i, oeuvre, bindings)


def import_from_data_module(data_module):
    for csv_file in data_module.csv_files:
        import_csv_file(csv_file, data_module.bindings)


def run():
    translation.activate('fr')
    from .data import data_modules
    for data_module in data_modules:
        import_from_data_module(data_module)
