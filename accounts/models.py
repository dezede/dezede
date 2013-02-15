# coding: utf-8

from django.contrib.auth.models import User
from django.db.models import Model, OneToOneField, ForeignKey, permalink
from django.utils.translation import ungettext_lazy, ugettext_lazy as _


class StudentProfile(Model):
    user = OneToOneField(User, related_name='student_profile',
                         verbose_name=_('Utilisateur'))
    professor = ForeignKey(User, related_name='students',
                           verbose_name=_('professeur'))

    class Meta(object):
        verbose_name = ungettext_lazy(u'profil étudiant',
                                      u'profils étudiants', 1)
        verbose_name_plural = ungettext_lazy(u'profil étudiant',
                                             u'profils étudiants', 2)

    def __unicode__(self):
        user = self.user
        full_name = user.get_full_name()
        return full_name if full_name else user.username
    __unicode__.admin_order_field = 'user'

    def professor_name(self):
        return self.professor.get_full_name() or unicode(self.professor)
    professor_name.short_description = _('professeur')
    professor_name.admin_order_field = 'professor'

    @permalink
    def get_absolute_url(self):
        return ('profiles_profile_detail',
                (), {'username': self.user.username})

    def permalien(self):
        return self.get_absolute_url()
