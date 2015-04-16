# coding: utf-8

from __future__ import unicode_literals
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from exporter import Exporter, exporter_registry

from .models import *


class CommonModelExporter(Exporter):
    columns = ('owner',)
    RENDU = _('rendu')

    def __init__(self, queryset=None):
        super(CommonModelExporter, self).__init__(queryset)
        self.verbose_overrides['owner'] = self.get_field('owner').verbose_name
        for s in self.columns:
            suffix = '_str'
            if s.endswith(suffix):
                self.verbose_overrides[s] = self.get_verbose_name(
                    s.split(suffix)[0]) + ' (%s)' % force_text(self.RENDU)
            elif '__' in s:
                self.verbose_overrides[s] = self.fields[s].verbose_name

    @staticmethod
    def get_owner(obj):
        if obj.owner is None:
            return ''
        return force_text(obj.owner)

PUBLISHED_MODEL_COLUMNS = CommonModelExporter.columns + ('etat__nom',)
AUTORITE_MODEL_COLUMNS = \
    PUBLISHED_MODEL_COLUMNS + ('notes_publiques', 'notes_privees')


class RenduExporter(CommonModelExporter):

    def __init__(self, queryset=None):
        super(RenduExporter, self).__init__(queryset)
        self.verbose_overrides['rendu'] = self.RENDU

    @staticmethod
    def get_rendu(obj):
        return force_text(obj)


@exporter_registry.add
class LieuExporter(RenduExporter):
    model = Lieu
    columns = (
        'id', 'rendu', 'nom', 'parent__id', 'nature__nom', 'historique',
        'longitude', 'latitude', 'code_postal', 'type_de_scene',
    ) + AUTORITE_MODEL_COLUMNS
    verbose_overrides = {
        'parent__id': _('ID parent'),
        'longitude': _('longitude'),
        'latitude': _('latitude'),
    }

    @staticmethod
    def get_nature_str(obj):
        return force_text(obj.nature)

    @staticmethod
    def get_longitude(obj):
        if obj.geometry is None or obj.geometry.geom_type != 'Point':
            return
        return obj.geometry.coords[0]

    @staticmethod
    def get_latitude(obj):
        if obj.geometry is None or obj.geometry.geom_type != 'Point':
            return
        return obj.geometry.coords[1]


@exporter_registry.add
class EnsembleExporter(RenduExporter):
    model = Ensemble
    columns = ('id', 'rendu', 'particule_nom', 'nom', 'type__nom', 'siege',
               'siege_str') + AUTORITE_MODEL_COLUMNS

    @staticmethod
    def get_siege_str(obj):
        if obj.siege:
            return force_text(obj.siege)


@exporter_registry.add
class IndividusProfessionsExporter(Exporter):
    model = Individu.professions.through
    columns = ('individu', 'profession__nom')

    def get_verbose_table_name(self):
        return 'individus ↔ professions'


@exporter_registry.add
class ParenteDIndividuExporter(CommonModelExporter):
    model = ParenteDIndividus
    columns = ('parent', 'enfant', 'type__nom') + CommonModelExporter.columns


@exporter_registry.add
class ProfessionExporter(CommonModelExporter):
    model = Profession
    columns = ('id', 'nom', 'nom_pluriel', 'nom_feminin', 'parent__id',
               'classement') + AUTORITE_MODEL_COLUMNS


@exporter_registry.add
class IndividuExporter(RenduExporter):
    model = Individu
    columns = (
        'id', 'rendu', 'professions_str',
        'particule_nom', 'nom', 'particule_nom_naissance', 'nom_naissance',
        'prenoms', 'prenoms_complets', 'pseudonyme', 'titre',
        'naissance_date', 'naissance_date_approx', 'naissance_lieu',
        'naissance_lieu_str', 'naissance_lieu_approx', 'deces_date',
        'deces_date_approx', 'deces_lieu', 'deces_lieu_str',
        'deces_lieu_approx', 'biographie', 'isni') + AUTORITE_MODEL_COLUMNS
    m2ms = ('professions', 'parents')
    verbose_overrides = {
        'naissance_lieu': _('lieu de naissance'),
        'deces_lieu': _('lieu de décès'), 'deces_date': _('date de décès'),
        'naissance_date': _('date de naissance'),
        'naissance_lieu_approx': _('lieu de naissance (approximatif)'),
        'deces_lieu_approx': _('lieu de décès (approximatif)'),
        'naissance_date_approx': _('date de naissance (approximative)'),
        'deces_date_approx': _('date de décès (approximative)'),
    }

    @staticmethod
    def get_naissance_lieu_str(obj):
        return obj.naissance.lieu_str(tags=False)

    @staticmethod
    def get_deces_lieu_str(obj):
        return obj.deces.lieu_str(tags=False)

    @staticmethod
    def get_professions_str(obj):
        return obj.calc_professions(tags=False)


