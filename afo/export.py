# coding: utf-8

from __future__ import unicode_literals
from datetime import timedelta
from django.utils.encoding import force_text
from exporter.base import Exporter
from exporter.registry import exporter_registry
from libretto.export import CommonModelExporter
from libretto.models import Evenement, ElementDeProgramme
from .models import EvenementAFO, LieuAFO


@exporter_registry.add
class EvenementAFOExporter(CommonModelExporter):
    model = EvenementAFO


@exporter_registry.add
class LieuAFOExporter(CommonModelExporter):
    model = LieuAFO


class AFOEvenementExporter(Exporter):
    model = Evenement
    columns = (
        'saison', 'ensemble', 'debut_date',
        'afo__code_programme', 'afo__tournee',
        'afo__titre_programme', 'afo__cycle',
        'latitude', 'longitude',
        'ville', 'debut_lieu__afo__code_postal', 'pays', 'debut_lieu__nom',
        'debut_lieu_id', 'afo__nom_festival',
        'afo__modalite_de_production', 'debut_lieu__afo__type_de_salle',
        'debut_lieu__afo__type_de_scene', 'afo__type_de_programme',
        'afo__presentation_specifique',
        'afo__public_specifique', 'afo__exonerees', 'afo__payantes',
        'afo__frequentation', 'afo__scolaires', 'afo__jauge',
    )
    verbose_overrides = {
        'ensemble': 'Orchestre',
        'afo__code_programme': 'Code du programme / série',
        'afo__tournee': 'Code ou titre de la tournée',
        'afo__titre_programme': 'Titre du programme 1)',
        'afo__cycle': 'Cycle 1)',
        'debut_lieu__afo__code_postal': 'Code postal',
        'debut_lieu__nom': 'Nom de la salle',
        'debut_lieu_id': 'ID salle',
        'afo__nom_festival': 'Nom du festival',
        'afo__modalite_de_production': 'Modalité de production',
        'debut_lieu__afo__type_de_salle': 'Type de lieu',
        'debut_lieu__afo__type_de_scene': 'Lieux labellisés',
        'afo__type_de_programme': 'Typologie artistique du programme',
        'afo__presentation_specifique': 'Si présentation spécifique (concert commenté, participatif), précisez',
        'afo__public_specifique': 'Si représentation / concert conçu exclusivement pour public spécifique, préciser le type de public.',
        'afo__exonerees': '1) Entrées exonérées',
        'afo__payantes': '2) Entrées payantes',
        'afo_frequentation': 'Fréquentation totale 1) + 2)',
        'afo__scolaires': 'Dont entrées dans le cadre scolaire',
        'afo__jauge': 'Jauge',
    }

    @staticmethod
    def get_saison(obj):
        return ', '.join(
            [saison.get_periode() for saison in obj.get_saisons()])

    @staticmethod
    def get_ensemble(obj):
        ensembles = Evenement.objects.filter(pk=obj.pk).ensembles()
        return '\n'.join([force_text(e) for e in ensembles])

    @staticmethod
    def get_longitude(obj):
        obj = obj.debut_lieu
        if obj is None or obj.geometry is None \
                or obj.geometry.geom_type != 'Point':
            return
        return obj.geometry.coords[0]

    @staticmethod
    def get_latitude(obj):
        obj = obj.debut_lieu
        if obj is None or obj.geometry is None \
                or obj.geometry.geom_type != 'Point':
            return
        return obj.geometry.coords[1]

    @staticmethod
    def get_ville(obj, nature='ville'):
        if obj.debut_lieu is None:
            return
        ville = (obj.debut_lieu.get_ancestors(include_self=True)
                 .filter(nature__nom=nature).first())
        if ville is not None:
            return force_text(ville)

    def get_pays(self, obj):
        return self.get_ville(obj, 'pays')


class AFOElementDeProgrammeExporter(Exporter):
    model = ElementDeProgramme
    columns = (
        'saison', 'ensemble', 'oeuvre', 'oeuvre_id', 'compositeur_nom',
        'compositeur_prenoms', 'compositeur_nom_complet', 'compositeur_id',
        'compositeur_naissance', 'compositeur_deces',
        'compositeur_naissance_plus_20', 'compositeur_periode',
    )
    verbose_overrides = {
        'ensemble': 'Orchestre',
        'oeuvre_id': 'ID de l’œuvre dans Dezède',
        'compositeur_nom': 'nom du compositeur',
        'compositeur_prenoms': 'prénoms du compositeur',
        'compositeur_nom_complet': 'nom complet du compositeur',
        'compositeur_id': 'ID du compositeur dans Dezède',
        'compositeur_naissance': 'date de naissance du compositeur',
        'compositeur_deces': 'date de déces du compositeur',
        'compositeur_naissance_plus_20': 'date de naissance du compositeur + 20 ans',
        'compositeur_periode': 'période du compositeur',
    }

    @staticmethod
    def get_saison(obj):
        return ', '.join(
            [saison.get_periode() for saison in obj.evenement.get_saisons()])

    @staticmethod
    def get_ensemble(obj):
        ensembles = Evenement.objects.filter(pk=obj.evenement_id).ensembles()
        return '\n'.join([force_text(e) for e in ensembles])

    @staticmethod
    def get_oeuvre(obj):
        if obj.oeuvre is not None:
            return force_text(obj.oeuvre)

    @staticmethod
    def get_oeuvre_id(obj):
        if obj.oeuvre_id is not None:
            return force_text(obj.oeuvre_id)

    @staticmethod
    def _get_compositeur_attr(obj, attr):
        if obj.oeuvre is None:
            return ()
        compositeurs = obj.oeuvre.auteurs.filter(profession__nom='compositeur',
                                                 individu__isnull=False)
        data = [getattr(c.individu, attr) for c in compositeurs]
        return ['' if v is None else v for v in data]

    def get_compositeur_nom(self, obj):
        return '\n'.join(self._get_compositeur_attr(obj, 'nom'))

    def get_compositeur_prenoms(self, obj):
        return '\n'.join(self._get_compositeur_attr(obj, 'prenoms'))

    def get_compositeur_nom_complet(self, obj):
        return '\n'.join(
            [m(tags=False, links=False)
             for m in self._get_compositeur_attr(obj, 'nom_complet')])

    def get_compositeur_id(self, obj):
        return '\n'.join(map(force_text,
                             self._get_compositeur_attr(obj, 'id')))

    def get_compositeur_naissance(self, obj):
        return '\n'.join(
            map(force_text, self._get_compositeur_attr(obj, 'naissance_date')))

    def get_compositeur_deces(self, obj):
        return '\n'.join(
            map(force_text, self._get_compositeur_attr(obj, 'deces_date')))

    def get_compositeur_naissance_plus_20(self, obj):
        return '\n'.join([
            '' if d == '' else force_text(d + timedelta(days=365.25*20))
            for d in self._get_compositeur_attr(obj, 'naissance_date')])

    def get_compositeur_periode(self, obj):
        from dossiers.views import PERIODS, PERIOD_NAMES

        out = []
        for naissance in self._get_compositeur_attr(obj, 'naissance_date'):
            if naissance == '':
                out.append(force_text(PERIOD_NAMES[-1]))
                continue
            for k, (year0, year1) in PERIODS.items():
                if year0 < naissance.year <= year1:
                    out.append(force_text(PERIOD_NAMES[k]))
                    break
        return '\n'.join(out)
