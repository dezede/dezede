
import numpy
import string
import calendar
import pandas
import importlib
from io import BytesIO
from itertools import chain
from collections import defaultdict, OrderedDict
from math import isnan

from django.apps import apps
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from django.db.models import (
    IntegerField, ForeignKey, DateTimeField, OneToOneField)
from django.db.models.fields.related import RelatedField, ForeignObjectRel
from django.db.models.query import QuerySet

from exporter.registry import exporter_registry
from exporter.base import Exporter

from libretto.models import Evenement

from exporter.base import Exporter

from libretto.models import *


class ScenariosExporter(object):
    exporters = []

    CONTENT_TYPES = {
        'xlsx': 'application/vnd.openxmlformats-officedocument'
                '.spreadsheetml.sheet',
    }

    def __init__(self, dossier, scenarios=[]):
        for scenario in scenarios:
            scenario = string.capwords(scenario.get('scenario')).replace('-', '')
            expt = f"dossiers.export.{scenario}"
            Exporter = self.loader(expt)
            self.exporters.append(Exporter(dossier.get_queryset()))

    def loader(self, path):
        module_name, class_name = path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    def get_dataframes(self):
        return [(exporter.get_verbose_table_name(), exporter._get_shaped_dataframe())
                for exporter in self.exporters]

    # def to_xlsx(self):
    #     return self.exporter.to_xlsx()

    def to_xlsx(self):
        f = BytesIO()
        with pandas.ExcelWriter(f, engine='xlsxwriter') as writer:
            for verbose_table_name, df in self.get_dataframes():
                table_name = force_text(verbose_table_name)

                df.to_excel(writer, str(table_name),
                            index=True, freeze_panes=(2, 0))

                worksheet = writer.sheets[str(table_name)]
                worksheet.set_column(0, 0, None, None, {'hidden': True})
                worksheet.set_row(2, None, None, {'hidden': True})

            writer.save()
        out = f.getvalue()
        f.close()
        return out

    def to_json(self):
        raise NotImplementedError

    def to_csv(self):
        raise NotImplementedError


