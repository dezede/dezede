from django_tables2 import Table
from .models import Individu


class IndividuTable(Table):
    class Meta:
        model = Individu
        attrs = {"class": "paleblue"}
        exclude = ('id', 'particule_nom', 'particule_nom_naissance',
                   'designation', 'etat', 'biographie', 'notes', 'slug',)
        ordering = ('nom',)
