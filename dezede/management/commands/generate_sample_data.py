"""
Génère un jeu de données d’exemple crédible et interconnecté pour le
développement et les démonstrations.

Contrairement aux imports spécialisés (``import_melodies``, ``import_poetes``),
cette commande ne dépend d’aucun fichier externe : elle fabrique de toutes
pièces des lieux, individus, ensembles, saisons, œuvres, événements, sources
et dossiers (de tous les types : dossiers d’événements, dossiers d’œuvres et
dossiers de sources) reliés entre eux, en respectant l’ordre de dépendance des
modèles.

Tous les champs optionnels (géo-positionnement des lieux, notes, biographies,
ISNI, périodes d’activité, caractéristiques d’œuvres, métadonnées de sources,
etc.) sont remplis environ une fois sur deux afin d’obtenir un jeu de données
réaliste qui exerce l’ensemble des affichages.

Exemples ::

    ./manage.py generate_sample_data
    ./manage.py generate_sample_data --scale 0.2 --seed 1 --flush

Le signal d’indexation (``libretto.signals.update_related_search_items``) est
débranché pendant la génération pour éviter de noyer la file RQ ; pensez à
lancer ``./manage.py update_index`` ensuite pour rendre la recherche cohérente.
"""

from contextlib import contextmanager
from datetime import date
from io import BytesIO
import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point, Polygon
from django.core.files.base import ContentFile
from django.core.management import call_command, get_commands
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.utils.lorem_ipsum import paragraphs, sentence
from PIL import Image, ImageDraw, ImageFont
from psycopg.types.range import Range
from tqdm import tqdm

from common.utils.file import FileAnalyzer

from dossiers.models import (
    CategorieDeDossiers, DossierDEvenements, DossierDOeuvres, DossierDeSources,
)
from libretto.models import (
    NatureDeLieu, Lieu, Individu, Profession, TypeDEnsemble, Ensemble, Membre,
    GenreDOeuvre, Oeuvre, Partie, Pupitre, Auteur,
    Evenement, ElementDeProgramme, ElementDeDistribution,
    TypeDeCaracteristiqueDeProgramme, CaracteristiqueDeProgramme,
    TypeDeSource, Source, Saison,
)
from libretto.models.base import slugify_unicode
from libretto.signals import update_related_search_items, handle_whitespaces


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

# Pluriels irréguliers (le simple ajout d’un « s » final serait incorrect
# pour ces noms composés).
TYPES_SOURCE_PLURIELS = {
    'compte rendu': 'comptes rendus',
    'article de presse': 'articles de presse',
}

# Types de sources « image » isolées (une seule page numérisée).
TYPES_SOURCE_IMAGE = ['photographie', 'gravure', 'affiche', 'dessin']

# Types de sources « livre » : recueils multi-pages promus en bibliothèque.
TYPES_LIVRE = ['recueil', 'livre', 'manuscrit', 'album', 'partition']

