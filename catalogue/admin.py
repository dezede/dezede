from musicologie.catalogue.models import *
from django.contrib import admin

class StatutAdmin(admin.ModelAdmin):
    exclude = ['slug']

class NaturedeLieuAdmin(admin.ModelAdmin):
    exclude = ['slug']

class LieuAdmin(admin.ModelAdmin):
    exclude = ['slug']

class ProfessionAdmin(admin.ModelAdmin):
    exclude = ['slug']

class IndividuAdmin(admin.ModelAdmin):
    exclude = ['slug']

class LivretAdmin(admin.ModelAdmin):
    exclude = ['slug']

class OeuvreAdmin(admin.ModelAdmin):
    exclude = ['slug']

class TypedeSourceAdmin(admin.ModelAdmin):
    exclude = ['slug']

admin.site.register(Illustration)
admin.site.register(Statut, StatutAdmin)
admin.site.register(NaturedeLieu, NaturedeLieuAdmin)
admin.site.register(Lieu, LieuAdmin)
admin.site.register(Saison)
admin.site.register(Profession, ProfessionAdmin)
admin.site.register(Individu, IndividuAdmin)
admin.site.register(Livret, LivretAdmin)
admin.site.register(Oeuvre, OeuvreAdmin)
admin.site.register(Representation)
admin.site.register(Evenement)
admin.site.register(TypedeSource, TypedeSourceAdmin)
admin.site.register(Source)

