# coding: utf-8

from __future__ import unicode_literals, print_function
import re

from django.core.cache import cache
from django.conf import settings
from django.core.files import File
from django.db import transaction
from django.db.backends import BaseDatabaseWrapper
from django.db.backends.util import CursorWrapper

from localflavor.fr.fr_department import DEPARTMENT_CHOICES_PER_REGION
from localflavor.fr.fr_region import REGION_CHOICES
import pandas as pd

from accounts.models import HierarchicUser
from libretto.models import *
from libretto.api.models.utils import update_or_create, SetDefaultEtat, \
    SetDefaultOwner


# commun aux deux feuilles
ORCHESTRE = 'Orchestres'

# feuille événements
DATE = 'date'
PROGRAMME = 'programme'
SOURCE = 'N° enregistrement'
DISTRIBUTION = 'interprètes'
SALLE = 'salle'
VILLE = 'Ville'
CODE_POSTAL = 'CP'
PAYS = 'Pays'
SOURCE_PK = 'N° enregistrement'

# feuille sources
N_SUPPORT = 'n°original'
N_PLAGE = "Numéro d'œuvre"
EVENEMENT = 'Événement'
TITRE = 'Titre œuvre'
NOM_FICHIER = 'Nom de fichier'
REMARQUE = 'Remarques'
EVENEMENT_INDEX = 'Événement'

# créés (communs aux deux feuilles)
EVENEMENT_OBJ = 'evenement'
ORCHESTRE_OBJ = 'orchestre'
SOURCE_OBJ = 'source'
SOURCE_INDEXES = 'source_indexes'


ORCHESTRE_USERS = {
    'Orchestre français des jeunes': 'ofj',
    'Orchestre Dijon Bourgogne': 'odb',
    'Orchestre régional de Basse-Normandie': 'orbn',
    "Orchestre d'Auvergne": 'oa',
}


def get_departement_dict():
    regions = dict(REGION_CHOICES)
    return {t[0]: (t[1], regions.get(t[2])) for t in DEPARTMENT_CHOICES_PER_REGION}

DEPARTMENTS = get_departement_dict()


def path(root_path, filename, ext):
    directory, _ = filename.split('_')
    return '/'.join([root_path, directory[:2], directory, filename + '.' + ext])


def replacements(s):
    s = unicode(s)
    for (old, new) in ((r'\s+', ' '), ("'", '’')):
        re.sub(old, new, s)
    return s

to_zip_code = lambda s: str(s).zfill(5) if s else str(s)


def to_int(s):
    return int(s) if s else 0


def create_source_id_column(row):
    return unicode(row[N_SUPPORT]) + '.' + unicode(row[N_PLAGE])


def proper_noun_case(string):
    separators = (' ', '-', '’')

    def inner(s, sep_tuple):
        return sep_tuple[0].join(inner(sub_s.capitalize(), sep_tuple[1:])
                                 for sub_s in s.split(sep_tuple[0])) \
            if sep_tuple else s
    return inner(string, separators)


def parse_person_name(prenoms, nom):
    prenoms, nom = map(proper_noun_case, (prenoms, nom))
    particule = ''
    for s in ('Van ', 'Van Der ', 'De '):
        if nom.startswith(s):
            particule = s.lower()
            nom = nom[len(s):]
    return [s.strip() for s in (prenoms, particule, nom)]


def build_users():
    for k, v in ORCHESTRE_USERS.items():
        ORCHESTRE_USERS[k] = HierarchicUser.objects.get_or_create(username=v, defaults={'last_name': k})[0]


def build_orchestre(row):
    s = row[ORCHESTRE]
    return Ensemble.objects.get_or_create(nom=s, owner=ORCHESTRE_USERS[s])[0]


def build_lieu(row):
    with SetDefaultOwner(ORCHESTRE_USERS[row[ORCHESTRE]]):
        if pd.notnull(row[PAYS]):
            country = Lieu.objects.get(nom=row[PAYS], nature=NatureDeLieu.objects.get(nom='pays'))
            if pd.notnull(row[CODE_POSTAL]):
                departement_code = row[CODE_POSTAL][:2]
                departement_name, region_name = DEPARTMENTS[departement_code]
                region = Lieu.objects.get_or_create(
                    nom=region_name, parent=country, nature=NatureDeLieu.objects.get(nom='région'))[0]
                if departement_code == '75':
                    town_parent = region
                    zip_code = '75000'
                else:
                    town_parent = Lieu.objects.get_or_create(
                        nom=departement_name, parent=region,
                        nature=NatureDeLieu.objects.get(nom='département'))[0]
                    zip_code = row[CODE_POSTAL]
                data = {'nom': row[VILLE], 'parent': town_parent, 'code_postal': zip_code,
                        'nature': NatureDeLieu.objects.get(nom='ville')}
                town = update_or_create(Lieu, data, unique_keys=('nom', 'parent', 'nature'))
                if pd.notnull(row[SALLE]):
                    data = {'nom': row[SALLE], 'parent': town, 'code_postal': row[CODE_POSTAL],
                            'nature': NatureDeLieu.objects.get(nom='salle')}
                    return update_or_create(Lieu, data, unique_keys=('nom', 'parent'))

                return town
            return Lieu.objects.get_or_create(
                nom=row[SALLE], parent=Lieu.objects.get(nom=row[VILLE]),
                nature=NatureDeLieu.objects.get(nom='salle'))[0]
        return None


