"""
Génère un jeu de données d’exemple crédible et interconnecté pour le
développement et les démonstrations.

Contrairement aux imports spécialisés (``import_melodies``, ``import_poetes``),
cette commande ne dépend d’aucun fichier externe : elle fabrique de toutes
pièces des lieux, individus, ensembles, œuvres, événements et sources reliés
entre eux, en respectant l’ordre de dépendance des modèles de ``libretto``.

Exemples ::

    ./manage.py generate_sample_data
    ./manage.py generate_sample_data --scale 0.2 --seed 1 --flush

Le signal d’indexation (``libretto.signals.update_related_search_items``) est
débranché pendant la génération pour éviter de noyer la file RQ ; pensez à
lancer ``./manage.py update_index`` ensuite pour rendre la recherche cohérente.
"""

from contextlib import contextmanager
from datetime import date
import random

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.signals import post_save
from django.utils.lorem_ipsum import paragraphs
from tqdm import tqdm

from libretto.models import (
    NatureDeLieu, Lieu, Individu, Profession, TypeDEnsemble, Ensemble, Membre,
    GenreDOeuvre, Oeuvre, Partie, Pupitre, Auteur,
    Evenement, ElementDeProgramme, ElementDeDistribution,
    TypeDeCaracteristiqueDeProgramme, CaracteristiqueDeProgramme,
    TypeDeSource, Source,
)
from libretto.signals import update_related_search_items


# ---------------------------------------------------------------------------
# Vocabulaires et banques de mots (français / musicologie)
# ---------------------------------------------------------------------------

NATURES_DE_LIEU = [
    # (nom, referent)
    ('pays', False),
    ('région', False),
    ('ville', True),
    ('théâtre', False),
    ('salle de concert', False),
    ('opéra', False),
    ('conservatoire', False),
    ('église', False),
    ('château', False),
]

GENRES = [
    # (nom, referent)
    ('opéra', True),
    ('opéra-comique', True),
    ('ballet', True),
    ('oratorio', False),
    ('symphonie', False),
    ('concerto', False),
    ('sonate', False),
    ('quatuor à cordes', False),
    ('mélodie', False),
    ('messe', False),
    ('cantate', False),
    ('poème symphonique', False),
    ('ouverture', False),
    ('suite', False),
    ('nocturne', False),
    ('étude', False),
    ('prélude', False),
    ('valse', False),
]

NUMBERED_GENRES = {
    'symphonie', 'concerto', 'sonate', 'quatuor à cordes', 'nocturne',
    'étude', 'prélude', 'valse', 'suite', 'ouverture',
}

# (nom, nom_feminin) — laisser nom_feminin vide si identique.
PROFESSIONS_CREATEURS = [
    ('compositeur', 'compositrice'),
    ('librettiste', ''),
    ('parolier', 'parolière'),
    ('arrangeur', 'arrangeuse'),
]
PROFESSIONS_INTERPRETES = [
    ('chef d’orchestre', 'cheffe d’orchestre'),
    ('pianiste', ''),
    ('violoniste', ''),
    ('violoncelliste', ''),
    ('organiste', ''),
    ('flûtiste', ''),
    ('ténor', ''),
    ('soprano', ''),
    ('baryton', ''),
    ('basse', ''),
    ('mezzo-soprano', ''),
    ('danseur', 'danseuse'),
    ('metteur en scène', 'metteuse en scène'),
]

TYPES_ENSEMBLE = [
    'orchestre', 'orchestre symphonique', 'chœur', 'ensemble vocal',
    'quatuor', 'troupe',
]

TYPES_SOURCE = [
    'partition', 'programme', 'compte rendu', 'lettre', 'affiche',
    'article de presse', 'livret', 'photographie',
]

INSTRUMENTS = [
    'violon', 'alto', 'violoncelle', 'contrebasse', 'flûte', 'hautbois',
    'clarinette', 'basson', 'cor', 'trompette', 'piano', 'harpe', 'orgue',
    'timbales',
]

