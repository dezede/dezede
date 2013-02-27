# coding: utf-8

from __future__ import unicode_literals
from django.contrib.admin import site, ModelAdmin
from .models import StudentProfile


class StudentProfileAdmin(ModelAdmin):
    list_display = ('__str__', 'professor_name')


site.register(StudentProfile, StudentProfileAdmin)
