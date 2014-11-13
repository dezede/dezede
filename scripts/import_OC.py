# coding: utf-8

from __future__ import unicode_literals
import os
import re
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.core.files import File
from django.db.backends import BaseDatabaseWrapper
from django.db.backends.util import CursorWrapper
from django.utils.html import linebreaks
import pandas as pd
from tqdm import tqdm
from accounts.models import HierarchicUser

from libretto.api.models.utils import update_or_create, SetDefaultEtat, \
    SetDefaultOwner
from libretto.api.models.espace_temps import parse_ancrage
from libretto.api.models.individu import get_individus, get_individu
from libretto.models import (
    Oeuvre, GenreDOeuvre, TypeDeCaracteristiqueDOeuvre, CaracteristiqueDOeuvre,
    Auteur, Profession, Source, SourceOeuvre, SourceIndividu, Fichier,
    TypeDeSource, Etat)
from libretto.models.functions import str_list


ID = 'Id Dezède'
TITRE = 'Titre'
GENRE = 'Genre'
COMPOSITEURS = 'Compositeur(s)'
LIBRETTISTES = 'Librettiste(s)'
CREATION_DATE = 'Date de création'
CREATION_LIEU = 'Lieu de création'
CREATION_OC_DATE = 'Date de première représentation à l’OC'
CREATION_OC_LIEU = 'Lieu de première représentation à l’OC'
TITRE_ALTERNATIF = 'Titre alternatif'
REF_BIBLIO = 'Réf. bibliogr.'

TYPE = 'Type de document'
TITRE_SOURCE = 'Nom de la source'
NUMERO = 'numéro de la source'
DATE = 'Date du document'
LEGENDE = 'Légende'
CONSERVATION = 'Lieu de conservation'
COTE = 'Cote'
NOTES_PUBLIQUES = 'Notes publiques'
NOTES_PRIVEES = 'Notes privées'
IMAGE0 = 'Première image'
IMAGE1 = 'Dernière image'

ARTISTE = 'Artiste'

OEUVRE = 'œuvre'


les_pat = r'(L\'|L’|L’|La |Le |Les )?'
TITRE_RE = re.compile(r'^%s(.+?)(?:(, ou )%s(.+))?$' % (les_pat, les_pat.lower()))
GENRE_RE = re.compile(r'^(.+?)(?: (en (?:un|une|deux|trois|quatre|cinq|six|sept) .+))?$')
IMAGE_RE = re.compile(r'FRAN_(0140|0141)_(\d{5})')
JPG_FOLDER = '/home/bertrand/Dropbox/OC_compressed/'


def create_oeuvre_notes(row):
    notes = ''
    if row[TITRE_ALTERNATIF]:
        notes += '<p>Titre alternatif : %s</p>' % row[TITRE_ALTERNATIF]
    creation_oc = str_list((row[CREATION_OC_LIEU], row[CREATION_OC_DATE]))
    if creation_oc:
        notes += '<p>Première représentation à l’Opéra-Comique : %s</p>' % creation_oc
    if row[REF_BIBLIO]:
        notes += '<p>Référence bibliographique : %s</p>' % row[REF_BIBLIO]
    if notes:
        for oeuvre in row[OEUVRE]:
            oeuvre.notes_publiques += notes
            oeuvre.save()
    return row


