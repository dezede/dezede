# coding: utf-8

from __future__ import unicode_literals
from django.utils.encoding import force_text

from exporter import Exporter, exporter_registry

from .models import Lieu, ElementDeProgramme, Evenement, Oeuvre, Individu


@exporter_registry.add
class LieuExporter(Exporter):
    model = Lieu
    columns = (
        'id', 'nom', 'parent', 'parent__nom', 'nature__nom', 'code_postal',
        'geometry', 'historique',
        'notes_publiques', 'notes_privees', 'etat__nom', 'owner'
    )
    verbose_overrides = {
        'parent': 'ID parent', 'parent__nom': 'nom du parent',
        'geometry': 'coordonnées GPS', 'owner': 'propriétaire',
    }

    @staticmethod
    def get_geometry(obj):
        if obj.geometry is None:
            return
        return force_text(obj.geometry)

    @staticmethod
    def get_owner(obj):
        return force_text(obj.owner)


TITRES = dict(Individu.TITRES)


@exporter_registry.add
class IndividuExporter(Exporter):
    model = Individu
    columns = (
        'id', 'particule_nom', 'nom', 'particule_nom_naissance',
        'nom_naissance', 'prenoms', 'prenoms_complets', 'pseudonyme', 'titre',
        'naissance', 'deces', 'professions', 'isni',
        'notes_publiques', 'notes_privees', 'etat__nom', 'owner',
    )
    verbose_overrides = {
        'evenement__etat__nom': 'état',
        'evenement__owner': 'propriétaire',
    }

    @staticmethod
    def get_titre(obj):
        return force_text(TITRES.get(obj.titre, ''))

    @staticmethod
    def get_naissance(obj):
        return obj.naissance.html(tags=False)

    @staticmethod
    def get_deces(obj):
        return obj.deces.html(tags=False)

    @staticmethod
    def get_professions(obj):
        return obj.calc_professions(tags=False)

    @staticmethod
    def get_owner(obj):
        return force_text(obj.owner)


@exporter_registry.add
class OeuvreExporter(Exporter):
    model = Oeuvre
    columns = (
        'id', 'str', 'genre__nom', 'coupe', 'numero', 'opus', 'tonalite',
        'surnom', 'incipit', 'nom_courant', 'caracteristiques', 'auteurs',
        'pupitres', 'creation',
        'notes_publiques', 'notes_privees', 'etat__nom', 'owner',
    )
    verbose_overrides = {
        'str': 'nom',
        'caracteristiques': 'autres caractéristiques',
        'etat__nom': 'état',
        'owner': 'propriétaire', 'creation': 'création',
    }

    @staticmethod
    def get_str(obj):
        return force_text(obj)

    @staticmethod
    def get_caracteristiques(obj):
        return obj.caracteristiques_html(tags=False)

    @staticmethod
    def get_auteurs(obj):
        return obj.auteurs_html(tags=False)

    @staticmethod
    def get_pupitres(obj):
        return obj.pupitres_html(tags=False)

    @staticmethod
    def get_owner(obj):
        return force_text(obj.owner)

    @staticmethod
    def get_creation(obj):
        return obj.creation.html(tags=False)


@exporter_registry.add
class ElementDeProgrammeExporter(Exporter):
    model = ElementDeProgramme
    columns = (
        'evenement', 'evenement__debut_date', 'evenement__debut_heure',
        'evenement__debut_lieu', 'evenement__debut_lieu__nom',
        'auteurs', 'oeuvre', 'distribution', 'distribution_generale',
        'evenement__code_programme', 'evenement__notes_publiques',
        'evenement__notes_privees', 'evenement__etat__nom',
        'evenement__owner',
    )
    verbose_overrides = {
        'evenement': 'ID',
        'evenement__debut_date': 'date',
        'evenement__debut_heure': 'heure',
        'evenement__debut_lieu': 'ID lieu',
        'evenement__debut_lieu__nom': 'nom du lieu',
        'distribution_generale': 'distribution générale de l’événement',
        'oeuvre': 'œuvre',
        'distribution': 'distribution de l’œuvre',
        'evenement__code_programme': 'code du programme',
        'evenement__notes_publiques': 'notes publiques',
        'evenement__notes_privees': 'notes privées',
        'evenement__etat__nom': 'état',
        'evenement__owner': 'propriétaire',
    }

    @staticmethod
    def get_auteurs(obj):
        if obj.oeuvre is None:
            return
        return obj.oeuvre.auteurs.html(tags=False)

    @staticmethod
    def get_oeuvre(obj):
        return force_text(obj.oeuvre)

    @staticmethod
    def get_distribution_generale(obj):
        return obj.evenement.distribution.html(tags=False)

    @staticmethod
    def get_distribution(obj):
        return obj.distribution.html(tags=False)

    @staticmethod
    def get_evenement__owner(obj):
        return force_text(obj.evenement.owner)


@exporter_registry.add
class EvenementExporter(Exporter):
    model = Evenement
    columns = (
        'id', 'debut_date', 'debut_heure', 'debut_lieu', 'debut_lieu__nom',
        'programme', 'code_programme', 'distribution',
        'exoneres', 'payantes', 'frequentation', 'scolaires', 'jauge',
        'recette_generale', 'recette_par_billets',
        'notes_publiques', 'notes_privees', 'etat__nom', 'owner',
    )
    verbose_overrides = {
        'debut_lieu': 'ID lieu',
        'debut_lieu__nom': 'nom du lieu',
        'owner': 'propriétaire',
    }

    @staticmethod
    def get_programme(obj):
        return '\n'.join([el.html(tags=False) for el in obj.programme.all()])

    @staticmethod
    def get_distribution(obj):
        return obj.distribution.html(tags=False)

    @staticmethod
    def get_owner(obj):
        return force_text(obj.owner)

