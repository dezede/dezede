"""Data import on 29/01/2024.

Sequel of Oeuvre import in dossier "Mélodies Françaises".
Imports Individu objects and links them to Oeuvres.
"""

import re
from traceback import print_exc
from typing import Tuple, Optional

import pandas as pd
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.html import linebreaks
from tqdm import tqdm

from accounts.models import HierarchicUser
from dossiers.models import DossierDOeuvres
from libretto.models import Oeuvre, Profession, Individu, Auteur, Etat


INITIAL_FILE_PATH = settings.BASE_DIR / 'scripts/data/mélodies_françaises_import_poètes.xlsx'


class Command(BaseCommand):
    help = (
        'Importe des données de la base de données Poulenc encore manquantes '
        'sur Dezède.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int)

    def handle(self, *args, **kwargs):
        limit = kwargs['limit']

        # ID Dossier "Mélodies françaises"
        self.oeuvres_dossier = list(
            DossierDOeuvres.objects.get(pk=646).oeuvres.values_list('pk', flat=True)
        )
        # ID propriétaire "François Le Roux"
        self.owner = HierarchicUser.objects.get(pk=945)
        # ID État "importé(e) automatiquement"
        self.etat = Etat.objects.get(pk=16)

        with transaction.atomic():
            oeuvres_a_modifier, autres_oeuvres = self.get_oeuvres_df(limit=limit)
            auteurs_df = self.get_auteurs_df(oeuvres_a_modifier)
            individus_df = self.import_individus(auteurs_df)
            auteurs_df = self.import_auteurs(auteurs_df, individus_df)
            all_oeuvres_df = pd.concat(
                [oeuvres_a_modifier, autres_oeuvres],
                sort=True,
            )
            self.to_excel(all_oeuvres_df, auteurs_df, individus_df)

    def get_oeuvres_df(
            self, limit: Optional[int] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df = pd.read_excel(
            INITIAL_FILE_PATH,
            dtype={
                'Oeuvre ID Dezède': int,
                'Poètes ID Dezède': str,
            }
        )
        if limit is not None:
            df = df.head(limit)

        df['oeuvre'] = df['Oeuvre ID Dezède'].map(self.get_oeuvre)

        to_be_modified = df['oeuvre'].notna() & df['Poètes'].notna()
        df['Poètes importés automatiquement'] = pd.Series(
            'oui', index=df.index).where(to_be_modified, other='non')
        other_df = df[~to_be_modified]
        return df[to_be_modified], other_df

    def get_oeuvre(self, pk: int):
        if pk not in self.oeuvres_dossier:
            return None
        try:
            oeuvre = Oeuvre.objects.get(pk=pk)
        except Oeuvre.DoesNotExist:
            self.stderr.write(
                f'Œuvre {pk=} n’existe pas dans Dezède.'
            )
            return None
        if oeuvre.owner_id != self.owner.id or oeuvre.etat_id != self.etat.id:
            self.stdout.write(
                f'Œuvre {pk=} ignorée car créée avant l’import des mélodies'
            )
            return None
        return oeuvre

    def get_auteurs_df(self, oeuvres_df: pd.DataFrame) -> pd.DataFrame:
        if oeuvres_df['Poètes'].hasnans:
            raise ValueError(
                'La colonne "Poètes" ne devrait pas comporter de valeur nan.'
            )
        if not (
            oeuvres_df['Poètes ID Dezède'].fillna('').str.count(';').equals(
                oeuvres_df['Poètes'].fillna('').str.count(';'))
        ):
            raise ValueError(
                'Les colonnes "Poètes ID Dezède" et "Poètes" devraient avoir le'
                'même nombre de ";" par cellule.'
            )

        profession_re = re.compile(
            r'^\s*(?:\[(?P<profession_str>\w+)\/?\w*\])?\s*(?P<individu_str>.*?)\s*$'
        )

        # Attention le chaînage est différent ici, c’est important.
        # Series.str.split renvoie None pour None, et [] pour ''
        # Ici on a besoin de [] pour explode
        oeuvres_df['poete_ID'] = (
            oeuvres_df['Poètes ID Dezède'].fillna('').str.replace(
                r'(?:\s+|-)', '', regex=True).str.split(';')
        )
        oeuvres_df['poete_str'] = (
            oeuvres_df['Poètes'].str.split(';')
        )
        df = oeuvres_df[[
            'oeuvre', 'poete_ID', 'poete_str', 'ID Poulenc',
        ]].explode(['poete_ID', 'poete_str'])

        df['poete_ID'] = pd.to_numeric(df['poete_ID'])

        if not df['poete_str'].str.fullmatch(profession_re).all():
            raise ValueError(
                'La colonne "poete_str" devrait suivre l’expression régulière '
                'profession_re.'
            )
        df[['profession_str', 'individu_str']] = (
            df['poete_str'].str.extract(profession_re)
        )
        df['profession_str'] = df['profession_str'].fillna('poète')
        if df['individu_str'].hasnans:
            raise ValueError(
                'La colonne "individu_str" ne devrait pas comporter de valeur nan.'
            )

        professions_dict = {}
        for s in df['profession_str'].unique():
            try:
                professions_dict[s] = Profession.objects.get(nom=s)
            except (Profession.DoesNotExist, Profession.MultipleObjectsReturned):
                self.stderr.write(
                    f'La profession "{s}" n’a pas été récupérée dans Dezède. '
                    'Les auteurs et individus concernés ne seront pas importés.'
                )
        df['profession'] = df['profession_str'].map(lambda s: professions_dict.get(s))
        df = df[df['profession'].notna()]

        return df

    def import_individus(self, df_auteurs: pd.DataFrame):
        individu_re = re.compile(
            r'^\s*(?P<nom_complet>[^(]+?)?\s*'
            '(?:\((?P<dates>[avJC\d\s\[\]\-?.]+)?\)'
            '\s*(?P<commentaire>.+)?)?\s*$'
        )
        particule_nom_re = re.compile(
            r'^\s*(?P<particule>des|de|d’|d\'|du|von|van|van der|van den|den|ten|da|di|do|del|de\sla|el)?'
            '\s*(?P<nom>[A-ZÂÊÎÔÛÁÉÍÓĆŃÀÈÒÙÄËÏÖÜŸÇÑØŁ’\s-]+)'
            '(?:\s+(?P<prenoms>[A-ZÂÊÎÔÛÁÉÍÓĆŃÀÈÒÙÄËÏÖÜŸÇÑØŁ\s-].*?))?\s*$'
        )

        df = df_auteurs[[
            'poete_ID', 'individu_str', 'ID Poulenc'
        ]].copy()

        a_creer = df['poete_ID'].isna()
        df['Importé automatiquement'] = pd.Series(
            'oui', index=df.index).where(a_creer, other='non')
        df_deja_crees = df[~a_creer].drop_duplicates('poete_ID')
        compositeur_dict = self.get_individu_dict(
            df_deja_crees['poete_ID'], context='compositeur'
        )
        df_deja_crees['individu'] = df_deja_crees['poete_ID'].map(
            lambda pk: compositeur_dict.get(pk)
        )
        df = df[a_creer].drop_duplicates(['individu_str'])

        if not df['individu_str'].str.fullmatch(individu_re).all():
            raise ValueError(
                'La colonne "individu_str" devrait suivre l’expression '
                'régulière individu_re.'
            )
        df[['nom_complet', 'dates', 'commentaire']] = (
            df['individu_str'].str.extract(individu_re)
        )

        naissance_deces_re = re.compile(
            r'^(?P<naissance_str>[^-]+)?-(?P<deces_str>[^-]+)?$'
        )
        if not df['dates'].str.fullmatch(naissance_deces_re, na=True).all():
            raise ValueError(
                '"dates" column devrait suivre l’expression régulière '
                'naissance_deces_re.'
            )
        df[['naissance_str', 'deces_str']] = (
            df['dates'].str.extract(naissance_deces_re)
        )
        self.format_ancrage_individu(df, 'naissance')
        self.format_ancrage_individu(df, 'deces')

        df[['particule_nom', 'nom', 'prenoms']] = (
            df['nom_complet'].str.extract(particule_nom_re)
        )
        no_particule = df['nom'].isna()
        df.loc[no_particule, 'nom'] = df.loc[no_particule, 'nom_complet']
        df['particule_nom'] = df['particule_nom'].fillna('')
        df['prenoms'] = df['prenoms'].fillna('')
        df['nom'] = df['nom'].str.capitalize()

        df['notes_privees'] = df['commentaire'].fillna('').map(
            lambda s: linebreaks(s) if s else ''
        )

        tqdm.pandas(desc='Import des individus')
        df['individu'] = df.progress_apply(self.create_individu, axis=1)
        df['poete_ID'] = df['individu'].map(lambda obj: '-' if obj is None else obj.pk)

        df = pd.concat([df, df_deja_crees]).sort_values('individu_str')

        duplicates_df = df[df.duplicated(subset=['individu_str'])]
        if not duplicates_df.empty:
            raise ValueError(
                f'Doublons trouvés pour ces individus: '
                f'{duplicates_df["individu_str"].to_list()}'
            )

        return df

    def format_ancrage_individu(self, df: pd.DataFrame, ancrage_name: str):
        annee_re = re.compile(r'^(?P<annee>\d{1,4})$')
        date_estimee_re = re.compile(r'^(?P<annee_approx>[\d?]+)\[(?P<annee>\d{1,4})\]$')
        date_tres_approx_re = re.compile(r'^(?P<annee_approx>\d[\d?]{0,2}\?)$')
        date_av_jc_re = re.compile(r'^(?P<date_approx>\d+\sav\.\sJ\.C\.)$')

        df['date_A'] = df[ancrage_name + '_str'].str.extract(annee_re)['annee'].str.zfill(4)
        df['date_B'] = df[ancrage_name + '_str'].str.extract(date_estimee_re)['annee'].str.zfill(4)
        df['date_C'] = df[ancrage_name + '_str'].str.extract(
            date_tres_approx_re
        )['annee_approx'].str.replace('?', '0', regex=False).str.zfill(4)
        df['date_D'] = df[ancrage_name + '_str'].str.fullmatch(
            date_av_jc_re, na=False
        ).map(lambda b: '0001' if b else None)

        df[ancrage_name + '_date'] = (
            df['date_D'].fillna(df['date_A']).fillna(df['date_B']).fillna(df['date_C'])
        )

        has_ancrage = df[ancrage_name + '_str'].notna()
        if not df[ancrage_name + '_date'].notna().equals(has_ancrage):
            raise ValueError(
                'Tous les ancrages spatio-temporels devraient suivre au moins'
                'une des expressions régulières proposées.'
            )

        df.loc[has_ancrage, ancrage_name + '_date'] = (
                df.loc[has_ancrage, ancrage_name + '_date'] + '-01-01'
        )
        df[ancrage_name + '_date'] = df[ancrage_name + '_date'].where(
            has_ancrage, other=None
        )
        df[ancrage_name + '_date_approx'] = df[ancrage_name + '_str'].fillna('')

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

    def create_individu(self, row):
        d = {s: row[s] for s in (
            'nom', 'prenoms', 'particule_nom', 'naissance_date', 'deces_date',
            'naissance_date_approx', 'deces_date_approx', 'notes_privees',
        )}
        d['owner'] = self.owner
        d['etat'] = self.etat
        individu = Individu(**d)
        try:
            individu.clean()
        except ValidationError:
            print_exc(file=self.stderr)
            self.stderr.write(
                f'Impossible de créer un individu avec ces données: {d}.'
            )
            return None
        else:
            individu.save()
            return individu

    def import_auteurs(
            self, df_auteurs: pd.DataFrame, df_individus: pd.DataFrame):
        # Merge those with the ID pre-filled.
        df_auteurs = df_auteurs.merge(
            df_individus[['poete_ID', 'individu']],
            how='left', on='poete_ID',
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

        df_auteurs['auteur'] = df_auteurs.apply(self.get_auteurs, axis=1)
        self.stdout.write('Création des auteurs en paquet…')
        has_auteur = df_auteurs['auteur'].notna()
        Auteur.objects.bulk_create(
            df_auteurs.loc[has_auteur, 'auteur'].to_list()
        )
        self.stdout.write('Fait.')
        return df_auteurs

    def get_auteurs(self, row):
        d = {s: row[s] for s in ('individu', 'oeuvre', 'profession')}
        auteur = Auteur(**d)
        try:
            auteur.clean()
        except ValidationError:
            print_exc(file=self.stderr)
            self.stderr.write(
                f'Impossible de créer un auteur avec ces données: {d}.'
            )
            return None
        return auteur

    def to_excel(self, df_oeuvres, df_auteurs, df_individus):
        self.stdout.write('Création d’un rapport Excel…')
        s_individus = df_auteurs[[
            'ID Poulenc', 'individu',
        ]].groupby('ID Poulenc')['individu'].apply(
            lambda series: ' ; '.join([str('-' if obj is None else obj.pk) for obj in series.to_list()])
        ).rename('Poètes ID Dezède')
        df_export = df_oeuvres.drop(['Poètes ID Dezède'], axis=1).merge(
            s_individus, on='ID Poulenc', how='left',
        )
        writer = pd.ExcelWriter(
            settings.BASE_DIR / 'scripts/data/mélodies_françaises_corrigées.xlsx',
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
                'Poètes importés automatiquement',
            ],
            index=False,
            sheet_name='Œuvres',
        )
        df_individus.to_excel(
            writer, index=False, sheet_name='Poètes',
            columns=[
                'poete_ID', 'individu_str', 'Importé automatiquement',
                'nom', 'prenoms', 'particule_nom', 'naissance_date', 'deces_date',
                'naissance_date_approx', 'deces_date_approx', 'notes_privees',
            ],
        )
        pd.read_excel(INITIAL_FILE_PATH, sheet_name=1).to_excel(
            writer, index=False, sheet_name='Compositeurs',
        )
        writer.close()
        self.stdout.write('Fait.')