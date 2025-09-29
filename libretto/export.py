from django.db.models.constants import LOOKUP_SEP
from django.utils.translation import gettext_lazy as _

from exporter.base import Exporter
from exporter.registry import exporter_registry

from .models import *


class CommonModelExporter(Exporter):
    RENDU = _('rendu')

    def __init__(self, queryset=None):
        super(CommonModelExporter, self).__init__(queryset)
        self.verbose_overrides['owner'] = self.get_field('owner').verbose_name
        for s in self.columns:
            suffix = '_str'
            if s.endswith(suffix):
                self.verbose_overrides[s] = self.get_verbose_name(
                    s.split(suffix)[0]) + f' ({self.rendu})'
            elif LOOKUP_SEP in s:
                self.verbose_overrides[s] = self.fields[s].verbose_name

    @staticmethod
    def get_owner(obj):
        if obj.owner is None:
            return ''
        return str(obj.owner)

COMMON_MODEL_COLUMNS = ('owner',)
PUBLISHED_MODEL_COLUMNS = COMMON_MODEL_COLUMNS + ('etat__nom',)
AUTORITE_MODEL_COLUMNS = \
    PUBLISHED_MODEL_COLUMNS + ('notes_publiques', 'notes_privees')


class RenduExporter(CommonModelExporter):

    def __init__(self, queryset=None):
        super(RenduExporter, self).__init__(queryset)
        self.verbose_overrides['rendu'] = self.RENDU

    @staticmethod
    def get_rendu(obj):
        return str(obj)


@exporter_registry.add
class LieuExporter(RenduExporter):
    model = Lieu
    columns = (
        'id', 'rendu', 'nom', 'parent', 'nature__nom', 'ville', 'historique',
        'longitude', 'latitude', 'afo',
    ) + AUTORITE_MODEL_COLUMNS
    verbose_overrides = {
        'longitude': _('longitude'),
        'latitude': _('latitude'),
    }

    @staticmethod
    def get_ville(obj):
        ville = obj.get_ancestors().filter(nature__nom='ville').first()
        if ville is not None:
            return str(ville)

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
            return str(obj.siege)


@exporter_registry.add
class IndividusProfessionsExporter(Exporter):
    model = Individu.professions.through
    columns = ('individu', 'profession__nom')

    def get_verbose_table_name(self):
        return _('individus ↔ professions')


@exporter_registry.add
class ParenteDIndividuExporter(CommonModelExporter):
    model = ParenteDIndividus
    columns = ('parent', 'enfant', 'type__nom') + COMMON_MODEL_COLUMNS


@exporter_registry.add
class ProfessionExporter(CommonModelExporter):
    model = Profession
    columns = (
        'id', 'nom', 'nom_pluriel', 'nom_feminin', 'parent'
    ) + AUTORITE_MODEL_COLUMNS


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
    columns = ('oeuvre', 'source', 'individu', 'profession__nom')


@exporter_registry.add
class PartieProfessionsExporter(Exporter):
    model = Partie.professions.through
    columns = ('partie', 'profession__nom')

    def get_verbose_table_name(self):
        return _('partie ↔ professions')


@exporter_registry.add
class PartieExporter(CommonModelExporter):
    model = Partie
    columns = (
        'id', 'nom', 'nom_pluriel', 'professions_str', 'parent',
    ) + AUTORITE_MODEL_COLUMNS
    m2ms = ('professions',)

    @staticmethod
    def get_professions_str(obj):
        return ', '.join([str(o) for o in obj.professions.all()])


@exporter_registry.add
class PupitreExporter(CommonModelExporter):
    model = Pupitre
    columns = ('oeuvre', 'partie__nom', 'soliste',
               'quantite_min', 'quantite_max')


