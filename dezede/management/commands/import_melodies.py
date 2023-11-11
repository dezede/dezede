import re
from traceback import print_exc
from typing import Optional, Tuple

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction

import pandas
from django.utils.html import linebreaks
from psycopg2._range import NumericRange
from tqdm import tqdm

from accounts.models import HierarchicUser
from dossiers.models import DossierDOeuvres, CategorieDeDossiers
from libretto.models import Etat, Individu, Profession
from libretto.models.oeuvre import (
    Pitch, GenreDOeuvre, TypeDeParenteDOeuvres, Partie, Oeuvre, ParenteDOeuvres,
    Pupitre, Auteur,
)

OWNER = HierarchicUser.objects.get(first_name='François', last_name='Le Roux')

ETAT = Etat.objects.get(nom='importé(e) automatiquement')

GENRE_D_OEUVRE = GenreDOeuvre.objects.get(nom='mélodie')

TYPE_DE_PARENTE_D_OEUVRES = TypeDeParenteDOeuvres.objects.get(
    nom='poème mis en musique')

EFFECTIF_BASE = Partie.objects.get(nom='voix')

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

REPLACEABLE_ALTERATIONS = {
'A##': 'B', 'B##': 'C#', 'C##': 'D', 'D##': 'E', 'E##': 'F#', 'F##': 'G',
'G##': 'A', 'Abb': 'G', 'Bbb': 'A', 'Cbb': 'A#', 'Dbb': 'C', 'Ebb': 'D',
'Fbb': 'D#', 'Gbb': 'F', 'Ab': 'G#', 'Bb': 'A#', 'Cb': 'B', 'Db': 'C#',
'Eb': 'D#', 'Fb': 'E', 'Gb': 'F#', 'B#': 'C', 'E#': 'F',
}

NESTED_PARENTHESES_RE = re.compile(r'^[^(]*\([^)]*\(.*$')

DATE_ISO_RE = re.compile(r'^(?P<date>\d{4}-\d{2}-\d{2})$')
DATE_YEAR_MONTH_RE = re.compile(r'^(?P<date>\d{4}-\d{2})$')
DATE_YEAR_RE = re.compile(r'^(?P<year>\d{4})$')
DATE_PARTIAL_YEAR_RE = re.compile(r'^[\d?]{4}\[(?P<year>\d{4})\]$')
DATE_YEAR_INTERVAL_RE = re.compile(r'^(?P<year>\d{4})-\d{4}$')

PROFESSION_RE = re.compile(
    r'^\s*(?:\[(?P<profession_str>\w+)\/?\w*\])?\s*(?P<individu_str>.*?)\s*$'
)

INDIVIDU_RE = re.compile(
    r'^\s*(?P<nom_complet>[\w\s’\'-\.]+?)?\s*'
    '(?:\((?P<dates>[\d\[\]?-]+)?\)'
    '\s*(?P<commentaire>.+)?)?\s*$'
)

PARTICULE_NOM_RE = re.compile(
    r'^\s*(?P<particule>des|de|d’|d\'|von|van|van der|van den|den|da|di|do|del|de\sla)?'
    '\s*(?P<nom>[A-ZÂÊÎÔÛÁÉÍÓĆŃÀÈÒÙÄËÏÖÜŸÇÑØŁ’*\s-]+?)'
    '(?:\s+(?P<prenoms>[A-ZÂÊÎÔÛÁÉÍÓĆŃÀÈÒÙÄËÏÖÜŸÇÑØŁ\s-].*?))?\s*$'
)


def html(comment, s):
    return linebreaks(f'{comment}: {s}') if s else ''


def get_ID_list_series(series):
    return series.str.replace(r'\s+', '', regex=True).str.split(';')


def replace_parentheses_with_quotes(s):
    if NESTED_PARENTHESES_RE.match(s):
        l = s.partition('(')
        out = ''.join([l[0], '« ', l[2]])
        l = out.rpartition(')')
        out = ''.join([l[0], ' »', l[2]])
        return out
    out = s.replace('(', '« ', 1)
    out = out.replace(')', ' »', 1)
    return out


def get_missing_parties_str(s, parties_list):
    parties_manquantes = ', '.join([partie for partie in parties_list if partie in s])
    return html('Parties manquantes dans Dezède', parties_manquantes)