class CustomExporter(Exporter):
    verbose_names = None
    background_colors = [
        "#76affe",
        "#83b6fc",
        "#8cbbfc",
        "#9ec7ff",
        "#accdfc",
        "#c4dbfc",
        "#eff6ff",
        "", ""]
    stats = 'count'
    sum_col = None
    swaps = None
    display_total = True
    purge = True

    def __init__(self, queryset=None):
        self.queryset = queryset

        if not self.columns:
            self.columns = [field.name for field in self.model._meta.fields]

        self.method_names = []
        self.lookups = []
        for column in self.columns:
            if hasattr(self, 'get_' + column):
                self.method_names.append(column)
            else:
                self.lookups.append(column)
        self.fields = {lookup: self.get_field(lookup.split('__')[0])
                       for lookup in self.lookups}
        self.final_fields = {lookup: self.get_final_field(lookup)
                             for lookup in self.lookups}
        self.null_int_lookups = []
        self.datetime_lookups = []
        for lookup, (_, field) in self.final_fields.items():
            if isinstance(field, ForeignObjectRel) \
                or (isinstance(field, (IntegerField, ForeignKey))
                    and field.null):
                self.null_int_lookups.append(lookup)
            elif isinstance(field, DateTimeField):
                self.datetime_lookups.append(lookup)

    def _get_background_colors(self):
        return self.background_colors

    def _swap_col(self, df):
        c = df.columns
        for swap in self.swaps:
            a, b = c.get_loc(swap[0]), c.get_loc(swap[1])
            df = df.rename(columns={c[a]: c[b], c[b]: c[a]})
            df[[c[a], c[b]]] = df[[c[b], c[a]]]
        return df

    def _background_color(self, row, nb_lines):
        background_colors = self._get_background_colors()
        elements = row.to_list()
        try:
            idx = list(i for i, v in enumerate(elements) if v)[0]
        except IndexError:
            idx = 0

        if row.name == (nb_lines - 1) and self.display_total:
            white = ("background-color: white," * len(elements[:idx])).split(',')[:-1]
            color = (("background-color: #d9ead3,") * len(elements[idx:])).split(',')[:-1]
            return white + color

        if idx == len(elements) - 2 or row.name == (nb_lines - 2) or all(len(str(ele)) == 0 for ele in elements[:-1]):
            return ['background-color: white'] * len(elements)

        try:
            bg_color = background_colors[idx]
        except IndexError:
            bg_color = background_colors[idx - 1]

        white = ("background-color: white," * len(elements[:idx])).split(',')[:-1]
        color = (("background-color:" + bg_color + ",") * len(elements[idx:])).split(',')[:-1]

        return white + color

    def _format_df(self, df, df_stats):
        def add_column(col_name, col_value, stats, tempdf):
            data = {col_name: col_value}
            if stats:
                data.update(stats)
            return tempdf.append(data, ignore_index=True)

        current = df.to_dict()
        newdf = pandas.DataFrame()
        col_args = df.columns.to_list()
        col_dict = {}
        for i, row in df.iterrows():
            for col in row.to_dict().keys():
                if current[col] != row[col]:
                    for idx, c in enumerate(col_args[col_args.index(col):]):
                        current[c] = row[c]
                        newdf = add_column(c, row[c], {self.stats: df_stats[f"{self.stats}_{c}"].loc[i]}, newdf)

        stats_col = newdf.pop(self.stats)
        newdf.insert(len(newdf.columns.to_list()), self.stats, stats_col)
        newdf[self.stats] = newdf[self.stats].fillna(0).astype(int)

        return newdf

    def _get_shaped_dataframe(self):
        df_initial = self._get_dataframe()

        if not (df_initial.index == 0).any():
            return df_initial

        df_columns = df_initial.columns.to_list()

        if self.stats == 'sum' and not self.sum_col:
            raise Exception("'sum_col' column is not defined")

        df_initial = df_initial.fillna(value='')

        for i, field in enumerate(df_columns, 1):
            stats_field = field
            if self.stats == 'sum':
                stats_field = self.sum_col
            df_initial[f'{self.stats}_{field}'] = df_initial.groupby(df_columns[:i])[[stats_field]].transform(self.stats)

        if self.purge:
            df_initial = df_initial.drop_duplicates(df_columns).reset_index(drop=True)

        divider = 1
        if self.stats == 'sum':
            del df_initial[self.sum_col]
            del df_initial[f'sum_{self.sum_col}']
        divider = 2
        half = int(len(df_initial.columns) / divider)

        df = df_initial.iloc[:, :half]
        df_stats = df_initial.iloc[:, half:]

        df = self._format_df(df, df_stats)

        total = df_stats.sum()[-1]

        if self.swaps:
            df = self._swap_col(df)

        spacer = (lambda x: ',' * x)(len(df.columns) - 1).split(',')

        if self.display_total:
            df.loc[len(df.index)] = spacer
            df.loc[len(df.index)] = spacer[:-2] + [_('TOTAL'), total]

        # Adds verbose column names
        verbose_names = []
        for column in df.columns:
            if column in self.verbose_names:
                verbose_name = force_text(self.verbose_names[column])
                verbose_names.append(verbose_name)
        df.columns = verbose_names

        df = df.replace(numpy.nan, '')

        df.columns = pandas.MultiIndex.from_tuples(zip([force_text(self.title)] + spacer[:-1], df.columns))

        if self.background_colors:
            df = df.style.apply(self._background_color, nb_lines=len(df.index), axis=1)

        return df

    def _get_individu_name(self, individu):
        if not individu.prenoms:
            particule = ''
            if individu.titre:
                particule += f'{individu.calc_titre()} '
            if individu.particule_nom:
                particule += f'{individu.particule_nom} '

            return f'{particule}{individu.nom}'
        return f'{individu.prenoms} {individu.nom}'

    def get_verbose_table_name(self):
        # Note: Excel sheet names can’t be larger than 31 characters.
        return self.tab_name


class Scenario1(CustomExporter):
    model = Evenement
    columns = [
        'annee', 'saison', 'mois', 'jour'
    ]
    verbose_names = {
        'annee': _('Année'),
        'saison': _('Saison'),
        'mois': _('Mois'),
        'jour': _('Jour'),
        'count': _('Nombre d\'événements')
    }
    m2ms = ()
    tab_name = _("1. Événements - chronologique")
    title = _("1. Événements : répartition chronologique")
    swaps = (
        ('annee', 'saison',),
    )

    def get_background_colors():
        return self.background_colors.insert(0, "#d9d2e9")

    @staticmethod
    def get_annee(obj):
        return obj.debut_date.year

    @staticmethod
    def get_saison(obj):
        saison = ', '.join([saison.get_periode() for saison in obj.get_saisons()])
        if saison:
            return saison
        return _('Donnée indisponible')

    @staticmethod
    def get_mois(obj):
        return calendar.month_name[obj.debut_date.month]

    @staticmethod
    def get_jour(obj):
        return obj.debut_date.day