@exporter_registry.add
class AuteurExporter(CommonModelExporter):
    model = Auteur
    columns = ('id', 'oeuvre', 'source', 'individu', 'profession__nom')


@exporter_registry.add
class PartieProfessionsExporter(Exporter):
    model = Partie.professions.through
    columns = ('partie', 'profession__nom')

    def get_verbose_table_name(self):
        return 'partie ↔ professions'


@exporter_registry.add
class PartieExporter(CommonModelExporter):
    model = Partie
    columns = ('id', 'nom', 'nom_pluriel', 'professions_str', 'parent__id',
               'classement') + AUTORITE_MODEL_COLUMNS
    m2ms = ('professions',)

    @staticmethod
    def get_professions_str(obj):
        return ', '.join([force_text(o) for o in obj.professions.all()])


@exporter_registry.add
class PupitreExporter(CommonModelExporter):
    model = Pupitre
    columns = ('id', 'partie__nom', 'soliste', 'quantite_min', 'quantite_max')


@exporter_registry.add
class OeuvreExporter(RenduExporter):
    model = Oeuvre
    columns = (
        'id', 'rendu', 'auteurs_str', 'pupitres_str', 'prefixe_titre', 'titre',
        'coordination', 'prefixe_titre_secondaire', 'titre_secondaire',
        'genre__nom', 'coupe', 'numero', 'tempo', 'tonalite', 'sujet', 'surnom',
        'incipit', 'nom_courant', 'extrait_de__id', 'type_extrait',
        'numero_extrait', 'creation_date', 'creation_date_approx',
        'creation_heure', 'creation_heure_approx', 'creation_lieu',
        'creation_lieu_str', 'creation_lieu_approx') + AUTORITE_MODEL_COLUMNS
    m2ms = ('auteurs', 'pupitres', 'meres')
    verbose_overrides = {
        'prefixe_titre_secondaire': 'article (2)',
        'creation_date': _('date de création'),
        'creation_date_approx': _('date de création (approximative)'),
        'creation_heure': _('heure de création'),
        'creation_heure_approx': _('heure de création (approximative)'),
        'creation_lieu': _('lieu de création'),
        'creation_lieu_approx': _('lieu de création (approximatif)'),
    }

    @staticmethod
    def get_auteurs_str(obj):
        return obj.auteurs_html(tags=False)

    @staticmethod
    def get_pupitres_str(obj):
        return obj.get_pupitres_str(prefix=False)

    @staticmethod
    def get_creation_lieu_str(obj):
        return obj.creation.lieu_str(tags=False)


@exporter_registry.add
class SourcesEvenementsExporter(Exporter):
    model = Source.evenements.through

    def get_verbose_table_name(self):
        return 'sources ↔ evenements'


@exporter_registry.add
class SourcesOeuvresExporter(Exporter):
    model = Source.oeuvres.through

    def get_verbose_table_name(self):
        return 'sources ↔ œuvres'


@exporter_registry.add
class SourcesIndividusExporter(Exporter):
    model = Source.individus.through

    def get_verbose_table_name(self):
        return 'sources ↔ individus'


@exporter_registry.add
class SourcesEnsemblesExporter(Exporter):
    model = Source.ensembles.through

    def get_verbose_table_name(self):
        return 'sources ↔ ensembles'


@exporter_registry.add
class SourcesLieuxExporter(Exporter):
    model = Source.lieux.through

    def get_verbose_table_name(self):
        return 'sources ↔ lieux'


@exporter_registry.add
class SourcesPartiesExporter(Exporter):
    model = Source.parties.through

    def get_verbose_table_name(self):
        return 'sources ↔ parties'


