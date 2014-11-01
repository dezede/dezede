# coding: utf-8

from __future__ import unicode_literals
from allauth.account.adapter import DefaultAccountAdapter


class HierarchicUserAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        data = form.cleaned_data
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.mentor = data['mentor']
        user.willing_to_be_mentor = data['willing_to_be_mentor']
        user.is_active = False

        user = super(HierarchicUserAdapter,
                     self).save_user(request, user, form, commit=commit)

        user.groups.add(*data['groups'])

        return user

    def confirm_email(self, request, email_address):
        super(HierarchicUserAdapter, self).confirm_email(request,
                                                         email_address)
        email_address.user.is_active = True
        email_address.user.save()