def create_oeuvre(row):
    d = {s: row[s] for s in (
        'prefixe_titre', 'titre', 'incipit', 'opus', 'ambitus',
        'creation_date', 'creation_date_approx', 'notes_privees',
    )}
    d['genre'] = GENRE_D_OEUVRE
    d['owner'] = OWNER
    d['etat'] = ETAT
    oeuvre = Oeuvre(**d)
    oeuvre.clean()
    oeuvre.save()
    return oeuvre


def update_oeuvre_notes(row):
    oeuvre =  row['oeuvre']
    oeuvre.notes_privees = row['notes_privees']
    oeuvre.save()


def get_parente_d_oeuvres(row):
    d = {
        'mere': row['oeuvre_mere'], 'fille': row['oeuvre'],
        'type': TYPE_DE_PARENTE_D_OEUVRES,
    }
    parente = ParenteDOeuvres(**d)
    parente.clean()
    return parente


def get_pupitre(row):
    pupitre = Pupitre(
        partie=row['partie'], oeuvre=row['oeuvre'],
        quantite_min=row['effectif'], quantite_max=row['effectif'],
    )
    pupitre.clean()
    return pupitre


def create_auteurs(row):
    d = {s: row[s] for s in ('individu', 'oeuvre', 'profession')}
    auteur = Auteur(**d)
    auteur.clean()
    return auteur


def group_compositeur_IDs(ids):
    ids = ids[pandas.notnull(ids)]
    return ", ".join(ids.to_list())


def format_ambitus(df: pandas.DataFrame):
    ambitus_re = re.compile(
        r'^\s*(?P<min_note>[A-G]#?)(?P<min_octave>-?\d+)-'
        '(?P<max_note>[A-G]#?)(?P<max_octave>-?\d+)\s*$'
    )
    get_pitch = lambda note, octave: Pitch.form_to_database_value(NOTES.index(note), int(octave))

    df['ambitus_str'] = df['Ambitus'].copy()
    for k, v in REPLACEABLE_ALTERATIONS.items():
        df['ambitus_str'] = df['ambitus_str'].str.replace(k, v)
    assert df['ambitus_str'].str.fullmatch(ambitus_re, na=True).all()
    has_ambitus = df['ambitus_str'].notnull()


    df[['min_note', 'min_octave', 'max_note', 'max_octave']] = (
        df['ambitus_str'].str.extract(ambitus_re)
    )
    df[['min_pitch', 'max_pitch', 'ambitus']] = None
    df.loc[has_ambitus, 'min_pitch'] = df.loc[has_ambitus].apply(
        lambda row: get_pitch(row['min_note'], row['min_octave']),
        axis=1,
    )
    df.loc[has_ambitus, 'max_pitch'] = df.loc[has_ambitus].apply(
        lambda row: get_pitch(row['max_note'], row['max_octave']),
        axis=1,
    )
    assert df.loc[has_ambitus, 'min_pitch'].le(df.loc[has_ambitus, 'max_pitch']).all()
    df.loc[has_ambitus, 'ambitus'] = (
        df[has_ambitus].apply(
            lambda row: NumericRange(
                row['min_pitch'], row['max_pitch'], bounds='[]'),
            axis=1,
        )
    )


def format_titre(df: pandas.DataFrame):
    # Bidouille pour compenser un mauvais choix de formatage
    df['oeuvre_titre'] = df['Oeuvre titre'].map(replace_parentheses_with_quotes)
    titre_re = re.compile(
        r'^\s*(?P<titre_avec_prefixe>[^«]+?)?\s*'
        '(?:«\s*(?P<incipit>[^»]+?)\s*»\s*(?P<notes_titre>.+)?)?\s*$'
    )

    prefixe_et_titre_re = re.compile(
        r'^(?:(?P<prefixe_titre>le\s|la\s|les\s|un\s|une\s|der\s|die\s'
        '|das\s|ein\s|l’|l\'|the\s|li\s|lou\s|el\s|los\s|lo\s)\s*)?'
        '(?P<titre>.*?)\s*$'
    )

    assert df['oeuvre_titre'].str.fullmatch(titre_re, na=False).all()
    df[['titre_avec_prefixe', 'incipit', 'notes_titre']] = (
        df['oeuvre_titre'].str.extract(titre_re)
    )
    df[['prefixe_titre', 'titre']] = (
        df['titre_avec_prefixe'].str.extract(prefixe_et_titre_re)
    )
    df[['prefixe_titre', 'titre', 'incipit']] = (
        df[['prefixe_titre', 'titre', 'incipit']].fillna('')
    )
    df['prefixe_titre'] = df['prefixe_titre'].str.strip()

    # Tronque les incipits trop grands
    has_long_incipit = df['incipit'].str.len() >= 100
    if has_long_incipit.sum():
        df.loc[has_long_incipit, 'incipit'] = (
            df.loc[has_long_incipit, 'incipit'].str.split(',', n=1, expand=True)[0]
        )


