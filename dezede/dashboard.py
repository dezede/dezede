"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'musicologie.dashboard.CustomIndexDashboard'
"""

from __future__ import unicode_literals
from django.utils.translation import gettext_lazy as _

from grappelli.dashboard import modules, Dashboard


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        self.children.append(modules.Group(
            None,
            column=1,
            collapsible=False,
            children=[
                modules.ModelList(
                    _('Saisie courante'),
                    column=1,
                    models=('libretto.models.source.Source',
                            'libretto.models.evenement.Evenement',
                            'libretto.models.oeuvre.Oeuvre',
                            'libretto.models.individu.Individu',
                            'libretto.models.personnel.Ensemble',
                            'libretto.models.espace_temps.Lieu',),
                ),
                modules.ModelList(
                    _('Saisie occasionnelle'),
                    column=1,
                    css_classes=('grp-collapse grp-closed',),
                    models=('libretto.models.*',),
                    exclude=('libretto.models.source.Source',
                             'libretto.models.evenement.Evenement',
                             'libretto.models.oeuvre.Oeuvre',
                             'libretto.models.individu.Individu',
                             'libretto.models.personnel.Ensemble',
                             'libretto.models.espace_temps.Lieu',),
                ),
                modules.ModelList(
                    _('AFO'),
                    column=1,
                    css_classes=('grp-collapse grp-closed',),
                    models=('afo.models.*',),
                )
            ]
        ))

        self.children.append(modules.ModelList(
            _('Gestion des contenus'),
            column=1,
            collapsible=False,
            css_classes=('grp-open',),
            models=('dossiers.*', 'dezede.*'),
        ))

        self.children.append(modules.ModelList(
            _('Didacticiel'),
            column=1,
            collapsible=False,
            css_classes=('grp-open',),
            models=('examens.*',),
        ))

        self.children.append(modules.RecentActions(
            _('Actions récentes'),
            limit=5,
            collapsible=False,
            column=2,
        ))

        self.children.append(modules.ModelList(
            _('Utilisateurs et groupes'),
            column=3,
            css_classes=('grp-collapse grp-closed',),
            models=('django.contrib.auth.*',
                    'accounts.*',
                    'django.contrib.sites.*',),
        ))

        self.children.append(modules.LinkList(
            _('Traduction'),
            column=3,
            css_classes=('grp-collapse grp-closed',),
            children=[
                {
                    'title': 'Transifex',
                    'url': 'https://www.transifex.com/projects/p/dezede/',
                    'external': True,
                },
            ]
        ))
