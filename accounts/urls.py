from allauth.account import views
from django.urls import path, re_path
from .views import (
    GrantToAdmin, EvenementsGraph, HierarchicUserDetail,
    PartenairesView, ComiteEditorialeView, ContributeursView,
    EquipeDeveloppementView, ProprietairesView, ComiteScientifiqueView)


urlpatterns = [
    path('comite-editorial', ComiteEditorialeView.as_view(),
        name='comite_editorial'),
    path('comite-scientifique', ComiteScientifiqueView.as_view(),
        name='comite_scientifique'),
    path('contributeurs', ContributeursView.as_view(), name='contributeurs'),
    path('equipe-developpement', EquipeDeveloppementView.as_view(),
        name='equipe_developpement'),
    path('proprietaires', ProprietairesView.as_view(), name='proprietaires'),
    path('partenaires', PartenairesView.as_view(), name='partenaires'),
    path('evenements_graph.svg', EvenementsGraph.as_view(),
        name='evenements_graph'),
    re_path(
        r'^utilisateurs/(?P<username>[\w.@+-]+)$',
        HierarchicUserDetail.as_view(), name='user_profile',
    ),

    path('acces-admin/<int:pk>', GrantToAdmin.as_view(),
        name='grant_to_admin'),

    path('creation-compte/', views.signup, name='account_signup'),
    path('connexion/', views.login, name='account_login'),
    path('deconnexion/', views.logout, name='account_logout'),

    path('mot-de-passe/changer/', views.password_change,
        name='account_change_password'),
    path('mot-de-passe/choisir/', views.password_set,
        name='account_set_password'),

    path('inactif/', views.account_inactive, name='account_inactive'),

    # E-mail
    # path('email/', views.email, name='account_email'),
    path('confirmation-email/', views.email_verification_sent,
        name='account_email_verification_sent'),
    re_path(r'^confirmation-email/(?P<key>[-:\w]+)/$', views.confirm_email,
        name='account_confirm_email'),

    # password reset
    path('mot-de-passe/reset/', views.password_reset,
        name='account_reset_password'),
    path('mot-de-passe/reset/done/', views.password_reset_done,
        name='account_reset_password_done'),
    re_path(r'^mot-de-passe/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$',
        views.password_reset_from_key,
        name='account_reset_password_from_key'),
    path('mot-de-passe/reset/key/done/', views.password_reset_from_key_done,
        name='account_reset_password_from_key_done'),
]
