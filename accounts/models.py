# coding: utf-8

from django.contrib.auth.models import User
from django.db.models import Model, OneToOneField, ForeignKey, permalink
from django.utils.translation import ungettext_lazy, ugettext_lazy as _


class StudentProfile(Model):
    user = OneToOneField(User, related_name='student_profile')
    professor = ForeignKey(User, related_name='students',
                           verbose_name=_('professeur'))

    class Meta:
        verbose_name = ungettext_lazy(u'profil étudiant',
                                      u'profils étudiants', 1)
        verbose_name_plural = ungettext_lazy(u'profil étudiant',
                                             u'profils étudiants', 2)

    def __unicode__(self):
        user = self.user
        full_name = user.get_full_name()
        return full_name if full_name else user.username

    @permalink
    def get_absolute_url(self):
        return ('profiles_profile_detail',
                (), {'username': self.user.username})
