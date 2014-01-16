# coding: utf-8

from django.conf import settings
from django.conf.urls import *
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from ajax_select import urls as ajax_select_urls
from filebrowser.sites import site
from .views import HomeView, CustomSearchView, autocomplete, ErrorView


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('libretto.urls')),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^dossiers/', include('dossiers.urls')),
    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^recherche/', CustomSearchView(), name='haystack_search'),
    url(r'^comptes/', include('accounts.urls')),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'autocomplete', autocomplete, name='autocomplete'),
    url(r'^404$', ErrorView.as_view(status=404)),
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

    import debug_toolbar

    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^403$', ErrorView.as_view(status=403)),
        url(r'^500$', ErrorView.as_view(status=500)),
        url(r'^503$', ErrorView.as_view(status=503)),
    )