def build_individus_ensembles_parties(row):
    with SetDefaultOwner(ORCHESTRE_USERS[row[ORCHESTRE]]):
        if pd.notnull(row[DISTRIBUTION]):
            l = []
            for line in row[DISTRIBUTION].split('\n'):
                parts = [s.strip() for s in line.split(';')]
                d = dict()
                if len(parts) == 3:
                    model = Individu
                    d['prenoms'], d['particule_nom'], d['nom'] = parse_person_name(*parts[:2])
                elif len(parts) == 2:
                    model = Ensemble
                    d['nom'] = parts[0]
                else:
                    raise Exception('colonne interprètes mal formatée.', line)
                interprete = update_or_create(model, d)
                s = parts[-1].lower()
                if s.startswith('Rôle de '):
                    s = s[len('Rôle de '):]
                    model = Role
                else:
                    model = Instrument
                partie = model.objects.get_or_create(nom=s)[0]
                l.append((interprete, partie))
            row[DISTRIBUTION] = l
    return row


def build_oeuvre_individus_auteurs(row):

    p = Profession.objects.get(nom='compositeur')

    with SetDefaultOwner(ORCHESTRE_USERS[row[ORCHESTRE]]):
        l = []
        for line in row[PROGRAMME].split('\n'):
            t = line.split(';')
            if len(t) == 3:
                if all(s.strip() for s in t):
                    d = {}
                    d['prenoms'], d['particule_nom'], d['nom'] = parse_person_name(*t[1:])
                    i = Individu.objects.get_or_create(**d)[0]
                    try:
                        o = Oeuvre.objects.get(
                            titre=t[0], auteurs__individu=i, auteurs__profession=p)
                    except Oeuvre.DoesNotExist, Oeuvre.MultipleObjectsReturned:
                        o = Oeuvre.objects.create(titre=t[0])
                        o.auteurs.add(Auteur.objects.create(
                            content_object=o, individu=i, profession=p))
                    l.append(o)
                else:
                    l.append(' '.join(line.split(';')).strip())
            else:
                raise Exception(line, 'Non parsable')
        row[PROGRAMME] = l
        return row


def build_evenement(row):
    return Evenement.objects.create(debut_date=row[DATE].date(), debut_lieu=row['lieu'],
                                    owner=ORCHESTRE_USERS[row[ORCHESTRE]])


def build_source(row, root_path):
    with SetDefaultOwner(ORCHESTRE_USERS[row[ORCHESTRE]]):
        source = Source.objects.create(
            titre=row[TITRE], type=TypeDeSource.objects.get_or_create(nom='Enregistrement')[0])
        for pos, ext in enumerate(('mp4', 'ogg')):
            with open(path(root_path, row[NOM_FICHIER], ext)) as f:
                Fichier.objects.create(source=source, position=pos, fichier=File(f))
        return source


def create_element_de_distribution(row):
    e = ElementDeDistribution.objects.create(content_object=row[EVENEMENT_OBJ])
    e.ensembles.add(row[ORCHESTRE_OBJ])
    if isinstance(row[DISTRIBUTION], list):
        for t in row[DISTRIBUTION]:
            e = ElementDeDistribution.objects.create(
                content_object=row[EVENEMENT_OBJ], pupitre=Pupitre.objects.create(partie=t[1])
            )
            if isinstance(t[0], Ensemble):
                e.ensembles.add(t[0])
            else:
                e.individus.add(t[0])
    return row


def create_element_de_programme(row):
    for pos, item in enumerate(row[PROGRAMME]):
        d = dict()
        if isinstance(item, unicode):
            d['autre'] = item
        else:
            d['oeuvre'] = item
        d.update({'numerotation': 'U', 'position': pos, 'evenement': row[EVENEMENT_OBJ]})
        ElementDeProgramme.objects.create(**d)
    return row


