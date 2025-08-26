from django.urls import include, re_path
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from ajax_select import urls as ajax_select_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from noridjango.urls import urlpatterns as noridjango_urls

from .api import wagtail_api_router
from .views import (
    HomeView, CustomSearchView, autocomplete, BibliographieView,
    RssFeed, GlobalSitemap,
)


admin.autodiscover()

urlpatterns = [
    re_path(r'^$', HomeView.as_view(), name='home'),
    re_path(r'^', include('libretto.urls')),
    re_path(r'^examens/', include('examens.urls')),
    re_path(r'^presentation$',
        TemplateView.as_view(template_name='pages/presentation.html'),
        name='presentation'),
    re_path(r'^contribuer$',
        TemplateView.as_view(template_name='pages/contribute.html'),
        name='contribuer'),
    re_path(r'^protection-donnees$',
        TemplateView.as_view(template_name='pages/protection_donnees.html'),
        name='protection_donnees'),
    re_path(r'^bibliographie$', BibliographieView.as_view(), name='bibliographie'),
    re_path(r'^', include('accounts.urls')),
    re_path(r'^dossiers/', include('dossiers.urls')),
    re_path(r'^admin/lookups/', include(ajax_select_urls)),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
    re_path(r'^tinymce/', include('tinymce.urls')),
    re_path(r'^grappelli/', include('grappelli.urls')),
    re_path(r'^recherche/', CustomSearchView(), name='haystack_search'),
    re_path(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    re_path(r'^autocomplete$', autocomplete, name='autocomplete'),
    re_path(r'^rss\.xml$', RssFeed(), name='rss_feed'),
    re_path(r'^sitemap.xml$', cache_page(24*60*60)(sitemap),
        {'sitemaps': {'global': GlobalSitemap}},
        name='django.contrib.sitemaps.views.sitemap'),
    *noridjango_urls,
    re_path(r'^wagtail-admin/', include(wagtailadmin_urls)),
    re_path(r'^documents/', include(wagtaildocs_urls)),
    re_path(r'^api/', wagtail_api_router.urls),
    # We add Wagtail url patterns after all others since
    # they can match almost any URL.
    re_path(r'^', include(wagtail_urls)),
]
