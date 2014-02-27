# coding: utf-8

from __future__ import unicode_literals
import socket
import re
import warnings

from bs4 import BeautifulSoup
import dateutil.parser
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.transaction import commit_on_success
from django.utils.encoding import force_text
from django.test.client import Client
# from IPython.display import display, HTML
import requests
from libretto.api.models.utils import update_or_create, KEEP
from libretto.models import Etat, Individu, Prenom, Profession, Instrument, \
    Pupitre, Oeuvre, Auteur, ElementDeDistribution, ElementDeProgramme, \
    NatureDeLieu, Lieu, AncrageSpatioTemporel, Evenement


cache.clear()

url = 'http://serveur.ensembleinter.com/oai'


etat = update_or_create(Etat, dict(
            nom='importé(e) automatiquement',
            nom_pluriel='importé(e)s automatiquement',
            message='<p>Les données ci-dessous ont été importées '
                    'automatiquement et sont en attente de relecture.',
            public=False), unique_keys=('nom',))


def request(*args, **kwargs):
    while True:
        try:
            r = requests.get(*args, **kwargs)
        except socket.error:
            pass
        else:
            break
    if r.status_code != 200:
        raise Exception('%d error' % r.status_code)
    return r


def get_identifiers():
    r = request(url, params={'verb': 'ListIdentifiers',
                             'set': 'concerts',
                             'metadataPrefix': 'mods'})
    soup = BeautifulSoup(r.text, 'xml')
    return [t.string for t in soup.ListIdentifiers.find_all('identifier')]


def get_data(identifier):
    r = request(url, params={'verb': 'GetRecord',
                             'identifier': identifier,
                             'metadataPrefix': 'mods'})
    soup = BeautifulSoup(r.text, 'xml')
    records = soup.GetRecord.find_all('record')
    assert len(records) == 1, 'There should be only one record'
    record = records[0]
    return record.metadata.mods


class ParseTag(object):
    def __init__(self, bs_tag):
        self.bs_tag = bs_tag

    def __enter__(self):
        return self.bs_tag

    def __exit__(self, type, value, traceback):
        if type is not None:
            raise
        contents = [content for content in self.bs_tag.contents
                    if force_text(content).strip()]
        assert not contents, '"%s" should be empty but this was found: %s' % (self.bs_tag.name, contents)
        self.bs_tag.extract()


NOM_COMPLET_RE = re.compile(r'^(?P<nom>.+),\s+(?P<prenom>.+)$')


def parse_individu(nom_complet):
    match = NOM_COMPLET_RE.match(nom_complet)
    if match is None:
        warnings.warn('Unable to parse "%s"' % repr(nom_complet))
        individu = update_or_create(Individu, dict(nom=nom_complet, etat=etat),
                                    unique_keys=('nom',))
    else:
        nom = match.group('nom')
        try:
            prenom = Prenom.objects.filter(prenom=match.group('prenom'))[0]
        except IndexError:
            prenom = Prenom.objects.create(prenom=match.group('prenom'))
        individu = update_or_create(Individu, dict(nom=nom.title(), prenoms=(prenom,), etat=etat),
                                    unique_keys=('nom', 'prenoms__prenom'), conflict_handling=KEEP)
    return individu


def parse_profession(role_tag):
    with ParseTag(role_tag) as role:
        nom = role.roleTerm.extract().string
        profession = Profession.objects.get_or_create(nom=nom.lower(), defaults={'etat': etat})[0]
    return profession


def parse_pupitre(role_tag):
    with ParseTag(role_tag) as role:
        nom = role.roleTerm.extract().string
        instrument = Instrument.objects.get_or_create(nom=nom.lower(), defaults={'etat': etat})[0]
        pupitre = Pupitre.objects.create(partie=instrument)
    return pupitre


build_group = lambda n: r'(?:\.|\s)'.join([r'(\d+)'] * n)
DANIELS_RE = re.compile(
    r'^%s$' % ur'\s*(?:-|—|//)\s*'.join([build_group(5), build_group(4),
                                         build_group(3), build_group(5)]))


