# coding: utf-8

from django.conf.urls import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from filebrowser.sites import site
from ajax_select import urls as ajax_select_urls
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('libretto.urls')),
    url(r'^dossiers/', include('dossiers.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^recherche/', include('haystack.urls')),
    url(r'^comptes/', include('accounts.urls')),
    url(r'^(?P<url>.*/)$', 'django.contrib.flatpages.views.flatpage'),
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