@exporter_registry.add
class OeuvreExporter(RenduExporter):
    model = Oeuvre
    columns = (
        'id', 'rendu', 'auteurs_str', 'pupitres_str', 'prefixe_titre', 'titre',
        'coordination', 'prefixe_titre_secondaire', 'titre_secondaire',
        'genre__nom', 'coupe', 'numero', 'incipit', 'tempo', 'tonalite',
        'sujet', 'arrangement', 'surnom', 'nom_courant',
        'extrait_de', 'type_extrait', 'numero_extrait',
        'creation_date', 'creation_date_approx',
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
        return _('sources ↔ evenements')


@exporter_registry.add
class SourcesOeuvresExporter(Exporter):
    model = Source.oeuvres.through

    def get_verbose_table_name(self):
        return _('sources ↔ œuvres')


@exporter_registry.add
class SourcesIndividusExporter(Exporter):
    model = Source.individus.through

    def get_verbose_table_name(self):
        return _('sources ↔ individus')


@exporter_registry.add
class SourcesEnsemblesExporter(Exporter):
    model = Source.ensembles.through

    def get_verbose_table_name(self):
        return _('sources ↔ ensembles')


@exporter_registry.add
class SourcesLieuxExporter(Exporter):
    model = Source.lieux.through

    def get_verbose_table_name(self):
        return _('sources ↔ lieux')


@exporter_registry.add
class SourcesPartiesExporter(Exporter):
    model = Source.parties.through

    def get_verbose_table_name(self):
        return _('sources ↔ parties')


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
    columns = ('id', 'evenement', 'evenement_str', 'element_de_programme',
               'individu', 'individu_str', 'ensemble', 'ensemble_str',
               'partie__nom', 'profession__nom') + COMMON_MODEL_COLUMNS

    @staticmethod
    def get_evenement_str(obj):
        if obj.evenement:
            return str(obj.evenement)

    @staticmethod
    def get_individu_str(obj):
        if obj.individu:
            return str(obj.individu)

    @staticmethod
    def get_ensemble_str(obj):
        if obj.ensemble:
            return str(obj.ensemble)


@exporter_registry.add
class CaracteristiqueDeProgrammeExporter(CommonModelExporter):
    model = CaracteristiqueDeProgramme
    columns = ('id', 'type__nom', 'valeur')


@exporter_registry.add
class ProgrammeCaracteristiquesExporter(Exporter):
    model = ElementDeProgramme.caracteristiques.through
    columns = ('elementdeprogramme', 'caracteristiquedeprogramme')
    verbose_overrides = {
        'elementdeprogramme': _('élément de programme'),
        'caracteristiquedeprogramme': _('caractéristique de programme')
    }

    def get_verbose_table_name(self):
        return _('programme ↔ caractéristiques')


@exporter_registry.add
class ElementDeProgrammeExporter(CommonModelExporter):
    model = ElementDeProgramme
    columns = ('id', 'evenement', 'evenement_str', 'oeuvre', 'oeuvre_str',
               'autre', 'caracteristiques_str', 'distribution_str',
               'numerotation', 'position', 'part_d_auteur') \
        + COMMON_MODEL_COLUMNS
    m2ms = ('caracteristiques', 'distribution')

    @staticmethod
    def get_evenement_str(obj):
        if obj.evenement:
            return str(obj.evenement)

    @staticmethod
    def get_oeuvre_str(obj):
        if obj.oeuvre:
            return str(obj.oeuvre)

    @staticmethod
    def get_caracteristiques_str(obj):
        return obj.calc_caracteristiques()

    @staticmethod
    def get_distribution_str(obj):
        return ', '.join([str(o) for o in obj.distribution.all()])


@exporter_registry.add
class EvenementExporter(CommonModelExporter):
    model = Evenement
    columns = (
        'id', 'saison', 'debut_date', 'debut_date_approx', 'debut_heure',
        'debut_heure_approx', 'debut_lieu', 'debut_lieu_str',
        'debut_lieu_approx', 'fin_date', 'fin_date_approx', 'fin_heure',
        'fin_heure_approx', 'fin_lieu', 'fin_lieu_str', 'fin_lieu_approx',
        'recette_generale', 'recette_par_billets', 'afo',
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
        'debut_lieu_approx': 'lieu de début (approximatif)',
        'fin_lieu_approx': 'date de fin (approximatif)',
    }

    @staticmethod
    def get_saison(obj):
        return ', '.join([saison.get_periode() for saison in obj.get_saisons()])

    @staticmethod
    def get_debut_lieu_str(obj):
        return obj.debut.lieu_str(tags=False)

    @staticmethod
    def get_fin_lieu_str(obj):
        return obj.fin.lieu_str(tags=False)
