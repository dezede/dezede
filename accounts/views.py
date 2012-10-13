# coding: utf-8

from django.views.generic import DetailView
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.template.loader import render_to_string


class GrantToAdmin(DetailView):
    model = User
    template_name = 'accounts/grant_to_admin.html'

    def get_context_data(self, **kwargs):
        context = super(GrantToAdmin, self).get_context_data(**kwargs)
        user = self.object
        if user.is_staff:
            context['already_staff'] = True
        else:
            user.is_staff = True
            user.save()
            site_url = 'http://' + get_current_site(self.request).domain
            email_content = render_to_string(
                'accounts/grant_to_admin_email.txt',
                {'user': user, 'site_url': site_url})
            user.email_user(u'[Dezède] Accès autorisé à l’administration',
                            email_content)
        return context