def format_creation_date_and_lieu(df: pandas.DataFrame):
    creation_re = re.compile(
        r'\s*(?P<creation_date_str>[\[\]\d?-]+)?\s*'
        '(?:\((?P<creation_lieu_str>[\w\s’-]+)\))?\s*'
    )
    assert df['Date composition'].str.fullmatch(creation_re, na=True).all()
    df[['creation_date_str', 'creation_lieu_str']] = (
        df['Date composition'].str.extract(creation_re)
    )
    df['date_A'] = df['creation_date_str'].str.extract(DATE_ISO_RE)['date']
    df['date_B'] = df['creation_date_str'].str.extract(DATE_YEAR_MONTH_RE)['date'] + '-01'
    df['date_C'] = df['creation_date_str'].str.extract(DATE_YEAR_RE)['year'] + '-01-01'
    df['date_D'] = df['creation_date_str'].str.extract(DATE_PARTIAL_YEAR_RE)['year'] + '-01-01'
    df['date_E'] = df['creation_date_str'].str.extract(DATE_YEAR_INTERVAL_RE)['year'] + '-01-01'

    df['creation_date'] = df['date_A'].fillna(df['date_B']).fillna(
        df['date_C']).fillna(df['date_D']).fillna(df['date_E'])
    df['creation_date'] = df['creation_date'].where(
        df['creation_date'].notnull(), other=None,
    )
    assert df['creation_date'].notnull().equals(df['creation_date_str'].notnull())
    df['creation_date_approx'] = df['creation_date_str'].fillna('')
    # NB: on n’ajoute pas de lieu de création,
    # car on ne peut pas savoir de quel lieu il s’agit juste d’après le nom.
    # Il y a plusieurs cas de lieux homonymes.


def format_notes(df: pandas.DataFrame):
    # NB: Les dédicaces sont ajoutées dans les notes privées, même si une autorité
    # est ajoutée en tant que dédicataire. Dans 1 cas, il y a plusieurs
    # dédicataires, dont au moins un qui n’est pas une autorité.
    df['dedicace_str'] = df['Dédicace'].where(
        df['Dédicataire ID Dezède'].str.contains('-', na=True),
        other='',
    )

    # Préformate pour les parentés d’œuvres
    assert (~df['Poésie ID Dezède'].str.contains('-', na=False)).all()
    assert (~df['Recueil poétique ID Dezède'].str.contains('-', na=False)).all()

    poesie_not_in_db = df['Poésie ID Dezède'].isnull()
    recueil_not_in_db = df['Recueil poétique ID Dezède'].isnull()
    df['notes_poesie'] = df['Poésie titre'].where(poesie_not_in_db, other='')
    df['poetes_str'] = df['Poètes'].where(poesie_not_in_db, other='')
    df['notes_poetes'] = df['Poètes commentaires'].where(
        poesie_not_in_db, other='',
    )
    df['date_poesie'] = df['Date poésie'].where(poesie_not_in_db, other='')
    df['notes_recueil_poetique'] = df['Recueil poétique'].where(
        poesie_not_in_db & recueil_not_in_db, other=''
    )

    df['notes_compositeurs'] = df['Compositeurs commentaires']
    df['tonalite'] = df['Tonalité']
    df['duree'] = df['Durée']
    df['commentaire'] = df['Commentaire']
    df['enregistrements'] = df['Enregistrements']

    notes_list = [
        'notes_titre', 'notes_compositeurs',
        'creation_lieu_str', 'dedicace_str', 'tonalite', 'duree',
        'notes_poesie', 'poetes_str', 'notes_poetes', 'date_poesie',
        'notes_recueil_poetique',
        'commentaire', 'enregistrements',
    ]

    df[notes_list] = df[notes_list].fillna('')

    df['notes_titre'] = df['notes_titre'].map(
        lambda s: html('Notes générales', s)
    )
    df['notes_compositeurs'] = df['notes_compositeurs'].map(
        lambda s: html('Notes sur les auteurs (musique)', s)
    )
    df['creation_lieu_str'] = df['creation_lieu_str'].map(lambda s: html('Composé à', s))
    df['dedicace_str'] = df['dedicace_str'].map(lambda s: html('Dédicace', s))
    df['tonalite'] = df['tonalite'].map(lambda s: html('Tonalité', s))
    df['duree'] = df['duree'].map(lambda s: html('Durée', s))

    df['notes_poesie'] = df['notes_poesie'].map(lambda s: html('Notes sur la poésie', s))
    df['poetes_str'] = df['poetes_str'].map(lambda s: html('Auteur(s) (texte)', s))
    df['notes_poetes'] = df['notes_poetes'].map(
        lambda s: html('Notes sur les auteurs (texte)', s)
    )
    df['date_poesie'] = df['date_poesie'].map(
        lambda s: html('Date de composition du texte', s)
    )
    df['notes_recueil_poetique'] = df['notes_recueil_poetique'].map(
        lambda s: html('Notes sur le recueil poétique', s)
    )

    df['commentaire'] = df['commentaire'].map(
        lambda s: html('Notes détaillées', s)
    )
    df['enregistrements'] = df['enregistrements'].map(
        lambda s: html('Notes sur les enregistrements', s)
    )
    df['notes_privees'] = df[notes_list].sum(axis=1)


