from django.contrib.admin import site, ModelAdmin
from .models import StudentProfile


class StudentProfileAdmin(ModelAdmin):
    list_display = ('__unicode__', 'professor_name')


site.register(StudentProfile, StudentProfileAdmin)
