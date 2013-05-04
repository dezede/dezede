# coding: utf-8

from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.contrib.sites.models import get_current_site
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views.generic import DetailView
from registration.backends.default.views import RegistrationView
from .forms import UserRegistrationForm


class GrantToAdmin(DetailView):
    model = get_user_model()
    template_name = 'accounts/grant_to_admin.html'

    def grant_user(self, user):
        user.is_staff = True
        user.save()
        site_url = 'http://' + get_current_site(self.request).domain
        email_content = render_to_string(
            'accounts/granted_to_admin_email.txt',
            {'user': user, 'site_url': site_url})
        user.email_user(
            '[Dezède] Accès autorisé à l’administration',
            email_content)

    def get_context_data(self, **kwargs):
        context = super(GrantToAdmin, self).get_context_data(**kwargs)
        current_user = self.request.user
        user_to_be_granted = self.object
        if current_user != user_to_be_granted.student_profile.professor:
            raise PermissionDenied
        if user_to_be_granted.is_staff:
            context['already_staff'] = True
        else:
            self.grant_user(user_to_be_granted)
        return context


class MyRegistrationView(RegistrationView):
    form_class = UserRegistrationForm

    def form_valid(self, request, form):
        new_user = self.register(request, **form.cleaned_data)
        form.save(request, new_user)
        success_url = self.get_success_url(request, new_user)

        try:
            to, args, kwargs = success_url
            return redirect(to, *args, **kwargs)
        except ValueError:
            return redirect(success_url)