ROLE_NAMES = [
    'Le Comte', 'La Comtesse', 'Figaro', 'Suzanne', 'Don Juan', 'Leporello',
    'Carmen', 'Don José', 'Faust', 'Marguerite', 'Méphistophélès', 'Le Roi',
    'La Reine', 'Le Prince', 'Orphée', 'Eurydice', 'Le Page', 'La Nourrice',
    'Le Soldat', 'Le Prêtre', 'La Sorcière', 'Le Poète',
]

# Géographie : pays -> villes (noms uniques au sein du pays).
PAYS_ET_VILLES = {
    'France': [
        'Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Rouen', 'Lille', 'Nantes',
        'Strasbourg', 'Toulouse', 'Versailles', 'Nice', 'Dijon',
    ],
    'Allemagne': ['Berlin', 'Munich', 'Dresde', 'Leipzig', 'Hambourg', 'Cologne'],
    'Italie': ['Milan', 'Venise', 'Rome', 'Naples', 'Florence', 'Turin'],
    'Autriche': ['Vienne', 'Salzbourg', 'Graz'],
    'Royaume-Uni': ['Londres', 'Édimbourg', 'Manchester'],
    'Russie': ['Saint-Pétersbourg', 'Moscou'],
}

PRENOMS_MASC = [
    'Antoine', 'Charles', 'Édouard', 'François', 'Georges', 'Henri', 'Jacques',
    'Jean', 'Louis', 'Marcel', 'Paul', 'Pierre', 'Camille', 'Gabriel',
    'Hector', 'Maurice', 'Théodore', 'Vincent', 'Auguste', 'Émile', 'Gustave',
    'Léon', 'Albert', 'Daniel', 'Étienne',
]
PRENOMS_FEM = [
    'Adèle', 'Amélie', 'Berthe', 'Camille', 'Cécile', 'Clara', 'Élise',
    'Eugénie', 'Geneviève', 'Hortense', 'Jeanne', 'Joséphine', 'Louise',
    'Marguerite', 'Marie', 'Pauline', 'Rose', 'Sophie', 'Thérèse', 'Yvonne',
    'Blanche', 'Henriette', 'Madeleine',
]
NOMS = [
    'Berlioz', 'Bizet', 'Charpentier', 'Debussy', 'Delacroix', 'Dubois',
    'Dupont', 'Durand', 'Fauré', 'Gounod', 'Lalande', 'Lefebvre', 'Leroy',
    'Martin', 'Massenet', 'Moreau', 'Nicolas', 'Petit', 'Rameau', 'Renard',
    'Rousseau', 'Roussel', 'Saint-Saëns', 'Simon', 'Vincent', 'Bernard',
    'Girard', 'Lemoine', 'Caron', 'Faure', 'Mercier', 'Boulanger', 'Chausson',
    'Lully', 'Couperin', 'Halévy', 'Adam', 'Thomas', 'Lalo', 'Chabrier',
]
PARTICULES = ['', '', '', '', '', 'de ', "d’", 'von ', 'van ', 'de la ']

# Banques pour les titres « significatifs » (opéras, ballets, etc.).
TITRE_NOMS = [
    'amants', 'larmes', 'roi', 'reine', 'nuit', 'rêve', 'fantôme', 'prophète',
    'barbier', 'noces', 'enlèvement', 'damnation', 'vêpres', 'pèlerin',
    'corsaire', 'troyens', 'huguenots', 'contes', 'saisons', 'élixir',
    'sortilège', 'captif', 'prince', 'sorcière', 'tempête', 'orage',
    'printemps', 'serment', 'voyageur', 'cloches',
]
TITRE_QUALIFS = [
    'de Venise', 'de Séville', 'du destin', 'perdu', 'enchanté', 'd’amour',
    'oublié', 'de minuit', 'des forêts', 'de Naples', 'fantastique',
    'éternel', 'd’automne', 'maudit', 'du Nord', 'sans retour',
]

TONALITE_GAMMES = ['C', 'A']          # majeur / mineur
TONALITE_NOTES = list('cdefgab')
TONALITE_ALTERATIONS = ['-', '0', '+']

CIRCONSTANCES = [
    '', '', 'Première', 'Concert d’abonnement', 'Soirée de gala',
    'Représentation de bienfaisance', 'Festival', 'Reprise',
    'Concert spirituel',
]

