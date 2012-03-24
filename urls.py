from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from musicologie import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^musicologie/', include('musicologie.foo.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^evenements/$', 'musicologie.catalogue.views.index_evenements', name='evenements'),
    url(r'^evenements/(?P<lieu_slug>[-\w]+)/$', 'musicologie.catalogue.views.index_evenements', name='evenement_lieu'),
    url(r'^evenements/(?P<lieu_slug>[-\w]+)/(?P<annee>\d+)/$', 'musicologie.catalogue.views.index_evenements', name='evenement_annee'),
    url(r'^evenements/(?P<lieu_slug>[-\w]+)/(?P<annee>\d+)/(?P<mois>\d+)/$', 'musicologie.catalogue.views.index_evenements', name='evenement_mois'),
    url(r'^evenements/(?P<lieu_slug>[-\w]+)/(?P<annee>\d+)/(?P<mois>\d+)/(?P<jour>\d+)/$', 'musicologie.catalogue.views.index_evenements', name='evenement_jour'),
    url(r'^individus/$', 'musicologie.catalogue.views.index_individus'),
    url(r'^individus/(?P<individu_slug>[-\w]+)/$', 'musicologie.catalogue.views.detail_individu'),
    url(r'^oeuvres/(?P<oeuvre_slug>[-\w]+)/$', 'musicologie.catalogue.views.detail_oeuvre'),
    url(r'^saisie/source/$', 'musicologie.catalogue.views.saisie_source'),
    url(r'^saisie/source/(?P<source_id>\d+)/$', 'musicologie.catalogue.views.saisie_source'),
    url(r'^lieux/$', 'musicologie.catalogue.views.index_lieux'),
    url(r'^lieux/(?P<lieu_slug>[-\w]+)/$', 'musicologie.catalogue.views.detail_lieu'),
    (r'^tinymce/', include('tinymce.urls')),
    (r'^grappelli/', include('grappelli.urls')),
    (r'^admin/filebrowser/', include('filebrowser.urls')),
    (r'^recherche/', include('haystack.urls')),
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    from django.views.static import serve
    _media_url = settings.MEDIA_URL
    if _media_url.startswith('/'):
        _media_url = _media_url[1:]
        urlpatterns += patterns('',
                                (r'^%s(?P<path>.*)$' % _media_url,
                                serve,
                                {'document_root': settings.MEDIA_ROOT}))
    del(_media_url, serve)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )

