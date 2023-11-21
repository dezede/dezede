from django.conf.urls import url
from dossiers.views import (
    CategorieDeDossiersList, DossierDetail,
    DossierDEvenementsStatsDetail,
    DossierDEvenementsDetailXeLaTeX,
    DossierDEvenementsDataGeoJson, DossierDEvenementsDataExport,
    DossierDEvenementsScenario, DossierDataDetail)


urlpatterns = [
    url(r'^$', CategorieDeDossiersList.as_view(),
        name='dossier_index'),
    url(r'^(?P<slug>[\w-]+)/$', DossierDetail.as_view(),
        name='dossier_detail'),
    url(r'^id/(?P<pk>\d+)/$', DossierDetail.as_view(),
        name='dossier_permanent_detail'),
    url(r'^(?P<slug>[\w-]+)/stats$', DossierDEvenementsStatsDetail.as_view(),
        name='dossierdevenements_stats_detail'),
    url(r'^id/(?P<pk>\d+)/stats$', DossierDEvenementsStatsDetail.as_view(),
        name='dossierdevenements_stats_permanent_detail'),
    url(r'^(?P<slug>[\w-]+)/data$', DossierDataDetail.as_view(),
        name='dossier_data_detail'),
    url(r'^id/(?P<pk>\d+)/data$', DossierDataDetail.as_view(),
        name='dossier_data_permanent_detail'),
    url(r'^(?P<slug>[\w-]+)/geojson$', DossierDEvenementsDataGeoJson.as_view(),
        name='dossierdevenements_data_geojson'),
    url(r'^id/(?P<pk>\d+)/geojson$', DossierDEvenementsDataGeoJson.as_view(),
        name='dossierdevenements_data_permanent_geojson'),
    url(r'^(?P<slug>[\w-]+)/export$',
        DossierDEvenementsDataExport.as_view(),
        name='dossierdevenements_data_export'),
    url(r'^id/(?P<pk>\d+)/export$',
        DossierDEvenementsDataExport.as_view(),
        name='dossierdevenements_data_export'),
    url(r'^(?P<slug>[\w-]+)/export-pdf$',
        DossierDEvenementsDetailXeLaTeX.as_view(),
        name='dossierdevenements_detail_xelatex'),
    url(r'^id/(?P<pk>\d+)/export-pdf$',
        DossierDEvenementsDetailXeLaTeX.as_view(),
        name='dossierdevenements_detail_permanent_xelatex'),
    url(r'^(?P<slug>[\w-]+)/export-scenario$',
        DossierDEvenementsScenario.as_view(),
        name='dossierdevenement_export_scenario')
]