class Scenario2(CustomExporter):
    model = Evenement
    background_colors = ["#3d85c6", "#6fa8dc", "#9fc5e8", "#a4cafe", "#d9d2e9", "#cfe2f3", "#c9daf8", "#c3ddfd", "#ebf5ff"]
    columns = [
        'pays', 'ville', 'salle',
    ]
    verbose_names = {
        'pays': _('Pays'),
        'ville': _('Ville'),
        'salle': _('Salle'),
        'count': _('Nombre d\'événements')
    }
    tab_name = _("2. Événements - géographique")
    title = _("2. Événements : répartition géographique")

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

    def get_salle(self, obj):
        if obj.debut_lieu is None:
            return
        path = (obj.debut_lieu.get_ancestors(include_self=True)
                .select_related('nature'))
        try:
            return path.last().nom
        except Exception:
            return ''


class Scenario3(CustomExporter):
    model = Evenement
    columns = [
        'oeuvre', 'auteur', 'annee', 'saison', 'mois',
    ]
    verbose_names = {
        'oeuvre': _('Œuvre'),
        'auteur': _('Auteur'),
        'annee': _('Année'),
        'saison': _('Saison'),
        'mois': _('Mois'),
        'count': _('Nombre d\'événements')
    }
    tab_name = _("3. Œuvres - chronologique")
    title = _("3. Œuvres : répartition chronologique")

    def __init__(self, queryset=None):
        events_pk = queryset.values_list('pk')
        elements = []

        for work in queryset.oeuvres():
            individus = {'names': [], 'pks': []}
            for individu in queryset.individus_auteurs().filter(auteurs__oeuvre__pk=work.pk).distinct():
                name = self._get_individu_name(individu)
                individus['names'].append(name)
                individus['pks'].append(individu.pk)

            for event in queryset.filter(Q(programme__oeuvre__auteurs__individu__pk__in=individus.get('pks')) and Q(programme__oeuvre__pk=work.pk)).distinct():
                setattr(event, 'oeuvre', work.titre_html(tags=False))
                setattr(event, 'auteur', ', '.join(individus.get('names')))
                elements.append(event)

        super(Scenario3, self).__init__(queryset=elements)

    def _get_related_exporters(self, parent_fk_ids=None, is_root=True):
        return [self]

    @staticmethod
    def get_oeuvre(obj):
        return obj.oeuvre

    @staticmethod
    def get_auteur(obj):
        return obj.auteur

    @staticmethod
    def get_annee(obj):
        return obj.debut_date.year

    @staticmethod
    def get_mois(obj):
        return calendar.month_name[obj.debut_date.month]

    @staticmethod
    def get_saison(obj):
        saison = ', '.join([saison.get_periode() for saison in obj.get_saisons()])
        if saison:
            return saison
        return _('Donnée indisponible')


