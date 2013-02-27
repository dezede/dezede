# coding: utf-8
from django.conf.urls import patterns, url, include
from .forms import UserRegistrationForm
from django.views.generic import TemplateView
from registration.views import activate
from .views import register, GrantToAdmin


urlpatterns = patterns('',
    url(r'^equipe/(?P<pk>\d+)', GrantToAdmin.as_view(), name='grant_to_admin'),
    url(r'^activation/complete/$',
        TemplateView.as_view(
            template_name='registration/activation_complete.html'),
        name='registration_activation_complete'),
    url(r'^activation/(?P<activation_key>\w+)/$',
        activate,
        {'backend': 'registration.backends.default.DefaultBackend'},
        name='registration_activate'),
    url(r'^creation/$',
        register,
        {'backend': 'registration.backends.default.DefaultBackend',
         'form_class': UserRegistrationForm},
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
