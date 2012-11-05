# coding: utf-8
from django.conf.urls import patterns, url, include
from .forms import UserRegistrationForm
from django.views.generic.simple import direct_to_template
from registration.views import activate
from .views import register, GrantToAdmin


urlpatterns = patterns('',
    url(r'^equipe/(?P<pk>\d+)', GrantToAdmin.as_view(), name='grant_to_admin'),
    url(r'^activation/complete/$',
        direct_to_template,
        {'template': 'registration/activation_complete.html'},
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
        direct_to_template,
        {'template': 'registration/registration_complete.html'},
        name='registration_complete'),
    url(r'^creation/close/$',
        direct_to_template,
        {'template': 'registration/registration_closed.html'},
        name='registration_disallowed'),
    (r'', include('registration.auth_urls')),
)