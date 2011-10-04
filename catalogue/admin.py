from catalogue.models import *
from django.contrib import admin

class LieuAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nom",)}

admin.site.register(Source)
admin.site.register(Individu)
admin.site.register(Oeuvre)
admin.site.register(Programme)
admin.site.register(Lieu, LieuAdmin)
admin.site.register(Illustration)
