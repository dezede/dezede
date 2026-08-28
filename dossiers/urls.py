from django.urls import path, re_path
from dossiers.views import (
    CategorieDeDossiersList, DossierDetail, DossierStatsDetail,
    DossierDetailXeLaTeX, DossierDataGeoJson, DossierEvenementsDataExport,
    DossierScenario, DossierDataDetail, DossierLegacyDataRedirect)


KIND = r'(?P<kind>evenements|oeuvres|sources)'
STATS_KIND = r'(?P<kind>evenements|oeuvres)'

urlpatterns = [
    path('', CategorieDeDossiersList.as_view(), name='dossier_index'),
    re_path(r'^(?P<slug>[\w-]+)/$', DossierDetail.as_view(),
        name='dossier_detail'),
    path('id/<int:pk>/', DossierDetail.as_view(),
        name='dossier_permanent_detail'),

    # Kind-scoped sub-resources.
    re_path(rf'^(?P<slug>[\w-]+)/{KIND}/data$', DossierDataDetail.as_view(),
        name='dossier_data_detail'),
    re_path(rf'^id/(?P<pk>\d+)/{KIND}/data$', DossierDataDetail.as_view(),
        name='dossier_data_permanent_detail'),
    re_path(rf'^(?P<slug>[\w-]+)/{STATS_KIND}/stats$',
        DossierStatsDetail.as_view(),
        name='dossier_stats_detail'),
    re_path(rf'^id/(?P<pk>\d+)/{STATS_KIND}/stats$',
        DossierStatsDetail.as_view(),
        name='dossier_stats_permanent_detail'),
    re_path(rf'^(?P<slug>[\w-]+)/{STATS_KIND}/geojson$',
        DossierDataGeoJson.as_view(),
        name='dossier_data_geojson'),
    re_path(rf'^id/(?P<pk>\d+)/{STATS_KIND}/geojson$',
        DossierDataGeoJson.as_view(),
        name='dossier_data_permanent_geojson'),
    re_path(r'^(?P<slug>[\w-]+)/(?P<kind>evenements)/export$',
        DossierEvenementsDataExport.as_view(),
        name='dossier_data_export'),
    re_path(r'^id/(?P<pk>\d+)/(?P<kind>evenements)/export$',
        DossierEvenementsDataExport.as_view(),
        name='dossier_data_permanent_export'),

    # Exports of the whole dossier (kind-independent).
    re_path(r'^(?P<slug>[\w-]+)/export-pdf$',
        DossierDetailXeLaTeX.as_view(),
        name='dossier_detail_xelatex'),
    path('id/<int:pk>/export-pdf',
        DossierDetailXeLaTeX.as_view(),
        name='dossier_detail_permanent_xelatex'),
    re_path(r'^(?P<slug>[\w-]+)/export-scenario$',
        DossierScenario.as_view(),
        name='dossier_export_scenario'),

    # Legacy kind-less URLs from before dossiers could mix several kinds of
    # data; permanently redirected to their kind-scoped equivalents.
    re_path(r'^(?P<slug>[\w-]+)/data$',
        DossierLegacyDataRedirect.as_view()),
    re_path(r'^id/(?P<pk>\d+)/data$',
        DossierLegacyDataRedirect.as_view(
            view_name='dossier_data_permanent_detail')),
    re_path(r'^(?P<slug>[\w-]+)/stats$',
        DossierLegacyDataRedirect.as_view(
            view_name='dossier_stats_detail', kind='evenements')),
    re_path(r'^id/(?P<pk>\d+)/stats$',
        DossierLegacyDataRedirect.as_view(
            view_name='dossier_stats_permanent_detail', kind='evenements')),
    re_path(r'^(?P<slug>[\w-]+)/geojson$',
        DossierLegacyDataRedirect.as_view(
            view_name='dossier_data_geojson', kind='evenements')),
    re_path(r'^id/(?P<pk>\d+)/geojson$',
        DossierLegacyDataRedirect.as_view(
            view_name='dossier_data_permanent_geojson', kind='evenements')),
    re_path(r'^(?P<slug>[\w-]+)/export$',
        DossierLegacyDataRedirect.as_view(
            view_name='dossier_data_export', kind='evenements')),
]
