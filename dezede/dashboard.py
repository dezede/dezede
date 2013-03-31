# coding: utf-8

"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'musicologie.dashboard.CustomIndexDashboard'
"""

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from grappelli.dashboard import modules, Dashboard


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        self.children.append(
            modules.ModelList(
                _('Saisie courante'),
                column=1,
                collapsible=False,
                css_classes=('grp-open',),
                models=('libretto.models.source.Source',
                        'libretto.models.evenement.Evenement',
                        'libretto.models.oeuvre.Oeuvre',
                        'libretto.models.individu.Individu',
                        'libretto.models.espace_temps.Lieu',),
            )
        )

        self.children.append(modules.ModelList(
            _('Rédaction'),
            column=1,
            collapsible=False,
            css_classes=('grp-open',),
            models=('dossiers.*', 'django.contrib.flatpages.*',),
        ))

        self.children.append(modules.Group(
            _('Fichiers'),
            column=1,
            collapsible=True,
            css_classes=('grp-collapse grp-closed',),
            children=[
                modules.LinkList(
                    _('Gestionnaire de fichiers bruts'),
                    column=1,
                    collapsible=False,
                    children=[
                        {
                            'title': 'FileBrowser',
                            'url': '/admin/filebrowser/browse/',
                            'external': False,
                        },
                    ]
                ),
                modules.ModelList(
                    _('Intégration à la base de données'),
                    collapsible=False,
                    models=('libretto.models.common.Document',
                            'libretto.models.common.Illustration',),
                )
            ]
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

        self.children.append(modules.LinkList(
            _('Support'),
            column=3,
            css_classes=('grp-collapse grp-closed',),
            children=[
                {
                    'title': _('Documentation de Django'),
                    'url': 'http://docs.djangoproject.com/',
                    'external': True,
                },
                {
                    'title': _('Documentation de Grappelli'),
                    'url': 'http://packages.python.org/django-grappelli/',
                    'external': True,
                },
                {
                    'title': _('Grappelli sur Google-Code'),
                    'url': 'http://code.google.com/p/django-grappelli/',
                    'external': True,
                },
            ]
        ))
