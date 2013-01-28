# coding: utf-8

from __future__ import unicode_literals
from django_tables2 import Table
from django_tables2.columns import Column, LinkColumn, CheckBoxColumn
from django_tables2.utils import A
from django.utils.translation import ugettext_lazy as _


class OeuvreTable(Table):
    genre = Column()
    titre = LinkColumn('oeuvre', args=(A('slug'),), verbose_name=_('titre'))
    titre_secondaire = Column()
    auteurs = Column(accessor='auteurs_html', verbose_name=_('auteurs'),
                          order_by='auteurs__individu__nom')

    class Meta:
        attrs = {'class': 'paleblue'}


class IndividuTable(Table):
    calc_fav_prenoms = Column(verbose_name=_('prénoms'),
                              order_by=('prenoms__prenom',))
    nom = LinkColumn('individu', args=(A('slug'),), accessor='nom_seul',
                     order_by=('pseudonyme', 'nom',))
    professions = Column(accessor='calc_professions',
                         verbose_name=_('professions'),
                         order_by=('professions__nom',))
    naissance = Column(verbose_name=_('naissance'),
                       order_by='ancrage_naissance')
    deces = Column(verbose_name=_('décès'), order_by='ancrage_deces')

    class Meta:
        attrs = {"class": "paleblue"}


class ProfessionTable(Table):
    # selection = CheckBoxColumn(accessor='pk')
    nom = LinkColumn('profession', args=(A('slug'),), verbose_name=_('nom'))
    individus_count = Column(accessor='individus.count', orderable=False,
                             verbose_name=_('nombre d’individus'))
    oeuvres_count = Column(accessor='auteurs.oeuvres.count', orderable=False,
                           verbose_name=_('nombre d’œuvres'))

    class Meta:
        attrs = {'class': 'paleblue'}


class PartieTable(Table):
    nom = LinkColumn('catalogue:role-ou-instrument_detail', args=(A('slug'),),
                     verbose_name=_('nom'))
    interpretes = Column(accessor='interpretes_html',
                 verbose_name=_('interprètes'),
                 order_by='pupitres__elements_de_distribution__individus__nom')

    class Meta:
        attrs = {'class': 'paleblue'}
