# coding: utf-8

from __future__ import unicode_literals, division
from datetime import datetime, time
from django.db import transaction
import pandas
from afo.models import EvenementAFO


DATE = 'Date de la représentation'
HEURE = 'Heure'
ORCHESTRE = 'Orchestre'
JAUGE = 'Jauge'

# à ajouter
TITRE_PROGRAMME = 'Titre du programme 1)'
TYPE_PROGRAMME = 'Typologie artistique du programme'
CODE_TOURNEE = 'Code ou titre de la tournée'
NOMENCLATURE = "Nomenclature d'exécution"
PERMANENTS = 'Nb de musiciens permanents convoqués (dont remplaçants)'
SUPPLEMENTAIRES = 'Nb de musiciens supplémentaires convoqués'
FESTIVAL = 'Nom du Festival'
MODALITE_PRODUCTION = 'Modalité de production'
TYPE_SALLE = 'Type de lieu'
PRESENTATION_SPECIFIQUE = 'Si présentation spécifique (concert commenté, participatif), précisez'
PUBLIC_SPECIFIQUE = 'Si représentation / concert conçu exclusivement pour public spécifique, préciser le type de public.'

ATTRS = {
    TITRE_PROGRAMME: 'titre_programme', TYPE_PROGRAMME: 'type_de_programme',
    CODE_TOURNEE: 'tournee', NOMENCLATURE: 'nomenclature',
    PERMANENTS: 'permanents', SUPPLEMENTAIRES: 'supplementaires',
    FESTIVAL: 'festival', MODALITE_PRODUCTION: 'modalite_production',
    TYPE_SALLE: 'type_salle', PRESENTATION_SPECIFIQUE: 'presentation_specifique',
    PUBLIC_SPECIFIQUE: 'public_specifique',
}

DEFAULT_VALUES = {
    DATE: '', HEURE: None, TITRE_PROGRAMME: '', CODE_TOURNEE: '',
    NOMENCLATURE: '', PERMANENTS: None, SUPPLEMENTAIRES: None, FESTIVAL: '',
}

BINDINGS = {
    TYPE_SALLE: {
        'Autres salles (Hors les murs, etc)': 'A',
        'Salles de spectacle pluridisciplinaires (théatre de ville, Centres culturels, etc.)': 'P',
        'Salles dédiées à la musique (Auditorium, opéra, etc.)': 'M',
    },
    TYPE_PROGRAMME: {
        'Symphonique (dont chœur/récital)': 'S',
        'Musique de chambre': 'MC',
        'Lyrique version concert': 'LC',
        'Lyrique version scénique': 'LS',
        'Chorégraphique': 'C',
        'Autre (ciné concerts, cross over, etc)': 'A',
    },
    MODALITE_PRODUCTION:  {
        'Contrat de cession': 'Ce', 'A': 'Autoproduction',
        'Contrat de coproduction': 'CP', 'Contrat de co-réalisation': 'CR',
        'Participation aux frais': 'P',
    },
    PRESENTATION_SPECIFIQUE: {
        'Concert commenté/présenté': 'C', 'Concert participatif': 'P',
        'Autre (précisez)': 'A',
    },
    PUBLIC_SPECIFIQUE: {
        'Public jeune en temps scolaire': 'JS',
        'Public jeune hors temps scolaire': 'JV',
        'Publics empêchés (santé, handicap, justice)': 'E',
        'Public de proximité': 'P', 'Public empêché': 'E',
        'Public senior': 'S', 'Jeune public': 'J',
    },
}

ORCHESTRES = {
    'Orchestre Poitou-Charentes': 200,
    "Orchestre d'Auvergne": 245,
    'Orchestre de Chambre de Toulouse': 208,
    'Orchestre de Paris': 206,
    'Orchestre de Picardie': 197,
    'Orchestre de chambre de Paris': 202,
    "Orchestre de l'Opéra de Rouen Haute-Normandie": 207,
    'Orchestre national de Lorraine': 203,
    'Orchestre national des Pays de la Loire': 199,
    'Orchestre symphonique et lyrique de Nancy': 204,
    'Orchestre National de Montpellier Languedoc Roussillon': 198,
    "Orchestre national d'Île-de-France": 196,
    'Orchestre Régional de Basse-Normandie': 201,
}


def add_afo_data(row):
    pk = row['id_dezede']
    if pandas.isnull(pk):
        return
    e = EvenementAFO.objects.get_or_create(evenement_id=pk)[0]
    for s in ATTRS:
        setattr(e, ATTRS[s],
                BINDINGS[s].get(row[s], '')
                if s in BINDINGS else row[s])
    e.save()


def run(*args):

    import_date = \
        lambda obj: obj.date().isoformat() if isinstance(obj, datetime) else obj
    # Transforme les valeurs aberrantes en 0:00
    import_heure = lambda obj: time(0, 0) if isinstance(obj, datetime) else obj
    df = pandas.read_excel(args[0],
                           converters={DATE: import_date, HEURE: import_heure})
    # Retire les concerts annulés
    df.drop(list(df[df[JAUGE] == 'concert annulé'].index), inplace=True)
    # Supprime une faute de frappe (espace en trop à la fin), retire les 'NC'
    df.replace(to_replace=['NC', "Orchestre national d'Île-de-France "],
               value=[None, "Orchestre national d'Île-de-France"],
               inplace=True)

    for k, v in DEFAULT_VALUES.items():
        df[k] = df[k].where((pandas.notnull(df[k])), v)

    with transaction.atomic():
        df.apply(add_afo_data, axis=1)
        raise Exception
