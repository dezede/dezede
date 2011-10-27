from musicologie.catalogue.models import *
from django.contrib import admin

class StatutAdmin(admin.ModelAdmin):
    exclude = ['slug']

class NaturedeLieuAdmin(admin.ModelAdmin):
    exclude = ['slug']

class LieuAdmin(admin.ModelAdmin):
    exclude = ['slug']

class IndividuAdmin(admin.ModelAdmin):
    exclude = ['slug']

class OeuvreAdmin(admin.ModelAdmin):
    exclude = ['slug']

class TypedeSourceAdmin(admin.ModelAdmin):
    prepopulated_fields = {'pluriel': ('nom',)}

admin.site.register(Statut, StatutAdmin)
admin.site.register(NaturedeLieu, NaturedeLieuAdmin)
admin.site.register(Lieu, LieuAdmin)
admin.site.register(Individu, IndividuAdmin)
admin.site.register(Oeuvre, OeuvreAdmin)
admin.site.register(Representation)
admin.site.register(Evenement)
admin.site.register(TypedeSource, TypedeSourceAdmin)
admin.site.register(Source)

