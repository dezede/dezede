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
    (r'^evenements/$', 'musicologie.catalogue.views.index_evenements'),
    (r'^evenements/(?P<lieu_slug>[-\w]+)/$', 'musicologie.catalogue.views.index_evenements'),
    (r'^evenements/(?P<lieu_slug>[-\w]+)/(?P<annee>\d+)/$', 'musicologie.catalogue.views.index_evenements'),
    (r'^evenements/(?P<lieu_slug>[-\w]+)/(?P<annee>\d+)/(?P<mois>\d+)/$', 'musicologie.catalogue.views.index_evenements'),
    (r'^evenements/(?P<lieu_slug>[-\w]+)/(?P<annee>\d+)/(?P<mois>\d+)/(?P<jour>\d+)/$', 'musicologie.catalogue.views.index_evenements'),
    (r'^individus/$', 'musicologie.catalogue.views.index_individus'),
    (r'^individus/(?P<individu_slug>[-\w]+)/$', 'musicologie.catalogue.views.detail_individu'),
    (r'^oeuvres/(?P<oeuvre_slug>[-\w]+)/$', 'musicologie.catalogue.views.detail_oeuvre'),
    (r'^saisie/source/$', 'musicologie.catalogue.views.saisie_source'),
    (r'^saisie/source/(?P<source_id>\d+)/$', 'musicologie.catalogue.views.saisie_source'),
    (r'^'+_('lieux')+'/$', 'musicologie.catalogue.views.index_lieux'),
    (r'^'+_('lieux')+'/(?P<lieu_slug>[-\w]+)/$', 'musicologie.catalogue.views.detail_lieu'),
    (r'^tinymce/', include('tinymce.urls')),
    (r'^grappelli/', include('grappelli.urls')),
    (r'^admin/filebrowser/', include('filebrowser.urls')),
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

