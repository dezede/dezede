# coding: utf-8

import csv, re, os.path, os, sys
from django.template.defaultfilters import title
from django.contrib.contenttypes.models import ContentType
from catalogue.models import Oeuvre, Prenom, Individu, Auteur, Profession, \
    AncrageSpatioTemporel, GenreDOeuvre, TypeDeCaracteristiqueDOeuvre, \
    CaracteristiqueDOeuvre, Lieu, NatureDeLieu
from django.utils.encoding import smart_unicode
from datetime import datetime
from catalogue.templatetags.extras import multiword_replace
from .routines import colored_print


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


def notify_send(msg):
    os.system('notify-send "%s"' % msg)


def ask_for_choice(object, k, v, new_v):
    intro = 'Deux possibilités pour le champ %s de %s.' % (k, object)
    notify_send(intro)
    colored_print(intro, 'yellow')
    colored_print('1. %s (valeur actuelle)' % v, 'yellow')
    colored_print('2. %s (valeur importable)' % new_v, 'yellow')
    colored_print('3. Créer un nouvel objet', 'yellow')
    return raw_input('Que faire ? (par défaut 2) ')


def update_or_create(Model, unique_keys, **kwargs):
    unique_kwargs = {k: kwargs[k] for k in unique_keys}
    try:
        object = Model.objects.get(**unique_kwargs)
    except Model.DoesNotExist:
        return Model.objects.create(**kwargs)
    changed_kwargs = {k: smart_unicode(v) if isinstance(v, str or unicode)
                                          else v for k, v in kwargs.items()
                      if smart_unicode(getattr(object, k)) != smart_unicode(v)}
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
                elif choice == '3':
                    return Model.objects.create(**kwargs)
                elif choice == '1':
                    break
    object.save()
    return object


def build_individu(individu_str):
    match = INDIVIDU_FULL_RE.match(individu_str)
    if match:
        nom = title(match.group('nom'))
        pseudonyme = ''
        prenom = match.group('prenoms')
        dates = match.group('dates')
        match_pseudonyme = PSEUDONYME_RE.match(prenom)
        if match_pseudonyme:
            prenom = match_pseudonyme.group('prenoms')
            pseudonyme = match_pseudonyme.group('pseudonyme')
        prenom = Prenom.objects.get_or_create(prenom=prenom)[0]

        naissance, deces = dates.split('-')
        i = Individu.objects.filter(nom=nom, prenoms=prenom,
                                    pseudonyme=pseudonyme,
                                    ancrage_naissance__date_approx=naissance,
                                    ancrage_deces__date_approx=deces)
        if i.exists():
            assert len(i) == 1
            return i[0]
        ancrage_naissance = AncrageSpatioTemporel.objects.create(
                                                         date_approx=naissance)
        ancrage_deces = AncrageSpatioTemporel.objects.create(date_approx=deces)
        individu = update_or_create(Individu, ['nom'],
                                    nom=nom, pseudonyme=pseudonyme,
                                    ancrage_naissance=ancrage_naissance,
                                    ancrage_deces=ancrage_deces)
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
        aut = Auteur.objects.get_or_create(profession=profession,
                                           individu=individu,
                                           content_type=Oeuvre_cti,
                                           object_id=oeuvre_obj.id)[0]
        aut.clean()


def build_ancrage(str, bindings):
    ancrage_re = bindings['creation'][1]
    match = ancrage_re.match(str)
    lieux = [l.strip() for l in match.group('lieux').split(',') if l]
    assert 1 <= len(lieux) <= 3
    nature_noms = ['ville', 'institution', 'salle']
    natures = [NatureDeLieu.objects.get_or_create(nom=s)[0]
                                                          for s in nature_noms]
    lieu = None
    for i, lieu_nom in enumerate(lieux):
        lieu = update_or_create(Lieu, ['nom'], nom=lieu_nom, nature=natures[i],
                                parent=lieu)
    date_str = match.group('date')
    try:
        date = datetime.strptime(date_str, '%d/%I/%Y')
    except ValueError:
        date_str = multiword_replace(date_str, {
            'janvier': 'January', 'février': 'February', 'mars': 'March',
            'avril': 'April', 'mai': 'May', 'juin': 'June', 'juillet': 'July',
            'août': 'August', 'septembre': 'September', 'octobre': 'October',
            'novembre': 'November', 'décembre': 'December'})
        date = datetime.strptime(date_str, '%d %B %Y')
    return AncrageSpatioTemporel.objects.get_or_create(lieu=lieu, date=date)[0]


exceptions = []


def print_exception(i, titre, e, notify=False):
    msg = 'Exception sur la %se ligne (œuvre %s) : %s' % (i, titre, e)
    if notify:
        notify_send(msg)
    colored_print(msg)


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
                oeuvre_obj.ancrage_creation = build_ancrage(creation_str, bindings)
            except:
                colored_print('Impossible de parser la création de « %s »'
                              % oeuvre_obj)
        # [Sauvegarde] :
        oeuvre_obj.save()
        colored_print(oeuvre_obj, 'green')
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
