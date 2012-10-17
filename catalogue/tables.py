# coding: utf-8

from django_tables2 import Table
from django_tables2.columns import Column, LinkColumn, CheckBoxColumn
from django_tables2.utils import A
from django.utils.translation import ugettext_lazy as _


class OeuvreTable(Table):
    genre = Column()
    titre = LinkColumn('oeuvre', args=(A('slug'),), verbose_name=_('titre'))
    titre_secondaire = Column()
    auteurs_html = Column(verbose_name=_('auteurs'))

    class Meta:
        attrs = {"class": "paleblue"}


class IndividuTable(Table):
    calc_fav_prenoms = Column(verbose_name=_(u'prénoms'),
                              order_by=('prenoms__prenom',))
    nom = LinkColumn('individu', args=(A('slug'),), accessor='nom_seul',
                     order_by=('pseudonyme', 'nom',))
    calc_professions = Column(verbose_name=_('professions'),
                              order_by=('professions__nom',))
    naissance = Column(verbose_name=_('naissance'),
                       order_by='ancrage_naissance')
    deces = Column(verbose_name=_(u'décès'), order_by='ancrage_deces')

    class Meta:
        attrs = {"class": "paleblue"}


class ProfessionTable(Table):
    # selection = CheckBoxColumn(accessor='pk')
    nom = LinkColumn('profession', args=(A('slug'),), verbose_name=_('nom'))

    class Meta:
        attrs = {"class": "paleblue"}


class PartieTable(Table):
    nom = LinkColumn('partie', args=(A('slug'),), verbose_name=_('nom'))
    interpretes_html = Column(verbose_name=_(u'interprètes'))

    class Meta:
        attrs = {"class": "paleblue"}
