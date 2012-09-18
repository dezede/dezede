from django_tables2 import Table
from django_tables2.columns import LinkColumn
from django_tables2.utils import A
from .models import Individu


class IndividuTable(Table):
    nom = LinkColumn('individu', args=(A('slug'),))
    class Meta:
        model = Individu
        attrs = {"class": "paleblue"}
        exclude = ('id', 'particule_nom', 'particule_nom_naissance',
                   'designation', 'etat', 'biographie', 'notes', 'slug',)
        ordering = ('nom',)
