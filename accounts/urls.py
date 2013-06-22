# coding: utf-8
from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from registration.backends.default.views import ActivationView
from .views import MyRegistrationView, GrantToAdmin, EvenementsGraph


urlpatterns = patterns('',
    url(r'^evenements_graph.svg$', EvenementsGraph.as_view(),
        name='evenements_graph'),
    url(r'^equipe/(?P<pk>\d+)$', GrantToAdmin.as_view(),
        name='grant_to_admin'),
    url(r'^activation/complete/$',
        TemplateView.as_view(
            template_name='registration/activation_complete.html'),
        name='registration_activation_complete'),
    url(r'^activation/(?P<activation_key>\w+)/$',
        ActivationView.as_view(),
        name='registration_activate'),
    url(r'^creation/$',
        MyRegistrationView.as_view(),
        name='registration_register'),
    url(r'^creation/complete/$',
        TemplateView.as_view(
            template_name='registration/registration_complete.html'),
        name='registration_complete'),
    url(r'^creation/close/$',
        TemplateView.as_view(
            template_name='registration/registration_closed.html'),
        name='registration_disallowed'),
    url(r'', include('registration.auth_urls')),
)
