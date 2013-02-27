# coding: utf-8

from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db.models import Model, OneToOneField, ForeignKey, permalink
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ungettext_lazy, ugettext_lazy as _


@python_2_unicode_compatible
class StudentProfile(Model):
    user = OneToOneField(User, related_name='student_profile',
                         verbose_name=_('Utilisateur'))
    professor = ForeignKey(User, related_name='students',
                           verbose_name=_('professeur'))

    class Meta(object):
        verbose_name = ungettext_lazy('profil étudiant',
                                      'profils étudiants', 1)
        verbose_name_plural = ungettext_lazy('profil étudiant',
                                             'profils étudiants', 2)

    def __str__(self):
        user = self.user
        full_name = user.get_full_name()
        return full_name if full_name else user.username
    __str__.admin_order_field = 'user'

    def professor_name(self):
        return self.professor.get_full_name() or smart_text(self.professor)
    professor_name.short_description = _('professeur')
    professor_name.admin_order_field = 'professor'

    @permalink
    def get_absolute_url(self):
        return ('profiles_profile_detail',
                (), {'username': self.user.username})

    def permalien(self):
        return self.get_absolute_url()