def parse_nomenclature(nomenclature_tag):  # TODO: finir de traiter les nomenclatures.
    with ParseTag(nomenclature_tag) as nomenclature:
        nomenclature.olees.extract()  # TODO: traiter olees ?
        daniels = nomenclature.daniels.extract().string
        if daniels is None:
            return
        assert DANIELS_RE.match(daniels) is not None, 'Unable to parse %s' % repr(daniels or '')


def parse_oeuvre(titleInfo):
    with ParseTag(titleInfo) as oeuvre_data:
        titre = oeuvre_data.title.extract().string
        titre_secondaire = oeuvre_data.subTitle.extract().string or ''  # TODO: Faire quelque chose de ceci.
        oeuvre = update_or_create(Oeuvre, dict(titre=titre, etat=etat), unique_keys=('titre',))
        oeuvre_data.nomenclature.extract()  # TODO: traiter les nomenclatures.
        #parse_nomenclature(oeuvre_data.nomenclature)
    return oeuvre


def parse_participant(evenement, oeuvre, individu_tag):
    with ParseTag(individu_tag):
        nom_complet = individu_tag.namePart.extract().string
        individu = parse_individu(nom_complet)
        if individu_tag.role.roleTerm.string.lower() == 'compositeur':
            profession = parse_profession(individu_tag.role)
            Auteur.objects.get_or_create(
                individu=individu, profession=profession,
                content_type=ContentType.objects.get_for_model(Oeuvre),
                object_id=oeuvre.pk)[0]
        else:
            pupitre = parse_pupitre(individu_tag.role)
            element_de_distribution = ElementDeDistribution.objects.create(pupitre=pupitre)
            element_de_distribution.individus.add(individu)
            return element_de_distribution


def parse_element_de_programme(evenement, i, item):
    oeuvre = parse_oeuvre(item.titleInfo)
    distribution = []
    individu_tags = item.find_all('name', type='personal')
    for individu_tag in individu_tags:
        element_de_distribution = parse_participant(evenement, oeuvre, individu_tag)
        if element_de_distribution is not None:
            distribution.append(element_de_distribution)
    element_de_programme = ElementDeProgramme.objects.create(
        evenement=evenement, position=i,
        oeuvre=oeuvre, etat=etat)
    element_de_programme.distribution.add(*distribution)
    return element_de_programme


def parse_programme(evenement, data):
    programme = data.find_all('relatedItem', type='constituent', recursive=False)
    for i, item in enumerate(programme, start=1):
        parse_element_de_programme(evenement, i, item)


def parse_place(place_tag):
    with ParseTag(place_tag) as place:
        nom_lieu = place.placeTerm.extract().string
        salle = NatureDeLieu.objects.get_or_create(nom='salle', defaults={'etat': etat})[0]
        lieu = Lieu.objects.get_or_create(nom=nom_lieu, nature=salle, defaults={'etat': etat})[0]
        # TODO: traiter tout ce qui suit :
        place.typeLieu.extract()
        place.presentation.extract()
        place.public.extract()
        place.jauge.extract()
    return lieu


def parse_evenement_meta(data):
    with ParseTag(data.originInfo) as metadata:
        metadata.programme.extract()  # TODO: traiter les typologies d'événements.
        lieu = parse_place(metadata.place)
        datetime = dateutil.parser.parse(metadata.dateOther.extract().string)
        ancrage = AncrageSpatioTemporel.objects.create(
            lieu=lieu, date=datetime.date(), heure=datetime.time())
        evenement = Evenement.objects.create(ancrage_debut=ancrage, relache=False, etat=etat)
    return evenement


commit_on_success()
def create_events():
    # c = Client()
    for identifier in get_identifiers():
        f = open('mapping_eic_dezede.txt', 'a')
        print(identifier)
        try:
            with commit_on_success():
                data = get_data(identifier)
                evenement = parse_evenement_meta(data)
                f.write('%s %s\n' % (evenement.pk, identifier))
                parse_programme(evenement, data)
                # r = c.get(reverse('evenement_pk', args=(evenement.pk,)))
                # evenement_html = BeautifulSoup(r.content).section
                # evenement_html.find(class_='btn-toolbar').extract()
                # display(HTML(force_text(evenement_html)))
        except:
            print('Erreur inattendue, on saute cet événement')
            f.write('%s %s\n' % (None, identifier))
        f.close()


create_events()