class Scenario4(CustomExporter):
    model = Evenement
    columns = [
        'oeuvre', 'auteur', 'pays', 'ville', 'salle', 'annee', 'saison', 'mois',
    ]
    verbose_names = {
        'oeuvre': _('Œuvre'),
        'auteur': _('Auteur'),
        'pays': _('Pays'),
        'ville': _('Ville'),
        'salle': _('Salle'),
        'annee': _('Année'),
        'saison': _('Saison'),
        'mois': _('Mois'),
        'count': _('Nombre d\'événements')
    }
    tab_name = _("4. Œuvres - géographique")
    title = _("4. Œuvres : répartition géographique")

    def __init__(self, queryset=None):
        events_pk = queryset.values_list('pk')
        elements = []

        for work in queryset.oeuvres():
            individus = {'names': [], 'pks': []}
            for individu in queryset.individus_auteurs().filter(auteurs__oeuvre__pk=work.pk).distinct():
                name = self._get_individu_name(individu)
                individus['names'].append(name)
                individus['pks'].append(individu.pk)

            for event in queryset.filter(Q(programme__oeuvre__auteurs__individu__pk=individus.get('pks')) and Q(programme__oeuvre__pk=work.pk)).distinct():
                setattr(event, 'oeuvre', work.titre_html(tags=False))
                setattr(event, 'auteur', ', '.join(individus.get('names')))
                elements.append(event)

        super(Scenario4, self).__init__(queryset=elements)

    def _get_related_exporters(self, parent_fk_ids=None, is_root=True):
        return [self]

    @staticmethod
    def get_oeuvre(obj):
        return obj.oeuvre

    @staticmethod
    def get_auteur(obj):
        return obj.auteur

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

    def get_salle(self, obj):
        if obj.debut_lieu is None:
            return
        path = (obj.debut_lieu.get_ancestors(include_self=True)
                .select_related('nature'))
        try:
            return path.last().nom
        except Exception:
            return ''

    def get_annee(self, obj):
        return obj.debut_date.year

    @staticmethod
    def get_saison(obj):
        saison = ', '.join([saison.get_periode() for saison in obj.get_saisons()])
        if saison:
            return saison
        return _('Donnée indisponible')

    def get_mois(self, obj):
        return calendar.month_name[obj.debut_date.month]


class Scenario5(CustomExporter):
    model = Evenement
    columns = [
        'auteur', 'annee', 'saison', 'mois', 'programmes',
    ]
    verbose_names = {
        'auteur': _('Auteur'),
        'annee': _('Année'),
        'saison': _('Saison'),
        'mois': _('Mois'),
        'sum': _('Nombre d\'éléments de programme')
    }
    tab_name = _("5. Auteurs - chronologique")
    title = _("5. Auteurs : répartition chronologique")
    stats = 'sum'
    sum_col = 'programmes'
    purge = False

    def __init__(self, queryset=None):
        elements = []

        for individu in queryset.individus_auteurs().distinct():
            for event in queryset.filter(programme__oeuvre__auteurs__individu__pk=individu.pk).distinct():
                name = self._get_individu_name(individu)
                setattr(event, 'auteur', name)
                setattr(event, 'programmes', event.programme.filter(oeuvre__auteurs__individu__pk=individu.pk).count())
                elements.append(event)

        super(Scenario5, self).__init__(queryset=elements)

    def _get_related_exporters(self, parent_fk_ids=None, is_root=True):
        return [self]

    def get_auteur(self, obj):
        return obj.auteur

    def get_annee(self, obj):
        return obj.debut_date.year

    @staticmethod
    def get_saison(obj):
        saison = ', '.join([saison.get_periode() for saison in obj.get_saisons()])
        if saison:
            return saison
        return _('Donnée indisponible')

    def get_mois(self, obj):
        return calendar.month_name[obj.debut_date.month]

    def get_programmes(self, obj):
        return obj.programmes


class Scenario6(CustomExporter):
    model = Evenement
    columns = [
        'interprete', 'annee', 'saison', 'mois'
    ]
    verbose_names = {
        'interprete': _('Interprète'),
        'annee': _('Année'),
        'saison': _('Saison'),
        'mois': _('Mois'),
        'count': _('Nombre d\'événements')
    }
    tab_name = _("6. Interprètes - chronologique")
    title = _("6. Interprètes : répartition chronologique")

    def __init__(self, queryset=None):
        event_pk = queryset.values_list('pk')
        elements = []

        for individu in queryset.individus_auteurs():
            has_distribution = False

            for elementdedistribution in apps.get_model('libretto', 'ElementDeDistribution').objects.filter(individu__pk=individu.pk, evenement__isnull=False, evenement__pk__in=event_pk).distinct():
                event = elementdedistribution.evenement
                name = self._get_individu_name(individu)
                setattr(event, 'interprete', name)
                elements.append(event)
                has_distribution = True

            if not has_distribution:
                individu_events = []
                for elementdeprogramme in apps.get_model('libretto', 'ElementDeProgramme').objects.filter(oeuvre__auteurs__individu__pk=individu.pk, evenement__isnull=False, evenement__pk__in=event_pk).distinct():
                    event = elementdeprogramme.evenement
                    if event.pk not in individu_events:
                        name = self._get_individu_name(individu)
                        setattr(event, 'interprete', name)
                        elements.append(event)
                        individu_events.append(event.pk)

        super(Scenario6, self).__init__(queryset=elements)

    def _get_related_exporters(self, parent_fk_ids=None, is_root=True):
        return [self]

    def get_interprete(self, obj):
        if hasattr(obj, 'interprete'):
            return obj.interprete
        return ' '

    def get_annee(self, obj):
        return obj.debut_date.year

    @staticmethod
    def get_saison(obj):
        saison = ', '.join([saison.get_periode() for saison in obj.get_saisons()])
        if saison:
            return saison
        return _('Donnée indisponible')

    def get_mois(self, obj):
        return calendar.month_name[obj.debut_date.month]


