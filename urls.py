from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from musicologie import settings
from musicologie.catalogue.models import Individu, Lieu
from musicologie.catalogue.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^musicologie/', include('musicologie.foo.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^sources/(?P<pk>\d+)/$', SourceDetailView.as_view(), name='source'),
    url(r'''^evenements'''
        r'''(?:\/(?P<lieu_slug>[-\w]+))?'''
        r'''(?:\/(?P<year>\d+))?'''
        r'''(?:\/(?P<month>\d+))?'''
        r'''(?:\/(?P<day>\d+))?/$''', EvenementListView.as_view(), name='evenements'),
    url(r'^individus/$', IndividuListView.as_view(), name='individus'),
    url(r'^individus/(?P<slug>[-\w]+)/$', IndividuDetailView.as_view(), name='individu'),
    url(r'^oeuvres/(?P<slug>[-\w]+)/$', OeuvreDetailView.as_view(), name='oeuvre'),
    url(r'^saisie/source/$', 'musicologie.catalogue.views.saisie_source', name='saisie_sources'),
    url(r'^saisie/source/(?P<source_id>\d+)/$', 'musicologie.catalogue.views.saisie_source', name='saisie_source'),
    url(r'^lieux/$', LieuListView.as_view(), name='lieux'),
    url(r'^lieux/(?P<slug>[-\w]+)/$', LieuDetailView.as_view(), name='lieu'),
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

