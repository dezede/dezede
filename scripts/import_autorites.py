# coding: utf-8

import csv, re, os.path, os
from django.template.defaultfilters import title
from django.contrib.contenttypes.models import ContentType
from catalogue.models import Oeuvre, Prenom, Individu, Auteur, Profession, \
    AncrageSpatioTemporel, GenreDOeuvre, TypeDeCaracteristiqueDOeuvre, \
    CaracteristiqueDOeuvre
from django.utils.encoding import smart_unicode


CURRENT_PATH = os.path.dirname(__file__)

DATA_PATH = os.path.join(CURRENT_PATH, 'data')

TITRE_RE = re.compile(r'^([^\(]+)\s+\(([^\)]+)\)$')
INDIVIDU_FULL_RE = re.compile(r'^([^,]+),\s+([^\(]+)\s+\(([^\)]+)\)$')
PSEUDONYME_RE = re.compile(r'^([^,]+),?\s+dit\s+([^\)]+)$')

def split_titre(titre):
    particule = ''
    match = TITRE_RE.match(titre)
    if match:
        particule = match.group(2)
        titre = match.group(1)
        if particule[-1] not in "'’":
            particule += ' '
    return particule, titre


def split_individus(individus):
    return individus.split(' ; ')


def notify(msg):
    os.system('notify-send "%s"' % msg)


def ask_for_choice(object, k, v, new_v):
    intro = 'Deux possibilités pour le champ %s de %s.' % (k, object)
    notify(intro)
    print intro
    print '1. %s (valeur actuelle)' % v
    print '2. %s (valeur importable)' % new_v
    return raw_input('Que choisir ? (par défaut 2) ')


def update_or_create(Model, unique_keys, **kwargs):
    unique_kwargs = {k: kwargs[k] for k in unique_keys}
    try:
        object = Model.objects.get(**unique_kwargs)
    except Model.DoesNotExist:
        return Model.objects.create(**kwargs)
    changed_kwargs = {k: smart_unicode(v) for k, v in kwargs.items()
                                    if getattr(object, k) != smart_unicode(v)}
    if not changed_kwargs:
        return object
    for k, new_v in changed_kwargs.items():
        v = getattr(object, k)
        if v:
            setattr(object, k, new_v)
        else:
            while True:
                choice = ask_for_choice(object, k, v, new_v)
                if choice in ('2', ''):
                    setattr(object, k, new_v)
                    break
                elif choice == '1':
                    break
    object.save()
    return object


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
        individu = update_or_create(Individu, ['nom', 'ancrage_naissance'],
                                    nom=nom, pseudonyme=pseudonyme,
                                    ancrage_naissance=naissance,
                                    ancrage_deces=deces)
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


exceptions = []


def print_exception(i, titre):
    print 'Exception sur la %se ligne (œuvre %s)' % (i, titre)


def import_oeuvre(i, oeuvre, bindings):
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
        for profession, profession_pluriel, auteurs_key in bindings['auteurs']:
            auteurs = oeuvre[auteurs_key]
            build_auteurs(oeuvre_obj, auteurs, profession, profession_pluriel)
        genre = GenreDOeuvre.objects.get_or_create(
                                              nom=oeuvre[bindings['genre']])[0]
        oeuvre_obj.genre = genre
        for type_nom, type_nom_pluriel, caracteristique_key \
                                               in bindings['caracteristiques']:
            type = TypeDeCaracteristiqueDOeuvre.objects.get_or_create(
                                 nom=type_nom, nom_pluriel=type_nom_pluriel)[0]
            caracteristique = CaracteristiqueDOeuvre.objects.get_or_create(
                              type=type, valeur=oeuvre[caracteristique_key])[0]
            oeuvre_obj.caracteristiques.add(caracteristique)
        oeuvre_obj.save()
        print oeuvre_obj
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        print_exception(i, titre)
        exceptions.append([i, titre])


def import_csv_file(csv_filename, bindings):
    csv_file = open(os.path.join(DATA_PATH, csv_filename))
    oeuvres = list(csv.DictReader(csv_file))
    for i, oeuvre in enumerate(oeuvres):
        import_oeuvre(i, oeuvre, bindings)


def run():
    bindings = {
        'titre': 'Titres principaux',
        'titre_secondaire': 'Titres secondaires',
        'auteurs': [['compositeur', 'compositeurs', 'Compositeurs'],
                    ['librettiste', 'librettistes', 'Librettistes']],
        'genre': 'Genres',
        'caracteristiques': [['découpage', 'découpages', 'Actes']],
    }
    import_csv_file('{# destroyed from git history #}.csv', bindings)

    bindings = {
        'titre': 'TP',
        'titre_secondaire': 'TS',
        'auteurs': [['compositeur', 'compositeurs',
                     'Compositeur'],
                    ['librettiste', 'librettistes',
                     'Librettiste'],
                    ['auteur dramatique', 'auteurs dramatiques',
                     'Auteur dramatique'],
                    ['adaptateur', 'adaptateurs', 'Adaptateur']],
        'genre': 'Genre',
        'caracteristiques': [['découpage', 'découpages', 'Acte']],
    }
    import_csv_file('{# destroyed from git history #}.csv', bindings)

    print '\nRécapitulatif des exceptions :'
    for i, titre in exceptions:
        print_exception(i, titre)