class Scenario7(CustomExporter):
    model = Evenement
    columns = [
        'auteur', 'oeuvre', 'annee', 'saison', 'mois'
    ]
    verbose_names = {
        'auteur': _('Auteur'),
        'oeuvre': _('Œuvre'),
        'annee': _('Année'),
        'saison': _('Saison'),
        'mois': _('Mois'),
        'count': _('Nombre d\'événements')
    }
    tab_name = _("7. Auteurs et œuvres")
    title = _("7. Auteurs et œuvres : répartition chronologique")

    def __init__(self, queryset=None):
        events_pk = queryset.values_list('pk')
        elements = []

        for individu in queryset.individus_auteurs():
            for work in queryset.oeuvres().filter(auteurs__individu__pk=individu.pk):
                for event in queryset.filter(Q(programme__oeuvre__auteurs__individu__pk=individu.pk) and Q(programme__oeuvre__pk=work.pk)):
                    name = self._get_individu_name(individu)
                    setattr(event, 'auteur', name)
                    setattr(event, 'oeuvre', work.titre_html(tags=False))
                    elements.append(event)

        super(Scenario7, self).__init__(queryset=elements)

    def _get_related_exporters(self, parent_fk_ids=None, is_root=True):
        return [self]

    def get_auteur(self, obj):
        return obj.auteur

    def get_oeuvre(self, obj):
        return obj.oeuvre

    @staticmethod
    def get_annee(obj):
        return obj.debut_date.year

    @staticmethod
    def get_saison(obj):
        saison = ', '.join([saison.get_periode() for saison in obj.get_saisons()])
        if saison:
            return saison
        return _('Donnée indisponible')

    @staticmethod
    def get_mois(obj):
        return calendar.month_name[obj.debut_date.month]


class Scenario8(CustomExporter):
    model = Evenement
    columns = [
        'pays', 'ville', 'salle', 'annee', 'saison', 'mois', 'jour', 'recettes',
    ]
    verbose_names = {
        'pays': _('Pays'),
        'ville': _('Ville'),
        'salle': _('Salle'),
        'annee': _('Année'),
        'saison': _('Saison'),
        'mois': _('Mois'),
        'jour': _('Jour'),
        'sum': _('Recette'),
    }
    tab_name = _("8. Recettes")
    title = _("8. Recettes")
    stats = 'sum'
    sum_col = 'recettes'

    @staticmethod
    def get_lieu(obj, nature):
        if obj.debut_lieu is None:
            return
        lieu = (obj.debut_lieu.get_ancestors(include_self=True)
                .filter(nature__nom=nature).first())
        if lieu is not None:
            return force_text(lieu)

    def get_pays(self, obj):
        return self.get_lieu(obj, 'pays')

    def get_ville(self, obj):
        return self.get_lieu(obj, 'ville')

    def get_salle(self, obj):
        if obj.debut_lieu is None:
            return
        path = (obj.debut_lieu.get_ancestors(include_self=True)
                .select_related('nature'))
        try:
            return path.last().nom
        except Exception:
            return ''

    @staticmethod
    def get_saison(obj):
        saison = ', '.join([saison.get_periode() for saison in obj.get_saisons()])
        if saison:
            return saison
        return _('Donnée indisponible')

    @staticmethod
    def get_annee(obj):
        return obj.debut_date.year

    @staticmethod
    def get_mois(obj):
        return calendar.month_name[obj.debut_date.month]

    @staticmethod
    def get_jour(obj):
        return obj.debut_date.day

    @staticmethod
    def get_recettes(obj):
        return obj.recette_generale or 0
