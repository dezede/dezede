from django.conf import settings
from django.conf.urls import *
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from ajax_select import urls as ajax_select_urls
from .views import (
    HomeView, CustomSearchView, autocomplete, ErrorView, BibliographieView)


admin.autodiscover()

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^', include('libretto.urls')),
    url(r'^examens/', include('examens.urls')),
    url(r'^presentation$',
        TemplateView.as_view(template_name='pages/presentation.html'),
        name='presentation'),
    url(r'^contribuer$',
        TemplateView.as_view(template_name='pages/contribute.html'),
        name='contribuer'),
    url(r'^bibliographie$', BibliographieView.as_view(), name='bibliographie'),
    url(r'^', include('accounts.urls')),
    url(r'^dossiers/', include('dossiers.urls')),
    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^recherche/', CustomSearchView(), name='haystack_search'),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'autocomplete', autocomplete, name='autocomplete'),
    url(r'^404$', ErrorView.as_view(status=404)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^403$', ErrorView.as_view(status=403)),
        url(r'^500$', ErrorView.as_view(status=500)),
        url(r'^503$', ErrorView.as_view(status=503)),
    ]
