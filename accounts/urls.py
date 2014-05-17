# coding: utf-8
from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from registration.backends.default.views import ActivationView
from .views import (
    MyRegistrationView, GrantToAdmin, EvenementsGraph, HierarchicUserDetail,
    PartenairesView, ComiteEditorialeView, ContributeursView,
    EquipeDeveloppementView)


urlpatterns = patterns('',
    url(r'^comite-editorial$', ComiteEditorialeView.as_view(),
        name='comite_editorial'),
    url(r'^contributeurs$', ContributeursView.as_view(), name='contributeurs'),
    url(r'^equipe-developpement$', EquipeDeveloppementView.as_view(),
        name='equipe_developpement'),
    url(r'^partenaires$', PartenairesView.as_view(), name='partenaires'),
    url(r'^evenements_graph\.svg$', EvenementsGraph.as_view(),
        name='evenements_graph'),
    url(r'^utilisateurs/(?P<username>[\w.@+-]+)$',
        HierarchicUserDetail.as_view(), name='user_profile'),
    url(r'^acces-admin/(?P<pk>\d+)$', GrantToAdmin.as_view(),
        name='grant_to_admin'),
    url(r'^activation-compte/complete/$',
        TemplateView.as_view(
            template_name='registration/activation_complete.html'),
        name='registration_activation_complete'),
    url(r'^activation-compte/(?P<activation_key>\w+)/$',
        ActivationView.as_view(),
        name='registration_activate'),
    url(r'^creation-compte/$',
        MyRegistrationView.as_view(),
        name='registration_register'),
    url(r'^creation-compte/complete/$',
        TemplateView.as_view(
            template_name='registration/registration_complete.html'),
        name='registration_complete'),
    url(r'^creation-compte/close/$',
        TemplateView.as_view(
            template_name='registration/registration_closed.html'),
        name='registration_disallowed'),
    url(r'^', include('registration.auth_urls')),
)