DECOUPAGES = ['en un acte', 'en deux actes', 'en trois actes',
              'en quatre actes', 'en cinq actes']

# Volumétrie de base (échelle « medium »), multipliée par --scale.
BASE_COUNTS = {
    'individus': 1000,
    'ensembles': 60,
    'oeuvres': 800,
    'evenements': 1500,
    'sources': 300,
}

OWNER_USERNAME = 'sample_data'


@contextmanager
def search_indexing_disabled():
    """Débranche le signal d’indexation pendant la génération en masse."""
    post_save.disconnect(update_related_search_items)
    try:
        yield
    finally:
        post_save.connect(update_related_search_items)


class Command(BaseCommand):
    help = ('Remplit la base avec un jeu de données d’exemple crédible '
            '(lieux, individus, œuvres, événements, sources).')

    def add_arguments(self, parser):
        parser.add_argument(
            '--scale', type=float, default=1.0,
            help='Multiplie les volumes de base (défaut : 1.0 ≈ medium).')
        parser.add_argument(
            '--seed', type=int, default=None,
            help='Graine aléatoire pour un jeu de données reproductible.')
        parser.add_argument(
            '--flush', action='store_true',
            help='Supprime d’abord les données générées par une exécution '
                 'précédente (limitées au propriétaire « %s »).'
                 % OWNER_USERNAME)

    # -- Helpers ----------------------------------------------------------

    def n(self, key):
        return max(1, int(BASE_COUNTS[key] * self.scale))

    def random_date(self, start_year, end_year):
        start = date(start_year, 1, 1).toordinal()
        end = date(end_year, 12, 31).toordinal()
        return date.fromordinal(random.randint(start, end))

    def vocab(self, model, nom, **extra):
        return model.objects.get_or_create(nom=nom, defaults=extra)[0]

    # -- Étapes -----------------------------------------------------------

    def create_owner(self):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=OWNER_USERNAME,
            defaults={'email': 'sample-data@example.com',
                      'first_name': 'Données', 'last_name': 'd’exemple'})
        if created:
            user.set_password(OWNER_USERNAME)
            user.save()
        return user

    def create_vocabularies(self):
        self.natures = {nom: self.vocab(NatureDeLieu, nom, referent=referent)
                        for nom, referent in NATURES_DE_LIEU}
        self.genres = {nom: self.vocab(GenreDOeuvre, nom, referent=referent)
                       for nom, referent in GENRES}
        self.types_ensemble = [self.vocab(TypeDEnsemble, nom)
                               for nom in TYPES_ENSEMBLE]
        self.types_source = [self.vocab(TypeDeSource, nom)
                             for nom in TYPES_SOURCE]

        self.professions_createurs = {}
        self.professions_interpretes = []
        for nom, feminin in PROFESSIONS_CREATEURS:
            self.professions_createurs[nom] = Profession.objects.get_or_create(
                nom=nom, defaults={'nom_feminin': feminin,
                                   'owner': self.owner})[0]
        for nom, feminin in PROFESSIONS_INTERPRETES:
            self.professions_interpretes.append(
                Profession.objects.get_or_create(
                    nom=nom, defaults={'nom_feminin': feminin,
                                       'owner': self.owner})[0])

        self.type_decoupage = TypeDeCaracteristiqueDeProgramme.objects \
            .get_or_create(nom='découpage')[0]
        self.decoupages = [
            CaracteristiqueDeProgramme.objects.get_or_create(
                type=self.type_decoupage, valeur=valeur)[0]
            for valeur in DECOUPAGES]

        # Instruments partagés (parties sans œuvre, réutilisées par les pupitres).
        self.instruments = []
        for nom in INSTRUMENTS:
            self.instruments.append(Partie.objects.get_or_create(
                nom=nom, parent=None, oeuvre=None,
                defaults={'type': Partie.INSTRUMENT, 'owner': self.owner})[0])

    def create_lieux(self):
        self.villes = []
        self.salles = []
        for pays_nom, villes in PAYS_ET_VILLES.items():
            pays = Lieu.objects.create(
                nom=pays_nom, nature=self.natures['pays'], owner=self.owner)
            for ville_nom in villes:
                ville = Lieu.objects.create(
                    nom=ville_nom, parent=pays, nature=self.natures['ville'],
                    owner=self.owner)
                self.villes.append(ville)
                for _i in range(random.randint(1, 3)):
                    nature_nom = random.choice(
                        ['théâtre', 'salle de concert', 'opéra',
                         'conservatoire', 'église'])
                    if nature_nom == 'opéra':
                        nom = 'Opéra de %s' % ville_nom
                    elif nature_nom == 'conservatoire':
                        nom = 'Conservatoire de %s' % ville_nom
                    elif nature_nom == 'église':
                        nom = 'Église Saint-%s' % random.choice(
                            ['Louis', 'Pierre', 'Paul', 'Roch', 'Eustache'])
                    else:
                        nom = '%s %s' % (
                            nature_nom.capitalize(),
                            random.choice(
                                ['des Arts', 'Royal', 'Lyrique', 'Favart',
                                 'de la Renaissance', 'National', 'Italien']))
                    salle, created = Lieu.objects.get_or_create(
                        nom=nom, parent=ville,
                        defaults={'nature': self.natures[nature_nom],
                                  'is_institution': True, 'owner': self.owner})
                    if created:
                        self.salles.append(salle)
        if not self.salles:  # garde-fou
            self.salles = list(self.villes)

    def create_individus(self):
        self.individus = []
        for _i in tqdm(range(self.n('individus')), desc='individus'):
            feminin = random.random() < 0.4
            prenoms = random.choice(PRENOMS_FEM if feminin else PRENOMS_MASC)
            if random.random() < 0.3:
                prenoms += ' ' + random.choice(
                    PRENOMS_FEM if feminin else PRENOMS_MASC)
            naissance = self.random_date(1700, 1950)
            deces = None
            if random.random() < 0.85:
                deces_year = min(naissance.year + random.randint(35, 95), 2020)
                if deces_year > naissance.year:
                    deces = self.random_date(deces_year, deces_year)
            individu = Individu(
                nom=random.choice(NOMS),
                particule_nom=random.choice(PARTICULES),
                prenoms=prenoms,
                titre='F' if feminin else 'M',
                designation='S',
                naissance_date=naissance,
                naissance_lieu=(random.choice(self.villes)
                                if random.random() < 0.6 else None),
                deces_date=deces,
                owner=self.owner,
            )
            individu.save()
            individu.professions.add(random.choice(
                self.professions_interpretes
                + list(self.professions_createurs.values())))
            self.individus.append(individu)

    def create_ensembles(self):
        self.ensembles = []
        for _i in tqdm(range(self.n('ensembles')), desc='ensembles'):
            type_ensemble = random.choice(self.types_ensemble)
            ville = random.choice(self.villes)
            nom = '%s %s de %s' % (
                type_ensemble.nom.capitalize(),
                random.choice(['', 'royal', 'national', 'philharmonique',
                               'lyrique']),
                ville.nom)
            nom = ' '.join(nom.split())[:75]
            ensemble = Ensemble(
                nom=nom, type=type_ensemble, siege=ville, owner=self.owner)
            ensemble.save()
            for individu in random.sample(
                    self.individus, min(len(self.individus),
                                        random.randint(3, 12))):
                Membre.objects.create(
                    ensemble=ensemble, individu=individu,
                    instrument=(random.choice(self.instruments)
                                if random.random() < 0.5 else None),
                    owner=self.owner)
            self.ensembles.append(ensemble)

    def make_titre(self):
        article = random.choice(['Le ', 'La ', 'Les ', 'L’', 'Un ', ''])
        nom = random.choice(TITRE_NOMS).capitalize()
        if random.random() < 0.8:
            return '%s%s %s' % (article, nom, random.choice(TITRE_QUALIFS))
        return '%s%s' % (article, nom)

    def make_tonalite(self):
        return '%s%s%s' % (random.choice(TONALITE_GAMMES),
                           random.choice(TONALITE_NOTES),
                           random.choice(TONALITE_ALTERATIONS))

    def create_oeuvres(self):
        self.oeuvres = []
        compositeurs = [i for i in self.individus]
        for _i in tqdm(range(self.n('oeuvres')), desc='œuvres'):
            genre = random.choice(list(self.genres.values()))
            oeuvre = Oeuvre(genre=genre, owner=self.owner)
            if genre.nom in NUMBERED_GENRES:
                oeuvre.numero = str(random.randint(1, 12))
                oeuvre.tonalite = self.make_tonalite()
                if random.random() < 0.7:
                    oeuvre.opus = str(random.randint(1, 130))
            else:
                oeuvre.titre = self.make_titre()
            if random.random() < 0.8:
                oeuvre.creation_date = self.random_date(1700, 1960)
                oeuvre.creation_lieu = random.choice(self.salles)
                oeuvre.creation_type = 2  # première mondiale
            oeuvre.save()

            # Auteur(s) : un compositeur, parfois un librettiste.
            compositeur = random.choice(compositeurs)
            Auteur.objects.create(
                oeuvre=oeuvre, individu=compositeur,
                profession=self.professions_createurs['compositeur'],
                owner=self.owner)
            if genre.nom in ('opéra', 'opéra-comique', 'ballet', 'oratorio') \
                    and random.random() < 0.8:
                Auteur.objects.create(
                    oeuvre=oeuvre, individu=random.choice(compositeurs),
                    profession=self.professions_createurs['librettiste'],
                    owner=self.owner)

            self.add_parties_et_pupitres(oeuvre, genre)
            self.oeuvres.append(oeuvre)

    def add_parties_et_pupitres(self, oeuvre, genre):
        if genre.nom in ('opéra', 'opéra-comique', 'ballet', 'oratorio'):
            # Quelques rôles propres à l’œuvre.
            oeuvre._roles = []
            for nom in random.sample(ROLE_NAMES,
                                     min(len(ROLE_NAMES), random.randint(2, 5))):
                role = Partie.objects.create(
                    nom=nom, type=Partie.ROLE, oeuvre=oeuvre,
                    premier_interprete=(random.choice(self.individus)
                                        if random.random() < 0.6 else None),
                    owner=self.owner)
                Pupitre.objects.create(oeuvre=oeuvre, partie=role, soliste=True)
                oeuvre._roles.append(role)
        else:
            # Effectif instrumental partagé.
            for instrument in random.sample(
                    self.instruments,
                    min(len(self.instruments), random.randint(1, 4))):
                Pupitre.objects.create(
                    oeuvre=oeuvre, partie=instrument,
                    soliste=(genre.nom == 'concerto'),
                    quantite_min=1,
                    quantite_max=random.choice([1, 1, 1, 2, 4, 8]))

    def create_evenements(self):
        self.evenements = []
        for _i in tqdm(range(self.n('evenements')), desc='événements'):
            evenement = Evenement(
                debut_date=self.random_date(1750, 1970),
                debut_lieu=random.choice(self.salles),
                circonstance=random.choice(CIRCONSTANCES),
                owner=self.owner)
            evenement.save()
            if random.random() < 0.3:
                evenement.caracteristiques.add(random.choice(self.decoupages))

            # Programme : quelques œuvres jouées.
            for oeuvre in random.sample(
                    self.oeuvres, min(len(self.oeuvres), random.randint(1, 4))):
                element = ElementDeProgramme.objects.create(
                    evenement=evenement, oeuvre=oeuvre, owner=self.owner)
                # Distribution liée aux rôles de l’œuvre, le cas échéant.
                for role in getattr(oeuvre, '_roles', [])[:3]:
                    if random.random() < 0.7:
                        ElementDeDistribution.objects.create(
                            element_de_programme=element,
                            individu=random.choice(self.individus),
                            partie=role, owner=self.owner)

            # Distribution au niveau de l’événement (chef, solistes, ensemble).
            for _j in range(random.randint(1, 4)):
                if random.random() < 0.25 and self.ensembles:
                    ElementDeDistribution.objects.create(
                        evenement=evenement,
                        ensemble=random.choice(self.ensembles),
                        profession=random.choice(self.professions_interpretes),
                        owner=self.owner)
                else:
                    ElementDeDistribution.objects.create(
                        evenement=evenement,
                        individu=random.choice(self.individus),
                        profession=random.choice(self.professions_interpretes),
                        owner=self.owner)
            self.evenements.append(evenement)

    def create_sources(self):
        for _i in tqdm(range(self.n('sources')), desc='sources'):
            source = Source(
                type=random.choice(self.types_source),
                titre=self.make_titre(),
                date=self.random_date(1750, 1970),
                est_promu=random.random() < 0.3,
                transcription=(''.join('<p>%s</p>' % p
                                       for p in paragraphs(random.randint(1, 2),
                                                           common=False))
                               if random.random() < 0.5 else ''),
                owner=self.owner)
            source.save()
            if self.evenements and random.random() < 0.7:
                source.evenements.add(*random.sample(
                    self.evenements,
                    min(len(self.evenements), random.randint(1, 3))))
            if self.oeuvres and random.random() < 0.5:
                source.oeuvres.add(*random.sample(
                    self.oeuvres,
                    min(len(self.oeuvres), random.randint(1, 3))))
            if self.individus and random.random() < 0.5:
                source.individus.add(*random.sample(
                    self.individus,
                    min(len(self.individus), random.randint(1, 3))))

    def flush(self):
        u = self.owner
        from django.db.models import Q
        self.stdout.write('Suppression des données d’exemple existantes…')
        # D’abord la correspondance (musicaLetters) : ses pages référencent des
        # individus/lieux en PROTECT, il faut donc les supprimer avant eux.
        from correspondence.models import LetterCorpus
        for corpus in LetterCorpus.objects.filter(owner=u):
            corpus.delete()  # supprime aussi les lettres (sous-arbre treebeard)
        ElementDeDistribution.objects.filter(
            Q(evenement__owner=u)
            | Q(element_de_programme__evenement__owner=u)).delete()
        ElementDeProgramme.objects.filter(evenement__owner=u).delete()
        Source.objects.filter(owner=u).delete()
        Evenement.objects.filter(owner=u).delete()
        Pupitre.objects.filter(oeuvre__owner=u).delete()
        Auteur.objects.filter(oeuvre__owner=u).delete()
        Membre.objects.filter(ensemble__owner=u).delete()
        Partie.objects.filter(owner=u, oeuvre__owner=u).delete()  # rôles
        Oeuvre.objects.filter(owner=u).delete()
        Ensemble.objects.filter(owner=u).delete()
        Individu.objects.filter(owner=u).delete()
        # Lieux : supprimer feuilles puis racines (CASCADE sur parent).
        for lieu in Lieu.objects.filter(owner=u).order_by('-path'):
            lieu.delete()

    # -- Entrée -----------------------------------------------------------

    @transaction.atomic
    def handle(self, **options):
        self.scale = options['scale']
        if options['seed'] is not None:
            random.seed(options['seed'])

        self.owner = self.create_owner()
        self.create_vocabularies()

        if options['flush']:
            self.flush()

        with search_indexing_disabled():
            self.create_lieux()
            self.create_individus()
            self.create_ensembles()
            self.create_oeuvres()
            self.create_evenements()
            self.create_sources()

        # Étape « correspondance » : peuple le sous-site musicaLetters en
        # réutilisant la commande sœur (mêmes propriétaire, échelle et options).
        call_command('generate_sample_letters', scale=self.scale,
                     seed=options['seed'], flush=options['flush'])

        self.stdout.write(self.style.SUCCESS(
            'Données d’exemple créées : '
            '%d lieux, %d individus, %d ensembles, %d œuvres, '
            '%d événements, %d sources.' % (
                Lieu.objects.filter(owner=self.owner).count(),
                len(self.individus), len(self.ensembles), len(self.oeuvres),
                len(self.evenements),
                Source.objects.filter(owner=self.owner).count())))
        self.stdout.write(
            'Pensez à lancer « ./manage.py update_index » pour rendre '
            'la recherche et l’autocomplétion cohérentes.')
