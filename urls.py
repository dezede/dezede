from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^musicologie/', include('musicologie.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^sources/$', 'catalogue.views.index_sources'),
    (r'^sources/(?P<lieu_slug>[-\w]+)/$', 'catalogue.views.index_sources'),
    (r'^sources/(?P<lieu_slug>[-\w]+)/(?P<annee>\d+)/$', 'catalogue.views.index_sources'),
    (r'^sources/(?P<lieu_slug>[-\w]+)/(?P<annee>\d+)/(?P<mois>\d+)/$', 'catalogue.views.index_sources'),
    (r'^sources/(?P<lieu_slug>[-\w]+)/(?P<annee>\d+)/(?P<mois>\d+)/(?P<jour>\d+)/$', 'catalogue.views.index_sources'),
    (r'^'+_('lieux')+'/$', 'catalogue.views.index_lieux'),
    (r'^'+_('lieux')+'/(?P<lieu_slug>[-\w]+)/$', 'catalogue.views.detail_lieu'),
)