def get_oeuvres(row):
    compositeur = Profession.objects.get(nom='compositeur')
    librettiste = Profession.objects.get(nom='librettiste')

    if row[ID]:
        row[OEUVRE] = list(Oeuvre.objects.filter(pk__in=[pk.strip() for pk in row[ID].split(';')]))
    elif row[TITRE]:
        data = dict(zip(('prefixe_titre', 'titre', 'coordination',
                         'prefixe_titre_secondaire', 'titre_secondaire'),
                        ['' if v is None else v for v in TITRE_RE.match(row[TITRE]).groups()]))
        if row[GENRE]:
            genre, decoupage = GENRE_RE.match(row[GENRE]).groups()
            data['genre'] = GenreDOeuvre.objects.get_or_create(nom=genre)[0]
            if decoupage:
                type_decoupage = TypeDeCaracteristiqueDOeuvre.objects.get(nom='découpage')
                c = CaracteristiqueDOeuvre.objects.filter(type=type_decoupage, valeur=decoupage).first()
                if c is None:
                    c = CaracteristiqueDOeuvre.objects.create(type=type_decoupage, valeur=decoupage)
                data['caracteristiques'] = [c]
        auteurs = [Auteur(individu=i, profession=compositeur)
                   for i in get_individus(row[COMPOSITEURS])]
        auteurs += [Auteur(individu=i, profession=librettiste)
                    for i in get_individus(row[LIBRETTISTES])]
        data['auteurs'] = auteurs
        ancrage_data = parse_ancrage(str_list((row[CREATION_LIEU], row[CREATION_DATE])), commit=True)
        for k, v in ancrage_data.items():
            ancrage_data['creation_' + k] = v
            del ancrage_data[k]
        data.update(ancrage_data)
        for k, v in data.items():
            if v is None:
                del data[k]
        row[OEUVRE] = [update_or_create(
            Oeuvre, data,
            unique_keys=('prefixe_titre', 'titre', 'coordination',
                         'prefixe_titre_secondaire', 'titre_secondaire',
                         'auteurs'))]
    else:
        row[OEUVRE] = []
    create_oeuvre_notes(row)
    return row


def get_artistes(individus_str):
    if not individus_str.strip():
        return []
    individus = []
    for individu_str in individus_str.split(';'):
        parts = individu_str.split(':')
        individu = get_individu(parts[0])
        if len(parts) == 2:
            individu.professions.add(update_or_create(Profession, {'nom': parts[1].strip()}))
        individus.append(individu)
    return individus


etat = Etat.objects.get_or_create(nom='importé automatiquement (public)',
                                  public=True)[0]


@SetDefaultOwner(HierarchicUser.objects.get(last_name='Opéra-Comique'))
@SetDefaultEtat(etat)
def run():
    if settings.DEBUG:
        BaseDatabaseWrapper.make_debug_cursor = lambda self, cursor: CursorWrapper(cursor, self)
    cache.clear()

    df = pd.read_excel('/home/bertrand/Téléchargements/ARCH_OC.xls').fillna('')
    for col in df.columns:
        for _, row in df.iterrows():
            if isinstance(row[col], datetime):
                row[col] = row[col].date()
        df[col] = df[col].astype(unicode).str.strip()
    df[DATE] = df[DATE].str.replace('sans date', '').str.replace('s.d.', '')

    df = df.apply(get_oeuvres, axis=1)
    df[ARTISTE] = df[ARTISTE].apply(get_artistes)

    for _, row in tqdm(df.iterrows(), total=len(df)):
        type = TypeDeSource.objects.get_or_create(nom=row[TYPE])[0]
        data = dict(type=type, titre=row[TITRE_SOURCE], numero=row[NUMERO],
                    legende=row[LEGENDE],
                    lieu_conservation=row[CONSERVATION], cote=row[COTE])
        if row[NOTES_PUBLIQUES]:
            data['notes_publiques'] = linebreaks(row[NOTES_PUBLIQUES])
        if row[NOTES_PRIVEES]:
            data['notes_privees'] = linebreaks(row[NOTES_PRIVEES])
        if row[TYPE] in ('livret', 'procès-verbal de censure') and not row[TITRE_SOURCE]:
            data['titre'] = row[TITRE]
        if row[DATE]:
            data.update(parse_ancrage(row[DATE]))
        source = Source.objects.create(**data)
        if row[OEUVRE]:
            SourceOeuvre.objects.bulk_create(
                [SourceOeuvre(source=source, oeuvre=oeuvre)
                 for oeuvre in row[OEUVRE]])
        if row[ARTISTE]:
            SourceIndividu.objects.bulk_create(
                [SourceIndividu(source=source, individu=individu)
                 for individu in row[ARTISTE]])

        match = IMAGE_RE.match(row[IMAGE0])
        fonds0, n0 = match.group(1, 2)
        match = IMAGE_RE.match(row[IMAGE1])
        fonds1, n1 = match.group(1, 2)
        n0, n1 = int(n0), int(n1)
        assert fonds0 == fonds1 and n0 <= n1
        for i, j in enumerate(range(n0, n1 + 1)):
            filename = 'FRAN_%s_%05d.jpg' % (fonds0, j)
            with open(os.path.join(JPG_FOLDER, filename)) as f:
                fichier = Fichier(source=source, fichier=File(f), position=i)
                fichier.save()