def format_ancrage_individu(df: pandas.DataFrame, ancrage_name: str):
    date_estimee_re = re.compile(r'^(?P<annee_approx>[\d?]{4})\[(?P<annee>\d{4})\]$')
    date_tres_approx_re = re.compile(r'^(?P<annee_approx>\d[\d?]{3})\??$')

    df['date_A'] = df[ancrage_name+'_str'].str.extract(DATE_YEAR_RE)
    df['date_B'] = df[ancrage_name+'_str'].str.extract(date_estimee_re)['annee']
    df['date_C'] = df[ancrage_name+'_str'].str.extract(
        date_tres_approx_re
    )['annee_approx'].str.replace('?', '0', regex=False)

    df[ancrage_name+'_date'] = (
        df['date_A'].fillna(df['date_B']).fillna(df['date_C'])
    )

    has_ancrage = df[ancrage_name+'_str'].notnull()
    assert df[ancrage_name+'_date'].notnull().equals(has_ancrage)

    df.loc[has_ancrage, ancrage_name + '_date'] = (
        df.loc[has_ancrage, ancrage_name + '_date'] + '-01-01'
    )
    df[ancrage_name+'_date'] = df[ancrage_name+'_date'].where(
        has_ancrage, other=None
    )
    df[ancrage_name+'_date_approx'] = df[ancrage_name+'_str'].fillna('')



