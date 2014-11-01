# coding: utf-8
from allauth.account import views
from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from .views import (
    GrantToAdmin, EvenementsGraph, HierarchicUserDetail,
    PartenairesView, ComiteEditorialeView, ContributeursView,
    EquipeDeveloppementView, ProprietairesView)


urlpatterns = patterns('',
    url(r'^comite-editorial$', ComiteEditorialeView.as_view(),
        name='comite_editorial'),
    url(r'^contributeurs$', ContributeursView.as_view(), name='contributeurs'),
    url(r'^equipe-developpement$', EquipeDeveloppementView.as_view(),
        name='equipe_developpement'),
    url(r'^proprietaires$', ProprietairesView.as_view(), name='proprietaires'),
    url(r'^partenaires$', PartenairesView.as_view(), name='partenaires'),
    url(r'^evenements_graph\.svg$', EvenementsGraph.as_view(),
        name='evenements_graph'),
    url(r'^utilisateurs/(?P<username>[\w.@+-]+)$',
        HierarchicUserDetail.as_view(), name='user_profile'),

    url(r'^acces-admin/(?P<pk>\d+)$', GrantToAdmin.as_view(),
        name='grant_to_admin'),

    url(r'^creation-compte/$', views.signup, name='account_signup'),
    url(r'^connexion/$', views.login, name='account_login'),
    url(r'^deconnexion/$', views.logout, name='account_logout'),

    url(r'^mot-de-passe/changer/$', views.password_change,
        name='account_change_password'),
    url(r'^mot-de-passe/choisir/$', views.password_set,
        name='account_set_password'),

    url(r'^inactif/$', views.account_inactive, name='account_inactive'),

    # E-mail
    # url(r'^email/$', views.email, name='account_email'),
    url(r'^confirmation-email/$', views.email_verification_sent,
        name='account_email_verification_sent'),
    url(r'^confirmation-email/(?P<key>\w+)/$', views.confirm_email,
        name='account_confirm_email'),

    # password reset
    url(r'^mot-de-passe/reset/$', views.password_reset,
        name='account_reset_password'),
    url(r'^mot-de-passe/reset/done/$', views.password_reset_done,
        name='account_reset_password_done'),
    url(r'^mot-de-passe/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$',
        views.password_reset_from_key,
        name='account_reset_password_from_key'),
    url(r'^mot-de-passe/reset/key/done/$', views.password_reset_from_key_done,
        name='account_reset_password_from_key_done'),
)
