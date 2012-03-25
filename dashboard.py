# coding: utf-8

"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'musicologie.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """
    
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        
        self.children.append(modules.Group(
            _(u'Base de données'),
            column=1,
            collapsible=False,
            children=[
                modules.ModelList(
                    _('Saisie courante'),
                    column=1,
                    models=('musicologie.catalogue.models.Source',
                            'musicologie.catalogue.models.Evenement',
                            'musicologie.catalogue.models.Oeuvre',
                            'musicologie.catalogue.models.Individu',
                            'musicologie.catalogue.models.Lieu',),
                ),
                modules.ModelList(
                    _('Saisie occasionnelle'),
                    column=1,
                    css_classes=('collapse closed',),
                    exclude=('django.contrib.*',
                             'musicologie.catalogue.models.Source',
                             'musicologie.catalogue.models.Evenement',
                             'musicologie.catalogue.models.Oeuvre',
                             'musicologie.catalogue.models.Individu',
                             'musicologie.catalogue.models.Lieu',),
                )
            ]
        ))
        
        self.children.append(modules.Group(
            _('Fichiers'),
            column=1,
            collapsible=False,
            children=[
                modules.LinkList(
                    _('Gestionnaire de fichiers bruts'),
                    column=2,
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
                    _(u'Intégration à la base de données'),
                    collapsible=False,
                    models=('musicologie.catalogue.models.Document',
                            'musicologie.catalogue.models.Illustration',),
                )
            ]
        ))
        
        self.children.append(modules.AppList(
            _('Utilisateurs et groupes'),
            column=2,
            css_classes=('collapse closed',),
            models=('django.contrib.*',),
        ))
        
        self.children.append(modules.LinkList(
            _('Traduction'),
            column=2,
            css_classes=('collapse open',),
            children=[
                {
                    'title': 'Rosetta',
                    'url': '/rosetta/pick/',
                    'external': False,
                },
            ]
        ))
        
        self.children.append(modules.LinkList(
            _('Support'),
            column=2,
            css_classes=('collapse closed',),
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
        
        self.children.append(modules.RecentActions(
            _(u'Actions récentes'),
            limit=8,
            collapsible=False,
            column=3,
        ))