@exporter_registry.add
class SourceExporter(CommonModelExporter):
    model = Source
    columns = (
        'id', 'type__nom', 'titre', 'legende', 'date', 'date_approx',
        'numero', 'folio', 'page', 'lieu_conservation', 'cote', 'url'
    ) + AUTORITE_MODEL_COLUMNS
    m2ms = ('evenements', 'oeuvres', 'individus', 'ensembles', 'lieux',
            'parties')


@exporter_registry.add
class ElementDeDistribution(CommonModelExporter):
    model = ElementDeDistribution
    columns = ('id', 'evenement', 'evenement_str',
               'individu', 'individu_str', 'ensemble', 'ensemble_str',
               'partie__nom', 'profession__nom') + CommonModelExporter.columns

    @staticmethod
    def get_evenement_str(obj):
        if obj.evenement:
            return force_text(obj.evenement)

    @staticmethod
    def get_individu_str(obj):
        if obj.individu:
            return force_text(obj.individu)

    @staticmethod
    def get_ensemble_str(obj):
        if obj.ensemble:
            return force_text(obj.ensemble)


@exporter_registry.add
class CaracteristiqueExporter(CommonModelExporter):
    model = Caracteristique
    columns = ('id', 'type__nom', 'valeur', 'classement')


@exporter_registry.add
class CaracteristiqueDeProgrammeExporter(CaracteristiqueExporter):
    model = CaracteristiqueDeProgramme


@exporter_registry.add
class ProgrammeCaracteristiquesExporter(Exporter):
    model = ElementDeProgramme.caracteristiques.through

    def get_verbose_table_name(self):
        return 'programme ↔ caractéristiques'


@exporter_registry.add
class ProgrammeDistribution(Exporter):
    model = ElementDeProgramme.distribution.through

    def get_verbose_table_name(self):
        return 'programme ↔ distribution'


@exporter_registry.add
class ElementDeProgrammeExporter(CommonModelExporter):
    model = ElementDeProgramme
    columns = ('id', 'evenement', 'evenement_str', 'oeuvre', 'oeuvre_str',
               'autre', 'caracteristiques_str', 'distribution_str',
               'numerotation', 'position', 'part_d_auteur')\
        + CommonModelExporter.columns
    m2ms = ('caracteristiques', 'distribution')

    @staticmethod
    def get_evenement_str(obj):
        if obj.evenement:
            return force_text(obj.evenement)

    @staticmethod
    def get_oeuvre_str(obj):
        if obj.oeuvre:
            return force_text(obj.oeuvre)

    @staticmethod
    def get_caracteristiques_str(obj):
        return obj.calc_caracteristiques()

    @staticmethod
    def get_distribution_str(obj):
        return ', '.join([force_text(o) for o in obj.distribution.all()])

    @staticmethod
    def get_personnels_str(obj):
        return ', '.join([force_text(o) for o in obj.personnels.all()])


@exporter_registry.add
class EvenementExporter(CommonModelExporter):
    model = Evenement
    columns = (
        'id', 'debut_date', 'debut_date_approx', 'debut_heure',
        'debut_heure_approx', 'debut_lieu', 'debut_lieu_str',
        'debut_lieu_approx', 'fin_date', 'fin_date_approx', 'fin_heure',
        'fin_heure_approx', 'fin_lieu', 'fin_lieu_str', 'fin_lieu_approx',
        'exoneres', 'payantes', 'frequentation', 'scolaires', 'jauge',
        'recette_generale', 'recette_par_billets', 'code_programme',
    ) + AUTORITE_MODEL_COLUMNS
    m2ms = ('programme', 'distribution')
    verbose_overrides = {
        'debut_date': 'date de début', 'debut_heure': 'heure de début',
        'debut_date_approx': 'date de début (approximative)',
        'debut_heure_approx': 'heure de début (approximative)',
        'fin_date': 'date de fin', 'fin_heure': 'heure de fin',
        'fin_date_approx': 'date de fin (approximative)',
        'fin_heure_approx': 'heure de fin (approximative)',
        'debut_lieu': 'lieu de début', 'fin_lieu': 'lieu de fin',
        'debut_lieu_approx': 'date de début (approximatif)',
        'fin_lieu_approx': 'date de fin (approximatif)',
    }

    @staticmethod
    def get_debut_lieu_str(obj):
        return obj.debut.lieu_str(tags=False)

    @staticmethod
    def get_fin_lieu_str(obj):
        return obj.fin.lieu_str(tags=False)