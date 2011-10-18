from musicologie.catalogue.models import *
from django.contrib import admin

class LieuAdmin(admin.ModelAdmin):
    exclude = ['slug']

class IndividuAdmin(admin.ModelAdmin):
    exclude = ['slug']

class OeuvreAdmin(admin.ModelAdmin):
    exclude = ['slug']

class TypedeSourceAdmin(admin.ModelAdmin):
    prepopulated_fields = {'pluriel': ('nom',)}

admin.site.register(Source)
admin.site.register(Individu, IndividuAdmin)
admin.site.register(Oeuvre, OeuvreAdmin)
admin.site.register(Programme)
admin.site.register(TypedeSource, TypedeSourceAdmin)
admin.site.register(Evenement)
admin.site.register(Lieu, LieuAdmin)

