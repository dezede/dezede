# coding: utf-8

from __future__ import unicode_literals
from django.views.generic import DetailView
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from registration.backends import get_backend
from django.core.exceptions import PermissionDenied


class GrantToAdmin(DetailView):
    model = User
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


def register(request, backend, success_url=None, form_class=None,
             disallowed_url='registration_disallowed',
             template_name='registration/registration_form.html',
             extra_context=None):
    """Copié depuis django-registration et modifié."""
    backend = get_backend(backend)
    if not backend.registration_allowed(request):
        return redirect(disallowed_url)
    if form_class is None:
        form_class = backend.get_form_class(request)

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_user = backend.register(request, **form.cleaned_data)
            form.save(request, new_user)
            if success_url is None:
                to, args, kwargs = backend.post_registration_redirect(
                    request, new_user)
                return redirect(to, *args, **kwargs)
            else:
                return redirect(success_url)
    else:
        form = form_class()

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    return render_to_response(template_name, {'form': form},
                              context_instance=context)