# Gabarits de titres de livres (« {} » est remplacé par un sujet).
TITRES_LIVRES = [
    'Recueil d’airs de {}', 'Album de mélodies de {}', 'Méthode de {}',
    'Chansonnier de {}', 'Œuvres complètes de {}', 'Cahier de {}',
    'Anthologie de {}', 'Mémoires de {}',
]
SUJETS_LIVRES = [
    'salon', 'concert', 'l’opéra', 'la cour', 'piano', 'chant', 'violon',
    'romances', 'la province', 'voyage', 'jeunesse',
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

# Géographie : pays -> villes (noms uniques au sein du pays), avec les
# coordonnées (longitude, latitude) servant au géo-positionnement.
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

# Coordonnées approximatives (longitude, latitude) des villes.
VILLE_COORDS = {
    'Paris': (2.3522, 48.8566), 'Lyon': (4.8357, 45.7640),
    'Marseille': (5.3698, 43.2965), 'Bordeaux': (-0.5792, 44.8378),
    'Rouen': (1.0993, 49.4431), 'Lille': (3.0573, 50.6292),
    'Nantes': (-1.5536, 47.2184), 'Strasbourg': (7.7521, 48.5734),
    'Toulouse': (1.4442, 43.6047), 'Versailles': (2.1301, 48.8049),
    'Nice': (7.2620, 43.7102), 'Dijon': (5.0415, 47.3220),
    'Berlin': (13.4050, 52.5200), 'Munich': (11.5820, 48.1351),
    'Dresde': (13.7373, 51.0504), 'Leipzig': (12.3731, 51.3397),
    'Hambourg': (9.9937, 53.5511), 'Cologne': (6.9603, 50.9375),
    'Milan': (9.1900, 45.4642), 'Venise': (12.3155, 45.4408),
    'Rome': (12.4964, 41.9028), 'Naples': (14.2681, 40.8518),
    'Florence': (11.2558, 43.7696), 'Turin': (7.6869, 45.0703),
    'Vienne': (16.3738, 48.2082), 'Salzbourg': (13.0550, 47.8095),
    'Graz': (15.4395, 47.0707), 'Londres': (-0.1276, 51.5074),
    'Édimbourg': (-3.1883, 55.9533), 'Manchester': (-2.2426, 53.4808),
    'Saint-Pétersbourg': (30.3351, 59.9343), 'Moscou': (37.6173, 55.7558),
}

# Coordonnées (longitude, latitude) servant de centre approximatif des pays.
PAYS_COORDS = {
    'France': (2.5, 46.5), 'Allemagne': (10.5, 51.0), 'Italie': (12.5, 42.5),
    'Autriche': (14.5, 47.5), 'Royaume-Uni': (-2.0, 53.5), 'Russie': (38.0, 56.0),
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

PSEUDONYMES = [
    'La Malibran', 'Le Rossignol', 'Mario', 'Rubini', 'La Grisi', 'Nourrit',
    'Le Cygne', 'La Damoreau', 'L’Aiglon', 'La Patti', 'Duprez', 'La Falcon',
]

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

TEMPI = [
    'Largo', 'Adagio', 'Andante', 'Andantino', 'Moderato', 'Allegretto',
    'Allegro', 'Allegro con brio', 'Presto', 'Presto ma non troppo',
    'Vivace', 'Lento', 'Grave',
]
SUJETS = [
    'un thème de Beethoven', 'un air populaire', 'des motifs de Lucia',
    'une romance ancienne', 'un choral de Bach', 'un thème original',
    'une mélodie écossaise', 'un noël provençal',
]
SURNOMS = [
    'Jupiter', 'Pastorale', 'Héroïque', 'L’Inachevée', 'La Surprise',
    'Les Adieux', 'Le Printemps', 'L’Empereur', 'La Tempête',
]
NOMS_COURANTS = [
    'barcarolle', 'sérénade', 'berceuse', 'tarentelle', 'romance sans paroles',
    'marche funèbre', 'air de bravoure', 'cavatine',
]
INCIPITS = [
    'Belle nuit, ô nuit d’amour', 'Plaisir d’amour', 'Connais-tu le pays',
    'Voi che sapete', 'Casta diva', 'Salut demeure chaste et pure',
    'Toréador, en garde', 'Pourquoi me réveiller',
]
ICTS = ['RV 42', 'K. 299d', 'Hob. XVI:24', 'BWV 1007', 'D. 911', 'op. posth.',
        'WoO 59', 'L. 75']

LIEUX_CONSERVATION = [
    'Bibliothèque nationale de France', 'Bibliothèque municipale de Lyon',
    'Archives municipales de Rouen', 'British Library',
    'Österreichische Nationalbibliothek', 'Bibliothèque de l’Opéra',
    'Conservatoire de Paris', 'Collection particulière',
    'Archives départementales de la Gironde', 'Staatsbibliothek zu Berlin',
]
COTES = ['Ms. 1234', 'Rés. F. 42', 'Vm7 567', 'D. 11.345', 'L. a. 9',
         'Fol. 23 bis', 'A-78/3', 'Carton 12, dossier 4']

ISNI_DIGITS = '0123456789'

TONALITE_GAMMES = ['C', 'A']          # majeur / mineur
TONALITE_NOTES = list('cdefgab')
TONALITE_ALTERATIONS = ['-', '0', '+']

CIRCONSTANCES = [
    'Première', 'Concert d’abonnement', 'Soirée de gala',
    'Représentation de bienfaisance', 'Festival', 'Reprise',
    'Concert spirituel', 'Inauguration', 'Concert de charité',
]

MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',
        'août', 'septembre', 'octobre', 'novembre', 'décembre']
SAISONS = ['hiver', 'printemps', 'été', 'automne']
MOMENTS = ['matinée', 'après-midi', 'soirée', 'nuit']

DECOUPAGES = ['en un acte', 'en deux actes', 'en trois actes',
              'en quatre actes', 'en cinq actes']

# Catégories sous lesquelles sont rangés les dossiers de premier niveau.
CATEGORIES_DOSSIERS = [
    'Théâtres et salles', 'Compositeurs', 'Genres et répertoires',
    'Villes et régions', 'Saisons et festivals',
]

# Gabarits de titres de dossiers (« {} » est remplacé par un sujet).
TITRES_DOSSIERS_EVENEMENTS = [
    'La saison lyrique à {}', 'Les concerts de {}', 'Représentations à {}',
    'Le théâtre de {} au XIXᵉ siècle', 'Festivals et galas de {}',
    'La vie musicale à {}', 'Soirées et premières à {}',
]
TITRES_DOSSIERS_OEUVRES = [
    'Le répertoire de {}', 'Les œuvres de {}', 'Catalogue des {}',
    'Autour de l’œuvre de {}', 'Le corpus des {} françaises',
    'Panorama des {}', 'Les grandes {} du répertoire',
]
TITRES_DOSSIERS_SOURCES = [
    'Sources autour de {}', 'Le fonds {}', 'Documents et {}',
    'Le corpus documentaire des {}', 'Archives et {}',
    'À travers les sources : {}', 'Pièces et témoignages de {}',
]

# Volumétrie de base (échelle « medium »), multipliée par --scale.
BASE_COUNTS = {
    'individus': 1000,
    'ensembles': 60,
    'oeuvres': 800,
    'evenements': 1500,
    'sources': 300,
    'sources_images': 80,
    'livres': 20,
    'saisons': 40,
    'dossiers_evenements': 8,
    'dossiers_oeuvres': 8,
    'dossiers_sources': 8,
}

OWNER_USERNAME = 'sample_data'

# Recherches Wikimedia Commons (domaine public) pour les images de couverture
# des dossiers : chaque terme est cherché dynamiquement via l’API Commons
# (voir ``_fetch_cover_images``) plutôt que de figer des URL de vignettes, qui
# encodent un hash de fichier fragile et changent de nom au moindre renommage.
WIKIMEDIA_COVER_SEARCH_TERMS = [
    'Paris Opera Garnier facade',
    'Opera Comique Paris',
    'La Scala Milan opera house',
    'Beethoven portrait',
    'Bizet portrait',
    'Camille Saint-Saens portrait',
    'Jules Massenet portrait',
    'Mozart portrait',
    'Chopin portrait',
    'Franz Liszt portrait',
    'Richard Wagner portrait',
    'Giuseppe Verdi portrait',
    'Claude Debussy portrait',
    'Gabriel Faure portrait',
    'concert hall auditorium interior',
    'opera house interior',
    'grand piano',
    'violin instrument',
    'orchestra concert',
    'sheet music manuscript',
]


@contextmanager
def search_indexing_disabled():
    """Débranche les signaux globaux (``pre_save`` de nettoyage des espaces et
    ``post_save`` d’indexation) pendant la génération en masse.

    Les ``bulk_create`` ne déclenchent de toute façon pas ces signaux ; on les
    débranche aussi pour les rares objets encore enregistrés un par un (arbres
    de lieux et d’œuvres), afin d’éviter de noyer la file RQ et d’appeler
    ``bleach`` sur chaque champ d’un jeu de données déjà propre."""
    post_save.disconnect(update_related_search_items)
    pre_save.disconnect(handle_whitespaces)
    try:
        yield
    finally:
        post_save.connect(update_related_search_items)
        pre_save.connect(handle_whitespaces)


class Command(BaseCommand):
    help = ('Remplit la base avec un jeu de données d’exemple crédible '
            '(lieux, individus, œuvres, événements, sources). Tous les champs '
            'optionnels sont remplis environ une fois sur deux.')

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

    def coin(self, p=0.5):
        """Vrai avec une probabilité ``p`` (1 sur 2 par défaut)."""
        return random.random() < p

    def random_date(self, start_year, end_year):
        start = date(start_year, 1, 1).toordinal()
        end = date(end_year, 12, 31).toordinal()
        return date.fromordinal(random.randint(start, end))

    def random_time(self):
        from datetime import time
        return time(random.randint(11, 22), random.choice([0, 15, 30, 45]))

    def opt_html(self, n_paragraphs=1):
        """Un petit fragment HTML une fois sur deux, sinon une chaîne vide."""
        if not self.coin():
            return ''
        return ''.join('<p>%s</p>' % p
                       for p in paragraphs(n_paragraphs, common=False))

    def opt_text(self):
        """Une phrase une fois sur deux, sinon une chaîne vide."""
        return sentence() if self.coin() else ''

    def opt(self, value):
        """Renvoie ``value`` une fois sur deux, sinon une chaîne vide."""
        return value if self.coin() else ''

    def random_isni(self):
        return ''.join(random.choices(ISNI_DIGITS, k=15)) \
            + random.choice(ISNI_DIGITS + 'X')

    def set_isni(self, obj):
        """Remplit l’ISNI une fois sur deux, sinon coche « sans ISNI » une
        fois sur deux."""
        if self.coin():
            obj.isni = self.random_isni()
        elif self.coin():
            obj.sans_isni = True

    def approx_date_str(self, year):
        return random.choice([
            'vers %d' % year,
            '%s %d' % (random.choice(MOIS), year),
            '%s %d' % (random.choice(SAISONS), year),
            'avant %d' % (year + 1),
        ])

    def approx_lieu_str(self, ville=None):
        if ville is not None:
            return random.choice(['environs de %s' % ville.nom,
                                  'région de %s' % ville.nom])
        return random.choice(['lieu inconnu', 'lieu non identifié'])

    def set_periode(self, obj, start_year=1700, end_year=1960):
        """Remplit une PeriodeDActivite (debut/fin + précisions) 1 fois sur 2."""
        if not self.coin():
            return
        debut = self.random_date(start_year, end_year)
        obj.debut = debut
        obj.debut_precision = random.choice([0, 0, 1, 2])
        if self.coin():
            obj.fin = self.random_date(debut.year, min(debut.year + 40, 2000))
            obj.fin_precision = random.choice([0, 0, 1, 2])

    def ville_point(self, ville_nom, jitter=0.03):
        coords = VILLE_COORDS.get(ville_nom)
        if coords is None:
            return None
        lon, lat = coords
        return Point(lon + random.uniform(-jitter, jitter),
                     lat + random.uniform(-jitter, jitter), srid=4326)

    def pays_polygon(self, pays_nom, half=2.5):
        coords = PAYS_COORDS.get(pays_nom)
        if coords is None:
            return None
        lon, lat = coords
        return Polygon((
            (lon - half, lat - half), (lon + half, lat - half),
            (lon + half, lat + half), (lon - half, lat + half),
            (lon - half, lat - half),
        ), srid=4326)

    def vocab(self, model, nom, **extra):
        return model.objects.get_or_create(nom=nom, defaults=extra)[0]

    # -- Helpers d’insertion en masse -------------------------------------

    @contextmanager
    def slug_autopopulate_disabled(self, *models):
        """Empêche temporairement ``AutoSlugField`` de (re)générer et de rendre
        unique le slug à l’enregistrement.

        ``AutoSlugField`` exécute son ``pre_save`` même pendant un
        ``bulk_create`` : avec ``always_update=True`` il lancerait une requête
        d’unicité par ligne et produirait des collisions au sein d’un même lot
        (les lignes du lot ne sont pas encore en base). On désactive donc la
        régénération et le contrôle d’unicité, après avoir nous-mêmes attribué
        des slugs uniques via :meth:`assign_unique_slugs`."""
        saved = []
        for model in models:
            f = model._meta.get_field('slug')
            # ``Field.unique`` is a read-only property backed by ``_unique``.
            saved.append((f, f.always_update, f._unique))
            f.always_update = False
            f._unique = False
        try:
            yield
        finally:
            for f, always_update, unique in saved:
                f.always_update = always_update
                f._unique = unique

    def assign_unique_slugs(self, model, objs, bases):
        """Attribue à chaque objet un slug unique dérivé de ``bases`` (liste de
        chaînes brutes), en évitant les collisions avec la base et au sein du
        lot, à la manière d’``AutoSlugField``."""
        used = set(model.objects.values_list('slug', flat=True))
        for obj, base in zip(objs, bases):
            root = slugify_unicode(base)[:50] or model._meta.model_name
            slug = root
            i = 1
            while slug in used:
                i += 1
                suffix = '-%d' % i
                slug = '%s%s' % (root[:50 - len(suffix)], suffix)
            used.add(slug)
            obj.slug = slug

    def bulk_create_tree(self, model, objs, slug_bases):
        """``bulk_create`` pour un modèle arborescent (paquet ``tree``) : les
        chemins (``path``) sont calculés côté base par un déclencheur, à
        condition que les parents soient déjà enregistrés (les appeler par
        niveau, parents d’abord). Les slugs uniques sont attribués à la main."""
        if not objs:
            return
        with self.slug_autopopulate_disabled(model):
            self.assign_unique_slugs(model, objs, slug_bases)
            model.objects.bulk_create(objs)

    def bulk_m2m(self, model, field_name, pairs):
        """Crée en une requête les lignes de la table d’association d’un champ
        ``ManyToManyField``. ``pairs`` : itérable de couples
        ``(objet_source, objet_cible)``."""
        pairs = [(s, t) for s, t in pairs if s is not None and t is not None]
        if not pairs:
            return
        field = model._meta.get_field(field_name)
        through = field.remote_field.through
        src = field.m2m_field_name()
        tgt = field.m2m_reverse_field_name()
        through.objects.bulk_create(
            [through(**{'%s_id' % src: s.pk, '%s_id' % tgt: t.pk})
             for s, t in pairs],
            ignore_conflicts=True)

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
        self.types_source = [
            self.vocab(TypeDeSource, nom,
                       nom_pluriel=TYPES_SOURCE_PLURIELS.get(nom, ''))
            for nom in TYPES_SOURCE]
        self.types_source_image = [self.vocab(TypeDeSource, nom)
                                   for nom in TYPES_SOURCE_IMAGE]
        self.types_livre = [self.vocab(TypeDeSource, nom)
                            for nom in TYPES_LIVRE]

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
        self.all_professions = (self.professions_interpretes
                                + list(self.professions_createurs.values()))

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
        # Lieu est un modèle arborescent : on insère par niveau (pays, villes,
        # salles), parents d’abord, pour que le déclencheur calcule les chemins.
        self.villes = []
        self.ville_noms = {}  # ville -> nom (pour le jitter des salles)
        self.salles = []

        # Niveau 1 : pays.
        pays_par_nom = {}
        for pays_nom in PAYS_ET_VILLES:
            pays_par_nom[pays_nom] = Lieu(
                nom=pays_nom, nature=self.natures['pays'], owner=self.owner,
                # Pays et villes sont toujours géo-positionnés (leurs
                # coordonnées sont connues) : sans cela les cartes du frontend
                # n'ont aucun point à agréger et restent vides.
                geometry=self.pays_polygon(pays_nom),
                historique=self.opt_html(), notes_publiques=self.opt_html(),
                notes_privees=self.opt_html())
        pays_objs = list(pays_par_nom.values())
        self.bulk_create_tree(Lieu, pays_objs, [p.nom for p in pays_objs])

        # Niveau 2 : villes.
        for pays_nom, villes in PAYS_ET_VILLES.items():
            for ville_nom in villes:
                self.villes.append(Lieu(
                    nom=ville_nom, parent=pays_par_nom[pays_nom],
                    nature=self.natures['ville'], owner=self.owner,
                    geometry=self.ville_point(ville_nom, jitter=0.0),
                    historique=self.opt_html(),
                    notes_publiques=self.opt_html(),
                    notes_privees=self.opt_html()))
        self.bulk_create_tree(Lieu, self.villes, [v.nom for v in self.villes])
        for ville in self.villes:
            self.ville_noms[ville.pk] = ville.nom

        # Niveau 3 : salles (dédoublonnées par (nom, ville) comme le faisait
        # l’ancien get_or_create).
        seen = set()
        for ville in self.villes:
            for _i in range(random.randint(1, 3)):
                nature_nom = random.choice(
                    ['théâtre', 'salle de concert', 'opéra',
                     'conservatoire', 'église'])
                if nature_nom == 'opéra':
                    nom = 'Opéra de %s' % ville.nom
                elif nature_nom == 'conservatoire':
                    nom = 'Conservatoire de %s' % ville.nom
                elif nature_nom == 'église':
                    nom = 'Église Saint-%s' % random.choice(
                        ['Louis', 'Pierre', 'Paul', 'Roch', 'Eustache'])
                else:
                    nom = '%s %s' % (
                        nature_nom.capitalize(),
                        random.choice(
                            ['des Arts', 'Royal', 'Lyrique', 'Favart',
                             'de la Renaissance', 'National', 'Italien']))
                if (nom, ville.pk) in seen:
                    continue
                seen.add((nom, ville.pk))
                self.salles.append(Lieu(
                    nom=nom, parent=ville, nature=self.natures[nature_nom],
                    is_institution=True, owner=self.owner,
                    geometry=(self.ville_point(ville.nom)
                              if self.coin() else None),
                    historique=self.opt_html(),
                    notes_publiques=self.opt_html(),
                    notes_privees=self.opt_html()))
        self.bulk_create_tree(Lieu, self.salles, [s.nom for s in self.salles])
        if not self.salles:  # garde-fou
            self.salles = list(self.villes)

    def create_individus(self):
        self.individus = []
        prof_choices = []  # professions tirées pour chaque individu (même ordre)
        for _i in tqdm(range(self.n('individus')), desc='individus'):
            feminin = random.random() < 0.4
            prenoms = random.choice(PRENOMS_FEM if feminin else PRENOMS_MASC)
            if random.random() < 0.3:
                prenoms += ' ' + random.choice(
                    PRENOMS_FEM if feminin else PRENOMS_MASC)
            naissance = self.random_date(1700, 1950)
            naissance_ville = (random.choice(self.villes)
                               if self.coin() else None)
            deces = deces_ville = None
            if self.coin():
                deces_year = min(naissance.year + random.randint(35, 95), 2020)
                if deces_year > naissance.year:
                    deces = self.random_date(deces_year, deces_year)
                    deces_ville = (random.choice(self.villes)
                                   if self.coin() else None)

            nom = random.choice(NOMS)
            individu = Individu(
                nom=nom,
                particule_nom=random.choice(PARTICULES),
                particule_nom_naissance=self.opt(random.choice(PARTICULES)),
                nom_naissance=(random.choice(NOMS) if self.coin() else ''),
                prenoms=prenoms,
                prenoms_complets=(
                    prenoms + ' ' + random.choice(
                        PRENOMS_FEM if feminin else PRENOMS_MASC)
                    if self.coin() else ''),
                pseudonyme=(random.choice(PSEUDONYMES) if self.coin() else ''),
                titre='F' if feminin else 'M',
                designation='S',
                naissance_date=naissance,
                naissance_date_approx=(self.approx_date_str(naissance.year)
                                       if self.coin() else ''),
                naissance_lieu=naissance_ville,
                naissance_lieu_approx=(
                    self.approx_lieu_str(naissance_ville) if self.coin()
                    else ''),
                deces_date=deces,
                deces_date_approx=(
                    self.approx_date_str(deces.year)
                    if deces and self.coin() else ''),
                deces_lieu=deces_ville,
                deces_lieu_approx=(
                    self.approx_lieu_str(deces_ville)
                    if deces and self.coin() else ''),
                biographie=self.opt_html(random.randint(1, 2)),
                notes_publiques=self.opt_html(),
                notes_privees=self.opt_html(),
                owner=self.owner,
            )
            self.set_isni(individu)
            self.individus.append(individu)
            prof_choices.append(random.sample(
                self.all_professions, random.randint(1, 2)))

        with self.slug_autopopulate_disabled(Individu):
            self.assign_unique_slugs(
                Individu, self.individus, [i.nom for i in self.individus])
            Individu.objects.bulk_create(self.individus)
        self.bulk_m2m(Individu, 'professions', [
            (individu, profession)
            for individu, profs in zip(self.individus, prof_choices)
            for profession in profs])

    def create_ensembles(self):
        self.ensembles = []
        membres = []
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
                nom=nom, type=type_ensemble,
                particule_nom=self.opt(random.choice(['Le ', 'La ', 'Les '])),
                siege=ville if self.coin() else None,
                notes_publiques=self.opt_html(),
                notes_privees=self.opt_html(),
                owner=self.owner)
            self.set_isni(ensemble)
            self.set_periode(ensemble, 1750, 1980)
            ensemble.save()
            for individu in random.sample(
                    self.individus, min(len(self.individus),
                                        random.randint(3, 12))):
                membre = Membre(
                    ensemble=ensemble, individu=individu,
                    instrument=(random.choice(self.instruments)
                                if self.coin() else None),
                    profession=(random.choice(self.professions_interpretes)
                                if self.coin() else None),
                    owner=self.owner)
                self.set_periode(membre, 1750, 1990)
                membres.append(membre)
            self.ensembles.append(ensemble)
        Membre.objects.bulk_create(membres)

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

    def make_titre_livre(self):
        return random.choice(TITRES_LIVRES).format(
            random.choice(SUJETS_LIVRES))

    # -- Génération d’images ----------------------------------------------

    # Teintes chaudes « parchemin » pour le fond des pages numérisées.
    PARCHEMIN = [(244, 238, 222), (240, 234, 214), (248, 243, 230),
                 (236, 228, 206)]

    # Ratios largeur/hauteur courants pour des livres (portrait) : poche,
    # in-octavo, A5/ISO, in-quarto… Chaque livre en choisit un comme base ;
    # ses pages s’en écartent légèrement (numérisation amateur imparfaite).
    BOOK_ASPECT_RATIOS = (
        0.618,  # nombre d’or
        0.625,  # 5:8 (poche)
        0.647,  # digest 5,5 × 8,5"
        0.667,  # 2:3 (broché courant)
        0.690,  # in-octavo
        0.707,  # 1:√2 (A5 / ISO 216)
        0.730,  # crown
        0.773,  # quarto / US Letter
    )

    # Polices TrueType à essayer pour le texte des pages. Contrairement à la
    # police bitmap par défaut de Pillow (ASCII seulement, qui rend « Œ » ou
    # « è » en tofu), DejaVu couvre les accents et ligatures. Presque toujours
    # présente sous Debian ; sinon on retombe sur ``load_default``.
    FONT_CANDIDATES = (
        '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    )

    @classmethod
    def _load_font(cls, size):
        for path in cls.FONT_CANDIDATES:
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
        return ImageFont.load_default(size=size)

    def make_page_image(self, titre, page_label, aspect_ratio=0.727):
        """Génère en mémoire un JPEG ressemblant à une page numérisée (fond
        teinté façon parchemin, titre et numéro de page dessinés, fausses
        lignes de texte), renvoyé en ``ContentFile`` prêt pour ``Source.fichier``.

        ``aspect_ratio`` est le ratio largeur/hauteur visé (défaut ≈ 800/1100) ;
        on lui applique une petite perturbation aléatoire par page pour imiter
        un cadrage amateur jamais parfaitement reproductible d’une page à
        l’autre.

        Le texte est dessiné avec une police TrueType (cf. :meth:`_load_font`)
        afin que les caractères accentués et la ligature « Œ » des titres
        s’affichent correctement plutôt qu’en tofu."""
        # Hauteur de référence légèrement variable, puis ratio bruité (± ~4 %)
        # pour que deux pages d’un même livre ne soient jamais identiques.
        height = random.randint(1075, 1125)
        jittered_ratio = aspect_ratio * random.uniform(0.96, 1.04)
        width = max(1, round(height * jittered_ratio))
        img = Image.new('RGB', (width, height), random.choice(self.PARCHEMIN))
        draw = ImageDraw.Draw(img)
        ink = (60, 50, 40)
        margin = 70

        title_font = self._load_font(34)
        body_font = self._load_font(20)

        # Titre tronqué à la largeur réelle (les glyphes TrueType débordent du
        # gabarit en caractères) puis filet de séparation.
        max_title_width = width - 2 * margin
        title = titre
        while title and draw.textlength(title, font=title_font) > max_title_width:
            title = title[:-1].rstrip()
        if title != titre:
            title = title[:-1].rstrip() + '…'
        draw.text((margin, margin), title, fill=ink, font=title_font)
        draw.line((margin, margin + 60, width - margin, margin + 60),
                  fill=ink, width=2)

        # Fausses lignes de texte (rectangles gris clair de longueur variable).
        y = margin + 110
        line_color = (170, 160, 140)
        while y < height - 140:
            line_width = random.randint((width - 2 * margin) // 2,
                                        width - 2 * margin)
            draw.rectangle((margin, y, margin + line_width, y + 8),
                           fill=line_color)
            y += 34

        # Numéro de page, centré en bas.
        draw.text((width // 2 - 30, height - 90), page_label, fill=ink,
                  font=body_font)

        buf = BytesIO()
        img.save(buf, format='JPEG', quality=80, progressive=True)
        name = '%s_%s.jpg' % (
            slugify_unicode(titre)[:40] or 'page',
            slugify_unicode(page_label) or 'p')
        return ContentFile(buf.getvalue(), name=name)

    def create_oeuvres(self):
        # Oeuvre est arborescent (extrait_de) : on construit toutes les œuvres
        # sans les enregistrer, puis on insère en masse les « racines » avant
        # les extraits (qui y font référence). Les enfants (auteurs, rôles,
        # pupitres, dédicataires) sont accumulés et insérés après.
        self.oeuvres = []
        self._auteurs = []
        self._dedic_pairs = []
        self._role_specs = []     # (oeuvre, nom, premier_interprete, profession)
        self._inst_pupitres = []  # Pupitre instrumentaux prêts à insérer
        specs = []                # (oeuvre, genre, veut_extrait)
        for _i in tqdm(range(self.n('oeuvres')), desc='œuvres'):
            genre = random.choice(list(self.genres.values()))
            significatif = genre.nom not in NUMBERED_GENRES
            oeuvre = Oeuvre(
                genre=genre,
                numero=(str(random.randint(1, 12))
                        if genre.nom in NUMBERED_GENRES else ''),
                tonalite=(self.make_tonalite() if self.coin() else ''),
                opus=(str(random.randint(1, 130)) if self.coin() else ''),
                ict=(random.choice(ICTS) if self.coin() else ''),
                coupe=(random.choice(DECOUPAGES).replace('en ', '')
                       if genre.nom in ('opéra', 'opéra-comique', 'ballet')
                       and self.coin() else ''),
                incipit=(random.choice(INCIPITS) if self.coin() else ''),
                tempo=(random.choice(TEMPI) if self.coin() else ''),
                sujet=(random.choice(SUJETS) if self.coin() else ''),
                surnom=(random.choice(SURNOMS) if self.coin() else ''),
                nom_courant=(random.choice(NOMS_COURANTS)
                             if self.coin() else ''),
                arrangement=(random.choice([Oeuvre.TRANSCRIPTION,
                                            Oeuvre.ORCHESTRATION])
                             if self.coin() else None),
                ambitus=(Range(random.randint(24, 48),
                               random.randint(60, 96), '[]')
                         if self.coin() else None),
                notes_publiques=self.opt_html(),
                notes_privees=self.opt_html(),
                owner=self.owner)
            if significatif:
                oeuvre.titre = self.make_titre()
                if self.coin():
                    oeuvre.coordination = ', '
                    oeuvre.titre_secondaire = self.make_titre()
            if self.coin():
                creation = self.random_date(1700, 1960)
                oeuvre.creation_date = creation
                oeuvre.creation_lieu = random.choice(self.salles)
                oeuvre.creation_type = random.choice([1, 2, 3])
                if self.coin():
                    oeuvre.creation_heure = self.random_time()
                if self.coin():
                    oeuvre.creation_date_approx = self.approx_date_str(
                        creation.year)

            # Sera peut-être transformée en extrait (résolu après la boucle,
            # une fois les œuvres référentes enregistrées et pourvues d’un pk).
            veut_extrait = self.coin(0.25)

            # Auteur(s) : un compositeur, parfois un librettiste.
            compositeur = random.choice(self.individus)
            self._auteurs.append(Auteur(
                oeuvre=oeuvre, individu=compositeur,
                profession=self.professions_createurs['compositeur'],
                owner=self.owner))
            if genre.nom in ('opéra', 'opéra-comique', 'ballet', 'oratorio') \
                    and self.coin():
                self._auteurs.append(Auteur(
                    oeuvre=oeuvre, individu=random.choice(self.individus),
                    profession=self.professions_createurs['librettiste'],
                    owner=self.owner))

            # Dédicataire(s), une fois sur deux.
            if self.coin():
                for individu in random.sample(
                        self.individus, random.randint(1, 2)):
                    self._dedic_pairs.append((oeuvre, individu))

            self.add_parties_et_pupitres(oeuvre, genre)
            self.oeuvres.append(oeuvre)
            specs.append((oeuvre, genre, veut_extrait))

        # Parents potentiels : œuvres référentes qui ne deviendront pas extraits.
        significatives = [o for o, g, we in specs if g.referent and not we]
        roots, extracts = [], []
        for oeuvre, genre, veut_extrait in specs:
            (extracts if veut_extrait and significatives else roots).append(
                oeuvre)
        # Racines d’abord (le déclencheur a besoin du parent enregistré).
        self.bulk_create_tree(
            Oeuvre, roots, [self._oeuvre_slug_base(o) for o in roots])
        for oeuvre in extracts:
            oeuvre.extrait_de = random.choice(significatives)
            oeuvre.type_extrait = random.choice([
                Oeuvre.ACTE, Oeuvre.SCENE, Oeuvre.MORCEAU, Oeuvre.MOUVEMENT])
            oeuvre.numero_extrait = str(random.randint(1, 8))
        self.bulk_create_tree(
            Oeuvre, extracts, [self._oeuvre_slug_base(o) for o in extracts])

        self.flush_oeuvres_children()

    def _oeuvre_slug_base(self, oeuvre):
        if oeuvre.titre:
            return oeuvre.titre
        return ' '.join(p for p in (
            oeuvre.genre.nom, oeuvre.numero or oeuvre.opus
            or oeuvre.surnom or oeuvre.nom_courant) if p)

    def flush_oeuvres_children(self):
        """Insère en masse auteurs, dédicataires, rôles et pupitres accumulés
        pendant :meth:`create_oeuvres`."""
        Auteur.objects.bulk_create(self._auteurs)
        self.bulk_m2m(Oeuvre, 'dedicataires', self._dedic_pairs)

        # Rôles (Partie) : slug unique attribué à la main, puis bulk_create.
        roles = [
            Partie(nom=nom, type=Partie.ROLE, oeuvre=oeuvre,
                   premier_interprete=premier_interprete, owner=self.owner)
            for oeuvre, nom, premier_interprete, _profession
            in self._role_specs]
        with self.slug_autopopulate_disabled(Partie):
            self.assign_unique_slugs(
                Partie, roles, [r.nom for r in roles])
            Partie.objects.bulk_create(roles)

        # Pupitres des rôles (solistes) + association des œuvres à leurs rôles
        # (réutilisée plus tard pour la distribution des événements).
        role_pupitres = []
        role_prof_pairs = []
        for role, (oeuvre, _nom, _interp, profession) in zip(
                roles, self._role_specs):
            if not hasattr(oeuvre, '_roles'):
                oeuvre._roles = []
            oeuvre._roles.append(role)
            role_pupitres.append(Pupitre(oeuvre=oeuvre, partie=role,
                                         soliste=True))
            if profession is not None:
                role_prof_pairs.append((role, profession))
        Pupitre.objects.bulk_create(self._inst_pupitres + role_pupitres)
        self.bulk_m2m(Partie, 'professions', role_prof_pairs)

    def add_parties_et_pupitres(self, oeuvre, genre):
        if genre.nom in ('opéra', 'opéra-comique', 'ballet', 'oratorio'):
            # Quelques rôles propres à l’œuvre (insérés en masse plus tard).
            for nom in random.sample(ROLE_NAMES,
                                     min(len(ROLE_NAMES), random.randint(2, 5))):
                self._role_specs.append((
                    oeuvre, nom,
                    random.choice(self.individus) if self.coin() else None,
                    random.choice(self.professions_interpretes)
                    if self.coin() else None))
        else:
            # Effectif instrumental partagé.
            for instrument in random.sample(
                    self.instruments,
                    min(len(self.instruments), random.randint(1, 4))):
                self._inst_pupitres.append(Pupitre(
                    oeuvre=oeuvre, partie=instrument,
                    soliste=(genre.nom == 'concerto'),
                    quantite_min=1,
                    quantite_max=random.choice([1, 1, 1, 2, 4, 8]),
                    facultatif=self.coin(0.15)))

    def create_evenements(self):
        # Phase 1 : construire tous les événements puis les insérer en masse.
        self.evenements = []
        event_carac = []   # caractéristique (ou None) par événement, même ordre
        programmes = []    # liste d’œuvres jouées par événement (ou None)
        for _i in tqdm(range(self.n('evenements')), desc='événements'):
            debut = self.random_date(1750, 1970)
            debut_salle = random.choice(self.salles)
            relache = self.coin(0.1)
            evenement = Evenement(
                debut_date=debut,
                debut_lieu=debut_salle,
                debut_heure=(self.random_time() if self.coin() else None),
                debut_date_approx=(self.approx_date_str(debut.year)
                                   if self.coin() else ''),
                debut_heure_approx=(random.choice(MOMENTS)
                                    if self.coin() else ''),
                circonstance=(random.choice(CIRCONSTANCES)
                              if self.coin() else ''),
                relache=relache,
                programme_incomplet=self.coin(),
                recette_generale=(random.randint(200, 20000)
                                  if self.coin() else None),
                recette_par_billets=(
                    '+'.join(str(random.randint(50, 4000))
                             for _ in range(random.randint(1, 4)))
                    if self.coin() else ''),
                notes_publiques=self.opt_html(),
                notes_privees=self.opt_html(),
                owner=self.owner)
            # Événement sur plusieurs jours / avec lieu de fin, une fois sur deux.
            if self.coin():
                fin = self.random_date(debut.year, debut.year + 1)
                if fin >= debut:
                    evenement.fin_date = fin
                evenement.fin_lieu = (random.choice(self.salles)
                                      if self.coin() else None)
                if self.coin():
                    evenement.fin_heure = self.random_time()
            self.evenements.append(evenement)
            event_carac.append(random.choice(self.decoupages)
                               if self.coin() else None)
            programmes.append(None if relache else random.sample(
                self.oeuvres, min(len(self.oeuvres), random.randint(1, 4))))
        Evenement.objects.bulk_create(self.evenements)
        self.bulk_m2m(Evenement, 'caracteristiques',
                      zip(self.evenements, event_carac))

        # Phase 2 : éléments de programme (œuvres jouées + entrées « autre »).
        # ``position`` est calculé à la main car ``bulk_create`` court-circuite
        # le ``save()`` qui le déduit habituellement par agrégat.
        elements = []
        element_carac = []
        element_oeuvre = []  # œuvre liée à chaque élément (pour la distribution)
        for evenement, programme in zip(self.evenements, programmes):
            if programme is None:
                continue
            position = 0
            for oeuvre in programme:
                position += 1
                elements.append(ElementDeProgramme(
                    evenement=evenement, oeuvre=oeuvre, position=position,
                    numerotation=random.choices(
                        ['O', 'B', 'U', 'E'], weights=[70, 15, 10, 5])[0],
                    part_d_auteur=(round(random.uniform(0, 100), 2)
                                   if self.coin() else None),
                    owner=self.owner))
                element_carac.append(random.choice(self.decoupages)
                                     if self.coin() else None)
                element_oeuvre.append(oeuvre)
            # Une entrée « autre » (œuvre non identifiée), parfois.
            if self.coin(0.2):
                position += 1
                elements.append(ElementDeProgramme(
                    evenement=evenement, position=position,
                    autre='%s (œuvre non identifiée)' % self.make_titre(),
                    numerotation='U', owner=self.owner))
                element_carac.append(None)
                element_oeuvre.append(None)
        ElementDeProgramme.objects.bulk_create(elements)
        self.bulk_m2m(ElementDeProgramme, 'caracteristiques',
                      zip(elements, element_carac))

        # Phase 3 : distributions (par rôle d’œuvre, puis au niveau événement).
        distributions = []
        for element, oeuvre in zip(elements, element_oeuvre):
            if oeuvre is None:
                continue
            for role in getattr(oeuvre, '_roles', [])[:3]:
                if self.coin(0.7):
                    distributions.append(ElementDeDistribution(
                        element_de_programme=element,
                        individu=random.choice(self.individus),
                        partie=role, owner=self.owner))
        for evenement, programme in zip(self.evenements, programmes):
            if programme is None:
                continue
            # Distribution au niveau de l’événement (chef, solistes, ensemble).
            for _j in range(random.randint(1, 4)):
                if self.coin(0.25) and self.ensembles:
                    distributions.append(ElementDeDistribution(
                        evenement=evenement,
                        ensemble=random.choice(self.ensembles),
                        profession=random.choice(self.professions_interpretes),
                        owner=self.owner))
                else:
                    distributions.append(ElementDeDistribution(
                        evenement=evenement,
                        individu=random.choice(self.individus),
                        profession=random.choice(self.professions_interpretes),
                        owner=self.owner))
        ElementDeDistribution.objects.bulk_create(distributions)

    def create_sources(self):
        sources = self.sources = []
        for _i in tqdm(range(self.n('sources')), desc='sources'):
            ancrage = self.random_date(1750, 1970)
            titre = self.make_titre()
            source = Source(
                type=random.choice(self.types_source),
                titre=titre,
                legende=self.opt_text(),
                date=ancrage,
                date_approx=(self.approx_date_str(ancrage.year)
                             if self.coin() else ''),
                numero=(str(random.randint(1, 400)) if self.coin() else ''),
                folio=(str(random.randint(1, 200)) if self.coin() else ''),
                page=(str(random.randint(1, 600)) if self.coin() else ''),
                lieu_conservation=(random.choice(LIEUX_CONSERVATION)
                                   if self.coin() else ''),
                cote=(random.choice(COTES) if self.coin() else ''),
                url=('https://example.org/source/%d' % random.randint(1, 99999)
                     if self.coin() else ''),
                # Promotion en bibliothèque rare ici : la bibliothèque est
                # surtout peuplée par les livres et images générés ensuite.
                est_promu=self.coin(0.15),
                transcription=self.opt_html(random.randint(1, 2)),
                presentation=self.opt_text(),
                contexte=self.opt_text(),
                sources_et_protocole=self.opt_text(),
                bibliographie=self.opt_text(),
                publications=self.opt_text(),
                developpements=self.opt_text(),
                notes_publiques=self.opt_html(),
                notes_privees=self.opt_html(),
                owner=self.owner)
            sources.append(source)
        Source.objects.bulk_create(sources)

        # Quelques sources rattachées à une source « parente » antérieure
        # (forêt sans cycle : on ne référence qu’un index inférieur).
        with_parent = []
        for i, source in enumerate(sources):
            if i and self.coin(0.2):
                source.parent = sources[random.randint(0, i - 1)]
                with_parent.append(source)
        if with_parent:
            Source.objects.bulk_update(with_parent, ['parent'])

        # Relations ManyToMany, insérées en masse par table d’association.
        self.link_sources_m2m(sources)

        # Sources « image » isolées et livres multi-pages (avec fichiers).
        self.create_source_images_and_books()

    def link_sources_m2m(self, sources):
        """Relie une liste de sources à des événements, œuvres, individus,
        ensembles et lieux (insertion en masse par table d’association)."""
        m2m = {'evenements': ([], self.evenements, 0.7, (1, 3)),
               'oeuvres': ([], self.oeuvres, 0.5, (1, 3)),
               'individus': ([], self.individus, 0.5, (1, 3)),
               'ensembles': ([], self.ensembles, 0.3, (1, 2)),
               'lieux': ([], self.villes, 0.3, (1, 2))}
        for source in sources:
            for pairs, pool, p, (lo, hi) in m2m.values():
                if pool and self.coin(p):
                    for target in random.sample(
                            pool, min(len(pool), random.randint(lo, hi))):
                        pairs.append((source, target))
        for field_name, (pairs, _pool, _p, _r) in m2m.items():
            self.bulk_m2m(Source, field_name, pairs)

    def link_pages_m2m(self, pages):
        """Relie environ la moitié des pages de livres à un petit nombre
        d’objets liés (œuvres, individus, événements), de quoi alimenter la
        barre latérale de présentation page par page. Les autres pages restent
        nues, comme des pages numérisées au contenu non encore identifié."""
        m2m = {'oeuvres': ([], self.oeuvres, (1, 2)),
               'individus': ([], self.individus, (1, 2)),
               'evenements': ([], self.evenements, (1, 1))}
        for page in pages:
            if not self.coin():
                continue
            for pairs, pool, (lo, hi) in m2m.values():
                if pool and self.coin():
                    for target in random.sample(
                            pool, min(len(pool), random.randint(lo, hi))):
                        pairs.append((page, target))
        for field_name, (pairs, _pool, _r) in m2m.items():
            self.bulk_m2m(Source, field_name, pairs)

    def create_source_images_and_books(self):
        """Crée des sources « image » isolées et des livres multi-pages
        (recueils) promus en bibliothèque, en générant de vrais fichiers JPEG.

        Ces lignes portent des fichiers : on les enregistre une par une (via
        ``save()``), comme le fait :func:`libretto.jobs.split_pdf`, afin que
        ``FileField.pre_save`` valide chaque fichier dans le stockage — les
        ``bulk_create`` court-circuiteraient cette écriture. Les vignettes sont
        générées paresseusement par easy-thumbnails à la première requête."""
        # -- Sources « image » isolées --------------------------------------
        images = []
        for _i in tqdm(range(self.n('sources_images')), desc='sources image'):
            ancrage = self.random_date(1750, 1970)
            titre = self.make_titre()
            source = Source(
                type=random.choice(self.types_source_image),
                titre=titre,
                legende=self.opt_text() or sentence(),
                date=ancrage,
                lieu_conservation=(random.choice(LIEUX_CONSERVATION)
                                   if self.coin() else ''),
                cote=(random.choice(COTES) if self.coin() else ''),
                # Non promues : la bibliothèque ne doit mettre en avant que les
                # livres multi-pages, pas ces images isolées qui, dans la
                # galerie, sont indiscernables d’un livre alors qu’elles n’ont
                # qu’une seule page.
                est_promu=False,
                fichier=self.make_page_image(titre, 'p. 1'),
                type_fichier=FileAnalyzer.IMAGE,
                notes_publiques=self.opt_html(),
                notes_privees=self.opt_html(),
                owner=self.owner)
            source.save()
            images.append(source)
        self.link_sources_m2m(images)

        # -- Livres multi-pages (recueils) promus en bibliothèque ------------
        livres = []
        pages = []
        for _i in tqdm(range(self.n('livres')), desc='livres'):
            ancrage = self.random_date(1750, 1970)
            titre = self.make_titre_livre()
            # Format de base du livre : toutes ses pages partagent ce ratio,
            # à un léger bruit de numérisation près (cf. make_page_image).
            book_ratio = random.choice(self.BOOK_ASPECT_RATIOS)
            livre = Source(
                type=random.choice(self.types_livre),
                titre=titre,
                date=ancrage,
                date_approx=(self.approx_date_str(ancrage.year)
                             if self.coin() else ''),
                lieu_conservation=random.choice(LIEUX_CONSERVATION),
                cote=random.choice(COTES),
                est_promu=True,
                presentation=self.opt_text(),
                contexte=self.opt_text(),
                notes_publiques=self.opt_html(),
                notes_privees=self.opt_html(),
                owner=self.owner)
            livre.save()
            for position in range(1, random.randint(3, 20) + 1):
                page_label = 'p. %d' % position
                page = Source(
                    parent=livre, position=position, page=str(position),
                    type=livre.type,
                    fichier=self.make_page_image(titre, page_label,
                                                 aspect_ratio=book_ratio),
                    type_fichier=FileAnalyzer.IMAGE,
                    owner=self.owner)
                page.save()
                pages.append(page)
            livres.append(livre)
        self.link_sources_m2m(livres)
        self.link_pages_m2m(pages)

        self.source_images = images
        self.livres = livres
        self.livre_pages = pages

    def create_saisons(self):
        # Saisons rattachées à un ensemble ou à un lieu, réutilisées par les
        # dossiers d’événements (champ ``saisons``). Une saison court de
        # septembre à juin de l’année suivante.
        self.saisons = []
        for _i in tqdm(range(self.n('saisons')), desc='saisons'):
            annee = random.randint(1750, 1960)
            saison = Saison(debut=date(annee, 9, 1), fin=date(annee + 1, 6, 30),
                            owner=self.owner)
            if self.ensembles and self.coin():
                saison.ensemble = random.choice(self.ensembles)
            else:
                saison.lieu = random.choice(self.salles or self.villes)
            self.saisons.append(saison)
        Saison.objects.bulk_create(self.saisons)

    def _dossier_common_kwargs(self, titre, used_slugs):
        """Champs communs à tous les dossiers (article, métadonnées, slug)."""
        root = slugify_unicode(titre)[:50] or 'dossier'
        slug = root
        i = 1
        while slug in used_slugs:
            i += 1
            suffix = '-%d' % i
            slug = '%s%s' % (root[:50 - len(suffix)], suffix)
        used_slugs.add(slug)
        return dict(
            titre=titre,
            titre_court=self.opt(titre[:50]),
            slug=slug,
            # ``presentation`` n’est pas optionnel : toujours rempli.
            presentation=''.join(
                '<p>%s</p>' % p for p in paragraphs(random.randint(1, 3),
                                                    common=False)),
            contexte=self.opt_html(random.randint(1, 2)),
            sources_et_protocole=self.opt_html(),
            bibliographie=self.opt_html(),
            publications=self.opt_text(),
            developpements=self.opt_text(),
            date_publication=self.random_date(2010, 2024),
            owner=self.owner,
        )

    COMMONS_API = 'https://commons.wikimedia.org/w/api.php'
    COMMONS_USER_AGENT = 'dezede-sample-data/1.0 (https://dezede.org/)'

    def _commons_api_get(self, params):
        url = self.COMMONS_API + '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(
            url, headers={'User-Agent': self.COMMONS_USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.load(resp)

    def _find_commons_file(self, search_term):
        """Recherche un fichier image existant sur Wikimedia Commons pour
        ``search_term`` et renvoie son URL de vignette (~1000 px), ou ``None``.

        On passe par l’API de recherche plutôt que par une URL de vignette
        écrite en dur : ces URL encodent un hash de fichier et changent de nom
        au moindre renommage/déplacement sur Commons, donc les deviner à la
        main produit des liens invalides ou périmés."""
        data = self._commons_api_get({
            'action': 'query', 'list': 'search', 'srnamespace': '6',
            'srsearch': search_term + ' filetype:bitmap', 'srlimit': '5',
            'format': 'json'})
        titles = [r['title'] for r in data.get('query', {}).get('search', [])]
        if not titles:
            return None
        data = self._commons_api_get({
            'action': 'query', 'titles': '|'.join(titles), 'prop': 'imageinfo',
            'iiprop': 'url', 'iiurlwidth': '1000', 'format': 'json'})
        for page in data.get('query', {}).get('pages', {}).values():
            imageinfo = page.get('imageinfo')
            if imageinfo:
                return imageinfo[0].get('thumburl') or imageinfo[0].get('url')
        return None

    def _fetch_cover_images(self):
        """Downloads Wikimedia Commons cover images once (resolved dynamically
        by search, see :meth:`_find_commons_file`), caching them as
        ``ContentFile``. Images that fail to find or download are silently
        skipped so the command still works offline."""
        self._cover_images = []
        for term in tqdm(WIKIMEDIA_COVER_SEARCH_TERMS, desc='images dossiers'):
            try:
                thumb_url = self._find_commons_file(term)
                if thumb_url is None:
                    continue
                req = urllib.request.Request(
                    thumb_url, headers={'User-Agent': self.COMMONS_USER_AGENT})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read()
                filename = slugify_unicode(term)[:40] + '.jpg'
                self._cover_images.append(ContentFile(data, name=filename))
            except Exception:
                pass
            # Courtoisie envers l’API Commons (pas de clé d’API, IP partagée).
            time.sleep(0.5)

    def _assign_cover_image(self, dossier):
        """Assigns a random cached cover image to ``dossier.logo`` (50 % chance,
        silently skipped when no images were downloaded)."""
        if not self._cover_images or not self.coin():
            return
        cf = random.choice(self._cover_images)
        # ContentFile is not reusable after the first save (the file pointer is
        # exhausted). Wrap the raw bytes in a fresh ContentFile each time.
        dossier.image_couverture.save(cf.name, ContentFile(cf.read(), name=cf.name),
                              save=True)
        cf.seek(0)

    def create_dossiers(self):
        # Deux types de dossiers existent : dossiers d’événements et dossiers
        # d’œuvres. On en crée plusieurs de chaque, certains à sélection
        # « dynamique » (critères : lieux, individus, genres, dates…), d’autres
        # à sélection « manuelle » (événements ou œuvres explicitement listés),
        # avec quelques dossiers imbriqués pour exercer l’arborescence.
        self.categories = [
            CategorieDeDossiers.objects.get_or_create(
                nom=nom, defaults={'position': pos, 'owner': self.owner})[0]
            for pos, nom in enumerate(CATEGORIES_DOSSIERS, start=1)]
        used_slugs = set(
            DossierDEvenements.objects.values_list('slug', flat=True))
        used_slugs |= set(DossierDOeuvres.objects.values_list('slug', flat=True))
        used_slugs |= set(
            DossierDeSources.objects.values_list('slug', flat=True))

        villes_noms = [v.nom for v in self.villes]
        genres = list(self.genres.values())
        dossiers = []  # (dossier, peut_avoir_des_enfants)

        # -- Dossiers d’événements -------------------------------------------
        for _i in tqdm(range(self.n('dossiers_evenements')),
                       desc='dossiers d’événements'):
            sujet = random.choice(villes_noms) if villes_noms else 'la province'
            titre = random.choice(TITRES_DOSSIERS_EVENEMENTS).format(sujet)
            debut = self.random_date(1750, 1900)
            dossier = DossierDEvenements(
                categorie=random.choice(self.categories),
                circonstance=self.opt(random.choice(CIRCONSTANCES)),
                debut=debut,
                fin=self.random_date(debut.year, 1970),
                **self._dossier_common_kwargs(titre, used_slugs))
            dossier.save()
            self._assign_cover_image(dossier)
            dossier.editeurs_scientifiques.add(self.owner)
            if self.coin(0.6):
                # Sélection dynamique : critères de filtrage.
                dossier.lieux.set(random.sample(
                    self.villes, min(len(self.villes), random.randint(1, 3))))
                dossier.oeuvres.set(random.sample(
                    self.oeuvres, min(len(self.oeuvres), random.randint(1, 3))))
                dossier.individus.set(random.sample(
                    self.individus,
                    min(len(self.individus), random.randint(1, 3))))
                if self.ensembles and self.coin():
                    dossier.ensembles.set(random.sample(
                        self.ensembles,
                        min(len(self.ensembles), random.randint(1, 2))))
                if self.saisons and self.coin():
                    dossier.saisons.set(random.sample(
                        self.saisons,
                        min(len(self.saisons), random.randint(1, 2))))
            else:
                # Sélection manuelle : événements explicitement listés.
                dossier.evenements.set(random.sample(
                    self.evenements,
                    min(len(self.evenements), random.randint(200, 500))))
            if self.coin(0.3):
                dossier.sources.set(random.sample(
                    self.sources, min(len(self.sources), random.randint(1, 3))))
            dossiers.append((dossier, True))

        # -- Dossiers d’œuvres -----------------------------------------------
        for _i in tqdm(range(self.n('dossiers_oeuvres')),
                       desc='dossiers d’œuvres'):
            if genres and self.coin():
                sujet = random.choice(genres).nom + 's'
            else:
                sujet = random.choice(NOMS)
            titre = random.choice(TITRES_DOSSIERS_OEUVRES).format(sujet)
            debut = self.random_date(1700, 1900)
            dossier = DossierDOeuvres(
                categorie=random.choice(self.categories),
                debut=debut,
                fin=self.random_date(debut.year, 1960),
                **self._dossier_common_kwargs(titre, used_slugs))
            dossier.save()
            self._assign_cover_image(dossier)
            dossier.editeurs_scientifiques.add(self.owner)
            if self.coin(0.6):
                # Sélection dynamique : critères de filtrage.
                dossier.genres.set(random.sample(
                    genres, min(len(genres), random.randint(1, 3))))
                dossier.lieux.set(random.sample(
                    self.villes, min(len(self.villes), random.randint(1, 2))))
                dossier.individus.set(random.sample(
                    self.individus,
                    min(len(self.individus), random.randint(1, 3))))
                if self.ensembles and self.coin():
                    dossier.ensembles.set(random.sample(
                        self.ensembles,
                        min(len(self.ensembles), random.randint(1, 2))))
            else:
                # Sélection manuelle : œuvres explicitement listées.
                dossier.oeuvres.set(random.sample(
                    self.oeuvres,
                    min(len(self.oeuvres), random.randint(200, 400))))
            if self.coin(0.3):
                dossier.sources.set(random.sample(
                    self.sources, min(len(self.sources), random.randint(1, 3))))
            dossiers.append((dossier, True))

        # -- Dossiers de sources ---------------------------------------------
        dossiers += [(d, True)
                     for d in self.create_dossiers_de_sources(used_slugs)]

        # -- Quelques dossiers imbriqués -------------------------------------
        # Un dossier contenu dans un autre ne peut pas être dans une catégorie.
        # Les dossiers parents ne conservent pas de sélection propre.
        parents = [d for d, can_parent in dossiers if can_parent]
        filter_fields = {
            'DossierDEvenements': [
                'lieux', 'oeuvres', 'individus', 'ensembles', 'saisons',
                'evenements', 'sources',
            ],
            'DossierDOeuvres': [
                'genres', 'lieux', 'individus', 'ensembles', 'oeuvres',
                'sources',
            ],
            'DossierDeSources': [
                'types', 'lieux', 'individus', 'oeuvres', 'ensembles',
                'sources',
            ],
        }
        for parent in random.sample(parents,
                                    min(len(parents), max(1, len(parents) // 3))):
            model = type(parent)
            prefixe = ('Compléments' if self.coin() else 'Annexe')
            titre = '%s : %s' % (prefixe, parent.titre)
            enfant = model(parent=parent, categorie=None,
                           **self._dossier_common_kwargs(titre, used_slugs))
            enfant.save()
            enfant.editeurs_scientifiques.add(self.owner)
            for field_name in filter_fields.get(model.__name__, []):
                getattr(parent, field_name).clear()
            if hasattr(parent, 'debut') or hasattr(parent, 'fin'):
                model.objects.filter(pk=parent.pk).update(debut=None, fin=None)
        self.dossiers = [d for d, _ in dossiers]

    def create_dossiers_de_sources(self, used_slugs):
        # Dossiers de sources : un corpus de sources sélectionnées soit
        # « dynamiquement » (par type de source, fenêtre de dates, et une
        # dimension liée : lieu, individu, œuvre ou ensemble), soit
        # « manuellement » (sources explicitement listées). Renvoie la liste
        # des dossiers créés.
        #
        # Pour la sélection dynamique, tous les critères sont combinés en ET et
        # les sources ne sont liées que parcimonieusement aux entités : on
        # dérive donc fenêtre de dates et dimension liée de sources *réelles*
        # du type choisi, ce qui garantit un résultat non vide.
        noms_types = [t.nom for t in self.types_source]
        dossiers = []
        for _i in tqdm(range(self.n('dossiers_sources')),
                       desc='dossiers de sources'):
            sujet = (random.choice(noms_types) if noms_types
                     else random.choice(NOMS))
            titre = random.choice(TITRES_DOSSIERS_SOURCES).format(sujet)
            dossier = DossierDeSources(
                categorie=random.choice(self.categories),
                **self._dossier_common_kwargs(titre, used_slugs))
            dossier.save()
            self._assign_cover_image(dossier)
            dossier.editeurs_scientifiques.add(self.owner)
            if self.coin(0.6) and self.types_source:
                # -- Sélection dynamique --------------------------------------
                types = random.sample(
                    self.types_source,
                    min(len(self.types_source), random.randint(1, 2)))
                dossier.types.set(types)
                qs = Source.objects.filter(
                    owner=self.owner, type__in=[t.pk for t in types]
                ).exclude(date__isnull=True)
                # Fenêtre de dates dérivée des dates réelles (donc non vide).
                dates = sorted(qs.values_list('date', flat=True))
                if dates and self.coin():
                    i = random.randint(0, len(dates) - 1)
                    j = random.randint(i, len(dates) - 1)
                    dossier.debut, dossier.fin = dates[i], dates[j]
                    dossier.save(update_fields=['debut', 'fin'])
                    qs = qs.filter(date__gte=dates[i], date__lte=dates[j])
                # Dimension liée supplémentaire, prise parmi les entités liées
                # aux sources déjà filtrées (type + dates).
                extra = random.choice(
                    ['lieux', 'individus', 'oeuvres', 'ensembles', None, None])
                if extra is not None:
                    extra_model = {'lieux': Lieu, 'individus': Individu,
                                   'oeuvres': Oeuvre,
                                   'ensembles': Ensemble}[extra]
                    pool = list(extra_model.objects.filter(
                        sources__in=qs).distinct()[:50])
                    if pool:
                        getattr(dossier, extra).set(random.sample(
                            pool, min(len(pool), random.randint(1, 2))))
            else:
                # -- Sélection manuelle : sources explicitement listées -------
                dossier.sources.set(random.sample(
                    self.sources,
                    min(len(self.sources), random.randint(100, 300))))
            dossiers.append(dossier)
        return dossiers

    def flush(self):
        u = self.owner
        from django.db.models import Q
        self.stdout.write('Suppression des données d’exemple existantes…')
        # Dossiers et saisons d’abord : ils référencent (en ManyToMany)
        # événements, œuvres, sources, etc. supprimés plus bas.
        DossierDEvenements.objects.filter(owner=u).delete()
        DossierDOeuvres.objects.filter(owner=u).delete()
        DossierDeSources.objects.filter(owner=u).delete()
        CategorieDeDossiers.objects.filter(owner=u).delete()
        Saison.objects.filter(owner=u).delete()
        # D’abord la correspondance (musicaLetters) : ses pages référencent des
        # individus/lieux en PROTECT, il faut donc les supprimer avant eux.
        from correspondence.models import LetterCorpus
        for corpus in LetterCorpus.objects.filter(owner=u):
            corpus.delete()  # supprime aussi les lettres (sous-arbre treebeard)
        # Suppressions en masse (``QuerySet.delete()`` au lieu d’un objet à la
        # fois), dans l’ordre des contraintes PROTECT : on supprime ce qui
        # référence avant ce qui est référencé. CASCADE et M2M sont gérés par
        # le collecteur de Django en quelques requêtes.
        ElementDeDistribution.objects.filter(
            Q(evenement__owner=u)
            | Q(element_de_programme__evenement__owner=u)).delete()
        ElementDeProgramme.objects.filter(evenement__owner=u).delete()
        Source.objects.filter(owner=u).delete()
        Evenement.objects.filter(owner=u).delete()  # PROTECT vers Lieu
        Pupitre.objects.filter(oeuvre__owner=u).delete()  # PROTECT vers Partie
        Auteur.objects.filter(oeuvre__owner=u).delete()  # PROTECT vers Individu
        Partie.objects.filter(owner=u, oeuvre__owner=u).delete()  # rôles
        Oeuvre.objects.filter(owner=u).delete()  # CASCADE sur extrait_de
        Membre.objects.filter(ensemble__owner=u).delete()
        Ensemble.objects.filter(owner=u).delete()
        Individu.objects.filter(owner=u).delete()
        Lieu.objects.filter(owner=u).delete()  # CASCADE sur parent

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

        self._fetch_cover_images()

        with search_indexing_disabled():
            self.create_lieux()
            self.create_individus()
            self.create_ensembles()
            self.create_saisons()
            self.create_oeuvres()
            self.create_evenements()
            self.create_sources()
            self.create_dossiers()

        # Étape « correspondance » : peuple le sous-site musicaLetters en
        # réutilisant la commande sœur (mêmes propriétaire, échelle et options),
        # si elle est disponible.
        if 'generate_sample_letters' in get_commands():
            call_command('generate_sample_letters', scale=self.scale,
                         seed=options['seed'], flush=options['flush'])
        else:
            self.stdout.write(self.style.WARNING(
                'Commande « generate_sample_letters » introuvable : '
                'étape « correspondance » ignorée.'))

        self.stdout.write(self.style.SUCCESS(
            'Données d’exemple créées : '
            '%d lieux, %d individus, %d ensembles, %d saisons, %d œuvres, '
            '%d événements, %d sources (dont %d images et %d livres en '
            'bibliothèque), %d dossiers (%d d’événements, %d d’œuvres, '
            '%d de sources).' % (
                Lieu.objects.filter(owner=self.owner).count(),
                len(self.individus), len(self.ensembles), len(self.saisons),
                len(self.oeuvres), len(self.evenements),
                Source.objects.filter(owner=self.owner).count(),
                Source.objects.filter(
                    owner=self.owner,
                    type_fichier=FileAnalyzer.IMAGE).count(),
                len(self.livres),
                DossierDEvenements.objects.filter(owner=self.owner).count()
                + DossierDOeuvres.objects.filter(owner=self.owner).count()
                + DossierDeSources.objects.filter(owner=self.owner).count(),
                DossierDEvenements.objects.filter(owner=self.owner).count(),
                DossierDOeuvres.objects.filter(owner=self.owner).count(),
                DossierDeSources.objects.filter(owner=self.owner).count())))
        self.stdout.write(
            'Pensez à lancer « ./manage.py update_index » pour rendre '
            'la recherche et l’autocomplétion cohérentes.')