class Command(BaseCommand):
    help = 'Imports data from Poulenc database.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int)

    def get_oeuvre(self, pk):
        try:
            return Oeuvre.objects.get(pk=pk)
        except Oeuvre.DoesNotExist:
            self.stderr.write(
                f'L’œuvre de pk {pk} n’existe pas dans Dezède.'
            )

    def import_oeuvres(
        self, limit: Optional[int] = None,
    ) -> Tuple[pandas.DataFrame, pandas.DataFrame]:
        ### Dataframe d’oeuvres
        df = pandas.read_excel(
            settings.BASE_DIR / 'scripts/data/mélodies_françaises_pour_importation.xlsx',
            dtype={
                'Oeuvre ID Dezède': float,
                'Date composition': str,
                'Date poésie': str,
                'Compositeurs ID Dezède': str,
                'Poètes ID Dezède': str,
                'Dédicataire ID Dezède': str,
                'Poésie ID Dezède': str,
                'Recueil poétique ID Dezède': str,
            }
        )
        df['oeuvre'] = None

        # Sépare le tableau en deux (les œuvres déjà dans Dezède et les autres)
        a_creer = df['Oeuvre ID Dezède'].isnull()

        df_deja_crees = df[~a_creer].copy()
        df_deja_crees['oeuvre'] = df_deja_crees['Oeuvre ID Dezède'].map(
            lambda pk: self.get_oeuvre(pk)
        )
        disparus = df_deja_crees['oeuvre'].isnull()
        df_deja_crees.loc[disparus, 'erreurs'] = (
            df_deja_crees.loc[disparus, 'Oeuvre ID Dezède'].map(
                lambda s: f'L’œuvre de pk {s} n’est pas dans Dezède.'
            )
        )
        df_deja_crees['est_importe'] = False
        imperfect_input_ids = df_deja_crees[
            df_deja_crees["Oeuvre ID Dezède"].duplicated()
        ]["Oeuvre ID Dezède"].unique()
        if imperfect_input_ids:
            self.stderr.write(
                f'Imperfect Œuvre IDs found for multiple Œuvres '
                f'instead of one: {imperfect_input_ids}'
            )

        df = df[a_creer].copy()
        if limit is not None:
            df = df.head(limit)

        # Supprime les '"' parasites (probablement dûs à un mauvais formatage LibreOffice)
        for s in (
            'Compositeurs', 'Compositeurs commentaires', 'Compositeurs ID Dezède',
            'Poètes', 'Poètes commentaires', 'Poètes ID Dezède',
            'Oeuvre titre', 'Date composition', 'Tonalité', 'Ambitus', 'Effectif', 'Dédicace',
            'Poésie titre', 'Recueil poétique', 'Date poésie', 'Durée', 'Opus', 'Commentaire',
            'Enregistrements',
        ):
            df[s] = df[s].str.strip('"')

        format_titre(df)
        format_ambitus(df)
        format_creation_date_and_lieu(df)
        format_notes(df)

        df['opus'] = df['Opus'].fillna('')
        assert df['opus'].str.fullmatch(r'^(\d+(/\d+)?)?$').all()

        tqdm.pandas(desc='Import des œuvres')
        df['oeuvre'] = df.progress_apply(create_oeuvre, axis=1)
        df['Oeuvre ID Dezède'] = df['oeuvre'].map(lambda obj: obj.pk)
        return df, df_deja_crees

    def import_parentes(self, df_oeuvres: pandas.DataFrame):
        df_oeuvres['oeuvre_mere'] = get_ID_list_series(
            df_oeuvres['Poésie ID Dezède'].fillna(df_oeuvres['Recueil poétique ID Dezède'])
        )

        has_oeuvre_mere = df_oeuvres['oeuvre_mere'].notnull()
        if (~has_oeuvre_mere).all():
            self.stdout.write('Pas d’œuvre parente à importer.')
            return
        df = df_oeuvres.loc[has_oeuvre_mere, ['oeuvre_mere', 'oeuvre']].explode(
            ['oeuvre_mere'])
        df = df[~df['oeuvre_mere'].str.contains('-')]
        df['oeuvre_mere'] = pandas.to_numeric(df['oeuvre_mere'])
        df['oeuvre_mere'] = df['oeuvre_mere'].map(
            lambda n: Oeuvre.objects.get(pk=n)
        )
        df['parente'] = df.apply(get_parente_d_oeuvres, axis=1)

        self.stdout.write('Creating parentés d’œuvres in bulk…')
        ParenteDOeuvres.objects.bulk_create(df['parente'].to_list())
        self.stdout.write('Done.')

    def get_individu_dict(self, pk_series, context='dédicataire'):
        d = {}
        for pk in pk_series.unique():
            try:
                d[pk] = Individu.objects.get(pk=pk)
            except Individu.DoesNotExist:
                self.stderr.write(
                    f'L’individu {context} de pk {pk} n’existe pas dans Dezède.'
                )
        return d

    def import_dedicaces(self, df_oeuvres):
        df_oeuvres['dedicataire_ID'] = get_ID_list_series(
            df_oeuvres['Dédicataire ID Dezède']
        )
        has_dedicace = df_oeuvres['dedicataire_ID'].notnull()
        if (~has_dedicace).all():
            self.stdout.write('Pas de dédicace à importer.')
            return
        df = (
            df_oeuvres.loc[has_dedicace, ['dedicataire_ID', 'oeuvre']].explode(
                ['dedicataire_ID'])
        )
        # Retire les dédicataires qui ne sont pas des autorités
        df = df[~df['dedicataire_ID'].str.contains('-')]
        dedicataire_dict = self.get_individu_dict(df['dedicataire_ID'])
        df['dedicataire'] = df['dedicataire_ID'].map(
            lambda pk: dedicataire_dict.get(pk)
        )
        df = df[df['dedicataire'].notnull()]
        self.stdout.write('Creating dedicaces…')
        df.apply(
            lambda row: row['oeuvre'].dedicataires.add(row['dedicataire']),
            axis=1,
        )
        self.stdout.write('Done.')

    def get_partie_dict(self, series):
        d = {}
        for nom in series.unique():
            try:
                d[nom] = Partie.objects.get(nom=nom)
            except Partie.DoesNotExist:
                self.stderr.write(
                    f'La partie "{nom}" n’existe pas dans Dezède.'
                )
        return d

    def import_pupitres(self, df_oeuvres):
        # voix et piano sont l’effectif par défaut, inutile de le mentionner.
        df_oeuvres['pupitre_str'] = (
            df_oeuvres['Effectif'].str.replace(
                "'", '’', regex=False,
            ).str.replace(
                'flute', 'flûte', regex=False,
            ).str.replace(
                r';\s*piano\s*;', ';', regex=True,
            ).str.replace(
                r'(:^\s*piano\s*;|;\s*piano\s*$|^\s*piano\s*$)', '', regex=True,
            )
        )
        df_oeuvres['pupitre_str'] = df_oeuvres['pupitre_str'].where(
            df_oeuvres['pupitre_str'] != '', other=None,
        ).str.split(';')

        has_pupitre = df_oeuvres['pupitre_str'].notnull()
        if (~has_pupitre).all():
            self.stdout.write('Pas de pupitre à importer.')
            return

        df = df_oeuvres.loc[has_pupitre, ['oeuvre', 'pupitre_str']].explode(
            ['pupitre_str'])
        pupitre_re = re.compile(
            r'\s*(?P<instrument>[\w’\s-]+)\s*(?P<effectif>\(\d+\))?\s*'
        )
        assert df['pupitre_str'].str.fullmatch(pupitre_re).all()
        df[['instrument', 'effectif']] = df['pupitre_str'].str.extract(pupitre_re)

        df['effectif'] = pandas.to_numeric(
            df['effectif'].fillna('1').str.strip('()')
        )
        df['instrument'] = df['instrument'].str.strip()
        assert df['instrument'].notnull().all()

        partie_dict = self.get_partie_dict(df['instrument'])
        df['partie'] = df['instrument'].map(partie_dict)

        missing_parties = [s for s in df['instrument'].unique()
                           if s not in partie_dict]
        df_oeuvres['parties_manquantes'] = (
            df_oeuvres['Effectif'].fillna('').map(
                lambda s: get_missing_parties_str(s, missing_parties)
            )
        )
        df_oeuvres['notes_privees'] = (
            df_oeuvres['parties_manquantes'].str.cat(df_oeuvres['notes_privees'])
        )
        df_oeuvres[df_oeuvres['parties_manquantes'] != ''].apply(
            update_oeuvre_notes, axis=1
        )

        df = df[df['partie'].notnull()]
        df['pupitre'] = df.apply(get_pupitre, axis=1)
        self.stdout.write('Creating Pupitres in bulk…')
        Pupitre.objects.bulk_create(df['pupitre'].to_list())
        self.stdout.write('Done.')

    def get_auteurs_df(self, oeuvres_df: pandas.DataFrame):
        assert oeuvres_df['Compositeurs'].notnull().all()
        assert(
            oeuvres_df['Compositeurs ID Dezède'].fillna('').str.count(';').equals(
            oeuvres_df['Compositeurs'].fillna('').str.count(';'))
        )

        # Attention le chaînage est différent ici, c’est important.
        # Series.str.split renvoie None pour None, et [] pour ''
        # Ici on a besoin de [] pour explode
        oeuvres_df['compositeur_ID'] = (
            oeuvres_df['Compositeurs ID Dezède'].fillna('').str.replace(
                r'(?:\s+|-)', '', regex=True).str.split(';')
        )
        oeuvres_df['compositeur_str'] = (
            oeuvres_df['Compositeurs'].str.split(';')
        )
        df = oeuvres_df[[
            'oeuvre', 'compositeur_ID', 'compositeur_str', 'ID Poulenc',
        ]].explode(['compositeur_ID', 'compositeur_str'])

        df['compositeur_ID'] = pandas.to_numeric(df['compositeur_ID'])

        assert df['compositeur_str'].str.fullmatch(PROFESSION_RE).all()
        df[['profession_str', 'individu_str']] = (
            df['compositeur_str'].str.extract(PROFESSION_RE)
        )
        df['profession_str'] = df['profession_str'].fillna('compositeur')
        assert df['individu_str'].notnull().all()

        professions_dict = {
            s: Profession.objects.get(nom=s)
            for s in df['profession_str'].unique()
        }
        df['profession'] = df['profession_str'].map(lambda s: professions_dict[s])

        return df

    def create_individu(self, row):
        d = {s: row[s] for s in (
            'nom', 'prenoms', 'particule_nom', 'naissance_date', 'deces_date',
            'naissance_date_approx', 'deces_date_approx', 'notes_privees',
        )}
        d['owner'] = OWNER
        d['etat'] = ETAT
        individu = Individu(**d)
        try:
            individu.clean()
        except ValidationError:
            print_exc(file=self.stderr)
            self.stderr.write(
                f'Unable to create an individu with these data: {d}'
            )
        individu.save()
        return individu

    def import_individus(self, df_auteurs: pandas.DataFrame):
        df = df_auteurs[[
            'compositeur_ID', 'individu_str', 'ID Poulenc'
        ]]

        a_creer = df['compositeur_ID'].isnull()
        df_deja_crees = df[~a_creer].drop_duplicates('compositeur_ID')
        compositeur_dict = self.get_individu_dict(
            df_deja_crees['compositeur_ID'], context='compositeur'
        )
        df_deja_crees['individu'] = df_deja_crees['compositeur_ID'].map(
            lambda pk: compositeur_dict.get(pk)
        )
        df = df[a_creer].drop_duplicates(['individu_str'])

        assert df['individu_str'].str.fullmatch(INDIVIDU_RE).all()
        df[['nom_complet', 'dates', 'commentaire']] = (
            df['individu_str'].str.extract(INDIVIDU_RE)
        )

        naissance_deces_re = re.compile(
            r'^(?P<naissance_str>[^-]+)?-(?P<deces_str>[^-]+)?$'
        )
        assert df['dates'].str.fullmatch(naissance_deces_re, na=True).all()
        df[['naissance_str', 'deces_str']] = (
            df['dates'].str.extract(naissance_deces_re)
        )
        format_ancrage_individu(df, 'naissance')
        format_ancrage_individu(df, 'deces')

        df[['particule_nom', 'nom', 'prenoms']] = (
            df['nom_complet'].str.extract(PARTICULE_NOM_RE)
        )
        no_particule = df['nom'].isnull()
        df.loc[no_particule, 'nom'] = df.loc[no_particule, 'nom_complet']
        df['particule_nom'] = df['particule_nom'].fillna('')
        df['prenoms'] = df['prenoms'].fillna('')
        df['nom'] = df['nom'].str.capitalize()

        df['notes_privees'] = df['commentaire'].fillna('').map(
            lambda s: linebreaks(s) if s else ''
        )

        tqdm.pandas(desc='Import des individus')
        df['individu'] = df.progress_apply(self.create_individu, axis=1)
        df['compositeur_ID'] = df['individu'].map(lambda obj: obj.pk)

        df = pandas.concat([df, df_deja_crees]).sort_values('individu_str')
        return df

    def import_auteurs(
            self, df_auteurs: pandas.DataFrame, df_individus: pandas.DataFrame):
        # Merge those with the ID pre-filled.
        df_auteurs = df_auteurs.merge(
            df_individus[['compositeur_ID', 'individu']],
            how='left', on='compositeur_ID',
        )
        # Add those created in a new column (plus imperfect match for pre-filled
        # IDs, but we will not use this imperfect match thanks
        # to fillna downstream).
        df_auteurs = df_auteurs.merge(
            df_individus[['individu_str', 'individu']].rename(columns={
                'individu': 'individu_cree',
            }),
            how='left', on='individu_str',
        )

        # Use `individu` from the pre-filled ID when available, and by default
        # use the created individu.
        df_auteurs['individu'] = df_auteurs['individu'].fillna(
            df_auteurs['individu_cree'],
        )
        df_auteurs.drop(columns=['individu_cree'], inplace=True)

        if df_auteurs['individu'].hasnans:
            raise ValueError('Unexpected NaNs in the `individu` column.')

        df_auteurs['auteur'] = df_auteurs.apply(create_auteurs, axis=1)
        self.stdout.write('Creating auteurs in bulk…')
        Auteur.objects.bulk_create(df_auteurs['auteur'].to_list())
        self.stdout.write('Done.')
        return df_auteurs

    def import_dossier(self, df_oeuvres: pandas.DataFrame):
        self.stdout.write('Creating dossier…')
        dossier = DossierDOeuvres(
            categorie=CategorieDeDossiers.objects.get(nom='Archives du spectacle'),
            owner=OWNER, etat=ETAT, titre='Mélodies françaises',
            presentation='<p>Lorem ipsum</p>',
            slug='melodies-francaises',
        )
        dossier.clean()
        dossier.save()
        editeur_scientifique = HierarchicUser.objects.get(
            first_name='Lucia', last_name='Pasini',
        )
        dossier.editeurs_scientifiques.add(editeur_scientifique)
        dossier.oeuvres.set(
            df_oeuvres.loc[df_oeuvres['oeuvre'].notnull(), 'oeuvre'].to_list()
        )
        self.stdout.write('Done.')

    def to_excel(self, df_oeuvres, df_auteurs, df_individus):
        s_individus = df_auteurs[[
            'ID Poulenc', 'individu',
        ]].groupby('ID Poulenc')['individu'].apply(
            lambda series: ' ; '.join([str(obj.pk) for obj in series.to_list()])
        ).rename('Compositeurs ID Dezède')
        df_export = df_oeuvres.drop(['Compositeurs ID Dezède']).merge(
            s_individus, on='ID Poulenc', how='left',
        )
        writer = pandas.ExcelWriter(
            settings.BASE_DIR / 'scripts/data/mélodies_françaises_importées.xlsx',
            engine='xlsxwriter',
        )
        df_export.to_excel(
            writer,
            columns=[
                'ID Poulenc', 'Compositeurs', 'Compositeurs commentaires',
                'Compositeurs ID Dezède', 'Poètes', 'Poètes commentaires',
                'Poètes ID Dezède', 'Oeuvre titre', 'Oeuvre ID Dezède',
                'Date composition', 'Tonalité', 'Ambitus', 'Effectif', 'Dédicace',
                'Dédicataire ID Dezède', 'Poésie titre', 'Poésie ID Dezède',
                'Recueil poétique', 'Recueil poétique ID Dezède', 'Date poésie',
                'Durée', 'Opus', 'Commentaire', 'Enregistrements',
            ],
            index=False,
            sheet_name='Œuvres',
        )
        df_individus.to_excel(
            writer, index=False, sheet_name='Individus',
            columns=['compositeur_ID', 'individu_str'],
        )
        writer.close()

    def handle(self, *args, **kwargs):
        limit = kwargs['limit']

        with Oeuvre.disabled_tree_trigger():
            with transaction.atomic():
                oeuvres_df, oeuvres_dezede_df = self.import_oeuvres(limit=limit)
                self.import_pupitres(oeuvres_df)
                self.import_dedicaces(oeuvres_df)
                self.import_parentes(oeuvres_df)
                auteurs_df = self.get_auteurs_df(oeuvres_df)
                individus_df = self.import_individus(auteurs_df)
                auteurs_df = self.import_auteurs(auteurs_df, individus_df)
                all_oeuvres_df = pandas.concat(
                    [oeuvres_df, oeuvres_dezede_df],
                    sort=True,
                )
                self.import_dossier(all_oeuvres_df)
                self.to_excel(all_oeuvres_df, auteurs_df, individus_df)

        self.stdout.write('Rebuilding Œuvre paths…')
        Oeuvre.rebuild_paths()
        self.stdout.write('Done.')