def create_source_evenement_link(row, series):
    if row[EVENEMENT_INDEX] > 0:
        SourceEvenement.objects.get_or_create(
            source=row[SOURCE_OBJ], evenement=series[row[EVENEMENT_INDEX]])
        row[SOURCE_OBJ].date = series[row[EVENEMENT_INDEX]].debut_date
        row[SOURCE_OBJ].save()
    return row


def index_from_source_pk(row, series):
    def f(s):
        return None if s == '0.0' else series[series == s].index[0]
    l = []
    for prog in row[SOURCE_PK].split(', '):
        recs = prog.split(' – ')
        l.append(f(recs[0]) if len(recs) == 1 else [f(rec) for rec in recs])
    row[SOURCE_INDEXES] = l
    return row


def create_source_oeuvre_link(row, series):

    def inner(item, oeuvre):
        if isinstance(item, list):
            for sub_item in item:
                inner(sub_item, oeuvre)
                return
        if item:
            source = series[item]
            if isinstance(oeuvre, Oeuvre):
                SourceOeuvre.objects.create(source=source, oeuvre=oeuvre)
            source.save()
        return

    for pos, obj in enumerate(row[SOURCE_INDEXES]):
        inner(obj, row[PROGRAMME][pos])
    return row


etat = Etat.objects.get_or_create(nom='importé(e) automatiquement')[0]


@transaction.atomic
@SetDefaultEtat(etat)
def run(root_path):

    cache.clear()
    root_path = root_path.rstrip('/')

    if settings.DEBUG:
        BaseDatabaseWrapper.make_debug_cursor = lambda self, cursor: CursorWrapper(cursor, self)

    # Importation du fichier dans des DataFrame
    xls = pd.ExcelFile(root_path + '/Campagne num° 2012-13.xlsx')
    converters = {SALLE: replacements, VILLE: replacements, CODE_POSTAL: to_zip_code,
                  PROGRAMME: replacements, DISTRIBUTION: replacements}
    event_df = xls.parse(0, index_col=0, converters=converters)
    record_df = xls.parse(1, converters={s: to_int for s in
                                         (EVENEMENT, N_SUPPORT, N_PLAGE)})

    record_df.drop(['Support', 'Durée œuvre', 'Durée extrait', 'Format pivot', 'Format compressé', 'ordre'], axis=1, inplace=True)
    excl_msg = "Ne pas importer dans Dezède ; ces morceaux sont interprétés par d'autres artistes invités des folles journées"
    record_df = record_df[record_df[NOM_FICHIER].notnull() & (record_df[REMARQUE] != excl_msg)]
    record_df[SOURCE_PK] = record_df.apply(create_source_id_column, axis=1)
    record_df.drop([N_SUPPORT, N_PLAGE], axis=1, inplace=True)

    build_users()
    print('Users créés.')

    event_df[ORCHESTRE_OBJ] = event_df.apply(build_orchestre, axis=1)
    print('Ensembles créés (orchestres).')

    event_df['lieu'] = event_df.apply(build_lieu, axis=1)
    event_df.drop([SALLE, VILLE, CODE_POSTAL, PAYS], axis=1, inplace=True)
    print('Lieux créés.')

    event_df[EVENEMENT_OBJ] = event_df.apply(build_evenement, axis=1)
    event_df.drop('lieu', axis=1, inplace=True)
    print('Evenements créés.')

    record_df[SOURCE_OBJ] = record_df.apply(build_source, axis=1, args=(root_path,))
    record_df.drop([REMARQUE, NOM_FICHIER], axis=1, inplace=True)
    print('Sources créés.')

    record_df.apply(create_source_evenement_link, axis=1, args=(event_df[EVENEMENT_OBJ],))
    print('SourceEvenement créés.')

    event_df = event_df.apply(build_oeuvre_individus_auteurs, axis=1)
    event_df.apply(create_element_de_programme, axis=1)
    print('Oeuvres, Individus, Auteurs créés, ElementsDeProgramme créés.')

    event_df = event_df.apply(build_individus_ensembles_parties, axis=1)
    event_df.apply(create_element_de_distribution, axis=1)
    print('Individus, Ensembles, Parties, ElementsDeDistribution créés.')

    event_df = event_df.apply(index_from_source_pk, axis=1, args=(record_df[SOURCE_PK],))
    print()
    event_df = event_df.apply(create_source_oeuvre_link, axis=1, args=(record_df[SOURCE_OBJ],))
    print('SourceOeuvre créés.')