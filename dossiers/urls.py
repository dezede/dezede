from django.urls import path, re_path
from dossiers.views import (
    CategorieDeDossiersList, DossierDetail,
    DossierDEvenementsStatsDetail,
    DossierDEvenementsDetailXeLaTeX,
    DossierDEvenementsDataGeoJson, DossierDEvenementsDataExport,
    DossierDEvenementsScenario, DossierDataDetail)


urlpatterns = [
    path('', CategorieDeDossiersList.as_view(), name='dossier_index'),
    re_path(r'^(?P<slug>[\w-]+)/$', DossierDetail.as_view(),
        name='dossier_detail'),
    path('id/<int:pk>/', DossierDetail.as_view(),
        name='dossier_permanent_detail'),
    re_path(r'^(?P<slug>[\w-]+)/stats$', DossierDEvenementsStatsDetail.as_view(),
        name='dossierdevenements_stats_detail'),
    path('id/<int:pk>/stats', DossierDEvenementsStatsDetail.as_view(),
        name='dossierdevenements_stats_permanent_detail'),
    re_path(r'^(?P<slug>[\w-]+)/data$', DossierDataDetail.as_view(),
        name='dossier_data_detail'),
    path('id/<int:pk>/data', DossierDataDetail.as_view(),
        name='dossier_data_permanent_detail'),
    re_path(r'^(?P<slug>[\w-]+)/geojson$', DossierDEvenementsDataGeoJson.as_view(),
        name='dossierdevenements_data_geojson'),
    path('id/<int:pk>/geojson', DossierDEvenementsDataGeoJson.as_view(),
        name='dossierdevenements_data_permanent_geojson'),
    re_path(r'^(?P<slug>[\w-]+)/export$',
        DossierDEvenementsDataExport.as_view(),
        name='dossierdevenements_data_export'),
    path('id/<int:pk>/export',
        DossierDEvenementsDataExport.as_view(),
        name='dossierdevenements_data_export'),
    re_path(r'^(?P<slug>[\w-]+)/export-pdf$',
        DossierDEvenementsDetailXeLaTeX.as_view(),
        name='dossierdevenements_detail_xelatex'),
    path('id/<int:pk>/export-pdf',
        DossierDEvenementsDetailXeLaTeX.as_view(),
        name='dossierdevenements_detail_permanent_xelatex'),
    re_path(r'^(?P<slug>[\w-]+)/export-scenario$',
        DossierDEvenementsScenario.as_view(),
        name='dossierdevenement_export_scenario')
]
